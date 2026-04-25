# Estándares de código

## Propósito

Este documento define las convenciones técnicas transversales para todo el código del Sistema de Pañol — backend (9 microservicios NestJS), frontends (Next.js, Vite+React), scripts y tests. Es la fuente de verdad referenciada desde `CLAUDE.md` y desde los ADRs (ver `RNF-MNT.1`). El objetivo es que cualquier persona del equipo pueda abrir cualquier archivo y encontrar el mismo estilo, la misma forma de validar entrada, la misma forma de loguear, la misma forma de configurar.

Documentos complementarios:
- `01-hexagonal-architecture.md` — cómo se estructura internamente cada microservicio.
- `02-testing-strategy.md` — cómo se prueba.

---

## 1. Entorno y tooling

### Runtime y package manager

| Herramienta | Versión | Por qué |
|---|---|---|
| Node.js | 20 LTS | LTS vigente durante la vida del proyecto; stable APIs. |
| pnpm | ≥ 9.x | Monorepo workspaces rápidos, cache compartido (ver ADR-001). |
| Turborepo | ≥ 2.x | Cache de build y task graph entre apps y libs. |
| TypeScript | 5.x | Strict mode obligatorio. |

**Fijación de versiones**: el `package.json` raíz declara `"engines": { "node": ">=20.10.0 <21", "pnpm": ">=9" }`. Las dependencias se instalan con versiones exactas o rangos `^` conservadores — no `*` ni `latest`.

### Scripts raíz del monorepo

Convención: todos los comandos comunes corren desde la raíz via Turbo. Cada app/lib define los mismos scripts locales (`build`, `lint`, `typecheck`, `test`, `dev`).

```
pnpm install          # instala todo
pnpm build            # construye todos los paquetes en orden de deps
pnpm lint             # ESLint todo
pnpm typecheck        # tsc --noEmit todo
pnpm test             # unit + integration
pnpm test:e2e         # end-to-end (requiere docker compose up)
pnpm dev              # levanta todo en modo watch
```

---

## 2. TypeScript

### Config base

`tsconfig.base.json` en la raíz define la configuración estricta compartida. Cada app/lib extiende desde ahí con su propio `tsconfig.json` que solo ajusta `outDir`, `rootDir` y referencias.

Flags obligatorios en el base:

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noImplicitAny": true,
    "noImplicitReturns": true,
    "noImplicitOverride": true,
    "noUncheckedIndexedAccess": true,
    "noFallthroughCasesInSwitch": true,
    "exactOptionalPropertyTypes": true,
    "forceConsistentCasingInFileNames": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "isolatedModules": true,
    "resolveJsonModule": true,
    "declaration": true,
    "sourceMap": true,
    "removeComments": false
  }
}
```

Los frontends (`next.js`, `vite`) usan `target` y `module` distintos (`ES2022` + `ESNext`), pero preservan todos los flags estrictos.

### Política sobre `any`

**Prohibido** en código de dominio y aplicación. Permitido únicamente en adaptadores que integran con librerías externas sin tipos, y **siempre con comentario que lo justifique**:

```ts
// eslint-disable-next-line @typescript-eslint/no-explicit-any
// SDK sin tipos, envolvemos inmediatamente en tipo nuestro
const raw = (externalSdk as any).rawCall(...);
```

Si el tipo se puede derivar con `unknown` + narrowing, siempre se prefiere `unknown`.

### Inference vs anotación

- Tipar explícitamente los **bordes**: argumentos de funciones públicas, retornos de funciones exportadas, props de componentes, schemas Zod.
- Dejar que TypeScript infiera **variables locales**.
- Evitar tipos "obvios" repetidos: `const n: number = 1` → `const n = 1`.

### Tipos utilitarios

- Usar `Readonly<>`, `ReadonlyArray<>` en APIs que no deben mutarse.
- Preferir tipos discriminados (tagged unions) para estados.
- Evitar `enum` de TypeScript (son raros al compilar); preferir `as const` + `type Foo = typeof FOO[keyof typeof FOO]`.

Ejemplo canónico:

```ts
export const USER_STATUS = {
  CREADO: 'CREADO',
  PENDIENTE_CAMBIO_CLAVE: 'PENDIENTE_CAMBIO_CLAVE',
  ACTIVO: 'ACTIVO',
  BLOQUEADO_MOROSIDAD: 'BLOQUEADO_MOROSIDAD',
  BLOQUEADO_ADMINISTRATIVO: 'BLOQUEADO_ADMINISTRATIVO',
  INACTIVO: 'INACTIVO',
} as const;

