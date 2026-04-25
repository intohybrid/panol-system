# Importación del backlog en Jira Cloud (plan gratis)

Esta guía te deja las 50 user stories, los 11 epics y los 3 sprints creados en tu proyecto Jira a partir de `jira-import.csv`.

## Cambio importante: Jira Cloud 2024+

Atlassian [reemplazó `Epic Link` y `Epic Name` por el campo **Parent**](https://support.atlassian.com/jira-software-cloud/docs/upcoming-changes-epic-link-replaced-with-parent/). Por eso el CSV ya no trae esas columnas: usa `Parent` para la relación Epic → Story. Esto aplica tanto a team-managed como a company-managed en Jira Cloud moderno.

Content rephrased for compliance.

## Archivos

- `docs/agile/jira-import.csv` — backlog completo en formato CSV importable (11 epics + 50 stories, 3 sprints).
- `docs/agile/generate_jira_csv.py` — script que regenera el CSV desde `backlog.csv` si cambias algo (requiere Python 3).

## Columnas del CSV

| Columna | Propósito |
|---|---|
| `Issue Id` | Identificador interno del CSV (EPIC-01..EPIC-11, US-001..US-050). Se usa para resolver el `Parent`. |
| `Issue Type` | `Epic` o `Story`. |
| `Summary` | Título del issue. |
| `Description` | Cuerpo con criterios de aceptación. |
| `Status` | `To Do` para todas las filas (todo arranca sin iniciar). |
| `Priority` | `Medium` por defecto. |
| `Sprint` | `Sprint 0`, `Sprint 1` o `Sprint 2`. Jira los crea por nombre. Vacío para epics. |
| `Story Points` | Numérico. Vacío para epics. |
| `Parent` | En stories, el `Issue Id` del Epic al que pertenecen (reemplaza al antiguo `Epic Link`). Vacío para epics. |
| `Labels` (x4) | Las demás etiquetas del backlog: `team:A`, `team:B`, `tipo:negocio`, `tipo:tecnica`, `RF:*`. |

## Pre-requisitos

1. Cuenta de Jira Cloud (plan gratis sirve).
2. Un site creado.
3. Un proyecto **Jira Software** tipo **Scrum** (no Kanban, porque necesitamos sprints). Si es team-managed, revisa la nota al final.
4. Rol de administrador del site o del proyecto.

## Paso 1: Abrir el importer de admin

1. Settings (engranaje arriba a la derecha) → **System**.
2. En "Import and Export" → **External System Import**.
3. Selecciona **CSV**.

> No uses el importer "Import issues from CSV" que aparece dentro de cada proyecto; no resuelve la jerarquía Parent con la misma fiabilidad. El de admin sí.

## Paso 2: Subir el archivo

1. Click en **Choose File** y selecciona `docs/agile/jira-import.csv`.
2. Si aparece un campo para "Configuration file", déjalo vacío la primera vez.
3. Click **Next**.

## Paso 3: Configuración del import

- **Import to project**: selecciona tu proyecto Scrum existente.
- **Email Suffix**: déjalo como está.
- **Date format**: no aplica (el CSV no trae fechas).
- **CSV Delimiter**: coma (`,`).
- **CSV Encoding**: UTF-8.
- Click **Next**.

## Paso 4: Mapeo de campos

Jira te muestra cada columna del CSV. Mapea así:

| Columna CSV | Campo Jira |
|---|---|
| `Issue Id` | **Work item ID** (antes se llamaba "Issue Id"; si no ves ese nombre, elige "External ID") |
| `Issue Type` | **Issue Type** / **Work item Type** |
| `Summary` | **Summary** |
| `Description` | **Description** |
| `Status` | **Status** |
| `Priority` | **Priority** |
| `Sprint` | **Sprint** |
| `Story Points` | **Story point estimate** (team-managed) o **Story Points** (company-managed) |
| `Parent` | **Parent** |
| `Labels` (x4) | **Labels** en las cuatro |

> **Importante sobre Parent**: si marcas `Parent` y Jira muestra el aviso "Map work item ID to proceed", significa que antes de poder usar Parent debes mapear la columna `Issue Id` al campo **Work item ID**. El importer necesita ese campo para resolver las referencias internas del CSV (valores como `EPIC-01`, `EPIC-02`). Mapea primero `Issue Id` → `Work item ID` y el aviso en Parent desaparece.

### Qué hacer si alguna columna no aparece para mapear

- **`Sprint` no aparece**: tu proyecto es Kanban o team-managed sin backlog activado. Habilita el backlog en Project Settings → Features, o crea el proyecto como Scrum.
- **`Parent` no aparece**: confirma que `Issue Type` está bien mapeado primero; Jira evalúa el tipo antes de ofrecer Parent. Si sigue sin aparecer, tu proyecto puede ser muy antiguo; intenta con un proyecto Scrum nuevo.
- **`Story Points` se llama distinto**: en team-managed es "Story point estimate", en company-managed es "Story Points". Ambos aceptan enteros.

Click **Next**.

## Paso 5: Mapeo de valores (value mapping)

Jira muestra los valores únicos de `Status`:

- `To Do` → **To Do**
- `In Progress` → **In Progress** (si apareciera)
- `Done` → **Done** (si apareciera)

En este backlog todas las filas arrancan en `To Do`, así que solo ese valor.

Click **Begin Import**.

## Paso 6: Verificación

1. **Backlog**: 50 stories.
2. **Sprints**: Sprint 0, 1, 2 creados (sin iniciar). Cada story en el sprint correcto.
3. **Epics**: 11 en el panel de Epics. Cada story enlazada a una epic como hijo.
4. **Story Points**: valores entre 2 y 13 visibles en cada story.
5. **Labels**: `team:A`, `team:B`, `tipo:negocio`, `tipo:tecnica`, `RF:*` aplicadas por story.

## Troubleshooting

- **"Map work item ID to proceed" al marcar Parent**: tienes que mapear la columna `Issue Id` del CSV al campo **Work item ID** (antes "Issue Id"). Jira usa esa columna para resolver los valores de Parent (`EPIC-01`, etc.) dentro del mismo CSV. Sin ese mapeo, Parent no funciona.
- **"Parent issue does not exist" o Parent queda vacío**: revisa que mapeaste `Issue Id` a **Work item ID** (no a Summary ni a otra cosa). El importer resuelve el Parent buscando el valor en la columna Work item ID del mismo CSV.
- **Los sprints no se crean**: el campo `Sprint` solo funciona en proyectos Scrum con backlog activado. Si creaste un Kanban, activa el backlog o rehaz el proyecto como Scrum.
- **Story Points vacíos después del import**: elegiste la columna Jira incorrecta. En team-managed es "Story point estimate". Edita en lote o reimporta.
- **Las epics se duplican al reintentar**: los Issue Id del CSV son internos, no claves Jira. Antes de reimportar, borra los issues creados la vez anterior (bulk delete desde Backlog) o borra y recrea el proyecto.
- **Caracteres raros (ñ, acentos)**: confirma encoding UTF-8 en el paso 3.
- **"El Issue Type Epic no existe"**: en team-managed muy minimalistas, Epic puede no estar habilitada. Project Settings → Issue Types → agrega Epic.

## Team-managed vs company-managed

El CSV funciona en ambos, pero:

- En **company-managed** el comportamiento del importer es el más cercano a la doc clásica: `Issue Id` + `Parent` resuelven la jerarquía y ya.
- En **team-managed** el importer puede tener más fricciones con custom fields. Si el `Parent` no se resuelve, un workaround es importar primero solo las epics y después las stories con una segunda pasada del CSV (usando Parent con el Issue Key de Jira real, ej. "SP-1", en vez del Issue Id interno).

Si tu proyecto es team-managed y el import falla, avísame con el error exacto y ajustamos.

## Regenerar el CSV

Si cambias `backlog.csv`:

```bash
cd docs/agile
python3 generate_jira_csv.py
```

Revisa las 11 epics definidas en `EPIC_DEFS` del script si agregaste tags `epic:*` nuevos.

## Mapeo interno CSV → Jira

- `ref` del backlog → `Issue Id` (US-001..US-050).
- `tag epic:xxx` → `Parent` apuntando a EPIC-01..EPIC-11.
- `milestone` → `Sprint`.
- `user_story_points` → `Story Points` (`?` queda vacío).
- `status` (`New`, `Ready`) → `To Do` en Jira.
- `tags` restantes (`team:*`, `tipo:*`, `RF:*`) → `Labels`.

## Qué no está incluido

- Asignaciones (assignee): vacío, se asigna en el Sprint Planning.
- Descripciones de epics: genéricas; ajústalas después.
- Componentes de Jira: no se usan; la división lógica está en Labels.
- Custom fields: no hay en el CSV.
