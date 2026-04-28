# Architecture Decision Records (ADRs)

Registro de decisiones arquitectónicas del Sistema de Pañol. Formato: MADR breve (Contexto / Decisión / Alternativas / Consecuencias).

| ID | Decisión | Estado |
|---|---|---|
| [ADR-001](ADR-001-stack-tecnologico.md) | Stack tecnológico base (TypeScript + NestJS + PostgreSQL + RabbitMQ + Next.js + Vite). | Aceptada |
| [ADR-002](ADR-002-postgresql-vs-mongodb.md) | PostgreSQL único en lugar de MongoDB del MERN original. | Aceptada |
| [ADR-003](ADR-003-nestjs-vs-express.md) | NestJS en lugar de Express puro. | Aceptada |
| [ADR-004](ADR-004-microservicios-vs-monolito.md) | 8 microservicios en lugar de monolito modular. | Aceptada |
| [ADR-005](ADR-005-rabbitmq-vs-kafka.md) | RabbitMQ en lugar de Kafka. | Aceptada |
| [ADR-006](ADR-006-saga-coreografiada-vs-orquestada.md) | Saga coreografiada en lugar de orquestada (Temporal). | Aceptada |
| [ADR-007](ADR-007-notificaciones-in-app-vs-email.md) | Notificaciones in-app en MVP, email diferido. | Aceptada para MVP |
| [ADR-008](ADR-008-gateway-propio-vs-kong.md) | API Gateway propio en NestJS (BFF) en lugar de Kong/Traefik. | Aceptada para MVP |
| [ADR-009](ADR-009-cloud-agnostico.md) | Diseño cloud-agnóstico, sin lock-in a AWS/Azure/GCP. | Aceptada |
| [ADR-010](ADR-010-reserva-stock-ttl.md) | Reserva de stock con TTL configurable usando Message Expiration. | Aceptada |
| [ADR-011](ADR-011-pin-totem-sesion-persistente.md) | PIN de 4 dígitos en tótem con sesión persistente durante el turno. | Aceptada |
| [ADR-012](ADR-012-qr-codigo-barras-roadmap.md) | QR y código de barras como roadmap, fuera del MVP. | Aceptada para MVP |
| [ADR-013](ADR-013-sso-federado-roadmap.md) | SSO federado como roadmap; JWT local en MVP. | Aceptada para MVP |
| [ADR-014](ADR-014-coordinador-administra-docentes.md) | Coordinador puede administrar usuarios Docentes (extiende el Caso 11). | Aceptada |
| [ADR-015](ADR-015-reports-svc-read-model.md) | Reports-svc como microservicio dedicado con read-model propio (CQRS). | Aceptada |
| [ADR-016](ADR-016-despliegue-uis-path-routing.md) | Despliegue de UIs con puerto separado en MVP, JWT en header. | Aceptada para MVP |

## Cómo agregar un ADR

1. Copiar el archivo más reciente como plantilla.
2. Numerar consecutivamente (`ADR-NNN-titulo-corto.md`).
3. Escribir Contexto / Decisión / Alternativas / Consecuencias.
4. Agregar entrada en esta tabla y enlace cruzado en los documentos de `docs/architecture/` que dependan de la decisión.
5. Si la decisión reemplaza otra, marcar la anterior como `Reemplazada por ADR-NNN` y la nueva con `Reemplaza a ADR-MMM`.
