#!/usr/bin/env python3
"""
import_to_jira.py

Importa el backlog de docs/agile/backlog.csv directamente a Jira Cloud via API.

Qué hace:
  1. Crea 11 Epics en el proyecto destino (una por tag epic:* del backlog).
  2. Crea 3 Sprints (Sprint 0, Sprint 1, Sprint 2) en el board.
  3. Crea 50 Stories, cada una con Parent = epic correspondiente, Sprint
     asignado, Story Points, Labels y Description.

Uso:
    # 1) Expone tus credenciales como variables de entorno
    export JIRA_BASE_URL="https://intohybrid.atlassian.net"
    export JIRA_EMAIL="intohybrid@gmail.com"
    export JIRA_TOKEN="tu-api-token-aqui"
    export JIRA_PROJECT_KEY="SCRUM"
    export JIRA_BOARD_ID="1"

    # 2) Corre
    python3 docs/agile/import_to_jira.py

Windows PowerShell:
    $env:JIRA_BASE_URL = "https://intohybrid.atlassian.net"
    $env:JIRA_EMAIL = "intohybrid@gmail.com"
    $env:JIRA_TOKEN = "tu-api-token-aqui"
    $env:JIRA_PROJECT_KEY = "SCRUM"
    $env:JIRA_BOARD_ID = "1"
    python docs/agile/import_to_jira.py

Cómo obtener el API token:
    https://id.atlassian.com/manage-profile/security/api-tokens
    → Create API token → copiar el valor → pegar en JIRA_TOKEN.

Idempotencia:
  - Si un Epic con el mismo Summary ya existe, se reutiliza (no se duplica).
  - Los Sprints son detectados por nombre en el board.
  - Las Stories se crean siempre (no se detectan duplicados).
    Si corres el script dos veces, verás 100 stories. Borra las primeras
    antes de reintentar.

Dependencias:
  pip install requests

Si no tienes requests, también corre con urllib (stdlib), pero requests hace
el código más legible. El script intenta usar requests y cae a urllib si no.
"""

import csv
import json
import os
import re
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

try:
    import requests  # type: ignore
    HAVE_REQUESTS = True
except ImportError:
    HAVE_REQUESTS = False
    import urllib.request
    import urllib.error
    import base64


# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

BASE_URL = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
EMAIL = os.environ.get("JIRA_EMAIL", "")
TOKEN = os.environ.get("JIRA_TOKEN", "")
PROJECT_KEY = os.environ.get("JIRA_PROJECT_KEY", "SCRUM")
BOARD_ID = os.environ.get("JIRA_BOARD_ID", "1")

CSV_PATH = Path(__file__).parent / "backlog.csv"

SPRINT_START = date(2026, 4, 27)
SPRINT_DURATION_DAYS = 14
SPRINT_NAMES = ["Sprint 0", "Sprint 1", "Sprint 2"]

EPIC_DEFS = {
    "plataforma":     ("Plataforma base", "Setup monorepo, infra, observabilidad y EIP de soporte."),
    "auth":           ("Autenticación y usuarios", "Login, JWT, gestión de usuarios y roles."),
    "inventario":     ("Inventario y catálogo", "CRUD de recursos, estados y niveles de stock."),
    "solicitudes":    ("Solicitudes web y workflow", "Creación de solicitudes, estados y TTL."),
    "prestamos":      ("Préstamos y devoluciones", "Materialización, devoluciones y tickets."),
    "notificaciones": ("Notificaciones in-app", "Bandeja, WebSocket y PDF de respaldo."),
    "ia":             ("Inteligencia artificial", "Scoring de riesgo y asistente conversacional."),
    "gestion":        ("Gestión y administración", "Bloqueos, alertas, parámetros, auditoría."),
    "reportes":       ("Reportes operativos y de gestión", "Dashboards para Pañolero, Coord y Jefe."),
    "portal":         ("Portal web (Next.js)", "UI principal para alumnos, docentes y admin."),
    "totem":          ("Tótem (modo kiosko)", "UI del Pañolero para validar y entregar."),
}


# ---------------------------------------------------------------------------
# Validación de entorno
# ---------------------------------------------------------------------------

def check_env():
    missing = [k for k in ("JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_TOKEN") if not os.environ.get(k)]
    if missing:
        print(f"ERROR: faltan variables de entorno: {', '.join(missing)}")
        print("Revisar la cabecera del script para ver cómo configurarlas.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# HTTP helpers (requests si existe; urllib si no)
# ---------------------------------------------------------------------------

def _auth_header() -> str:
    if HAVE_REQUESTS:
        return ""  # requests maneja auth directamente
    raw = f"{EMAIL}:{TOKEN}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")


