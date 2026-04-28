# Modelo de datos

## Propósito

Este documento describe el **modelo de datos** del Sistema de Pañol y cómo se distribuye entre las bases de cada microservicio. Es la referencia para:

- Generar las migraciones Prisma de cada servicio.
- Razonar sobre integridad transaccional dentro de un servicio versus consistencia eventual entre servicios.
- Defender en mesa redonda por qué hay 8 bases en lugar de una sola.

El diagrama formal vive en `docs/design/diagrams/ERD-01-modelo-datos.drawio`.

---

## Principio de diseño: database-per-service

Cada microservicio es **dueño exclusivo de su esquema**. No hay foreign keys físicas cruzando bases. Esto trae tres consecuencias que aceptamos conscientemente:

1. **Aislamiento operativo**: una migración de `auth_db` no puede romper a `loan-svc`. Cada servicio evoluciona su esquema sin coordinación global.
2. **Integridad por evento**: cuando `loan-svc` necesita saber el `usuario_id`, lo recibe en el payload del evento `request.created`. No hace `JOIN` con `auth_db`. Si el usuario fue dado de baja después, ese hecho llega como evento (`user.deactivated`) y se procesa.
3. **Lecturas agregadas via CQRS**: para reportes que cruzan dominios (p. ej. "préstamos por carrera por mes"), `reports-svc` mantiene proyecciones que copian campos relevantes de varios servicios. No hay `JOIN` distribuido en runtime.

Todo esto está formalizado en ADR-002 (Postgres-only), ADR-004 (microservicios vs monolito) y ADR-015 (reports-svc CQRS).

---

## Inventario de bases

| Base | Servicio dueño | Cardinalidad típica | Notas |
|---|---|---|---|
| `auth_db` | auth-svc | ~500 usuarios MVP | Núcleo de identidad. Toda otra BD referencia `usuario_id` lógicamente. |
| `inventory_db` | inventory-svc | ~500 recursos, ~5k movimientos/semestre | Catálogo + stock + reservas + reconciliación. |
| `request_db` | request-svc | ~50 solicitudes/día | Solicitudes con TTL + drafts del asistente + aprobaciones especiales. |
| `loan_db` | loan-svc | ~50 préstamos/día | Núcleo transaccional. Solo escribe via comando del tótem. |
| `notification_db` | notification-svc | ~200 notifs/día | In-app + tickets PDF. TTL de 90 días. |
| `ai_risk_db` | ai-risk-svc | scoring por solicitud | Histórico para auditoría del modelo. |
| `ai_assistant_db` | ai-assistant-svc | conversaciones por usuario activo | Persistencia de turnos + mapping de actividades. |
| `reports_db` | reports-svc | proyecciones | Read-model CQRS. No fuente de verdad de nada. |

> **Estado actual del init**: `infra/postgres/init/01-create-databases.sql` crea 7 bases. Falta agregar `ai_assistant_db` — es un gap conocido que se resolverá antes de Fase 5 (cuando entre el slice del asistente).

---

## Convenciones de modelado

- **PK siempre UUID v4** (no autoincrementales). Así el ID se puede generar en aplicación antes de tocar la base, y los IDs no chocan al promover datos entre ambientes.
- **Timestamps con zona** (`TIMESTAMPTZ`). UTC en BD, conversión a hora local en UI.
- **Estados como ENUM** Postgres. Type-safe del lado de la aplicación con Prisma. Cambios de enum requieren migración explícita.
- **JSONB** para payloads variables (`drivers` del scoring, `payload` de eventos en outbox, `features` del perfil de riesgo). No para datos consultables con frecuencia.
- **Lock optimista con `version`** en agregados que pueden tener escrituras concurrentes (`resources`, `requests`, `loans`). Evita condiciones de carrera en las reservas (RC.12).
- **Tabla `outbox_events` + `processed_events`** en cada servicio que publica o consume eventos. Patrón EIP-05 — sin esto no hay saga confiable.
- **Campo `audit_log`** en servicios con acciones sensibles (auth, inventory, request, loan, notification). Append-only.

---

## Relaciones logicas que cruzan bases

Estas son referencias por ID que viajan via eventos. **No son FK físicas**.

