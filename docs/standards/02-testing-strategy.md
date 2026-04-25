# Estrategia de testing

## Propósito

Este documento define **qué tipos de test se escriben, dónde viven, cómo se ejecutan, y con qué herramientas**, para los nueve microservicios y los dos frontends del Sistema de Pañol. Es la contrapartida natural de `01-hexagonal-architecture.md`: si la arquitectura está bien, cada capa tiene un tipo de test claro y barato; si los tests son difíciles de escribir, la arquitectura está rota.

Cubre el requerimiento `RNF-MNT.2` (cobertura ≥ 70% en módulos de dominio) y `RNF-MNT.3` (cada servicio testeable en aislamiento).

---

## 1. Pirámide

Cuatro niveles, de más rápidos y numerosos a más lentos y selectivos:

```
        ┌──────────┐
        │   e2e    │  ~10 tests  (flujos de negocio completos, docker compose)
        ├──────────┤
        │  contract│  ~20 tests  (validar schemas de eventos y APIs)
        ├──────────┤
        │integración│ ~40 tests  (adaptadores con Postgres y RabbitMQ reales)
        ├──────────┤
        │  unitario│  ~200 tests (dominio + casos de uso, sin I/O)
        └──────────┘
```

Números orientativos para un microservicio "mediano" (auth-svc, inventory-svc). Servicios chicos como `api-gateway` tienen menos dominio y más integración HTTP.

### Objetivo de cobertura

- `domain/`: **≥ 85%** líneas y ramas. Las reglas de negocio no se pueden evolucionar con confianza si no están cubiertas.
- `application/use-cases/`: **≥ 80%** líneas.
- `infrastructure/`: **≥ 60%** líneas. Los mappers y repositories se prueban por integración, no línea por línea.
- **Promedio del servicio ≥ 70%** (`RNF-MNT.2`).

La cobertura se reporta con `jest --coverage` y se publica en CI como artefacto. No se falla el build por estar un punto debajo del umbral — se alerta.

---

## 2. Herramientas

| Nivel | Herramienta | Por qué |
|---|---|---|
| Unit | **Jest** | Ya viene con Nest; rápido; buen ecosistema de matchers. |
| Integración | **Jest + Testcontainers** | Levanta Postgres y RabbitMQ reales por test suite. Realismo sin mocks frágiles. |
| Contract | **Jest + Zod schemas de `libs/events/`** | Validar que los publishers emiten lo que los consumers aceptan. |
| E2E API | **Supertest + docker compose** | Corre el servicio real contra dependencias reales. |
| E2E UI | **Playwright** | Portal web + tótem. Cross-browser, paralelismo. |
| Property-based (opcional) | **fast-check** | Para value objects con reglas complejas (normalización de RUT, DocumentoVO). |

Frontends:

| Nivel | Herramienta |
|---|---|
| Unit (hooks, utils) | **Jest** |
| Component | **Vitest + @testing-library/react** |
| E2E | **Playwright** |

`@testing-library` prioriza queries por rol ARIA, alineado con la política de accesibilidad de `00-coding-standards.md §12`.

---

## 3. Ubicación de los tests

### Convención de archivos

| Tipo | Ubicación | Sufijo |
|---|---|---|
| Unit (dominio, app) | **al lado** del archivo bajo test | `.spec.ts` |
| Integración | `test/integration/` del servicio | `.integration-spec.ts` |
| Contract | `test/contract/` del servicio | `.contract-spec.ts` |
| E2E API | `test/e2e/` del servicio | `.e2e-spec.ts` |
| E2E UI | `apps/<frontend>/e2e/` | `.e2e.ts` (Playwright) |

Los unit co-localizados bajan la fricción (abre un archivo, ve su test al lado). Los demás van en `test/` porque requieren setup y fixtures compartidas.

### Ejemplo estructural

```
apps/auth-svc/
├── src/
│   ├── domain/
│   │   └── user/
│   │       ├── user.ts
│   │       ├── user.spec.ts               ← unit: reglas de la entidad
│   │       ├── documento.vo.ts
│   │       └── documento.vo.spec.ts       ← unit: value object
│   ├── application/
│   │   └── use-cases/create-user/
│   │       ├── create-user.use-case.ts
│   │       └── create-user.use-case.spec.ts ← unit: puertos fake
│   └── infrastructure/
│       └── outbound/persistence/
│           ├── prisma-user.repository.ts
│           └── (no .spec.ts aquí — se cubre por integración)
└── test/
    ├── integration/
    │   ├── prisma-user-repository.integration-spec.ts
    │   └── outbox-relay.integration-spec.ts
    ├── contract/
    │   └── user-created-event.contract-spec.ts
    └── e2e/
        └── create-user.e2e-spec.ts
```

