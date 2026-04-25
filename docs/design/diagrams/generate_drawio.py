#!/usr/bin/env python3
"""
generate_drawio.py — Generador de los 14 diagramas .drawio del Sistema de Pañol.

Produce archivos compatibles con draw.io / diagrams.net:
  - DC-01..DC-03  Diagramas estructurales UML
  - SEQ-01..SEQ-06 Diagramas de secuencia UML
  - EIP-01..EIP-05 Diagramas de integración con shapes oficiales Hohpe

Uso:
    python3 generate_drawio.py

Salida:
    Genera/sobrescribe los .drawio en este mismo directorio.

Notas:
- Las posiciones (x,y) son aproximadas; el usuario puede pulir el layout
  abriendo cada archivo en draw.io desktop o app.diagrams.net.
- Para EIP, draw.io trae las stencils oficiales de Hohpe en la librería
  "Enterprise Integration". Los shapes se referencian con
  "shape=mxgraph.eip.<nombre>".
- Para UML estándar, draw.io tiene shapes nativos (umlActor, umlBoundary,
  umlEntity, etc.) y para secuencia (umlLifeline, sync/async messages).
"""

from __future__ import annotations

import os
from pathlib import Path
from xml.sax.saxutils import escape

OUT_DIR = Path(__file__).parent

# ============================================================================
# Helpers de XML draw.io
# ============================================================================

def page_header(name: str, page_id: str, w: int = 1600, h: int = 1000) -> str:
    return (
        f'  <diagram id="{page_id}" name="{escape(name)}">\n'
        f'    <mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" '
        f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" '
        f'pageScale="1" pageWidth="{w}" pageHeight="{h}" math="0" shadow="0">\n'
        f'      <root>\n'
        f'        <mxCell id="0" />\n'
        f'        <mxCell id="1" parent="0" />\n'
    )

PAGE_FOOTER = (
    '      </root>\n'
    '    </mxGraphModel>\n'
    '  </diagram>\n'
)

def mxfile(pages_xml: str) -> str:
    return (
        '<mxfile host="app.diagrams.net" agent="generator" type="device">\n'
        f'{pages_xml}'
        '</mxfile>\n'
    )

_ATTR_ESCAPE = {'"': '&quot;', "'": '&apos;'}

def _attr(s: str) -> str:
    return escape(s, _ATTR_ESCAPE).replace("\n", "&#10;")

def cell_vertex(cid: str, value: str, style: str, x: int, y: int, w: int, h: int) -> str:
    v = _attr(value)
    return (
        f'        <mxCell id="{cid}" value="{v}" style="{style}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
        f'        </mxCell>\n'
    )

def cell_edge(cid: str, source: str, target: str, label: str = "", style: str = "endArrow=classic;html=1;") -> str:
    v = _attr(label)
    return (
        f'        <mxCell id="{cid}" value="{v}" style="{style}" edge="1" parent="1" '
        f'source="{source}" target="{target}">\n'
        f'          <mxGeometry relative="1" as="geometry" />\n'
        f'        </mxCell>\n'
    )

def cell_floating_edge(cid: str, x1: int, y1: int, x2: int, y2: int, label: str = "", style: str = "endArrow=classic;html=1;") -> str:
    v = _attr(label)
    return (
        f'        <mxCell id="{cid}" value="{v}" style="{style}" edge="1" parent="1">\n'
        f'          <mxGeometry relative="1" as="geometry">\n'
        f'            <mxPoint x="{x1}" y="{y1}" as="sourcePoint" />\n'
        f'            <mxPoint x="{x2}" y="{y2}" as="targetPoint" />\n'
        f'          </mxGeometry>\n'
        f'        </mxCell>\n'
    )

# Estilos reutilizables (UML)
STYLE_BOX = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
    "fontSize=12;fontStyle=1;align=center;verticalAlign=middle;"
)
STYLE_BOX_INTERNAL = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;"
    "fontSize=11;align=center;verticalAlign=middle;"
)
STYLE_BOX_EXTERNAL = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;"
    "fontSize=11;align=center;verticalAlign=middle;"
)
STYLE_BOX_DB = (
    "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;"
    "size=15;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;align=center;"
)
STYLE_BOX_BROKER = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;"
    "fontSize=12;fontStyle=1;align=center;verticalAlign=middle;"
)
STYLE_ACTOR = (
    "shape=umlActor;verticalLabelPosition=bottom;labelBackgroundColor=none;"
    "verticalAlign=top;html=1;outlineConnect=0;fontSize=12;fontStyle=1;"
)
STYLE_NOTE = (
    "shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;darkOpacity=0.05;"
    "fillColor=#fff2cc;strokeColor=#d6b656;fontSize=10;align=left;"
)
STYLE_BOUNDARY = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#666;dashed=1;"
    "fontSize=14;fontStyle=1;verticalAlign=top;align=left;spacingTop=6;spacingLeft=10;"
)
STYLE_TITLE = (
    "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;"
    "whiteSpace=wrap;rounded=0;fontSize=18;fontStyle=1;"
)
STYLE_SUBTITLE = (
    "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;"
    "whiteSpace=wrap;rounded=0;fontSize=12;fontStyle=2;"
)
STYLE_LIFELINE = (
    "shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;"
    "container=1;dropTarget=0;collapsible=0;recursiveResize=0;outlineConnect=0;"
    "fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;fontStyle=1;"
)
STYLE_ACTIVATION = (
    "html=1;points=[];perimeter=orthogonalPerimeter;outlineConnect=0;targetShapes=umlLifeline;"
    "fillColor=#fff;strokeColor=#000;"
)
STYLE_MSG_SYNC = (
    "html=1;verticalAlign=bottom;startSize=8;endSize=8;exitX=1;exitY=0;exitDx=0;exitDy=0;"
    "entryX=0;entryY=0;entryDx=0;entryDy=0;jettySize=auto;orthogonalLoop=1;endArrow=block;"
    "endFill=1;fontSize=11;"
)
STYLE_MSG_ASYNC = (
    "html=1;verticalAlign=bottom;startSize=8;endSize=8;jettySize=auto;orthogonalLoop=1;"
    "endArrow=open;endFill=0;fontSize=11;"
)
STYLE_MSG_RETURN = (
    "html=1;verticalAlign=bottom;startSize=8;endSize=8;jettySize=auto;orthogonalLoop=1;"
    "endArrow=open;endFill=0;dashed=1;fontSize=11;"
)
STYLE_FRAGMENT = (
    "shape=umlFrame;whiteSpace=wrap;html=1;pointerEvents=0;fillColor=none;strokeColor=#999;"
    "fontSize=11;fontStyle=1;align=left;verticalAlign=top;"
)

# Estilos EIP (oficiales Hohpe en draw.io)
def eip_style(shape: str) -> str:
    return (
        f"sketch=0;html=1;dashed=0;strokeColor=#000;fillColor=#fff;"
        f"shape=mxgraph.eip.{shape};fontSize=11;align=center;"
    )

# ============================================================================
# DC-01 — Diagrama de Contexto del Sistema
# ============================================================================

