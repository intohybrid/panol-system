# Arquitectura hexagonal para microservicios

## Propósito

Este documento define **la estructura interna canónica** que debe seguir cada microservicio del Sistema de Pañol. Es la especificación que responde a tres preguntas concretas:

1. ¿Dónde va cada cosa — entidades, reglas, DTOs, Prisma, handlers AMQP, controllers HTTP?
2. ¿Qué puede depender de qué?
3. ¿Cómo se ve, en código, un caso de uso completo de principio a fin?

La motivación del patrón (Ports & Adapters de Alistair Cockburn, también llamado "hexagonal architecture") es aislar las **reglas de negocio** de los **detalles técnicos** — framework, base de datos, transporte. Las reglas no cambian cuando cambia la BD; los adaptadores sí. Es la forma correcta de construir un microservicio event-driven que además usa Prisma, NestJS, AMQP y Postgres sin quedar casado con ninguno.

Aplica a los ocho microservicios de dominio (`auth-svc`, `inventory-svc`, `request-svc`, `loan-svc`, `notification-svc`, `ai-risk-svc`, `ai-assistant-svc`, `api-gateway`) con la misma estructura. `reports-svc` tiene una variante reducida descrita al final (§7).

---

## 1. Las tres capas

Cada microservicio se organiza en tres capas concéntricas. La capa externa depende de la interna; la interna **no** conoce a la externa.

