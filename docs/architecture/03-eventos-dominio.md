# Eventos de dominio

## Propósito

Este documento es el contrato formal de los eventos que los microservicios publican y consumen a través de RabbitMQ. Cada evento declara: qué lo dispara, qué payload lleva, qué servicios lo consumen y qué patrón EIP lo transporta (detalle del patrón en `04-eip-catalog.md`). Es la fuente de verdad que usa `libs/events/` del monorepo para generar los esquemas Zod compartidos por los servicios.

## Convenciones

### Nomenclatura

Las routing keys siguen la forma `<dominio>.<verbo-en-pasado>`. Ejemplos: `request.created`, `loan.returned`, `stock.low`. El verbo siempre en pasado porque un evento es un hecho consumado; si alguien necesita expresar una intención (`please-do-X`), es un comando, no un evento, y va por el exchange `domain.commands`.

### Exchange único `domain.events`

Todos los eventos de dominio se publican en el exchange `domain.events` (tipo `topic`). Las colas de los consumidores se enlazan con patrones (`inventory.*`, `loan.#`, `stock.low`) para implementar Content-Based Router sin código aplicativo.

### Headers obligatorios

Todo mensaje AMQP publicado incluye los siguientes headers para observabilidad y trazabilidad:

| Header | Uso |
|---|---|
| `x-trace-id` | OpenTelemetry trace id propagado desde el origen. Permite reconstruir un flujo completo atravesando servicios. |
| `x-correlation-id` | Correlaciona conversaciones de negocio (por ejemplo, todos los eventos de una misma solicitud). |
| `x-schema-version` | Versión del esquema del payload. Habilita evolución sin romper consumidores. |
| `x-source-service` | Servicio que publica. Redundante con el routing key pero útil para filtrado en DLQ. |
| `x-published-at` | Timestamp ISO-8601 UTC. Independiente del timestamp de persistencia del broker. |

### Versionado

Los payloads se versionan con semantic versioning por dominio. Cambios retrocompatibles (agregar campo opcional) suben el minor; cambios que rompen consumidores suben el major y requieren que los consumidores declaren explícitamente qué versión aceptan. El header `x-schema-version` transporta la versión.

### Idempotencia

Todo consumidor debe tratar los eventos como "al menos una vez" y deduplicar por `(x-source-service, eventId)` contra una tabla local `processed_events`. Esto habilita reintentos del broker sin efectos duplicados.

### Outbox pattern

Los eventos no se publican directamente desde el código de dominio. El servicio persiste el evento en su tabla `outbox_events` dentro de la misma transacción que el cambio de estado de negocio. Un relay (`@nestjs/schedule` cada 500 ms) toma los eventos `status='pending'` y los publica al broker; al éxito los marca `status='published'`. Garantiza que no haya evento sin cambio ni cambio sin evento.

---

## Catálogo de eventos

### Dominio `user` (auth-svc)

#### `user.created`

| Campo | Tipo | Descripción |
|---|---|---|
| `userId` | UUID | Identificador del usuario creado. |
| `role` | enum | `JEFE` / `COORDINADOR` / `PANOLERO` / `DOCENTE` / `ALUMNO`. |
| `documento` | string | ID sin RUT chileno (RC.04). |
| `carreraId` | UUID nullable | Carrera asociada (solo para Alumno/Docente). |
| `createdBy` | UUID | Operador que creó el registro. |
| `createdAt` | ISO-8601 | Timestamp de creación. |

**Publica**: `auth-svc` tras crear un usuario (individual o por importación Excel).  
**Consumen**: `notification-svc` (saludo personalizado — RS.3), `ai-risk-svc` (para inicializar perfil de riesgo base), `reports-svc` (proyección `proyeccion_usuarios`).

#### `user.blocked` / `user.unblocked`

| Campo | Tipo | Descripción |
|---|---|---|
| `userId` | UUID | Usuario afectado. |
| `reason` | enum | `MOROSIDAD_AUTOMATICA` (RC.01) / `ADMINISTRATIVO` (RC.10). |
| `motivo` | string | Texto libre del operador (obligatorio si `reason=ADMINISTRATIVO`). |
| `blockedBy` | UUID nullable | `null` si la regla automática lo gatilló. |
| `effectiveAt` | ISO-8601 | |

**Publica**: `auth-svc` (al persistir el bloqueo, incluso si fue gatillado por `loan-svc`).  
**Consumen**: `request-svc` (para rechazar solicitudes futuras — RC.15), `notification-svc` (informar al usuario), `ai-assistant-svc` (el asistente debe negarse a ayudar a un moroso), `reports-svc` (actualiza proyección de usuarios).

---

### Dominio `inventory` (inventory-svc)

#### `stock.changed`

| Campo | Tipo | Descripción |
|---|---|---|
| `recursoId` | UUID | Recurso afectado. |
| `delta` | integer | Unidades que entraron (+) o salieron (−). |
| `stockActual` | integer | Stock resultante. |
| `motivo` | enum | `PRESTAMO` / `DEVOLUCION` / `ALTA` / `BAJA` / `PERDIDA` / `AJUSTE_MANTENCION`. |
| `loanId` | UUID nullable | Si aplica. |

