# Trazabilidad

## Propósito

Matriz de trazabilidad del sistema. Conecta RF y RS con casos de uso, roles que los ejecutan, reglas de negocio que aplican y servicios que los implementan. Es un documento vivo: cada user story del backlog debe poder enlazarse a al menos un RF.

---

## Matriz RF ↔ CU ↔ Rol ↔ Servicio ↔ Regla

### Requerimientos originales del Caso 11

| RF | Nombre corto | CU | Rol principal | Servicio | Reglas |
|---|---|---|---|---|---|
| RF.1 | Autenticación | CU1 | Todos | `auth-svc` | RC.04, RC.13 |
| RF.2 | Administrar usuarios admin | CU2 | Jefe | `auth-svc` | RC.08 |
| RF.3 | Administrar alumnos/docentes | CU2 | Coordinador, Jefe | `auth-svc` | RC.04 |
| RF.4 | Administrar inventario | CU3 | Pañolero, Jefe | `inventory-svc` | RC.03, RC.09, RC.18 |
| RF.5 | Crear solicitud web | CU4 | Alumno, Docente | `request-svc` | RC.16 |
| RF.6 | Consultar/validar solicitud | CU5 | Pañolero | `request-svc`, `loan-svc` | RC.16 |
| RF.7 | Materializar solicitud en préstamo | CU5 | Pañolero | `loan-svc` | RC.07, RC.17 |
| RF.8 | Registrar préstamos/devoluciones | CU5 | Pañolero | `loan-svc`, `inventory-svc` | RC.07, RC.17 |
| RF.9 | Consultar préstamos del día | CU5, CU7 | Pañolero, Coordinador | `loan-svc` | N/A |
| RF.9b | Reportes por perfil | CU7 | Jefe, Coordinador, Pañolero | `loan-svc`, `inventory-svc` | N/A |
| RF.10 | Ticket de respaldo | CU5 | Sistema | `notification-svc` | RC.07 |
| RF.11 | Alerta de morosos | CU6 | Sistema | `notification-svc` | RC.01 |
| RF.12 | Alerta de stock bajo | CU6 | Sistema | `notification-svc`, `inventory-svc` | RC.05 |
| RF.13 | Reportes de gestión | CU7 | Jefe, Coordinador | `inventory-svc`, `loan-svc` | RC.05, RC.17 |
| RF.14 | Bloqueo automático de morosos | CU5, CU6 | Sistema | `loan-svc`, `auth-svc` | RC.01 |

### Requerimientos complementarios

| RF | Nombre corto | CU | Rol principal | Servicio | Reglas |
|---|---|---|---|---|---|
| RF-C.01 | Reserva con TTL | CU4 | Sistema | `request-svc`, `inventory-svc` | RC.06, RC.16 |
| RF-C.02 | Scoring de riesgo | CU4 | Sistema | `ai-risk-svc`, `request-svc` | RC.11 |
| RF-C.03 | Asistente conversacional | CU4b | Alumno, Docente | `ai-assistant-svc` | RC.15 |
| RF-C.04 | Workflow con blacklist | CU4 | Sistema | `request-svc`, `auth-svc` | RC.01, RC.10, RC.11 |
| RF-C.05 | Préstamo Especial multi-día | CU4c | Jefe, Coordinador | `request-svc`, `loan-svc` | RC.02 |
| RF-C.06 | Préstamo parcial | CU5 | Pañolero | `loan-svc`, `inventory-svc` | N/A |
| RF-C.07 | Estados de devolución | CU5 | Pañolero | `loan-svc`, `inventory-svc` | RC.17, RC.18 |
| RF-C.08 | Estado En Mantención | CU3 | Pañolero, Jefe | `inventory-svc` | RC.18 |
| RF-C.09 | PIN de acciones sensibles | CU4, CU5 | Pañolero | `auth-svc` (valida PIN) | RC.14 |
| RF-C.10 | Cambio obligatorio de clave | CU1 | Todos | `auth-svc` | RC.13 |
| RF-C.11 | Historial personal | CU4 | Alumno, Docente | `request-svc`, `loan-svc` | N/A |
| RF-C.12 | ID sin RUT chileno | CU2 | Coordinador, Jefe | `auth-svc` | RC.04 |
| RF-C.13 | Solicitud en nombre de otro usuario | CU4 | Pañolero, Coordinador | `request-svc`, `auth-svc` | RC.16 |