```
┌─────────────────────────────────────────────────────────┐
│  infrastructure/  (adaptadores: HTTP, AMQP, Prisma...)  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  application/  (casos de uso, puertos)            │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │  domain/  (entidades, value objects, reglas)│  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Regla de dependencia (no negociable)

| Desde | Puede importar de |
|---|---|
| `domain/` | **Nada** del servicio. Solo tipos primitivos y otros archivos de `domain/`. |
| `application/` | `domain/`. |
| `infrastructure/` | `application/` y `domain/`. |

**Flechas de import siempre apuntan hacia adentro**. Si necesitas que el dominio sepa de una BD o de un evento, la respuesta es declarar un **puerto** (interfaz) en `application/` y dejar que la infrastructure la implemente.

### Qué no puede estar en cada capa

**`domain/` no puede tener**:
- Decorators de NestJS (`@Injectable`, `@Controller`...).
- Tipos o funciones de Prisma Client.
- Tipos HTTP o AMQP.
- Imports de `@nestjs/*`, `prisma`, `amqplib`, `axios`, etc.
- Llamadas a `process.env` ni a `new Date()` sin abstracción (usa un `Clock` port).
- Llamadas a `console.log` ni a logger.

**`application/` no puede tener**:
- Decorators de NestJS excepto `@Injectable` en los casos de uso (es el mínimo necesario para DI y es un compromiso pragmático aceptado).
- Imports de Prisma, AMQP, HTTP.

**`infrastructure/` es libre** — ahí viven todos los detalles técnicos.

---

## 2. Estructura de carpetas por servicio

```
apps/<service>-svc/
├── src/
│   ├── domain/
│   │   ├── <entity-name>/
│   │   │   ├── <entity>.ts              # la entidad agregada
│   │   │   ├── <entity>.events.ts       # eventos de dominio emitidos por la entidad
│   │   │   └── <vo>.vo.ts               # value objects
│   │   ├── errors/
│   │   │   ├── base.ts                  # DomainError abstracta
│   │   │   └── <specific>-error.ts
│   │   └── services/                    # domain services (lógica entre entidades)
│   │       └── <name>.service.ts
│   │
│   ├── application/
│   │   ├── use-cases/
│   │   │   ├── <command>/
│   │   │   │   ├── <command>.use-case.ts
│   │   │   │   └── <command>.input.ts   # input del caso de uso
│   │   │   └── <query>/
│   │   │       └── <query>.use-case.ts
│   │   └── ports/
│   │       ├── <entity>-repository.port.ts
│   │       ├── event-publisher.port.ts
│   │       ├── clock.port.ts
│   │       └── <other-service>-client.port.ts
│   │
│   ├── infrastructure/
│   │   ├── inbound/                     # adaptadores primarios (driving)
│   │   │   ├── http/
│   │   │   │   ├── <entity>.controller.ts
│   │   │   │   ├── dto/
│   │   │   │   │   └── <command>.dto.ts
│   │   │   │   └── mappers/
│   │   │   │       └── <entity>.http-mapper.ts
│   │   │   └── messaging/
│   │   │       ├── <event>.consumer.ts
│   │   │       └── mappers/
│   │   │           └── <event>.payload-mapper.ts
│   │   │
│   │   ├── outbound/                    # adaptadores secundarios (driven)
│   │   │   ├── persistence/
│   │   │   │   ├── prisma/
│   │   │   │   │   ├── schema.prisma
│   │   │   │   │   └── migrations/
│   │   │   │   ├── <entity>.prisma-mapper.ts
│   │   │   │   └── prisma-<entity>.repository.ts
│   │   │   ├── messaging/
│   │   │   │   ├── amqp-event.publisher.ts
│   │   │   │   └── outbox/
│   │   │   │       ├── outbox-event.prisma.ts
│   │   │   │       └── outbox-relay.service.ts
│   │   │   └── external/
│   │   │       └── <external>-http.client.ts
│   │   │
│   │   └── modules/                     # NestJS modules de composición
│   │       ├── <entity>.module.ts
│   │       └── app.module.ts
│   │
│   ├── config/
│   │   └── env.schema.ts
│   ├── shared/
│   │   └── logger.module.ts
│   ├── main.ts
│   └── bootstrap.ts
│
├── test/
│   ├── unit/                    # domain + application, sin infraestructura real
│   ├── integration/             # infrastructure contra dependencias reales (testcontainers)
│   └── e2e/                     # el servicio completo arriba
│
├── Dockerfile
├── package.json
├── tsconfig.json
└── README.md
```

### Nombramiento

Las convenciones de sufijos están en `00-coding-standards.md` §4. Repite aquí solo lo esencial: `.use-case.ts`, `.port.ts`, `.repository.ts`, `.controller.ts`, `.consumer.ts`, `.event-handler.ts`, `.dto.ts`, `.schema.ts`, `.spec.ts`.

---

## 3. Qué pone cada capa

### 3.1. `domain/`

**Responsabilidad**: modelar el negocio. Contiene las entidades agregadas, sus reglas de invariante (`RC.*`), value objects y eventos de dominio que emiten.

**No conoce**: BD, framework, transporte, logger, clock del sistema.

#### Entidad agregada

Una entidad es una clase con identidad. Sus métodos son operaciones del negocio — no setters anémicos.

```ts
// domain/user/user.ts
import { DocumentoVO } from './documento.vo';
import { UserStatus, USER_STATUS } from './user-status';
import { InvalidUserTransitionError } from '../errors/invalid-user-transition-error';

export class User {
  private constructor(
    public readonly id: string,
    public readonly documento: DocumentoVO,
    public readonly nombres: string,
    public readonly apellidos: string,
    public readonly role: UserRole,
    public readonly carreraId: string | null,
    private _status: UserStatus,
    private readonly _passwordHash: string,
    private _pinHash: string | null,
  ) {}

  static create(input: {
    id: string;
    documento: DocumentoVO;
    nombres: string;
    apellidos: string;
    role: UserRole;
    carreraId: string | null;
    initialPasswordHash: string;
  }): User {
    return new User(
      input.id,
      input.documento,
      input.nombres,
      input.apellidos,
      input.role,
      input.carreraId,
      USER_STATUS.CREADO,
      input.initialPasswordHash,
      null,
    );
  }

  get status(): UserStatus { return this._status; }

  blockForMorosidad(): void {
    if (this._status === USER_STATUS.INACTIVO) {
      throw new InvalidUserTransitionError(this.id, this._status, USER_STATUS.BLOQUEADO_MOROSIDAD);
    }
    this._status = USER_STATUS.BLOQUEADO_MOROSIDAD;
  }

  // ... más métodos de transición según STATE-01-usuario.drawio
}
```

Lo que ves:

- Constructor privado — solo se instancia por factoría (`create`) o por rehidratación desde el repositorio.
- Método `blockForMorosidad` encapsula la regla y lanza error de dominio si la transición es inválida.
- No hay `@Injectable`, no hay `@Column`, no hay Prisma.

#### Value Object

Objetos sin identidad, inmutables, comparables por valor.

```ts
// domain/user/documento.vo.ts
export class DocumentoVO {
  private constructor(
    public readonly tipo: 'RUT' | 'DNI' | 'PASAPORTE',
    public readonly valor: string,
  ) {}

  static create(tipo: DocumentoVO['tipo'], valor: string): DocumentoVO {
    const normalized = DocumentoVO.normalize(tipo, valor);
    DocumentoVO.validate(tipo, normalized);
    return new DocumentoVO(tipo, normalized);
  }

  equals(other: DocumentoVO): boolean {
    return this.tipo === other.tipo && this.valor === other.valor;
  }

  private static normalize(tipo: DocumentoVO['tipo'], valor: string): string { ... }
  private static validate(tipo: DocumentoVO['tipo'], valor: string): void { ... }
}
```

#### Eventos de dominio

Un evento de dominio es lo que la entidad "anuncia" cuando cambia de estado. Se devuelve como parte del resultado del método, no se publica directamente:

```ts
// domain/user/user.events.ts
export class UserBlockedDomainEvent {
  constructor(
    public readonly userId: string,
    public readonly reason: 'MOROSIDAD_AUTOMATICA' | 'ADMINISTRATIVO',
    public readonly motivo: string | null,
    public readonly occurredAt: Date,
  ) {}
}
```

El caso de uso (capa application) es quien toma estos eventos y los pasa al outbox. El dominio solo los crea.

#### Errores de dominio

Ver `00-coding-standards.md` §6. Jerarquía obligatoria con `code` y `httpStatus`.

### 3.2. `application/`

**Responsabilidad**: orquestar casos de uso. Coordina operaciones sobre el dominio usando puertos. Declara las interfaces que la infrastructure implementa.

#### Puertos

Un puerto es una **interfaz TypeScript**. No sabe nada de implementación.

```ts
// application/ports/user-repository.port.ts
import { User } from '../../domain/user/user';
import { DocumentoVO } from '../../domain/user/documento.vo';

export interface UserRepository {
  findById(id: string): Promise<User | null>;
  findByDocumento(documento: DocumentoVO): Promise<User | null>;
  save(user: User): Promise<void>;
}

export const USER_REPOSITORY = Symbol('UserRepository');
```

El `Symbol` sirve como token de inyección en NestJS (ver §4). La interfaz no tiene decorators.

```ts
// application/ports/event-publisher.port.ts
export interface EventPublisher {
  /**
   * Persiste el evento en outbox dentro de la transacción actual.
   * El relay publica luego al broker.
   */
  publishInOutbox(event: DomainEventEnvelope): Promise<void>;
}

