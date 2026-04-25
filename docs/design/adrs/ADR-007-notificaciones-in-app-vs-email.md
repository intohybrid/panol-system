# ADR-007 — Notificaciones in-app en lugar de email

- **Estado**: Aceptada para MVP
- **Fecha**: 2026-04-17
- **Decisores**: Equipo Magíster

## Contexto

El Caso 11 menciona "alertas" y "tickets" sin especificar el canal. La interpretación natural en sistemas universitarios es correo electrónico. La integración con SMTP institucional o un servicio transaccional (SendGrid, SES) es operativamente sencilla, pero introduce dependencia externa, costos por volumen y un componente regulatorio adicional (Ley 19.628 al manejar direcciones de email persistentemente).

## Decisión

En el MVP, todas las notificaciones (creación de solicitud, ticket de préstamo, ticket de devolución, alerta de morosidad, alerta de stock bajo, bloqueo automático) se entregan **in-app**: persistidas en la bandeja del usuario en `notification-svc` y empujadas en tiempo real vía WebSocket a las UIs (portal y tótem). Los tickets son PDF descargables desde la bandeja, generados con PDFKit.

El email queda fuera del MVP, registrado como evolución natural en el roadmap.

## Alternativas consideradas

### Email transaccional desde el inicio

- **Pros**: Cubre el canal que el usuario probablemente espera. No requiere que el alumno entre al portal para ver notificaciones.
- **Contras**:
  - Dependencia de SMTP institucional (cuotas, configuración, autoritzación) o de un proveedor transaccional (costo, vendor).
  - Direcciones de email son dato personal (Ley 19.628), exigen políticas de retención y consentimiento explícitas.
  - Bounce rate, deliverability, lista de bloqueo: complejidades operativas que no aportan al objetivo del trabajo final.
  - El portal ya es un canal capturado: el alumno entra para crear la solicitud, puede ver la notificación al volver.

### Notificación push (FCM, APNs)

- **Pros**: Mejor UX que email para alertas urgentes.
- **Contras**: Requiere app móvil (no hay en MVP), credenciales de proveedor, vendor lock-in.

### SMS

- **Pros**: Universal.
- **Contras**: Costo por mensaje, integración con un proveedor regional, sobreingeniería para un MVP académico.

## Decisión justificada

El portal y el tótem son los dos canales activos del MVP. El alumno entra al portal para crear la solicitud y para ver historial; la notificación in-app encaja en su flujo natural. WebSocket sobre el API Gateway entrega en tiempo real cuando la sesión está abierta; al re-abrir la app, la bandeja persistente muestra lo no leído.

Email es deuda técnica controlada: la arquitectura ya separa `notification-svc` como adaptador de canal. Agregar email después es agregar un consumer en ese servicio, no rediseñar.

## Consecuencias

- `notification-svc` implementa solo el canal IN_APP en MVP. La interfaz `NotificationChannel` está diseñada para que canales adicionales (EMAIL, SMS, PUSH) sean implementaciones nuevas sin tocar el resto.
- WebSocket sobre Socket.IO en el API Gateway. Bandeja en Postgres con TTL configurable (90 días por defecto).
- Tickets PDF en `notification-svc` con PDFKit; descargables desde la bandeja.
- En el roadmap: agregar SMTP institucional como segundo canal usando el mismo evento `notification.delivered` derivado.
- La defensa en mesa redonda: "in-app sale del flujo natural del usuario y evita acoplar el MVP a un proveedor externo; email es upgrade no rediseño".
