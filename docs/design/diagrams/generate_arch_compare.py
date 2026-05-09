#!/usr/bin/env python3
"""
generate_arch_compare.py - Genera ARCH-01-demo-vs-produccion.drawio.

Comparacion side-by-side de la arquitectura del demo (mock-first, in-memory,
HTTP sincrono) vs la arquitectura objetivo de produccion (Postgres-per-service,
RabbitMQ con 4 exchanges, EIP completos).

Mismo layout vertical en ambas columnas (UI -> Gateway -> Servicios -> 
Persistencia -> Bus) para comparar capa a capa.

Color coding:
  - Verde:  componente compartido entre demo y prod
  - Amarillo: solo en demo (shortcut)
  - Naranja: solo en prod
  - Rojo:   diferencia clave (sync vs async, etc.)
"""
from __future__ import annotations
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent / "ARCH-01-demo-vs-produccion.drawio"

# ----- Estilos -----
COMMON = "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;align=center;verticalAlign=middle;fontSize=11;fontStyle=1;"
DEMO   = "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;align=center;verticalAlign=middle;fontSize=11;"
PROD   = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;align=center;verticalAlign=middle;fontSize=11;"
DIFF   = "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;align=center;verticalAlign=middle;fontSize=10;fontStyle=2;"
SECTION = "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#999999;dashed=1;align=left;verticalAlign=top;fontSize=11;fontStyle=1;fontColor=#666666;spacingLeft=8;spacingTop=4;"
COL_DEMO = "swimlane;fontSize=18;fontStyle=1;fillColor=#fff8d0;strokeColor=#d6b656;swimlaneFillColor=#fffef5;startSize=40;rounded=1;"
COL_PROD = "swimlane;fontSize=18;fontStyle=1;fillColor=#ffe6cc;strokeColor=#d79b00;swimlaneFillColor=#fffaf2;startSize=40;rounded=1;"
NOTE = "shape=note;whiteSpace=wrap;html=1;fillColor=#fff8d0;strokeColor=#d6b656;align=left;verticalAlign=top;fontSize=10;spacingLeft=4;spacingTop=2;"
EDGE_HTTP_SYNC = "endArrow=classic;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;strokeWidth=2;"
EDGE_AMQP = "endArrow=classic;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;dashed=1;strokeColor=#d79b00;strokeWidth=2;"

PAGE_W = 2400
PAGE_H = 1500

def attr(s):
    return escape(s, {'"': "&quot;"}).replace("\n", "&#10;")

def cell(cid, value, style, x, y, w, h, parent="1"):
    return (
        f'<mxCell id="{cid}" value="{attr(value)}" style="{style}" vertex="1" parent="{parent}">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'
    )

def edge(cid, src, tgt, label="", style=EDGE_HTTP_SYNC):
    return (
        f'<mxCell id="{cid}" value="{attr(label)}" style="{style}" edge="1" parent="1" '
        f'source="{src}" target="{tgt}"><mxGeometry relative="1" as="geometry"/></mxCell>'
    )