export const EVENT_PUBLISHER = Symbol('EventPublisher');
```

```ts
// application/ports/clock.port.ts
export interface Clock {
  now(): Date;
}
export const CLOCK = Symbol('Clock');
```

#### Casos de uso

Un caso de uso = una clase con un método público `execute`. Recibe un input, devuelve un output, coordina el flujo. Es la única capa que sabe qué puertos usar.

```ts
// application/use-cases/create-user/create-user.use-case.ts
import { Inject, Injectable } from '@nestjs/common';
import { randomUUID } from 'node:crypto';
import { User } from '../../../domain/user/user';
import { DocumentoVO } from '../../../domain/user/documento.vo';
import { UserRepository, USER_REPOSITORY } from '../../ports/user-repository.port';
import { EventPublisher, EVENT_PUBLISHER } from '../../ports/event-publisher.port';
import { Clock, CLOCK } from '../../ports/clock.port';
import { PasswordHasher, PASSWORD_HASHER } from '../../ports/password-hasher.port';
import { DuplicateDocumentoError } from '../../../domain/errors/duplicate-documento-error';

export interface CreateUserInput {
  documentoTipo: 'RUT' | 'DNI' | 'PASAPORTE';
  documentoValor: string;
  nombres: string;
  apellidos: string;
  role: UserRole;
  carreraId: string | null;
  createdBy: string;
}

@Injectable()
export class CreateUserUseCase {
  constructor(
    @Inject(USER_REPOSITORY) private readonly users: UserRepository,
    @Inject(EVENT_PUBLISHER) private readonly events: EventPublisher,
    @Inject(CLOCK) private readonly clock: Clock,
    @Inject(PASSWORD_HASHER) private readonly hasher: PasswordHasher,
  ) {}

