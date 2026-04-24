# CLAUDE.md — Sistema de Pañol (Proyecto Integrador MCI)

Este archivo es el contexto raíz del proyecto para Claude Code y otros agentes. Antes de escribir código o documentación, leer este archivo y, si la tarea lo amerita, los MDs referenciados en `docs/`.

## Qué es este proyecto

Sistema de gestión de préstamos de materiales, herramientas y equipos para un Pañol universitario (Caso 11 del Magíster en Ingeniería Informática, UNAB). El sistema tiene dos frentes: una aplicación web pública para que alumnos y docentes creen solicitudes en línea, y un tótem local en el pañol donde el pañolero valida solicitudes, registra préstamos y devoluciones.

Es a la vez un trabajo académico (video final con rúbrica) y un proyecto con prototipo funcional real.

## Stack obligatorio

- **Backend**: Node.js + TypeScript + NestJS (microservicios). No Express puro.
- **Broker de mensajes**: RabbitMQ. Toda comunicación entre servicios va por el broker, no HTTP directo (salvo excepciones justificadas).
- **Base de datos**: PostgreSQL con Prisma ORM. No MongoDB — sustitución consciente respecto del stack MERN original (ver `docs/design/adrs/ADR-002-descartar-mongodb.md`).
- **Frontend web (portal alumnos/docentes)**: Next.js + TypeScript.
- **Frontend tótem (pañolero)**: Vite + React + TypeScript.
- **IA**: Servidor MCP (`@modelcontextprotocol/sdk`) expuesto al asistente; cliente adapta MCP a OpenAI function calling.
- **Autenticación**: JWT local (SSO federado en roadmap).
- **Observabilidad**: OpenTelemetry + Pino + Grafana/Loki.
- **Testing**: Jest + Supertest + Playwright.
- **Infra de desarrollo**: Docker + docker-compose.

## Arquitectura en una frase

Microservicios reales separados, event-driven sobre RabbitMQ, con Saga coreografiada para transacciones distribuidas (préstamo/devolución/expiración de reserva TTL), applicando Enterprise Integration Patterns de Hohpe de forma explícita.

Detalle en `docs/architecture/`.

## Metodología

LeSS básico con dos equipos Feature, un único Product Backlog, Product Owner único, Sprint Review conjunta. Gestión en Taiga. Detalle en `docs/standards/methodology/`.

## Qué SÍ hacer

- Seguir los ADRs de `docs/design/adrs/`. Si necesitas desviarte de una decisión, crea un nuevo ADR que la actualice — no modifiques el original.
- Tipar todo. `any` solo en boundary de librerías sin tipos, con comentario que lo justifique.
- Validar entrada en los borders con `class-validator` (DTO NestJS) o `zod` (frontends).
- Publicar eventos de dominio en RabbitMQ con el contrato definido en `docs/architecture/03-eventos-dominio.md`.
- Escribir tests para cualquier flujo que cruce un boundary de servicio.
- Usar Conventional Commits.

## Qué NO hacer

- No llamar HTTP entre microservicios (salvo API Gateway → servicios, o casos justificados).
- No acceder a la BD de otro servicio. Cada servicio es dueño de su schema.
- No mezclar responsabilidades entre frontends (el tótem no hace crear-cuenta; el portal no hace validación de préstamo).
- No usar `enviar email` — notificaciones son **in-app** en esta fase (ver `ADR-007-notificaciones-in-app.md`).
- No implementar QR/código de barras todavía — está en roadmap, no en MVP.
- No introducir librerías sin actualizar `docs/standards/00-coding-standards.md`.

## Cómo arrancar

1. Leer `docs/requirements/` para entender el caso.
2. Leer `docs/architecture/00-overview.md` y `03-eip-catalog.md`.
3. Leer los ADRs relevantes en `docs/design/adrs/`.
4. Levantar infra local con `docker-compose up` (ver `docs/standards/00-coding-standards.md`).

## Documentación

- `docs/requirements/` — caso, RF/RS, casos de uso, trazabilidad.
- `docs/architecture/` — stack, topología, EIP, SAGA, IA+MCP, eventos.
- `docs/design/adrs/` — decisiones arquitecturales y sus justificaciones.
- `docs/design/diagrams/` — diagramas `.drawio` (EIP Hohpe, C4, secuencia).
- `docs/standards/` — convenciones de código, testing, Git flow, CI/CD.
- `docs/standards/methodology/` — LeSS aplicado al proyecto.