export type UserStatus = typeof USER_STATUS[keyof typeof USER_STATUS];
```

---

## 3. Linting y formateo

### ESLint

Un `eslint.config.js` raíz con configuración flat. Reglas clave:

- `@typescript-eslint/recommended-type-checked`
- `@typescript-eslint/no-explicit-any: error`
- `@typescript-eslint/no-floating-promises: error`
- `@typescript-eslint/no-misused-promises: error`
- `@typescript-eslint/consistent-type-imports: error` (usa `import type`)
- `import/order` con grupos: node builtin → externos → internos de lib → locales
- `no-console: error` en todo el backend. Logging solo por Pino.
- `unicorn/prefer-node-protocol: error` (`node:fs` no `fs`)

Cada frontend agrega sus plugins (`eslint-plugin-react`, `eslint-plugin-jsx-a11y`).

### Prettier

Un `.prettierrc` raíz, sin excepciones por app:

```jsonc
{
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

### Pre-commit

`husky` + `lint-staged` en la raíz:

- Corre ESLint y Prettier sobre los archivos staged.
- Corre `pnpm typecheck` si hay cambios en `.ts`/`.tsx`.
- **No corre tests en pre-commit** para no castigar al desarrollador; eso es trabajo de CI.

---

## 4. Naming conventions

### Archivos y carpetas

- **Kebab-case** para archivos: `create-user.use-case.ts`, `prisma-user.repository.ts`.
- **Kebab-case** para carpetas: `application/use-cases/`, `infrastructure/outbound/persistence/`.
- Excepción: archivos que son componentes React o clases "externalizadas" usan PascalCase si el ecosistema lo espera: `UserCard.tsx`, `AppModule.ts`. En NestJS, el convenio es `kebab` para archivos y clases PascalCase internas — seguimos el convenio del framework.

### Sufijos canónicos por tipo

| Tipo | Sufijo | Ejemplo |
|---|---|---|
| Entidad de dominio | ninguno | `user.ts` exporta `class User` |
| Value Object | `.vo.ts` | `documento.vo.ts` |
| Caso de uso | `.use-case.ts` | `create-user.use-case.ts` |
| Puerto (interfaz) | `.port.ts` | `user-repository.port.ts` |
| Adaptador | según tecnología | `prisma-user.repository.ts`, `amqp-event.publisher.ts` |
| DTO entrante | `.dto.ts` | `create-user.dto.ts` |
| Schema Zod | `.schema.ts` | `user-created-event.schema.ts` |
| Controlador HTTP | `.controller.ts` | `user.controller.ts` |
| Event handler AMQP | `.event-handler.ts` o `.consumer.ts` | `loan-overdue.consumer.ts` |
| Módulo NestJS | `.module.ts` | `user.module.ts` |
| Test unit | `.spec.ts` | `create-user.use-case.spec.ts` |
| Test e2e | `.e2e-spec.ts` | `create-user.e2e-spec.ts` |

### Símbolos TypeScript

- **Clases**: PascalCase. `User`, `CreateUserUseCase`, `PrismaUserRepository`.
- **Interfaces y types**: PascalCase sin prefijo `I`. `UserRepository`, no `IUserRepository`.
- **Funciones y variables**: camelCase. `createUser`, `isBlocked`.
- **Constantes globales**: SCREAMING_SNAKE_CASE. `DEFAULT_TTL_MINUTES`.
- **Acrónimos**: primera letra mayúscula, resto minúscula en medio de palabra. `HttpClient`, no `HTTPClient`. `UserId`, no `UserID`.
- **Tipos de eventos**: PascalCase. `UserCreatedEvent` (el schema; su routing key sigue siendo `user.created`).

---

## 5. Validación en bordes

Regla: **toda entrada del exterior se valida en el borde**, nunca en el dominio. El dominio asume sus entradas ya válidas.

### Backend (NestJS)

- **HTTP**: DTO con `class-validator` + `class-transformer`, activado con `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true })` en `main.ts`.
- **AMQP eventos**: Zod schema por evento en `libs/events/`. El consumer valida con `schema.parse(payload)` antes de invocar el caso de uso. Si falla, `nack(requeue=false)` → va a DLX.
- **Variables de entorno**: Zod schema en `libs/shared/config/env.schema.ts`. Se valida al arrancar (ver §7).

### Frontend

- Formularios con `react-hook-form` + `zodResolver`.
- Respuestas del API se declaran con el mismo Zod schema que publica el backend (compartido vía `libs/shared-types/` o generado con OpenAPI).

### Regla de oro

Un valor que cruzó el borde y pasó la validación **nunca se vuelve a validar** en capas internas. Si una capa desconfía de su entrada, es que la API está mal diseñada.

---

## 6. Manejo de errores

### Jerarquía de errores de dominio

Cada servicio define su propia jerarquía en `domain/errors/`:

```ts
// domain/errors/base.ts
export abstract class DomainError extends Error {
  abstract readonly code: string;
  abstract readonly httpStatus: number;
}

// domain/errors/user-not-found.ts
export class UserNotFoundError extends DomainError {
  readonly code = 'USER_NOT_FOUND';
  readonly httpStatus = 404;
  constructor(public readonly userId: string) {
    super(`User ${userId} not found`);
  }
}
```

### Conversión en adaptadores

Los adaptadores inbound (HTTP, AMQP) convierten errores de dominio al protocolo correspondiente mediante un `ExceptionFilter` global:

- `DomainError` → respuesta HTTP con el `httpStatus` del error, payload `{ code, message, details }`.
- Error inesperado → `500`, log con stack, respuesta genérica sin detalles.
- Error de validación → `400` con detalle de los campos inválidos.

El dominio **nunca** lanza `HttpException` ni errores específicos de NestJS.

### Errores fatales

- Falla de conexión al broker al arrancar: `process.exit(1)`. Kubernetes/Compose reinicia.
- Falla de conexión a BD al arrancar: igual.
- Error en runtime: log + responder 5xx, **no crashear**. Health check baja si hay demasiados 5xx seguidos.

### Async obligatoriamente manejado

`@typescript-eslint/no-floating-promises` y `no-misused-promises` forzados en ESLint. Toda promesa se `await`-ea o se `.catch()`-ea explícitamente. Sin promesas huérfanas.

---

## 7. Configuración

### Fuente única: variables de entorno

Cada servicio carga `.env` en desarrollo (vía `docker-compose`). En producción las variables vienen del orquestador. No hay archivos de config por ambiente — solo variables.

### Validación al arrancar

Cada servicio tiene `src/config/env.schema.ts`:

```ts
import { z } from 'zod';

export const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']),
  PORT: z.coerce.number().int().positive(),
  DATABASE_URL: z.string().url(),
  RABBITMQ_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
});

export type Env = z.infer<typeof envSchema>;

export function loadEnv(): Env {
  const parsed = envSchema.safeParse(process.env);
  if (!parsed.success) {
    console.error('❌ Invalid env:', parsed.error.format());
    process.exit(1);
  }
  return parsed.data;
}
```

El servicio lee la config UNA vez al arrancar y la inyecta como `ConfigService` de Nest. El dominio no conoce `process.env` — recibe valores tipados como argumento.

### Secretos

- `JWT_SECRET`, contraseñas de DB, API keys: **nunca** en el repo.
- `.env.example` con placeholders se commitea. `.env` está en `.gitignore`.
- En producción: secrets manager del cloud correspondiente (fuera del alcance MVP; se declara en ADR-009 como roadmap).

### Configuración por Escuela

Parámetros operativos (`RS-JC.5`: TTL de reserva, umbrales de stock, umbral de scoring, sufijo de clave inicial, días máximos de Especial) **no son variables de entorno**. Viven en la BD de `auth-svc` (tabla `school_config`) y se leen con cache de 60 s. Razón: debe poder cambiarse sin redeploy por el Jefe.

---

## 8. Logging

### Librería

**Pino** en todos los servicios backend. Un `LoggerModule` común en `libs/infra-nestjs/` lo expone como `PinoLogger` inyectable.

### Formato

Logs **siempre JSON estructurado**, nunca texto plano. Campos mínimos:

```json
{
  "level": "info",
  "time": "2026-04-25T10:14:32.123Z",
  "service": "auth-svc",
  "traceId": "a1b2c3d4...",
  "userId": "uuid",
  "msg": "User created",
  "context": { "documento": "12345678-9" }
}
```

### Niveles

- `debug`: detalle de flujo para desarrollo. No se emite en producción.
- `info`: eventos de negocio relevantes (usuario creado, préstamo emitido).
- `warn`: situaciones recuperables (timeout de scoring → fallback).
- `error`: errores inesperados o transiciones a estados inválidos.
- `fatal`: solo antes de `process.exit`.

### Datos sensibles

- **Nunca** loguear: contraseñas, hashes, tokens JWT completos, PIN, payloads completos de usuarios con PII.
- Logger redactor configurado en `libs/infra-nestjs/` para campos `password`, `passwordHash`, `pinHash`, `token`, `authorization`, `cookie`.

### Propagación de trace-id

- HTTP: header `x-trace-id` generado por el API Gateway al recibir la request. Cada servicio lo propaga al llamar a otro y lo pone como header AMQP al publicar.
- AMQP: header `x-trace-id` obligatorio (`03-eventos-dominio.md`). Middleware de NestJS microservices lo extrae y lo pone en el contexto de log.

---

## 9. Dependencias (política)

### Cómo introducir una dependencia

Checklist antes de agregar una librería:

1. ¿Existe ya algo equivalente en las deps del monorepo? Preferir reutilizar.
2. ¿Está activamente mantenida? Último commit < 6 meses, issues con respuestas.
3. ¿Su licencia es MIT/Apache/BSD? Si es GPL o propietaria, requiere ADR.
4. ¿Tiene tipos TypeScript? Si no, pensar dos veces.
5. ¿Está bien descargada? < 10 k descargas semanales es señal de alerta.
6. ¿Tiene dependencias transitivas extrañas? Revisar `npm-ls`.
7. Verificar nombre contra typo-squatting (variantes de nombres populares).

### Fijación de versiones

- Deps directas: `^` solo si la librería sigue semver estrictamente; de otro modo versión exacta.
- Deps críticas (prisma, nestjs, typescript, zod): versión exacta.
- `pnpm-lock.yaml` commiteado y versionado.

### Auditoría

- `pnpm audit` corre en CI. Vulnerabilidades alto/crítico rompen el build.
- `pnpm outdated` semanal, revisión manual de upgrades mayor.

---

## 10. Estructura de commit

### Conventional Commits (convención blanda)

Recomendado pero no bloqueante. Facilita changelog y lectura rápida del historial.

Formato:

```
<type>(<scope>): <subject>

<body opcional>

<footer opcional>
```

Tipos comunes:

| Tipo | Uso |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `refactor` | Cambio que no altera comportamiento |
| `docs` | Solo documentación |
| `test` | Solo tests |
| `chore` | Tooling, dependencias, config |
| `perf` | Mejora de performance |

Scope sugerido: nombre del microservicio (`auth`, `inventory`, `request`, `loan`, `notification`, `ai-risk`, `ai-assistant`, `reports`, `gateway`, `portal`, `totem`) o `monorepo`, `docs`, `infra`.

Ejemplos buenos:

```
feat(auth): implementa cambio obligatorio de clave en primer login (RF-C.10)
fix(inventory): corrige liberación de reserva al cancelar solicitud
docs(architecture): agrega ADR-015 para reports-svc
chore(monorepo): actualiza turbo a 2.1.0
```

### Reglas mínimas (sí obligatorias)

- Mensaje en español o inglés, consistente dentro del PR.
- Primer línea ≤ 72 caracteres.
- Referenciar ID de requerimiento (`RF-C.10`, `RC.01`) o de task cuando aplica.
- **No** mensajes como `wip`, `fix`, `update`, `asdf`. Si usas WIP local, haz squash antes de integrar.

---

## 11. Documentación de código

### Comentarios

- El código debe ser legible por nombre; los comentarios explican **por qué**, no **qué**.
- Si necesitas un comentario largo, probablemente el código puede refactorearse.
- Excepciones aceptadas: lógica de negocio no obvia referenciada a un `RC.*`, workarounds por bugs de librería (link al issue), decisiones de performance no intuitivas.

### JSDoc

- Funciones **exportadas** desde `libs/` tienen JSDoc con `@param`, `@returns`, `@throws`.
- Casos de uso de `application/` tienen un JSDoc breve explicando el flujo de negocio y el requerimiento asociado.
- El dominio tiene JSDoc en métodos no triviales que cambian estado.

Ejemplo:

```ts
/**
 * Marca al usuario como bloqueado por morosidad automática (RC.01).
 *
 * @throws {InvalidUserStateError} si el usuario ya está en un estado terminal.
 */
blockForMorosidad(reason: string): void { ... }
```

### OpenAPI

- El API Gateway genera OpenAPI 3 desde los decorators NestJS con `@nestjs/swagger`.
- La especificación se publica en `GET /docs` en desarrollo.
- El archivo `.json` exportado se commitea en `docs/api/openapi.json` tras cada sprint para trazabilidad.

---

## 12. Accesibilidad (frontends)

Regla mínima de la guía Kiro: el código generado debe ser accesible.

- Elementos interactivos con `aria-label` cuando no hay texto visible.
- Contraste AA mínimo en colores.
- Formularios: `<label>` asociado a cada `<input>`; errores anunciados con `aria-live`.
- Navegación por teclado funcional en portal y tótem (el tótem es **exclusivamente** teclado y touch, sin mouse — verificar que todo se alcanza con Tab + Enter).
- Testing con `@testing-library/react` (prioriza queries por rol ARIA).

La validación completa de WCAG requiere revisión manual con herramientas de asistencia; el MVP apunta a "sin errores obvios de accesibilidad" como baseline.

---

## 13. Referencias

- Arquitectura interna de cada servicio: `01-hexagonal-architecture.md`.
- Testing: `02-testing-strategy.md`.
- Stack tecnológico: `docs/architecture/01-stack-tecnologico.md`.
- ADRs aplicables: ADR-001 (stack), ADR-003 (NestJS), ADR-009 (cloud-agnóstico).
- Requerimientos que este documento cubre: `RNF-MNT.1`, `RNF-MNT.2`, `RNF-MNT.3`, `RNF-OBS.2`, `RNF-SEC.2`.