---

## Matriz RS ↔ RF ↔ Rol

### Requerimientos generales

| RS | Nombre corto | RF | Rol |
|---|---|---|---|
| RS.1 | Alertas de stock | RF.12 | Sistema |
| RS.2 | Ticket automático | RF.10 | Sistema |
| RS.3 | Saludo personalizado | RF.1 | Todos |
| RS.4 | Cierre por inactividad | RF.1 | Todos excepto Pañolero |

### Por rol

| Rol | RS | Descripción |
|---|---|---|
| Jefe de Carrera | RS-JC.1 a RS-JC.5 | Crear usuarios, dar de baja, administrar inventario, reportes, configurar parámetros. |
| Coordinador | RS-CC.1 a RS-CC.4 | Crear alumnos, importar Excel, bloquear morosos, reportes. |
| Pañolero | RS-PN.1 a RS-PN.6 | Inventario, reportes diarios, préstamos, devoluciones, anulaciones, bloqueo de alumnos. |
| Docente y Alumno | RS-DA.1 a RS-DA.3 | Crear solicitud, asistente, historial. |

---

## Matriz Servicio ↔ RF (vista desde la arquitectura)

Indica qué RF implementa cada microservicio. Apoya la distribución de trabajo entre los dos equipos Feature (LeSS).

| Servicio | RF implementados |
|---|---|
| `auth-svc` | RF.1, RF.2, RF.3, RF.14, RF-C.04, RF-C.09, RF-C.10, RF-C.12, RF-C.13 |
| `inventory-svc` | RF.4, RF.9b, RF.12, RF.13, RF-C.01, RF-C.06, RF-C.07, RF-C.08 |
| `request-svc` | RF.5, RF.6, RF-C.01, RF-C.02, RF-C.04, RF-C.05, RF-C.11, RF-C.13 |
| `loan-svc` | RF.7, RF.8, RF.9, RF.9b, RF.13, RF.14, RF-C.05, RF-C.06, RF-C.07, RF-C.11 |
| `notification-svc` | RF.10, RF.11, RF.12 |
| `ai-risk-svc` | RF-C.02 |
| `ai-assistant-svc` | RF-C.03 |
| `api-gateway` | RF.1 (entrada), todos los demás como routing layer |

---

## Matriz Regla ↔ Servicio (dónde se ejecuta cada regla)

| Regla | Servicios que la aplican |
|---|---|
| RC.01 (morosidad, regla determinística) | `loan-svc` (detección), `auth-svc` (persiste bloqueo) |
| RC.02 (duración préstamos) | `loan-svc`, `request-svc` |
| RC.03 (tipos recurso) | `inventory-svc` |
| RC.04 (identificación) | `auth-svc` |
| RC.05 (niveles stock) | `inventory-svc` |
| RC.06 (TTL reserva) | `request-svc`, `inventory-svc`, broker (delayed-message) |
| RC.07 (ticket correlativo) | `loan-svc`, `notification-svc` |
| RC.08 (bloqueo por rol) | `auth-svc` |
| RC.09 (imagen recurso) | `inventory-svc` |
| RC.10 (blacklist manual) | `auth-svc` |
| RC.11 (scoring umbral) | `ai-risk-svc`, `request-svc` |
| RC.12 (concurrencia stock) | `inventory-svc` |
| RC.13 (cambio clave) | `auth-svc` |
| RC.14 (sesión pañolero) | `auth-svc` (valida PIN), `totem` |
| RC.15 (moroso bloqueado) | `auth-svc`, `request-svc`, `ai-assistant-svc` |
| RC.16 (estados solicitud) | `request-svc` |
| RC.17 (estados préstamo) | `loan-svc` |
| RC.18 (estados recurso) | `inventory-svc` |

---

## Matriz CU ↔ Backlog

