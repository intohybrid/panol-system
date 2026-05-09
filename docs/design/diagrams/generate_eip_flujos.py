#!/usr/bin/env python3
"""
generate_eip_flujos.py - Genera EIP-01-flujos-funcionales.drawio.

Un solo diagrama grande con 5 columnas verticales (una por flujo funcional
critico del Pañol). Cada columna muestra todos los pasos del flujo, con
los iconos EIP de Hohpe inline en los puntos de integracion.
"""
from __future__ import annotations
from pathlib import Path
from xml.sax.saxutils import escape

OUT_DIR = Path(__file__).parent
NL = "\n"

# Estilos por tipo de elemento
STYLE_TITLE   = "text;html=1;align=center;verticalAlign=middle;fontSize=22;fontStyle=1;fontColor=#222;"
STYLE_SUBTITLE= "text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor=#666;"
STYLE_FLOW_HDR= "rounded=1;whiteSpace=wrap;html=1;fillColor=#1f4e79;strokeColor=#1f4e79;fontColor=#fff;fontSize=14;fontStyle=1;align=center;verticalAlign=middle;"
STYLE_ACTOR   = "shape=mxgraph.uml.actor;whiteSpace=wrap;html=1;align=center;verticalAlign=top;fontSize=11;fontStyle=1;"
STYLE_SVC     = "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;fontStyle=1;align=center;verticalAlign=middle;"
STYLE_FRONT   = "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;fontStyle=1;align=center;verticalAlign=middle;"
STYLE_DB      = "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=10;align=center;"
STYLE_NOTE    = "rounded=0;whiteSpace=wrap;html=1;fillColor=#fff8d0;strokeColor=#d6b656;fontSize=10;fontStyle=2;align=left;verticalAlign=top;spacing=4;"
STYLE_EXT     = "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;fontStyle=1;align=center;verticalAlign=middle;"
STYLE_RESULT  = "rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;fontStyle=1;align=center;verticalAlign=middle;"
STYLE_EIP_LBL = "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=10;fontStyle=2;align=center;spacing=2;"
STYLE_EDGE    = "endArrow=classic;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;strokeWidth=2;fontSize=9;"
STYLE_EDGE_DSH= "endArrow=classic;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;strokeWidth=2;fontSize=9;dashed=1;dashPattern=6 4;strokeColor=#b85450;"
STYLE_EDGE_AMQP="endArrow=classic;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;strokeWidth=2;fontSize=9;strokeColor=#d79b00;dashed=1;dashPattern=8 4;"

def eip_shape(name):
    return ("sketch=0;outlineConnect=0;html=1;dashed=0;strokeColor=#000;fillColor=#fff;"
            "shape=mxgraph.eip." + name + ";fontSize=10;align=center;verticalAlign=top;")

def attr(s):
    return escape(s, {'"': "&quot;"}).replace("\n", "&#10;")

def cell(cid, value, style, x, y, w, h):
    return ('<mxCell id="' + cid + '" value="' + attr(value) + '" style="' + style +
            '" vertex="1" parent="1"><mxGeometry x="' + str(x) + '" y="' + str(y) +
            '" width="' + str(w) + '" height="' + str(h) + '" as="geometry"/></mxCell>')

def edge(cid, src, tgt, label="", style=None):
    if style is None: style = STYLE_EDGE
    return ('<mxCell id="' + cid + '" value="' + attr(label) + '" style="' + style +
            '" edge="1" parent="1" source="' + src + '" target="' + tgt +
            '"><mxGeometry relative="1" as="geometry"/></mxCell>')


# ============================================================================
# Definicion de los 5 flujos como secuencia de pasos.
# Cada paso es (tipo, label, [icono EIP opcional], [estilo edge opcional])
#
# tipos: actor, front, svc, db, ext, channel (con icono EIP), result, note
# ============================================================================

