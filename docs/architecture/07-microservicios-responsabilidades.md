# Microservicios y responsabilidades

## Propósito

Este documento es la **lista canónica** de los microservicios del Sistema de Pañol. Para cada servicio declara: responsabilidad única, datos que posee, eventos que publica, eventos que consume, interacciones síncronas, tecnología específica y decisiones arquitectónicas asociadas. Sirve como fuente de verdad para asignación de trabajo, onboarding de nuevos desarrolladores, diagramas y trazabilidad en la mesa redonda.

La topología se describe en `02-topologia-microservicios.md` (visión horizontal). Los eventos se contratan en `03-eventos-dominio.md` (visión por evento). Este documento da la visión vertical: **qué hace cada servicio, de principio a fin**.

---

## Índice

| # | Servicio | Rol |
|---|---|---|
| 1 | `api-gateway` | Puerta de entrada HTTP/WebSocket del exterior. BFF. |
| 2 | `auth-svc` | Usuarios, roles, autenticación, JWT. |
| 3 | `inventory-svc` | Catálogo, stock, altas/bajas de recursos. |
| 4 | `request-svc` | Solicitudes on-line y reservas con TTL. |
| 5 | `loan-svc` | Préstamos, devoluciones, atrasos. Núcleo transaccional. |
| 6 | `notification-svc` | Notificaciones in-app y tickets PDF. |
| 7 | `ai-risk-svc` | Scoring de riesgo de morosidad. |
| 8 | `ai-assistant-svc` | Asistente conversacional con MCP + OpenAI. |
| 9 | `reports-svc` | Read-model CQRS. Proyecciones para reportes de gestión. |

Total: **1 gateway + 8 servicios de dominio + 1 read-model = 9 microservicios backend**, más 2 frontends (`web-portal`, `totem`).

---

## 1. `api-gateway`

**Tipo**: Gateway / BFF (Backend for Frontend).  
**Clasificación**: No es microservicio de dominio. Agrega y orquesta.  
**ADR asociado**: ADR-008.

### Responsabilidad

Es el único punto de entrada HTTP desde los frontends (`web-portal`, `totem`). Autentica con JWT, aplica rate-limit, agrega datos de múltiples servicios cuando es necesario, y expone un WebSocket para notificaciones push in-app.

### Datos propios

Ninguno persistido. Cachea sesiones y tokens en memoria con TTL corto.

### Endpoints expuestos (alto nivel)

- `POST /auth/login`, `POST /auth/refresh`, `POST /auth/change-password`, `POST /auth/verify-pin`
- `GET/POST /users/*`, `GET/POST /students/import`
- `GET /inventory/*`, `POST /inventory/resources`, `PATCH /inventory/resources/:id`
- `POST /requests`, `GET /requests/:id`, `POST /requests/:id/cancel`
- `POST /loans/:requestId/materialize`, `POST /loans/:id/return`, `GET /loans/*`
- `GET /notifications`, `GET /notifications/:id/ticket.pdf`
- `POST /assistant/messages` (chat del asistente)
- `GET /reports/stock`, `GET /reports/top-resources`, `GET /reports/overdue`, `GET /reports/losses`
- `WS /events` (notificaciones push)

### Dependencias

- HTTP síncrono hacia `auth-svc`, `inventory-svc`, `request-svc`, `loan-svc`, `notification-svc`, `ai-assistant-svc`, `reports-svc`.
- AMQP hacia `domain.commands` solo para endpoints que disparan comandos con replyTo.

### No hace

- No publica eventos de dominio propios.
- No persiste estado de negocio.
- No invoca LLM directamente: delega todo a `ai-assistant-svc`.

### Tecnología específica

- NestJS HTTP + Socket.IO para WebSocket.
- `@nestjs/throttler` para rate-limit.
- `@nestjs/passport` + `passport-jwt` para validar JWT.

---

## 2. `auth-svc`

**Tipo**: Microservicio de dominio.  
**Bounded context**: Identidad y acceso.  
**ADRs asociados**: ADR-011 (PIN tótem), ADR-013 (JWT local, SSO roadmap), ADR-014 (Coord administra Docentes).

