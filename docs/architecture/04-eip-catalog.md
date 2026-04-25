# Catálogo de Enterprise Integration Patterns

## Propósito

Este documento enumera los patrones de integración empresarial de Gregor Hohpe (Enterprise Integration Patterns, Addison-Wesley 2003) que el Sistema de Pañol implementa explícitamente, dónde se usa cada uno, qué problema resuelve y cómo se materializa en el stack (RabbitMQ + NestJS). Es la fuente que sustenta el bloque de arquitectura de la rúbrica y la sección EIP de la presentación final. Los íconos oficiales de Hohpe se reproducen en los diagramas `.drawio` (`docs/architecture/diagrams/eip/`).

## Mapa rápido

| # | Patrón EIP | Servicios involucrados | Caso concreto |
|---|---|---|---|
| 1 | Publish-Subscribe Channel | Todos | Eventos de dominio (`request.created`, `loan.issued`, `stock.low`, etc.). |
| 2 | Content-Based Router | `notification-svc` | Decide destinatarios de cada evento según tipo y rol. |
| 3 | Message Expiration | `request-svc`, broker | TTL de reservas (RC.06) sin job externo. |
| 4 | Dead Letter Channel | Todos los consumidores | Captura mensajes que fallaron tras N reintentos para análisis. |
| 5 | Request-Reply | `request-svc` ↔ `inventory-svc`, `request-svc` ↔ `ai-risk-svc` | Validación de disponibilidad y scoring síncrono. |
| 6 | Message Channel | RabbitMQ | Cualquier exchange + queue. Implícito pero nombrado. |
| 7 | Document Message | Todos | Payload de eventos como documentos JSON autocontenidos. |
| 8 | Correlation Identifier | Request-Reply, headers AMQP | `x-correlation-id` propagado en todos los mensajes. |
| 9 | Idempotent Receiver | Todos los consumidores | Tabla `processed_events` por servicio. |
| 10 | Transactional Outbox | Todos los publishers | Tabla `outbox_events` + relay. Garantiza atomicidad evento-BD. |

Los cinco primeros son los que se documentan a continuación con detalle de problema, solución y configuración. Los cinco siguientes son patrones de soporte que aparecen mencionados pero no requieren tratamiento extenso porque su uso es transversal.

---

## 1. Publish-Subscribe Channel

### Problema

Cuando un servicio produce un hecho relevante (un préstamo se materializó, una solicitud expiró, el stock cayó bajo el umbral), múltiples servicios pueden necesitar reaccionar: el inventario debe descontar, el notificador debe avisar al usuario, el módulo de reportes debe actualizar agregados. Si el publisher conoce a sus consumidores y los invoca uno a uno, queda acoplado a cada nuevo destinatario y a la disponibilidad de cada uno.

### Solución

Un canal de tipo Publish-Subscribe entrega cada mensaje a todos los consumidores suscritos, sin que el publisher conozca su existencia. Los consumidores se suscriben de forma independiente y procesan a su propio ritmo.

### Implementación en el sistema

- Exchange `domain.events` de tipo `topic` en RabbitMQ.
- Cada consumidor declara una cola privada (`<servicio>.<dominio>`) y la enlaza al exchange con un patrón de routing key (`request.*`, `loan.#`, etc.).
- En NestJS se materializa con `@EventPattern('loan.issued')` en el controller de microservicios.
- Mensajes durables, colas durables, prefetch=10, ack manual.

### Eventos que lo usan

`user.*`, `stock.*`, `request.*` (excepto el delayed), `loan.*`, `risk.scored`, `notification.delivered`. Listado completo en `03-eventos-dominio.md`.

### Por qué Publish-Subscribe y no llamadas HTTP

Una llamada HTTP punto-a-punto requeriría que el publisher conociera la URL de cada consumidor, gestionara reintentos por consumidor, y bloquearía al publisher si un consumidor está caído. Publish-Subscribe desacopla disponibilidad y escala los consumidores horizontalmente sin que el publisher se entere.

---

## 2. Content-Based Router

### Problema

`notification-svc` recibe eventos heterogéneos (`stock.low`, `loan.overdue`, `loan.issued`, `request.expired`) y debe decidir, para cada uno, qué destinatarios reciben qué notificación y por qué canal. Hardcodear `if (event=='stock.low') ...` mezcla lógica de routing con lógica de presentación y se vuelve frágil al crecer.

### Solución

Un Content-Based Router examina el contenido del mensaje (tipo, dominio, payload) y lo enruta a uno o varios canales lógicos de salida. La lógica de routing está en un único lugar y se modifica como configuración, no como código mezclado con la entrega.

### Implementación en el sistema

Dos niveles de routing operan en cascada:

