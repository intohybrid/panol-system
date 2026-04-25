# ADR-001 — Stack tecnológico base

- **Estado**: Aceptada
- **Fecha**: 2026-04-15
- **Decisores**: Equipo Magíster (rol Product Owner + Architect)

## Contexto

El Caso 11 exige un stack MERN como referencia. La arquitectura propuesta es de microservicios con comunicación asíncrona, persistencia transaccional, frontend web (portal) y frontend SPA (tótem). Hay que elegir el conjunto tecnológico de partida con dos restricciones explícitas: cloud-agnóstico y compatible con la formación del equipo (Magíster en Ingeniería Informática, sin experiencia previa profunda en infraestructura cloud).

## Decisión

Adoptar como base el stack: **TypeScript + NestJS 10 (microservices) + PostgreSQL 16 + Prisma 5 + RabbitMQ 3.13 + Next.js 14 + Vite+React 18**. Detalle completo en `docs/architecture/01-stack-tecnologico.md`.

## Alternativas consideradas

- **MERN puro (Express + MongoDB)**. Cumple la letra del enunciado pero conflictúa con la naturaleza transaccional del préstamo (ACID requerido) y con la calidad de la DX (Express puro implica reinventar separación de capas). Descartada (ver ADR-002 y ADR-003).
- **JVM (Spring Boot + Camel + Kafka)**. Maduro para EIP, pero el equipo no domina Java; el costo de aprendizaje supera el beneficio para un MVP académico de 2 sprints.
- **Python/FastAPI**. Bueno para IA pero el ecosistema de microservicios con broker, outbox y EIP es menos directo que NestJS. Se conserva Python solo en el entrenamiento offline del scoring.

## Consecuencias

- TypeScript end-to-end (backend, frontend, contratos de eventos compartidos en `libs/events/`). Type safety cruza boundaries.
- NestJS aporta DI, decorators, transporte AMQP nativo y mapeo directo a EIP (`@MessagePattern` ↔ Request-Reply, `@EventPattern` ↔ Publish-Subscribe). Reduce código repetitivo de integración.
- PostgreSQL único habilita ACID donde se necesita (préstamos) sin abrir el frente de polyglot persistence en MVP.
- El monorepo con pnpm + turborepo permite builds incrementales y compartir código tipado.
- Costo: dos frameworks frontend (Next.js para portal, Vite para tótem) duplican setup pero responden a contextos distintos (SSR + SEO vs SPA fullscreen kiosko).