### Responsabilidad

Dueño exclusivo de usuarios, roles, sesiones y la emisión de JWT. Gestiona alta/baja lógica, importación masiva desde Excel/CSV, cambio de clave, reset, bloqueo/desbloqueo manual y automático, y el PIN de 4 dígitos del Pañolero.

### Datos propios (Postgres `auth_db`)

- `users` — documento, nombre, role, carreraId, email, phone, status (ACTIVO/INACTIVO/BLOQUEADO), passwordHash, pinHash nullable, createdAt, updatedAt.
- `user_blocks` — historial de bloqueos: reason, motivo, blockedBy, blockedAt, unblockedAt.
- `password_resets` — tokens temporales para reset.
- `login_attempts` — contadores de intentos fallidos por IP y por usuario.
- `outbox_events`, `processed_events` — infraestructura de mensajería.
- `audit_log` — acciones sobre usuarios (CRUD, bloqueo, reset).

### Eventos publicados

| Evento | Cuándo |
|---|---|
| `user.created` | Alta individual o por importación. |
| `user.updated` | Cambio de datos no sensibles. |
| `user.deactivated` | Baja lógica. |
| `user.blocked` | Bloqueo manual o automático. |
| `user.unblocked` | Levantamiento de bloqueo. |

### Eventos consumidos

| Evento | Acción |
|---|---|
| `loan.overdue` | Evalúa RC.01. Si se cumple el umbral (3 atrasos en el semestre), publica `user.blocked` con reason=MOROSIDAD_AUTOMATICA. |

### Interacciones síncronas

- **Expone HTTP** (solo al gateway): login, refresh, verifyPin, changePassword, importStudents, createUser, block/unblock, getUser.

### RBAC (resumen)

- **JEFE**: alcance total sobre todos los perfiles y configuración (`RS-JC.5`).
- **COORDINADOR**: CRUD sobre Alumnos y Docentes (ADR-014). Bloqueo de Alumnos y Docentes.
- **PANOLERO**: autogestión de su perfil y PIN. Bloqueo solo de Alumnos.
- **DOCENTE / ALUMNO**: autogestión de su perfil.

### Contratos de máquina de estado

- Usuario: `docs/architecture/08-estados-entidades.md` — sección "Usuario".

---

## 3. `inventory-svc`

**Tipo**: Microservicio de dominio.  
**Bounded context**: Catálogo y stock.

### Responsabilidad

Dueño del catálogo de recursos (`Material`, `Herramienta`, `Equipo` según `RC.03`) y de su stock agregado por tipología (`SP.10`, sin trackeo de instancia individual). Gestiona altas, bajas lógicas, modificaciones, estado "En Mantención" y los umbrales de alerta por recurso. Reserva stock al recibir solicitudes, lo descuenta al materializarse un préstamo, lo reabre en devoluciones y lo libera al expirar reservas.

### Datos propios (Postgres `inventory_db`)

- `resources` — id, nombre, categoria, detalle, stockTotal, stockMaximoHistorico, thresholdBajoPct, thresholdCriticoPct, estado (ACTIVO/EN_MANTENCION/BAJA), imagenUrl, codigoExterno nullable, version (lock optimista).
- `stock_reservations` — requestId, recursoId, cantidad, estado (ACTIVA/LIBERADA/CONSUMIDA), createdAt, expiresAt.
- `stock_movements` — log append-only: recursoId, delta, motivo, loanId nullable, performedAt, performedBy.
- `stock_reconciliation` — discrepancias detectadas por el job nocturno (ver `05-saga-coreografiada.md`).
- `outbox_events`, `processed_events`, `audit_log`.

### Eventos publicados