def flow_definitions():
    return [
        # ────────────── Flujo 1: Crear solicitud ──────────────
        ("Flujo 1 — Crear solicitud", "F1", [
            ("actor",   "Alumno"),
            ("front",   "web-portal" + NL + "POST /requests + JWT"),
            ("svc",     "api-gateway" + NL + "valida JWT, proxy"),
            ("svc",     "request-svc" + NL + "valida usuario activo +" + NL + "ítems disponibles"),
            ("svc",     "inventory-svc" + NL + "reserva stock (lock optimista)" + NL + "estado=ACTIVA"),
            ("db",      "request_db" + NL + "INSERT requests +" + NL + "INSERT outbox_events" + NL + "(misma TX)"),
            ("note",    "<b>EIP — Transactional Outbox</b>" + NL + "Negocio + evento se escriben juntos." + NL + "Sin chance de mensaje fantasma."),
            ("svc",     "Relay polling" + NL + "@nestjs/schedule"),
            ("channel", "domain.events" + NL + "key=request.created", "messageChannel", "Pub-Sub Channel"),
            ("result",  "notification-svc" + NL + "→ avisa pañolero" + NL + "(WebSocket)"),
            ("result",  "ai-risk-svc" + NL + "→ recalcula perfil" + NL + "de riesgo"),
            ("result",  "reports-svc" + NL + "→ actualiza" + NL + "proyección CQRS"),
            ("channel", "domain.delayed" + NL + "x-delay=900000ms (15 min)", "messExp", "Message Expiration"),
            ("note",    "Si el préstamo NO se materializa en 15 min →" + NL + "ver Flujo 4 (compensación)."),
        ]),

        # ────────────── Flujo 2: Materializar préstamo ──────────────
        ("Flujo 2 — Materializar préstamo", "F2", [
            ("actor",   "Pañolero"),
            ("front",   "tótem" + NL + "PIN virtual"),
            ("svc",     "api-gateway" + NL + "valida PIN/JWT"),
            ("svc",     "loan-svc" + NL + "recibe POST /loans/:id" + NL + "/materialize"),
            ("channel", "domain.commands" + NL + "key=risk.score" + NL + "correlation_id=L-1234" + NL + "reply_to=q.reply.loan",
                       "messageChannel", "Request-Reply + Correlation Id"),
            ("svc",     "ai-risk-svc" + NL + "calcula score" + NL + "(modelo ONNX)"),
            ("channel", "queue.reply.loan" + NL + "(temporal exclusiva)" + NL + "correlation_id=L-1234",
                       "messageChannel", "Reply Channel"),
            ("svc",     "loan-svc" + NL + "matchea correlation_id" + NL + "→ score=0.87 ≥ umbral"),
            ("db",      "loan_db" + NL + "INSERT loan +" + NL + "INSERT outbox_events"),
            ("svc",     "Relay polling"),
            ("channel", "domain.events" + NL + "key=loan.issued", "messageChannel", "Pub-Sub Channel"),
            ("result",  "inventory-svc" + NL + "descuenta stock real" + NL + "(reserva → CONSUMIDA)"),
            ("result",  "notification-svc" + NL + "genera ticket PDF" + NL + "+ avisa alumno"),
            ("result",  "request-svc" + NL + "marca solicitud" + NL + "MATERIALIZADA"),
            ("result",  "reports-svc" + NL + "actualiza proyecciones"),
            ("note",    "<b>Idempotent Receiver:</b> cada consumer chequea x-event-id" + NL + "contra processed_events antes de procesar."),
        ]),

        # ────────────── Flujo 3: Devolución ──────────────
        ("Flujo 3 — Devolución", "F3", [
            ("actor",   "Pañolero"),
            ("front",   "tótem" + NL + "selecciona préstamo"),
            ("front",   "marca ítems:" + NL + "BUENO / DAÑADO / FALTANTE"),
            ("svc",     "api-gateway"),
            ("svc",     "loan-svc" + NL + "POST /loans/:id/return" + NL + "cierra préstamo"),
            ("db",      "loan_db" + NL + "UPDATE loans returned_at +" + NL + "INSERT outbox_events" + NL + "(misma TX)"),
            ("svc",     "Relay polling"),
            ("channel", "domain.events" + NL + "key=loan.returned", "messageChannel", "Pub-Sub Channel"),
            ("result",  "inventory-svc" + NL + "+stock (BUENO)" + NL + "stock.lost (FALTANTE)"),
            ("result",  "notification-svc" + NL + "notifica al alumno"),
            ("result",  "reports-svc" + NL + "actualiza proyección" + NL + "de devoluciones"),
            ("channel", "[si atrasado o FALTANTE]" + NL + "domain.events key=loan.overdue", "messageChannel", "Pub-Sub Channel"),
            ("svc",     "auth-svc consume" + NL + "evalúa RC.01" + NL + "(2 atrasos / 1 faltante)"),
            ("channel", "domain.events" + NL + "key=user.blocked" + NL + "reason=MOROSIDAD", "messageChannel", "Pub-Sub Channel"),
            ("result",  "request-svc cancela" + NL + "solicitudes pendientes" + NL + "del usuario"),
        ]),

        # ────────────── Flujo 4: Reserva expira (compensación) ──────────────
        ("Flujo 4 — Reserva expira (compensación)", "F4", [
            ("note",    "Origen: el mensaje delayed publicado en Flujo 1." + NL + "El préstamo NO se materializó en 15 min."),
            ("channel", "domain.delayed" + NL + "TTL=15 min vencido", "messExp", "Message Expiration"),
            ("channel", "domain.dlx" + NL + "(fanout)", "deadLetterChannel", "Dead Letter Channel"),
            ("svc",     "request-svc" + NL + "compensation handler" + NL + "consume domain.dlx"),
            ("svc",     "verifica request" + NL + "todavía PENDIENTE" + NL + "(idempotente)"),
            ("db",      "request_db" + NL + "UPDATE requests state=VENCIDA"),
            ("channel", "domain.events" + NL + "key=request.expired", "messageChannel", "Pub-Sub Channel"),
            ("result",  "inventory-svc" + NL + "libera reserva" + NL + "stock vuelve a disponible"),
            ("result",  "notification-svc" + NL + "notifica alumno" + NL + "(reserva venció)"),
            ("result",  "reports-svc" + NL + "actualiza contador" + NL + "de expiraciones"),
            ("note",    "<b>Idempotent Receiver:</b> si la solicitud ya fue cancelada/" + NL + "materializada por otra vía, el handler DESCARTA el mensaje" + NL + "sin tocar nada."),
        ]),

        # ────────────── Flujo 5: Asistente conversacional ──────────────
        ("Flujo 5 — Asistente conversacional", "F5", [
            ("actor",   "Alumno"),
            ("front",   "web-portal /chat" + NL + "(streaming)"),
            ("svc",     "api-gateway" + NL + "valida JWT"),
            ("svc",     "ai-assistant-svc" + NL + "guardrail RC.15:" + NL + "rechaza si user.blocked"),
            ("ext",     "OpenAI API" + NL + "GPT-4o-mini" + NL + "function calling"),
            ("channel", "MCP tool call" + NL + "search_catalog / check_availability /" + NL + "create_request_draft", "messageChannel", "Service Activator"),
            ("svc",     "ai-assistant-svc" + NL + "invoca tool MCP local" + NL + "(no HTTP externo)"),
            ("svc",     "inventory-svc" + NL + "(o request-svc)" + NL + "responde data"),
            ("ext",     "OpenAI API" + NL + "construye respuesta" + NL + "con la data"),
            ("svc",     "ai-assistant-svc" + NL + "stream tokens al portal"),
            ("front",   "web-portal /chat" + NL + "muestra respuesta +" + NL + "acción sugerida"),
            ("result",  "[opcional] alumno confirma" + NL + "→ create_request_draft" + NL + "→ borrador en request-svc"),
            ("note",    "<b>Service Activator:</b> el LLM llama tools como si fueran funciones." + NL + "El svc traduce la llamada a comandos AMQP/HTTP internos."),
        ]),
    ]