---

## 4. Tests unitarios (dominio y aplicación)

### Dominio — sin framework, sin IO

Los tests de `domain/` son Jest puro. No importan `@nestjs/*`, no tocan BD, no invocan AMQP. **Si necesitas mockear algo, es que el dominio tiene una dependencia mal planteada**.

Ejemplo: test de la entidad `User`.

```ts
// domain/user/user.spec.ts
import { User } from './user';
import { DocumentoVO } from './documento.vo';
import { InvalidUserTransitionError } from '../errors/invalid-user-transition-error';
import { USER_STATUS } from './user-status';

describe('User', () => {
  const baseInput = {
    id: 'u-1',
    documento: DocumentoVO.create('RUT', '12345678-9'),
    nombres: 'Juan',
    apellidos: 'Pérez',
    role: 'ALUMNO' as const,
    carreraId: 'c-1',
    initialPasswordHash: 'hash',
  };

  it('comienza en estado CREADO', () => {
    const u = User.create(baseInput);
    expect(u.status).toBe(USER_STATUS.CREADO);
  });

  it('RC.01 - se puede bloquear por morosidad desde ACTIVO', () => {
    const u = User.create(baseInput);
    u.markPasswordChanged();
    u.blockForMorosidad();
    expect(u.status).toBe(USER_STATUS.BLOQUEADO_MOROSIDAD);
  });

  it('no se puede bloquear por morosidad si está INACTIVO', () => {
    const u = User.create(baseInput);
    u.deactivate();
    expect(() => u.blockForMorosidad()).toThrow(InvalidUserTransitionError);
  });
});
```

Cada test referencia un `RC.*` cuando aplica. Es la evidencia de que una regla del catálogo está cubierta.

### Aplicación — puertos fake

Los casos de uso se testean con **implementaciones fake** de los puertos. No se mockean con `jest.mock()` salvo excepción muy localizada. Un fake es una implementación real del puerto, en memoria, para tests:

```ts
// test/fakes/in-memory-user.repository.ts
import { UserRepository } from '../../src/application/ports/user-repository.port';
import { User } from '../../src/domain/user/user';
import { DocumentoVO } from '../../src/domain/user/documento.vo';

export class InMemoryUserRepository implements UserRepository {
  private readonly store = new Map<string, User>();

  async findById(id: string) { return this.store.get(id) ?? null; }
  async findByDocumento(d: DocumentoVO) {
    return [...this.store.values()].find((u) => u.documento.equals(d)) ?? null;
  }
  async save(u: User) { this.store.set(u.id, u); }
}
```

```ts
// application/use-cases/create-user/create-user.use-case.spec.ts
describe('CreateUserUseCase', () => {
  let users: InMemoryUserRepository;
  let events: InMemoryEventPublisher;
  let clock: FrozenClock;
  let hasher: FakePasswordHasher;
  let useCase: CreateUserUseCase;

  beforeEach(() => {
    users = new InMemoryUserRepository();
    events = new InMemoryEventPublisher();
    clock = new FrozenClock(new Date('2026-04-25T10:00:00Z'));
    hasher = new FakePasswordHasher();
    useCase = new CreateUserUseCase(users, events, clock, hasher);
  });

  it('crea un usuario y publica user.created en outbox', async () => {
    const { userId } = await useCase.execute({
      documentoTipo: 'RUT',
      documentoValor: '12345678-9',
      nombres: 'Juan',
      apellidos: 'Pérez',
      role: 'ALUMNO',
      carreraId: 'c-1',
      createdBy: 'op-1',
    });

    const saved = await users.findById(userId);
    expect(saved).not.toBeNull();
    expect(events.published).toHaveLength(1);
    expect(events.published[0]).toMatchObject({
      eventType: 'user.created',
      payload: expect.objectContaining({ userId, role: 'ALUMNO' }),
    });
  });

  it('rechaza documento duplicado', async () => {
    await useCase.execute({ ...validInput });
    await expect(useCase.execute({ ...validInput })).rejects.toThrow(DuplicateDocumentoError);
  });
});
```

Lo que ves:
- Sin `jest.mock()`.
- Los fakes son clases reales que implementan los puertos. Se pueden reusar entre tests.
- El caso de uso se instancia manualmente con `new`. Nest no se levanta.
- Rápido: miles de tests corren en segundos.