| Evento | Cuándo |
|---|---|
| `resource.created` | Alta de recurso. |
| `resource.updated` | Cambio de campos no sensibles. |
| `resource.deactivated` | Baja lógica. |
| `resource.maintenance.started` / `resource.maintenance.ended` | Cambio a/desde `EN_MANTENCION`. |
| `stock.changed` | Cualquier movimiento de stock (alta, baja, préstamo, devolución, pérdida). |
| `stock.low` | Cruce descendente del umbral `BAJO` o `CRITICO`. |
| `stock.normalized` | Cruce ascendente de regreso a `NORMAL`. |
| `stock.lost` | Devolución con faltante o daño no funcional. |

### Eventos consumidos

| Evento | Acción |
|---|---|
| `request.created` | Marca `stock_reservations.estado=ACTIVA` por la cantidad pedida. |
| `request.cancelled` | Libera reserva (estado=LIBERADA), publica `stock.changed` motivo=LIBERACION_RESERVA. |
| `request.expired` | Libera reserva idéntica a cancelled. |
| `loan.issued` | Descuenta stock (estado reserva=CONSUMIDA), publica `stock.changed` motivo=PRESTAMO. Re-evalúa umbrales y publica `stock.low` si corresponde. |
| `loan.returned` | Reabre stock, si hay faltantes publica `stock.lost`. Re-evalúa umbrales y publica `stock.normalized` si corresponde. |

### Interacciones síncronas

- **Expone AMQP** (`domain.commands`): `inventory.validate` — verifica disponibilidad en el momento de creación de la solicitud (Request-Reply). Timeout objetivo 2 s.
- **Expone HTTP** (solo gateway): CRUD de recursos, listados, consultas puntuales.

### Jobs internos

- Reconciliación nocturna: compara `stockTotal` vs `stockTotal - SUM(reservas activas)` contra el "ground truth" calculado a partir de `stock_movements`. Registra discrepancias. Alerta al Jefe si encuentra delta.

### Contratos de máquina de estado

- Recurso: ver `08-estados-entidades.md`.
- Reserva de stock: ver `08-estados-entidades.md`.

---

## 4. `request-svc`

**Tipo**: Microservicio de dominio.  
**Bounded context**: Solicitudes on-line.  
**ADRs asociados**: ADR-010 (TTL de reserva).

### Responsabilidad

Dueño de las solicitudes creadas desde el portal web (autor alumno o docente, o en nombre de otro vía `RF-C.13`). Aplica validaciones síncronas (blacklist, disponibilidad, scoring), reserva stock con TTL vía `domain.delayed`, gestiona el estado de la solicitud a lo largo de su vida (RC.16), y coordina la aprobación del préstamo Especial multi-día (`RF-C.05`).

### Datos propios (Postgres `request_db`)

- `requests` — id, usuarioId, operadorId nullable, creadaPorOperador, fechaRetiro, tipoPrestamo, estado, riesgoScore, drivers, ttlExpiresAt, createdAt, updatedAt, cancelledAt nullable, version.
- `request_items` — requestId, recursoId, cantidadSolicitada, cantidadEntregada nullable.
- `special_approvals` — requestId, reviewerId, decision, motivo, decidedAt.
- `drafts` — solicitudes en estado BORRADOR creadas por el asistente conversacional, con autocaducidad 24 h.
- `outbox_events`, `processed_events`, `audit_log`.

### Eventos publicados

| Evento | Cuándo |
|---|---|
| `request.draft_created` | El asistente creó un borrador (no confirma reserva). |
| `request.created` | Usuario confirma; validaciones pasan; reserva activa. |
| `request.pending_approval` | Especial multi-día esperando decisión. |
| `request.approved` / `request.rejected` | Decisión de Especial. |
| `request.cancelled` | Cancelación por usuario u operador. |
| `request.expired` | TTL vencido sin materializar. |
| `request.materialized` | `loan-svc` confirmó materialización (espejo útil para consumidores que no escuchan `loan.issued`). |

Además publica un mensaje `request.expire` al exchange `domain.delayed` con `x-delay=ttl_ms` por cada `request.created` (no es evento de dominio sino comando delayed).

### Eventos consumidos

