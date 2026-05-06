# Plan de Desarrollo — Sistema de Pañol

**Branch:** `feature/ppt` (renombrar a `develop` cuando arranque desarrollo).
**Fecha plan:** 26 de abril de 2026.
**Aprobado por:** Marcelo.
**Estrategia general:** infraestructura primero → smoke tests → bootstrap monorepo → design system → vertical slices (Opción B) → servicios transversales → cierre con `.pptx` y video.

---

## Principios de ejecución

1. **Cada fase termina con una Definition of Done verificable** — no se avanza con "casi funciona".
2. **El delta entre desarrollo y documentación se anota en `docs/CHANGELOG-DEV.md` apenas ocurre** — para que la actualización final de la PPT sea mecánica, no arqueología.
3. **Los estándares de `docs/standards/` son ley** desde la primera línea de código (hexagonal, testing, coding conventions). No se "agrega después".
4. **Cada slice es demostrable end-to-end** — preferimos profundidad vertical antes que ancho horizontal.
5. **Commits chicos y temáticos** — un PR por capítulo del plan, no megacommits.

---

## Fase 0 — Housekeeping (5–10 min)

Limpiar la baseline antes de tocar código.

**Acciones**

1. Crear `.gitattributes` con `* text=auto eol=lf` para evitar la guerra CRLF/LF.
2. `git add --renormalize .` y commit del cambio de line endings.
3. Commit de `docs/REPORTE-REVISION-ENTREGABLES.md` y `docs/REORDEN-TAREAS.md` (creados fuera de sesión).
4. Push de `feature/ppt`.

**Definition of Done**

- `git status` limpio.
- `git diff` ignorando whitespace = `git diff` real.

---

## Fase 1 — Infraestructura base (docker-compose)

Levantar lo mínimo para que cualquier microservicio del Sprint 0 conecte a su backing service.

**Servicios incluidos**

| Servicio | Imagen | Propósito | Puerto host |
|---|---|---|---|
| postgres | `postgres:16-alpine` | 7 bases por servicio (auth, inventory, request, loan, notification, ai-risk, reports) | 5432 |
| mongodb | `mongo:7` | catálogo de inventario (polyglot, ADR-002) | 27017 |
| rabbitmq | custom (3.12-management + plugin delayed) | bus de eventos + comandos + delayed + DLX | 5672 / 15672 |
| adminer | `adminer:latest` | UI de inspección Postgres | 8080 |
| mongo-express | `mongo-express:latest` | UI de inspección Mongo | 8081 |

**Archivos creados**

```
infra/
├── docker-compose.yml
├── .env.example
├── README.md
├── postgres/
│   └── init/01-create-databases.sql
└── rabbitmq/
    ├── Dockerfile
    ├── enabled_plugins
    └── definitions.json
```

`definitions.json` declara desde el inicio los 4 exchanges (`domain.events` topic, `domain.commands` direct, `domain.delayed` x-delayed-message, `domain.dlx` fanout) — alineado con `docs/architecture/02-topologia-microservicios.md`.

**Definition of Done**

- `docker compose up -d` deja todo healthy en < 60s.
- RabbitMQ Management UI (`http://localhost:15672`) muestra los 4 exchanges declarados.
- Adminer (`http://localhost:8080`) lista las 7 bases.
- Mongo Express (`http://localhost:8081`) responde.

---

## Fase 2 — Smoke tests (Python)

Validar la infra capa por capa antes de meter NestJS y Prisma.

**Archivos creados**

```
infra/smoke-tests/
├── requirements.txt
├── conftest.py                  # fixtures: conexiones a postgres/mongo/rabbitmq
├── test_01_postgres.py          # connect + create temp table + tx commit/rollback
├── test_02_mongo.py             # connect + insert + find + delete
├── test_03_rabbitmq_basic.py    # publish a domain.events → consumer recibe
├── test_04_delayed_exchange.py  # TTL 3s en domain.delayed → entrega tardía verificada
├── test_05_dlx.py               # mensaje rechazado N veces → cae a domain.dlx
├── test_06_request_reply.py     # correlation_id + reply_to vía cola temporal
├── test_07_outbox.py            # insert outbox + relay polling publica al broker
└── run_all.py                   # corre los 7 con reporte resumen
```

**Definition of Done**

- `python infra/smoke-tests/run_all.py` imprime `7/7 OK` con tiempos y termina con exit code 0.
- Cada test mapea 1:1 a un EIP del catálogo (`docs/architecture/04-eip-catalog.md`).

