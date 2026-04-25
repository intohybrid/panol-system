# ADR-005 — RabbitMQ en lugar de Kafka

- **Estado**: Aceptada
- **Fecha**: 2026-04-16
- **Decisores**: Equipo Magíster

## Contexto

La arquitectura es asíncrona basada en eventos. Hay que elegir el broker de mensajes. Las dos opciones serias en 2026 son RabbitMQ (broker tradicional, AMQP 0.9.1) y Apache Kafka (log distribuido). Cada uno tiene fortalezas diferentes; la decisión depende del perfil de carga, el patrón de uso y la familiaridad del equipo.

## Decisión

Adoptar **RabbitMQ 3.13** con plugins `rabbitmq_delayed_message_exchange` y `rabbitmq_shovel`.

## Alternativas consideradas

### Kafka

- **Fortalezas**: alta tasa de throughput, retención larga del log, replay nativo, particionamiento horizontal trivial.
- **Debilidades para este caso**:
  - El sistema tiene volumen bajo a moderado (cientos de eventos por hora en producción inicial). Kafka es overkill.
  - Patrón Request-Reply es más natural en AMQP que en Kafka (donde requiere topics adicionales y correlación manual).
  - Patrón Message Expiration con TTL configurable por mensaje no es nativo de Kafka. Requiere lógica aplicativa o herramientas externas.
  - Operativamente más caro: Zookeeper o KRaft, particionamiento, retención, consumidores con offset propio.
  - El equipo tiene curva de aprendizaje real.

### NATS

- **Fortalezas**: Simple, rápido, JetStream agrega persistencia.
- **Debilidades**: Ecosistema NestJS menos maduro que con AMQP. No tiene tanta literatura sobre EIP. Menor adopción en empresas chilenas (relevante para defensa académica).

### Redis Streams

- **Fortalezas**: Si Redis ya está en el stack para cache, no agrega componente.
- **Debilidades**: Ni el equipo ni el caso requieren Redis; agregarlo solo para mensajería es introducir un componente que va a hacer dos trabajos a medias.

## Decisión justificada

RabbitMQ es **el broker de manual** para EIP de Hohpe:

- Topic exchanges → Publish-Subscribe + Content-Based Router de forma declarativa.
- TTL por mensaje y delayed message exchange → Message Expiration sin job externo.
- Dead letter exchange → Dead Letter Channel nativo.
- `replyTo` + `correlationId` → Request-Reply estándar.
- Mapeo 1:1 con NestJS (`@MessagePattern`, `@EventPattern`).

Tener un broker que materializa los patrones que el sistema usa, sin glue code, es la razón principal. Para un MVP académico que evidencia EIP, el costo operativo de Kafka no se justifica.

## Consecuencias

- Topología clara: 4 exchanges (`domain.events`, `domain.commands`, `domain.delayed`, `domain.dlx`) cubren todo el sistema.
- Plugin `delayed-message` instala el exchange `x-delayed-message` que implementa el TTL de reservas (RC.06) sin código.
- En producción de mayor volumen, RabbitMQ con quorum queues y clustering basta; si en algún momento el volumen exige Kafka, la separación de responsabilidades por evento permite reemplazar el broker sin tocar la lógica de dominio (los handlers están en NestJS, son agnósticos del transporte concreto).
- La defensa en mesa redonda es directa: "RabbitMQ porque los patrones del libro de Hohpe son patrones nativos del broker".