| Evento | Acción |
|---|---|
| `user.blocked` | Si el usuario tiene solicitudes en BORRADOR o PENDIENTE, las cancela automáticamente con reason=USER_BLOCKED. |
| `loan.issued` | Marca la solicitud como MATERIALIZADA o MATERIALIZADA_PARCIAL. |
| `request.expire` (delayed, mismo servicio lo escucha) | Si la solicitud sigue en PENDIENTE, la marca como VENCIDA y publica `request.expired`. Idempotente. |

### Interacciones síncronas

- **Consume AMQP** (`domain.commands`): `inventory.validate` y `risk.score` (Request-Reply con timeouts 2 s / 1.5 s).
- **Consume HTTP**: `GET /users/:id/is-blocked` a `auth-svc` (fallback conservador: si timeout, bloquea).
- **Expone HTTP** (gateway): crear, cancelar, consultar, aprobar/rechazar Especial.

### Contratos de máquina de estado

- Solicitud: ver `08-estados-entidades.md`.

---

## 5. `loan-svc`

**Tipo**: Microservicio de dominio.  
**Bounded context**: Préstamos efectivos.  

### Responsabilidad

Es el núcleo transaccional. Convierte solicitudes validadas en préstamos al presentarse el solicitante en el pañol. Registra devoluciones con clasificación de estado de cada ítem (`RF-C.07`). Detecta atrasos y emite `loan.overdue`. Verifica las tres condiciones deterministas de `RC.01` y notifica a `auth-svc` cuando se cumple la regla. Se apoya en outbox para garantizar atomicidad cambio-evento.

### Datos propios (Postgres `loan_db`)

- `loans` — id, ticketId, requestId, usuarioId, panoleroId, fechaLimite, issuedAt, returnedAt nullable, estado, version.
- `loan_items` — loanId, recursoId, cantidad, estadoDevolucion (null mientras abierto; `BUENO`/`DAÑADO_MENOR`/`DAÑADO_MAYOR`/`FALTANTE`), observacion.
- `overdue_flags` — loanId, usuarioId, detectedAt, diasAtraso (para contar contra RC.01).
- `outbox_events`, `processed_events`, `audit_log`.

### Eventos publicados

| Evento | Cuándo |
|---|---|
| `loan.issued` | Materialización exitosa en el tótem. Incluye ítems efectivamente entregados. |
| `loan.returned` | Devolución registrada. Incluye estado de cada ítem. |
| `loan.overdue` | Job periódico detecta `fechaLimite < now` y préstamo aún EN_CURSO. Publica un evento por día de atraso. |
| `loan.annulled` | Pañolero anula préstamo antes de entrega efectiva (`RS-PN.4`). |

### Eventos consumidos

Ninguno. Es publisher puro; recibe comandos HTTP desde el gateway (tótem) para sus operaciones.

### Interacciones síncronas

- **Consume HTTP**: `GET /requests/:id` a `request-svc` para validar estado RESERVADA y `ttlExpiresAt`.
- **Expone HTTP** (gateway): `POST /loans/:requestId/materialize`, `POST /loans/:id/return`, `POST /loans/:id/annul`, `GET /loans?day=X`.

### Jobs internos

- **Overdue detection**: cada hora (`@nestjs/schedule`), busca préstamos abiertos con `fechaLimite < now`. Publica `loan.overdue` si no se publicó ya en las últimas 24 h (deduplicación por `loanId + fecha`).

### Contratos de máquina de estado

- Préstamo: ver `08-estados-entidades.md`.

---

## 6. `notification-svc`

**Tipo**: Microservicio de dominio / adaptador de canal.  
**Bounded context**: Notificaciones y tickets.  
**ADR asociado**: ADR-007.

### Responsabilidad

Consumidor múltiple. Escucha todos los eventos relevantes, decide destinatarios y canal (Content-Based Router — `04-eip-catalog.md`), persiste cada notificación en su bandeja propia y la empuja en tiempo real vía WebSocket al usuario destinatario. Genera PDFs de ticket con PDFKit al procesar `loan.issued` y `loan.returned`.

### Datos propios (Postgres `notification_db`)

