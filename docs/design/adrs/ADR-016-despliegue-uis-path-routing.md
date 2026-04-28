# ADR-016 — Despliegue de UIs con separación por puerto/path y JWT en header

- **Estado**: Aceptada para MVP
- **Fecha**: 2026-04-25
- **Decisores**: Equipo Magíster

## Contexto

El sistema tiene dos frontends y un API Gateway (ADR-008):

- `web-portal` (Next.js 14) — alumnos, docentes y administradores.
- `totem` (Vite + React) — SPA kiosko del Pañolero.
- `api-gateway` (NestJS) — único punto de entrada backend.

Los documentos de arquitectura describen el stack de cada UI pero no declaraban **cómo se sirven las UIs, cómo se enrutan las peticiones y cómo se autentican** contra el gateway. Hay tres preguntas abiertas:

1. **Topología del edge**: ¿reverse proxy único (Traefik/nginx) con paths y un solo puerto? ¿Puertos separados por servicio? ¿Subdominios?
2. **Modo de servicio de cada UI**: Next.js en standalone (SSR en Node) vs export estático. Vite SPA estático vs servido por nginx.
3. **Transporte de credenciales**: JWT en header `Authorization` vs cookies httpOnly.

El proyecto es **académico, local, MVP** (ambiente contenido). Cualquier pieza operativa adicional (reverse proxy, secrets manager, CDN) tiene costo de aprendizaje y configuración que no aporta al objetivo de la rúbrica ni al prototipo funcional.

## Decisión

### 1. Topología: puertos separados en MVP, path-based para producción

En el MVP local, cada pieza escucha en su propio puerto del host:

| Pieza | Puerto host | URL local |
|---|---|---|
| `web-portal` (Next.js) | 3000 | `http://localhost:3000` |
| `totem` (Vite SPA) | 3001 | `http://localhost:3001` |
| `api-gateway` (NestJS) | 4000 | `http://localhost:4000` |
| WebSocket del gateway | 4000 | `ws://localhost:4000/ws` |
| RabbitMQ Management | 15672 | `http://localhost:15672` |
| pgAdmin (opcional) | 5050 | `http://localhost:5050` |

Las UIs apuntan al gateway mediante variable de entorno `NEXT_PUBLIC_API_BASE_URL=http://localhost:4000` (portal) y `VITE_API_BASE_URL=http://localhost:4000` (tótem). El gateway habilita **CORS explícito** para los orígenes `http://localhost:3000` y `http://localhost:3001`.

Para **producción**, la forma recomendada es reverse proxy único con separación por path (`/` → portal, `/totem` → tótem, `/api` → gateway, `/api/ws` → WebSocket), pero su configuración queda fuera del alcance del MVP. Se documenta como evolución en §Consecuencias.

### 2. Modo de servicio

- **web-portal (Next.js 14) en modo `standalone`**. Build produce `.next/standalone/server.js`, contenedor corre Node con `node server.js`. SSR habilitado (justificado en `01-stack-tecnologico.md`: SSR útil para primera carga y metadata del portal).
- **totem (Vite SPA) servido por nginx liviano**. Build produce `dist/`, contenedor multi-stage (stage build con Node + Vite, stage runtime con `nginx:alpine` sirviendo `dist/`). SPA pura sin SSR (es kiosko, primera carga no se optimiza).

### 3. Autenticación: JWT en header `Authorization: Bearer`

- El gateway emite JWT en `POST /auth/login` en el cuerpo de la respuesta.
- Las UIs guardan el JWT en **localStorage** del navegador.
- Cada request HTTP del cliente lleva `Authorization: Bearer <jwt>`.
- Las conexiones WebSocket Socket.IO reciben el JWT como `auth.token` en el handshake (`io(url, { auth: { token } })`).
- Refresh token también en el body de la respuesta, se rota cuando el access token vence.

No se usan cookies en MVP. Se revisa para producción real (ver consecuencias).

## Alternativas consideradas

### Traefik como reverse proxy desde el MVP

- **Pros**: misma topología que producción; un solo puerto; CORS se elimina (mismo origen); descubrimiento por labels de Docker cómodo.
- **Contras**: una pieza operativa adicional que aprender y configurar; labels de Docker para routing añaden verbosidad al `docker-compose.yml`; problema de WebSocket con Traefik requiere tuning extra; el equipo no lo conoce todavía.

### nginx como reverse proxy desde el MVP

- **Pros**: estándar, bien conocido.
- **Contras**: configuración separada (`nginx.conf`), otro contenedor, SSL self-signed para local si queremos HTTPS end-to-end. Aporta realismo pero distrae.

### Subdominios (`portal.panol.local`, `totem.panol.local`, `api.panol.local`)

- **Pros**: cookies compartidas por parent domain (útil si se usaran cookies de sesión).
- **Contras**: requiere DNS local (`/etc/hosts` o DNS interno del compose), más setup para developer onboarding. No aporta sobre paths/puertos.

### Next.js export estático + nginx

- **Pros**: más simple (sin runtime Node), CDN-friendly.
- **Contras**: pierde SSR. El stack lo justifica en ADR-001 y en `01-stack-tecnologico.md`. Cambiar a estático sería rediseño del portal.

### JWT en cookie httpOnly