  async execute(input: CreateUserInput): Promise<{ userId: string }> {
    const documento = DocumentoVO.create(input.documentoTipo, input.documentoValor);

    const existing = await this.users.findByDocumento(documento);
    if (existing) throw new DuplicateDocumentoError(documento);

    const initialPasswordHash = await this.hasher.hash(
      `${documento.valor}${process.env.SCHOOL_PASSWORD_SUFFIX}`, // placeholder; en la práctica viene por ConfigService
    );

    const user = User.create({
      id: randomUUID(),
      documento,
      nombres: input.nombres,
      apellidos: input.apellidos,
      role: input.role,
      carreraId: input.carreraId,
      initialPasswordHash,
    });

    await this.users.save(user);
    await this.events.publishInOutbox({
      eventType: 'user.created',
      aggregateId: user.id,
      schemaVersion: '1.0',
      occurredAt: this.clock.now(),
      payload: {
        userId: user.id,
        role: user.role,
        documento: documento.valor,
        carreraId: user.carreraId,
        createdBy: input.createdBy,
        createdAt: this.clock.now().toISOString(),
      },
    });

    return { userId: user.id };
  }
}
```

Lo que ves:

- Un solo `@Injectable` (compromiso pragmático).
- Inyección por `Symbol` (no por nombre de clase). Permite que la implementación Prisma se sustituya por un fake en tests sin tocar esta clase.
- Todas las dependencias son **puertos**, nunca implementaciones.
- La lógica de negocio (transiciones de estado, validación de documento) vive en la entidad. El caso de uso es el director de orquesta, no el músico.

### 3.3. `infrastructure/`

**Responsabilidad**: implementar los puertos y conectar con el mundo externo. Aquí sí hay decorators, Prisma, AMQP, HTTP, Nest.

#### Adaptadores primarios (inbound, `inbound/`)

Son quienes **invocan** al caso de uso. Vienen del mundo exterior (usuario HTTP, mensaje AMQP).

**HTTP controller**:

```ts
// infrastructure/inbound/http/user.controller.ts
import { Body, Controller, Inject, Post } from '@nestjs/common';
import { ApiTags } from '@nestjs/swagger';
import { CreateUserUseCase } from '../../../application/use-cases/create-user/create-user.use-case';
import { CreateUserDto } from './dto/create-user.dto';

@ApiTags('users')
@Controller('users')
export class UserController {
  constructor(private readonly createUser: CreateUserUseCase) {}

  @Post()
  async create(@Body() dto: CreateUserDto): Promise<{ userId: string }> {
    return this.createUser.execute({
      documentoTipo: dto.documentoTipo,
      documentoValor: dto.documentoValor,
      nombres: dto.nombres,
      apellidos: dto.apellidos,
      role: dto.role,
      carreraId: dto.carreraId,
      createdBy: dto.createdBy,
    });
  }
}
```

El controller es **delgado**: recibe DTO, llama al caso de uso, devuelve resultado. Sin lógica.

**DTO con validación** (class-validator):

```ts
// infrastructure/inbound/http/dto/create-user.dto.ts
import { IsEnum, IsOptional, IsString, IsUUID, Length } from 'class-validator';

export class CreateUserDto {
  @IsEnum(['RUT', 'DNI', 'PASAPORTE'])
  documentoTipo!: 'RUT' | 'DNI' | 'PASAPORTE';

  @IsString()
  @Length(1, 20)
  documentoValor!: string;

  @IsString()
  @Length(1, 100)
  nombres!: string;

  @IsString()
  @Length(1, 100)
  apellidos!: string;

  @IsEnum(['JEFE', 'COORDINADOR', 'PANOLERO', 'DOCENTE', 'ALUMNO'])
  role!: UserRole;

  @IsOptional()
  @IsUUID()
  carreraId!: string | null;

  @IsUUID()
  createdBy!: string;
}
```

**AMQP consumer**:

```ts
// infrastructure/inbound/messaging/loan-overdue.consumer.ts
import { Controller } from '@nestjs/common';
import { EventPattern, Payload, Ctx, RmqContext } from '@nestjs/microservices';
import { LoanOverdueEventSchema } from '@libs/events/loan';
import { EvaluateMorosidadUseCase } from '../../../application/use-cases/evaluate-morosidad/evaluate-morosidad.use-case';

