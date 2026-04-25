# Backlog LeSS — Sistema de Pañol

## Propósito

Esta carpeta contiene el backlog único del proyecto, planificado en 3 sprints según LeSS básico con 2 equipos Feature (A y B). El archivo `backlog.csv` es la fuente importable directamente en Taiga.

## Estructura LeSS aplicada

LeSS (Large-Scale Scrum) básico: un solo backlog único, dos equipos Feature trabajando en paralelo, un solo Product Owner, ceremonias compartidas (Sprint Planning Two-Team, Daily Scrum por equipo, Sprint Review única, Retro por equipo + Overall Retro). Sprints de 2 semanas.

| Equipo | Foco preferente (no exclusivo) | Capacidad por sprint (story points) |
|---|---|---|
| Team A | Flujo principal: auth, solicitudes, préstamos, devoluciones, portal | ~50 |
| Team B | Inventario, notificaciones, IA, reportes, plataforma, tótem | ~50 |

LeSS exige Feature Teams (no por componente), por lo tanto cualquier equipo puede tomar cualquier US. La columna `team:A` o `team:B` en el campo `tags` es una asignación inicial sugerida que el sprint planning puede reasignar.

## Plan de los 3 sprints

### Sprint 0 — Plataforma + Auth + Catálogo base (14 US)

Objetivo: dejar la plataforma operativa, autenticación funcionando y la administración de usuarios y catálogo lista para que Sprint 1 construya el flujo completo.

Stories: US-001 a US-014.

**Definition of Ready** Sprint 0: docs de requirements y architecture publicados; Caso 11 leído por todo el equipo.

**Definition of Done** Sprint 0: docker-compose levanta el stack; login y JWT funcionan; ADRs base publicados; CI verde por servicio.

### Sprint 1 — Flujo solicitud → préstamo → devolución (19 US)

Objetivo: el camino feliz completo del usuario está implementado, incluyendo la asistencia conversacional MVP.

Stories: US-015 a US-033.

**Definition of Done** Sprint 1: un alumno puede armar su solicitud (con o sin asistente), el pañolero la valida y materializa en el tótem, el ticket PDF se entrega in-app, la devolución cierra el ciclo. TTL de reservas operando vía Message Expiration. Préstamo parcial cubierto.

### Sprint 2 — IA, gestión, reportes y consolidación (17 US)

Objetivo: scoring predictivo + reportes de gestión + automatizaciones (alertas, bloqueos) + observabilidad de cara a la mesa redonda.

Stories: US-034 a US-050.

**Definition of Done** Sprint 2: scoring decide aceptación con drivers visibles; alertas automáticas de morosidad y stock; reportes operativos y de gestión; trazas distribuidas demostrables en Grafana; auditoría completa.

## Criterios DoR / DoD globales

**Definition of Ready** (toda US debe cumplir antes de entrar al sprint):
- Tiene asignado al menos un RF o RS de `docs/requirements/`.
- Tiene criterios de aceptación verificables.
- Está estimada en story points (Fibonacci: 1, 2, 3, 5, 8, 13).
- No tiene dependencia bloqueante con US fuera del sprint.

**Definition of Done** (US se cierra cuando):
- Código mergeado a `main` con revisión cruzada.
- Tests unitarios pasando; e2e cuando aplique.
- Lint y type-check verdes.
- Documentación actualizada si la US toca arquitectura, eventos o reglas.
- Demo en Sprint Review cubre el criterio de aceptación principal.

## Estimación

Fibonacci: 1, 2, 3, 5, 8, 13. Story points relativos al esfuerzo del equipo. Velocity esperada Sprint 1 y Sprint 2 (después de Sprint 0 de calibración): ~50 puntos por equipo, ~100 puntos totales por sprint.

Resumen de puntos del backlog:

| Sprint | Puntos | US |
|---|---|---|
| Sprint 0 | 64 | 14 |
| Sprint 1 | 107 | 19 |
| Sprint 2 | 94 | 17 |
| **Total** | **265** | **50** |

Sprint 1 quedó por encima de la velocity esperada (107 vs ~100 objetivo). En el primer Sprint Refinement se evalúa si una US se posterga al Sprint 2 o si dos US menores migran al Sprint 0. Los pesos pesados de Sprint 1 son US-018 (crear solicitud, 8), US-020 (TTL, 8), US-024 (materializar, 8), US-025 (devolver, 8), US-032 (asistente MVP, 13).

## Mapeo épicas

| Epic tag | Descripción | Servicios |
|---|---|---|
| `epic:plataforma` | Setup, infra, observabilidad, EIP de soporte | Todos |
| `epic:auth` | Autenticación, usuarios, roles | `auth-svc` |
| `epic:inventario` | Catálogo y stock | `inventory-svc` |
| `epic:solicitudes` | Solicitudes web y workflow | `request-svc` |
| `epic:prestamos` | Materialización y devolución | `loan-svc` |
| `epic:notificaciones` | In-app + tickets PDF | `notification-svc` |
| `epic:ia` | Scoring + asistente | `ai-risk-svc`, `ai-assistant-svc` |
| `epic:gestion` | Bloqueos, alertas, parámetros, auditoría | `auth-svc`, `loan-svc`, `inventory-svc` |
| `epic:reportes` | Operativos y de gestión | `loan-svc`, `inventory-svc` |
| `epic:portal` | UI Next.js | `web-portal` |
| `epic:totem` | UI tótem | `totem` |

