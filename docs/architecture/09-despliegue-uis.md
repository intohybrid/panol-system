# Despliegue de UIs y ruteo del edge

## Propósito

Este documento responde de forma operativa a tres preguntas que los documentos hermanos dejaban sin tratar:

1. ¿Cómo se sirve cada frontend? (contenedor, proceso, puerto).
2. ¿Cómo llegan las peticiones del cliente al `api-gateway` y a los servicios internos?
3. ¿Cómo se autentican las UIs y cómo viaja el token?

Las decisiones están tomadas en **ADR-016**. Este documento detalla cómo se materializan: estructura de contenedores, variables de entorno, CORS, WebSocket, refresh token, kiosko del tótem y la evolución a producción.

Aplica al MVP local con `docker-compose`. La topología de producción se documenta al final como roadmap.

---

## 1. Piezas del frontend y modo de servicio

### `web-portal` — Next.js 14 standalone

Aplicación Next.js servidor-rendered destinada a alumnos, docentes, coordinadores y jefes. Corre como proceso Node dentro de un contenedor.

- **Build**: `next build` con `output: 'standalone'` configurado en `next.config.js`. Produce `.next/standalone/server.js` + assets optimizados.
- **Runtime**: `node server.js`. Listen en `PORT` (3000 por defecto).
- **Hidratación**: SSR para rutas autenticadas con datos del usuario; client-side navigation dentro de la app.
- **Llamadas al backend**: TanStack Query + interceptor que adjunta `Authorization: Bearer <jwt>`.

**Justificación del SSR standalone**: `01-stack-tecnologico.md` ya lo decidió. Next.js standalone produce un bundle mínimo listo para contenedor sin depender del CLI de Next en runtime, lo que permite imagen Docker pequeña (~150 MB).

### `totem` — Vite + React SPA

Aplicación Vite de React para el Pañolero, servida como estáticos en un contenedor `nginx:alpine`.

- **Build**: `vite build` produce `dist/` con `index.html`, JS y CSS hashed.
- **Runtime**: nginx sirve `dist/` con fallback SPA (`try_files $uri $uri/ /index.html`).
- **Sesión**: mantiene la pantalla abierta durante el turno del Pañolero (ver `RC.14`). Reingreso de PIN (ADR-011) para acciones sensibles.
- **Llamadas al backend**: cliente HTTP (Axios) con interceptor similar al portal.

**Justificación nginx para el tótem**: es una SPA pura, no necesita Node en runtime. nginx sirve estáticos eficientemente, el contenedor queda ~25 MB, y configurar el fallback SPA es una línea.

### `api-gateway` — NestJS

Ya documentado en `07-microservicios-responsabilidades.md §1` y en ADR-008. Expone HTTP (comandos/queries) y WebSocket (Socket.IO) a las UIs.

---

## 2. Dockerfiles (esqueleto canónico)

### Portal

```dockerfile
# apps/web-portal/Dockerfile

FROM node:20-alpine AS builder
WORKDIR /app
COPY . .
RUN corepack enable && pnpm install --frozen-lockfile
RUN pnpm --filter web-portal build

FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/apps/web-portal/.next/standalone ./
COPY --from=builder /app/apps/web-portal/.next/static ./apps/web-portal/.next/static
COPY --from=builder /app/apps/web-portal/public ./apps/web-portal/public
EXPOSE 3000
USER node
CMD ["node", "apps/web-portal/server.js"]
```

### Tótem

```dockerfile
# apps/totem/Dockerfile

FROM node:20-alpine AS builder
WORKDIR /app
COPY . .
RUN corepack enable && pnpm install --frozen-lockfile
RUN pnpm --filter totem build

FROM nginx:alpine AS runtime
COPY --from=builder /app/apps/totem/dist /usr/share/nginx/html
COPY apps/totem/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

`apps/totem/nginx.conf` mínimo:

```nginx
server {
  listen 80;
  server_name _;
  root /usr/share/nginx/html;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  # Headers de seguridad básicos
  add_header X-Content-Type-Options nosniff;
  add_header X-Frame-Options DENY;
  add_header Referrer-Policy strict-origin-when-cross-origin;
}
```

### API Gateway

Dockerfile estándar NestJS (ver `hexagonal-template/README.md` para el patrón multi-stage).

---

## 3. docker-compose (fragmento de frontends + gateway)

Extracto del `infra/docker-compose.yml` que se construirá en el Paso 2. Los servicios backend, broker y DB se agregan en esa fase; aquí se muestra solo la parte que toca este documento.

```yaml
services:
  web-portal:
    build:
      context: ../
      dockerfile: apps/web-portal/Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_BASE_URL: http://localhost:4000
      NEXT_PUBLIC_WS_URL: ws://localhost:4000/ws
      NODE_ENV: production
    depends_on:
      - api-gateway

  totem:
    build:
      context: ../
      dockerfile: apps/totem/Dockerfile
    ports:
      - "3001:80"
    environment:
      VITE_API_BASE_URL: http://localhost:4000
      VITE_WS_URL: ws://localhost:4000/ws
    depends_on:
      - api-gateway

  api-gateway:
    build:
      context: ../
      dockerfile: apps/api-gateway/Dockerfile
    ports:
      - "4000:4000"
    environment:
      PORT: 4000
      CORS_ALLOWED_ORIGINS: "http://localhost:3000,http://localhost:3001"
      JWT_SECRET: "${JWT_SECRET}"
      RABBITMQ_URL: "amqp://rabbitmq:5672"
      # ... resto
    depends_on:
      - rabbitmq
