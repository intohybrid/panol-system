# Saga coreografiada: solicitud → préstamo → devolución

## Propósito

Este documento describe la transacción distribuida central del sistema: el paso de una solicitud web a un préstamo materializado y a su devolución posterior, atravesando varios microservicios sin un orquestador central. Justifica la elección de coreografía sobre orquestación (decisión registrada en ADR-006) y describe los pasos felices, las compensaciones y los puntos de fallo que la implementación debe contemplar.

## Por qué saga y no transacción ACID

La transacción de "crear solicitud" toca al menos cuatro servicios: `auth-svc` (verificar bloqueo), `request-svc` (persistir solicitud), `inventory-svc` (reservar stock), `ai-risk-svc` (calcular score). Cada uno tiene su propia base de datos PostgreSQL. Una transacción distribuida 2PC entre cuatro bases es operativamente costosa y no escala. La saga reemplaza el commit atómico por una secuencia de pasos locales, cada uno con su propia compensación si el paso siguiente falla. La consistencia es eventual; el valor es que el sistema siempre converge a un estado válido.

## Coreografiada vs orquestada

En orquestación, un componente central (Temporal, AWS Step Functions, una máquina de estados explícita) dirige la saga, conoce todos los pasos y decide cuándo invocar cada servicio. En coreografía, no hay director: cada servicio reacciona a eventos publicados por otros y publica los suyos. La saga emerge de la conversación.

Se elige coreografía por tres razones (detalle en ADR-006):

1. **El flujo principal es lineal y estable**. No hay ramificaciones complejas que justifiquen un motor de workflow.
2. **El stack ya tiene broker y outbox**. Agregar Temporal sumaría una pieza operativa que no aporta sobre lo que ya hay.
3. **El equipo es de Magíster sin experiencia previa en motores de workflow**. La coreografía es directa de entender y de mantener con las herramientas que ya están en el repo.

El costo es que la saga "no vive en un solo lugar": para entenderla hay que leer este documento y los handlers de eventos repartidos por los servicios. Este documento es la respuesta a ese costo.

---

## Saga 1: solicitud → préstamo (camino feliz)

```
Alumno                Portal                request-svc        inventory-svc      ai-risk-svc       loan-svc        notification-svc
  │                     │                       │                    │                   │                │                  │
  │ crea solicitud      │                       │                    │                   │                │                  │
  ├────────────────────>│                       │                    │                   │                │                  │
  │                     │ POST /requests        │                    │                   │                │                  │
  │                     ├──────────────────────>│                    │                   │                │                  │
  │                     │                       │ Request-Reply      │                   │                │                  │
  │                     │                       ├───────────────────>│                   │                │                  │
  │                     │                       │<───── disponible ──┤                   │                │                  │
  │                     │                       │ Request-Reply                          │                │                  │
  │                     │                       ├───────────────────────────────────────>│                │                  │
  │                     │                       │<──────────── score ────────────────────┤                │                  │
  │                     │                       │ persiste solicitud + outbox            │                │                  │
  │                     │                       │ publica request.created                │                │                  │
  │                     │                       │ publica request.expire (delayed TTL)   │                │                  │
  │                     │<────── 201 OK ────────┤                    │                   │                │                  │
  │<── notif (in-app) ──┤                       │                    │                   │                │                  │
  │                     │                       │                    │ reserva stock     │                │                  │
  │                     │                       │                    │ (RC.06)           │                │                  │
  │                     │                       │                                                          │                  │
  │                     │                       │                                                          │  request.created │
  │                     │                       │                                                          │<─────────────────┤
  │                     │                       │                                                          │ persiste notif   │
  │                     │                       │                                                          │ push WebSocket   │
  │ presencia en pañol  │                       │                    │                   │                │                  │
  │ (≤ TTL)             │                       │                    │                   │                │                  │
  │                     │                                                                 │                │                  │
  │                     │ Tótem: panolero valida y materializa                            │                │                  │
  │                     ├────────────────────────────────────────────────────────────────>│                │                  │
  │                     │                       │                    │                   │ persiste loan  │                  │
  │                     │                       │                    │                   │ + outbox       │                  │
  │                     │                       │                    │                   │ publica loan.issued                │
  │                     │                       │                    │ descuenta stock   │                │                  │
  │                     │                       │                    │ definitivo        │                │                  │
  │                     │                       │                    │                   │                │ genera PDF       │
  │                     │                       │                    │                   │                │ entrega ticket   │
  │<── ticket PDF in-app │                      │                    │                   │                │                  │
```