def dc_01_contexto():
    cells = []
    cells.append(cell_vertex("title", "DC-01 — Diagrama de Contexto del Sistema de Pañol",
                             STYLE_TITLE, 200, 20, 1200, 30))
    cells.append(cell_vertex("subtitle", "Sistema como caja única, actores y sistemas externos",
                             STYLE_SUBTITLE, 200, 50, 1200, 20))

    # Sistema central
    cells.append(cell_vertex("sys", "Sistema de Pañol\n(UNAB Viña del Mar)\n\n• Préstamos\n• Inventario\n• Notificaciones\n• IA (scoring + asistente)",
                             STYLE_BOX, 600, 380, 360, 220))

    # Actores
    cells.append(cell_vertex("a_alumno", "Alumno", STYLE_ACTOR, 130, 200, 40, 60))
    cells.append(cell_vertex("a_panolero", "Pañolero", STYLE_ACTOR, 130, 470, 40, 60))
    cells.append(cell_vertex("a_admin", "Administrador", STYLE_ACTOR, 130, 720, 40, 60))

    # Sistemas externos
    cells.append(cell_vertex("ext_sso", "LDAP / SSO\nUNAB",
                             STYLE_BOX_EXTERNAL, 1300, 220, 200, 90))
    cells.append(cell_vertex("ext_openai", "OpenAI API\n(Asistente IA)",
                             STYLE_BOX_EXTERNAL, 1300, 420, 200, 90))
    cells.append(cell_vertex("ext_email", "Servicio de email\n(diferido — fuera de MVP)",
                             STYLE_BOX_EXTERNAL, 1300, 620, 200, 90))

    # Conexiones
    cells.append(cell_edge("e1", "a_alumno", "sys", "Solicita préstamo,\nrecibe ticket"))
    cells.append(cell_edge("e2", "a_panolero", "sys", "Valida solicitudes,\nmaterializa préstamos,\nregistra devoluciones"))
    cells.append(cell_edge("e3", "a_admin", "sys", "Gestiona usuarios,\ncatálogo, parámetros"))

    cells.append(cell_edge("e4", "sys", "ext_sso", "Autentica usuarios"))
    cells.append(cell_edge("e5", "sys", "ext_openai", "Function calling +\nMCP tools"))
    cells.append(cell_edge("e6", "sys", "ext_email", "Notificaciones\n(post-MVP)",
                           "endArrow=classic;html=1;dashed=1;"))

    # Nota
    cells.append(cell_vertex("note1",
                             "Frontera del sistema:\nlo que está dentro del recuadro central\nes alcance del proyecto.",
                             STYLE_NOTE, 600, 700, 360, 80))

    return [("DC-01", "Contexto", "".join(cells))]


# ============================================================================
# DC-02 — Diagrama de Componentes / Topología de Microservicios
# ============================================================================

def dc_02_componentes():
    cells = []
    cells.append(cell_vertex("title", "DC-02 — Componentes / Topología de Microservicios",
                             STYLE_TITLE, 200, 20, 1200, 30))
    cells.append(cell_vertex("subtitle", "8 microservicios + frontends + RabbitMQ + PostgreSQL por servicio",
                             STYLE_SUBTITLE, 200, 50, 1200, 20))

    # Capa frontends
    cells.append(cell_vertex("front_box", "Capa de presentación", STYLE_BOUNDARY,
                             80, 110, 1440, 110))
    cells.append(cell_vertex("front_web", "web-portal\n(Next.js 14)\nUI alumno + admin",
                             STYLE_BOX_INTERNAL, 200, 140, 240, 70))
    cells.append(cell_vertex("front_totem", "totem\n(Vite + React)\nUI pañolero",
                             STYLE_BOX_INTERNAL, 1100, 140, 240, 70))

    # API Gateway
    cells.append(cell_vertex("gw", "api-gateway\n(NestJS BFF)\nautenticación + ruteo",
                             STYLE_BOX_INTERNAL, 660, 280, 280, 70))

    # Capa microservicios
    cells.append(cell_vertex("svc_box", "Capa de microservicios (NestJS 10 + Prisma 5)",
                             STYLE_BOUNDARY, 80, 380, 1440, 240))

    cells.append(cell_vertex("svc_auth", "auth-svc\nUsuarios + roles + JWT",
                             STYLE_BOX_INTERNAL, 110, 420, 200, 70))
    cells.append(cell_vertex("svc_inv", "inventory-svc\nCatálogo + stock",
                             STYLE_BOX_INTERNAL, 330, 420, 200, 70))
    cells.append(cell_vertex("svc_req", "request-svc\nSolicitudes + workflow",
                             STYLE_BOX_INTERNAL, 550, 420, 200, 70))
    cells.append(cell_vertex("svc_loan", "loan-svc\nPréstamos + devoluciones",
                             STYLE_BOX_INTERNAL, 770, 420, 200, 70))
    cells.append(cell_vertex("svc_notif", "notification-svc\nIn-app + tickets PDF",
                             STYLE_BOX_INTERNAL, 990, 420, 200, 70))
    cells.append(cell_vertex("svc_risk", "ai-risk-svc\nScoring (RF + ONNX)",
                             STYLE_BOX_INTERNAL, 1210, 420, 200, 70))
    cells.append(cell_vertex("svc_assist", "ai-assistant-svc\nMCP + OpenAI",
                             STYLE_BOX_INTERNAL, 550, 520, 200, 70))

    # Bases de datos
    cells.append(cell_vertex("db_box", "Persistencia (PostgreSQL 16 — schema por servicio)",
                             STYLE_BOUNDARY, 80, 660, 1440, 130))
    cells.append(cell_vertex("db_auth", "auth_db", STYLE_BOX_DB, 130, 700, 140, 70))
    cells.append(cell_vertex("db_inv", "inventory_db", STYLE_BOX_DB, 350, 700, 140, 70))
    cells.append(cell_vertex("db_req", "request_db", STYLE_BOX_DB, 570, 700, 140, 70))
    cells.append(cell_vertex("db_loan", "loan_db", STYLE_BOX_DB, 790, 700, 140, 70))
    cells.append(cell_vertex("db_notif", "notification_db", STYLE_BOX_DB, 1010, 700, 140, 70))
    cells.append(cell_vertex("db_risk", "risk_db", STYLE_BOX_DB, 1230, 700, 140, 70))

    # Broker
    cells.append(cell_vertex("broker", "RabbitMQ 3.13\ndomain.events (topic)\ndomain.commands (direct)\ndomain.delayed (delayed)\ndomain.dlx (fanout)",
                             STYLE_BOX_BROKER, 1300, 280, 220, 80))

    # Cliente externo
    cells.append(cell_vertex("openai", "OpenAI API",
                             STYLE_BOX_EXTERNAL, 800, 540, 160, 50))

    # Conexiones síncronas (HTTP)
    cells.append(cell_edge("c_web_gw", "front_web", "gw", "HTTPS / JWT",
                           "endArrow=classic;html=1;"))
    cells.append(cell_edge("c_totem_gw", "front_totem", "gw", "HTTPS / JWT",
                           "endArrow=classic;html=1;"))
    for sid in ["svc_auth", "svc_inv", "svc_req", "svc_loan", "svc_notif", "svc_risk"]:
        cells.append(cell_edge(f"c_gw_{sid}", "gw", sid, "",
                               "endArrow=classic;html=1;dashed=0;"))
    cells.append(cell_edge("c_gw_assist", "gw", "svc_assist", "",
                           "endArrow=classic;html=1;dashed=0;"))

    # Conexiones a BD
    pairs_db = [("svc_auth","db_auth"), ("svc_inv","db_inv"), ("svc_req","db_req"),
                ("svc_loan","db_loan"), ("svc_notif","db_notif"), ("svc_risk","db_risk")]
    for sid, did in pairs_db:
        cells.append(cell_edge(f"c_{sid}_{did}", sid, did, "",
                               "endArrow=open;endFill=0;html=1;"))

    # Conexiones al broker (asíncronas — eventos)
    for sid in ["svc_auth", "svc_inv", "svc_req", "svc_loan", "svc_notif", "svc_risk", "svc_assist"]:
        cells.append(cell_edge(f"c_{sid}_broker", sid, "broker", "",
                               "endArrow=classic;html=1;dashed=1;strokeColor=#d79b00;"))

    # ai-assistant -> OpenAI
    cells.append(cell_edge("c_assist_openai", "svc_assist", "openai", "function calling",
                           "endArrow=classic;html=1;"))

    # Leyenda
    cells.append(cell_vertex("leyenda",
                             "Leyenda:\n— sólida = HTTP síncrono\n— punteada naranja = evento asíncrono (AMQP)\n— sólida fina = lectura/escritura BD",
                             STYLE_NOTE, 90, 820, 360, 90))

    return [("DC-02", "Componentes", "".join(cells))]


# ============================================================================
# DC-03 — Diagrama de Despliegue
# ============================================================================