@Controller()
export class LoanOverdueConsumer {
  constructor(private readonly evaluate: EvaluateMorosidadUseCase) {}

  @EventPattern('loan.overdue')
  async handle(@Payload() rawPayload: unknown, @Ctx() ctx: RmqContext) {
    const payload = LoanOverdueEventSchema.parse(rawPayload);
    const channel = ctx.getChannelRef();
    const message = ctx.getMessage();

    try {
      await this.evaluate.execute({
        userId: payload.usuarioId,
        loanId: payload.loanId,
        diasAtraso: payload.diasAtraso,
      });
      channel.ack(message);
    } catch (err) {
      // estrategia de retry/DLX documentada en 04-eip-catalog.md §4
      this.handleFailure(err, channel, message);
    }
  }
}
```

El consumer **valida con Zod al borde** y delega al caso de uso. Nunca toca BD ni dominio directamente.

#### Adaptadores secundarios (outbound, `outbound/`)

Implementan los puertos.

**Repositorio Prisma**:

```ts
// infrastructure/outbound/persistence/prisma-user.repository.ts
import { Injectable } from '@nestjs/common';
import { PrismaService } from './prisma.service';
import { UserRepository } from '../../../application/ports/user-repository.port';
import { User } from '../../../domain/user/user';
import { DocumentoVO } from '../../../domain/user/documento.vo';
import { UserPrismaMapper } from './user.prisma-mapper';

@Injectable()
export class PrismaUserRepository implements UserRepository {
  constructor(private readonly prisma: PrismaService) {}

  async findById(id: string): Promise<User | null> {
    const row = await this.prisma.user.findUnique({ where: { id } });
    return row ? UserPrismaMapper.toDomain(row) : null;
  }

  async findByDocumento(documento: DocumentoVO): Promise<User | null> {
    const row = await this.prisma.user.findUnique({
      where: {
        documentoTipo_documentoValor: {
          documentoTipo: documento.tipo,
          documentoValor: documento.valor,
        },
      },
    });
    return row ? UserPrismaMapper.toDomain(row) : null;
  }

  async save(user: User): Promise<void> {
    const data = UserPrismaMapper.toPersistence(user);
    await this.prisma.user.upsert({
      where: { id: user.id },
      create: data,
      update: data,
    });
  }
}
```

Nota: **el mapper** `UserPrismaMapper` es crítico. Su trabajo es traducir entre el modelo de dominio (`User` con métodos) y la fila de Prisma (objeto plano). Vive en `outbound/persistence/`.

**Event publisher con outbox**:

```ts
// infrastructure/outbound/messaging/outbox/outbox-event.publisher.ts
import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../persistence/prisma.service';
import { EventPublisher } from '../../../../application/ports/event-publisher.port';
import { DomainEventEnvelope } from '../../../../application/ports/event-publisher.port';

@Injectable()
export class OutboxEventPublisher implements EventPublisher {
  constructor(private readonly prisma: PrismaService) {}

  async publishInOutbox(event: DomainEventEnvelope): Promise<void> {
    await this.prisma.outboxEvent.create({
      data: {
        id: randomUUID(),
        aggregateId: event.aggregateId,
        eventType: event.eventType,
        schemaVersion: event.schemaVersion,
        payload: event.payload,
        headers: event.headers ?? {},
        status: 'PENDING',
        createdAt: event.occurredAt,
      },
    });
  }
}
```

El outbox se escribe **dentro de la misma transacción** que la persistencia del agregado. Esto se logra con una Unit of Work compartida (ver §5).

**Relay de outbox** (publica al broker):

```ts
// infrastructure/outbound/messaging/outbox/outbox-relay.service.ts
import { Injectable } from '@nestjs/common';
import { Interval } from '@nestjs/schedule';
import { PrismaService } from '../../persistence/prisma.service';
import { AmqpPublisher } from '../amqp.publisher';

