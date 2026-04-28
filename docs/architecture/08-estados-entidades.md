# Estados de las entidades principales

## Propósito

Este documento define las **máquinas de estado** de las entidades centrales del Sistema de Pañol. Para cada entidad declara: sus estados, las transiciones válidas, los eventos o acciones que las disparan, las guardias (preconditions), el servicio que es dueño de la máquina, y los estados terminales. Es la referencia normativa para implementación, testing y diagramas `.drawio` (STATE-*).

Las reglas de negocio que sustentan los estados están en `05-reglas-de-negocio.md`. Los eventos que disparan transiciones están contratados en `03-eventos-dominio.md`. La propiedad de cada entidad se declara en `07-microservicios-responsabilidades.md`.

## Convenciones

- **Estado inicial**: se marca con `[*]` en notación UML y con "inicial" en prosa.
- **Estado terminal**: no admite transiciones salientes. Se marca con doble borde en los diagramas `.drawio`.
- **Guardia** (`guard`): condición que debe cumplirse para que la transición se ejecute. Se escribe entre corchetes, ej. `[ttlExpirado]`.
- **Disparador**: evento externo o acción de usuario que inicia la transición. Se escribe antes de `/`.
- **Efecto**: acción colateral al transicionar. Se escribe después de `/`.
- Nomenclatura: `disparador [guard] / efecto`.

---

## 1. Usuario

**Servicio dueño**: `auth-svc`.  
**Archivo**: `STATE-01-usuario.drawio`.  
**Referencias**: RC.01, RC.08, RC.10, RC.13, RC.15, RF-C.10, ADR-011, ADR-014.

### Estados

| Estado | Descripción |
|---|---|
| `CREADO` | **Inicial**. Usuario creado por alta individual o importación masiva. Clave inicial asignada. Aún no ingresó al sistema. |
| `PENDIENTE_CAMBIO_CLAVE` | Se autenticó con clave inicial pero no la ha cambiado. No puede acceder a funcionalidades (RF-C.10). |
| `ACTIVO` | Estado operativo normal. Puede usar todas las funcionalidades según su rol. |
| `BLOQUEADO_MOROSIDAD` | Bloqueo automático por cumplir RC.01. Puede autenticarse y leer su historial; no puede crear solicitudes (RC.15). |
| `BLOQUEADO_ADMINISTRATIVO` | Bloqueo manual por Coord/Jefe por motivo declarado en texto libre (RC.10). Mismas restricciones que el anterior. |
| `INACTIVO` | Baja lógica (CN.03). Conservado para auditoría. No puede autenticarse. |

### Transiciones

| Desde | Hacia | Disparador | Guard / Efecto |
|---|---|---|---|
| — | `CREADO` | `auth-svc` procesa alta individual o importación | / publica `user.created` |
| `CREADO` | `PENDIENTE_CAMBIO_CLAVE` | login exitoso con clave inicial | |
| `PENDIENTE_CAMBIO_CLAVE` | `ACTIVO` | usuario cambia clave exitosamente | |
| `ACTIVO` | `BLOQUEADO_MOROSIDAD` | consumo de `loan.overdue` evalúa RC.01 y se cumple | [RC.01 se cumple] / publica `user.blocked` reason=MOROSIDAD_AUTOMATICA |
| `ACTIVO` | `BLOQUEADO_ADMINISTRATIVO` | Coord/Jefe bloquea manualmente | [motivo obligatorio] / publica `user.blocked` reason=ADMINISTRATIVO |
| `BLOQUEADO_MOROSIDAD` | `ACTIVO` | cool-off 30 días vence (o Coord/Jefe desbloquea) | / publica `user.unblocked` |
| `BLOQUEADO_ADMINISTRATIVO` | `ACTIVO` | Coord/Jefe desbloquea manualmente | / publica `user.unblocked` |
| `ACTIVO` | `INACTIVO` | Coord/Jefe da de baja (RS-JC.2) | / publica `user.deactivated` |
| `BLOQUEADO_*` | `INACTIVO` | Coord/Jefe da de baja | / publica `user.deactivated` |

### Estado terminal