---

## Fase 3 — Bootstrap del monorepo (TypeScript)

Estructura siguiendo `01-stack-tecnologico.md` y el template hexagonal.

**Setup**

- `pnpm` 9 + `turborepo` 2.
- TypeScript 5 con `strict: true` global.
- ESLint + Prettier + Vitest configurados a nivel root.
- Husky + commitlint para mantener convenciones.

**Estructura inicial**

```
apps/                # microservicios + frontends (vacío inicialmente)
libs/
├── events/          # esquemas Zod por evento + headers x-schema-version
├── messaging/       # cliente AMQP (publish, consume, outbox, idempotent receiver)
├── auth/            # JWT helpers (sign, verify, refresh)
├── db/              # Prisma config + helpers compartidos
└── observability/   # OTel SDK setup (DEFERRED a Sprint 2 según US-049)
```

**Definition of Done**

- `pnpm install && pnpm lint && pnpm test` pasa en verde sin apps todavía.
- README de root con cómo levantar y cómo agregar un servicio nuevo (replicar template hexagonal).

---

## Fase 3.5 — Design System (libs/ui-kit)

Acordar lenguaje visual antes de construir pantallas. Versión liviana, no producto en sí.

**Alcance**

- **Tokens** (TS module): paleta UNAB + neutros, tipografía (Inter), spacing 4px-base, radius 4/8/16, shadows, motion.
- **Tailwind config compartido** consumiendo los tokens. No más colores hardcoded.
- **6–8 componentes base** sobre **shadcn/ui + Radix UI**: `Button`, `Input`, `Select`, `Card`, `Dialog`, `Toast`, `Table`, `FormField`.
- **Dos modos por componente**: `density="comfortable"` (portal) vs `density="touch"` (tótem — fuentes 1.25×, hit areas ≥ 44px, contraste alto WCAG AAA).
- **Storybook** para auditar visualmente.
- **A11y baseline**: contraste WCAG AA mínimo, focus visible, ARIA en componentes interactivos, soporte de teclado.

**Archivos**

```
libs/ui-kit/
├── package.json
├── tailwind.config.ts
├── src/
│   ├── tokens/
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   ├── spacing.ts
│   │   └── index.ts
│   ├── components/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Card.tsx
│   │   ├── Dialog.tsx
│   │   ├── Toast.tsx
│   │   ├── Table.tsx
│   │   └── FormField.tsx
│   └── index.ts
└── .storybook/
```

**Definition of Done**

- `pnpm --filter ui-kit storybook` abre Storybook con los 8 componentes en ambos modos.
- Test de contraste automatizado pasa para todas las combinaciones de fondo/texto.
- Documentación de tokens y uso en `libs/ui-kit/README.md`.

---

## Fase 4 — Slice 1: CU1 Login

Primer flujo end-to-end visible desde el navegador.

**Servicios**

- `apps/auth-svc` (NestJS hexagonal): domain (User, Credentials), application (LoginUseCase, RefreshUseCase), infrastructure (Postgres repo con Prisma, JWT signer, HTTP controller, AMQP publisher para `user.logged_in`).
- `apps/api-gateway` (NestJS): expone `/auth/login`, `/auth/refresh`, `/auth/me`, hace proxy a auth-svc, valida JWT en middleware.
- `apps/web-portal` (Next.js 14 standalone): página `/login` consumiendo ui-kit, TanStack Query, interceptor que adjunta JWT y maneja refresh automático.

**Eventos publicados**

- `user.logged_in` (auth-svc → domain.events)

**Definition of Done**

- Usuario seedeado hace login en `localhost:3000/login`, recibe JWT, ve dashboard "Hola, {nombre}".
- Refresh token rota correctamente al expirar el access token (TTL corto en dev, 30s).
- Test E2E con Playwright cubre login feliz + credenciales inválidas.
- Trace OTel atraviesa portal → gateway → auth-svc (DEFERRED si OTel no se monta hasta Sprint 2; entonces logs estructurados con request-id manual).

---

## Fase 5 — Slices 2–5

Cada slice replica el patrón del Slice 1: agrega los servicios necesarios, los eventos AMQP, la UI mínima.