## Cómo importar a Taiga

> **Nota importante**: Taiga **no tiene un CSV importer integrado en la UI**. Las opciones reales son: (1) subir un JSON dump al Project Importer, (2) usar la Taiga API con un script, o (3) cargar manualmente. El método recomendado es (1).

### Método recomendado — JSON dump al Project Importer

El archivo `taiga-dump.json` es un dump completo del proyecto compatible con el Project Importer oficial de Taiga. Contiene proyecto, statuses, points, roles, milestones, tags y las 50 user stories con sus puntos asignados.

**Pasos**:

1. Iniciar sesión en Taiga (`taiga.io` o instancia self-hosted).
2. En el dashboard de proyectos, click en **+ → Import project**.
3. Seleccionar **Taiga** como origen.
4. Subir `docs/agile/taiga-dump.json`.
5. Esperar al callback "Import successful". El proyecto aparece en el listado del usuario.
6. Verificar:
   - Nombre del proyecto: "Sistema de Pañol — UNAB Viña del Mar".
   - Backlog con 50 US.
   - 3 milestones (Sprint 0, Sprint 1, Sprint 2) con fechas correctas.
   - Las US del Sprint 0 marcadas como `Ready`; las demás en `New`.
   - Tags `epic:*`, `team:*`, `tipo:*`, `sprint:*`, `RF:*` aplicadas.
   - Story points por US visibles para el rol "Equipo Feature".

### Si el dump no se acepta

Las versiones de Taiga han cambiado el esquema interno con el tiempo. Si el importer reporta un error específico:

- **Versión incompatible / esquema inválido**: regenerar con el script ajustado. La sección "Compatibilidad" más abajo describe los puntos de fricción comunes.
- **Statuses no existen**: el dump declara los statuses estándar; si tu instancia tiene un set diferente, ajustar `US_STATUSES` en `generate_taiga_dump.py`.
- **Slug duplicado**: el slug `panol-unab` ya existe en tu cuenta. Cambiar `PROJECT_SLUG` en el script y regenerar.

### Regenerar el dump

```bash
cd docs/agile
python3 generate_taiga_dump.py
```

Genera `taiga-dump.json` desde `backlog.csv`. Editar `SPRINT_START` en el script para ajustar las fechas reales del proyecto antes de regenerar.

### Métodos alternativos

**Script Taiga API**: si el dump no se acepta o se prefiere carga incremental, hay scripts de la comunidad (`richbl/taiga.io-scripts`) y la API REST oficial de Taiga (`POST /api/v1/userstories`). Requiere API token.

**Carga manual**: el `backlog.csv` y la matriz en `07-trazabilidad.md` son fuentes legibles para copy-paste a la UI de Taiga si todo lo demás falla. Estimar 2–3 minutos por US.

### Columnas del CSV (referencia humana)

| Columna | Uso |
|---|---|
| `ref` | Número de referencia interno (US-001..US-050). En Taiga, cada US recibe su propio ref autoincremental. |
| `subject` | Título de la US. |
| `description` | Cuerpo en markdown con criterios de aceptación. |
| `status` | Estado inicial: `New` o `Ready`. |
| `is_closed` | `true`/`false`. Todas en `false`. |
| `tags` | Etiquetas separadas por coma. Incluyen `epic:`, `team:`, `tipo:`, `sprint:`, `RF:`. |
| `user_story_points` | Story points (Fibonacci). |
| `milestone` | Sprint al que pertenece. |

## Compatibilidad del JSON dump

El esquema del Project Importer de Taiga puede variar entre versiones. Los puntos donde más comúnmente aparecen incompatibilidades:

- **`role_points`**: requiere que el rol exista. El dump declara el rol `Equipo Feature`, pero si la versión usa `slug` en lugar de `name` para mapear, hay que ajustar.
- **`tags`**: en algunas versiones se serializan como lista plana de strings; en otras como `[name, color]`. El script usa la segunda forma (más reciente).
- **`milestones.disponibility`**: el campo cambió de nombre entre versiones (`disponibility` vs `availability`). Si el importer no lo reconoce, eliminar la línea del script.
- **`is_closed` en US**: algunas versiones requieren un `finish_date` cuando `is_closed=true`. Como nuestras US están todas abiertas, no aplica.

## Mapeo US ↔ RF

El detalle vive en `docs/requirements/07-trazabilidad.md`, sección "Matriz CU ↔ Backlog". Esta sección debe quedar sincronizada con el backlog.csv: cada US apunta a un RF (en `tags:RF:`) y la trazabilidad agrega CU y sprint.

## Mantenimiento

- El backlog se refina antes de cada Sprint Planning (Backlog Refinement).
- US nuevas se agregan al CSV con ref consecutiva (US-051, US-052, ...).
- Cambios de estado durante el sprint se hacen en Taiga, no en el CSV.
- Al cierre del proyecto, exportar el estado final desde Taiga como evidencia para la mesa redonda.