### Dónde no usar fakes

- **Jamás** se fakea `domain/`. El dominio es real siempre.
- **Jamás** se fakea lógica propia. Solo se fakean los puertos (I/O externo).

---

## 5. Tests de integración

### Objetivo

Validar que los **adaptadores** cumplen el contrato del puerto. El repositorio Prisma escribe y lee correctamente de una Postgres real. El event publisher publica correctamente a un RabbitMQ real.

### Testcontainers

Cada suite de integración levanta sus dependencias al inicio y las tira al final. Un helper compartido en `libs/testing/` expone:

```ts
import { startTestPostgres } from '@libs/testing/postgres-container';
import { startTestRabbitMq } from '@libs/testing/rabbitmq-container';

let postgres: StartedPostgresContainer;
let rabbit: StartedRabbitMqContainer;

beforeAll(async () => {
  postgres = await startTestPostgres();
  rabbit = await startTestRabbitMq();
  process.env.DATABASE_URL = postgres.connectionString;
  process.env.RABBITMQ_URL = rabbit.connectionString;
  // ejecuta migraciones Prisma
  await runMigrations(postgres.connectionString);
}, 60_000);

afterAll(async () => {
  await postgres.stop();
  await rabbit.stop();
});
```

### Ejemplo

```ts
// test/integration/prisma-user-repository.integration-spec.ts
describe('PrismaUserRepository (integration)', () => {
  let repo: PrismaUserRepository;
  let prisma: PrismaService;

  beforeAll(async () => {
    prisma = new PrismaService({ url: process.env.DATABASE_URL! });
    await prisma.$connect();
    repo = new PrismaUserRepository(prisma);
  });

  afterAll(() => prisma.$disconnect());

  beforeEach(() => prisma.user.deleteMany());

  it('persiste y recupera un usuario por documento', async () => {
    const user = User.create({ ... });
    await repo.save(user);

    const found = await repo.findByDocumento(user.documento);
    expect(found).not.toBeNull();
    expect(found!.id).toBe(user.id);
    expect(found!.documento.equals(user.documento)).toBe(true);
  });

  it('retorna null si no existe', async () => {
    expect(await repo.findById('inexistente')).toBeNull();
  });
});
```

### Integration para AMQP

El `OutboxRelayService` se testea arrancando RabbitMQ real, escribiendo filas pending en outbox, esperando a que el relay publique, y verificando que un consumer test recibe el mensaje.

```ts
// test/integration/outbox-relay.integration-spec.ts
it('publica eventos PENDING al broker y los marca PUBLISHED', async () => {
  await prisma.outboxEvent.create({
    data: { id: 'e-1', eventType: 'user.created', payload: { ... }, status: 'PENDING', ... },
  });

  const received = await waitForMessage('user.created', 5_000);
  expect(received.payload).toEqual(expect.objectContaining({ ... }));

  const row = await prisma.outboxEvent.findUnique({ where: { id: 'e-1' } });
  expect(row?.status).toBe('PUBLISHED');
});
```

### Consideraciones

- Integration tests son **más lentos** (arranque de contenedores: 3-8 s por suite). Por eso se separan de unit: unit corre en cada commit/watch, integration corre en CI y bajo demanda.
- Usar `docker` o `podman` como runtime. `@testcontainers/node` soporta ambos.
- Limpiar estado **entre tests**, no entre suites. Cada `it` debe ser independiente.

---

## 6. Contract tests

### Propósito

Los eventos de dominio son un contrato entre microservicios. Un cambio en `request-svc` que rompe `loan-svc` es el peor bug del sistema event-driven. Los contract tests lo previenen.

### Mecanismo

`libs/events/` contiene los Zod schemas de todos los eventos (`03-eventos-dominio.md`). Cada servicio publisher tiene un test que valida que su output cumple el schema:

```ts
// test/contract/user-created-event.contract-spec.ts
import { UserCreatedEventSchema } from '@libs/events/user';
import { CreateUserUseCase } from '../../src/application/use-cases/create-user/create-user.use-case';

it('emite un user.created que cumple el schema', async () => {
  // ... ejecuta el caso de uso con fakes ...
  const published = events.published[0];

  const result = UserCreatedEventSchema.safeParse(published.payload);
  expect(result.success).toBe(true);
  if (!result.success) {
    console.error(result.error.format());
  }
});
```