**Publica**: `inventory-svc` cada vez que cambia el stock de un recurso (transición RC.18).  
**Consumen**: `notification-svc` (si cruza umbral, emite alerta), `reports-svc` (proyección de stock y recursos top).

#### `stock.low`

| Campo | Tipo | Descripción |
|---|---|---|
| `recursoId` | UUID | |
| `nivel` | enum | `BAJO` / `CRITICO` (RC.05). Un evento `stock.low` solo se publica cuando el stock cruza el umbral descendente. La transición de retorno a `NORMAL` (al reponer stock) se notifica con el evento separado `stock.normalized` (mismo payload, mismo patrón), que permite a `notification-svc` cerrar alertas abiertas sin ambigüedad semántica en el nombre del evento. |
| `stockActual` | integer | |
| `umbral` | integer | Umbral configurado para ese recurso. |

**Publica**: `inventory-svc` cuando una transición de stock cruza el umbral descendente (histéresis de un evento por transición, sin rebotes). El evento simétrico `stock.normalized` se publica al cruzar el umbral en sentido ascendente.  
**Consumen**: `notification-svc` (alerta a Jefe, Coord y Pañolero — RS.1, RF.12; `stock.normalized` cierra la alerta), `reports-svc` (estado actual del indicador).

#### `stock.lost`

| Campo | Tipo | Descripción |
|---|---|---|
| `recursoId` | UUID | |
| `cantidad` | integer | Unidades declaradas como pérdida o daño. |
| `loanId` | UUID | Préstamo que originó la pérdida. |
| `usuarioId` | UUID | Responsable del préstamo. |
| `tipo` | enum | `FALTANTE` / `DANADO_NO_FUNCIONAL`. |

**Publica**: `inventory-svc` al procesar una devolución con faltante o daño (RC.17, RF-C.07).  
**Consumen**: `loan-svc` (contabiliza contra morosidad — RC.01), `notification-svc` (alerta), `reports-svc` (proyección de pérdidas por recurso).

---

### Dominio `request` (request-svc)

#### `request.created`

| Campo | Tipo | Descripción |
|---|---|---|
| `requestId` | UUID | |
| `usuarioId` | UUID | Solicitante (no el operador si fue creada por otro — RF-C.13). |
| `operadorId` | UUID nullable | Si `creadaPorOperador=true`. |
| `creadaPorOperador` | boolean | RF-C.13. |
| `items` | array | `[{recursoId, cantidad, reservaId}]`. |
| `fechaRetiro` | ISO-8601 | |
| `ttlExpiresAt` | ISO-8601 | Momento en que expira la reserva (RC.06). |
| `riesgoScore` | float | 0..1 devuelto por `ai-risk-svc` (RC.11). |
| `tipoPrestamo` | enum | `NORMAL` / `ESPECIAL_MULTIDIA` (RC.02, RF-C.05). |

**Publica**: `request-svc` tras validar disponibilidad (Request-Reply con `inventory-svc`), consultar scoring (Request-Reply con `ai-risk-svc`) y aplicar RC.01/RC.10/RC.11.  
**Consumen**: `inventory-svc` (marca la reserva como activa), `notification-svc` (confirma al usuario), `ai-assistant-svc` (actualiza contexto conversacional), `reports-svc` (proyección de solicitudes por recurso y período).

#### `request.cancelled`

| Campo | Tipo | Descripción |
|---|---|---|
| `requestId` | UUID | |
| `cancelledBy` | UUID nullable | `null` si fue cancelada por sistema. |
| `reason` | enum | `USUARIO` / `OPERADOR` / `APROBACION_DENEGADA` (para Especial — RF-C.05). |
| `cancelledAt` | ISO-8601 | |

**Publica**: `request-svc`.  
**Consumen**: `inventory-svc` (libera reserva), `notification-svc` (informa al usuario), `reports-svc` (actualiza proyección de solicitudes).

#### `request.expired`

| Campo | Tipo | Descripción |
|---|---|---|
| `requestId` | UUID | |
| `expiredAt` | ISO-8601 | |

**Publica**: `request-svc` tras recibir el mensaje delayed del exchange `domain.delayed` (Message Expiration).  
**Consumen**: `inventory-svc` (libera reserva), `notification-svc` (avisa al usuario), `reports-svc` (actualiza proyección de solicitudes).

---

### Dominio `loan` (loan-svc)

#### `loan.issued`

| Campo | Tipo | Descripción |
|---|---|---|
| `loanId` | UUID | |
| `requestId` | UUID | Solicitud materializada. |
| `usuarioId` | UUID | |
| `items` | array | `[{recursoId, cantidad}]` efectivamente entregados (puede ser parcial — RF-C.06). |
| `fechaLimite` | ISO-8601 | Según RC.02. |
| `panoleroId` | UUID | Operador del tótem que materializó. |
| `issuedAt` | ISO-8601 | |
| `ticketId` | string | Correlativo generado por el sistema (RC.07). |