def http(method: str, url: str, payload: Any = None, params: dict | None = None) -> dict:
    """Ejecuta una request HTTP y devuelve el body JSON parseado."""
    full_url = url if url.startswith("http") else f"{BASE_URL}{url}"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    if HAVE_REQUESTS:
        r = requests.request(
            method, full_url,
            auth=(EMAIL, TOKEN),
            headers=headers,
            json=payload,
            params=params,
            timeout=30,
        )
        if r.status_code >= 400:
            raise RuntimeError(f"HTTP {r.status_code} {method} {full_url}\n{r.text}")
        if not r.text:
            return {}
        try:
            return r.json()
        except json.JSONDecodeError:
            return {"raw": r.text}
    else:
        if params:
            qs = "&".join(f"{k}={v}" for k, v in params.items())
            full_url = f"{full_url}?{qs}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(full_url, data=data, method=method, headers={**headers, "Authorization": _auth_header()})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
                if not body:
                    return {}
                try:
                    return json.loads(body)
                except json.JSONDecodeError:
                    return {"raw": body}
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code} {method} {full_url}\n{body}")


# ---------------------------------------------------------------------------
# Descubrimiento del proyecto
# ---------------------------------------------------------------------------

def get_issue_types(project_key: str) -> dict[str, str]:
    """
    Devuelve {nombre_tipo_lowercase: id_tipo} para este proyecto.

    Intenta dos caminos, en orden, para tolerar la nueva experiencia
    "Spaces" de Jira Cloud que oculta endpoints clásicos:

      a) /rest/api/3/project/{key}  -> el clásico.
      b) /rest/api/3/issuetype/project?projectId=<id>  -> alternativo.
    """
    # Intento A
    try:
        data = http("GET", f"/rest/api/3/project/{project_key}")
        mapping = {t["name"].lower(): t["id"] for t in data.get("issueTypes", [])}
        if mapping:
            return mapping
    except RuntimeError as e:
        print(f"  (aviso) /rest/api/3/project/{project_key} falló: {e}")

    # Intento B: hay que conocer el projectId numérico primero
    try:
        # /rest/api/3/issue/createmeta se banca el key o el id
        meta = http("GET", "/rest/api/3/issue/createmeta", params={
            "projectKeys": project_key,
            "expand": "projects.issuetypes",
        })
        projects = meta.get("projects", [])
        if projects:
            return {t["name"].lower(): t["id"] for t in projects[0].get("issuetypes", [])}
    except RuntimeError as e:
        print(f"  (aviso) /rest/api/3/issue/createmeta falló: {e}")

    return {}


def list_all_projects() -> list[dict]:
    """Devuelve todos los proyectos visibles por el usuario autenticado."""
    out = []
    start = 0
    while True:
        data = http("GET", "/rest/api/3/project/search", params={"startAt": start, "maxResults": 50})
        out.extend(data.get("values", []))
        if data.get("isLast", True):
            break
        start += len(data.get("values", []))
        if not data.get("values"):
            break
    return out


def resolve_project_key(requested: str) -> str:
    """
    Confirma el project key usando un probe directo al endpoint de issue
    types. Si el /project/search no lista nada (común en Spaces nuevos),
    aceptamos el key tal cual y dejamos que falle más adelante con un
    error descriptivo si el key está mal.
    """
    # Primero probamos con createmeta que es menos exigente en permisos.
    try:
        meta = http("GET", "/rest/api/3/issue/createmeta", params={"projectKeys": requested})
        if meta.get("projects"):
            p = meta["projects"][0]
            if p.get("key", "").upper() != requested.upper():
                print(f"  Nota: el proyecto real es '{p['key']}' (ajustando desde '{requested}').")
            return p["key"]
    except RuntimeError:
        pass  # seguimos con el siguiente intento

    # Si createmeta no funciona, intentamos /project/search
    try:
        projects = list_all_projects()
        for p in projects:
            if p["key"].upper() == requested.upper():
                if p["key"] != requested:
                    print(f"  Nota: el proyecto real es '{p['key']}' (ajustando desde '{requested}').")
                return p["key"]
        if projects:
            print(f"ERROR: no se encontró ningún proyecto con key '{requested}'.")
            print("Proyectos visibles por tu usuario:")
            for p in projects:
                print(f"  key='{p['key']}'  name='{p.get('name', '')}'  id={p.get('id', '')}")
            sys.exit(1)
    except RuntimeError:
        pass

    # Si llegamos acá, ambos endpoints fallaron (típico en Spaces). Confiamos
    # en el key dado y dejamos que el fallo aparezca más tarde con detalle.
    print(f"  (aviso) no pude listar proyectos via API; asumo project key '{requested}' tal cual.")
    print("          Si el proyecto no existe con ese key, fallará al crear issues.")
    return requested