Y cada servicio consumer tiene un test que valida que acepta el schema del publisher:

```ts
// test/contract/loan-overdue.contract-spec.ts (en auth-svc)
import { LoanOverdueEventSchema } from '@libs/events/loan';

it('evaluate-morosidad consume payloads que cumplen loan.overdue', async () => {
  const samplePayload = {
    loanId: 'l-1',
    usuarioId: 'u-1',
    diasAtraso: 2,
    detectedAt: new Date().toISOString(),
  };
  // valida que el schema acepta
  expect(() => LoanOverdueEventSchema.parse(samplePayload)).not.toThrow();
  // y que el consumer lo procesa sin error
  await consumer.handle(samplePayload, mockCtx());
  // ... aserciones sobre el efecto en el dominio ...
});
```

### Qué NO son

No son "tests de contrato" en el sentido de Pact (consumer-driven contracts con broker de contratos). Son más modestos: usan el schema Zod compartido como fuente de verdad. Es suficiente para el MVP y no requiere infraestructura extra. Si el proyecto creciera a decenas de servicios, considerar Pact.

---

## 7. Tests end-to-end (e2e)

### Tipos

**E2E API por servicio** — el servicio real contra sus dependencias reales (Testcontainers), se hacen requests HTTP con Supertest y se verifican efectos:

```ts
// test/e2e/create-user.e2e-spec.ts
describe('POST /users (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    // levanta Postgres y RabbitMQ con Testcontainers
    // crea el módulo real de Nest con providers reales
    app = await createTestApp();
  });

  it('crea un usuario y publica user.created al broker', async () => {
    const response = await request(app.getHttpServer())
      .post('/users')
      .send({ documentoTipo: 'RUT', documentoValor: '12345678-9', nombres: 'Juan', ... })
      .expect(201);

    expect(response.body).toHaveProperty('userId');

    const message = await waitForBrokerMessage('user.created', 5_000);
    expect(message.payload.userId).toBe(response.body.userId);
  });
});
```

**E2E multi-servicio** — escenario de negocio completo cruzando varios servicios, levantados con docker-compose. Se reserva para pocos flujos críticos:

- CU2 → CU3: crear solicitud → materializar préstamo → verificar ticket en notificaciones.
- Saga TTL: crear solicitud → esperar TTL → verificar `request.expired` y liberación de reserva.
- Saga morosidad: crear préstamo → forzar atraso → verificar bloqueo automático del usuario.

Estos viven en `test/e2e/cross-service/` en la raíz del monorepo, no en un servicio específico.

**E2E UI** — Playwright en `apps/web-portal/e2e/` y `apps/totem/e2e/`. Flujos de usuario reales: login, crear solicitud, interactuar con chat asistente. Se corre contra el compose completo levantado.

### Frecuencia y ejecución

- Unit + integración: en cada push (CI).
- Contract: en cada push.
- E2E por servicio: en cada push, en paralelo por servicio.
- E2E multi-servicio: en PR a `main` y nightly.
- E2E UI: en PR a `main`.

Los flujos lentos no deben bloquear cada commit; el objetivo es no romper `main`, no bloquear el desarrollo.

---

## 8. Property-based testing (opcional)

Para lógica con invariantes claras — value objects con normalización, cálculo de score, reglas de morosidad — property-based testing con `fast-check` aporta más confianza que ejemplos manuales.

```ts
// domain/user/documento.vo.spec.ts
import fc from 'fast-check';

it('normaliza cualquier RUT equivalente al mismo value', () => {
  fc.assert(
    fc.property(
      fc.integer({ min: 1_000_000, max: 99_999_999 }),
      fc.constantFrom('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'K'),
      (numero, dv) => {
        const conPuntos = `${formatWithDots(numero)}-${dv}`;
        const sinPuntos = `${numero}-${dv}`;
        const conMayus = `${numero}-${dv.toUpperCase()}`;
        return (
          DocumentoVO.create('RUT', conPuntos).valor ===
          DocumentoVO.create('RUT', sinPuntos).valor &&
          DocumentoVO.create('RUT', sinPuntos).valor ===
          DocumentoVO.create('RUT', conMayus).valor
        );
      },
    ),
    { numRuns: 1000 },
  );
});
```

Usarlo donde la superficie de entrada sea amplia y las propiedades sean claras. No es obligatorio.

---

## 9. Fixtures y factories

Crear entidades realistas en tests es repetitivo. Un factory por agregado resuelve.

