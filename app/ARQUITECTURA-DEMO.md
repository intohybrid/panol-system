# Arquitectura del Demo — Decisiones Técnicas

**Branch:** `feature/app-demo`  
**Fecha:** 2026-05-06  
**Contexto:** Este documento registra las decisiones tomadas para el demo funcional mock-first. Complementa `app.md` y `app-web.md`. Para la arquitectura objetivo de producción ver `docs/architecture/`.

---

## 1. Topología — Opción B: Procesos separados

**Decisión:** Cada microservicio corre como un proceso Node.js independiente.

```
[web-portal :4200] ─┐
                    ├──> [api-gateway :3000] ──HTTP──> [auth-svc        :3001]
[totem      :4201] ─┘                                  [inventory-svc   :3002]
                                                        [request-svc     :3003]
                                                        [loan-svc        :3004]
                                                        [ai-assistant-svc:3005]
```

**Justificación:** Demostrar la separación real de responsabilidades frente a la rúbrica. Cada servicio tiene su propia colección in-memory (simula su propia BD), su propio `package.json` y corre en su puerto declarado en `app.md`.

**Servicios del demo (scope reducido):** Se incluyen los 5 servicios más relevantes para el flujo principal. `notification-svc`, `ai-risk-svc` y `reports-svc` quedan fuera del demo por complejidad y son roadmap.

| Servicio | Puerto | Responsabilidad en el demo |
|---|---|---|
| `api-gateway` | 3000 | Único punto de entrada de los frontends. Proxy + auth middleware. |
| `auth-svc` | 3001 | Login, JWT, verificación de PIN, seed de usuarios. |
| `inventory-svc` | 3002 | Catálogo, stock, reservas. |
| `request-svc` | 3003 | Creación de solicitudes, TTL simulado. |
| `loan-svc` | 3004 | Materialización y devolución. |
| `ai-assistant-svc` | 3005 | Asistente por keyword matching (mock). |

---

## 2. Autenticación — JWT real (HS256)

**Decisión:** Se usa `@nestjs/jwt` con secret hardcodeado para el demo.

```
POST /auth/login → { documento, password }
                 ← { accessToken, refreshToken, user }

POST /auth/verify-pin → { pin }   (solo Pañolero, desde el tótem)
                      ← { ok: true }
```

- **Access token TTL:** 8 horas (suficiente para una demo sin expiración molesta).
- **Secret:** `PANOL_DEMO_SECRET_2026` (hardcodeado, no requiere `.env` para correr).
- **Payload JWT:** `{ sub: userId, role, nombre, documento }`.
- **Almacenamiento en frontend:** `localStorage` con claves `panol.access_token` y `panol.user`.
- **Interceptor Angular:** `AuthInterceptor` adjunta `Authorization: Bearer <token>` a todas las requests.
- **Middleware gateway:** Valida JWT en cada request entrante antes de hacer proxy al servicio destino. Rutas públicas: `POST /auth/login`.

**Contraseñas:** Hasheadas con `bcrypt` (salt rounds: 10). El seed usa `bcrypt.hashSync` para generar los hashes en tiempo de inicio del servicio.

**Justificación:** JWT real demuestra autenticación completa a la rúbrica. TTL extendido a 8 h evita interrupciones durante la demo.

---

## 3. SSR (Server-Side Rendering) — Deshabilitado en demo

**Decisión:** El `web-portal` corre como **SPA pura** (sin SSR) durante el demo.

**Justificación técnica:** Con Angular Universal SSR, el servidor Node que renderiza las páginas hace llamadas HTTP directamente (no pasan por el proxy `proxy.conf.json` del dev server). En un entorno con 6 procesos en puertos distintos, eso requiere configurar URLs separadas para SSR y para el cliente. Esta complejidad no aporta valor a la demo.

**Cómo se deshabilita:** Se elimina `provideServerRendering` del `app.config.ts` del `web-portal` y se ajusta el `angular.json` para no usar `server.ts`. Los archivos `app.config.server.ts`, `app.routes.server.ts` y `server.ts` se conservan (para no perder trabajo) pero no se usan en la configuración de demo.