- **Pros**: más seguro contra XSS (el script no puede leer la cookie); estándar en apps serias.
- **Contras**: requiere CSRF token para mutaciones, `SameSite=Lax/Strict`, complica WebSocket (cookie viaja al handshake solo si mismo origen), complica tests. Seguridad agregada es importante en producción pero excede el alcance MVP.

### Cero autenticación en el MVP

Inaceptable. `RNF-SEC.*` exige RBAC y control de acceso.

## Decisión justificada

El proyecto es académico y local. Simplicidad de setup para cualquier desarrollador pesa sobre realismo de producción. Puertos separados funcionan con una línea de compose por servicio; Traefik funciona con configuración, labels y debug adicional. Diferir el reverse proxy a producción no compromete el diseño: el gateway sigue siendo el único punto de entrada backend; las UIs nunca hablan con servicios internos directo.

Next.js standalone preserva SSR y la decisión ya está en stack; Vite servido por nginx es el patrón canónico de SPA y ya viene casi gratis en un `Dockerfile` multi-stage.

JWT en header es lo más directo para un MVP que usa tanto REST como WebSocket. La alternativa cookie agregará complejidad sin beneficio visible en la defensa de la rúbrica (el tema de seguridad transversal se cubre con RNF-SEC.* y con ADR-011 del PIN del tótem).

## Consecuencias

### Del lado del desarrollo

- Cada UI declara `NEXT_PUBLIC_API_BASE_URL` / `VITE_API_BASE_URL` en su `.env.example` con default `http://localhost:4000`.
- El `api-gateway` habilita CORS con lista explícita de orígenes leída de `CORS_ALLOWED_ORIGINS` env var; en MVP local: `http://localhost:3000,http://localhost:3001`.
- Las UIs implementan un **interceptor HTTP** (Axios/TanStack Query) que agrega el header `Authorization: Bearer <jwt>` automáticamente.
- El cliente Socket.IO pasa el JWT en `auth.token`; el gateway lo valida en el middleware de conexión.

### Del lado del contenedor

- `apps/web-portal/Dockerfile`: multi-stage con `output: 'standalone'` configurado en `next.config.js`. Contenedor final basado en `node:20-alpine`, entrypoint `node server.js`, expone `PORT=3000`.
- `apps/totem/Dockerfile`: multi-stage. Stage build con Node 20 corre `vite build` produciendo `dist/`. Stage runtime: `nginx:alpine` copia `dist/` a `/usr/share/nginx/html` y un `nginx.conf` mínimo con SPA fallback (`try_files $uri $uri/ /index.html`).
- `apps/api-gateway/Dockerfile`: multi-stage estándar NestJS. Node 20 alpine runtime.

### Del lado del `docker-compose`

Servicios mínimos del compose (contemplado para el Paso 2 de la implementación):

```
services:
  web-portal:
    build: ./apps/web-portal
    ports: ["3000:3000"]
    environment:
      NEXT_PUBLIC_API_BASE_URL: http://localhost:4000
    depends_on: [api-gateway]

  totem:
    build: ./apps/totem
    ports: ["3001:80"]   # nginx escucha en 80 dentro del contenedor
    environment:
      VITE_API_BASE_URL: http://localhost:4000
    depends_on: [api-gateway]

  api-gateway:
    build: ./apps/api-gateway
    ports: ["4000:4000"]
    environment:
      CORS_ALLOWED_ORIGINS: http://localhost:3000,http://localhost:3001
    # ... resto de config
```

Las UIs y el gateway son todas piezas del compose; se levantan con `docker compose up`.

### Del lado de producción (roadmap)

Cuando se despliegue a cloud real, se introduce un reverse proxy (Traefik/nginx/ALB/Front Door) con la topología path-based:

- `/` → web-portal
- `/totem` → totem
- `/api` → api-gateway
- `/api/ws` → api-gateway WebSocket

JWT seguirá viajando en header (no hay cambio de transporte). Si la organización exige cookies httpOnly por política, se agrega un ADR que reemplace este y el gateway se adapta: ambas UIs dejan de guardar en localStorage y pasan a depender de la cookie `Set-Cookie` emitida por el gateway.

### Seguridad transversal

- CORS cerrado por orígen explícito (no `*`).
- JWT con firma rotable (HS256 en MVP, RS256 en producción) — ver ADR-013.
- Access token vence en 15 min; refresh token en 7 días.
- WebSocket valida el JWT en handshake y rechaza si está vencido o falta.
- El PIN del tótem (ADR-011) es una capa adicional específica del tótem; no reemplaza al JWT.

### Defensa en mesa redonda

"En MVP local separamos las tres piezas por puerto para simplificar el setup de cualquier desarrollador del equipo. El diseño prevé reverse proxy único en producción con path-based routing, sin cambiar cómo hablan las UIs con el gateway. JWT en header es portable entre REST y WebSocket y evita la complejidad de cookies+CSRF para un prototipo académico."

## Referencias

- ADR-001 (stack), ADR-008 (API Gateway propio), ADR-009 (cloud-agnóstico), ADR-011 (PIN tótem), ADR-013 (JWT local, SSO roadmap).
- `docs/architecture/01-stack-tecnologico.md` — stack de frontends.
- `docs/architecture/02-topologia-microservicios.md` — topología de microservicios.
- `docs/architecture/09-despliegue-uis.md` — documento extendido con el detalle práctico.
- `RNF-SEC.1`, `RNF-SEC.4`, `RNF-SEC.5` — requerimientos de seguridad cubiertos.