El backlog completo vive en `docs/agile/backlog.csv` (importable a Taiga; instrucciones en `docs/agile/README.md`). La matriz a continuación enlaza cada US con su CU, RF, equipo y sprint, permitiendo verificar cobertura del backlog respecto de los requerimientos antes de iniciar los sprints.

| US | Épica | Equipo | CU | RF / Regla | Sprint |
|---|---|---|---|---|---|
| US-001 | plataforma | A | — | técnica (monorepo) | Sprint 0 |
| US-002 | plataforma | A | — | técnica (broker + BD) | Sprint 0 |
| US-003 | plataforma | B | — | técnica (libs/events) | Sprint 0 |
| US-004 | plataforma | B | — | técnica (infra-nestjs) | Sprint 0 |
| US-005 | plataforma | A | — | técnica (CI/CD) | Sprint 0 |
| US-006 | auth | A | CU1 | RF.1 | Sprint 0 |
| US-007 | auth | A | CU1 | RF-C.10 / RC.13 | Sprint 0 |
| US-008 | auth | A | CU1 | RS.3, RS.4 | Sprint 0 |
| US-009 | auth | A | CU2 | RF.2 / RC.08 | Sprint 0 |
| US-010 | auth | B | CU2 | RF-C.12 / RC.04 | Sprint 0 |
| US-011 | auth | B | CU2 | RF.3 | Sprint 0 |
| US-012 | auth | B | CU2 | RF.3 (alterno) | Sprint 0 |
| US-013 | totem | B | — | técnica (kiosko) | Sprint 0 |
| US-014 | portal | A | — | técnica (shell Next.js) | Sprint 0 |
| US-015 | inventario | B | CU3 | RF.4 / RC.03, RC.18 | Sprint 1 |
| US-016 | inventario | B | CU3 | RF.4 / RC.09 | Sprint 1 |
| US-017 | inventario | B | CU3 | RF-C.08 / RC.18 | Sprint 1 |
| US-018 | solicitudes | A | CU4 | RF.5 | Sprint 1 |
| US-019 | solicitudes | A | CU4 | RC.16 | Sprint 1 |
| US-020 | solicitudes | A | CU4 | RF-C.01 / RC.06 | Sprint 1 |
| US-021 | solicitudes | A | CU4 | RF-C.04 / RC.01, RC.10 | Sprint 1 |
| US-022 | totem | A | CU5 | RF.6 / CN.05 | Sprint 1 |
| US-023 | totem | A | CU5 | RF-C.09 / RC.14 | Sprint 1 |
| US-024 | prestamos | A | CU5 | RF.7 / RC.07, RC.17 | Sprint 1 |
| US-025 | prestamos | A | CU5 | RF.8 / RC.17 | Sprint 1 |
| US-026 | prestamos | A | CU5 | RF-C.06 | Sprint 1 |
| US-027 | prestamos | A | CU5 | RF-C.07 / RC.17, RC.18 | Sprint 1 |
| US-028 | notificaciones | B | CU5 | RF.10 / RC.07 | Sprint 1 |
| US-029 | notificaciones | B | — | técnica (WebSocket) | Sprint 1 |
| US-030 | notificaciones | B | CU5 | RF.10 | Sprint 1 |
| US-031 | portal | B | CU4 | RF-C.11 | Sprint 1 |
| US-032 | ia | B | CU4b | RF-C.03 | Sprint 1 |
| US-033 | solicitudes | A | CU4 (alterno C) | RF-C.13 | Sprint 1 |
| US-034 | ia | B | CU4 | RF-C.02 / RC.11 | Sprint 2 |
| US-035 | ia | B | CU4 | RC.11 | Sprint 2 |
| US-036 | solicitudes | A | CU4c | RF-C.05 / RC.02 | Sprint 2 |
| US-037 | solicitudes | A | CU4c | RF-C.05 | Sprint 2 |
| US-038 | gestion | A | CU6 | RF.11 | Sprint 2 |
| US-039 | gestion | A | CU6 | RF.14 / RC.01 | Sprint 2 |
| US-040 | gestion | A | CU6 | RC.10 / RC.08 | Sprint 2 |
| US-041 | gestion | B | CU6 | RF.12 / RS.1 | Sprint 2 |
| US-042 | inventario | B | CU3 | RC.05 | Sprint 2 |
| US-043 | reportes | B | CU7 | RF.9 | Sprint 2 |
| US-044 | reportes | B | CU7 | RF.13 / RF.9b | Sprint 2 |
| US-045 | gestion | A | CU3 (extensión) | RS-JC.5 | Sprint 2 |
| US-046 | ia | B | CU4b | RF-C.03 | Sprint 2 |
| US-047 | ia | B | CU4b | RC.15 | Sprint 2 |
| US-048 | plataforma | A | — | técnica (DLC + reconciliación) | Sprint 2 |
| US-049 | plataforma | B | — | técnica (observabilidad) | Sprint 2 |
| US-050 | gestion | A | — | RC.13, RC.14 (auditoría) | Sprint 2 |

