#!/usr/bin/env python3
"""
generate_jira_csv.py

Convierte docs/agile/backlog.csv en un CSV importable por Jira Cloud
(System -> External System Import -> CSV) con:

- Epics derivadas de los tags `epic:*` del backlog.
- User stories como issues de tipo Story, enlazadas a su Epic via Epic Link.
- Sprints (Sprint 0, Sprint 1, Sprint 2) para que Jira los cree por nombre.
- Story Points numéricos. "?" o ausencia se deja vacío.
- Labels: todos los tags del backlog excepto `epic:*` y `sprint:*` (esos se
  mapean a Epic Link y Sprint respectivamente).
- Status: se mapea desde el CSV origen al set estándar de Jira Scrum:
  New / Ready -> To Do, In progress -> In Progress, Done -> Done.

Uso:
    python3 generate_jira_csv.py

Salida:
    docs/agile/jira-import.csv
"""

import csv
import re
from pathlib import Path

HERE = Path(__file__).parent
CSV_IN = HERE / "backlog.csv"
CSV_OUT = HERE / "jira-import.csv"


# ---------------------------------------------------------------------------
# Mapeo de epic:<slug> -> (Epic Name human-readable, Epic Id CSV-local)
# ---------------------------------------------------------------------------

EPIC_DEFS = {
    "plataforma":     ("Plataforma base", "Setup monorepo, infra, observabilidad y EIP de soporte"),
    "auth":           ("Autenticación y usuarios", "Login, JWT, gestión de usuarios y roles"),
    "inventario":     ("Inventario y catálogo", "CRUD de recursos, estados y niveles de stock"),
    "solicitudes":    ("Solicitudes web y workflow", "Creación de solicitudes, estados y TTL"),
    "prestamos":      ("Préstamos y devoluciones", "Materialización, devoluciones y tickets"),
    "notificaciones": ("Notificaciones in-app", "Bandeja, WebSocket y PDF de respaldo"),
    "ia":             ("Inteligencia artificial", "Scoring de riesgo y asistente conversacional"),
    "gestion":        ("Gestión y administración", "Bloqueos, alertas, parámetros, auditoría"),
    "reportes":       ("Reportes operativos y de gestión", "Dashboards para Pañolero, Coord y Jefe"),
    "portal":         ("Portal web (Next.js)", "UI principal para alumnos, docentes y admin"),
    "totem":          ("Tótem (modo kiosko)", "UI del Pañolero para validar y entregar"),
}

# Prioridad Jira por defecto
DEFAULT_PRIORITY = "Medium"