**Publica**: `loan-svc` tras materializar en el tótem.  
**Consumen**: `inventory-svc` (descuenta stock definitivamente), `notification-svc` (genera PDF y entrega ticket), `reports-svc` (proyección de recursos top y agregados de préstamos).

#### `loan.returned`

| Campo | Tipo | Descripción |
|---|---|---|
| `loanId` | UUID | |
| `itemsReturned` | array | `[{recursoId, cantidad, estado}]` con estado `OK` / `DANADO` / `FALTANTE` (RC.17). |
| `returnedAt` | ISO-8601 | |
| `panoleroId` | UUID | |
| `ticketDevolucionId` | string | Correlativo del ticket de devolución. |

**Publica**: `loan-svc` al registrar devolución en el tótem.  
**Consumen**: `inventory-svc` (reabre stock y publica `stock.lost` si corresponde), `notification-svc` (PDF de devolución), `reports-svc` (proyección de devoluciones tardías por recurso y por usuario).

#### `loan.overdue`

| Campo | Tipo | Descripción |
|---|---|---|
| `loanId` | UUID | |
| `usuarioId` | UUID | |
| `diasAtraso` | integer | |
| `detectedAt` | ISO-8601 | |

**Publica**: `loan-svc` cuando un job periódico detecta que `fechaLimite < now()` y el préstamo sigue abierto.  
**Consumen**: `notification-svc` (alerta moroso — RF.11), `auth-svc` (evalúa bloqueo automático — RC.01, cuando se cumple el tercer atraso en el semestre), `reports-svc` (proyección de devoluciones tardías por usuario).

---

### Dominio `risk` (ai-risk-svc)

#### `risk.scored`

| Campo | Tipo | Descripción |
|---|---|---|
| `usuarioId` | UUID | |
| `requestId` | UUID nullable | Si el scoring se asoció a una solicitud específica. |
| `score` | float | 0..1. |
| `drivers` | array | Factores que más contribuyeron al score. |
| `modelVersion` | string | Para auditabilidad del modelo. |

**Publica**: `ai-risk-svc` asíncrono tras responder un scoring síncrono (Request-Reply). La respuesta síncrona decide el flujo; el evento es para registro y análisis.  
**Consumen**: `reports-svc` (auditoría del modelo, dataset de reentrenamiento).

---

### Dominio `notification` (notification-svc)

#### `notification.delivered`

| Campo | Tipo | Descripción |
|---|---|---|
| `notificationId` | UUID | |
| `usuarioId` | UUID | |
| `tipo` | enum | `REQUEST_CREADA` / `LOAN_EMITIDO` / `LOAN_DEVUELTO` / `STOCK_BAJO` / `MOROSIDAD` / `BLOQUEO` / `REQUEST_EXPIRADA`. |
| `canal` | enum | `IN_APP` (único en MVP). |
| `deliveredAt` | ISO-8601 | |

**Publica**: `notification-svc`.  
**Consumen**: `reports-svc` (efectividad de notificación), auditoría.

---

## Matriz evento ↔ patrón EIP ↔ exchange

| Evento | Patrón EIP | Exchange | Routing key |
|---|---|---|---|
| `user.*` | Publish-Subscribe | `domain.events` | `user.*` |
| `stock.changed` | Publish-Subscribe | `domain.events` | `stock.changed` |
| `stock.low` | Publish-Subscribe + Content-Based Router | `domain.events` | `stock.low` |
| `stock.normalized` | Publish-Subscribe | `domain.events` | `stock.normalized` |
| `stock.lost` | Publish-Subscribe | `domain.events` | `stock.lost` |
| `request.created` | Publish-Subscribe | `domain.events` | `request.created` |
| `request.cancelled` | Publish-Subscribe | `domain.events` | `request.cancelled` |
| `request.expired` | Message Expiration → Publish-Subscribe | `domain.delayed` → `domain.events` | `request.expired` |
| `loan.*` | Publish-Subscribe | `domain.events` | `loan.*` |
| `risk.scored` | Publish-Subscribe (asíncrono tras Request-Reply síncrono) | `domain.events` | `risk.scored` |
| `notification.delivered` | Publish-Subscribe | `domain.events` | `notification.delivered` |
| _Fallos de consumo_ | Dead Letter Channel | `domain.dlx` | (captura por fanout) |
| `request.validateDisponibilidad` | Request-Reply | `domain.commands` | `inventory.validate` |
| `risk.score` | Request-Reply | `domain.commands` | `risk.score` |

El patrón concreto, su configuración en RabbitMQ y su razón de ser están en `04-eip-catalog.md`.

---

## Evolución y compatibilidad

Cuando un evento deba evolucionar de forma no retrocompatible, se publican ambas versiones en paralelo durante un sprint. Los consumidores migran de `x-schema-version=1.x` a `2.0` y solo cuando todos estén migrados se deprecra la v1. La transición queda registrada en un ADR ad-hoc dentro de `docs/design/adrs/`.