def dc_03_despliegue():
    cells = []
    cells.append(cell_vertex("title", "DC-03 — Diagrama de Despliegue",
                             STYLE_TITLE, 200, 20, 1200, 30))
    cells.append(cell_vertex("subtitle", "Topología de despliegue cloud-agnóstica con Docker Compose / K8s",
                             STYLE_SUBTITLE, 200, 50, 1200, 20))

    # Cliente
    cells.append(cell_vertex("client_box", "<<device>> Navegador / Tótem",
                             STYLE_BOUNDARY, 80, 110, 320, 200))
    cells.append(cell_vertex("client_web", "Navegador del alumno\n(Chrome / Firefox)",
                             STYLE_BOX_INTERNAL, 100, 150, 280, 60))
    cells.append(cell_vertex("client_totem", "Tablet / kiosko\n(navegador kiosco)",
                             STYLE_BOX_INTERNAL, 100, 230, 280, 60))

    # Ingress / Reverse proxy
    cells.append(cell_vertex("ingress", "<<node>> Reverse Proxy / Ingress\n(Traefik o nginx)",
                             STYLE_BOX_INTERNAL, 470, 150, 280, 60))

    # Host de aplicaciones
    cells.append(cell_vertex("app_host", "<<node>> Host de aplicaciones (Docker host / cluster K8s)",
                             STYLE_BOUNDARY, 80, 350, 1440, 380))

    # Frontends (containers)
    cells.append(cell_vertex("c_web", "<<container>>\nweb-portal:latest\n(Next.js)",
                             STYLE_BOX_INTERNAL, 110, 390, 220, 60))
    cells.append(cell_vertex("c_totem", "<<container>>\ntotem:latest\n(Vite SPA)",
                             STYLE_BOX_INTERNAL, 350, 390, 220, 60))
    cells.append(cell_vertex("c_gw", "<<container>>\napi-gateway:latest",
                             STYLE_BOX_INTERNAL, 590, 390, 220, 60))

    # Microservicios
    services = [
        ("c_auth", "auth-svc"), ("c_inv", "inventory-svc"),
        ("c_req", "request-svc"), ("c_loan", "loan-svc"),
        ("c_notif", "notification-svc"), ("c_risk", "ai-risk-svc"),
        ("c_assist", "ai-assistant-svc"),
    ]
    for i, (cid, name) in enumerate(services):
        col = i % 4
        row = i // 4
        x = 110 + col * 240
        y = 480 + row * 80
        cells.append(cell_vertex(cid, f"<<container>>\n{name}:latest", STYLE_BOX_INTERNAL, x, y, 220, 60))

    # Datos
    cells.append(cell_vertex("data_host", "<<node>> Host de datos",
                             STYLE_BOUNDARY, 80, 760, 700, 200))
    cells.append(cell_vertex("c_pg", "<<container>>\npostgres:16\n(schemas: auth, inventory,\nrequest, loan, notification, risk)",
                             STYLE_BOX_DB, 130, 800, 280, 110))
    cells.append(cell_vertex("c_volumes", "Volumen persistente\n/var/lib/postgresql",
                             STYLE_BOX_INTERNAL, 450, 820, 250, 60))

    # Broker host
    cells.append(cell_vertex("broker_host", "<<node>> Host de mensajería",
                             STYLE_BOUNDARY, 820, 760, 380, 200))
    cells.append(cell_vertex("c_rabbit", "<<container>>\nrabbitmq:3.13-management\n+ rabbitmq_delayed_message_exchange",
                             STYLE_BOX_BROKER, 850, 800, 320, 100))

    # Observabilidad
    cells.append(cell_vertex("obs_host", "<<node>> Observabilidad",
                             STYLE_BOUNDARY, 1240, 760, 280, 200))
    cells.append(cell_vertex("c_otel", "<<container>>\notel-collector",
                             STYLE_BOX_INTERNAL, 1260, 800, 240, 50))
    cells.append(cell_vertex("c_grafana", "<<container>>\nGrafana + Tempo",
                             STYLE_BOX_INTERNAL, 1260, 870, 240, 50))

    # Conexiones
    cells.append(cell_edge("c1", "client_web", "ingress", "HTTPS"))
    cells.append(cell_edge("c2", "client_totem", "ingress", "HTTPS"))
    cells.append(cell_edge("c3", "ingress", "c_web", "/portal"))
    cells.append(cell_edge("c4", "ingress", "c_totem", "/totem"))
    cells.append(cell_edge("c5", "ingress", "c_gw", "/api"))

    cells.append(cell_edge("c6", "c_pg", "c_volumes", "mount",
                           "endArrow=open;endFill=0;html=1;"))

    # Nota
    cells.append(cell_vertex("note_dep",
                             "Cloud-agnóstico:\ndocker-compose para desarrollo / mesa redonda;\nmismo Compose desplegable a EKS/AKS/GKE\nsin cambios de código.",
                             STYLE_NOTE, 1240, 50, 280, 90))

    return [("DC-03", "Despliegue", "".join(cells))]


# ============================================================================
# Helpers para diagramas de secuencia
# ============================================================================

