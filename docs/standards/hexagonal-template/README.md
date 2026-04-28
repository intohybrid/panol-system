# Plantilla hexagonal — referencia de scaffold

## Propósito

Esta carpeta documenta la **estructura canónica de carpetas y archivos** que debe tener un microservicio nuevo del Sistema de Pañol. Es una referencia textual, no código ejecutable — el scaffolding real se incorpora al monorepo en el Paso 2 de la implementación.

Úsala como checklist cuando:

- Se crea un microservicio nuevo.
- Se revisa uno existente para verificar que sigue la convención.
- Se incorpora un desarrollador nuevo al equipo.

La especificación completa de por qué existe cada carpeta está en `../01-hexagonal-architecture.md`. Este README solo lista la estructura.

---

## Estructura de archivos por microservicio estándar

Aplica a los ocho servicios de dominio: `auth-svc`, `inventory-svc`, `request-svc`, `loan-svc`, `notification-svc`, `ai-risk-svc`, `ai-assistant-svc`, `api-gateway`.

```
apps/<service>-svc/
├── src/
│   ├── domain/                              # Capa 1 — núcleo de negocio
│   │   ├── <agregado>/
│   │   │   ├── <agregado>.ts                # Entidad agregada
│   │   │   ├── <agregado>.events.ts         # Eventos de dominio que emite
│   │   │   ├── <vo>.vo.ts                   # Value objects del agregado
│   │   │   └── <status>.ts                  # Enums/constantes del agregado
│   │   ├── errors/
│   │   │   ├── base.ts                      # DomainError abstracta
│   │   │   └── <specific>-error.ts
│   │   └── services/                        # Domain services (opcional)
│   │       └── <name>.service.ts
│   │
│   ├── application/                         # Capa 2 — casos de uso
│   │   ├── use-cases/
│   │   │   ├── <command-name>/
│   │   │   │   ├── <command>.use-case.ts
│   │   │   │   └── <command>.input.ts       # Tipo del input (opcional, si es complejo)
│   │   │   └── <query-name>/
│   │   │       └── <query>.use-case.ts
│   │   └── ports/                           # Interfaces que infrastructure implementa
│   │       ├── <agregado>-repository.port.ts
│   │       ├── event-publisher.port.ts
│   │       ├── clock.port.ts
│   │       ├── id-generator.port.ts
│   │       └── <external>-client.port.ts
│   │
│   ├── infrastructure/                      # Capa 3 — adaptadores
│   │   ├── inbound/                         # Adaptadores primarios (driving)
│   │   │   ├── http/
│   │   │   │   ├── <agregado>.controller.ts
│   │   │   │   ├── dto/
│   │   │   │   │   ├── <command>.dto.ts
│   │   │   │   │   └── <query-response>.dto.ts
│   │   │   │   ├── mappers/
│   │   │   │   │   └── <agregado>.http-mapper.ts
│   │   │   │   └── filters/
│   │   │   │       └── domain-exception.filter.ts
│   │   │   └── messaging/
│   │   │       ├── <event>.consumer.ts
│   │   │       └── mappers/
│   │   │           └── <event>.payload-mapper.ts
│   │   │
│   │   ├── outbound/                        # Adaptadores secundarios (driven)
│   │   │   ├── persistence/
│   │   │   │   ├── prisma/
│   │   │   │   │   ├── schema.prisma
│   │   │   │   │   └── migrations/
│   │   │   │   ├── prisma.service.ts
│   │   │   │   ├── prisma-<agregado>.repository.ts
│   │   │   │   ├── <agregado>.prisma-mapper.ts
│   │   │   │   └── prisma-unit-of-work.ts
│   │   │   ├── messaging/
│   │   │   │   ├── amqp.publisher.ts        # wrapper sobre amqplib
│   │   │   │   └── outbox/
│   │   │   │       ├── outbox-event.publisher.ts
│   │   │   │       └── outbox-relay.service.ts
│   │   │   ├── external/                    # clientes HTTP de otros servicios
│   │   │   │   └── <external>-http.client.ts
│   │   │   ├── clock/
│   │   │   │   └── system-clock.ts
│   │   │   └── id-generator/
│   │   │       └── uuid-id-generator.ts
│   │   │
│   │   └── modules/                         # Composición NestJS
│   │       ├── persistence.module.ts
│   │       ├── messaging.module.ts
│   │       ├── <agregado>.module.ts
│   │       └── app.module.ts
│   │
│   ├── config/
│   │   └── env.schema.ts                    # Zod schema de .env
│   │
│   ├── shared/                              # helpers específicos del servicio
│   │   └── logger.module.ts
│   │
│   ├── main.ts                              # bootstrap del HTTP server
│   └── bootstrap.ts                         # arranque del microservicio AMQP
│
├── test/
│   ├── fakes/                               # implementaciones fake de puertos
│   │   ├── in-memory-<agregado>.repository.ts
│   │   ├── in-memory-event.publisher.ts
│   │   ├── frozen-clock.ts
│   │   └── fixed-id-generator.ts
│   ├── factories/
│   │   └── <agregado>.factory.ts
│   ├── integration/
│   │   ├── prisma-<agregado>-repository.integration-spec.ts
│   │   └── outbox-relay.integration-spec.ts
│   ├── contract/
│   │   └── <event>.contract-spec.ts
│   └── e2e/
│       └── <command>.e2e-spec.ts
│
├── Dockerfile                               # multi-stage: build + runtime
├── package.json
├── tsconfig.json
├── jest.config.ts
├── .env.example
└── README.md                                # qué hace el servicio, cómo correrlo
```