- `notifications` — id, usuarioId, tipo, canal, payload JSONB, readAt nullable, deliveredAt, createdAt, ttl (default 90 días).
- `notification_rules` — eventType, role, channel, template. Configurables sin despliegue.
- `tickets` — ticketId, notificationId, type (PRESTAMO/DEVOLUCION), pdfPath, generatedAt.
- `failed_deliveries` — para debugging del WebSocket.
- `outbox_events`, `processed_events`, `audit_log`.

### Eventos publicados

| Evento | Cuándo |
|---|---|
| `notification.delivered` | Tras entregar una notificación (persistida + websocket intentado). |

### Eventos consumidos

Casi todos los eventos del sistema:

- `user.created` (saludo — RS.3)
- `user.blocked` / `user.unblocked` (comunica al usuario y a administradores)
- `stock.low` / `stock.normalized` (alerta a Jefe/Coord/Pañolero)
- `stock.lost` (alerta)
- `request.created` / `request.cancelled` / `request.expired` / `request.approved` / `request.rejected` / `request.pending_approval` (comunica al solicitante; si es `pending_approval`, notifica al aprobador)
- `loan.issued` (genera ticket PDF + notificación al solicitante)
- `loan.returned` (genera ticket PDF + notificación al solicitante)
- `loan.overdue` (alerta al usuario y al Coord)

### Interacciones síncronas

- **Expone HTTP** (gateway): `GET /notifications`, `GET /notifications/:id/ticket.pdf`, `PATCH /notifications/:id/read`.
- **Expone WebSocket** a través del API Gateway (Socket.IO).

### Tecnología específica

- `PDFKit` para tickets.
- `socket.io` para WebSocket.
- Template engine simple (Handlebars o similar) para textos de notificación.

### Contratos de máquina de estado

- Notificación: ver `08-estados-entidades.md`.

---

## 7. `ai-risk-svc`

**Tipo**: Microservicio de IA / servicio de inferencia.  
**Bounded context**: Scoring de riesgo.  
**ADR asociado**: ADR-006 (indirectamente, por IA como servicio).

### Responsabilidad

Calcula un score 0..1 de probabilidad de morosidad dado un usuario y un contexto de solicitud. Expone endpoint síncrono por AMQP (`risk.score`), devuelve el score y los drivers (features que más influyeron). Publica el resultado como evento asíncrono `risk.scored` para auditoría del modelo. Reentrena offline semestralmente.

### Datos propios (Postgres `ai_risk_db`)

- `user_risk_profiles` — usuarioId, features agregados (historial_atrasos_30d, historial_perdidas_semestre, prestamos_activos, etc.), lastComputedAt.
- `scoring_log` — timestamp, usuarioId, requestId, score, drivers, modelVersion. Dataset para auditoría.
- `models` — modelVersion, rutaOnnx, auc, trainedAt, active. Un modelo activo a la vez.
- `outbox_events`, `processed_events`.

### Eventos publicados

| Evento | Cuándo |
|---|---|
| `risk.scored` | Asíncrono, tras responder una solicitud de score. Para registro y entrenamiento futuro. |

### Eventos consumidos

| Evento | Acción |
|---|---|
| `user.created` | Inicializa `user_risk_profiles` con prior neutro (0.5, sin historial). |
| `loan.issued` | Actualiza `prestamos_activos_actuales`. |
| `loan.returned` | Calcula si fue con atraso; actualiza `historial_atrasos_30d`. |
| `loan.overdue` | Actualiza contador y la fecha de último atraso. |
| `stock.lost` | Si el responsable era un préstamo cerrado, actualiza `historial_perdidas_semestre`. |

### Interacciones síncronas

- **Expone AMQP** (`domain.commands`): `risk.score` — Request-Reply. Timeout objetivo 1.5 s; latencia p99 < 200 ms.
- No expone HTTP directo (el asistente tampoco lo usa — el asistente consulta solo `consultar_mi_historial` a `loan-svc`, no scoring, por diseño).

### Tecnología específica

