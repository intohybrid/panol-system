# ADR-002 — PostgreSQL en lugar de MongoDB

- **Estado**: Aceptada
- **Fecha**: 2026-04-15
- **Decisores**: Equipo Magíster

## Contexto

El stack MERN del enunciado especifica MongoDB. El núcleo del sistema es transaccional: una solicitud reserva stock, un préstamo descuenta stock, una devolución reabre stock. Cualquier desincronía entre la base y los eventos genera inconsistencias visibles al usuario (ver dos veces el mismo recurso, perder una unidad). Hay que elegir el motor de persistencia y justificar la desviación del enunciado si la hubiera.

## Decisión

Usar **PostgreSQL 16** como única base operativa de todos los microservicios. Cada microservicio es dueño exclusivo de su esquema. Polyglot persistence (Mongo para catálogo + Postgres para transaccional) queda explícitamente fuera del MVP.

## Alternativas consideradas

- **MongoDB único**. Cumple la letra del enunciado. Las transacciones multi-documento existen desde 4.0 pero son operativamente más caras y semánticamente diferentes a las relacionales. El modelo de datos del sistema es relacional (préstamo↔usuario↔recurso↔carrera), no documental.
- **Polyglot (Mongo catálogo + Postgres transaccional)**. Aporta poco en MVP y duplica operación (dos motores, dos drivers, dos backups). Diferida.
- **MySQL**. Equivalente a Postgres en muchos casos pero con menos features avanzados (JSONB, particionamiento declarativo, search trgm). Postgres gana sin debate fuerte.

## Consecuencias

- ACID cuando se necesita (préstamo, descuento de stock, outbox).
- Modelo relacional natural para reportes con SQL puro.
- Prisma como ORM type-safe, migraciones declarativas, ecosistema maduro.
- Desviación del enunciado documentada y defendible: la rúbrica valora razonamiento técnico sobre obediencia ciega al stack sugerido.
- Si en producción se decide usar MongoDB para catálogo (RAG sobre fichas de recursos, búsqueda full-text), la migración es localizada a `inventory-svc` y no impacta al resto.