| Slice | CU | Servicios nuevos | UI nueva | Eventos clave |
|---|---|---|---|---|
| 2 | CU2 — Crear solicitud | `inventory-svc`, `request-svc` | catálogo + carrito en portal | `request.created`, `inventory.reserved` |
| 3 | CU3 — Materializar préstamo | `loan-svc` | tótem (Vite) con escaneo manual | `loan.created`, `inventory.consumed` |
| 4 | CU4 — Devolución | (loan-svc existente) | flujo devolución en tótem | `loan.closed`, `inventory.replenished` |
| 5 | CU7 — Asistente | `ai-assistant-svc` | chat en portal | `assistant.message_sent` |

**Definition of Done por slice**

- Test E2E Playwright cubre el camino feliz del CU + un caso alterno relevante.
- `request.created` y `loan.created` siguen el patrón Outbox + Idempotent Receiver del Slice 1.
- El delta vs documentos se registra en `CHANGELOG-DEV.md`.

---

## Fase 6 — Servicios transversales

Se enchufan al bus consumiendo eventos ya publicados — sin UI nueva, solo enriquecen.

- `notification-svc`: consume `loan.created` y `loan.closed`, publica `notification.delivered`, genera tickets PDF.
- `ai-risk-svc`: consume `loan.closed` y `loan.overdue`, publica `risk.scored`. Request-Reply vía AMQP cuando `loan-svc` lo invoca antes de materializar.
- `reports-svc` (ADR-015): consume todos los eventos de dominio, mantiene proyecciones CQRS read-only para los reportes de Jefe de Carrera.

**Definition of Done**

- Cada uno tiene tests unitarios de su lógica + un test de contrato (consumer-driven) para los eventos que consume.
- El portal muestra notificaciones en tiempo real vía Socket.IO desde el gateway.

---

## Fase 7 — Cierre: PPT + video

1. Actualizar `docs/presentation/PPT-content.md` con los deltas registrados en `CHANGELOG-DEV.md`.
2. Decidir si actualizar DC-01..03 + EIP-01..02 con `reports-svc` (decisión del usuario, no bloqueante).
3. Exportar los 19 (o 20) `.drawio` a PNG @300dpi y SVG.
4. Generar `docs/presentation/Panol-Sistema.pptx` siguiendo el skill `pptx`.
5. Pase visual de las 29 slides; ajustes de layout.
6. Grabar el video.

---

## Decisiones tomadas

1. **Observabilidad (OTel + Grafana)** se difiere a Sprint 2 según US-049. En Fases 1–4 usamos logs estructurados con `request-id` propagado manualmente.
2. **Seeds de datos** se generan en cada slice (en su propio `prisma/seed.ts`), no en Fase 1. Excepción: en Fase 1 se crean usuarios baseline (1 alumno, 1 pañolero, 1 coord, 1 jc) para los smoke tests del slice 1.
3. **CI/CD**: GitHub Actions con lint + tests por PR se monta en Fase 3 (bootstrap). Pipeline mínimo al inicio, se enriquece con cada slice.
4. **Dev environment**: Docker Desktop estándar + VS Code local. No devcontainers en esta iteración (riesgo de overhead innecesario).

---

## Riesgos y contingencias

| Riesgo | Probabilidad | Impacto | Contingencia |
|---|---|---|---|
| Plugin delayed-message de RabbitMQ no carga | Media | Alto | Fallback: TTL en cola con `x-message-ttl` (sin delayed exchange — pierde flexibilidad pero funciona) |
| shadcn/ui choca con SSR de Next.js | Baja | Medio | Usar `next/dynamic` o "use client" en componentes interactivos |
| Setup hexagonal genera fricción en velocidad inicial | Media | Bajo | Aceptado — el costo se paga una vez y permea todo el proyecto |
| Tiempo se acorta y no se llega a Slice 5 (asistente) | Media | Medio | Slice 5 es el menos crítico de la rúbrica; se puede mostrar como "trabajo en progreso" si no termina |
| OpenAI API rate limit en demo | Baja | Medio | Usar `gpt-4o-mini` con caché de respuestas para el video |

---

## Próximos pasos inmediatos

1. Ejecutar Fase 0 (housekeeping) — *manual del usuario*.
2. Aprobar este plan — *check con Marcelo*.
3. Crear `infra/` (docker-compose + smoke tests) — *Fase 1+2 en bundle*.
4. Levantar la infra y correr `python infra/smoke-tests/run_all.py`.
5. Si 7/7 OK → arrancar Fase 3 (bootstrap monorepo).