`INACTIVO`. No hay reactivación en MVP; si el usuario vuelve, se crea un usuario nuevo (respetando unicidad del par `documento_tipo, documento_valor`).

### Permisos por estado (resumen)

| Estado | Puede loguearse | Puede usar portal | Puede crear solicitud | Puede operar tótem (si es Pañolero) |
|---|---|---|---|---|
| `CREADO` | Sí | Forzado a `PENDIENTE_CAMBIO_CLAVE` | No | No |
| `PENDIENTE_CAMBIO_CLAVE` | Sí (modal clave) | Solo para cambiar clave | No | No |
| `ACTIVO` | Sí | Sí | Sí | Sí (según rol) |
| `BLOQUEADO_*` | Sí | Sí (modo lectura, historial) | No | No |
| `INACTIVO` | No | — | — | — |

---

## 2. Solicitud

**Servicio dueño**: `request-svc`.  
**Archivo**: `STATE-02-solicitud.drawio`.  
**Referencias**: RC.06, RC.16, RF-C.01, RF-C.04, RF-C.05, RF-C.06, RF-C.13, ADR-010.

### Estados

| Estado | Descripción |
|---|---|
| `BORRADOR` | **Inicial opcional**. Creado por el asistente conversacional. No reserva stock. Auto-expira en 24 h. |
| `PENDIENTE` | Creada y confirmada por el usuario; stock reservado con TTL (RC.06). Esperando materialización en el tótem. |
| `PENDIENTE_APROBACION` | Solo para `ESPECIAL_MULTIDIA` (RF-C.05). Esperando decisión de Coord/Jefe. Stock no reservado todavía. |
| `APROBADA` | Especial aprobada. Stock reservado con TTL = plazo acordado. Equivalente funcional a `PENDIENTE` para el flujo de materialización. |
| `RECHAZADA` | Especial rechazada por Coord/Jefe. **Terminal**. |
| `MATERIALIZADA` | Todos los ítems solicitados se entregaron efectivamente. **Terminal**. |
| `MATERIALIZADA_PARCIAL` | Subconjunto de los ítems se entregó (RF-C.06). Los no entregados quedan con cantidadEntregada=0. **Terminal**. |
| `VENCIDA` | TTL expiró sin materialización. **Terminal**. |
| `CANCELADA` | Cancelada por el usuario o por un operador antes de materializar. **Terminal**. |

### Transiciones

| Desde | Hacia | Disparador | Guard / Efecto |
|---|---|---|---|
| — | `BORRADOR` | asistente invoca `crear_solicitud_borrador` | |
| `BORRADOR` | — | 24 h sin confirmación | / se elimina el draft |
| — | `PENDIENTE` | usuario confirma solicitud estándar | [validaciones RF-C.04 pasan: no bloqueado, stock disponible, score aceptable] / publica `request.created` + mensaje `request.expire` delayed |
| — | `PENDIENTE_APROBACION` | usuario confirma solicitud Especial | [mismas validaciones] / publica `request.pending_approval` |
| `PENDIENTE_APROBACION` | `APROBADA` | Coord/Jefe aprueba | / publica `request.approved` + reserva stock con TTL = plazo acordado |
| `PENDIENTE_APROBACION` | `RECHAZADA` | Coord/Jefe rechaza | / publica `request.rejected` |
| `PENDIENTE` | `MATERIALIZADA` | `loan.issued` confirma entrega completa | [todos los ítems con cantidadEntregada == cantidadSolicitada] / sin efecto adicional |
| `APROBADA` | `MATERIALIZADA` | `loan.issued` confirma entrega completa | [igual] |
| `PENDIENTE` | `MATERIALIZADA_PARCIAL` | `loan.issued` confirma entrega parcial (RF-C.06) | [al menos un ítem con cantidadEntregada < cantidadSolicitada] / libera reserva del faltante |
| `APROBADA` | `MATERIALIZADA_PARCIAL` | `loan.issued` confirma entrega parcial | [igual] |
| `PENDIENTE` | `VENCIDA` | handler recibe `request.expire` delayed | [estado sigue PENDIENTE] / publica `request.expired` |
| `APROBADA` | `VENCIDA` | handler recibe `request.expire` delayed | [estado sigue APROBADA] / publica `request.expired` |
| `PENDIENTE` | `CANCELADA` | usuario cancela desde el portal | / publica `request.cancelled` reason=USUARIO |
| `PENDIENTE` | `CANCELADA` | operador (Pañolero/Coord) cancela desde tótem/portal | / publica `request.cancelled` reason=OPERADOR |
| `PENDIENTE_APROBACION` | `CANCELADA` | usuario cancela | / publica `request.cancelled` reason=USUARIO |
| `APROBADA` | `CANCELADA` | usuario u operador cancela | / publica `request.cancelled` |
| `PENDIENTE` | `CANCELADA` | consumidor de `user.blocked` | [usuario fue bloqueado] / publica `request.cancelled` reason=USER_BLOCKED |