**Nivel broker (declarativo)**. Las routing keys del topic exchange ya hacen routing parcial. Por ejemplo, una cola enlazada con `loan.#` solo recibe eventos del dominio `loan`. Esto es Content-Based Router *implícito* configurado en el broker.

**Nivel aplicación (explícito)**. Dentro de `notification-svc`, un módulo `NotificationRouter` recibe el evento y consulta una tabla `notification_rules` con la forma `(eventType, role, channel, template)` para producir N notificaciones derivadas. Por ejemplo, `stock.low CRITICO` produce 3 notificaciones (Jefe, Coord, Pañolero); `loan.issued` produce 1 (al usuario solicitante); `loan.overdue` produce 1 al usuario y 1 al Coord (como observador).

Las reglas son datos, no código. Cambiar una regla no requiere despliegue de servicio.

### Por qué CBR y no múltiples consumidores

Se podría hacer que `notification-svc` ejecutara N suscriptores a N event types y resolviera dentro de cada handler. Es válido pero esparce la lógica. Centralizar en un router visible facilita la auditabilidad ("¿quién recibe qué cuando pasa X?") que es propio de un sistema con regulaciones internas y reglas administrativas (RS-* del Caso 11).

---

## 3. Message Expiration

### Problema

Una solicitud reserva stock por un TTL configurable (RC.06, por defecto 4 horas). Si el alumno no se presenta en el pañol antes de ese tiempo, la reserva debe liberarse para que ese stock vuelva a estar disponible para otros. La solución obvia —un cron que cada minuto recorre solicitudes y libera las vencidas— introduce un proceso fuera del flujo de eventos, con su propia disponibilidad, su propio scheduling y su propia idempotencia que cuidar.

### Solución

Message Expiration delega al broker la responsabilidad de "no entregar este mensaje hasta que pase X tiempo". Cuando la solicitud se crea, se publica un mensaje de comando `request.expire(requestId)` con un retraso igual al TTL. El broker lo retiene y lo entrega al consumidor exactamente cuando vence.

### Implementación en el sistema

- Plugin `rabbitmq_delayed_message_exchange` instalado.
- Exchange `domain.delayed` de tipo `x-delayed-message` con `x-delayed-type=direct`.
- Al crear `request.created`, `request-svc` publica además un mensaje al `domain.delayed` con header `x-delay=<ttl_ms>` y routing key `request.expire`.
- Cuando el TTL vence, el broker entrega el mensaje a `request-svc`, que verifica si la solicitud sigue en estado `RESERVADA` (no se materializó ni se canceló) y publica `request.expired`. La cadena Publish-Subscribe normal hace que `inventory-svc` libere el stock.

### Comportamiento ante materialización temprana

Si la solicitud se materializa antes del TTL, el mensaje delayed eventualmente llegará pero `request-svc` lo descartará (la solicitud ya está en estado `MATERIALIZADA`). La idempotencia natural del consumidor evita efectos no deseados.

### Por qué Message Expiration y no cron

Cron requiere: scheduler propio, persistencia separada, lógica de "qué solicitudes están pendientes", reintentos en caso de caída del scheduler, lock distribuido si el cron corre en múltiples réplicas. Message Expiration colapsa todo eso a una decisión: "el broker ya hace eso, dejémoslo hacer su trabajo".

---

## 4. Dead Letter Channel

### Problema

Un consumidor puede fallar al procesar un mensaje por razones permanentes (payload corrupto, regla violada, bug de integración). Reintentar indefinidamente bloquea la cola y degrada al sistema. Descartar silenciosamente esconde el problema.

### Solución

Un Dead Letter Channel es un canal aparte donde se desvían los mensajes que no se pudieron procesar tras N intentos. Permite analizarlos sin bloquear el flujo principal y sin perderlos.

### Implementación en el sistema

- Exchange `domain.dlx` (fanout) declarado como Dead Letter Exchange para todas las colas de consumo de `domain.events`.
- Argumentos por cola: `x-dead-letter-exchange=domain.dlx`, `x-message-ttl=<configurable>`, sin `x-max-retries` (la lógica de reintento la maneja la app).
- Política de reintento aplicativa: hasta 3 reintentos con backoff exponencial (1s, 5s, 25s); al cuarto fallo se hace `nack(requeue=false)` y el broker lo enruta al DLX.
- Cola `audit.dead-letters` consume todo lo que llega al DLX y persiste en una tabla `dead_letter_log` con el payload, headers, motivo del último fallo y stack trace. Sirve como bandeja de incidentes para el equipo.

### Por qué Dead Letter Channel y no logs

Los logs son texto y se rotan; un DLQ es un mensaje completo, replayable. Cuando un bug se arregla, los mensajes muertos se pueden reinyectar al flujo normal con una herramienta administrativa (no implementada en MVP, pero el diseño lo habilita).