| Referencia | Origen | Destino | Vehículo |
|---|---|---|---|
| `requests.usuario_id` | request_db | `auth_db.users` | payload de `request.created` |
| `requests.operador_id` | request_db | `auth_db.users` | mismo |
| `request_items.recurso_id` | request_db | `inventory_db.resources` | payload de `request.created` |
| `stock_reservations.request_id` | inventory_db | `request_db.requests` | payload de `request.created` |
| `loans.request_id` | loan_db | `request_db.requests` | payload de `loan.issued` |
| `loans.usuario_id` | loan_db | `auth_db.users` | mismo |
| `loans.panolero_id` | loan_db | `auth_db.users` | mismo |
| `loan_items.recurso_id` | loan_db | `inventory_db.resources` | mismo |
| `overdue_flags.usuario_id` | loan_db | `auth_db.users` | calculado localmente, replicado |
| `notifications.usuario_id` | notification_db | `auth_db.users` | payload de cualquier evento de dominio |
| `user_risk_profiles.usuario_id` | ai_risk_db | `auth_db.users` | payloads varios |
| `scoring_log.request_id` | ai_risk_db | `request_db.requests` | payload de `risk.score` (request-reply) |
| `conversations.usuario_id` | ai_assistant_db | `auth_db.users` | header JWT del usuario |
| Proyecciones | reports_db | varios | consume todos los eventos de dominio |

---

## Casos donde la consistencia eventual se nota

Tres escenarios concretos donde el sistema no es ACID global y hay que diseñar para ello:

**1. Reserva de stock vs disponibilidad mostrada en UI.**
Cuando un alumno arma carrito, el portal pregunta a `inventory-svc` por la disponibilidad. La respuesta usa `stock_total - SUM(stock_reservations WHERE estado='ACTIVA')`. Si dos alumnos consultan al mismo tiempo y el último ejemplar está libre, ambos ven "Disponible". El primero que confirma gana la reserva via lock optimista en `resources.version`; el segundo recibe error 409 (RC.12). Es decir: la UI puede mostrar info ligeramente stale, pero la BD es siempre consistente.

**2. Materialización parcial cierra la solicitud y la reserva en momentos distintos.**
Cuando el pañolero entrega solo 2 de 3 ítems solicitados, `loan-svc` publica `loan.issued` con cantidades efectivas. `request-svc` cambia el estado de la solicitud a `MATERIALIZADA_PARCIAL`. `inventory-svc` consume el evento, descuenta los 2 efectivos y libera la reserva del faltante. Estos tres pasos no son atómicos — entre el primero y el último puede haber milisegundos en los que la solicitud diga "MATERIALIZADA_PARCIAL" mientras la reserva del faltante todavía aparece como `ACTIVA`. Es aceptado.

**3. Bloqueo por morosidad después de crear solicitud.**
`loan.overdue` llega a `auth-svc` que evalúa RC.01 y publica `user.blocked`. `request-svc` consume `user.blocked` y cancela las solicitudes pendientes del usuario. Hay una ventana donde el usuario puede ya estar bloqueado pero la solicitud sigue como `PENDIENTE`. Si intentara materializarla en el tótem, el servicio de préstamos validaría el estado actual del usuario (consultando `auth-svc`) y rechazaría — pero la solicitud queda "fantasma" hasta que la cancela el consumer, o hasta que vence el TTL.

Estas ventanas son segundos en operación normal y no rompen la integridad — solo la apariencia momentánea. El alternativo sería SAGA orquestada (Temporal) — descartado en ADR-006.

---

## Migración y versionado

- **Prisma migrate** declarativo por servicio. Cada servicio tiene su `prisma/schema.prisma` y su histórico en `prisma/migrations/`.
- **Migraciones son CI-mandatory**: cada PR que toca el schema debe incluir su migration y pasar el test de "aplicar migration sobre BD limpia".
- **Compatibilidad atrás**: una migration que rompe consumidores se hace en dos pasos — primero agrega la nueva columna manteniendo la vieja, deploy de consumidores que leen la nueva, luego segunda migration que elimina la vieja. Patrón "expand/contract".
- **Campos de eventos siguen el mismo principio** — versión vía header `x-schema-version` (ver `03-eventos-dominio.md`).

---

## Documentación relacionada

- `02-topologia-microservicios.md` — qué servicio habla con qué base.
- `03-eventos-dominio.md` — contratos de los eventos que vehiculan los IDs cross-DB.
- `07-microservicios-responsabilidades.md` — datos propios de cada servicio (fuente de este modelo).
- `08-estados-entidades.md` — máquinas de estado de las entidades centrales.
- `docs/design/adrs/ADR-002-postgresql-vs-mongodb.md` — por qué Postgres puro.
- `docs/design/adrs/ADR-015-reports-svc-read-model.md` — el read-model CQRS.
- `docs/design/diagrams/ERD-01-modelo-datos.drawio` — diagrama formal.