### Estados terminales

`MATERIALIZADA`, `MATERIALIZADA_PARCIAL`, `VENCIDA`, `CANCELADA`, `RECHAZADA`.

### Idempotencia de la expiración

El handler del mensaje `request.expire` delayed es idempotente: si la solicitud ya está en estado terminal distinto de PENDIENTE/APROBADA, el mensaje se descarta sin efecto.

---

## 3. Préstamo

**Servicio dueño**: `loan-svc`.  
**Archivo**: `STATE-03-prestamo.drawio`.  
**Referencias**: RC.01, RC.02, RC.07, RC.17, RF-C.07, RS-PN.4.

### Estados

| Estado | Descripción |
|---|---|
| `EN_CURSO` | **Inicial**. Préstamo emitido; recursos fueron entregados; aún no devuelto. |
| `ATRASADO` | Estado transitorio: `fechaLimite < now()` y el préstamo sigue abierto. Visible como flag y dispara `loan.overdue`. Sigue siendo "abierto" operativamente. |
| `DEVUELTO` | Devolución correcta: todos los ítems con estado `BUENO` o `DAÑADO_MENOR`. **Terminal**. |
| `DEVUELTO_CON_FALTANTE` | Devolución con al menos un ítem en `FALTANTE` o `DAÑADO_MAYOR`. **Terminal**. |
| `ANULADO` | Anulado por el Pañolero (RS-PN.4) antes de que el usuario retire físicamente los recursos. **Terminal**. |

### Transiciones

| Desde | Hacia | Disparador | Guard / Efecto |
|---|---|---|---|
| — | `EN_CURSO` | Pañolero materializa en el tótem | [solicitud PENDIENTE o APROBADA, dentro de TTL, PIN validado] / publica `loan.issued` |
| `EN_CURSO` | `ATRASADO` | job periódico detecta `fechaLimite < now` | / publica `loan.overdue` (una vez por día) |
| `ATRASADO` | `EN_CURSO` | (no transita de vuelta; `ATRASADO` es un "flag" sobre `EN_CURSO`) | — |
| `EN_CURSO` / `ATRASADO` | `DEVUELTO` | Pañolero registra devolución sin incidencias | [todos los ítems `BUENO` o `DAÑADO_MENOR`, PIN validado] / publica `loan.returned` |
| `EN_CURSO` / `ATRASADO` | `DEVUELTO_CON_FALTANTE` | Pañolero registra devolución con incidencia | [al menos un ítem `FALTANTE` o `DAÑADO_MAYOR`, PIN validado] / publica `loan.returned` + `stock.lost` en `inventory-svc` |
| `EN_CURSO` | `ANULADO` | Pañolero anula (cliente no apareció físicamente) | [PIN validado, motivo obligatorio] / publica `loan.annulled` + rollback de stock |

### Aclaración sobre `ATRASADO`

En la implementación, `ATRASADO` no es un cambio del campo `estado` sino un flag derivable del mismo: `estado == EN_CURSO AND fechaLimite < now()`. Se expone como estado en las consultas y en la UI para claridad, pero internamente el estado base sigue siendo `EN_CURSO`. El job que publica `loan.overdue` usa la deduplicación `loanId + fecha(detectedAt)` para emitir un solo evento por día por préstamo.

### Estados terminales