# Mapeo status CSV origen -> status Jira Scrum por defecto
STATUS_MAP = {
    "New": "To Do",
    "Ready": "To Do",
    "In progress": "In Progress",
    "Ready for test": "In Progress",
    "Done": "Done",
    "Closed": "Done",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_tags(raw):
    if not raw:
        return []
    return [t.strip() for t in raw.split(",") if t.strip()]


def extract_epic_slug(tags):
    for t in tags:
        if t.startswith("epic:"):
            return t.split(":", 1)[1]
    return None


def extract_sprint(tags, fallback):
    # Preferir columna `milestone` del CSV; los tags `sprint:N` son redundantes.
    if fallback:
        return fallback.strip()
    for t in tags:
        if t.startswith("sprint:"):
            n = t.split(":", 1)[1]
            return f"Sprint {n}"
    return ""


def filter_labels(tags):
    """Devuelve las labels que deben ir a Jira (excluye epic:*, sprint:*)."""
    out = []
    for t in tags:
        if t.startswith("epic:") or t.startswith("sprint:"):
            continue
        # Normaliza: Jira no permite espacios en labels; el CSV ya no los tiene.
        out.append(t)
    return out


def story_points(raw):
    if raw is None:
        return ""
    raw = str(raw).strip()
    if raw in ("", "?"):
        return ""
    try:
        return str(int(raw))
    except ValueError:
        return ""


def clean_description(raw):
    # El CSV usa \n escapados; los convertimos a saltos reales.
    if not raw:
        return ""
    return raw.replace("\\n", "\n")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_rows():
    # 1) Cargar todas las US
    stories = []
    used_epic_slugs = set()
    max_labels = 0

    with open(CSV_IN, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tags = parse_tags(row["tags"])
            epic_slug = extract_epic_slug(tags)
            if epic_slug:
                used_epic_slugs.add(epic_slug)
            labels = filter_labels(tags)
            max_labels = max(max_labels, len(labels))
            stories.append({
                "csv_ref": row["ref"].strip(),
                "subject": row["subject"].strip(),
                "description": clean_description(row["description"]),
                "status": STATUS_MAP.get(row["status"].strip(), "To Do"),
                "points": story_points(row.get("user_story_points")),
                "sprint": extract_sprint(tags, row.get("milestone", "")),
                "epic_slug": epic_slug,
                "labels": labels,
            })

    # 2) Construir filas de Epic (una por epic slug usado)
    epic_rows = []
    epic_issue_id = {}  # epic_slug -> Issue Id (usado como Parent en stories)
    next_id = 1
    for slug in sorted(used_epic_slugs):
        if slug not in EPIC_DEFS:
            # Epic desconocido: generamos uno genérico con el slug.
            name = slug.capitalize()
            desc = f"Epic derivado del tag epic:{slug} del backlog."
        else:
            name, desc = EPIC_DEFS[slug]
        issue_id = f"EPIC-{next_id:02d}"
        next_id += 1
        epic_issue_id[slug] = issue_id
        epic_rows.append({
            "Issue Id": issue_id,
            "Issue Type": "Epic",
            "Summary": name,
            "Description": desc,
            "Status": "To Do",
            "Priority": DEFAULT_PRIORITY,
            "Sprint": "",
            "Story Points": "",
            "Parent": "",
            "labels": [f"epic:{slug}"],
        })

    # 3) Construir filas de Story
    story_rows = []
    story_id_counter = 1
    for s in stories:
        issue_id = f"US-{story_id_counter:03d}"
        story_id_counter += 1
        story_rows.append({
            "Issue Id": issue_id,
            "Issue Type": "Story",
            "Summary": s["subject"],
            "Description": s["description"],
            "Status": s["status"],
            "Priority": DEFAULT_PRIORITY,
            "Sprint": s["sprint"],
            "Story Points": s["points"],
            "Parent": epic_issue_id.get(s["epic_slug"], ""),
            "labels": s["labels"],
        })

    all_rows = epic_rows + story_rows
    # Recalcula max_labels contemplando los epic rows
    for r in all_rows:
        max_labels = max(max_labels, len(r["labels"]))

    return all_rows, max_labels


def write_csv(rows, max_labels):
    base_fields = [
        "Issue Id",
        "Issue Type",
        "Summary",
        "Description",
        "Status",
        "Priority",
        "Sprint",
        "Story Points",
        "Parent",
    ]
    # Jira permite varias columnas "Labels" con el mismo nombre y las suma.
    label_fields = ["Labels"] * max_labels
    fieldnames = base_fields + label_fields

    with open(CSV_OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        for r in rows:
            row = [
                r["Issue Id"],
                r["Issue Type"],
                r["Summary"],
                r["Description"],
                r["Status"],
                r["Priority"],
                r["Sprint"],
                r["Story Points"],
                r["Parent"],
            ]
            labels = r["labels"] + [""] * (max_labels - len(r["labels"]))
            writer.writerow(row + labels)


def main():
    rows, max_labels = build_rows()
    write_csv(rows, max_labels)
    n_epics = sum(1 for r in rows if r["Issue Type"] == "Epic")
    n_stories = sum(1 for r in rows if r["Issue Type"] == "Story")
    print(f"Generado {CSV_OUT}")
    print(f"  Epics:   {n_epics}")
    print(f"  Stories: {n_stories}")
    print(f"  Labels columns: {max_labels}")


if __name__ == "__main__":
    main()