# ============================================================================
# Renderizado
# ============================================================================
COL_WIDTH = 540
COL_X_GAP = 80
ROW_HEIGHT = 80
ROW_HEIGHT_NOTE = 70
ROW_HEIGHT_CHANNEL = 100
TOP_MARGIN = 110
HEADER_H = 60
ELEMENT_W = 360

def style_for_type(t):
    return {
        "actor":   STYLE_ACTOR,
        "front":   STYLE_FRONT,
        "svc":     STYLE_SVC,
        "db":      STYLE_DB,
        "ext":     STYLE_EXT,
        "result":  STYLE_RESULT,
        "note":    STYLE_NOTE,
    }.get(t, STYLE_SVC)

def render_flow(cells, col_idx, flow_title, flow_id, steps):
    x_left = 60 + col_idx * (COL_WIDTH + COL_X_GAP)
    x_elem = x_left + (COL_WIDTH - ELEMENT_W) // 2

    # Header de columna
    cells.append(cell(flow_id + "_hdr", flow_title, STYLE_FLOW_HDR,
                      x_left, TOP_MARGIN, COL_WIDTH, HEADER_H))

    y = TOP_MARGIN + HEADER_H + 30
    prev_id = None

    for i, step in enumerate(steps):
        sid = flow_id + "_s" + str(i)
        ttype = step[0]
        label = step[1]

        if ttype == "channel":
            # icon + label panel
            shape_name = step[2]
            eip_label = step[3]
            h = ROW_HEIGHT_CHANNEL
            # Pequeño label "EIP — <pattern>" arriba del shape
            cells.append(cell(sid + "_lbl", "EIP · " + eip_label,
                              STYLE_EIP_LBL, x_elem, y, ELEMENT_W, 22))
            # El channel con icono Hohpe
            cells.append(cell(sid, label, eip_shape(shape_name),
                              x_elem, y + 22, ELEMENT_W, h - 22))
        elif ttype == "note":
            h = ROW_HEIGHT_NOTE
            cells.append(cell(sid, label, STYLE_NOTE, x_elem, y, ELEMENT_W, h))
        elif ttype == "actor":
            # actor más chico, centrado
            h = 70
            actor_w = 50
            actor_x = x_elem + (ELEMENT_W - actor_w) // 2
            cells.append(cell(sid, label, STYLE_ACTOR, actor_x, y, actor_w, h))
        else:
            h = ROW_HEIGHT
            cells.append(cell(sid, label, style_for_type(ttype), x_elem, y, ELEMENT_W, h))

        if prev_id is not None:
            edge_style = STYLE_EDGE_AMQP if (ttype == "channel" or steps[i-1][0] == "channel") else STYLE_EDGE
            cells.append(edge("e_" + flow_id + "_" + str(i), prev_id, sid, "", edge_style))
        prev_id = sid
        y += h + 25

    return y