`DEVUELTO`, `DEVUELTO_CON_FALTANTE`, `ANULADO`.

### Interacción con morosidad (RC.01)

Un préstamo que devuelve con atraso > 24 h, o 2 préstamos con atraso > 6 h, o 1 con `FALTANTE` en el semestre en curso, gatillan `loan.overdue` agregado que `auth-svc` evalúa para bloquear al usuario. Esto es evento fuera de la máquina del préstamo, pero dispara el cambio de estado del Usuario hacia `BLOQUEADO_MOROSIDAD`.

---

## 4. Recurso

**Servicio dueño**: `inventory-svc`.  
**Archivo**: `STATE-04-recurso.drawio`.  
**Referencias**: RC.03, RC.09, RC.18, RF-C.08.

### Estados

| Estado | Descripción |
|---|---|
| `ACTIVO` | **Inicial**. Disponible para ser solicitado (si hay stock). |
| `EN_MANTENCION` | Temporalmente no asignable (RF-C.08). No aparece en listados de solicitud. Puede reactivarse. |
| `BAJA` | Fuera del inventario permanentemente. Registro histórico conservado (CN.03). **Terminal**. |

### Transiciones

| Desde | Hacia | Disparador | Guard / Efecto |
|---|---|---|---|
| — | `ACTIVO` | alta por Pañolero o Jefe | / publica `resource.created`; emite `stock.changed` motivo=ALTA |
| `ACTIVO` | `EN_MANTENCION` | Pañolero o Jefe marca En Mantención | / publica `resource.maintenance.started` |
| `EN_MANTENCION` | `ACTIVO` | Pañolero o Jefe reactiva | / publica `resource.maintenance.ended` |
| `ACTIVO` | `BAJA` | Pañolero o Jefe da de baja | [motivo obligatorio] / publica `resource.deactivated` + `stock.changed` motivo=BAJA |
| `EN_MANTENCION` | `BAJA` | Pañolero o Jefe da de baja | [motivo obligatorio] / publica `resource.deactivated` |

### Estado terminal

`BAJA`. Un recurso en BAJA no puede volver a ACTIVO. Si se reincorpora la misma tipología al inventario, se crea un recurso nuevo con su propio identificador, preservando la historia.

### Relación con stock

Los niveles de stock (`NORMAL`, `BAJO`, `CRITICO` según RC.05) son una dimensión **derivada**, no un estado principal del recurso. Se calculan como `f(stockActual, stockMaximoHistorico)` y se publican como eventos (`stock.low`, `stock.normalized`) cuando cruzan umbrales, pero el recurso sigue siendo `ACTIVO`.

---

## 5. Reserva de stock

**Servicio dueño**: `inventory-svc` (reservación); `request-svc` (ciclo de vida disparador).  
**Archivo**: `STATE-05-reserva-stock.drawio`.  
**Referencias**: RC.06, RC.12, RF-C.01, ADR-010.

### Contexto

Cada `request_item` con cantidad N genera N unidades de reserva sobre un recurso específico. La reserva vive dentro de `inventory-svc` (`stock_reservations`). Su ciclo está sincronizado con el ciclo de la solicitud que la originó, pero es una entidad con identidad propia y máquina de estado diferenciada porque representa una "promesa" de stock, no el préstamo efectivo.

### Estados

| Estado | Descripción |
|---|---|
| `ACTIVA` | **Inicial**. Stock retenido, no descontado. Cuenta contra disponibilidad pero el inventario real no bajó. |
| `CONSUMIDA` | El préstamo se materializó. El stock se descontó definitivamente. **Terminal**. |
| `LIBERADA_POR_EXPIRACION` | TTL venció sin materialización. Stock vuelve a disponible. **Terminal**. |
| `LIBERADA_POR_CANCELACION` | Solicitud fue cancelada antes de materializar. Stock vuelve a disponible. **Terminal**. |
| `LIBERADA_PARCIAL` | En materialización parcial (RF-C.06): parte del ítem se consume y parte se libera. La reserva original se divide en una CONSUMIDA + una LIBERADA_POR_CANCELACION efectiva. **Terminal**. |

### Transiciones

