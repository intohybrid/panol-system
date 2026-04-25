# Import de backlog a Jira Cloud via API

Plan B cuando el importer CSV de Jira Cloud no carga ("We couldn't load this page" o falla en el mapeo). Este script usa la API REST de Jira + Agile para crear epics, sprints y stories sin pasar por la UI del importer.

## Pre-requisitos

- Python 3.8+ instalado.
- Proyecto en Jira Cloud ya creado (tipo **Scrum**) con board configurado.
- Rol de **admin** del proyecto (para crear sprints).
- API token personal de tu cuenta Atlassian.

## Paso 1: Generar API token

1. Ve a https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token** (no "Create API token with scopes" si se ofrecen los dos).
3. Dale un label: `backlog-import`.
4. Copia el valor del token. Solo se muestra una vez; si lo pierdes tienes que generar otro.

### Importante — tipos de token de Jira 2025+

Atlassian introdujo dos tipos de token:

- **Classic API token**: acceso completo como tu usuario. **Usa este**.
- **Scoped API token**: pide permisos explícitos. Con los scopes por defecto, endpoints como `/rest/api/3/project/search` devuelven lista vacía y parece que "no tienes proyectos". Si solo te deja crear tokens scoped, marca los siguientes scopes clásicos:
  - `read:jira-work`
  - `write:jira-work`
  - `manage:jira-project`
  - `manage:jira-configuration`

Si ya creaste un token sin estos scopes y el script te dice "tu usuario no tiene acceso a ningún proyecto" o falla al crear sprints con 401, **el problema es el token**, no tu proyecto.

## Paso 2: Limpiar los issues de ejemplo (opcional)

Si tu proyecto nuevo tiene Task 1 y Task 2 de ejemplo, bórralos antes de importar:

1. En Jira, entra al **Backlog** del proyecto.
2. Click derecho en cada task de ejemplo → **Delete**.
3. Confirma.

Si dejas el sprint de ejemplo vacío, el script crea "Sprint 0", "Sprint 1", "Sprint 2" adicionales sin problema. Puedes borrar el sprint de ejemplo desde el Backlog también.

## Paso 3: Configurar variables de entorno

### Windows PowerShell

```powershell
$env:JIRA_BASE_URL = "https://intohybrid.atlassian.net"
$env:JIRA_EMAIL = "intohybrid@gmail.com"
$env:JIRA_TOKEN = "<pega-tu-token-aqui>"
$env:JIRA_PROJECT_KEY = "SCRUM"
$env:JIRA_BOARD_ID = "1"
```

### Windows CMD

```cmd
set JIRA_BASE_URL=https://intohybrid.atlassian.net
set JIRA_EMAIL=intohybrid@gmail.com
set JIRA_TOKEN=<pega-tu-token-aqui>
set JIRA_PROJECT_KEY=SCRUM
set JIRA_BOARD_ID=1
```

### macOS / Linux

```bash
export JIRA_BASE_URL="https://intohybrid.atlassian.net"
export JIRA_EMAIL="intohybrid@gmail.com"
export JIRA_TOKEN="<pega-tu-token-aqui>"
export JIRA_PROJECT_KEY="SCRUM"
export JIRA_BOARD_ID="1"
```

## Paso 4: Instalar dependencia (opcional pero recomendado)

```bash
pip install requests
```

Si no tienes requests, el script cae a `urllib` de stdlib y funciona igual.

## Paso 5: Ejecutar

```bash
python docs/agile/import_to_jira.py
```

El script imprime qué hace paso a paso:

- Detecta los tipos de issue del proyecto (Epic, Story).
- Busca los IDs de los custom fields Story Points y Sprint.
- Crea (o reutiliza) los 3 sprints en el board.
- Crea 11 epics (o reutiliza las que ya existan con el mismo nombre).
- Crea las 50 stories, una por una, con Parent, Sprint, Story Points, Labels y Description.

Salida esperada:

```
Target: https://intohybrid.atlassian.net  project=SCRUM  board=1
User:   intohybrid@gmail.com

Descubriendo tipos de issue del proyecto...
  Epic  id=10000
  Story id=10001

Buscando custom fields (Story Points, Sprint)...
  Story Points field: customfield_10016
  Sprint field:       customfield_10020

Asegurando sprints en el board...
  Sprint creado: Sprint 0 (id=1) 2026-04-27 -> 2026-05-10
  Sprint creado: Sprint 1 (id=2) 2026-05-11 -> 2026-05-24
  Sprint creado: Sprint 2 (id=3) 2026-05-25 -> 2026-06-07

Epics existentes en el proyecto:

Creando/reutilizando epics del backlog...
  [new  ] auth             -> SCRUM-3: Autenticación y usuarios
  [new  ] gestion          -> SCRUM-4: Gestión y administración
  ...

Creando stories...
  [  1/ 50] SCRUM-14: Setup monorepo con pnpm + turborepo
  [  2/ 50] SCRUM-15: Levantar docker-compose con RabbitMQ + Postgres
  ...

============================================================
Resumen: 50 stories creadas, 0 fallaron
         11 epics listas
         3 sprints listos
============================================================
```

## Paso 6: Verificación en Jira

1. **Backlog**: debería mostrar los 3 sprints con las stories repartidas (14 en Sprint 0, 19 en Sprint 1, 17 en Sprint 2).
2. **Epics**: en el panel de epics verás las 11 con sus stories colgando.
3. **Story points**: visibles en cada story.
4. **Labels**: `team:A`, `team:B`, `tipo:negocio`, `tipo:tecnica`, `RF:*`.

## Troubleshooting

### `HTTP 401 Unauthorized`

El email o token están mal. Regenera el token y vuelve a exportarlo.

### `HTTP 403 Forbidden` al crear sprints

Necesitas rol admin del proyecto. Project Settings → People → confirma que eres admin.

### `El proyecto SCRUM no expone Epic o Story`

Tu proyecto está configurado como team-managed con workflow simplificado. Agrega los tipos en Project Settings → Issue Types → Add work type.

### `customfield_XXXXX` no encontrado

Algunos sites tienen los campos Story Points y Sprint con nombres distintos. El script los busca por substring:

- "Story point estimate" (team-managed).
- "Story Points" (company-managed).
- "Sprint".

Si tu site usa otro nombre, edita en el script la función `detect_custom_field()` con el substring correcto. Puedes listar todos tus fields con:

```bash
curl -u "<email>:<token>" https://<tusite>.atlassian.net/rest/api/3/field | python -m json.tool | grep '"name"'
```

### El script se cayó en la mitad

Las stories ya creadas se mantienen. Antes de reintentar:

1. Ve al backlog en Jira y borra las stories creadas (filtra por labels `team:*` o simplemente bulk delete las que no esperabas).
2. Deja los epics y sprints si coinciden con lo que espera el script (se reutilizan automáticamente).
3. Vuelve a correr.

### Quiero borrar todo y empezar de cero

En Jira, Filters → Advanced (JQL):

```
project = SCRUM
```

Selecciona todos → Bulk change → Delete. Luego recorre el script de nuevo.

## Limpiar credenciales del entorno

Cuando termines, vacía el token del entorno:

PowerShell: `Remove-Item Env:JIRA_TOKEN`
Bash: `unset JIRA_TOKEN`

Y si ya no lo vas a usar, **revoca el token en Atlassian**:
https://id.atlassian.com/manage-profile/security/api-tokens
