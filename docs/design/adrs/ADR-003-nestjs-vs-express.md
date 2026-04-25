# ADR-003 — NestJS en lugar de Express puro

- **Estado**: Aceptada
- **Fecha**: 2026-04-15
- **Decisores**: Equipo Magíster

## Contexto

El stack MERN del enunciado sugiere Express como framework backend. El sistema se diseña como 8 microservicios con comunicación AMQP, outbox, validación tipada y observabilidad transversal. Express puro es minimalista y obliga a construir desde cero lo que en frameworks "opinados" viene resuelto: estructura de capas, inyección de dependencias, integración con transporte AMQP, validación de schemas, decoradores de routing.

## Decisión

Adoptar **NestJS 10** como framework backend para todos los microservicios. Express queda como motor HTTP por debajo (NestJS lo usa internamente), pero el código aplicativo no toca Express directamente.

## Alternativas consideradas

- **Express puro**. Cumple el enunciado pero exige que el equipo invente convenciones internas (estructura, DI, transport adapters), lo que en 2 sprints de MVP es deuda inmediata.
- **Fastify directo**. Más rápido que Express en benchmarks; el equipo no lo conoce y no se justifica el aprendizaje.
- **Hono / Elysia**. Modernos y livianos; ecosistema de microservicios con AMQP menos maduro que NestJS.
- **Koa**. Sucesor "natural" de Express, similar tradeoff. Ningún beneficio concreto para este caso.

## Consecuencias

- Estructura de capas modular (Module / Controller / Service / Repository) consistente entre los 8 servicios. Onboarding y revisión cruzada baratos.
- Soporte nativo de transporte AMQP con `@nestjs/microservices`. `@MessagePattern` y `@EventPattern` se mapean directo a Request-Reply y Publish-Subscribe (EIP).
- DI integrada permite testabilidad alta (mockear dependencias, módulos de testing).
- Validación con `class-validator` o Zod (preferido por equipo) en cada DTO.
- OpenTelemetry tiene módulos integradores con NestJS.
- Costo: NestJS añade abstracción que un Express puro no tiene. El argumento "Express es más simple" es real pero engañoso a escala de 8 servicios; cada servicio debería re-implementar esa abstracción.
- La rúbrica valora arquitectura limpia y patrones explícitos. NestJS facilita exponer eso sin código boilerplate.
