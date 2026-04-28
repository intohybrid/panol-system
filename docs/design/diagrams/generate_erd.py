#!/usr/bin/env python3
"""
generate_erd.py - Genera ERD-01-modelo-datos.drawio.

Diagrama Entidad-Relacion del Sistema de Panol con polyglot por servicio:
- 8 bases PostgreSQL (database-per-service).
- Cada base agrupada como swimlane.
- Lineas solidas: FK dentro de la misma BD.
- Lineas punteadas: referencias logicas entre BDs (no son FK fisicas;
  los IDs viajan via eventos de dominio).

Uso:
    python3 generate_erd.py
"""
from __future__ import annotations
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent / "ERD-01-modelo-datos.drawio"

# ----- Estilos -----
DB_STYLE = "swimlane;fontSize=14;fontStyle=1;fillColor=#f5f5f5;strokeColor=#666666;swimlaneFillColor=#fafafa;startSize=28;rounded=1;"
TBL_HEADER = "<b style='font-size:12px;'>{name}</b><br/><hr style='margin:2px 0;'>"
TBL_STYLE_BUSINESS = "rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;align=left;verticalAlign=top;fontSize=10;spacingLeft=4;spacingTop=2;"
TBL_STYLE_INFRA    = "rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;align=left;verticalAlign=top;fontSize=9;spacingLeft=4;spacingTop=2;dashed=0;"
TBL_STYLE_PROJECTION = "rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;align=left;verticalAlign=top;fontSize=10;spacingLeft=4;spacingTop=2;"
EDGE_FK_LOCAL  = "endArrow=ERmany;startArrow=ERone;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
EDGE_FK_REMOTE = "endArrow=open;startArrow=none;html=1;dashed=1;dashPattern=4 4;strokeColor=#a64545;edgeStyle=orthogonalEdgeStyle;rounded=0;"
NOTE_STYLE = "shape=note;whiteSpace=wrap;html=1;fillColor=#fff8d0;strokeColor=#d6b656;align=left;verticalAlign=top;fontSize=10;spacingLeft=4;spacingTop=2;"

PAGE_W = 2400
PAGE_H = 1700

def attr(s: str) -> str:
    return escape(s, {'"': "&quot;"}).replace("\n", "&#10;")

def render_table(cid, name, fields, x, y, w=210, parent="1"):
    """Una tabla con nombre arriba y campos como rows."""
    rows = "".join(f"<div>{f}</div>" for f in fields)
    body = f"<b>{name}</b><hr style='margin:2px 0;border:0;border-top:1px solid #888;'>{rows}"
    style = TBL_STYLE_BUSINESS
    if name.startswith(("outbox_", "processed_", "audit_")):
        style = TBL_STYLE_INFRA
    elif name.startswith(("reporte_", "proyeccion_", "projection_")):
        style = TBL_STYLE_PROJECTION
    h = 22 + 14 * len(fields) + 6
    return (
        f'<mxCell id="{cid}" value="{attr(body)}" style="{style}" vertex="1" parent="{parent}">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
    ), h

def db_swimlane(cid, name, x, y, w, h):
    return (
        f'<mxCell id="{cid}" value="{attr(name)}" style="{DB_STYLE}" vertex="1" parent="1">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
    )

def edge(cid, src, tgt, label="", style=EDGE_FK_REMOTE):
    return (
        f'<mxCell id="{cid}" value="{attr(label)}" style="{style}" edge="1" parent="1" '
        f'source="{src}" target="{tgt}"><mxGeometry relative="1" as="geometry"/></mxCell>'
    )

# Pkey/Fkey shorthand
PK = "&#128273; "  # llave (key) icon
FK = "&#128279; "  # link icon

