# ADR-004 — Microservicios en lugar de monolito modular

- **Estado**: Aceptada
- **Fecha**: 2026-04-16
- **Decisores**: Equipo Magíster

## Contexto

El sistema cubre 7 dominios funcionales claramente diferenciables (auth, inventory, request, loan, notification, ai-risk, ai-assistant) más un BFF (api-gateway). La rúbrica valora el uso de Enterprise Integration Patterns y la elección arquitectónica con justificación. Hay dos caminos viables:

1. **Monolito modular**. Un solo proyecto con módulos NestJS bien delimitados internamente, una sola base de datos, un solo despliegue.
2. **Microservicios**. Cada dominio en su propio servicio, base de datos privada por servicio, comunicación por broker.

## Decisión

Diseñar como **8 microservicios independientes** con comunicación asíncrona vía RabbitMQ y persistencia separada por servicio.

## Alternativas consideradas

### Monolito modular (la alternativa principal)

- **Pros**: Operación más simple en MVP (un despliegue, un Postgres, un proceso). Transacciones ACID intra-monolito sin saga.
- **Contras**: La rúbrica del trabajo final exige evidencia explícita de EIP. Un monolito puede usar internamente Publish-Subscribe (event bus en memoria) pero pierde el sentido del patrón, que es desacoplar deployables y permitir escalamiento independiente. EIP se apoya genuinamente en separación física.

### Microservicios sin broker (HTTP punto-a-punto)

- **Pros**: Familiar.
- **Contras**: Acoplamiento implícito por URL conocida, fragilidad ante caídas, lógica de retry/timeout repetida en cada cliente. Pierde Publish-Subscribe nativo. No queda claro qué patrón EIP se demuestra.

### Serverless (FaaS por dominio)

- **Pros**: Escalamiento automático y costo cero en reposo.
- **Contras**: Cold start incompatible con timeout estricto del scoring. Vendor lock-in contradice el principio cloud-agnóstico.

## Decisión justificada

Microservicios + RabbitMQ es la opción que mejor demuestra los patrones que la rúbrica evalúa. El costo operativo en MVP se contiene con docker-compose para desarrollo y un único nodo en producción inicial. La separación en 8 servicios sigue criterio de bounded context (cada servicio tiene un cambio independiente, data ownership, lenguaje ubicuo propio).

## Consecuencias

- 8 servicios desplegables independientes. CI/CD por servicio.
- Cada servicio dueño de su esquema PostgreSQL; la información atraviesa boundaries solo como eventos.
- Saga coreografiada para transacciones distribuidas (ADR-006).
- Outbox pattern obligatorio en cada publisher para atomicidad.
- Costo operativo más alto: 8 procesos vs 1, monitoreo más complejo, debugging distribuido.
- La separación habilita escalado por servicio: `notification-svc` y `ai-assistant-svc` tienen patrones de carga distintos al resto.
- Se acepta consistencia eventual donde antes habría ACID inter-módulo.