def get_existing_epics(project_key: str) -> dict[str, str]:
    """Devuelve {summary_epic: issueKey} para epics existentes."""
    jql = f'project = "{project_key}" AND issuetype = Epic'
    result: dict[str, str] = {}
    next_token: str | None = None
    while True:
        payload: dict[str, Any] = {
            "jql": jql,
            "fields": ["summary"],
            "maxResults": 100,
        }
        if next_token is not None:
            payload["nextPageToken"] = next_token
        data = http("POST", "/rest/api/3/search/jql", payload=payload)
        for iss in data.get("issues", []):
            result[iss["fields"]["summary"]] = iss["key"]
        if data.get("isLast", True):
            break
        next_token = data.get("nextPageToken")
        if not next_token:
            break
    return result


def detect_custom_field(name_substr: str) -> str | None:
    """
    Encuentra el id (p.ej. customfield_10016) de un campo custom por
    coincidencia case-insensitive de substring del nombre.
    """
    fields = http("GET", "/rest/api/3/field")
    for f in fields:
        if name_substr.lower() in f.get("name", "").lower():
            return f["id"]
    return None


# ---------------------------------------------------------------------------
# Sprints (Agile API)
# ---------------------------------------------------------------------------

def get_board_sprints(board_id: str) -> dict[str, int] | None:
    """
    Devuelve {nombre_sprint: sprint_id} para los sprints del board.

    Retorna None si la Agile API no está disponible para este token
    (p. ej. API token con scopes granulares sin permiso sobre agile).
    """
    result = {}
    start = 0
    while True:
        try:
            data = http("GET", f"/rest/agile/1.0/board/{board_id}/sprint", params={"startAt": start, "maxResults": 50})
        except RuntimeError as e:
            msg = str(e)
            if "401" in msg or "403" in msg:
                print(f"  (aviso) Agile API no accesible con este token: {msg.splitlines()[0]}")
                return None
            raise
        for s in data.get("values", []):
            result[s["name"]] = s["id"]
        if data.get("isLast", True):
            break
        start += len(data.get("values", []))
        if not data.get("values"):
            break
    return result


def create_sprint(board_id: str, name: str, start: date, end: date) -> int | None:
    payload = {
        "name": name,
        "startDate": start.isoformat() + "T00:00:00.000Z",
        "endDate": end.isoformat() + "T00:00:00.000Z",
        "originBoardId": int(board_id),
        "goal": f"{name} del backlog Pañol",
    }
    try:
        data = http("POST", "/rest/agile/1.0/sprint", payload=payload)
        return data["id"]
    except RuntimeError as e:
        msg = str(e)
        if "401" in msg or "403" in msg:
            print(f"  (aviso) no puedo crear sprint via Agile API: {msg.splitlines()[0]}")
            return None
        raise


def ensure_sprints(board_id: str) -> dict[str, int]:
    """
    Garantiza que existan Sprint 0/1/2 en el board. Si la Agile API no está
    accesible con este token, devuelve {} y el script sigue sin asignar sprint.
    """
    existing = get_board_sprints(board_id)
    if existing is None:
        print("  Saltando creación de sprints (el token no tiene scope agile).")
        print("  Las stories se crearán sin asignación de sprint.")
        print("  Para resolver: regenera tu token de Jira como 'Classic' o")
        print("  con los scopes 'read:jira-work' y 'write:jira-work'.")
        return {}

    out = {}
    for i, name in enumerate(SPRINT_NAMES):
        if name in existing:
            out[name] = existing[name]
            print(f"  Sprint existente: {name} (id={existing[name]})")
        else:
            start = SPRINT_START + timedelta(days=i * SPRINT_DURATION_DAYS)
            end = start + timedelta(days=SPRINT_DURATION_DAYS - 1)
            sid = create_sprint(board_id, name, start, end)
            if sid is None:
                # No hay permiso; abortamos el resto del ensure_sprints.
                return out
            out[name] = sid
            print(f"  Sprint creado: {name} (id={sid}) {start} -> {end}")
    return out


# ---------------------------------------------------------------------------
# ADF (Atlassian Document Format) converter
# ---------------------------------------------------------------------------

