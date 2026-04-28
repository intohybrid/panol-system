#!/usr/bin/env python3
"""
generate_taiga_dump.py

Convierte docs/agile/backlog.csv en un JSON dump compatible con el Project
Importer de Taiga (Admin → Settings → Import).

Uso:
    python3 generate_taiga_dump.py

Salida:
    docs/agile/taiga-dump.json   (importable en Taiga)

Notas:
- El formato del dump puede variar levemente entre versiones de Taiga.
  Si el importer rechaza el archivo, revisar la sección "Compatibilidad"
  en docs/agile/README.md.
- Las fechas de los sprints se calculan a partir de SPRINT_START en este
  script. Ajustar antes de regenerar si las fechas reales del proyecto
  cambian.
"""

import csv
import json
import re
from datetime import date, timedelta
from pathlib import Path

# ============================================================================
# Configuración
# ============================================================================

PROJECT_NAME = "Sistema de Pañol — UNAB Viña del Mar"
PROJECT_DESCRIPTION = (
    "Sistema de gestión de pañol para la Escuela de Informática UNAB Viña del "
    "Mar. Caso 11 del MIT Design Full Stack + MIT Design AI. Backlog único, "
    "metodología LeSS básica con 2 equipos Feature, sprints de 2 semanas."
)
PROJECT_SLUG = "panol-unab"

SPRINT_START = date(2026, 4, 27)         # Lunes — Sprint 0 arranca este día
SPRINT_DURATION_DAYS = 14                # 2 semanas
SPRINT_NAMES = ["Sprint 0", "Sprint 1", "Sprint 2"]

CSV_PATH = Path(__file__).parent / "backlog.csv"
OUT_PATH = Path(__file__).parent / "taiga-dump.json"


# ============================================================================
# Statuses
# ============================================================================

US_STATUSES = [
    {"name": "New",            "slug": "new",            "order": 1, "is_closed": False, "color": "#999999", "wip_limit": None},
    {"name": "Ready",          "slug": "ready",          "order": 2, "is_closed": False, "color": "#70728F", "wip_limit": None},
    {"name": "In progress",    "slug": "in-progress",    "order": 3, "is_closed": False, "color": "#E47C40", "wip_limit": None},
    {"name": "Ready for test", "slug": "ready-for-test", "order": 4, "is_closed": False, "color": "#E4CE40", "wip_limit": None},
    {"name": "Done",           "slug": "done",           "order": 5, "is_closed": True,  "color": "#A8E440", "wip_limit": None},
]

TASK_STATUSES = [
    {"name": "New",         "slug": "new",         "order": 1, "is_closed": False, "color": "#999999"},
    {"name": "In progress", "slug": "in-progress", "order": 2, "is_closed": False, "color": "#E47C40"},
    {"name": "Ready for test", "slug": "ready-for-test", "order": 3, "is_closed": False, "color": "#E4CE40"},
    {"name": "Closed",      "slug": "closed",      "order": 4, "is_closed": True,  "color": "#A8E440"},
    {"name": "Needs Info",  "slug": "needs-info",  "order": 5, "is_closed": False, "color": "#5178D3"},
]

ISSUE_STATUSES = [
    {"name": "New",            "slug": "new",            "order": 1, "is_closed": False, "color": "#999999"},
    {"name": "In progress",    "slug": "in-progress",    "order": 2, "is_closed": False, "color": "#E47C40"},
    {"name": "Ready for test", "slug": "ready-for-test", "order": 3, "is_closed": False, "color": "#E4CE40"},
    {"name": "Closed",         "slug": "closed",         "order": 4, "is_closed": True,  "color": "#A8E440"},
    {"name": "Needs Info",     "slug": "needs-info",     "order": 5, "is_closed": False, "color": "#5178D3"},
    {"name": "Rejected",       "slug": "rejected",       "order": 6, "is_closed": True,  "color": "#FA8072"},
    {"name": "Postponed",      "slug": "postponed",      "order": 7, "is_closed": False, "color": "#5C3566"},
]

