# Topología de microservicios

## Criterio de separación

Cada microservicio corresponde a un **bounded context** del dominio. La separación sigue tres pruebas:

1. **Cambio independiente**: si un cambio del negocio toca solo un servicio, el recorte es correcto.
2. **Data ownership**: cada servicio es único dueño de sus tablas. Si dos servicios necesitan la misma entidad, o está mal recortada o falta un evento.
3. **Lenguaje ubicuo diferenciado**: "préstamo" en `loan-svc` no es lo mismo que "solicitud" en `request-svc`, aunque se confundan en el habla coloquial.

## Los ocho servicios de dominio + reports-svc

### `api-gateway`
BFF para portal web y tótem. REST para comandos y queries, WebSocket para notificaciones push in-app. Autentica JWT, agrega datos, aplica rate-limit. No habla con el broker, habla HTTP con los demás servicios (o publica comandos en colas privadas si corresponde). Es el único punto de entrada desde el exterior.

### `auth-svc`
Dueño de usuarios, roles (Jefe de Carrera, Coordinador, Pañolero, Docente, Alumno) y sesiones. Emite `user.created`, `user.blocked`, `user.unblocked`. JWT firmado con clave rotable. SSO federado diferido.

### `inventory-svc`
Dueño del catálogo de recursos (materiales, herramientas, equipos) y de su stock por categoría. Gestiona altas, bajas y modificaciones de inventario. Reacciona a `loan.issued` (descuenta), `loan.returned` (reabre), `request.expired` (libera reserva). Emite `stock.changed`, `stock.low` con nivel (Normal/Bajo/Crítico), `stock.lost` cuando una devolución declara faltante.

### `request-svc`
Dueño de las solicitudes web. Valida disponibilidad consultando `inventory-svc` (Request-Reply) y consulta a `ai-risk-svc` para score (Request-Reply síncrono). Aplica reglas de blacklist. Emite `request.created`, `request.cancelled`, `request.expired`. Las solicitudes son inmutables una vez validadas; modificar es crear-y-cancelar.

### `loan-svc`
Dueño de los préstamos efectivos y su ciclo de vida. Es el servicio **transaccional** más crítico. Convierte solicitudes validadas en préstamos al presentarse el solicitante en el pañol. Registra devoluciones. Ejecuta compensaciones ante fallos de saga. Emite `loan.issued`, `loan.returned`, `loan.overdue`. Se apoya en `outbox_events` para garantizar consistencia evento-BD.

### `notification-svc`
Consumidor múltiple. Escucha todos los eventos relevantes y enruta (Content-Based Router) a los destinatarios correctos. Persiste notificaciones en su propia bandeja Postgres y empuja por WebSocket a las UIs. Genera PDFs del ticket con PDFKit al procesar `loan.issued` y `loan.returned`.

### `ai-risk-svc`
Servicio de scoring. Expone endpoint `POST /score` con `{userId, requestedItems, context}` y devuelve `{score: 0..1, drivers: [...]}`. Modelo entrenado offline (Python/scikit-learn) con features: historial de devoluciones tardías, tipo de recurso, carrera, período académico, historial de faltantes. Emite `risk.scored` asíncrono para registro; su respuesta síncrona es la que decide el flujo.

### `ai-assistant-svc`
Servidor MCP + cliente que lo consume desde OpenAI. Expone tools al LLM: `consultar_inventario`, `validar_disponibilidad`, `sugerir_recursos_por_actividad`, `crear_solicitud_borrador`. El cliente traduce estas tools MCP a function calls de OpenAI y orquesta la conversación desde el portal web. Detalle en `06-ia-mcp.md`.

### `reports-svc`
Read-model dedicado bajo CQRS (ver ADR-015). No tiene lógica de dominio ni publica eventos; consume eventos de dominio de `domain.events` y mantiene proyecciones desnormalizadas en su propia base PostgreSQL, optimizadas para los reportes de `RF.13`: stock disponible/no disponible, recursos más y menos solicitados por período, devoluciones fuera de plazo por recurso y por usuario, recursos con mayor tasa de pérdida o baja. Expone sus queries por HTTP a través del API Gateway. Consistencia eventual (ventana típica < 2 s).

## Comunicación entre servicios

| Origen | Destino | Tipo | Transporte |
|---|---|---|---|
| UI → API Gateway | comandos/queries | Request-Reply | HTTP/REST |
| API Gateway → servicio | query crítico | Request-Reply | HTTP/REST |
| Servicio → servicio | evento de dominio | Publish-Subscribe | AMQP (RabbitMQ) |
| `request-svc` → `ai-risk-svc` | score de riesgo (síncrono) | Request-Reply | AMQP con `replyTo` |
| `request-svc` → `inventory-svc` | validar disponibilidad | Request-Reply | AMQP con `replyTo` |
| Servicios → `notification-svc` | hechos a notificar | Publish-Subscribe | AMQP (topic exchange) |
| Servicios → UIs | notificaciones push | Push | WebSocket vía API Gateway |

La regla general: **HTTP solo desde el exterior al gateway**; todo lo interno entre microservicios va por el broker.

## Exchanges y colas (mapa inicial)

- Exchange `domain.events` (topic): canal de eventos de dominio. Routing keys `user.*`, `inventory.*`, `request.*`, `loan.*`, `risk.*`.
- Exchange `domain.commands` (direct): para Request-Reply sobre AMQP.
- Exchange `domain.delayed` (x-delayed-message): para Message Expiration (TTL de reservas).
- Exchange `domain.dlx` (fanout): Dead Letter Exchange único para todo mensaje muerto; consumido por un servicio de auditoría simple.

Definición formal en `03-eventos-dominio.md`.

## Escalamiento y disponibilidad

En producción, cada servicio escala horizontalmente detrás del broker sin coordinación (competing consumers pattern). RabbitMQ se puede clusterizar con quorum queues para HA. El API Gateway corre detrás de un load balancer. Postgres con replicación primaria/réplica para lecturas de reporte. Todo opcional: el MVP corre en un nodo.