**En producción** el SSR se reactiva según `09-despliegue-uis.md`.

---

## 4. Arranque unificado y Ejecución del Demo

Para facilitar la evaluación de la arquitectura, se configuró un monorepo ligero que orquesta todos los microservicios y frontends usando `concurrently` desde el `package.json` raíz (`/app`).

### Instrucciones de Ejecución

1. **Navegar a la carpeta de la aplicación:**
   ```bash
   cd app
   ```

2. **Instalar dependencias globales y de todos los microservicios:**
   ```bash
   npm install
   ```

3. **Iniciar el entorno completo (8 procesos):**
   ```bash
   npm run demo
   ```

Esto levanta:
- **api-gateway** (3000)
- **auth-svc** (3001)
- **inventory-svc** (3002)
- **request-svc** (3003)
- **loan-svc** (3004)
- **ai-assistant-svc** (3005)
- **web-portal** (Angular, 4200)
- **totem** (Angular, 4201)

### Accesos Rápidos

- **Portal Web (Alumnos/Docentes):** [http://localhost:4200](http://localhost:4200)
- **Tótem (Pañoleros):** [http://localhost:4201](http://localhost:4201)

**Comandos individuales disponibles:**
```bash
npm run demo:backend   # solo los 6 procesos NestJS
npm run demo:frontend  # solo los 2 Angular dev servers
npm run demo:gateway   # solo el gateway
```

---

## 4.1 Estándares de Implementación Frontend (Angular 19+)

Para alinear el código con prácticas modernas, las aplicaciones `web-portal` y `totem` se desarrollan bajo las siguientes directrices:

1. **Reactividad con Signals:**
   Evitamos `RxJS` para el estado simple, prefiriendo Signals (`signal`, `computed`, `resource` para llamadas HTTP).

2. **Componentes Standalone y Control Flow:**
   Uso de `@Component({ standalone: true })` y nueva sintaxis de plantillas (`@if`, `@for`).

3. **Inyección de Dependencias (DI):**
   Uso preferencial de la función `inject()` sobre constructores para inyectar servicios.

4. **Diseño y Estilos:**
   Vanilla CSS con CSS Variables (Diseño basado en Tokens: Rojo `#e11d48` y Dark `#0f172a`).

5. **Intercepción de Tokens:**
   El JWT (obtenido tras el login) se inyecta automáticamente usando `AuthInterceptor` (basado en `HttpInterceptorFn`).

---

## 5. Usuarios del demo (seed hardcodeado en auth-svc)

**Decisión:** 4 usuarios, uno por cada rol relevante para el flujo principal.

| Rol | Nombre | RUT / Documento | Contraseña | PIN |
|---|---|---|---|---|
| `ALUMNO` | María González | `20123456-7` | `alumno123` | — |
| `PANOLERO` | Esteban Solís | `11234567-8` | `panolero123` | `1234` |

**Autenticación del Tótem (decisión demo):** El tótem usa **solo PIN** como mecanismo de acceso. No requiere usuario+contraseña. El flujo es:
1. Pañolero ingresa PIN en teclado virtual
2. `POST /auth/login-pin` busca el usuario con ese pinHash y devuelve JWT
3. Tótem almacena JWT y accede al dashboard

Esto simplifica el demo sin perder la demostración del PIN virtual (ADR-011). En producción el flujo sería usuario+contraseña al inicio del turno + PIN para acciones sensibles.
| `COORDINADOR` | Carmen Vidal | `12345678-9` | `coordinador123` | — |
| `JEFE` | Roberto Fuentes | `13456789-0` | `jefe123` | — |

Estos usuarios se generan en el arranque del `auth-svc` en su colección in-memory. **No se persisten entre reinicios** (comportamiento esperado del demo mock).

---

## 6. Estructura de directorios (`app/`)

**Decisión:** `app/` tiene su propio `package.json` raíz que actúa como coordinador del monorepo del demo.

```
app/
├── package.json              ← ROOT: workspaces, scripts concurrently
├── app.md                    ← guía del demo (actualizada)
├── app-web.md               ← guía frontend (actualizada)
├── ARQUITECTURA-DEMO.md     ← ESTE ARCHIVO: decisiones del demo
├── services/                ← microservicios NestJS (un dir por servicio)
│   ├── api-gateway/
│   │   ├── package.json
│   │   └── src/
│   ├── auth-svc/
│   │   ├── package.json
│   │   └── src/
│   ├── inventory-svc/
│   │   ├── package.json
│   │   └── src/
│   ├── request-svc/
│   │   ├── package.json
│   │   └── src/
│   ├── loan-svc/
│   │   ├── package.json
│   │   └── src/
│   └── ai-assistant-svc/
│       ├── package.json
│       └── src/
├── shared/                  ← interfaces TypeScript compartidas (no tiene runtime)
│   ├── package.json
│   └── src/
│       ├── models/          ← User, Resource, Request, Loan (interfaces tipadas)
│       └── events/          ← contratos de eventos de dominio (strings + payloads)
└── frontend/
    └── panol-frontend/      ← Angular Workspace (sin cambios de estructura)
        └── projects/
            ├── web-portal/  ← SPA sin SSR (demo)
            └── totem/
```

---

## 7. Comunicación entre servicios (demo shortcut)

**Decisión:** En el demo, los servicios se comunican via **HTTP directo** entre ellos. El `api-gateway` llama a cada servicio via HTTP. Cuando un servicio necesita notificar a otro (equivalente a publicar un evento en RabbitMQ), lo hace via una llamada HTTP al servicio destino.

**Ejemplo — flujo de reserva:**
```
Portal → POST /requests (gateway)
gateway → POST http://request-svc:3003/requests
request-svc → (valida) → POST http://inventory-svc:3002/stock/reserve  ← "evento" simulado
inventory-svc → actualiza su colección in-memory → 200 OK
request-svc → 201 Created (la solicitud con estado PENDIENTE)
gateway → 201 → Portal
```

**Esto NO es lo que iría en producción.** En producción, `request-svc` publicaría `request.created` en `domain.events` (RabbitMQ) e `inventory-svc` lo consumiría asincrónicamente. El demo simplifica esto a HTTP síncrono para no requerir un broker.

Esta decisión se documenta explícitamente para que la mesa redonda entienda la diferencia.

---

## 8. Scope de funcionalidades del demo

### ✅ Incluido en el demo
- Login con JWT (todos los roles)
- PIN del pañolero en el tótem (teclado numérico virtual)
- Catálogo de inventario con stock disponible
- Asistente IA (keyword matching mock, sin OpenAI real)
- Crear solicitud (con validación de stock)
- Reserva de stock (simula TTL de 30 min en demo)
- Materializar préstamo desde el tótem
- Devolución con estado por ítem (BUENO / DAÑADO / FALTANTE)

### ❌ Fuera del scope del demo (roadmap)
- Notificaciones in-app (notification-svc)
- Tickets PDF (notification-svc)
- Scoring de riesgo real (ai-risk-svc)
- Reportes de gestión (reports-svc)
- OpenAI real (requiere API key y costo)
- WebSocket push (requiere Socket.IO setup completo)
- Bloqueo automático de morosos (auth-svc reactivo)
- Importación masiva de alumnos (CSV/Excel)

---

## Referencias

- `app/app.md` — instrucciones de ejecución del demo
- `app/app-web.md` — estándares de implementación Angular
- `docs/architecture/07-microservicios-responsabilidades.md` — fuente de verdad de responsabilidades
- `docs/architecture/09-despliegue-uis.md` — decisión sobre SSR y puertos
- `docs/design/adrs/ADR-011-pin-totem-sesion-persistente.md` — PIN del pañolero