EPIC_STATUSES = [
    {"name": "New",         "slug": "new",         "order": 1, "is_closed": False, "color": "#999999"},
    {"name": "In progress", "slug": "in-progress", "order": 2, "is_closed": False, "color": "#E47C40"},
    {"name": "Ready for test", "slug": "ready-for-test", "order": 3, "is_closed": False, "color": "#E4CE40"},
    {"name": "Done",        "slug": "done",        "order": 4, "is_closed": True,  "color": "#A8E440"},
]

POINTS = [
    {"name": "?",  "value": None, "order": 1},
    {"name": "0",  "value": 0,    "order": 2},
    {"name": "1",  "value": 1,    "order": 3},
    {"name": "2",  "value": 2,    "order": 4},
    {"name": "3",  "value": 3,    "order": 5},
    {"name": "5",  "value": 5,    "order": 6},
    {"name": "8",  "value": 8,    "order": 7},
    {"name": "13", "value": 13,   "order": 8},
    {"name": "21", "value": 21,   "order": 9},
    {"name": "40", "value": 40,   "order": 10},
]

PRIORITIES = [
    {"name": "Low",    "order": 1, "color": "#666666"},
    {"name": "Normal", "order": 3, "color": "#669933"},
    {"name": "High",   "order": 5, "color": "#CC0000"},
]

SEVERITIES = [
    {"name": "Wishlist", "order": 1, "color": "#666666"},
    {"name": "Minor",    "order": 2, "color": "#669933"},
    {"name": "Normal",   "order": 3, "color": "#0000FF"},
    {"name": "Important","order": 4, "color": "#FF8A84"},
    {"name": "Critical", "order": 5, "color": "#CC0000"},
]

ISSUE_TYPES = [
    {"name": "Bug",        "order": 1, "color": "#CC0000"},
    {"name": "Question",   "order": 2, "color": "#669933"},
    {"name": "Enhancement","order": 3, "color": "#0000FF"},
]

ROLES = [
    {
        "name": "Equipo Feature",
        "slug": "equipo-feature",
        "order": 1,
        "computable": True,
        "permissions": [
            "view_project",
            "view_milestones", "add_milestone", "modify_milestone", "delete_milestone",
            "view_epics", "add_epic", "modify_epic", "comment_epic", "delete_epic",
            "view_us", "add_us", "modify_us", "comment_us", "delete_us",
            "view_tasks", "add_task", "modify_task", "comment_task", "delete_task",
            "view_issues", "add_issue", "modify_issue", "comment_issue", "delete_issue",
            "view_wiki_pages", "add_wiki_page", "modify_wiki_page", "comment_wiki_page", "delete_wiki_page",
            "view_wiki_links", "add_wiki_link", "modify_wiki_link", "delete_wiki_link",
        ],
    },
    {
        "name": "Product Owner",
        "slug": "product-owner",
        "order": 2,
        "computable": False,
        "permissions": [
            "view_project",
            "view_milestones", "add_milestone", "modify_milestone", "delete_milestone",
            "view_epics", "add_epic", "modify_epic", "comment_epic", "delete_epic",
            "view_us", "add_us", "modify_us", "comment_us", "delete_us",
            "view_tasks", "add_task", "modify_task", "comment_task", "delete_task",
            "view_issues", "add_issue", "modify_issue", "comment_issue", "delete_issue",
            "view_wiki_pages", "add_wiki_page", "modify_wiki_page", "comment_wiki_page", "delete_wiki_page",
            "view_wiki_links", "add_wiki_link", "modify_wiki_link", "delete_wiki_link",
        ],
    },
]


# ============================================================================
# Helpers
# ============================================================================

def calc_milestones():
    out = []
    for i, name in enumerate(SPRINT_NAMES):
        start = SPRINT_START + timedelta(days=i * SPRINT_DURATION_DAYS)
        finish = start + timedelta(days=SPRINT_DURATION_DAYS - 1)
        out.append({
            "name": name,
            "slug": re.sub(r"\s+", "-", name.lower()),
            "estimated_start": start.isoformat(),
            "estimated_finish": finish.isoformat(),
            "created_date": SPRINT_START.isoformat() + "T00:00:00+0000",
            "modified_date": SPRINT_START.isoformat() + "T00:00:00+0000",
            "closed": False,
            "disponibility": 0.0,
            "order": i + 1,
        })
    return out


def parse_tags(raw):
    if not raw:
        return []
    tags = []
    for piece in raw.split(","):
        t = piece.strip()
        if t:
            # [name, color] — color None deja a Taiga elegir uno
            tags.append([t, None])
    return tags