def main():
    cells = []
    # ===== Layout: 8 swimlanes en grid 4x2 =====
    # Cada swimlane: 580x470 aprox.
    SW = 560
    SH = 460
    GAP = 30
    LEFT = 30
    TOP  = 80

    # Posiciones de los 8 dbs
    db_positions = {
        "auth_db":         (LEFT,                TOP),
        "inventory_db":    (LEFT + (SW + GAP),   TOP),
        "request_db":      (LEFT + 2*(SW + GAP), TOP),
        "loan_db":         (LEFT + 3*(SW + GAP), TOP),
        "notification_db": (LEFT,                TOP + (SH + GAP)),
        "ai_risk_db":      (LEFT + (SW + GAP),   TOP + (SH + GAP)),
        "ai_assistant_db": (LEFT + 2*(SW + GAP), TOP + (SH + GAP)),
        "reports_db":      (LEFT + 3*(SW + GAP), TOP + (SH + GAP)),
    }

    db_titles = {
        "auth_db":         "auth_db  -  auth-svc",
        "inventory_db":    "inventory_db  -  inventory-svc",
        "request_db":      "request_db  -  request-svc",
        "loan_db":         "loan_db  -  loan-svc",
        "notification_db": "notification_db  -  notification-svc",
        "ai_risk_db":      "ai_risk_db  -  ai-risk-svc",
        "ai_assistant_db": "ai_assistant_db  -  ai-assistant-svc",
        "reports_db":      "reports_db  -  reports-svc",
    }

    for dbid, (x, y) in db_positions.items():
        cells.append(db_swimlane(f"db_{dbid}", db_titles[dbid], x, y, SW, SH))

    # Helper para posicionar tablas dentro de un swimlane (coords relativas al swimlane)
    def place_in(dbid, tables_layout):
        """tables_layout: list of (cid_suffix, name, fields, rel_x, rel_y, w)."""
        rendered = []
        for suffix, name, fields, rx, ry, w in tables_layout:
            x = rx
            y = ry
            cid = f"t_{dbid}_{suffix}"
            xml, _h = render_table(cid, name, fields, x, y, w=w)
            # parent = the swimlane
            xml = xml.replace('parent="1"', f'parent="db_{dbid}"', 1)
            rendered.append(xml)
        return rendered

    # ===== Tablas por db =====

    # auth_db
    cells.extend(place_in("auth_db", [
        ("users", "users", [
            f"{PK} id : UUID", "documento_tipo : VARCHAR", "documento_valor : VARCHAR",
            "nombre : TEXT", "email : TEXT", "role : ENUM",
            "carrera_id : UUID", "status : ENUM", "password_hash : TEXT",
            "pin_hash : TEXT?", "created_at : TIMESTAMPTZ", "updated_at : TIMESTAMPTZ",
        ], 20, 40, 240),
        ("user_blocks", "user_blocks", [
            f"{PK} id : UUID", f"{FK} user_id : UUID", "reason : ENUM",
            "motivo : TEXT", "blocked_by : UUID", "blocked_at : TIMESTAMPTZ",
            "unblocked_at : TIMESTAMPTZ?",
        ], 290, 40, 230),
        ("password_resets", "password_resets", [
            f"{PK} id : UUID", f"{FK} user_id : UUID",
            "token : TEXT", "expires_at : TIMESTAMPTZ",
        ], 20, 240, 240),
        ("login_attempts", "login_attempts", [
            f"{PK} id : UUID", "ip : INET", "user_identifier : TEXT",
            "count : INT", "last_attempt_at : TIMESTAMPTZ",
        ], 290, 240, 230),
        ("outbox", "outbox_events", [
            f"{PK} event_id : UUID", "routing_key : TEXT",
            "payload : JSONB", "published_at : TIMESTAMPTZ?",
        ], 20, 360, 240),
        ("processed", "processed_events", [
            f"{PK} event_id : UUID", "processed_at : TIMESTAMPTZ",
        ], 290, 360, 230),
    ]))

    # inventory_db
    cells.extend(place_in("inventory_db", [
        ("resources", "resources", [
            f"{PK} id : UUID", "nombre : TEXT", "categoria : TEXT",
            "detalle : TEXT", "stock_total : INT",
            "stock_max_historico : INT", "threshold_bajo_pct : FLOAT",
            "threshold_critico_pct : FLOAT", "estado : ENUM",
            "imagen_url : TEXT?", "codigo_externo : TEXT?", "version : INT",
        ], 20, 40, 250),
        ("reservations", "stock_reservations", [
            f"{PK} id : UUID", "request_id : UUID (logico)",
            f"{FK} recurso_id : UUID", "cantidad : INT",
            "estado : ENUM", "created_at : TIMESTAMPTZ",
            "expires_at : TIMESTAMPTZ",
        ], 290, 40, 250),
        ("movements", "stock_movements", [
            f"{PK} id : UUID", f"{FK} recurso_id : UUID",
            "delta : INT", "motivo : ENUM",
            "loan_id : UUID? (logico)", "performed_at : TIMESTAMPTZ",
            "performed_by : UUID",
        ], 20, 240, 250),
        ("reconciliation", "stock_reconciliation", [
            f"{PK} id : UUID", f"{FK} recurso_id : UUID",
            "discrepancia : INT", "detected_at : TIMESTAMPTZ",
        ], 290, 240, 250),
        ("outbox", "outbox_events", [f"{PK} event_id", "routing_key", "payload", "published_at?"], 20, 380, 250),
        ("processed", "processed_events", [f"{PK} event_id", "processed_at"], 290, 380, 250),
    ]))

    # request_db
    cells.extend(place_in("request_db", [
        ("requests", "requests", [
            f"{PK} id : UUID", "usuario_id : UUID (logico)",
            "operador_id : UUID? (logico)", "creada_por_operador : BOOL",
            "fecha_retiro : TIMESTAMPTZ", "tipo_prestamo : ENUM",
            "estado : ENUM", "riesgo_score : FLOAT?",
            "drivers : JSONB?", "ttl_expires_at : TIMESTAMPTZ?",
            "version : INT", "created_at : TIMESTAMPTZ",
        ], 20, 40, 250),
        ("items", "request_items", [
            f"{PK} id : UUID", f"{FK} request_id : UUID",
            "recurso_id : UUID (logico)", "cantidad_solicitada : INT",
            "cantidad_entregada : INT?",
        ], 290, 40, 250),
        ("approvals", "special_approvals", [
            f"{PK} id : UUID", f"{FK} request_id : UUID",
            "reviewer_id : UUID (logico)", "decision : ENUM",
            "motivo : TEXT", "decided_at : TIMESTAMPTZ",
        ], 20, 240, 250),
        ("drafts", "drafts", [
            f"{PK} id : UUID", "usuario_id : UUID (logico)",
            "payload : JSONB", "expires_at : TIMESTAMPTZ",
        ], 290, 240, 250),
        ("outbox", "outbox_events", [f"{PK} event_id", "routing_key", "payload", "published_at?"], 20, 380, 250),
        ("processed", "processed_events", [f"{PK} event_id", "processed_at"], 290, 380, 250),
    ]))

    # loan_db
    cells.extend(place_in("loan_db", [
        ("loans", "loans", [
            f"{PK} id : UUID", "ticket_id : UUID UNIQUE",
            "request_id : UUID (logico)", "usuario_id : UUID (logico)",
            "panolero_id : UUID (logico)", "fecha_limite : TIMESTAMPTZ",
            "issued_at : TIMESTAMPTZ", "returned_at : TIMESTAMPTZ?",
            "estado : ENUM", "version : INT",
        ], 20, 40, 250),
        ("items", "loan_items", [
            f"{PK} id : UUID", f"{FK} loan_id : UUID",
            "recurso_id : UUID (logico)", "cantidad : INT",
            "estado_devolucion : ENUM?", "observacion : TEXT?",
        ], 290, 40, 250),
        ("overdue", "overdue_flags", [
            f"{PK} id : UUID", f"{FK} loan_id : UUID",
            "usuario_id : UUID (logico)", "detected_at : TIMESTAMPTZ",
            "dias_atraso : INT",
        ], 20, 240, 250),
        ("outbox", "outbox_events", [f"{PK} event_id", "routing_key", "payload", "published_at?"], 20, 380, 250),
        ("processed", "processed_events", [f"{PK} event_id", "processed_at"], 290, 380, 250),
    ]))

    # notification_db
    cells.extend(place_in("notification_db", [
        ("notifications", "notifications", [
            f"{PK} id : UUID", "usuario_id : UUID (logico)",
            "tipo : ENUM", "canal : ENUM", "payload : JSONB",
            "read_at : TIMESTAMPTZ?", "delivered_at : TIMESTAMPTZ?",
            "ttl : INTERVAL", "created_at : TIMESTAMPTZ",
        ], 20, 40, 250),
        ("rules", "notification_rules", [
            f"{PK} id : UUID", "event_type : TEXT", "role : ENUM",
            "channel : ENUM", "template : TEXT",
        ], 290, 40, 250),
        ("tickets", "tickets", [
            f"{PK} id : UUID", "ticket_id : UUID UNIQUE",
            f"{FK} notification_id : UUID", "type : ENUM",
            "pdf_path : TEXT", "generated_at : TIMESTAMPTZ",
        ], 20, 240, 250),
        ("failed", "failed_deliveries", [
            f"{PK} id : UUID", f"{FK} notification_id : UUID",
            "reason : TEXT", "attempted_at : TIMESTAMPTZ",
        ], 290, 240, 250),
        ("outbox", "outbox_events", [f"{PK} event_id", "routing_key", "payload", "published_at?"], 20, 380, 250),
        ("processed", "processed_events", [f"{PK} event_id", "processed_at"], 290, 380, 250),
    ]))

    # ai_risk_db
    cells.extend(place_in("ai_risk_db", [
        ("profiles", "user_risk_profiles", [
            f"{PK} usuario_id : UUID (logico)",
            "features : JSONB",
            "last_computed_at : TIMESTAMPTZ",
        ], 20, 40, 250),
        ("scoring", "scoring_log", [
            f"{PK} id : UUID", "timestamp : TIMESTAMPTZ",
            "usuario_id : UUID (logico)", "request_id : UUID (logico)",
            "score : FLOAT", "drivers : JSONB",
            f"{FK} model_version : TEXT",
        ], 290, 40, 250),
        ("models", "models", [
            f"{PK} model_version : TEXT", "ruta_onnx : TEXT",
            "auc : FLOAT", "trained_at : TIMESTAMPTZ", "active : BOOL",
        ], 20, 240, 250),
        ("outbox", "outbox_events", [f"{PK} event_id", "routing_key", "payload", "published_at?"], 20, 380, 250),
        ("processed", "processed_events", [f"{PK} event_id", "processed_at"], 290, 380, 250),
    ]))

    # ai_assistant_db
    cells.extend(place_in("ai_assistant_db", [
        ("conversations", "conversations", [
            f"{PK} id : UUID", "usuario_id : UUID (logico)",
            "started_at : TIMESTAMPTZ", "last_turn_at : TIMESTAMPTZ",
            "tokens_used : INT", "closed_reason : ENUM?",
        ], 20, 40, 250),
        ("turns", "turns", [
            f"{PK} id : UUID", f"{FK} conversation_id : UUID",
            "role : ENUM", "content : TEXT",
            "tool_call_payload : JSONB?", "tokens_this_turn : INT",
        ], 290, 40, 250),
        ("mapping", "activity_resource_mapping", [
            f"{PK} id : UUID", "actividad : TEXT",
            "keywords : TEXT[]", "recurso_ids : UUID[]",
        ], 20, 240, 250),
        ("processed", "processed_events", [f"{PK} event_id", "processed_at"], 290, 240, 250),
    ]))

    # reports_db (CQRS read-model — todo proyecciones)
    cells.extend(place_in("reports_db", [
        ("rep_stock", "reporte_stock", [
            f"{PK} recurso_id : UUID", "categoria : TEXT",
            "stock_actual : INT", "disponible : INT",
            "ultima_actualizacion : TIMESTAMPTZ",
        ], 20, 40, 250),
        ("rep_solicitudes", "reporte_solicitudes_recurso", [
            f"{PK} (recurso_id, anio, mes)",
            "cantidad_solicitudes : INT",
            "cantidad_cancelaciones : INT",
            "cantidad_expiraciones : INT",
        ], 290, 40, 250),
        ("rep_devoluciones", "reporte_devoluciones_tardias", [
            f"{PK} loan_id : UUID", "recurso_id : UUID",
            "usuario_id : UUID", "dias_atraso : INT",
            "faltantes : INT", "fecha_devolucion : TIMESTAMPTZ",
        ], 20, 200, 250),
        ("rep_perdidas", "reporte_perdidas_recurso", [
            f"{PK} recurso_id : UUID", "cantidad_perdidas : INT",
            "cantidad_bajas : INT", "ultima_fecha_perdida : TIMESTAMPTZ",
        ], 290, 200, 250),
        ("proy_users", "proyeccion_usuarios", [
            f"{PK} usuario_id : UUID", "documento : TEXT", "nombre : TEXT",
            "role : ENUM", "carrera_id : UUID", "activo : BOOL",
        ], 20, 340, 250),
        ("proy_resources", "proyeccion_recursos", [
            f"{PK} recurso_id : UUID", "nombre : TEXT", "categoria : TEXT",
        ], 290, 340, 250),
    ]))

    # ===== FK locales (dentro del mismo db) =====
    local_fks = [
        ("fkl_1", "t_auth_db_users", "t_auth_db_user_blocks", ""),
        ("fkl_2", "t_auth_db_users", "t_auth_db_password_resets", ""),
        ("fkl_3", "t_inventory_db_resources", "t_inventory_db_reservations", ""),
        ("fkl_4", "t_inventory_db_resources", "t_inventory_db_movements", ""),
        ("fkl_5", "t_inventory_db_resources", "t_inventory_db_reconciliation", ""),
        ("fkl_6", "t_request_db_requests", "t_request_db_items", ""),
        ("fkl_7", "t_request_db_requests", "t_request_db_approvals", ""),
        ("fkl_8", "t_loan_db_loans", "t_loan_db_items", ""),
        ("fkl_9", "t_loan_db_loans", "t_loan_db_overdue", ""),
        ("fkl_10", "t_notification_db_notifications", "t_notification_db_tickets", ""),
        ("fkl_11", "t_notification_db_notifications", "t_notification_db_failed", ""),
        ("fkl_12", "t_ai_risk_db_models", "t_ai_risk_db_scoring", ""),
        ("fkl_13", "t_ai_assistant_db_conversations", "t_ai_assistant_db_turns", ""),
    ]
    for cid, src, tgt, lbl in local_fks:
        cells.append(edge(cid, src, tgt, lbl, EDGE_FK_LOCAL))

    # ===== Referencias logicas entre BDs (dashed) =====
    remote_refs = [
        ("ref_1",  "t_auth_db_users", "t_request_db_requests",         "usuario_id"),
        ("ref_2",  "t_request_db_requests", "t_loan_db_loans",         "request_id"),
        ("ref_3",  "t_request_db_requests", "t_inventory_db_reservations", "request_id"),
        ("ref_4",  "t_inventory_db_resources", "t_request_db_items",   "recurso_id"),
        ("ref_5",  "t_inventory_db_resources", "t_loan_db_items",      "recurso_id"),
        ("ref_6",  "t_auth_db_users", "t_loan_db_loans",               "usuario_id / panolero_id"),
        ("ref_7",  "t_auth_db_users", "t_loan_db_overdue",             "usuario_id"),
        ("ref_8",  "t_auth_db_users", "t_notification_db_notifications","usuario_id"),
        ("ref_9",  "t_auth_db_users", "t_ai_risk_db_profiles",         "usuario_id (PK)"),
        ("ref_10", "t_auth_db_users", "t_ai_risk_db_scoring",          "usuario_id"),
        ("ref_11", "t_request_db_requests", "t_ai_risk_db_scoring",    "request_id"),
        ("ref_12", "t_auth_db_users", "t_ai_assistant_db_conversations","usuario_id"),
        ("ref_13", "t_loan_db_loans", "t_inventory_db_movements",      "loan_id"),
        # CQRS proyecciones
        ("ref_14", "t_auth_db_users", "t_reports_db_proy_users",       "proyeccion CQRS"),
        ("ref_15", "t_inventory_db_resources", "t_reports_db_proy_resources", "proyeccion CQRS"),
    ]
    for cid, src, tgt, lbl in remote_refs:
        cells.append(edge(cid, src, tgt, lbl, EDGE_FK_REMOTE))

    # ===== Leyenda =====
    legend = (
        "<b>Convenciones</b><br/>"
        "&#128273; PK &#160; &#128279; FK<br/>"
        "<b>Lineas:</b><br/>"
        "- Solida (azul): FK fisica dentro de la BD<br/>"
        "- Punteada (rojiza): referencia logica entre BDs<br/>"
        "&#160; (los IDs viajan via eventos, no hay FK fisica)<br/>"
        "<b>Colores de tabla:</b><br/>"
        "- Azul: tabla de negocio<br/>"
        "- Verde: proyeccion / read-model (CQRS)<br/>"
        "- Amarillo: infraestructura (outbox / processed_events)<br/>"
    )
    cells.append(
        f'<mxCell id="legend" value="{attr(legend)}" style="{NOTE_STYLE}" vertex="1" parent="1">'
        f'<mxGeometry x="30" y="1480" width="500" height="180" as="geometry"/></mxCell>'
    )

    title_xml = (
        f'<mxCell id="title" value="ERD-01 - Modelo de datos (database-per-service)" '
        f'style="text;html=1;align=left;verticalAlign=middle;fontSize=22;fontStyle=1;" '
        f'vertex="1" parent="1">'
        f'<mxGeometry x="30" y="20" width="900" height="40" as="geometry"/></mxCell>'
    )
    subtitle = (
        f'<mxCell id="subtitle" value="8 bases PostgreSQL aisladas (database-per-service). '
        f'Las relaciones cross-BD son referencias logicas por evento, no FK fisicas." '
        f'style="text;html=1;align=left;verticalAlign=middle;fontSize=12;fontColor=#666666;" '
        f'vertex="1" parent="1">'
        f'<mxGeometry x="30" y="50" width="1400" height="22" as="geometry"/></mxCell>'
    )

    body = title_xml + subtitle + "".join(cells)

    out = (
        '<mxfile host="app.diagrams.net" agent="generator" type="device">\n'
        f'  <diagram id="erd-01" name="ERD-01 Modelo de datos">\n'
        f'    <mxGraphModel dx="2400" dy="1700" grid="1" gridSize="10" guides="1" '
        f'tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" '
        f'pageWidth="{PAGE_W}" pageHeight="{PAGE_H}" math="0" shadow="0">\n'
        '      <root>\n'
        '        <mxCell id="0"/>\n'
        '        <mxCell id="1" parent="0"/>\n'
        f'        {body}\n'
        '      </root>\n'
        '    </mxGraphModel>\n'
        '  </diagram>\n'
        '</mxfile>\n'
    )

    OUT.write_text(out, encoding="utf-8")
    print(f"  OK - {OUT.name} ({len(out)} bytes)")

if __name__ == "__main__":
    main()
