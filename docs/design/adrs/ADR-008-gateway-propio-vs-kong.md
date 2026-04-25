# ADR-008 — API Gateway propio en NestJS en lugar de Kong/Traefik

- **Estado**: Aceptada para MVP
- **Fecha**: 2026-04-18
- **Decisores**: Equipo Magíster

## Contexto

El sistema necesita un punto de entrada único para portal web y tótem. El Gateway debe: validar JWT, enrutar a los servicios internos, exponer WebSocket para notificaciones push, agregar datos de varios servicios cuando convenga (BFF), aplicar rate-limit. Hay tres caminos: usar un API Gateway dedicado (Kong, Traefik, Apigee, KrakenD), construirlo como un NestJS más, o no tener gateway y dejar que las UIs hablen directo con cada servicio.

## Decisión

Construir un **`api-gateway` propio en NestJS**, parte del mismo monorepo, que actúa como BFF (Backend for Frontends). HTTP para comandos y queries hacia los servicios internos, WebSocket (Socket.IO) hacia las UIs.

## Alternativas consideradas

### Kong

- **Fortalezas**: Producto maduro, gestión de plugins, dashboard, rate-limit declarativo.
- **Debilidades**: Componente operativo adicional (plus su BD Postgres); plugins complejos; no es un BFF (no agrega datos), por lo que de todas formas habría que poner un BFF detrás.

### Traefik

- **Fortalezas**: Liviano, descubrimiento dinámico vía Docker labels.
- **Debilidades**: Mismas que Kong en términos de "no es BFF". Bueno como reverse proxy puro, no como capa de adaptación al frontend.

### KrakenD / Tyk / Express Gateway

- Similar tradeoff. Aporta poco para el MVP académico y suma componente nuevo.

### Sin gateway (UIs directo a servicios)

- **Pros**: Menos código.
- **Contras**: CORS por servicio, JWT validation por servicio, exposición de la topología interna al cliente, imposibilidad de agregar datos de varios servicios para una vista única (lo cual sí necesita el portal).

## Decisión justificada

Un BFF propio en NestJS resuelve los tres requisitos en un solo lugar:

1. **Punto único de validación JWT y rate-limit**. Los servicios internos confían en el header `x-user-id` que el gateway inyecta.
2. **Composición de respuestas**. Por ejemplo, el dashboard del portal trae `historial + reservas activas + score` agregando 3 servicios; el gateway compone la respuesta y la UI hace una sola llamada.
3. **WebSocket en un único host**. El portal abre un solo WebSocket; el gateway recibe eventos del broker y los re-emite a la UI correcta.

Costo: un servicio más que mantener. Beneficio: UI simple, topología interna oculta, capa donde aplicar policy transversal (auth, rate-limit, audit).

Kong/Traefik se reconsideran cuando aparezcan necesidades específicas (gestión de partners externos, rate-limit por API key, plugins de seguridad complejos). En MVP no aplica.

## Consecuencias

- `apps/api-gateway/` en el monorepo, mismo stack y operaciones.
- Servicios internos no exponen HTTP al exterior; hablan AMQP entre sí y HTTP solo al gateway.
- En producción, el gateway corre detrás de un load balancer (cloud-agnóstico: ALB, Application Gateway, Cloud Load Balancer, o nginx en on-prem).
- Si se agrega una segunda UI (app móvil, integración con SIS), se evalúa si comparte el mismo BFF o se crea uno nuevo (BFF "uno por front" es un patrón válido).
- La defensa: "el gateway no es solo proxy; es adaptación al frontend (BFF) y cabe en el stack sin sumar pieza nueva".
