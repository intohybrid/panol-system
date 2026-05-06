-- ─────────────────────────────────────────────────────────────────────────
-- Sistema de Pañol — bootstrap de bases de datos por microservicio
--
-- Cada microservicio que requiere persistencia transaccional tiene su propia
-- base PostgreSQL (database-per-service). Polyglot persistence con MongoDB
-- queda fuera del MVP (ADR-002).
--
-- Bases creadas:
--   1. auth_db          — usuarios, roles, credenciales (auth-svc)
--   2. inventory_db     — recursos, stock, reservas, movimientos (inventory-svc)
--   3. request_db       — solicitudes, drafts, aprobaciones (request-svc)
--   4. loan_db          — préstamos, devoluciones, atrasos (loan-svc)
--   5. notification_db  — notificaciones in-app, tickets PDF (notification-svc)
--   6. ai_risk_db       — perfiles de riesgo, scoring log, modelos (ai-risk-svc)
--   7. ai_assistant_db  — conversaciones, turns, mapping de actividades (ai-assistant-svc)
--   8. reports_db       — proyecciones CQRS read-only (reports-svc, ADR-015)
--
-- Ver `docs/architecture/10-modelo-datos.md` para detalle de tablas y
-- relaciones (ERD-01-modelo-datos.drawio).
--
-- Este script corre automáticamente al iniciar el contenedor postgres por
-- primera vez (volumen vacío). Para re-ejecutarlo: `docker compose down -v`
-- y volver a levantar.
-- ─────────────────────────────────────────────────────────────────────────

CREATE DATABASE auth_db;
CREATE DATABASE inventory_db;
CREATE DATABASE request_db;
CREATE DATABASE loan_db;
CREATE DATABASE notification_db;
CREATE DATABASE ai_risk_db;
CREATE DATABASE ai_assistant_db;
CREATE DATABASE reports_db;

-- Permisos: el usuario panol ya es OWNER de todas las bases creadas con su
-- rol. No se requieren GRANTS adicionales para desarrollo local.