def main():
    cells = []

    # Titulo
    cells.append(cell("title",
                      "EIP — Flujos funcionales del Sistema de Pañol",
                      STYLE_TITLE, 60, 20, 2900, 36))
    cells.append(cell("subtitle",
                      "5 flujos críticos de negocio. Cada paso visible, con íconos EIP de Hohpe inline en los puntos de integración.",
                      STYLE_SUBTITLE, 60, 60, 2900, 22))

    # Render 5 columnas
    flows = flow_definitions()
    max_y = 0
    for i, (title, fid, steps) in enumerate(flows):
        y_end = render_flow(cells, i, title, fid, steps)
        max_y = max(max_y, y_end)

    # Leyenda al pie
    legend_y = max_y + 30
    legend = (
        "<b>Convenciones</b>" + NL +
        "🟦 Frontend · 🟩 Microservicio · 🟨 Base de datos · 🟧 Channel/EIP icon · 🟪 Resultado/consumidor · 🟥 Sistema externo" + NL + NL +
        "<b>Flechas:</b> sólida = HTTP síncrono · punteada naranja = AMQP asincrónico · punteada roja = camino de error / DLX" + NL +
        "<b>EIPs visibles:</b> Pub-Sub Channel · Message Expiration · Dead Letter Channel · Request-Reply + Correlation Identifier · Service Activator · Idempotent Receiver · Transactional Outbox"
    )
    cells.append(cell("legend", legend, STYLE_NOTE, 60, legend_y, 2900, 110))

    # Width total: 5 cols * 540 + 4*80 + margins = 2700+320+120 = 3140
    PAGE_W = 3160
    PAGE_H = legend_y + 160

    out = ('<mxfile host="app.diagrams.net" agent="generator" type="device">' + NL +
           '  <diagram id="eip-flujos" name="EIP — Flujos funcionales">' + NL +
           '    <mxGraphModel dx="' + str(PAGE_W) + '" dy="' + str(PAGE_H) +
           '" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
           'fold="1" page="1" pageScale="1" pageWidth="' + str(PAGE_W) +
           '" pageHeight="' + str(PAGE_H) + '" math="0" shadow="0">' + NL +
           '      <root>' + NL +
           '        <mxCell id="0"/>' + NL +
           '        <mxCell id="1" parent="0"/>' + NL +
           '        ' + "".join(cells) + NL +
           '      </root>' + NL +
           '    </mxGraphModel>' + NL +
           '  </diagram>' + NL +
           '</mxfile>' + NL)

    out_path = OUT_DIR / "EIP-01-flujos-funcionales.drawio"
    out_path.write_text(out, encoding="utf-8")
    print("  OK - " + out_path.name + "  (" + str(PAGE_W) + "x" + str(PAGE_H) + " px, " +
          str(len(cells)) + " cells)")

if __name__ == "__main__":
    main()