### Pasos detallados

1. **Solicitud llega al portal**. Alumno arma la solicitud (con o sin asistente conversacional) y confirma. Portal hace `POST /requests` al API Gateway.
2. **Validaciones síncronas en `request-svc`**. Verifica blacklist (consulta a `auth-svc` por HTTP interno), stock disponible (Request-Reply AMQP a `inventory-svc`), score de riesgo (Request-Reply AMQP a `ai-risk-svc`). Si cualquiera falla, retorna error 4xx al portal y no publica nada.
3. **Persistencia local + outbox**. La transacción Postgres en `request-svc` hace dos cosas atómicamente: persiste la solicitud con estado `RESERVADA`, e inserta dos filas en `outbox_events`: `request.created` y un `request.expire` con `x-delay=ttl_ms`.
4. **Relay publica al broker**. El relay de outbox toma las filas pending y las publica. `request.created` al exchange `domain.events`; `request.expire` al exchange `domain.delayed`.
5. **`inventory-svc` consume `request.created`**. Marca el stock como reservado (no descuenta).
6. **`notification-svc` consume `request.created`**. Persiste notificación in-app y la empuja por WebSocket al alumno.
7. **El alumno se presenta en el pañol**. El pañolero abre el tótem, busca la solicitud por documento, valida ítem por ítem (RF.7), reingresa PIN (RF-C.09) y confirma materialización.
8. **`loan-svc` materializa**. Verifica que la solicitud esté en estado `RESERVADA` y dentro del TTL. Persiste el préstamo + outbox de `loan.issued`. Marca la solicitud como `MATERIALIZADA`.
9. **`inventory-svc` consume `loan.issued`**. Descuenta stock definitivo. Si cruza umbral, publica `stock.low`.
10. **`notification-svc` consume `loan.issued`**. Genera PDF con PDFKit, persiste notificación, entrega ticket.

### Saga 2: devolución

Mismo patrón. El pañolero registra devolución; `loan-svc` publica `loan.returned`; `inventory-svc` reabre stock y publica `stock.lost` si hay faltante; `notification-svc` genera PDF de devolución.

---

## Compensaciones

La saga no usa compensaciones explícitas en el camino feliz porque cada paso es local y reversible por el siguiente evento del flujo. Sin embargo, hay tres puntos donde la coreografía debe lidiar con desviaciones.

### Caso 1: TTL de reserva expira

Si el alumno no se presenta antes del TTL, el mensaje delayed llega a `request-svc`. El handler verifica el estado actual de la solicitud:

- Si está en `RESERVADA`, la marca como `EXPIRADA` y publica `request.expired`. `inventory-svc` libera la reserva y publica `stock.changed` (motivo `LIBERACION_RESERVA`). `notification-svc` avisa al usuario.
- Si está en `MATERIALIZADA` o `CANCELADA`, descarta el mensaje (idempotencia). No hay efecto.

No hay compensación que ejecutar contra `loan-svc` porque nunca creó nada.

### Caso 2: el pañolero materializa solicitud parcialmente

El alumno solicitó 3 unidades de un recurso pero el pañolero entrega solo 2 (RF-C.06). `loan-svc` registra el préstamo con la cantidad efectiva y publica `loan.issued` con la lista real de ítems. `inventory-svc` descuenta exactamente lo entregado, no lo solicitado. La solicitud queda como `MATERIALIZADA_PARCIAL`. La unidad faltante de la reserva se libera. No hay compensación porque el negocio acepta el resultado parcial como válido.

### Caso 3: fallo de un consumidor downstream

Si `inventory-svc` falla repetidamente al procesar `loan.issued` (bug, BD caída, etc.), el mensaje termina en `domain.dlx` tras 3 reintentos con backoff. La saga queda en estado inconsistente: `loan-svc` cree que prestó, pero `inventory-svc` no descontó. Esto se detecta con dos mecanismos:

- **Reconciliación automática nocturna**. Un job (en `inventory-svc`) compara stock contra préstamos abiertos y registra discrepancias en una tabla `stock_reconciliation`. Genera alerta in-app al Jefe de Carrera.
- **Re-publicación manual desde DLQ**. Una vez resuelto el bug, los mensajes muertos se reinyectan al exchange `domain.events` con un script administrativo. La idempotencia del consumidor garantiza que el reproceso es seguro.

No hay compensación en `loan-svc` (revertir el préstamo) porque el caso es operativamente excepcional y revertir un préstamo ya entregado físicamente al alumno no tiene sentido.

