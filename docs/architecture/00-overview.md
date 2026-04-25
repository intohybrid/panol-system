# Arquitectura — Visión general

## Propósito

Este documento describe la arquitectura del Sistema de Pañol a nivel conceptual. Es el punto de entrada a la carpeta `architecture/`; los documentos hermanos (`01-stack`, `02-topología`, `03-eventos-dominio`, `04-eip-catalog`, `05-saga-coreografiada`, `06-ia-mcp`) detallan cada aspecto. Los ADRs asociados viven en `docs/design/adrs/`.

## Idea central

El sistema se diseña como un conjunto de servicios pequeños e independientes que se comunican intercambiando mensajes a través de un broker central (RabbitMQ), en lugar de llamarse entre sí por HTTP. Las operaciones que involucran a varios servicios (por ejemplo, materializar una solicitud en un préstamo) se resuelven como una secuencia de eventos: cada servicio completa su parte y publica un mensaje que dispara el siguiente paso.

## Analogía con el pañol físico

La arquitectura se deja entender observando cómo funciona un pañol real en una escuela:

- Una persona atiende en ventanilla (el pañolero).
- Una bodega con estantes guarda los recursos.
- Un registro lleva los préstamos del día.
- Un coordinador revisa morosos y toma acción.

Cada rol tiene responsabilidades acotadas y ninguno invade el trabajo del otro. La coordinación ocurre mediante notas, formularios o avisos verbales — no existe una "persona central" que tome todas las decisiones. En el software, cada rol se encarna en un microservicio y las "notas" son eventos publicados en el broker de mensajes.

## Principios de diseño

1. **Desacoplamiento por eventos**. Un servicio no conoce a sus consumidores. Publica hechos; otros deciden qué hacer con ellos.
2. **Propiedad de los datos**. Cada servicio es único dueño de su esquema PostgreSQL. Ningún otro servicio accede a esas tablas; si necesita la información, la recibe como evento.
3. **Patrones de integración explícitos**. Toda integración entre servicios se implementa mediante un Enterprise Integration Pattern identificable (Publish-Subscribe, Content-Based Router, Message Expiration, Dead Letter Channel, Request-Reply). El catálogo completo está en `04-eip-catalog.md`.
4. **Consistencia eventual con outbox pattern**. Publicar un evento y persistir en la base local ocurren atómicamente mediante la tabla `outbox_events` + relay. Esto evita pérdidas de mensajes y dobles publicaciones.
5. **Expiración temporal como mecanismo de limpieza**. Las reservas de stock vencen automáticamente mediante el patrón Message Expiration. No hay job externo ni lógica imperativa de "revisar reservas vencidas".
6. **IA tratada como servicio con contrato claro**. El scoring de riesgo y el asistente conversacional son microservicios con interfaz definida. Se pueden reemplazar, desactivar o evolucionar sin impactar al flujo transaccional principal.
7. **Neutralidad respecto al proveedor cloud**. El diseño y los diagramas usan abstracciones (broker, DB, compute, object storage) que se mapean a AWS, Azure, GCP u on-prem sin cambios estructurales.
8. **Observabilidad transversal**. OpenTelemetry instrumentado en todos los servicios; el trace-id se propaga como header AMQP de modo que un flujo completo es trazable aunque atraviese seis servicios y dos frontends.

## Componentes principales

La tabla describe los nueve microservicios. El detalle de comunicación y datos vive en `02-topologia-microservicios.md`.

| Servicio | Responsabilidad | Ejemplos de eventos publicados |
|---|---|---|
| `auth-svc` | Usuarios, roles, autenticación, emisión de JWT. | `user.created`, `user.blocked` |
| `inventory-svc` | Catálogo de recursos, stock, umbrales de alerta, bajas. | `stock.changed`, `stock.low`, `stock.lost` |
| `request-svc` | Solicitudes on-line de alumnos y docentes. | `request.created`, `request.cancelled`, `request.expired` |
| `loan-svc` | Préstamos efectivos y devoluciones. Núcleo transaccional. | `loan.issued`, `loan.returned`, `loan.overdue` |
| `notification-svc` | Notificaciones in-app, bandeja persistente, ticket PDF. | `notification.delivered` |
| `ai-risk-svc` | Scoring de riesgo de morosidad por usuario y recurso. | `risk.scored` |
| `ai-assistant-svc` | Asistente conversacional (servidor MCP + cliente OpenAI). | `assistant.suggested` |
| `reports-svc` | Read-model consumer puro (CQRS). Proyecciones desnormalizadas para reportes de gestión. | — (no publica eventos de dominio) |
| `api-gateway` | BFF HTTP/WebSocket entre frontends y los servicios internos. | — |

## Flujo principal: solicitud a préstamo

El siguiente flujo es el corazón funcional del sistema y es el caso que demuestra casi todos los patrones de integración en acción.

1. El alumno crea una solicitud desde el portal web para los recursos que necesita.
2. `request-svc` valida disponibilidad consultando a `inventory-svc` (Request-Reply sobre AMQP) y consulta a `ai-risk-svc` para obtener el score de riesgo. Si el score y la blacklist lo permiten, crea la solicitud y emite `request.created`, que lleva asociada una reserva de stock con TTL configurable (por defecto 4 horas).
3. `inventory-svc` reacciona a `request.created` reservando el stock sin descontarlo.
4. El alumno se presenta en el pañol antes de que expire el TTL. El pañolero abre el tótem, ubica la solicitud por RUT o ID y la valida. `loan-svc` crea el préstamo y emite `loan.issued`. `inventory-svc` descuenta definitivamente el stock reservado. `notification-svc` genera el ticket PDF y lo entrega como notificación in-app al alumno.
5. El alumno devuelve los recursos. El pañolero registra la devolución. `loan-svc` emite `loan.returned`. `inventory-svc` reabre el stock; si hay faltante o daño, se registra el evento `stock.lost` con ajuste de baja.

El caso de compensación ocurre cuando el alumno no se presenta en el pañol antes del TTL: la reserva expira automáticamente, `request-svc` emite `request.expired`, `inventory-svc` libera el stock reservado y `loan-svc` no hace nada porque nunca hubo préstamo. Este comportamiento es lo que implementa la Saga coreografiada y el patrón Message Expiration de forma coordinada. Detalle en `05-saga-coreografiada.md`.

## Alcance del MVP

El MVP funcional cubre los flujos de los nueve servicios en modo single-sede, con autenticación local JWT y notificaciones in-app. No incluye:

- SSO federado (Keycloak / Entra ID / Google Workspace).
- Escaneo de QR o código de barras con periféricos en el tótem.
- Operación multi-sede con réplicas por escuela.
- Envío de correo electrónico (in-app only).
- Polyglot persistence (MongoDB para catálogo + PostgreSQL para transaccional).

Cada uno de estos tiene su ADR asociado (`docs/design/adrs/`) que documenta la razón de la exclusión y los pasos necesarios para incorporarlo en fases posteriores.
