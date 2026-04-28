# ADR-015 — Reports-svc como microservicio dedicado con read-model propio (CQRS)

- **Estado**: Aceptada
- **Fecha**: 2026-04-25
- **Decisores**: Equipo Magíster

## Contexto

`RF.9b` y `RF.13` exigen reportes de gestión (stock disponible, recursos más y menos solicitados, devoluciones fuera de plazo, tasas de pérdida) consumibles por el Jefe de Carrera y el Coordinador. Los datos necesarios están repartidos entre `inventory-svc` (catálogo, stock, bajas), `loan-svc` (préstamos, devoluciones, atrasos), `request-svc` (solicitudes, cancelaciones, expiraciones) y `ai-risk-svc` (scores y drivers, para auditoría del modelo).

Las opciones para servir estos reportes son tres:

1. Ejecutar joins cross-servicio consultando a cada uno por HTTP/AMQP en tiempo de query. Rompe la regla "no BD de otro servicio" y exige que cada servicio exponga APIs de lectura ricas, mezclando su API transaccional con queries analíticas.
2. Replicar la lógica en cada servicio ("cada uno tiene sus propios reportes"). Esto fragmenta reporting, obliga al usuario a visitar varios endpoints para una visión consolidada y duplica cálculos.
3. Construir un servicio dedicado que consuma eventos de dominio y mantenga sus propias tablas desnormalizadas optimizadas para lectura analítica.

El documento `04-eip-catalog.md` ya describe una arquitectura event-driven con outbox, Pub-Sub y entrega "al menos una vez". Hay infraestructura para alimentar un read-model sin construir nada nuevo.

## Decisión

Se incorpora un **noveno microservicio**: `reports-svc`, que actúa como **read-model consumidor puro** bajo el patrón CQRS:

- Consume eventos de dominio desde `domain.events` (topic `#`, o patrones específicos por proyección).
- Mantiene su propia base de datos PostgreSQL con **tablas desnormalizadas** optimizadas para queries analíticas (agregados precalculados, índices específicos).
- Expone queries HTTP (vía API Gateway) para los reportes definidos en `RF.13`: stock disponible/no disponible, recursos más/menos solicitados por período, devoluciones fuera de plazo por recurso y por usuario, recursos con más pérdidas/bajas.
- **No publica eventos de dominio propios**. Es un sink.
- **No tiene lógica de negocio compleja**: traduce eventos en actualizaciones de proyección y sirve queries pre-calculadas.

La eventual consistencia de los reportes es aceptable (ventana de segundos), y se documenta como característica esperada del diseño.

## Alternativas consideradas

### Joins cross-servicio en tiempo de query

- **Pros**: sin duplicación de datos; los reportes reflejan estado en tiempo real.
- **Contras**: acopla a los servicios transaccionales con responsabilidades de reporting. Rompe data ownership. Cada servicio debe exponer APIs analíticas que compiten con su API transaccional. Queries distribuidas son lentas y frágiles. Imposible de auditar ("¿qué datos había cuando se corrió el reporte ayer?").

### Reportes embebidos en cada servicio

- **Pros**: sin nuevo servicio.
- **Contras**: fragmenta el reporting. No hay cruces útiles ("recursos más solicitados por carrera" cruza `request-svc` y `auth-svc`). Duplica cálculos de agregados. Expone en cada servicio endpoints analíticos que ensucian su API de dominio.

### Data warehouse / OLAP separado (Metabase, Cube.js, Superset)

- **Pros**: herramienta visual rica; dashboards sin código.
- **Contras**: sobreingeniería para MVP. Introduce ETL, scheduling y una BI stack completa. No aporta más que el read-model servido por NestJS para los 4-5 reportes especificados. Queda en roadmap si el sistema crece.

### Read-model embebido en un servicio existente (`loan-svc`)

- **Pros**: no agrega servicio.
- **Contras**: mezcla responsabilidades. `loan-svc` es transaccional crítico; darle el rol de reporting consume recursos, rompe aislamiento y complica escalado independiente (los reportes de fin de mes no deberían pausar emisión de préstamos).

## Decisión justificada

Un read-model dedicado es la aplicación canónica de CQRS en una arquitectura event-driven. El costo de agregar un microservicio consumer-only es bajo (comparte plantilla hexagonal, DB propia, docker-compose profile); el beneficio es:

- **Data ownership preservada**: cada servicio transaccional sigue siendo dueño exclusivo de sus tablas. `reports-svc` solo observa eventos.
- **Independencia operativa**: los reportes se escalan, optimizan y mantienen sin tocar los servicios transaccionales.
- **Auditabilidad**: cada proyección puede reconstruirse reproduciendo el stream de eventos desde cero (event replay).
- **Punto defensible en la rúbrica**: CQRS es un patrón mencionado explícitamente en la literatura de Hohpe (separación de canales de command y query) y articula bien con la saga coreografiada.

## Consecuencias

### Servicios

- `reports-svc` se agrega a `apps/reports-svc/` siguiendo la plantilla hexagonal.
- Su `schema.prisma` incluye tablas desnormalizadas:
  - `reporte_stock` — stock actual por recurso con flag disponible/no disponible.
  - `reporte_solicitudes_recurso` — agregado de solicitudes por recurso y por período.
  - `reporte_devoluciones_tardias` — desnormalización de préstamos cerrados con atraso, agrupable por recurso o por usuario.
  - `reporte_perdidas_recurso` — agregado de `stock.lost` y bajas por recurso.
  - `proyeccion_usuarios` — copia lean de usuarios (documento, nombre, carrera) para joins locales sin salir del servicio.
- Consume los eventos: `stock.changed`, `stock.lost`, `request.created`, `request.cancelled`, `request.expired`, `loan.issued`, `loan.returned`, `loan.overdue`, `user.created`, `user.blocked`, `user.unblocked`, `risk.scored`.

### API Gateway

- Expone queries HTTP nuevas: `GET /reports/stock`, `GET /reports/recursos-top`, `GET /reports/devoluciones-tardias`, `GET /reports/perdidas`. Todas protegidas por RBAC (solo Jefe y Coordinador).

### Consistencia

- Los reportes son **eventualmente consistentes**. Ventana esperada: < 2 s bajo carga normal, < 30 s bajo carga alta. La UI del portal debe indicar "actualizado hace N segundos" cuando corresponda.
- Event replay para reconstruir proyecciones: script administrativo que vacía y re-consume desde el broker o desde los outbox de cada servicio.

### Reentrenamiento de modelos

- `reports-svc` es también la fuente natural de datos para reentrenar `ai-risk-svc`: exporta un dataset etiquetado (préstamos cerrados con flag de atraso/pérdida) que alimenta el entrenamiento offline.

### Observabilidad

- Lag de proyección instrumentado con métrica `reports_projection_lag_seconds` (diferencia entre `publishedAt` del evento y su procesamiento en `reports-svc`). Alerta si > 60 s.

### Defensa en mesa redonda

- "Reports es CQRS aplicado al dominio: command-side son los microservicios transaccionales; query-side es `reports-svc` con proyecciones dedicadas. Separa escalamiento, preserva data ownership y deja un camino natural hacia BI".