def points_name(pts_value):
    """Maps the integer in the CSV to the matching points 'name' in POINTS."""
    if pts_value in (None, ""):
        return "?"
    try:
        v = int(pts_value)
    except ValueError:
        return "?"
    for p in POINTS:
        if p["value"] == v:
            return p["name"]
    # if not found, default to "?"
    return "?"


# ============================================================================
# Build dump
# ============================================================================

def build():
    # Read CSV
    user_stories = []
    sprint_orders = {n: 0 for n in SPRINT_NAMES}
    backlog_order = 0

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            backlog_order += 1
            milestone = row["milestone"].strip() if row["milestone"] else None
            if milestone in sprint_orders:
                sprint_orders[milestone] += 1
                sprint_order = sprint_orders[milestone]
            else:
                sprint_order = 0

            ref_match = re.match(r"US-(\d+)", row["ref"].strip())
            ref = int(ref_match.group(1)) if ref_match else backlog_order

            us = {
                "ref": ref,
                "subject": row["subject"].strip(),
                "description": row["description"].replace("\\n", "\n"),
                "tags": parse_tags(row["tags"]),
                "status": row["status"].strip() if row["status"] else "New",
                "milestone": milestone,
                "is_closed": row["is_closed"].strip().lower() == "true",
                "client_requirement": False,
                "team_requirement": False,
                "backlog_order": backlog_order,
                "sprint_order": sprint_order,
                "kanban_order": backlog_order,
                "created_date": SPRINT_START.isoformat() + "T00:00:00+0000",
                "modified_date": SPRINT_START.isoformat() + "T00:00:00+0000",
                "finish_date": None,
                "external_reference": None,
                "watchers": [],
                "role_points": [
                    {"role": "Equipo Feature", "points": points_name(row["user_story_points"])}
                ],
                "generated_from_issue": None,
                "tribe_gig": None,
                "due_date": None,
                "due_date_reason": "",
            }
            user_stories.append(us)

    dump = {
        "name": PROJECT_NAME,
        "slug": PROJECT_SLUG,
        "description": PROJECT_DESCRIPTION,
        "creation_template": None,
        "is_private": True,
        "is_kanban_activated": False,
        "is_backlog_activated": True,
        "is_issues_activated": True,
        "is_wiki_activated": True,
        "is_epics_activated": True,
        "is_contact_activated": False,
        "videoconferences": "",
        "videoconferences_extra_data": "",
        "anon_permissions": [],
        "public_permissions": [],
        "modules_config": {},
        "logo": None,
        "total_milestones": None,
        "total_story_points": None,
        "tags": list(set(t for us in user_stories for t, _ in us["tags"])),
        "tags_colors": [],

        "default_us_status": "New",
        "default_points": "?",
        "default_priority": "Normal",
        "default_severity": "Normal",
        "default_task_status": "New",
        "default_issue_status": "New",
        "default_issue_type": "Bug",
        "default_epic_status": "New",

        "us_statuses": US_STATUSES,
        "us_duedates": [],
        "task_statuses": TASK_STATUSES,
        "task_duedates": [],
        "issue_statuses": ISSUE_STATUSES,
        "issue_duedates": [],
        "issue_types": ISSUE_TYPES,
        "epic_statuses": EPIC_STATUSES,
        "priorities": PRIORITIES,
        "severities": SEVERITIES,
        "points": POINTS,
        "roles": ROLES,
        "memberships": [],
        "milestones": calc_milestones(),
        "user_stories": user_stories,
        "epics": [],
        "tasks": [],
        "issues": [],
        "wiki_pages": [],
        "wiki_links": [],
        "userstorycustomattributes": [],
        "taskcustomattributes": [],
        "issuecustomattributes": [],
        "epiccustomattributes": [],
    }
    return dump


def main():
    dump = build()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(dump, f, ensure_ascii=False, indent=2)
    print(f"OK — dump escrito en: {OUT_PATH}")
    print(f"   {len(dump['user_stories'])} user stories")
    print(f"   {len(dump['milestones'])} milestones")
    print(f"   {len(dump['tags'])} tags únicas")


if __name__ == "__main__":
    main()