- Modelo Random Forest entrenado en Python/scikit-learn.
- Exportado a ONNX; sirve en Node con `onnxruntime-node`.
- SHAP local para generar drivers.
- Job offline Python para reentrenamiento semestral.

### Consideraciones éticas

- Auditoría semestral de equidad por carrera y género (`08-amenazas-e-impacto.md` AM.08).
- Drivers transparentes devueltos en cada score: el usuario puede impugnar.

---

## 8. `ai-assistant-svc`

**Tipo**: Microservicio de IA / servicio conversacional.  
**Bounded context**: Asistencia al usuario.  
**ADR asociado**: ADR-006.

### Responsabilidad

Interactúa con el alumno/docente vía chat para ayudarlo a armar una solicitud. Internamente: servidor MCP que expone tools de dominio al LLM; cliente OpenAI que consume el LLM y traduce las tool calls a invocaciones MCP locales. Produce un borrador de solicitud; la confirmación final la hace el usuario con un click separado (no hay acción de escritura sin confirmación explícita).

### Datos propios (Postgres `ai_assistant_db`)

- `conversations` — id, usuarioId, startedAt, lastTurnAt, tokensUsed, closedReason nullable.
- `turns` — conversationId, role (user/assistant/tool), content, toolCallPayload nullable, tokensThisTurn.
- `activity_resource_mapping` — tabla `(actividad, keywords, recursoIds)` mantenida por el Pañolero para la tool `sugerir_recursos_por_actividad`.
- `processed_events`.

### Eventos publicados

Ninguno obligatorio. Opcionalmente `assistant.suggested` para métricas (contemplado en `00-overview.md`), deferido.

### Eventos consumidos

| Evento | Acción |
|---|---|
| `user.blocked` | Cierra cualquier conversación abierta del usuario; el chat se inhabilita en el portal. |
| `user.unblocked` | Re-habilita el chat. |

### Interacciones síncronas

- **Expone HTTP** (gateway): `POST /assistant/messages`, `GET /assistant/conversations/:id`, `DELETE /assistant/conversations/:id`.
- **Invoca HTTP**: `inventory-svc`, `request-svc`, `loan-svc`, `auth-svc` a través de las tools MCP.
- **Invoca externo**: API de OpenAI (gpt-4o u otro).

### Tools MCP expuestas

- `consultar_inventario(filtros)`
- `validar_disponibilidad(items, fecha)`
- `sugerir_recursos_por_actividad(actividad)`
- `crear_solicitud_borrador(items, fecha)` — produce un draft, no confirma
- `consultar_mi_historial()`
- `consultar_estado_solicitud(requestId)`

Detalle y contratos en `06-ia-mcp.md`.

### Guardrails

- Rate limit por usuario: 30 mensajes/hora.
- Budget por conversación: 8K tokens default.
- Bloqueo en profundidad: el servidor MCP rechaza tools de escritura si `auth-svc` reporta usuario bloqueado.

---

## 9. `reports-svc`

**Tipo**: Microservicio de read-model (CQRS).  
**Bounded context**: Reporting y analítica operativa.  
**ADR asociado**: ADR-015.

### Responsabilidad

Consumidor puro de eventos de dominio. Mantiene proyecciones desnormalizadas en su propia base PostgreSQL, optimizadas para los reportes de `RF.13`: stock, recursos más/menos solicitados, devoluciones tardías, pérdidas. Expone queries HTTP al API Gateway. Es también la fuente natural del dataset de reentrenamiento para `ai-risk-svc`.

### Datos propios (Postgres `reports_db`)

- `reporte_stock` — recursoId, categoria, stockActual, disponible, ultimaActualizacion.
- `reporte_solicitudes_recurso` — recursoId, anio, mes, cantidadSolicitudes, cantidadCancelaciones, cantidadExpiraciones.
- `reporte_devoluciones_tardias` — loanId, recursoId, usuarioId, diasAtraso, faltantes, fechaDevolucion.
- `reporte_perdidas_recurso` — recursoId, cantidadPerdidas, cantidadBajas, ultimaFechaPerdida.
- `proyeccion_usuarios` — usuarioId, documento, nombre, role, carreraId, activo (copia lean para hacer joins locales sin salir del servicio).
- `proyeccion_recursos` — recursoId, nombre, categoria (copia lean).
- `processed_events` — crítico para evitar reprocesar eventos en replays.
- `projection_lag_metrics` — para el dashboard de salud del read-model.