def main():
    cells = []

    # Titulo principal
    cells.append(cell("title", "Arquitectura: Demo vs Produccion (mismas capas, diferentes mecanismos)",
                      "text;html=1;align=center;verticalAlign=middle;fontSize=20;fontStyle=1;",
                      40, 10, 2320, 32))
    cells.append(cell("subtitle",
        "feature/app-demo (mock-first, in-memory, HTTP sincrono) vs docs/architecture/ (Postgres-per-service, RabbitMQ, EIP completos)",
        "text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor=#666666;",
        40, 44, 2320, 22))

    # ===== Columna DEMO =====
    DEMO_X = 40
    DEMO_W = 1140
    cells.append(cell("col_demo", "DEMO - feature/app-demo",
                      COL_DEMO, DEMO_X, 80, DEMO_W, 1340))

    # ===== Columna PROD =====
    PROD_X = 1220
    PROD_W = 1140
    cells.append(cell("col_prod", "PRODUCCION - docs/architecture/",
                      COL_PROD, PROD_X, 80, PROD_W, 1340))

    # Helper: parent override para cells dentro de las columnas
    def in_col(cells_list, col_id):
        out = []
        for c in cells_list:
            out.append(c.replace('parent="1"', f'parent="{col_id}"', 1))
        return out

    # ===== Capa 1: Frontends =====
    sec_y = 50
    sec_h = 130
    demo_cells = []
    demo_cells.append(cell("sec_demo_ui", "Frontends (UI)", SECTION, 20, sec_y, 1100, sec_h))
    demo_cells.append(cell("ui_demo_portal", "web-portal\nAngular 19 SPA\n:4200\n(SSR deshabilitado)",
                            DEMO, 60, sec_y+30, 220, 90))
    demo_cells.append(cell("ui_demo_totem", "totem\nAngular 19 SPA\n:4201\n(PIN-only login)",
                            DEMO, 320, sec_y+30, 220, 90))
    demo_cells.append(cell("ui_demo_design", "Design tokens:\nLujo Academico Editorial (portal)\nPizarra de Laboratorio (totem)\nVanilla CSS + Variables",
                            DEMO, 580, sec_y+30, 280, 90))
    demo_cells.append(cell("ui_demo_state", "Reactividad:\nSignals + computed\n@if / @for\ninject() DI",
                            DEMO, 900, sec_y+30, 200, 90))
    cells.extend(in_col(demo_cells, "col_demo"))

    prod_cells = []
    prod_cells.append(cell("sec_prod_ui", "Frontends (UI)", SECTION, 20, sec_y, 1100, sec_h))
    prod_cells.append(cell("ui_prod_portal", "web-portal\nNext.js 14 standalone\nSSR + TanStack Query\n:3000",
                            PROD, 60, sec_y+30, 220, 90))
    prod_cells.append(cell("ui_prod_totem", "totem\nVite + React + Zustand\nKiosko fullscreen\n:3001",
                            PROD, 320, sec_y+30, 220, 90))
    prod_cells.append(cell("ui_prod_design", "Design system:\nshadcn/ui + Radix\nTailwind + tokens UNAB\nlibs/ui-kit (Storybook)",
                            PROD, 580, sec_y+30, 280, 90))
    prod_cells.append(cell("ui_prod_routing", "Edge routing:\nReverse proxy:\n/, /totem, /api, /api/ws\n(ADR-016)",
                            PROD, 900, sec_y+30, 200, 90))
    cells.extend(in_col(prod_cells, "col_prod"))

    # ===== Capa 2: Gateway =====
    sec_y = 200
    sec_h = 110
    demo_cells = []
    demo_cells.append(cell("sec_demo_gw", "API Gateway", SECTION, 20, sec_y, 1100, sec_h))
    demo_cells.append(cell("gw_demo", "api-gateway (NestJS)\n:3000\nMiddleware JWT (HS256)\nProxy HTTP a servicios\nSecret hardcoded en demo",
                            COMMON, 360, sec_y+30, 380, 70))
    cells.extend(in_col(demo_cells, "col_demo"))

    prod_cells = []
    prod_cells.append(cell("sec_prod_gw", "API Gateway", SECTION, 20, sec_y, 1100, sec_h))
    prod_cells.append(cell("gw_prod", "api-gateway (NestJS)\n:4000 + WebSocket\n@nestjs/passport + JWT\nRate-limit + CORS allowlist\nADR-008",
                            COMMON, 360, sec_y+30, 380, 70))
    cells.extend(in_col(prod_cells, "col_prod"))

    # ===== Capa 3: Microservicios =====
    sec_y = 330
    sec_h = 280
    demo_cells = []
    demo_cells.append(cell("sec_demo_svc", "Microservicios (6) - NestJS", SECTION, 20, sec_y, 1100, sec_h))
    svc_demo = [
        ("auth-svc",          "auth-svc :3001",          60,  sec_y+40),
        ("inv-svc",           "inventory-svc :3002",     320, sec_y+40),
        ("req-svc",           "request-svc :3003",       580, sec_y+40),
        ("loan-svc",          "loan-svc :3004",          840, sec_y+40),
        ("ai-asst",           "ai-assistant-svc :3005\n(keyword matching mock)", 60,  sec_y+130),
        ("ai-asst-detail",    "ALCANCE\n5 servicios + gateway = 6\nNo notification-svc\nNo ai-risk-svc\nNo reports-svc",  580, sec_y+130),
    ]
    for cid, label, x, y in svc_demo:
        s = COMMON
        if cid == "ai-asst-detail":
            s = DIFF
        demo_cells.append(cell(f"svc_demo_{cid}", label, s, x, y, 220, 80))
    cells.extend(in_col(demo_cells, "col_demo"))

    prod_cells = []
    prod_cells.append(cell("sec_prod_svc", "Microservicios (9) - NestJS hexagonal", SECTION, 20, sec_y, 1100, sec_h))
    svc_prod = [
        ("auth-svc",  "auth-svc",        60,  sec_y+40),
        ("inv-svc",   "inventory-svc",   320, sec_y+40),
        ("req-svc",   "request-svc",     580, sec_y+40),
        ("loan-svc",  "loan-svc",        840, sec_y+40),
        ("notif",     "notification-svc\n+ tickets PDF", 60,  sec_y+130),
        ("risk",      "ai-risk-svc\n(scoring ONNX)",     320, sec_y+130),
        ("ai-asst",   "ai-assistant-svc\n(MCP + OpenAI)",580, sec_y+130),
        ("reports",   "reports-svc\n(CQRS read-model)\nADR-015", 840, sec_y+130),
    ]
    for cid, label, x, y in svc_prod:
        s = COMMON
        if cid in ("notif", "risk", "reports"):
            s = PROD
        prod_cells.append(cell(f"svc_prod_{cid}", label, s, x, y, 220, 80))
    cells.extend(in_col(prod_cells, "col_prod"))

    # ===== Capa 4: Persistencia =====
    sec_y = 630
    sec_h = 220
    demo_cells = []
    demo_cells.append(cell("sec_demo_db", "Persistencia", SECTION, 20, sec_y, 1100, sec_h))
    demo_cells.append(cell("db_demo_main",
        "<b>In-memory por servicio</b><br/>"
        "Map&lt;id, User&gt; en auth-svc<br/>"
        "Map&lt;id, Resource&gt; en inventory<br/>"
        "Map&lt;id, Request&gt; en request<br/>"
        "Map&lt;id, Loan&gt; en loan<br/>"
        "<br/>"
        "Sin persistencia entre reinicios<br/>"
        "(seed hardcoded al boot)",
        DEMO, 60, sec_y+40, 380, 160))
    demo_cells.append(cell("db_demo_diff",
        "<b>Diferencia clave</b><br/>"
        "Sin Prisma. Sin migraciones.<br/>"
        "Sin SQL. Sin transacciones.<br/>"
        "Sin lock optimista (RC.12).<br/>"
        "<br/>"
        "Suficiente para demo;<br/>"
        "no apto para produccion.",
        DIFF, 480, sec_y+40, 280, 160))
    demo_cells.append(cell("db_demo_shared",
        "<b>Tipos compartidos</b><br/>"
        "app/shared/src/models/<br/>"
        "User, Resource, Request, Loan<br/>"
        "(interfaces TS)",
        DEMO, 800, sec_y+40, 280, 160))
    cells.extend(in_col(demo_cells, "col_demo"))

    prod_cells = []
    prod_cells.append(cell("sec_prod_db", "Persistencia (database-per-service)", SECTION, 20, sec_y, 1100, sec_h))
    db_grid = [
        ("auth_db",         60,  sec_y+40),
        ("inventory_db",    220, sec_y+40),
        ("request_db",      380, sec_y+40),
        ("loan_db",         540, sec_y+40),
        ("notification_db", 700, sec_y+40),
        ("ai_risk_db",      860, sec_y+40),
        ("ai_assistant_db", 60,  sec_y+110),
        ("reports_db",      220, sec_y+110),
    ]
    for name, x, y in db_grid:
        prod_cells.append(cell(f"db_prod_{name}", name + "\n(Postgres 16)", PROD, x, y, 140, 50))
    prod_cells.append(cell("db_prod_orm",
        "<b>ORM:</b> Prisma 5<br/>"
        "<b>Lock optimista:</b> resources.version (RC.12)<br/>"
        "<b>Migraciones:</b> expand/contract<br/>"
        "<b>Outbox:</b> outbox_events + processed_events<br/>"
        "Ver ERD-01-modelo-datos.drawio",
        PROD, 380, sec_y+110, 700, 80))
    cells.extend(in_col(prod_cells, "col_prod"))

    # ===== Capa 5: Bus / Comunicacion =====
    sec_y = 870
    sec_h = 280
    demo_cells = []
    demo_cells.append(cell("sec_demo_bus", "Comunicacion entre servicios", SECTION, 20, sec_y, 1100, sec_h))
    demo_cells.append(cell("bus_demo_http",
        "<b>HTTP sincrono directo</b><br/>"
        "No hay broker.<br/>"
        "service-a llama a service-b via HTTP.<br/>"
        "Si una llamada falla, falla la cadena.",
        DEMO, 60, sec_y+40, 320, 130))
    demo_cells.append(cell("bus_demo_flow",
        "<b>Ejemplo: crear solicitud</b><br/>"
        "Portal -&gt; gateway -&gt; request-svc<br/>"
        "request-svc -&gt; HTTP -&gt; inventory-svc (reserva)<br/>"
        "inventory-svc -&gt; 200 OK<br/>"
        "request-svc -&gt; 201 Created<br/>"
        "<br/>"
        "<b>EIP simulados (no reales):</b><br/>"
        "Pub-Sub = HTTP fan-out<br/>"
        "Request-Reply = HTTP normal<br/>"
        "Outbox = no implementado<br/>"
        "DLX = no implementado",
        DIFF, 400, sec_y+40, 360, 220))
    demo_cells.append(cell("bus_demo_note",
        "<b>Por que es valido en demo:</b><br/>"
        "Permite mostrar el flujo end-to-end<br/>"
        "sin levantar RabbitMQ.<br/>"
        "<br/>"
        "<b>Por que NO en prod:</b><br/>"
        "Acopla services. Si auth-svc cae,<br/>"
        "todo cae. No hay buffering ni retries.<br/>"
        "Cualquier microservicios real necesita<br/>"
        "un broker.",
        NOTE, 780, sec_y+40, 300, 220))
    cells.extend(in_col(demo_cells, "col_demo"))

    prod_cells = []
    prod_cells.append(cell("sec_prod_bus", "Comunicacion entre servicios", SECTION, 20, sec_y, 1100, sec_h))
    prod_cells.append(cell("bus_prod_rmq",
        "<b>RabbitMQ 3.12 + plugins</b><br/>"
        "(delayed_message, prometheus)<br/>"
        "<br/>"
        "<b>4 exchanges:</b><br/>"
        "domain.events (topic) - Pub-Sub<br/>"
        "domain.commands (direct) - Req-Reply<br/>"
        "domain.delayed (x-delayed) - TTL<br/>"
        "domain.dlx (fanout) - DLC",
        PROD, 60, sec_y+40, 320, 200))
    prod_cells.append(cell("bus_prod_eip",
        "<b>EIPs implementados (Hohpe):</b><br/>"
        "<br/>"
        "&#9679; Publish-Subscribe (EIP-02)<br/>"
        "&#9679; Content-Based Router (EIP-02)<br/>"
        "&#9679; Message Expiration (EIP-03)<br/>"
        "&#9679; Dead Letter Channel<br/>"
        "&#9679; Request-Reply + Correlation Id (EIP-04)<br/>"
        "&#9679; Transactional Outbox (EIP-05)<br/>"
        "&#9679; Idempotent Receiver (EIP-05)<br/>"
        "<br/>"
        "Ver: 04-eip-catalog.md",
        PROD, 400, sec_y+40, 360, 220))
    prod_cells.append(cell("bus_prod_saga",
        "<b>Saga coreografiada</b><br/>"
        "(no orquestada — ADR-006)<br/>"
        "<br/>"
        "request.created -&gt; reserva<br/>"
        "loan.issued -&gt; descuento<br/>"
        "loan.closed -&gt; reposicion<br/>"
        "request.expired -&gt; compensacion<br/>"
        "<br/>"
        "Ver: 05-saga-coreografiada.md",
        PROD, 780, sec_y+40, 300, 220))
    cells.extend(in_col(prod_cells, "col_prod"))

    # ===== Capa 6: Observabilidad / Operacion =====
    sec_y = 1170
    sec_h = 130
    demo_cells = []
    demo_cells.append(cell("sec_demo_obs", "Observabilidad / Operacion", SECTION, 20, sec_y, 1100, sec_h))
    demo_cells.append(cell("obs_demo",
        "<b>concurrently</b> para arrancar 8 procesos<br/>"
        "Console logs por color (-c blue,green,...)<br/>"
        "Sin tracing distribuido<br/>"
        "Sin metrics<br/>"
        "Sin Docker (procesos npm puros)",
        DEMO, 60, sec_y+30, 1020, 90))
    cells.extend(in_col(demo_cells, "col_demo"))

    prod_cells = []
    prod_cells.append(cell("sec_prod_obs", "Observabilidad / Operacion", SECTION, 20, sec_y, 1100, sec_h))
    prod_cells.append(cell("obs_prod",
        "<b>OpenTelemetry SDK</b> + Pino logs estructurados<br/>"
        "<b>Tempo</b> (traces) + <b>Loki</b> (logs) + <b>Grafana</b> dashboards<br/>"
        "<b>Docker compose</b> para dev local (validado: 7/7 smoke tests OK)<br/>"
        "Cloud-agnostico (ADR-009): EKS/AKS/GKE/on-premise<br/>"
        "Ver: 01-stack-tecnologico.md, US-049 (deferred a Sprint 2)",
        PROD, 60, sec_y+30, 1020, 90))
    cells.extend(in_col(prod_cells, "col_prod"))

    # ===== Leyenda y notas finales =====
    legend = (
        "<b>Convenciones:</b><br/>"
        "&#128997; <b>Verde</b> = componente/concepto compartido entre demo y produccion<br/>"
        "&#128993; <b>Amarillo</b> = solo en demo (mock o shortcut)<br/>"
        "&#128992; <b>Naranja</b> = solo en produccion (no implementado en demo)<br/>"
        "&#128308; <b>Rojo</b> = diferencia clave que requiere atencion en mesa redonda<br/>"
        "<br/>"
        "<b>Decision documentada en:</b> app/ARQUITECTURA-DEMO.md<br/>"
        "<b>Trazabilidad ADRs:</b> ADR-002 (Postgres), ADR-005 (RabbitMQ), ADR-006 (saga coreo), ADR-008 (gateway), ADR-016 (UI routing)"
    )
    cells.append(cell("legend", legend, NOTE, 40, 1430, 2320, 60))

    body = "".join(cells)

    out = (
        '<mxfile host="app.diagrams.net" agent="generator" type="device">\n'
        '  <diagram id="arch-01" name="Demo vs Produccion">\n'
        f'    <mxGraphModel dx="2400" dy="1500" grid="1" gridSize="10" guides="1" '
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