```ts
// test/factories/user.factory.ts
import { User } from '../../src/domain/user/user';
import { DocumentoVO } from '../../src/domain/user/documento.vo';

let counter = 0;

export function makeUser(overrides: Partial<{
  id: string;
  documento: DocumentoVO;
  role: UserRole;
}> = {}): User {
  counter++;
  return User.create({
    id: overrides.id ?? `u-${counter}`,
    documento: overrides.documento ?? DocumentoVO.create('RUT', `1234567${counter}-${counter}`),
    nombres: 'Juan',
    apellidos: 'Pérez',
    role: overrides.role ?? 'ALUMNO',
    carreraId: 'c-1',
    initialPasswordHash: 'hash',
  });
}
```

Uso:

```ts
const u1 = makeUser();
const u2 = makeUser({ role: 'DOCENTE' });
```

Convención:
- Un factory por agregado, en `test/factories/`.
- Valores por defecto realistas.
- `overrides` como parámetro opcional.
- Contador global para IDs únicos entre invocaciones.

---

## 10. Tests de los frontends

### Unit y componente

- Hooks puros y utils: Jest.
- Componentes React: `@testing-library/react` + `@testing-library/jest-dom`.
- Queries prioritarias: `getByRole`, `getByLabelText`. Evitar `getByTestId` salvo último recurso.

```ts
// apps/web-portal/src/components/LoginForm.spec.tsx
it('muestra error si el documento es inválido', async () => {
  render(<LoginForm onSubmit={jest.fn()} />);
  await userEvent.type(screen.getByLabelText(/documento/i), 'invalid');
  await userEvent.click(screen.getByRole('button', { name: /ingresar/i }));
  expect(await screen.findByRole('alert')).toHaveTextContent(/documento inválido/i);
});
```

### E2E Playwright

- Escenarios de flujo: login → crear solicitud → ver confirmación.
- Tótem: login del pañolero, validación con PIN, materialización.
- Chat del asistente: conversación de ejemplo, creación de borrador.
- Accesibilidad: el flujo debe completarse solo con teclado.

Playwright corre contra un ambiente levantado con `docker compose up`. Los tests se ejecutan serialmente por ambiente; paralelismo dentro del navegador.

---

## 11. CI/CD (referencia)

- **Cada push**: lint, typecheck, unit, integration, contract.
- **PR a `main`**: anterior + e2e por servicio + e2e multi-servicio + e2e UI.
- **Nightly**: anterior + tests largos (property-based con 10k iteraciones, stress suave).

Todos los jobs publican reportes de cobertura, logs, y (cuando aplica) screenshots/videos de Playwright en caso de fallo.

Matriz de CI:

```
lint           →  pnpm lint
typecheck      →  pnpm typecheck
unit           →  pnpm test
integration    →  pnpm test:integration
contract       →  pnpm test:contract
e2e-service    →  pnpm test:e2e --filter=<service>
e2e-full       →  pnpm test:e2e:cross-service
e2e-ui         →  pnpm test:e2e:ui
```

---

## 12. Qué NO hacer

- **No usar `jest.mock()` para mockear puertos**. Usar implementaciones fake. `jest.mock()` está bien para librerías externas muy molestas (casos concretos: librerías que tocan `process` o `fs` al importar).
- **No testear detalles de implementación**. Tests que rompen al refactorar sin cambiar comportamiento son señal de acoplamiento indebido. Testear comportamiento, no estructura interna.
- **No mockear `Date`/`Math.random` con sinon ni timers globales**. Usar puertos `Clock` e `IdGenerator`.
- **No compartir estado entre tests**. `beforeEach` limpia. Cada test se ejecuta en aislamiento.
- **No omitir un test porque "ese caso es obvio"**. Si es obvio, el test se escribe en un minuto y documenta.
- **No meter lógica de negocio en tests**. Si un test tiene `if` sobre el resultado, es señal de que no sabe qué esperar — refactorizar.

---

## 13. Referencias

- `01-hexagonal-architecture.md` — la arquitectura que habilita esta estrategia.
- `00-coding-standards.md` — lint, TypeScript, naming de archivos `.spec.ts`.
- `docs/architecture/03-eventos-dominio.md` — fuente de los schemas Zod usados en contract tests.
- `docs/architecture/08-estados-entidades.md` — las transiciones que los tests de dominio deben cubrir.
- Requerimiento `RNF-MNT.2`: cobertura ≥ 70%.
- Requerimiento `RNF-MNT.3`: cada servicio testeable en aislamiento.