### Eventos publicados

**Ninguno de dominio**. Es sink. Opcionalmente publica métricas de lag en un canal de observabilidad.

### Eventos consumidos

Todos los relevantes para las proyecciones:

- `user.created` / `user.updated` / `user.blocked` / `user.unblocked` / `user.deactivated` → `proyeccion_usuarios`
- `resource.created` / `resource.updated` / `resource.deactivated` → `proyeccion_recursos`
- `stock.changed` / `stock.low` / `stock.normalized` / `stock.lost` → `reporte_stock`, `reporte_perdidas_recurso`
- `request.created` / `request.cancelled` / `request.expired` → `reporte_solicitudes_recurso`
- `loan.issued` / `loan.returned` / `loan.overdue` → `reporte_devoluciones_tardias`, `reporte_solicitudes_recurso`
- `risk.scored` → tabla `scoring_log` mirror, útil para auditoría y retraining

### Interacciones síncronas

- **Expone HTTP** (gateway): endpoints de lectura agregada. Todos protegidos por RBAC (Jefe y Coordinador como mínimo).
  - `GET /reports/stock`
  - `GET /reports/top-resources?period=...`
  - `GET /reports/overdue?by=resource|user`
  - `GET /reports/losses`

### Consistencia

- **Eventualmente consistente**. Lag típico < 2 s; alerta si > 60 s.
- Idempotencia estricta por `processed_events`.
- Replay posible: script administrativo vacía proyecciones y reprocesa desde el broker (o desde los outbox de los servicios publishers si el broker ya los descartó).

### No hace

- No tiene lógica de negocio. No valida, no decide, no publica eventos de dominio.
- No es autoridad para ningún dato: los publishers son la fuente de verdad.

---

## Matriz compacta

| Servicio | Publica | Consume | DB | HTTP | AMQP expone | Stateful |
|---|---|---|---|---|---|---|
| `api-gateway` | — | — | — | ✔ (in/out) | — | No |
| `auth-svc` | user.* | loan.overdue | ✔ | ✔ (out para gateway) | — | Sí |
| `inventory-svc` | stock.* resource.* | request.* loan.* | ✔ | ✔ (out) | ✔ `inventory.validate` | Sí |
| `request-svc` | request.* | user.blocked loan.issued request.expire | ✔ | ✔ (out) | — | Sí |
| `loan-svc` | loan.* | — | ✔ | ✔ (out) | — | Sí |
| `notification-svc` | notification.delivered | casi todo | ✔ | ✔ (out + WS) | — | Sí |
| `ai-risk-svc` | risk.scored | user.created loan.* stock.lost | ✔ | — | ✔ `risk.score` | Sí |
| `ai-assistant-svc` | — | user.blocked/unblocked | ✔ | ✔ (out + llama otros) | — | Sí |
| `reports-svc` | — | casi todo | ✔ | ✔ (out, solo lectura) | — | Sí (read-model) |

## Asignación por equipo Feature (sugerido)

LeSS básico con dos equipos Feature y un único backlog. Asignación sugerida para no solapar modificaciones del mismo servicio en el mismo sprint:

- **Equipo A (núcleo transaccional)**: `auth-svc`, `inventory-svc`, `request-svc`, `loan-svc`, `api-gateway`, `totem`.
- **Equipo B (experiencia y periférica)**: `notification-svc`, `ai-risk-svc`, `ai-assistant-svc`, `reports-svc`, `web-portal`.

Esta asignación es una referencia; en LeSS la capacidad es compartida y cualquier equipo puede tomar cualquier feature del backlog. El valor está en minimizar conflictos de integración en sprints tempranos.