def markdown_to_adf(md: str) -> dict:
    """
    Conversor minimal de markdown a ADF (Atlassian Document Format).
    Soporta: párrafos, listas con "-", texto con **bold**.
    No es perfecto, pero cubre el formato que usamos en los criterios de aceptación.
    """
    if not md:
        return {"type": "doc", "version": 1, "content": []}

    # Normaliza "\\n" escapado a salto de línea real (vienen del CSV)
    text = md.replace("\\n", "\n")

    content = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("- "):
            # Acumula lista
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(_inline_to_adf(lines[i][2:]))
                i += 1
            content.append({
                "type": "bulletList",
                "content": [
                    {"type": "listItem", "content": [{"type": "paragraph", "content": item}]}
                    for item in items
                ],
            })
        else:
            # Párrafo que puede estar compuesto de múltiples líneas
            para = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("- "):
                para.append(lines[i])
                i += 1
            content.append({
                "type": "paragraph",
                "content": _inline_to_adf(" ".join(para)),
            })
    return {"type": "doc", "version": 1, "content": content}


def _inline_to_adf(text: str) -> list[dict]:
    """Convierte **bold** inline. Todo lo demás se deja como texto plano."""
    out = []
    pattern = re.compile(r"\*\*(.+?)\*\*")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            out.append({"type": "text", "text": text[pos:m.start()]})
        out.append({"type": "text", "text": m.group(1), "marks": [{"type": "strong"}]})
        pos = m.end()
    if pos < len(text):
        out.append({"type": "text", "text": text[pos:]})
    return out or [{"type": "text", "text": text}]


# ---------------------------------------------------------------------------
# Creación de issues
# ---------------------------------------------------------------------------

def create_epic(project_key: str, epic_type_id: str | None, name: str, description: str, labels: list[str]) -> str:
    payload: dict[str, Any] = {
        "fields": {
            "project": {"key": project_key},
            "summary": name,
            "description": markdown_to_adf(description),
            "labels": labels,
        }
    }
    if epic_type_id:
        payload["fields"]["issuetype"] = {"id": epic_type_id}
    else:
        payload["fields"]["issuetype"] = {"name": "Epic"}
    data = http("POST", "/rest/api/3/issue", payload=payload)
    return data["key"]


def create_story(
    project_key: str,
    story_type_id: str | None,
    summary: str,
    description: str,
    labels: list[str],
    parent_key: str | None,
    story_points: float | None,
    sp_field_id: str | None,
    sprint_field_id: str | None,
    sprint_id: int | None,
    story_type_name: str = "Story",
) -> str:
    fields: dict[str, Any] = {
        "project": {"key": project_key},
        "summary": summary,
        "description": markdown_to_adf(description),
        "labels": labels,
    }
    if story_type_id:
        fields["issuetype"] = {"id": story_type_id}
    else:
        fields["issuetype"] = {"name": story_type_name}
    if parent_key:
        fields["parent"] = {"key": parent_key}
    if story_points is not None and sp_field_id:
        fields[sp_field_id] = story_points
    if sprint_id is not None and sprint_field_id:
        fields[sprint_field_id] = sprint_id

    data = http("POST", "/rest/api/3/issue", payload={"fields": fields})
    return data["key"]


# ---------------------------------------------------------------------------
# Parsing del backlog
# ---------------------------------------------------------------------------

def parse_tags(raw: str) -> list[str]:
    if not raw:
        return []
    return [t.strip() for t in raw.split(",") if t.strip()]


def extract_epic_slug(tags: list[str]) -> str | None:
    for t in tags:
        if t.startswith("epic:"):
            return t.split(":", 1)[1]
    return None


def filter_labels(tags: list[str]) -> list[str]:
    """Labels para Jira: excluye epic:* y sprint:*."""
    out = []
    for t in tags:
        if t.startswith("epic:") or t.startswith("sprint:"):
            continue
        # Jira no permite espacios en labels. Reemplaza por underscore por si acaso.
        out.append(t.replace(" ", "_"))
    return out


