# ADR-006 — Saga coreografiada en lugar de orquestada

- **Estado**: Aceptada
- **Fecha**: 2026-04-17
- **Decisores**: Equipo Magíster

## Contexto

La transacción distribuida central del sistema (solicitud → reserva → préstamo → devolución) atraviesa cuatro a cinco microservicios con bases de datos separadas. ACID 2PC entre cuatro Postgres no es viable. Hay que elegir una estrategia de saga: coreografiada (cada servicio reacciona a eventos) u orquestada (un componente central dirige la saga).

## Decisión

Implementar **saga coreografiada** sobre RabbitMQ usando outbox pattern + Publish-Subscribe + Message Expiration. Sin orquestador central. Detalle del flujo en `docs/architecture/05-saga-coreografiada.md`.

## Alternativas consideradas

### Saga orquestada con motor (Temporal)

- **Fortalezas**: La saga vive en un solo lugar (el workflow); fácil de leer, mantener, debuggear. Reintentos, timeouts, compensaciones declarativas. Visualización de estado en tiempo real.
- **Debilidades para este caso**:
  - Agrega un componente operacional adicional (servidor Temporal, cluster, persistencia propia).
  - Curva de aprendizaje del SDK Temporal y de su modelo de programación.
  - El flujo principal del sistema es lineal, sin ramificaciones complejas. Temporal brilla cuando hay ramas, esperas largas (días), human-in-the-loop, retry policies sofisticadas. Aquí no.
  - Se aleja del stack y de la rúbrica, que valora EIP nativos del broker.

### Saga orquestada con máquina de estados manual

- **Fortalezas**: Sin componente nuevo; un servicio (`request-svc` o un nuevo `saga-orchestrator`) implementa la máquina.
- **Debilidades**: Reinvención. Toda la complejidad de Temporal sin los beneficios. Acopla a un punto único de falla.

### Saga coreografiada (la elegida)

- **Fortalezas**:
  - Se apoya en infraestructura ya elegida (broker + outbox).
  - Patrones EIP de Hohpe materializados naturalmente.
  - Sin componente nuevo, sin lock-in.
  - El equipo lo entiende sin entrenamiento adicional.
- **Debilidades**:
  - La saga "no vive en un solo lugar". Compensa el documento `05-saga-coreografiada.md` y los diagramas de secuencia (tarea #8 del backlog).
  - Compensaciones distribuidas: cada servicio implementa la suya en respuesta a eventos de otros.
  - Reconciliación nocturna obligatoria para detectar estados inconsistentes ante fallos no recuperados (DLQ). Acepta este costo.

## Consecuencias

- Sin orquestador. Cada servicio reacciona a eventos publicados.
- Outbox pattern obligatorio en cada publisher para garantizar atomicidad cambio-evento.
- Idempotencia obligatoria en cada consumer (tabla `processed_events`).
- Compensaciones explícitas donde corresponde (TTL expira → liberar reserva; devolución parcial → ajustar stock).
- Documentación de la saga es el contrato: si alguien quiere entender el flujo, lee el documento, no busca un workflow file.
- Si el negocio crece a flujos con ramas o human-in-the-loop, se reevalúa migrar a Temporal sin reescribir el dominio: los handlers actuales seguirían existiendo, Temporal solo coordinaría su invocación.