@Injectable()
export class OutboxRelayService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly amqp: AmqpPublisher,
  ) {}

  @Interval(500)
  async publishPending() {
    const pending = await this.prisma.outboxEvent.findMany({
      where: { status: 'PENDING' },
      take: 50,
      orderBy: { createdAt: 'asc' },
    });

    for (const evt of pending) {
      try {
        await this.amqp.publish('domain.events', evt.eventType, evt.payload, evt.headers);
        await this.prisma.outboxEvent.update({
          where: { id: evt.id },
          data: { status: 'PUBLISHED', publishedAt: new Date() },
        });
      } catch (err) {
        // log, quedará pendiente para siguiente iteración
      }
    }
  }
}
```

#### Módulos NestJS

Los módulos son **puramente de composición** — no contienen lógica. Conectan puertos con adaptadores vía DI.

```ts
// infrastructure/modules/user.module.ts
import { Module } from '@nestjs/common';
import { UserController } from '../inbound/http/user.controller';
import { LoanOverdueConsumer } from '../inbound/messaging/loan-overdue.consumer';
import { CreateUserUseCase } from '../../application/use-cases/create-user/create-user.use-case';
import { EvaluateMorosidadUseCase } from '../../application/use-cases/evaluate-morosidad/evaluate-morosidad.use-case';
import { USER_REPOSITORY } from '../../application/ports/user-repository.port';
import { EVENT_PUBLISHER } from '../../application/ports/event-publisher.port';
import { CLOCK } from '../../application/ports/clock.port';
import { PrismaUserRepository } from '../outbound/persistence/prisma-user.repository';
import { OutboxEventPublisher } from '../outbound/messaging/outbox/outbox-event.publisher';
import { SystemClock } from '../outbound/clock/system-clock';
import { PersistenceModule } from './persistence.module';