def story_points(raw: Any) -> float | None:
    if raw is None:
        return None
    s = str(raw).strip()
    if s in ("", "?"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def load_backlog() -> list[dict]:
    out = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tags = parse_tags(row["tags"])
            out.append({
                "subject": row["subject"].strip(),
                "description": row["description"],
                "tags": tags,
                "epic_slug": extract_epic_slug(tags),
                "labels": filter_labels(tags),
                "sprint": row.get("milestone", "").strip(),
                "points": story_points(row.get("user_story_points")),
            })
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    check_env()

    print(f"Target: {BASE_URL}  project={PROJECT_KEY}  board={BOARD_ID}")
    print(f"User:   {EMAIL}\n")

    # 0) Resolver el project key real (case-insensitive + diagnóstico si no existe)
    print("Verificando proyecto...")
    project_key = resolve_project_key(PROJECT_KEY)
    print(f"  Project key confirmado: {project_key}\n")

    # 1) Issue types
    print("Descubriendo tipos de issue del proyecto...")
    types = get_issue_types(project_key)
    # El proyecto puede estar configurado con Story, Task o ambos.
    # Preferimos Story; si no existe, usamos Task (muy común en los
    # team-managed nuevos donde Story ni siquiera viene de serie).
    story_type_name = None
    for candidate in ("story", "task"):
        if not types or candidate in types:
            story_type_name = candidate.capitalize()
            break
    if not types:
        print("  (aviso) no pude leer los issue types; usaré 'Epic' y 'Story' tal cual.")
        epic_type_id = None
        story_type_id = None
        story_type_name = story_type_name or "Story"
    else:
        if "epic" not in types:
            print(f"ERROR: el proyecto {project_key} no expone 'Epic' como issue type.")
            print(f"Tipos disponibles: {list(types.keys())}")
            print("Agrega Epic desde Project settings -> Issue types -> Add work type.")
            sys.exit(1)
        if story_type_name is None:
            print(f"ERROR: el proyecto {project_key} no tiene 'Story' ni 'Task' como issue types.")
            print(f"Tipos disponibles: {list(types.keys())}")
            sys.exit(1)
        epic_type_id = types["epic"]
        story_type_id = types[story_type_name.lower()]
        print(f"  Epic          id={epic_type_id}")
        print(f"  {story_type_name:13} id={story_type_id}  (usado como unidad de historia)")
    print()

    # 2) Custom fields
    print("Buscando custom fields (Story Points, Sprint)...")
    sp_field = detect_custom_field("Story point estimate") or detect_custom_field("Story Points")
    sprint_field = detect_custom_field("Sprint")
    print(f"  Story Points field: {sp_field}")
    print(f"  Sprint field:       {sprint_field}\n")

    # 3) Sprints
    print("Asegurando sprints en el board...")
    sprints = ensure_sprints(BOARD_ID)
    print()

    # 4) Epics: reutiliza existentes si coinciden por Summary
    print("Epics existentes en el proyecto:")
    existing_epics = get_existing_epics(project_key)
    for s, k in existing_epics.items():
        print(f"  {k}: {s}")
    print()

    print("Creando/reutilizando epics del backlog...")
    epic_key_by_slug: dict[str, str] = {}
    for slug, (name, desc) in EPIC_DEFS.items():
        if name in existing_epics:
            epic_key_by_slug[slug] = existing_epics[name]
            print(f"  [reuse] {slug:16} -> {existing_epics[name]}: {name}")
        else:
            key = create_epic(project_key, epic_type_id, name, desc, [f"epic:{slug}"])
            epic_key_by_slug[slug] = key
            print(f"  [new  ] {slug:16} -> {key}: {name}")
            time.sleep(0.2)  # throttle suave
    print()

    # 5) Stories
    print("Cargando backlog desde CSV...")
    backlog = load_backlog()
    print(f"  {len(backlog)} user stories\n")

    print("Creando stories...")
    created = 0
    failed = 0
    for i, s in enumerate(backlog, 1):
        parent_key = epic_key_by_slug.get(s["epic_slug"]) if s["epic_slug"] else None
        sprint_id = sprints.get(s["sprint"])
        try:
            key = create_story(
                project_key,
                story_type_id,
                s["subject"],
                s["description"],
                s["labels"],
                parent_key,
                s["points"],
                sp_field,
                sprint_field,
                sprint_id,
                story_type_name=story_type_name or "Story",
            )
            created += 1
            print(f"  [{i:3}/{len(backlog)}] {key}: {s['subject'][:60]}")
            time.sleep(0.2)
        except Exception as e:
            failed += 1
            print(f"  [{i:3}/{len(backlog)}] FAIL: {s['subject'][:60]}")
            print(f"       {e}")
    print()

    print("=" * 60)
    print(f"Resumen: {created} stories creadas, {failed} fallaron")
    print(f"         {len(epic_key_by_slug)} epics listas")
    print(f"         {len(sprints)} sprints listos")
    print("=" * 60)


if __name__ == "__main__":
    main()