```

**Observaciones importantes**:

- `NEXT_PUBLIC_*` y `VITE_*` son variables **que el bundler inyecta en el bundle cliente**. Apuntan a `localhost:4000` porque la UI las evalúa en el navegador del desarrollador, no dentro del contenedor. Si apuntaran a `http://api-gateway:4000`, el navegador del desarrollador no resuelve ese hostname y falla.
- Para las **server-side calls del portal** (SSR) que necesiten hablar con el gateway desde dentro del contenedor, se usa una variable adicional `API_BASE_URL_INTERNAL=http://api-gateway:4000` (sin prefijo `NEXT_PUBLIC_`). El código de servidor en Next.js la usa; el código de cliente usa `NEXT_PUBLIC_API_BASE_URL`.

### Variable pública vs interna en Next.js

| Variable | Leída desde | Valor en MVP local |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | navegador | `http://localhost:4000` |
| `NEXT_PUBLIC_WS_URL` | navegador | `ws://localhost:4000/ws` |
| `API_BASE_URL_INTERNAL` | SSR dentro del contenedor | `http://api-gateway:4000` |

Esta separación evita el bug clásico "funciona en client-side pero no en SSR" o viceversa.

---

## 4. CORS

El `api-gateway` activa CORS con una lista explícita de orígenes leída de `CORS_ALLOWED_ORIGINS`:

```ts
// apps/api-gateway/src/main.ts
app.enableCors({
  origin: env.CORS_ALLOWED_ORIGINS.split(',').map((s) => s.trim()),
  credentials: false, // no usamos cookies
  methods: ['GET', 'POST', 'PATCH', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Trace-Id'],
  maxAge: 86400,
});
```

Regla: **nunca `origin: '*'`**. Cada ambiente declara sus orígenes explícitamente.

---

## 5. Autenticación y JWT

### Flujo

1. **Login**: `POST /auth/login` con `{ documento, password }`. Gateway valida contra `auth-svc`, responde con `{ accessToken, refreshToken, user }` en el cuerpo.
2. **Almacenamiento**: UI guarda ambos tokens en `localStorage` (portal y tótem) con claves `panol.access_token` y `panol.refresh_token`.
3. **Peticiones REST**: interceptor HTTP adjunta `Authorization: Bearer <accessToken>` en todas las requests.
4. **Peticiones WebSocket**: cliente Socket.IO pasa el token en handshake:

   ```ts
   import { io } from 'socket.io-client';

   const socket = io(WS_URL, {
     auth: { token: getAccessToken() },
   });
   ```

5. **Refresh**: si la respuesta es `401`, el interceptor llama `POST /auth/refresh` con el refresh token, guarda el nuevo par y reintenta la petición original (una sola vez; si falla de nuevo, logout).

### Tiempos de vida

- **Access token**: 15 minutos. Firmado con `JWT_SECRET` (HS256 en MVP).
- **Refresh token**: 7 días. Persistido en `auth-svc` (tabla `refresh_tokens`) para poder revocar.
- Logout: borra localStorage + invalida refresh token en servidor.

### Riesgos aceptados

- localStorage es accesible desde JavaScript y por tanto vulnerable a XSS. Mitigación: la política de `00-coding-standards.md §5` exige escapar texto libre en frontends y la CSP del nginx del tótem bloquea scripts inline.
- No hay rotación automática del `JWT_SECRET` en MVP. En producción se implementa con un secrets manager (ADR-009 roadmap).

---

## 6. WebSocket

El `api-gateway` expone un único endpoint Socket.IO en `ws://localhost:4000/ws`. Las UIs se suscriben al topic correspondiente a su usuario (`user:{userId}`) y reciben notificaciones push derivadas de `notification-svc`.

### Handshake

El gateway valida el JWT en el middleware de conexión:

```ts
@WebSocketGateway({ path: '/ws', cors: { origin: ENV.CORS_ALLOWED_ORIGINS.split(',') } })
export class NotificationsGateway implements OnGatewayConnection {
  async handleConnection(client: Socket) {
    const token = client.handshake.auth?.token;
    const payload = await this.jwtService.verifyAsync(token).catch(() => null);
    if (!payload) return client.disconnect(true);
    client.data.userId = payload.sub;
    client.join(`user:${payload.sub}`);
  }
}
```

Si el token está vencido o falta, se cierra la conexión. El cliente debe reautenticar y reconectar.

### Reconexión