@Module({
  imports: [PersistenceModule],
  controllers: [UserController, LoanOverdueConsumer],
  providers: [
    CreateUserUseCase,
    EvaluateMorosidadUseCase,
    { provide: USER_REPOSITORY, useClass: PrismaUserRepository },
    { provide: EVENT_PUBLISHER, useClass: OutboxEventPublisher },
    { provide: CLOCK, useClass: SystemClock },
  ],
})
export class UserModule {}
```

El truco de `{ provide: SYMBOL, useClass: Impl }` es lo que permite al caso de uso inyectar por token sin conocer la clase concreta. En tests, se usa `{ provide: USER_REPOSITORY, useValue: fakeRepo }`.

---

## 4. Tabla: qué capa importa qué

| De (archivo) | Puede importar de |
|---|---|
| `domain/user/user.ts` | Otros archivos de `domain/` dentro del mismo servicio. Tipos de Node (`node:crypto`) sin efectos secundarios. |
| `domain/errors/*.ts` | Tipos primitivos. Otros errores de `domain/`. |
| `application/ports/*.port.ts` | Solo `domain/`. |
| `application/use-cases/*.use-case.ts` | `domain/`, `application/ports/`. Y `@nestjs/common` para `@Injectable`/`@Inject`. |
| `infrastructure/inbound/http/*.controller.ts` | `application/use-cases/`, `infrastructure/inbound/http/dto/`. Nest. |
| `infrastructure/inbound/messaging/*.consumer.ts` | `application/use-cases/`, `@libs/events`. Nest. |
| `infrastructure/outbound/persistence/*.repository.ts` | `application/ports/`, `domain/`, mappers locales. Prisma. |
| `infrastructure/outbound/messaging/*.ts` | `application/ports/`. AMQP lib. |
| `infrastructure/modules/*.module.ts` | Todo lo anterior. Nest. |

**Prohibido**: que un archivo de `domain/` o `application/` importe algo de `infrastructure/`. ESLint enforzado con `eslint-plugin-boundaries` o reglas `import/no-restricted-paths`.

Ejemplo de regla de import en `.eslintrc`:

```jsonc
"import/no-restricted-paths": ["error", {
  "zones": [
    { "target": "./src/domain", "from": "./src/application" },
    { "target": "./src/domain", "from": "./src/infrastructure" },
    { "target": "./src/application", "from": "./src/infrastructure" }
  ]
}]
```

---

## 5. Unit of Work y transacciones

### Problema

El caso de uso `CreateUser` necesita hacer dos cosas atómicamente:

1. Persistir el `User` en `users`.
2. Insertar el evento `user.created` en `outbox_events`.

Si solo se persiste una, el sistema queda inconsistente (usuario sin evento, o evento sin usuario). La forma de evitarlo es usar una **única transacción Prisma** que abarque ambas escrituras.

### Solución

`PrismaService` expone un método `withTransaction`. El caso de uso lo usa envolviendo su lógica:

```ts
// application/ports/unit-of-work.port.ts
export interface UnitOfWork {
  run<T>(work: () => Promise<T>): Promise<T>;
}
export const UNIT_OF_WORK = Symbol('UnitOfWork');
```

Implementación Prisma:

```ts
// infrastructure/outbound/persistence/prisma-unit-of-work.ts
@Injectable()
export class PrismaUnitOfWork implements UnitOfWork {
  constructor(private readonly prisma: PrismaService) {}

  run<T>(work: () => Promise<T>): Promise<T> {
    return this.prisma.$transaction(async (tx) => {
      // AsyncLocalStorage para que los repos vean la tx activa
      return TransactionContext.run(tx, work);
    });
  }
}
```

El `CreateUserUseCase` real queda:

```ts
async execute(input: CreateUserInput): Promise<{ userId: string }> {
  return this.uow.run(async () => {
    // ... lógica ...
    await this.users.save(user);
    await this.events.publishInOutbox(event);
    return { userId: user.id };
  });
}
```

Los repositorios leen el `tx` del `TransactionContext` (AsyncLocalStorage) si existe; si no, usan el cliente base. Esto mantiene los casos de uso simples sin pasar `tx` explícitamente.

Si te resulta demasiado complejo implementar el `TransactionContext`, una alternativa aceptable para el MVP es pasar el `tx` explícitamente como argumento. Decisión pragmática del equipo; cualquiera de las dos formas se acepta si está documentada.

---

## 6. Reglas adicionales

### Tiempo no se lee de `new Date()` en dominio ni casos de uso

Usa el puerto `Clock`. Razón: los tests de dominio y casos de uso deben ser deterministas, y eso requiere poder congelar el tiempo.

### IDs no se generan con `randomUUID()` en dominio

Genera el ID en el caso de uso o recibe un ID como input. El dominio asume que el ID le llega. Razón: mismo argumento del Clock — tests determinísticos.

En el ejemplo de `CreateUserUseCase` se usa `randomUUID()` directamente como pragmatismo; si el servicio requiere más estricto, se agrega un puerto `IdGenerator`.

### No hay estado compartido entre requests

NestJS instancia providers como singletons por defecto. Está bien para stateless services. Cualquier estado mutable debe vivir en BD o en cache explícito, no en una propiedad de clase.

### El dominio nunca lanza errores HTTP

Lanza `DomainError`. El controller o un `ExceptionFilter` global lo mapea a HTTP. Si el dominio lanza `BadRequestException`, es bug.

### Eventos externos (los que vienen del broker) se validan con Zod antes de entrar al caso de uso

Visto en el consumer. Regla de oro: los tipos del dominio son la fuente de verdad del comportamiento; Zod es la fuente de verdad del intercambio.

---

## 7. Variante para `reports-svc`

`reports-svc` es un read-model puro (ADR-015). No tiene entidades con comportamiento de negocio; tiene **proyecciones** — tablas desnormalizadas que se actualizan al consumir eventos.

### Estructura reducida

```
apps/reports-svc/
├── src/
│   ├── projections/
│   │   ├── user-projection/
│   │   │   ├── user.projection.ts         # shape de la tabla proyeccion_usuarios
│   │   │   └── user-projection.handler.ts # consume user.*, updatea la tabla
│   │   ├── stock-projection/
│   │   ├── solicitudes-projection/
│   │   └── ...
│   ├── queries/
│   │   ├── stock-disponible/
│   │   │   └── stock-disponible.query.ts
│   │   └── ...
│   ├── infrastructure/
│   │   ├── inbound/
│   │   │   ├── http/            # endpoints de lectura
│   │   │   └── messaging/       # consumers que alimentan projections
│   │   └── outbound/
│   │       └── persistence/     # Prisma read-model
│   └── main.ts
└── ...
```

### Diferencias

- **No hay `domain/`**. No hay reglas de negocio. Las proyecciones son datos; los queries son lecturas.
- **No hay `application/use-cases/`**. En su lugar: `queries/` para lecturas y `projections/` para actualizaciones. Cada una es una clase simple con un método.
- **No hay outbox**. `reports-svc` solo consume, no publica eventos de dominio.
- **Sí hay idempotencia**: tabla `processed_events` igual que los demás.
- Los handlers de proyección hacen `upsert` directo a la tabla desnormalizada — no pasan por una capa de dominio.

Ejemplo de projection handler:

```ts
// projections/user-projection/user-projection.handler.ts
@Controller()
export class UserProjectionHandler {
  constructor(private readonly prisma: PrismaService) {}

  @EventPattern('user.created')
  async onCreated(@Payload() raw: unknown, @Ctx() ctx: RmqContext) {
    const payload = UserCreatedEventSchema.parse(raw);
    await this.prisma.proyeccionUsuarios.upsert({
      where: { userId: payload.userId },
      create: {
        userId: payload.userId,
        documento: payload.documento,
        role: payload.role,
        carreraId: payload.carreraId,
        activo: true,
      },
      update: { activo: true },
    });
    ctx.getChannelRef().ack(ctx.getMessage());
  }

  @EventPattern('user.blocked')
  async onBlocked(@Payload() raw: unknown, @Ctx() ctx: RmqContext) {
    const payload = UserBlockedEventSchema.parse(raw);
    await this.prisma.proyeccionUsuarios.update({
      where: { userId: payload.userId },
      data: { activo: false, estado: 'BLOQUEADO' },
    });
    ctx.getChannelRef().ack(ctx.getMessage());
  }
}
```

Simple, directo. No hay entidad `UserProjection` con métodos — es solo una tabla y un handler. Este es el trade-off correcto para CQRS lado de lectura.

---

## 8. Checklist para crear un microservicio nuevo

Cuando se crea un servicio (o se revisa uno existente), verificar:

- [ ] Estructura de carpetas coincide con §2.
- [ ] Regla de dependencia enforzada por ESLint (`import/no-restricted-paths`).
- [ ] Cada entidad agregada tiene su propio directorio en `domain/<entity>/`.
- [ ] Puertos declarados como interfaces TypeScript con `Symbol` token en `application/ports/`.
- [ ] Casos de uso con un solo método público `execute`.
- [ ] HTTP controllers delgados: DTO → use case → respuesta.
- [ ] AMQP consumers validan con Zod antes de invocar el caso de uso.
- [ ] Prisma repositories implementan el puerto del dominio, con mappers explícitos.
- [ ] Outbox pattern implementado con relay programado.
- [ ] Idempotent receiver implementado en consumers (tabla `processed_events`).
- [ ] `Clock` y `IdGenerator` como puertos, no `new Date()` ni `randomUUID()` en dominio.
- [ ] Config validada con Zod al arrancar (ver coding-standards §7).
- [ ] Tests unitarios de dominio sin NestJS, sin Prisma (§ 9).
- [ ] Tests de casos de uso con puertos fake.
- [ ] Tests de infraestructura con Testcontainers.
- [ ] Dockerfile multi-stage (build → runtime) definido.

---

## 9. Relación con testing

La testabilidad es la razón por la que la estructura es así. Ver `02-testing-strategy.md` para los detalles, pero la regla corta:

- **`domain/`** se testea con Jest puro, sin Nest, sin ninguna dep.
- **`application/`** se testea pasando implementaciones fake de los puertos.
- **`infrastructure/`** se testea con Testcontainers (Postgres, RabbitMQ reales).
- **`e2e/`** arranca el servicio completo vía Nest + compose y prueba end-to-end.

Si un test de dominio requiere mocks de Prisma, la arquitectura está rota: algún detalle se filtró al core.

---

## 10. Referencias

- Alistair Cockburn — "Hexagonal Architecture" (2005).
- Vaughn Vernon — "Implementing Domain-Driven Design" (2013).
- Herberto Graça — "DDD, Hexagonal, Onion, Clean, CQRS, how I put it all together" (blog post, 2017).
- ADR-003 (NestJS), ADR-015 (reports-svc CQRS).
- `docs/architecture/07-microservicios-responsabilidades.md` — qué hace cada servicio.
- `docs/architecture/08-estados-entidades.md` — máquinas de estado a implementar en `domain/`.
- `00-coding-standards.md` — convenciones transversales.
- `02-testing-strategy.md` — cómo probar cada capa.
