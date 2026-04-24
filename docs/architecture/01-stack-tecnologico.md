# Stack tecnológico

## Resumen

| Capa | Tecnología | Por qué esta, no otra |
|---|---|---|
| Lenguaje backend | TypeScript | Type safety en el código que cruza boundaries de servicios; ecosistema y DX superior a JS plano. |
| Framework backend | NestJS 10 (Microservices) | Equivalente en Node del modelo que ofrece Spring/Camel en JVM: decorators, DI, soporte nativo de transportes (AMQP, Kafka, NATS, gRPC), capas claras. Mapea 1:1 a EIP (`@MessagePattern` → Request-Reply; `@EventPattern` → Publish-Subscribe). |
| Broker de mensajes | RabbitMQ 3.13 + plugins `rabbitmq_delayed_message_exchange` y `rabbitmq_shovel` | Broker "de manual" para EIP de Hohpe: exchanges `fanout`/`direct`/`topic` realizan Publish-Subscribe y Content-Based Router; queues con TTL + DLX realizan Message Expiration y Dead Letter Channel. Plugin delayed-message implementa el TTL de reservas sin job externo. |
| ORM | Prisma 5 | Type-safety punta a punta, migraciones declarativas, DX moderna, buena documentación. |
| Base de datos | PostgreSQL 16 | ACID necesario para préstamo/devolución; relaciones ricas (recurso↔préstamo↔usuario↔carrera); reportes agregados con SQL. Sustituye conscientemente a MongoDB (ver ADR-002). |
| Outbox pattern | Tabla `outbox_events` + relay con `@nestjs/schedule` | Garantiza "publicar evento y persistir BD" como una unidad. Sin outbox no hay saga confiable. |
| Autenticación | `@nestjs/passport` + `passport-jwt` + `bcrypt` | Estándar NestJS. SSO federado en roadmap (Keycloak/OIDC). |
| API Gateway / BFF | NestJS propio (REST + WebSocket para notificaciones in-app) | Simple, mismo stack. No usamos Kong/Traefik en MVP para reducir complejidad operativa. |
| Frontend web (portal) | Next.js 14 + React 18 + TypeScript + TanStack Query | SSR útil para primera carga y metadata; auth robusta con middleware; TanStack Query para cache de estado servidor. |
| Frontend tótem | Vite 5 + React 18 + TypeScript + Zustand | SPA liviana fullscreen; Zustand para estado local simple (sesión de pañolero, turno de atención). |
| IA — Scoring | Servicio `ai-risk-svc` en NestJS con modelo entrenado en Python (scikit-learn) expuesto vía `onnxruntime-node` o API HTTP a un container Python | Entrena offline con datos sintéticos; sirve online en Node para mantener el stack coherente. |
| IA — Asistente | Servidor MCP con `@modelcontextprotocol/sdk` + cliente que adapta MCP a OpenAI function calling | MCP como contrato estándar entre el LLM y las tools de dominio (inventario, solicitudes). Function calling de OpenAI como motor de razonamiento. |
| Notificaciones | WebSocket (Socket.IO) sobre el API Gateway + bandeja persistente en Postgres | In-app only. Correo explícitamente fuera de scope (ver ADR-007). |
| PDF del ticket | PDFKit en `notification-svc` | Generación server-side, sin dependencias de Chromium. Descargable desde el portal. |
| Observabilidad | OpenTelemetry SDK + Pino + Grafana Loki + Tempo | Traces distribuidos que cruzan HTTP y AMQP; correlation-id propagado como header AMQP. |
| Testing | Jest + Supertest (unitario + e2e API) + Playwright (e2e web) | Jest viene con Nest. Playwright superior a Cypress para tests cross-browser y paralelismo. |
| Contenedores | Docker + docker-compose (dev) | Cada servicio con su Dockerfile; un `docker-compose.yml` levanta todo el sistema local incluyendo RabbitMQ, Postgres, Grafana. |
| CI/CD | GitHub Actions | Build, test, lint, type-check, Docker build por servicio. |
| Gestión de configuración | `@nestjs/config` + `.env.schema` validado con `zod` | Validar variables de entorno al arranque falla-rápido si falta configuración. |

## Estructura del monorepo

```
panol-system/
├── apps/
│   ├── api-gateway/
│   ├── auth-svc/
│   ├── inventory-svc/
│   ├── request-svc/
│   ├── loan-svc/
│   ├── notification-svc/
│   ├── ai-risk-svc/
│   ├── ai-assistant-svc/     # incluye el servidor MCP
│   ├── web-portal/           # Next.js
│   └── totem/                # Vite + React
├── libs/
│   ├── events/               # contratos de eventos de dominio (Zod schemas)
│   ├── shared-types/
│   └── infra-nestjs/         # módulos comunes: logging, tracing, outbox
├── infra/
│   ├── docker-compose.yml
│   ├── rabbitmq/
│   └── grafana/
├── docs/
└── CLAUDE.md
```

Monorepo con `pnpm` + `turborepo`. Cada `app` se puede buildear y ejecutar en aislamiento; `libs` comparten código tipado entre apps.

## Qué se descartó y por qué

Todos los descartes tienen ADR con contexto y consecuencias:

- MongoDB → ADR-002.
- Express puro → ADR-003.
- Monolito modular → ADR-004.
- Kafka → ADR-005.
- SAGA orquestada (Temporal) → ADR-006.
- Notificaciones por email → ADR-007.
- Kong/Traefik como API Gateway → ADR-008.
- Cloud específico (AWS/Azure/GCP) → ADR-009.