Socket.IO reconecta automáticamente con backoff. El cliente debe re-emitir el token en cada reconexión (Socket.IO `auth` callback):

```ts
const socket = io(WS_URL, {
  auth: (cb) => cb({ token: getAccessToken() }),
});
```

Esto asegura que después de un refresh de token, la próxima reconexión usa el nuevo token.

---

## 7. Kiosko del tótem

El tótem no es solo la SPA: es una tablet o PC físico en el mostrador del pañol que corre un navegador en modo kiosko apuntando a `http://<host-compose>/totem-url`.

### Configuración del navegador kiosko

**No es parte del compose**. Es configuración del dispositivo físico. Recomendación operativa:

- **Chromium kiosk mode**: `chromium --kiosk --disable-features=TranslateUI http://localhost:3001` lanzado al arranque del sistema operativo.
- Deshabilitar atajos de escape del navegador (extensión de kiosk).
- Deshabilitar atajos del OS para salir (configuración de Linux Kiosk / Windows Shell Launcher).
- Pantalla bloqueada contra salida al OS; único contenido visible: la SPA del tótem.

Esta configuración queda como **deuda operacional** documentada y no bloquea el MVP. El MVP demuestra el tótem en un navegador normal con F11 fullscreen.

### UX en el contenedor

El tótem de producción se conecta al gateway real, no a `localhost`. En el dispositivo físico, la variable `VITE_API_BASE_URL` se fija al URL del gateway de producción en el build time.

---

## 8. Health checks y disponibilidad

Cada UI contenedor expone su propio health check para el orquestador:

- **Portal**: `GET /api/health` (API route de Next.js que devuelve 200 si SSR responde).
- **Tótem**: `GET /health` (endpoint estático `health.txt` servido por nginx).
- **Gateway**: `GET /health` (endpoint del controller con `@Public()` que devuelve 200 si los servicios internos críticos responden al ping).

Docker-compose usa `healthcheck:` en cada servicio para que `depends_on` respete el orden de arranque real.

---

## 9. Evolución a producción

Cuando el sistema se despliegue a un ambiente real (cloud o on-prem), se introduce un **reverse proxy único** que hace la topología path-based. Ejemplos:

### Nginx (on-prem)

```nginx
server {
  listen 443 ssl;
  server_name panol.escuela.cl;

  location / {
    proxy_pass http://web-portal:3000;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }

  location /totem/ {
    proxy_pass http://totem:80/;
  }

  location /api/ {
    proxy_pass http://api-gateway:4000/;
  }

  location /api/ws {
    proxy_pass http://api-gateway:4000/ws;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 86400;
  }
}
```

### AWS

- CloudFront o ALB como edge.
- `/` → `web-portal` en ECS Fargate.
- `/totem/*` → `totem` en ECS o directamente S3 + CloudFront (estático).
- `/api/*` → `api-gateway` en ECS.
- ACM para TLS, Route53 para DNS, AWS Secrets Manager para `JWT_SECRET`.

### Azure

- Front Door + Azure Container Apps.
- Misma topología path-based.
- Key Vault para secretos.

### GCP

- Cloud Load Balancer + Cloud Run.
- Secret Manager para secretos.

**Cambio mínimo desde MVP**: solo la variable `NEXT_PUBLIC_API_BASE_URL` pasa de `http://localhost:4000` a `https://panol.escuela.cl/api`. El código no se toca.

---

## 10. Tabla resumen

| Aspecto | MVP local | Producción (roadmap) |
|---|---|---|
| Puerto portal | 3000 | 443 (vía proxy) |
| Puerto tótem | 3001 | 443 (vía proxy, path `/totem`) |
| Puerto gateway | 4000 | 443 (vía proxy, path `/api`) |
| CORS | Explícito por origen | Mismo origen (no aplica) |
| TLS | No (HTTP) | Obligatorio (HTTPS) |
| JWT | localStorage + header | localStorage + header |
| WebSocket | `ws://localhost:4000/ws` | `wss://panol.escuela.cl/api/ws` |
| Reverse proxy | No | Sí (nginx / Traefik / ALB / Front Door) |
| Secrets | `.env` local | Secrets manager del cloud |
| Kiosko | F11 fullscreen en Chrome | Navegador kiosko dedicado + OS lock |

---

## 11. Referencias

- **ADR-016** — decisión de topología, modo de servicio y transporte de JWT.
- ADR-001 (stack), ADR-008 (API Gateway propio), ADR-009 (cloud-agnóstico), ADR-011 (PIN tótem).
- `docs/architecture/01-stack-tecnologico.md` — justificación de Next.js y Vite.
- `docs/architecture/02-topologia-microservicios.md` — topología de backend.
- `docs/architecture/07-microservicios-responsabilidades.md` — qué hace el gateway.
- `docs/standards/00-coding-standards.md §7` — validación de `.env` con Zod.
- Requerimientos cubiertos: `RNF-SEC.1`, `RNF-SEC.4`, `RNF-SEC.5`, `RNF-DIS.1`.
