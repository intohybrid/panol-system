# ADR-010 — Reserva de stock con TTL configurable (Message Expiration)

- **Estado**: Aceptada
- **Fecha**: 2026-04-25
- **Decisores**: Equipo Magíster

## Contexto

Entre que un alumno crea una solicitud desde el portal y que se presenta en el pañol a retirar los recursos, pasan minutos u horas. En ese intervalo el stock de los recursos solicitados debe quedar "apartado" para que otros no lo pidan, pero sin descontarse del inventario real (todavía no hay entrega física). Dos problemas derivados:

1. Si la reserva fuera indefinida, un alumno que no se presenta bloquea recursos para siempre.
2. Si hubiera que liberar reservas manualmente, el Pañolero carga con una tarea de bookkeeping que el sistema debe automatizar.

El Caso 11 no menciona el concepto de reserva ni de TTL. Es una decisión del equipo derivada de la separación en el tiempo entre la creación on-line y la materialización presencial (`RF-C.01`, `RC.06`).

## Decisión

Toda solicitud crea una **reserva de stock con TTL configurable** (`RC.06`, por defecto 4 horas para solicitudes estándar, hasta 12 horas máximo; el plazo del préstamo Especial multi-día para solicitudes aprobadas). Al vencer el TTL, si la solicitud no se materializó en préstamo, la reserva se libera automáticamente y la solicitud queda en estado `VENCIDA`.

La expiración se implementa con el patrón **Message Expiration** de Hohpe, usando el plugin `rabbitmq_delayed_message_exchange`:

- Al crear `request.created`, `request-svc` publica además un mensaje de comando `request.expire(requestId)` al exchange `domain.delayed` con header `x-delay = ttl_ms`.
- El broker retiene el mensaje y lo entrega al vencer.
- `request-svc` recibe el mensaje, verifica si la solicitud sigue en `RESERVADA`; si es así, emite `request.expired`. Si no (materializada o cancelada), descarta (idempotencia natural).
- La cadena Publish-Subscribe normal hace que `inventory-svc` libere el stock.

El umbral TTL por defecto, máximo y por tipo de solicitud son parámetros configurables por el Jefe de Carrera (`RS-JC.5`).

## Alternativas consideradas

### Job cron que recorre solicitudes vencidas

- **Pros**: conceptualmente simple, cualquier dev lo entiende.
- **Contras**:
  - Introduce un proceso fuera del flujo de eventos con su propia disponibilidad, su propio scheduling y su propia idempotencia.
  - Requiere un lock distribuido si el cron corre en múltiples réplicas.
  - La granularidad de la expiración queda limitada al intervalo del cron (típicamente 1 minuto), lo que introduce una ventana de "reserva viva pero vencida".
  - Añade un componente operativo que no aporta sobre lo que el broker ya da.

### Campo `expires_at` consultado al leer disponibilidad

- **Pros**: no requiere ningún proceso de fondo.
- **Contras**:
  - Obliga a que cada consulta de disponibilidad filtre reservas vencidas, duplicando la lógica en múltiples consumers.
  - La liberación del stock no es un evento observable — no se puede notificar al usuario que su reserva expiró, no hay traza auditable.
  - Rompe el modelo event-driven: la expiración es un hecho de negocio, y un hecho de negocio debe ser un evento.

### TTL nativo de cola en RabbitMQ

- **Pros**: built-in del broker.
- **Contras**:
  - Aplica a la cola completa, no a mensajes individuales con delays distintos.
  - No cubre el caso de TTL heterogéneo (4 h para estándar, N días para Especial).

## Decisión justificada

Message Expiration con `rabbitmq_delayed_message_exchange` colapsa toda la gestión de TTL a una línea de código en el publisher y un handler idempotente en el consumer. El broker ya provee disponibilidad, reintentos y persistencia; delegarle la temporización del vencimiento elimina un componente operativo y mantiene la arquitectura homogénea (todo pasa por el broker).

Además, la expiración como evento (`request.expired`) es visible para `notification-svc` y para auditoría, cosa que el cron o el filtro en consulta no darían sin código adicional.

## Consecuencias

- Se requiere el plugin `rabbitmq_delayed_message_exchange` habilitado en la imagen de RabbitMQ (provisto en `infra/docker-compose.yml`).
- `request-svc` mantiene dos publicaciones al crear una solicitud: `request.created` (inmediato, `domain.events`) y `request.expire` (delayed, `domain.delayed`). Ambas van por outbox para atomicidad.
- Idempotencia obligatoria en el handler de `request.expire`: si la solicitud ya está materializada o cancelada al recibir el mensaje, se descarta sin efecto.
- El Jefe de Carrera controla TTL mínimos y máximos por configuración. Cambios en el TTL afectan solicitudes futuras, no las existentes (cada solicitud lleva su propio `ttlExpiresAt`).
- Defensa en mesa redonda: "el TTL no es un parche operativo; es un patrón EIP explícito (Message Expiration) con sustento teórico y ejecución delegada al broker".