---

## Estados y transiciones

### Solicitud (`request-svc`, RC.16)

```
[Borrador] ──(usuario confirma)──> [Reservada] ──(materializada)──> [Materializada]
                │                       │
                │                       ├─(TTL vence)───> [Expirada]
                │                       └─(usuario/operador cancela)──> [Cancelada]
                └─(usuario descarta)──> [Eliminada]
```

`Materializada` y `Materializada_Parcial` son ambas estado final. Una solicitud `Especial multi-día` (RF-C.05) tiene un estado adicional `Pendiente_Aprobacion` antes de `Reservada`.

### Préstamo (`loan-svc`, RC.17)

```
[Activo] ──(devuelto OK)──> [Cerrado_OK]
   │
   ├─(devuelto con faltante)──> [Cerrado_Faltante]
   ├─(devuelto con daño)──> [Cerrado_Danado]
   └─(fechaLimite < now)──> [Atrasado] ──(devuelto)──> [Cerrado_*]
```

`Atrasado` es transitorio: el préstamo sigue siendo el mismo objeto, solo cambia un flag y dispara `loan.overdue`. Tres préstamos `Atrasado` en el semestre activan RC.01.

### Recurso (`inventory-svc`, RC.18)

```
[Disponible] ──(loan.issued)──> [Prestado] ──(loan.returned OK)──> [Disponible]
                                    │
                                    ├─(loan.returned dañado)──> [En_Mantencion] (RF-C.08)
                                    └─(loan.returned faltante)──> [Perdido] (alta de baja)
```

---

## Garantías y trade-offs

| Garantía | Cómo se obtiene |
|---|---|
| **Atomicidad cambio-evento** | Outbox pattern. La fila en `outbox_events` se inserta dentro de la misma transacción del cambio de estado. |
| **Entrega al menos una vez** | Acks manuales + reintentos con backoff. Mensajes que fallen 3 veces van al DLQ. |
| **Idempotencia de consumo** | Tabla `processed_events` por servicio. Ningún evento se procesa dos veces. |
| **Orden por solicitud** | `correlationId` propagado. Dentro de una saga concreta, el orden está garantizado por el flujo causal de eventos. |
| **Visibilidad operativa** | `x-trace-id` en headers AMQP, OpenTelemetry, Grafana Tempo. Una saga completa se reconstruye en el visor de trazas. |

| Trade-off aceptado | Justificación |
|---|---|
| **Consistencia eventual** | El usuario ve la solicitud creada antes de que `inventory-svc` haya marcado la reserva. La ventana es de centenas de ms; no afecta UX. |
| **Saga distribuida en código** | No hay un único archivo "esta es la saga". Compensa el documento que estás leyendo y los diagramas de secuencia (tarea #8). |
| **DLQ requiere intervención manual** | No hay reproceso automático en MVP. El volumen esperado (mesa redonda + producción inicial pequeña) no lo justifica. Se documenta como deuda técnica controlada. |

---

## Defensa en mesa redonda

Las preguntas previsibles del jurado y sus respuestas cortas:

**¿Por qué no usar Temporal o un orquestador?**  
La saga es lineal, sin ramificaciones complejas. Agregar Temporal traería un componente operacional adicional que no aporta sobre lo que el broker ya da. ADR-006 documenta el descarte.

**¿Qué pasa si `inventory-svc` está caído cuando se crea una solicitud?**  
El paso síncrono de validación de disponibilidad falla con timeout (2 s). `request-svc` retorna error al portal y no se publica nada. El alumno reintenta más tarde.

**¿Y si `inventory-svc` cae después de aceptada la solicitud, antes de reservar?**  
El evento `request.created` está persistido en outbox. Cuando `inventory-svc` se recupera, su consumidor lee el mensaje en cola y reserva el stock. El TTL de la reserva no se vio afectado porque no es el broker quien lo cuenta; es el mensaje delayed publicado al inicio.

**¿Qué garantiza que dos pañoleros no materialicen la misma solicitud al mismo tiempo?**  
Concurrencia optimista en `loan-svc`: la transacción que cambia el estado de la solicitud usa `WHERE estado = 'RESERVADA'` y verifica el rowcount. El segundo pañolero recibe un error de conflicto.

**¿Cómo recuperan si un evento crítico se pierde?**  
No se pierde por diseño (outbox + acks manuales + DLQ). Si por error humano se descarta un mensaje, la reconciliación nocturna lo detecta y un script administrativo lo reinyecta.