def make_sequence(title: str, subtitle: str, lifelines, messages, fragments=None, notes=None):
    """
    lifelines = lista de tuplas (id, label, x)
    messages = lista de dicts: {id, src, tgt, y, label, kind}
        kind: 'sync' | 'async' | 'return' | 'self'
    fragments = lista de dicts: {id, x, y, w, h, label}
    notes = lista de dicts: {id, x, y, w, h, text}
    """
    cells = []
    cells.append(cell_vertex("title", title, STYLE_TITLE, 100, 10, 1400, 30))
    cells.append(cell_vertex("subtitle", subtitle, STYLE_SUBTITLE, 100, 40, 1400, 20))

    LIFELINE_TOP = 80
    LIFELINE_HEIGHT = 800
    LIFELINE_WIDTH = 130

    # Lifelines
    for lid, label, x in lifelines:
        cells.append(cell_vertex(lid, label, STYLE_LIFELINE,
                                 x, LIFELINE_TOP, LIFELINE_WIDTH, LIFELINE_HEIGHT))

    # Buscar coordenadas centrales de cada lifeline
    lifeline_x = {lid: x + LIFELINE_WIDTH // 2 for lid, _, x in lifelines}

    # Fragmentos
    if fragments:
        for f in fragments:
            cells.append(cell_vertex(f["id"], f["label"], STYLE_FRAGMENT,
                                     f["x"], f["y"], f["w"], f["h"]))

    # Notas
    if notes:
        for n in notes:
            cells.append(cell_vertex(n["id"], n["text"], STYLE_NOTE,
                                     n["x"], n["y"], n["w"], n["h"]))

    # Mensajes
    for m in messages:
        kind = m.get("kind", "sync")
        if kind == "sync":
            style = "html=1;verticalAlign=bottom;startSize=8;endSize=8;jettySize=auto;orthogonalLoop=1;endArrow=block;endFill=1;fontSize=11;"
        elif kind == "async":
            style = "html=1;verticalAlign=bottom;startSize=8;endSize=8;jettySize=auto;orthogonalLoop=1;endArrow=open;endFill=0;fontSize=11;"
        elif kind == "return":
            style = "html=1;verticalAlign=bottom;startSize=8;endSize=8;jettySize=auto;orthogonalLoop=1;endArrow=open;endFill=0;dashed=1;fontSize=11;"
        elif kind == "self":
            style = "html=1;verticalAlign=bottom;startSize=8;endSize=8;jettySize=auto;orthogonalLoop=1;endArrow=block;endFill=1;curved=0;fontSize=11;"
        else:
            style = "endArrow=classic;html=1;"

        if kind == "self":
            x = lifeline_x[m["src"]]
            y = m["y"]
            cells.append(cell_floating_edge(m["id"], x, y, x + 60, y + 30, m["label"], style))
            # cerrar el self con punto de retorno
        else:
            x1 = lifeline_x[m["src"]]
            x2 = lifeline_x[m["tgt"]]
            y = m["y"]
            cells.append(cell_floating_edge(m["id"], x1, y, x2, y, m["label"], style))

    return "".join(cells)


# ============================================================================
# SEQ-01 — Login y autenticación (CU1)
# ============================================================================

def seq_01_login():
    lifelines = [
        ("ll_user",  "Alumno : Usuario",            150),
        ("ll_web",   "web-portal",                  340),
        ("ll_gw",    "api-gateway",                 530),
        ("ll_auth",  "auth-svc",                    720),
        ("ll_db",    "auth_db : PostgreSQL",        910),
    ]
    messages = [
        {"id":"m1", "src":"ll_user", "tgt":"ll_web",  "y":140, "label":"1: ingresa email + password", "kind":"sync"},
        {"id":"m2", "src":"ll_web",  "tgt":"ll_gw",   "y":180, "label":"2: POST /auth/login", "kind":"sync"},
        {"id":"m3", "src":"ll_gw",   "tgt":"ll_auth", "y":220, "label":"3: forwardLogin()", "kind":"sync"},
        {"id":"m4", "src":"ll_auth", "tgt":"ll_db",   "y":260, "label":"4: SELECT user WHERE email=?", "kind":"sync"},
        {"id":"m5", "src":"ll_db",   "tgt":"ll_auth", "y":300, "label":"5: user + hash", "kind":"return"},
        {"id":"m6", "src":"ll_auth", "tgt":"ll_auth", "y":340, "label":"6: bcrypt.compare()", "kind":"self"},
        {"id":"m7", "src":"ll_auth", "tgt":"ll_auth", "y":400, "label":"7: sign JWT (15m) + refresh (7d)", "kind":"self"},
        {"id":"m8", "src":"ll_auth", "tgt":"ll_gw",   "y":460, "label":"8: { access_token, refresh_token, user }", "kind":"return"},
        {"id":"m9", "src":"ll_gw",   "tgt":"ll_web",  "y":500, "label":"9: 200 OK + cookies httpOnly", "kind":"return"},
        {"id":"m10","src":"ll_web",  "tgt":"ll_user", "y":540, "label":"10: redirige a /home", "kind":"return"},
    ]
    fragments = [
        {"id":"frag_alt", "x":110, "y":100, "w":960, "h":480,
         "label":"alt — credenciales válidas / inválidas"},
        {"id":"frag_else", "x":110, "y":600, "w":960, "h":120,
         "label":"[else credenciales inválidas]"},
    ]
    messages_else = [
        {"id":"me1", "src":"ll_auth", "tgt":"ll_gw",  "y":640, "label":"401 Unauthorized", "kind":"return"},
        {"id":"me2", "src":"ll_gw",   "tgt":"ll_web", "y":670, "label":"401 + mensaje de error", "kind":"return"},
        {"id":"me3", "src":"ll_web",  "tgt":"ll_user","y":700, "label":"muestra error", "kind":"return"},
    ]
    body = make_sequence(
        "SEQ-01 — Login y autenticación (CU1)",
        "JWT (access 15m) + refresh token (7d). RF.AU.1, RF.AU.2.",
        lifelines, messages + messages_else, fragments=fragments
    )
    return [("SEQ-01", "Login (CU1)", body)]


# ============================================================================
# SEQ-02 — Crear solicitud de préstamo (CU2)
# ============================================================================

def seq_02_solicitud():
    lifelines = [
        ("ll_alumno", "Alumno",                          150),
        ("ll_web",    "web-portal",                      330),
        ("ll_gw",     "api-gateway",                     510),
        ("ll_req",    "request-svc",                     690),
        ("ll_inv",    "inventory-svc",                   870),
        ("ll_broker", "RabbitMQ\ndomain.delayed +\ndomain.events", 1050),
        ("ll_notif",  "notification-svc",                1230),
    ]
    messages = [
        {"id":"m1", "src":"ll_alumno", "tgt":"ll_web", "y":140, "label":"1: arma carrito (items + fechas)", "kind":"sync"},
        {"id":"m2", "src":"ll_web",    "tgt":"ll_gw",  "y":175, "label":"2: POST /requests", "kind":"sync"},
        {"id":"m3", "src":"ll_gw",     "tgt":"ll_req", "y":210, "label":"3: createRequest()", "kind":"sync"},
        {"id":"m4", "src":"ll_req",    "tgt":"ll_inv", "y":245, "label":"4: GET /stock?items=[...] (Request-Reply)", "kind":"sync"},
        {"id":"m5", "src":"ll_inv",    "tgt":"ll_req", "y":280, "label":"5: { item: stock disponible }", "kind":"return"},
        {"id":"m6", "src":"ll_req",    "tgt":"ll_req", "y":315, "label":"6: validar reglas (RC.16) + persistir PENDIENTE_VALIDACION", "kind":"self"},
        {"id":"m7", "src":"ll_req",    "tgt":"ll_broker","y":380, "label":"7: publish request.created\nx-message-ttl=15min", "kind":"async"},
        {"id":"m8", "src":"ll_req",    "tgt":"ll_gw",  "y":420, "label":"8: 201 Created (requestId)", "kind":"return"},
        {"id":"m9", "src":"ll_gw",     "tgt":"ll_web", "y":455, "label":"9: 201 + tracking link", "kind":"return"},
        {"id":"m10","src":"ll_web",    "tgt":"ll_alumno","y":490, "label":"10: muestra solicitud en estado PENDIENTE", "kind":"return"},
        {"id":"m11","src":"ll_broker", "tgt":"ll_notif","y":540, "label":"11: deliver request.created (binding)", "kind":"async"},
        {"id":"m12","src":"ll_notif",  "tgt":"ll_notif","y":580, "label":"12: crear notificación in-app al pañolero", "kind":"self"},
    ]
    notes = [
        {"id":"note_ttl", "x":1100, "y":600, "w":380, "h":80,
         "text":"TTL de reserva (Message Expiration):\nsi request no es validada en 15 min,\nDLX dispara compensación (ver SEQ-06)."}
    ]
    body = make_sequence(
        "SEQ-02 — Crear solicitud de préstamo (CU2)",
        "Patrones: Request-Reply (verifica stock), Publish-Subscribe (notifica pañolero), Message Expiration (TTL reserva).",
        lifelines, messages, notes=notes
    )
    return [("SEQ-02", "Crear solicitud (CU2)", body)]


# ============================================================================
# SEQ-03 — Validación + materialización en tótem (CU3) con scoring (CU6)
# ============================================================================

def seq_03_materializar():
    lifelines = [
        ("ll_panol",  "Pañolero",            120),
        ("ll_totem",  "totem",               280),
        ("ll_gw",     "api-gateway",         440),
        ("ll_loan",   "loan-svc",            600),
        ("ll_risk",   "ai-risk-svc",         760),
        ("ll_inv",    "inventory-svc",       920),
        ("ll_broker", "RabbitMQ",            1080),
        ("ll_notif",  "notification-svc",    1240),
    ]
    messages = [
        {"id":"m1", "src":"ll_panol", "tgt":"ll_totem", "y":140, "label":"1: selecciona requestId", "kind":"sync"},
        {"id":"m2", "src":"ll_totem", "tgt":"ll_gw",    "y":170, "label":"2: POST /loans/materialize", "kind":"sync"},
        {"id":"m3", "src":"ll_gw",    "tgt":"ll_loan",  "y":200, "label":"3: materialize(requestId)", "kind":"sync"},
        {"id":"m4", "src":"ll_loan", "tgt":"ll_risk",   "y":235, "label":"4: score(userId, items)", "kind":"sync"},
        {"id":"m5", "src":"ll_risk", "tgt":"ll_risk",   "y":275, "label":"5: features + RF.predict (ONNX)", "kind":"self"},
        {"id":"m6", "src":"ll_risk", "tgt":"ll_loan",   "y":330, "label":"6: { score: 0..1, drivers: [...] }", "kind":"return"},
        {"id":"m7", "src":"ll_loan", "tgt":"ll_loan",   "y":370, "label":"7: aplica RC.11 (umbrales) + persiste préstamo", "kind":"self"},
        {"id":"m8", "src":"ll_loan", "tgt":"ll_broker", "y":425, "label":"8: publish loan.created", "kind":"async"},
        {"id":"m9", "src":"ll_broker","tgt":"ll_inv",   "y":465, "label":"9: deliver loan.created", "kind":"async"},
        {"id":"m10","src":"ll_inv",  "tgt":"ll_inv",    "y":505, "label":"10: stock -= cantidad", "kind":"self"},
        {"id":"m11","src":"ll_broker","tgt":"ll_notif", "y":545, "label":"11: deliver loan.created", "kind":"async"},
        {"id":"m12","src":"ll_notif","tgt":"ll_notif",  "y":585, "label":"12: genera ticket PDF + notif in-app", "kind":"self"},
        {"id":"m13","src":"ll_loan", "tgt":"ll_gw",     "y":640, "label":"13: 201 { loanId, ticketUrl }", "kind":"return"},
        {"id":"m14","src":"ll_gw",   "tgt":"ll_totem",  "y":670, "label":"14: 201 + URL del ticket", "kind":"return"},
        {"id":"m15","src":"ll_totem","tgt":"ll_panol",  "y":700, "label":"15: muestra QR / imprime", "kind":"return"},
    ]
    notes = [
        {"id":"note_saga", "x":110, "y":740, "w":440, "h":80,
         "text":"Saga coreografiada: cada servicio reacciona\na eventos sin orquestador. Compensación\nsi inventory-svc rechaza (ver SEQ-06)."},
        {"id":"note_score", "x":700, "y":740, "w":380, "h":80,
         "text":"RC.11: score>=0.7 acepta automático;\n0.4..0.7 requiere PIN del pañolero;\n<0.4 bloquea (override admin)."},
    ]
    body = make_sequence(
        "SEQ-03 — Validación + materialización (CU3 + scoring CU6)",
        "Patrones: Request-Reply (scoring), Publish-Subscribe (loan.created), Saga coreografiada.",
        lifelines, messages, notes=notes
    )
    return [("SEQ-03", "Materializar préstamo (CU3+CU6)", body)]


# ============================================================================
# SEQ-04 — Devolución y cierre del ciclo (CU4)
# ============================================================================

def seq_04_devolucion():
    lifelines = [
        ("ll_panol",  "Pañolero",            150),
        ("ll_totem",  "totem",               340),
        ("ll_gw",     "api-gateway",         530),
        ("ll_loan",   "loan-svc",            720),
        ("ll_broker", "RabbitMQ",            910),
        ("ll_inv",    "inventory-svc",       1100),
        ("ll_notif",  "notification-svc",    1290),
    ]
    messages = [
        {"id":"m1", "src":"ll_panol", "tgt":"ll_totem", "y":140, "label":"1: escanea QR del préstamo", "kind":"sync"},
        {"id":"m2", "src":"ll_totem", "tgt":"ll_gw",    "y":175, "label":"2: POST /loans/{id}/return", "kind":"sync"},
        {"id":"m3", "src":"ll_gw",    "tgt":"ll_loan",  "y":210, "label":"3: closeLoan(loanId)", "kind":"sync"},
        {"id":"m4", "src":"ll_loan",  "tgt":"ll_loan",  "y":245, "label":"4: marca DEVUELTO + calcula atraso (RC.18)", "kind":"self"},
        {"id":"m5", "src":"ll_loan",  "tgt":"ll_broker","y":300, "label":"5: publish loan.closed { onTime: bool, daysLate }", "kind":"async"},
        {"id":"m6", "src":"ll_broker","tgt":"ll_inv",   "y":340, "label":"6: deliver loan.closed", "kind":"async"},
        {"id":"m7", "src":"ll_inv",   "tgt":"ll_inv",   "y":380, "label":"7: stock += cantidad (reposición)", "kind":"self"},
        {"id":"m8", "src":"ll_broker","tgt":"ll_notif", "y":420, "label":"8: deliver loan.closed", "kind":"async"},
        {"id":"m9", "src":"ll_notif", "tgt":"ll_notif", "y":460, "label":"9: notif. al alumno + actualiza historial", "kind":"self"},
        {"id":"m10","src":"ll_loan",  "tgt":"ll_gw",    "y":510, "label":"10: 200 OK", "kind":"return"},
        {"id":"m11","src":"ll_gw",    "tgt":"ll_totem", "y":540, "label":"11: 200 OK", "kind":"return"},
        {"id":"m12","src":"ll_totem", "tgt":"ll_panol", "y":570, "label":"12: muestra confirmación", "kind":"return"},
    ]
    fragments = [
        {"id":"frag_partial", "x":110, "y":600, "w":1310, "h":120,
         "label":"opt — devolución parcial / con daños"},
    ]
    messages_partial = [
        {"id":"mp1", "src":"ll_panol", "tgt":"ll_totem", "y":640, "label":"alt: registra cantidad parcial / daño", "kind":"sync"},
        {"id":"mp2", "src":"ll_totem", "tgt":"ll_loan",  "y":670, "label":"PATCH /loans/{id}/partial", "kind":"sync"},
        {"id":"mp3", "src":"ll_loan",  "tgt":"ll_broker","y":700, "label":"publish loan.partial-return", "kind":"async"},
    ]
    body = make_sequence(
        "SEQ-04 — Devolución y cierre del ciclo (CU4)",
        "Cierra la saga: stock regresa, alumno notificado, score histórico actualizado (entra en RF.IA.5).",
        lifelines, messages + messages_partial, fragments=fragments
    )
    return [("SEQ-04", "Devolución (CU4)", body)]


# ============================================================================
# SEQ-05 — Asistente conversacional con MCP (CU7)
# ============================================================================

def seq_05_asistente():
    lifelines = [
        ("ll_alumno",  "Alumno",          150),
        ("ll_web",     "web-portal",      340),
        ("ll_gw",      "api-gateway",     530),
        ("ll_assist",  "ai-assistant-svc",720),
        ("ll_openai",  "OpenAI API",      910),
        ("ll_inv",     "inventory-svc\n(via MCP tool)", 1100),
        ("ll_req",     "request-svc\n(via MCP tool)",   1290),
    ]
    messages = [
        {"id":"m1","src":"ll_alumno","tgt":"ll_web","y":140,"label":"1: \"necesito multímetro y protoboard para mañana\"","kind":"sync"},
        {"id":"m2","src":"ll_web","tgt":"ll_gw","y":175,"label":"2: POST /assistant/chat","kind":"sync"},
        {"id":"m3","src":"ll_gw","tgt":"ll_assist","y":210,"label":"3: chat({userId, message})","kind":"sync"},
        {"id":"m4","src":"ll_assist","tgt":"ll_assist","y":245,"label":"4: guardrail: usuario bloqueado? (RC.15)","kind":"self"},
        {"id":"m5","src":"ll_assist","tgt":"ll_openai","y":295,"label":"5: chat.completions(messages, tools=MCP)","kind":"sync"},
        {"id":"m6","src":"ll_openai","tgt":"ll_assist","y":335,"label":"6: tool_call: search_catalog(\"multímetro\")","kind":"return"},
        {"id":"m7","src":"ll_assist","tgt":"ll_inv","y":370,"label":"7: invoca tool MCP","kind":"sync"},
        {"id":"m8","src":"ll_inv","tgt":"ll_assist","y":405,"label":"8: [item: multimetro-fluke, stock: 4]","kind":"return"},
        {"id":"m9","src":"ll_assist","tgt":"ll_openai","y":440,"label":"9: tool_response","kind":"sync"},
        {"id":"m10","src":"ll_openai","tgt":"ll_assist","y":475,"label":"10: tool_call: check_availability(itemIds, fechas)","kind":"return"},
        {"id":"m11","src":"ll_assist","tgt":"ll_inv","y":510,"label":"11: invoca tool MCP","kind":"sync"},
        {"id":"m12","src":"ll_inv","tgt":"ll_assist","y":545,"label":"12: { disponible: true }","kind":"return"},
        {"id":"m13","src":"ll_assist","tgt":"ll_openai","y":580,"label":"13: tool_response","kind":"sync"},
        {"id":"m14","src":"ll_openai","tgt":"ll_assist","y":615,"label":"14: respuesta natural + propuesta create_request","kind":"return"},
        {"id":"m15","src":"ll_assist","tgt":"ll_gw","y":650,"label":"15: { reply, suggestedAction }","kind":"return"},
        {"id":"m16","src":"ll_gw","tgt":"ll_web","y":685,"label":"16: 200 OK","kind":"return"},
        {"id":"m17","src":"ll_web","tgt":"ll_alumno","y":720,"label":"17: muestra respuesta + botón \"crear solicitud\"","kind":"return"},
    ]
    notes = [
        {"id":"note_mcp","x":110,"y":770,"w":480,"h":80,
         "text":"MCP expone 6 tools: search_catalog,\ncheck_availability, create_request,\nget_user_history, get_blocked_status, get_score_estimate."},
        {"id":"note_block","x":620,"y":770,"w":420,"h":80,
         "text":"Si guardrail detecta bloqueo (RC.15), el flujo termina\nen paso 4 con respuesta de error sin llamar a OpenAI."},
    ]
    body = make_sequence(
        "SEQ-05 — Asistente conversacional con MCP (CU7)",
        "Function calling de OpenAI invoca tools MCP del backend. Guardrails RC.15.",
        lifelines, messages, notes=notes
    )
    return [("SEQ-05", "Asistente MCP (CU7)", body)]


# ============================================================================
# SEQ-06 — Compensación: TTL de reserva vencido
# ============================================================================

def seq_06_compensacion():
    lifelines = [
        ("ll_req",    "request-svc",                       150),
        ("ll_delayed","Exchange\ndomain.delayed",          340),
        ("ll_dlx",    "Exchange\ndomain.dlx",              530),
        ("ll_inv",    "inventory-svc",                     720),
        ("ll_notif",  "notification-svc",                  910),
        ("ll_alumno", "Alumno\n(via in-app)",              1100),
    ]
    messages = [
        {"id":"m1","src":"ll_req","tgt":"ll_delayed","y":140,"label":"1: publish request.created\nx-delay=15min","kind":"async"},
        {"id":"m2","src":"ll_delayed","tgt":"ll_delayed","y":190,"label":"2: tiempo transcurrido sin validación","kind":"self"},
        {"id":"m3","src":"ll_delayed","tgt":"ll_dlx","y":250,"label":"3: TTL expirado → DLX captura","kind":"async"},
        {"id":"m4","src":"ll_dlx","tgt":"ll_req","y":300,"label":"4: deliver request.expired","kind":"async"},
        {"id":"m5","src":"ll_req","tgt":"ll_req","y":340,"label":"5: cancela request → estado EXPIRADA","kind":"self"},
        {"id":"m6","src":"ll_req","tgt":"ll_dlx","y":400,"label":"6: publish request.cancelled","kind":"async"},
        {"id":"m7","src":"ll_dlx","tgt":"ll_inv","y":440,"label":"7: deliver request.cancelled","kind":"async"},
        {"id":"m8","src":"ll_inv","tgt":"ll_inv","y":480,"label":"8: libera reserva (no había stock comprometido aún)","kind":"self"},
        {"id":"m9","src":"ll_dlx","tgt":"ll_notif","y":540,"label":"9: deliver request.cancelled","kind":"async"},
        {"id":"m10","src":"ll_notif","tgt":"ll_alumno","y":580,"label":"10: notif. \"tu solicitud expiró por falta de validación\"","kind":"async"},
    ]
    notes = [
        {"id":"note_idem","x":110,"y":640,"w":520,"h":80,
         "text":"Idempotent Receiver: si el evento se reentrega,\nrequest-svc consulta processed_events por\ncorrelation_id y descarta duplicados."},
        {"id":"note_compensation","x":680,"y":640,"w":420,"h":80,
         "text":"Esta es la compensación principal de la saga.\nAplica también a fallos downstream\n(p.ej. inventory-svc rechaza por stock 0)."},
    ]
    body = make_sequence(
        "SEQ-06 — Compensación: TTL de reserva vencido",
        "Patrón Message Expiration + Dead Letter Channel + Idempotent Receiver.",
        lifelines, messages, notes=notes
    )
    return [("SEQ-06", "Compensación TTL (saga)", body)]


# ============================================================================
# Diagramas EIP — usando shapes Hohpe oficiales
# ============================================================================

def eip_node(cid: str, label: str, x: int, y: int, w: int, h: int, shape: str):
    """Crea un nodo con shape EIP de Hohpe."""
    return cell_vertex(cid, label, eip_style(shape), x, y, w, h)


# ============================================================================
# EIP-01 — Topología general de mensajería
# ============================================================================

def eip_01_topologia():
    cells = []
    cells.append(cell_vertex("title", "EIP-01 — Topología general de mensajería",
                             STYLE_TITLE, 100, 10, 1400, 30))
    cells.append(cell_vertex("subtitle",
                             "Bus RabbitMQ con 4 exchanges. Bindings dirigen eventos a colas por servicio.",
                             STYLE_SUBTITLE, 100, 40, 1400, 20))

    # Productores (servicios)
    producers = [
        ("p_auth",   "auth-svc",          80, 100),
        ("p_inv",    "inventory-svc",     80, 200),
        ("p_req",    "request-svc",       80, 300),
        ("p_loan",   "loan-svc",          80, 400),
        ("p_risk",   "ai-risk-svc",       80, 500),
        ("p_notif",  "notification-svc",  80, 600),
    ]
    for pid, lbl, x, y in producers:
        cells.append(cell_vertex(pid, lbl, STYLE_BOX_INTERNAL, x, y, 180, 60))

    # Exchanges (Message Channel / Pub-Sub Channel — shape ipoChannel)
    exchanges = [
        ("ex_events",  "domain.events\n(topic)\n— Pub-Sub Channel",     360, 120, "publishSubscribe"),
        ("ex_cmd",     "domain.commands\n(direct)\n— Point-to-Point",   360, 250, "pointToPointChannel"),
        ("ex_delayed", "domain.delayed\n(x-delayed-message)\n— Message Expiration", 360, 380, "messageExpiration"),
        ("ex_dlx",     "domain.dlx\n(fanout)\n— Dead Letter Channel",   360, 510, "deadLetterChannel"),
    ]
    for eid, lbl, x, y, shape in exchanges:
        cells.append(eip_node(eid, lbl, x, y, 240, 90, shape))

    # Colas y consumidores
    consumers = [
        ("c_notif",  "queue.notification\n→ notification-svc",    700, 100),
        ("c_risk",   "queue.risk\n→ ai-risk-svc",                 700, 200),
        ("c_inv",    "queue.inventory\n→ inventory-svc",          700, 300),
        ("c_auth",   "queue.auth\n→ auth-svc",                    700, 400),
        ("c_req",    "queue.req-cmd\n→ request-svc (commands)",   1000, 250),
        ("c_dlq",    "queue.dlq\n→ DLQ handler / dashboard",      1000, 510),
        ("c_expired","queue.expired\n→ request-svc (compensación)",1000, 380),
    ]
    for qid, lbl, x, y in consumers:
        cells.append(eip_node(qid, lbl, x, y, 240, 70, "messageChannel"))

    # Conexiones productores → exchanges
    cells.append(cell_edge("e_p_auth_ev",  "p_auth",  "ex_events", "user.*",  "endArrow=classic;html=1;"))
    cells.append(cell_edge("e_p_inv_ev",   "p_inv",   "ex_events", "stock.*", "endArrow=classic;html=1;"))
    cells.append(cell_edge("e_p_req_ev",   "p_req",   "ex_events", "request.*", "endArrow=classic;html=1;"))
    cells.append(cell_edge("e_p_loan_ev",  "p_loan",  "ex_events", "loan.*",  "endArrow=classic;html=1;"))
    cells.append(cell_edge("e_p_risk_ev",  "p_risk",  "ex_events", "risk.scored", "endArrow=classic;html=1;"))
    cells.append(cell_edge("e_p_notif_ev", "p_notif", "ex_events", "notification.delivered", "endArrow=classic;html=1;"))

    cells.append(cell_edge("e_p_loan_cmd","p_loan",   "ex_cmd", "scoreUser", "endArrow=classic;html=1;dashed=1;"))
    cells.append(cell_edge("e_p_req_del", "p_req",    "ex_delayed", "TTL=15min", "endArrow=classic;html=1;dashed=1;"))

    # Exchange events → colas
    cells.append(cell_edge("e_ev_notif", "ex_events", "c_notif", "*.created / *.closed",
                           "endArrow=classic;html=1;"))
    cells.append(cell_edge("e_ev_risk", "ex_events", "c_risk", "loan.closed",
                           "endArrow=classic;html=1;"))
    cells.append(cell_edge("e_ev_inv", "ex_events", "c_inv", "loan.created /\nloan.closed",
                           "endArrow=classic;html=1;"))
    cells.append(cell_edge("e_ev_auth", "ex_events", "c_auth", "loan.overdue",
                           "endArrow=classic;html=1;"))

    # commands → request
    cells.append(cell_edge("e_cmd_req", "ex_cmd", "c_req", "command",
                           "endArrow=classic;html=1;"))

    # delayed → dlx (cuando expira)
    cells.append(cell_edge("e_del_dlx", "ex_delayed", "ex_dlx", "expirado",
                           "endArrow=classic;html=1;dashed=1;"))
    cells.append(cell_edge("e_dlx_exp", "ex_dlx", "c_expired", "request.expired",
                           "endArrow=classic;html=1;"))
    cells.append(cell_edge("e_dlx_dlq", "ex_dlx", "c_dlq", "fallos\nirrecuperables",
                           "endArrow=classic;html=1;"))

    cells.append(cell_vertex("note",
                             "Shapes oficiales Hohpe (draw.io / mxgraph.eip):\n• Pub-Sub Channel (events)\n• Point-to-Point Channel (commands)\n• Message Expiration (delayed)\n• Dead Letter Channel (dlx)",
                             STYLE_NOTE, 100, 730, 480, 110))

    return [("EIP-01", "Topología mensajería", "".join(cells))]


# ============================================================================
# EIP-02 — Publish-Subscribe + Content-Based Router
# ============================================================================

def eip_02_pubsub_router():
    cells = []
    cells.append(cell_vertex("title", "EIP-02 — Publish-Subscribe + Content-Based Router",
                             STYLE_TITLE, 100, 10, 1400, 30))
    cells.append(cell_vertex("subtitle",
                             "request.created se publica una vez; routing keys lo dirigen a múltiples consumidores.",
                             STYLE_SUBTITLE, 100, 40, 1400, 20))

    # Publisher
    cells.append(cell_vertex("pub", "request-svc\n(Publisher)",
                             STYLE_BOX_INTERNAL, 100, 250, 200, 80))

    # Mensaje
    cells.append(eip_node("msg", "request.created\nrouting_key=request.created.high_priority",
                          340, 260, 280, 70, "message"))

    # Pub-Sub Channel
    cells.append(eip_node("pubsub", "domain.events\nPublish-Subscribe Channel\n(topic)",
                          680, 240, 240, 110, "publishSubscribe"))

    # Content-Based Router
    cells.append(eip_node("router", "Content-Based Router\n(routing key matching)",
                          980, 240, 220, 110, "contentBasedRouter"))

    # Subscribers
    subs = [
        ("sub_notif", "notification-svc\n(in-app + ticket PDF)",   1280, 100),
        ("sub_risk",  "ai-risk-svc\n(actualiza features)",         1280, 220),
        ("sub_auth",  "auth-svc\n(actualiza historial usuario)",   1280, 340),
        ("sub_audit", "audit log\n(persistencia compliance)",      1280, 460),
    ]
    for sid, lbl, x, y in subs:
        cells.append(cell_vertex(sid, lbl, STYLE_BOX_INTERNAL, x, y, 220, 70))

    # Edges
    cells.append(cell_edge("e1","pub","msg","publish()","endArrow=classic;html=1;"))
    cells.append(cell_edge("e2","msg","pubsub","","endArrow=classic;html=1;"))
    cells.append(cell_edge("e3","pubsub","router","","endArrow=classic;html=1;"))
    cells.append(cell_edge("e4","router","sub_notif","[*.created.*]","endArrow=classic;html=1;"))
    cells.append(cell_edge("e5","router","sub_risk","[*.created.*]","endArrow=classic;html=1;"))
    cells.append(cell_edge("e6","router","sub_auth","[*.created.high_priority]","endArrow=classic;html=1;"))
    cells.append(cell_edge("e7","router","sub_audit","[#] (catch-all)","endArrow=classic;html=1;"))

    # Notas
    cells.append(cell_vertex("note1",
                             "Pub-Sub:\nUn evento publicado se entrega a TODOS los consumidores\nsuscritos. Cada uno tiene su propia cola y avanza independiente.",
                             STYLE_NOTE, 100, 450, 480, 90))
    cells.append(cell_vertex("note2",
                             "Content-Based Router:\nLas reglas viven en los bindings de RabbitMQ\n(routing_key + pattern). Cambiar reglas no requiere\nmodificar el publisher.",
                             STYLE_NOTE, 100, 560, 480, 100))

    return [("EIP-02", "Pub-Sub + CBR", "".join(cells))]


# ============================================================================
# EIP-03 — Message Expiration + Dead Letter Channel
# ============================================================================

def eip_03_expiration_dlc():
    cells = []
    cells.append(cell_vertex("title", "EIP-03 — Message Expiration + Dead Letter Channel",
                             STYLE_TITLE, 100, 10, 1400, 30))
    cells.append(cell_vertex("subtitle",
                             "Reserva con TTL automático. Si vence, DLX la captura y dispara compensación.",
                             STYLE_SUBTITLE, 100, 40, 1400, 20))

    # Producer
    cells.append(cell_vertex("pub","request-svc\n(crea reserva)",
                             STYLE_BOX_INTERNAL, 100, 250, 180, 80))

    # Mensaje con expiración
    cells.append(eip_node("msg","request.created\nx-delay=900000ms\n(15 min)",
                          320, 240, 220, 100, "messageExpiration"))

    # Delayed Exchange
    cells.append(eip_node("delayed","domain.delayed\n(x-delayed-message)",
                          580, 250, 220, 80, "messageChannel"))

    # Branch normal
    cells.append(cell_vertex("branch_ok","Pañolero valida\nantes de TTL",
                             STYLE_BOX_INTERNAL, 880, 130, 200, 70))
    cells.append(eip_node("queue_normal","queue.totem\n(sigue al flujo normal)",
                          1140, 130, 220, 70, "messageChannel"))

    # Branch expiración
    cells.append(eip_node("dlx","domain.dlx\nDead Letter Channel\n(fanout)",
                          880, 360, 220, 90, "deadLetterChannel"))
    cells.append(eip_node("queue_expired","queue.expired\n→ request.expired",
                          1140, 370, 220, 70, "messageChannel"))
    cells.append(cell_vertex("compensador","request-svc\n(handler de compensación)",
                             STYLE_BOX_INTERNAL, 1400, 370, 200, 70))

    # Edges
    cells.append(cell_edge("e1","pub","msg","publish()","endArrow=classic;html=1;"))
    cells.append(cell_edge("e2","msg","delayed","","endArrow=classic;html=1;"))
    cells.append(cell_edge("e3","delayed","branch_ok","[antes de TTL]\nrelease normal","endArrow=classic;html=1;dashed=0;"))
    cells.append(cell_edge("e4","branch_ok","queue_normal","","endArrow=classic;html=1;"))
    cells.append(cell_edge("e5","delayed","dlx","[TTL vencido]\nentrega a DLX","endArrow=classic;html=1;dashed=1;strokeColor=#b85450;"))
    cells.append(cell_edge("e6","dlx","queue_expired","","endArrow=classic;html=1;"))
    cells.append(cell_edge("e7","queue_expired","compensador","consume","endArrow=classic;html=1;"))

    # Notas
    cells.append(cell_vertex("note1",
                             "Message Expiration:\nEl broker (no la app) gestiona el tiempo. Si el consumer\nno valida en 15 min, el mensaje se considera 'muerto' y\npasa al DLX automáticamente.",
                             STYLE_NOTE, 100, 500, 480, 100))
    cells.append(cell_vertex("note2",
                             "Dead Letter Channel:\nNo es 'errores que tirar', es 'eventos que requieren\nprocesamiento alternativo' (compensación, alertas,\nDLQ humano).",
                             STYLE_NOTE, 600, 500, 480, 100))

    return [("EIP-03", "Expiration + DLC", "".join(cells))]


# ============================================================================
# EIP-04 — Request-Reply + Correlation Identifier
# ============================================================================

def eip_04_request_reply():
    cells = []
    cells.append(cell_vertex("title", "EIP-04 — Request-Reply + Correlation Identifier",
                             STYLE_TITLE, 100, 10, 1400, 30))
    cells.append(cell_vertex("subtitle",
                             "loan-svc consulta scoring a ai-risk-svc de forma asincrónica con correlación.",
                             STYLE_SUBTITLE, 100, 40, 1400, 20))

    # Requester
    cells.append(cell_vertex("requester","loan-svc\n(Requester)",
                             STYLE_BOX_INTERNAL, 100, 280, 180, 90))

    # Request msg
    cells.append(eip_node("req_msg",
                          "request:\n• payload: {userId, items}\n• correlation_id: uuid-1\n• reply_to: queue.reply.loan",
                          320, 130, 280, 110, "documentMessage"))

    cells.append(eip_node("req_channel","queue.commands.risk\n(Point-to-Point)",
                          640, 130, 220, 80, "pointToPointChannel"))

    # Replier
    cells.append(cell_vertex("replier","ai-risk-svc\n(Replier)",
                             STYLE_BOX_INTERNAL, 900, 280, 180, 90))

    # Correlation
    cells.append(eip_node("corr","Correlation Identifier",
                          580, 290, 220, 70, "correlationIdentifier"))

    # Reply msg
    cells.append(eip_node("rep_msg",
                          "reply:\n• payload: {score, drivers}\n• correlation_id: uuid-1",
                          320, 480, 280, 100, "documentMessage"))
    cells.append(eip_node("rep_channel","queue.reply.loan\n(temporal/exclusive)",
                          640, 490, 220, 80, "messageChannel"))

    # Flujos
    cells.append(cell_edge("e1","requester","req_msg","1: build request","endArrow=classic;html=1;"))
    cells.append(cell_edge("e2","req_msg","req_channel","2: send","endArrow=classic;html=1;"))
    cells.append(cell_edge("e3","req_channel","replier","3: consume","endArrow=classic;html=1;"))
    cells.append(cell_edge("e4","replier","rep_msg","4: build reply\n(copia correlation_id)","endArrow=classic;html=1;"))
    cells.append(cell_edge("e5","rep_msg","rep_channel","5: send to reply_to","endArrow=classic;html=1;"))
    cells.append(cell_edge("e6","rep_channel","requester","6: consume\n(filter by correlation_id)","endArrow=classic;html=1;"))
    cells.append(cell_edge("e7","corr","req_msg","tag","endArrow=open;endFill=0;html=1;dashed=1;"))
    cells.append(cell_edge("e8","corr","rep_msg","tag","endArrow=open;endFill=0;html=1;dashed=1;"))

    cells.append(cell_vertex("note",
                             "Request-Reply asincrónico:\nNo bloquea hilo. Patrón usado para scoring porque\nel modelo puede tardar 100-500ms; mantenemos\noperación no-bloqueante.\n\nCorrelation Identifier:\nGarantiza que la reply llega al request correcto\ncuando hay múltiples requests simultáneos.",
                             STYLE_NOTE, 1140, 280, 380, 200))

    return [("EIP-04", "Request-Reply", "".join(cells))]


# ============================================================================
# EIP-05 — Transactional Outbox + Idempotent Receiver
# ============================================================================

def eip_05_outbox_idempotent():
    cells = []
    cells.append(cell_vertex("title", "EIP-05 — Transactional Outbox + Idempotent Receiver",
                             STYLE_TITLE, 100, 10, 1400, 30))
    cells.append(cell_vertex("subtitle",
                             "Garantiza atomicidad escritura-publicación y deduplicación en el consumidor.",
                             STYLE_SUBTITLE, 100, 40, 1400, 20))

    # Servicio productor (loan-svc)
    cells.append(cell_vertex("svc_prod","loan-svc",
                             STYLE_BOX_INTERNAL, 80, 220, 160, 80))

    # Transacción local (BD del servicio)
    cells.append(cell_vertex("tx_box","Transacción local — loan_db",
                             STYLE_BOUNDARY, 280, 100, 460, 320))
    cells.append(cell_vertex("tbl_loans","tabla loans\n(estado del préstamo)",
                             STYLE_BOX_DB, 320, 150, 200, 90))
    cells.append(cell_vertex("tbl_outbox","tabla outbox_events\n(eventos pendientes)",
                             STYLE_BOX_DB, 540, 150, 180, 90))

    # Relay
    cells.append(cell_vertex("relay","outbox-relay\n(polling cada 1s)",
                             STYLE_BOX_INTERNAL, 800, 220, 180, 80))

    # Broker
    cells.append(eip_node("broker","domain.events\n(Pub-Sub)",
                          1020, 220, 200, 80, "publishSubscribe"))

    # Consumer
    cells.append(cell_vertex("svc_cons","notification-svc\n(consumer)",
                             STYLE_BOX_INTERNAL, 1280, 220, 180, 80))

    # Idempotent receiver (tabla processed_events)
    cells.append(eip_node("idempotent","Idempotent Receiver",
                          1280, 360, 200, 70, "idempotentReceiver"))
    cells.append(cell_vertex("tbl_processed","tabla processed_events\n(correlation_id PK)",
                             STYLE_BOX_DB, 1280, 470, 200, 90))

    # Edges
    cells.append(cell_edge("e1","svc_prod","tbl_loans","INSERT/UPDATE","endArrow=classic;html=1;"))
    cells.append(cell_edge("e2","svc_prod","tbl_outbox","INSERT event","endArrow=classic;html=1;"))
    cells.append(cell_edge("e3","tbl_outbox","relay","SELECT * WHERE published=false","endArrow=classic;html=1;dashed=1;"))
    cells.append(cell_edge("e4","relay","broker","publish()","endArrow=classic;html=1;"))
    cells.append(cell_edge("e5","relay","tbl_outbox","UPDATE published=true","endArrow=open;html=1;dashed=1;"))
    cells.append(cell_edge("e6","broker","svc_cons","deliver","endArrow=classic;html=1;"))
    cells.append(cell_edge("e7","svc_cons","idempotent","check","endArrow=classic;html=1;"))
    cells.append(cell_edge("e8","idempotent","tbl_processed","SELECT WHERE correlation_id=?","endArrow=open;html=1;dashed=1;"))

    cells.append(cell_vertex("note1",
                             "Transactional Outbox:\nLa misma transacción de BD que cambia el estado\ndel agregado escribe el evento. Si la TX falla,\nel evento NO existe — sin posibilidad de inconsistencia.",
                             STYLE_NOTE, 80, 600, 480, 110))
    cells.append(cell_vertex("note2",
                             "Idempotent Receiver:\nSi el broker re-entrega, el consumer chequea\nprocessed_events. Si correlation_id ya existe,\ndescarta sin reprocesar — entrega 'al menos una vez' se vuelve\nefectivamente 'exactamente una vez'.",
                             STYLE_NOTE, 600, 600, 480, 110))

    return [("EIP-05", "Outbox + Idempotent Rcv", "".join(cells))]


# ============================================================================
# Render
# ============================================================================

def write_diagram(filename: str, pages):
    """pages = lista de (page_id, page_name, cells_xml)"""
    body = ""
    for pid, pname, cells in pages:
        body += page_header(pname, pid)
        body += cells
        body += PAGE_FOOTER
    out = mxfile(body)
    path = OUT_DIR / filename
    path.write_text(out, encoding="utf-8")
    print(f"  ✓ {filename}")


def main():
    print("Generando diagramas .drawio...")
    diagrams = [
        ("DC-01-contexto.drawio",                 dc_01_contexto()),
        ("DC-02-componentes.drawio",              dc_02_componentes()),
        ("DC-03-despliegue.drawio",               dc_03_despliegue()),
        ("SEQ-01-login.drawio",                   seq_01_login()),
        ("SEQ-02-crear-solicitud.drawio",         seq_02_solicitud()),
        ("SEQ-03-materializar-prestamo.drawio",   seq_03_materializar()),
        ("SEQ-04-devolucion.drawio",              seq_04_devolucion()),
        ("SEQ-05-asistente-mcp.drawio",           seq_05_asistente()),
        ("SEQ-06-compensacion-ttl.drawio",        seq_06_compensacion()),
        ("EIP-01-topologia-mensajeria.drawio",    eip_01_topologia()),
        ("EIP-02-pubsub-content-router.drawio",   eip_02_pubsub_router()),
        ("EIP-03-message-expiration-dlc.drawio",  eip_03_expiration_dlc()),
        ("EIP-04-request-reply-correlation.drawio", eip_04_request_reply()),
        ("EIP-05-outbox-idempotent-receiver.drawio", eip_05_outbox_idempotent()),
    ]
    for fname, pages in diagrams:
        write_diagram(fname, pages)
    print(f"\nOK — {len(diagrams)} diagramas generados en {OUT_DIR}")


if __name__ == "__main__":
    main()