**Cobertura**: las 50 US cubren los 14 RF originales + 13 RF-C, las 18 reglas RC y los CU1–CU7. Las US técnicas (plataforma, infra, observabilidad) no enlazan a un RF de negocio pero son enablers necesarios para el cumplimiento. La trazabilidad inversa (RF → US) se valida con búsqueda por tag `RF:RF.N` en Taiga.

---

## Apéndice — Matriz granular RS ↔ RF ↔ CU por rol

Esta matriz desglosa cada requerimiento de sistema individual para enlazarlo con el RF y el CU que lo implementa. Reemplaza la descripción agregada de la sección "Por rol".

### Jefe de Carrera

| RS | Descripción breve | RF | CU |
|---|---|---|---|
| RS-JC.1 | Crear Coord, Pañolero, Docente, Alumno | RF.2, RF.3 | CU2 |
| RS-JC.2 | Modificar / baja lógica de cualquier usuario | RF.2, RF.3 | CU2 |
| RS-JC.3 | Administrar recursos (alta, modificación, baja) | RF.4, RF-C.08 | CU3 |
| RS-JC.4 | Generar reportes de gestión | RF.9b, RF.13 | CU7 |
| RS-JC.5 | Configurar parámetros operativos de la Escuela | RF.4 (parámetros), RC.01–RC.13 configurables | CU3 (extensión) |

### Coordinador de Carrera

| RS | Descripción breve | RF | CU |
|---|---|---|---|
| RS-CC.1 | Crear Alumnos individualmente | RF.3 | CU2 |
| RS-CC.2 | Importar Alumnos desde Excel/CSV | RF.3 | CU2 (flujo alterno A) |
| RS-CC.3 | Bloquear/desbloquear morosos (Alumnos y Docentes) | RF.14, RC.10 | CU6 |
| RS-CC.4 | Generar los mismos reportes que el Jefe | RF.9b, RF.13 | CU7 |

### Pañolero

| RS | Descripción breve | RF | CU |
|---|---|---|---|
| RS-PN.1 | Ingresar y mantener recursos del inventario | RF.4 | CU3 |
| RS-PN.2 | Consultar solicitudes y préstamos del día | RF.6, RF.9 | CU5 |
| RS-PN.3 | Validar solicitud y registrar préstamo | RF.7, RF.8, RF-C.06 | CU5 |
| RS-PN.4 | Dar de baja o anular préstamos no efectivos | RF.8 (extensión) | CU5 (flujo alterno B) |
| RS-PN.5 | Consultar reportes de estado | RF.9, RF.9b | CU7 |
| RS-PN.6 | Bloquear Alumnos morosos | RF.14, RC.08 | CU6 |
| — | Crear solicitud a nombre de otro usuario | RF-C.13 | CU4 (flujo alterno C) |

### Docente y Alumno

| RS | Descripción breve | RF | CU |
|---|---|---|---|
| RS-DA.1 | Crear solicitud web | RF.5 | CU4 |
| RS-DA.2 | Interactuar con el asistente conversacional | RF-C.03 | CU4b |
| RS-DA.3 | Consultar historial personal | RF-C.11 | CU4 |