| Desde | Hacia | Disparador | Guard / Efecto |
|---|---|---|---|
| — | `ACTIVA` | consumo de `request.created` o `request.approved` | [stock disponible; lock optimista OK] / descuenta disponibilidad |
| `ACTIVA` | `CONSUMIDA` | consumo de `loan.issued` con cantidad completa | / descuenta stock real; publica `stock.changed` motivo=PRESTAMO |
| `ACTIVA` | `LIBERADA_PARCIAL` | consumo de `loan.issued` con cantidad < reservada | / descuenta el parcial; reincorpora el resto a disponibilidad |
| `ACTIVA` | `LIBERADA_POR_EXPIRACION` | consumo de `request.expired` | / reincorpora todo a disponibilidad; publica `stock.changed` motivo=LIBERACION_RESERVA |
| `ACTIVA` | `LIBERADA_POR_CANCELACION` | consumo de `request.cancelled` | / igual que el anterior |

### Invariante de concurrencia (RC.12)

El paso — → `ACTIVA` usa lock optimista con campo `version` sobre `resources`. Si dos solicitudes compiten por el último ejemplar, solo una obtiene la reserva; la otra recibe error de concurrencia y el caller (request-svc) retorna error 409 al usuario sin haber publicado `request.created`.

### Estados terminales

`CONSUMIDA`, `LIBERADA_POR_EXPIRACION`, `LIBERADA_POR_CANCELACION`, `LIBERADA_PARCIAL`.

---

## 6. Notificación

**Servicio dueño**: `notification-svc`.  
**Archivo**: no se genera diagrama dedicado en este entrega (máquina muy simple; se documenta en texto).  
**Referencias**: ADR-007, RF.10, RF.11, RF.12.

### Estados

| Estado | Descripción |
|---|---|
| `PENDIENTE_ENTREGA` | **Inicial**. Persistida en `notifications` tras consumir un evento de dominio. Aún no se envió por WebSocket. |
| `ENTREGADA` | Entregada en tiempo real al cliente WebSocket. |
| `NO_ENTREGADA_EN_VIVO` | Usuario no tenía sesión WebSocket activa. Queda como "no leída" en bandeja para verse al siguiente login. |
| `LEIDA` | Usuario marcó como leída desde el portal. |
| `EXPIRADA` | TTL de 90 días venció. Archivada o eliminada. **Terminal**. |

### Transiciones resumidas

- `— → PENDIENTE_ENTREGA`: al persistir la notificación resultante del Content-Based Router.
- `PENDIENTE_ENTREGA → ENTREGADA`: emisión WebSocket exitosa + ack del cliente.
- `PENDIENTE_ENTREGA → NO_ENTREGADA_EN_VIVO`: si el usuario no está conectado.
- `ENTREGADA | NO_ENTREGADA_EN_VIVO → LEIDA`: al marcar como leída.
- `cualquiera → EXPIRADA`: job de limpieza a los 90 días.

Este ciclo no se considera crítico para la integridad del sistema y su diagrama de estado se omite en la entrega MVP.

---

## Resumen

| Entidad | Servicio dueño | Estado inicial | Terminales | Diagrama |
|---|---|---|---|---|
| Usuario | auth-svc | CREADO | INACTIVO | STATE-01 |
| Solicitud | request-svc | BORRADOR / PENDIENTE / PENDIENTE_APROBACION | MATERIALIZADA, MATERIALIZADA_PARCIAL, VENCIDA, CANCELADA, RECHAZADA | STATE-02 |
| Préstamo | loan-svc | EN_CURSO | DEVUELTO, DEVUELTO_CON_FALTANTE, ANULADO | STATE-03 |
| Recurso | inventory-svc | ACTIVO | BAJA | STATE-04 |
| Reserva de stock | inventory-svc | ACTIVA | CONSUMIDA, LIBERADA_*  | STATE-05 |
| Notificación | notification-svc | PENDIENTE_ENTREGA | EXPIRADA | (no diagrama) |

Los archivos `.drawio` de estos diagramas viven en `docs/design/diagrams/` y siguen las convenciones visuales declaradas en el README de ese directorio.