---

## 5. Request-Reply

### Problema

Algunos pasos del flujo no pueden completarse sin información sincrónica de otro servicio. Antes de crear una solicitud, `request-svc` necesita saber con certeza si hay stock disponible (no puede tomar la decisión por evento porque el evento llega después). Antes de aceptar la solicitud, necesita el score de riesgo del usuario para aplicar la regla RC.11.

### Solución

Request-Reply sobre AMQP: el cliente publica un mensaje en una cola de comandos con headers `replyTo` (cola privada del cliente) y `correlationId`. El servidor procesa, publica la respuesta en la `replyTo` con el mismo `correlationId`. El cliente espera la respuesta haciendo match por `correlationId`.

### Implementación en el sistema

- Exchange `domain.commands` (direct).
- Colas: `inventory.validate`, `risk.score`.
- En NestJS, `@MessagePattern('inventory.validate')` declara el handler en el servidor.
- En el cliente, `ClientProxy.send(...).toPromise()` retorna una promesa con la respuesta o timeout.
- Timeouts: 2 segundos para `inventory.validate`, 1.5 segundos para `risk.score`. Pasado el timeout, `request-svc` aplica fallback (denegar para inventario; aceptar con score neutro 0.5 para riesgo, registrando degradación).

### Por qué Request-Reply sobre AMQP y no HTTP

Mantener todo el tráfico inter-servicio sobre el broker permite reusar la observabilidad (trace-id en headers AMQP), la política de retry/DLQ y la topología única. Cambiar el transporte a HTTP rompería tres infraestructuras transversales para no ganar nada operacional.

### Por qué Request-Reply síncrono para scoring y no Publish-Subscribe

El scoring afecta la decisión inmediata de aceptar la solicitud. Hacerlo asíncrono obligaría a un estado intermedio "pendiente de score" en `request-svc`, con reintentos y compensaciones, todo para ahorrar 200 ms. La complejidad no se justifica.

---

## Patrones de soporte (uso transversal)

### Document Message

Todo evento es un Document Message: payload JSON autocontenido con la información necesaria para que el receptor actúe sin consultar al emisor. Si un campo no está en el payload, el evento está mal diseñado o falta una versión nueva del esquema.

### Correlation Identifier

Header `x-correlation-id` se propaga en toda la cadena: solicitud creada → préstamo emitido → notificación entregada → ticket generado, todos comparten el mismo correlation id, lo que permite reconstruir un flujo de negocio completo en Grafana Loki/Tempo.

### Idempotent Receiver

Cada consumidor mantiene una tabla `processed_events(eventId, sourceService, processedAt)` y descarta eventos ya procesados. Esto habilita la garantía de "al menos una vez" del broker sin efectos duplicados (un préstamo no se descuenta dos veces si el evento llega dos veces).

### Transactional Outbox

Cada servicio publisher tiene tabla `outbox_events(id, aggregateId, eventType, payload, headers, createdAt, status, publishedAt)`. La transacción de negocio inserta en `outbox_events` con `status='pending'`. Un relay (`@nestjs/schedule` cada 500 ms) lee los `pending`, publica al broker, marca `published`. Garantiza atomicidad cambio-en-BD ↔ publicación.

### Message Channel

Concepto base de Hohpe: cualquier canal abstracto por donde fluyen mensajes. En la implementación se mapea a (exchange + binding + queue) en RabbitMQ. Se nombra aquí para completitud teórica.

---

## Diagramas

Los íconos oficiales de Hohpe (los iconos azules y rojos del libro de EIP) están disponibles como shapes en draw.io. Los diagramas de cada patrón en este sistema viven en `docs/architecture/diagrams/eip/`:

- `pubsub-loan-issued.drawio` — `loan-svc` publica `loan.issued`; `inventory-svc`, `notification-svc` y reportes consumen.
- `cbr-notifications.drawio` — el router interno de `notification-svc` decide destinatarios.
- `expiration-reserva.drawio` — flujo completo del TTL de reserva con `domain.delayed`.
- `dlc-failed-events.drawio` — captura de mensajes muertos en `audit.dead-letters`.
- `request-reply-scoring.drawio` — `request-svc` ↔ `ai-risk-svc` síncrono.

Generación de diagramas — tarea #9 del backlog del proyecto.

---

## Cobertura de la rúbrica

El bloque "Arquitectura y patrones (EIP)" de la rúbrica exige evidenciar uso explícito de patrones de Hohpe, no solo nombrarlos. Este catálogo, junto con los diagramas y la matriz evento ↔ patrón en `03-eventos-dominio.md`, materializa esa evidencia: cada patrón está nombrado, justificado, configurado y enlazado a un caso del dominio. La defensa en mesa redonda usa este documento como referencia central.