---

## Variante para `reports-svc`

El read-model no tiene reglas de negocio. Estructura reducida:

```
apps/reports-svc/
├── src/
│   ├── projections/
│   │   └── <proyeccion>/
│   │       ├── <proyeccion>.projection.ts   # shape de la tabla proyectada
│   │       └── <proyeccion>.handler.ts      # consume eventos, hace upserts
│   ├── queries/
│   │   └── <query-name>/
│   │       ├── <query>.ts                   # clase con método execute(params)
│   │       └── <query>.dto.ts               # shape de respuesta
│   ├── infrastructure/
│   │   ├── inbound/
│   │   │   ├── http/                        # endpoints solo de lectura
│   │   │   └── messaging/                   # event handlers que alimentan projections
│   │   └── outbound/
│   │       └── persistence/
│   │           └── prisma/                  # read-model desnormalizado
│   ├── config/
│   ├── main.ts
│   └── bootstrap.ts
├── test/
│   ├── integration/
│   └── contract/
└── Dockerfile
```

Diferencias:
- No hay `domain/`.
- No hay `application/use-cases/`; se reemplaza por `queries/` (lecturas) y `projections/` (actualizaciones).
- No hay outbox (no publica eventos de dominio).
- Idempotencia se mantiene con `processed_events` en el módulo de messaging.

---

## Archivos raíz esperados por servicio

| Archivo | Contenido mínimo |
|---|---|
| `package.json` | scripts `build`, `dev`, `start`, `lint`, `typecheck`, `test`, `test:integration`, `test:e2e`. Dependencias del servicio. |
| `tsconfig.json` | extiende `../../tsconfig.base.json`. Define `outDir: dist`. |
| `jest.config.ts` | config de Jest, paths, roots para cada tipo de test. |
| `Dockerfile` | multi-stage: stage `builder` (instala deps, compila TS), stage `runtime` (Node slim + dist + node_modules prod). |
| `.env.example` | lista todas las variables con valores placeholder; se commitea. |
| `.env` | real, con secrets locales; se ignora en `.gitignore`. |
| `README.md` | nombre del servicio, responsabilidad (link a `docs/architecture/07-microservicios-responsabilidades.md`), cómo correrlo localmente, endpoints principales. |

---

## Librerías compartidas esperadas (`libs/`)

Cada microservicio importa de estas librerías del monorepo:

```
libs/
├── events/                                  # Zod schemas de todos los eventos de dominio
│   ├── user/
│   │   ├── user-created.schema.ts
│   │   └── user-blocked.schema.ts
│   ├── stock/
│   ├── request/
│   ├── loan/
│   ├── risk/
│   └── notification/
├── shared-types/                            # tipos transversales (UserRole, Carrera...)
│   └── roles.ts
├── infra-nestjs/                            # módulos Nest compartidos
│   ├── logger/
│   ├── tracing/
│   ├── rabbitmq/
│   └── prisma-utils/
└── testing/                                 # helpers para testcontainers
    ├── postgres-container.ts
    └── rabbitmq-container.ts
```

El contrato de qué va en qué lib se consolidará cuando el monorepo se inicialice. Hasta entonces, esta lista es la referencia.

---

## Checklist para crear un microservicio nuevo

Al crear o revisar un servicio, verificar:

- [ ] La estructura de carpetas coincide con la de este documento.
- [ ] `import/no-restricted-paths` de ESLint enforza la regla de dependencia hexagonal.
- [ ] Cada agregado tiene su propio directorio en `domain/<agregado>/`.
- [ ] Los puertos son interfaces TypeScript con un `Symbol` como token de inyección.
- [ ] Los casos de uso tienen un solo método público `execute`.
- [ ] Los controllers HTTP son delgados: DTO → use case → respuesta.
- [ ] Los consumers AMQP validan el payload con Zod antes de invocar el caso de uso.
- [ ] Los repositorios Prisma implementan el puerto del dominio con mappers explícitos (dominio ↔ fila).
- [ ] Outbox pattern implementado con relay programado (`@Interval(500)` o equivalente).
- [ ] Idempotent receiver: tabla `processed_events` y deduplicación en consumers.
- [ ] `Clock` e `IdGenerator` son puertos; nada en dominio llama a `new Date()` ni a `randomUUID()` directamente.
- [ ] Config de `.env` validada con Zod al arrancar.
- [ ] Tests unitarios de dominio sin NestJS ni Prisma.
- [ ] Tests de casos de uso con puertos fake (no `jest.mock`).
- [ ] Tests de integración con Testcontainers para Postgres y RabbitMQ.
- [ ] `Dockerfile` multi-stage (builder + runtime).
- [ ] `.env.example` actualizado con todas las variables.
- [ ] `README.md` del servicio linkea a `docs/architecture/07-microservicios-responsabilidades.md`.

---

## Referencias cruzadas

- `../00-coding-standards.md` — convenciones transversales (TypeScript, lint, naming).
- `../01-hexagonal-architecture.md` — explicación de cada decisión.
- `../02-testing-strategy.md` — cómo probar cada capa.
- `docs/architecture/07-microservicios-responsabilidades.md` — qué hace cada servicio.
- `docs/architecture/08-estados-entidades.md` — máquinas de estado a implementar en `domain/`.
- `docs/architecture/03-eventos-dominio.md` — contratos de eventos (la fuente de `libs/events/`).
- `docs/architecture/04-eip-catalog.md` — patrones de integración que los adaptadores materializan.
