#!/usr/bin/env python3
"""
generate_eip.py - Genera los EIP-* con estructura "patrón canónico arriba +
aplicación abajo" (estilo libro de Hohpe).

Por ahora solo se genera EIP-01 para validar el formato. Las funciones de los
otros patrones quedan comentadas en main() hasta validacion.
"""
from __future__ import annotations
from pathlib import Path
from xml.sax.saxutils import escape

OUT_DIR = Path(__file__).parent

# ====== Estilos ======
TITLE = "text;html=1;align=center;verticalAlign=middle;fontSize=22;fontStyle=1;fontColor=#333;"
SECTION = "text;html=1;align=left;verticalAlign=middle;fontSize=14;fontStyle=1;fontColor=#666;spacingLeft=10;"
DIVIDER = "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#999;dashed=1;dashPattern=8 8;"
ENDPOINT = "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;fontStyle=1;align=center;verticalAlign=middle;"
ENDPOINT_REAL = "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;fontStyle=1;align=center;verticalAlign=middle;"
BUS_FRAME = "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;dashed=1;dashPattern=10 5;align=center;verticalAlign=top;fontSize=14;fontStyle=1;spacingTop=8;"
CAPTION = "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff8d0;strokeColor=#d6b656;fontSize=11;fontStyle=2;align=left;verticalAlign=top;spacing=6;"
EDGE = "endArrow=classic;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;strokeWidth=2;fontSize=10;"
EDGE_DASHED = "endArrow=classic;html=1;rounded=0;edgeStyle=orthogonalEdgeStyle;strokeWidth=2;fontSize=10;dashed=1;dashPattern=6 4;strokeColor=#b85450;"

def eip_shape(name):
    return ("sketch=0;outlineConnect=0;html=1;dashed=0;strokeColor=#000;fillColor=#fff;"
            "shape=mxgraph.eip." + name + ";fontSize=11;align=center;verticalAlign=top;")

def attr(s):
    return escape(s, {'"': "&quot;"}).replace("\n", "&#10;")

def cell(cid, value, style, x, y, w, h):
    return ('<mxCell id="' + cid + '" value="' + attr(value) + '" style="' + style +
            '" vertex="1" parent="1"><mxGeometry x="' + str(x) + '" y="' + str(y) +
            '" width="' + str(w) + '" height="' + str(h) + '" as="geometry"/></mxCell>')

def edge(cid, src, tgt, label="", style=None):
    if style is None:
        style = EDGE
    return ('<mxCell id="' + cid + '" value="' + attr(label) + '" style="' + style +
            '" edge="1" parent="1" source="' + src + '" target="' + tgt +
            '"><mxGeometry relative="1" as="geometry"/></mxCell>')

def header(title, subtitle):
    return (cell("title", title, TITLE, 40, 20, 1500, 40) +
            cell("subtitle", subtitle,
                 "text;html=1;align=center;verticalAlign=middle;fontSize=12;fontColor=#888;",
                 40, 60, 1500, 22))

def section_label(cid, text, x, y, w=600):
    return cell(cid, text, SECTION, x, y, w, 24)

def horizontal_divider(cid, y):
    return cell(cid, "", DIVIDER, 40, y, 1500, 1)

def write_drawio(filename, body, page_w=1580, page_h=980, page_name="EIP"):
    out = ('<mxfile host="app.diagrams.net" agent="generator" type="device">\n'
           '  <diagram id="' + filename + '" name="' + escape(page_name) + '">\n'
           '    <mxGraphModel dx="' + str(page_w) + '" dy="' + str(page_h) +
           '" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
           'fold="1" page="1" pageScale="1" pageWidth="' + str(page_w) +
           '" pageHeight="' + str(page_h) + '" math="0" shadow="0">\n'
           '      <root>\n'
           '        <mxCell id="0"/>\n'
           '        <mxCell id="1" parent="0"/>\n'
           '        ' + body + '\n'
           '      </root>\n'
           '    </mxGraphModel>\n'
           '  </diagram>\n'
           '</mxfile>\n')
    (OUT_DIR / filename).write_text(out, encoding="utf-8")
    print("  OK - " + filename)


# =============================================================================
# EIP-01 — Topología de mensajería (Message Bus)
# =============================================================================
def eip_01_topologia_mensajeria():
    NL = "\n"  # newline literal para usar dentro de strings
    cells = []
    cells.append(header("EIP-01 — Topología de mensajería (Message Bus)",
                        "Backbone de mensajería compartido. Múltiples publishers/consumers, varios tipos de channel."))

    # ===== Pattern canonical =====
    cells.append(section_label("sec_pat", "Pattern (canónico, Hohpe)", 40, 100))

    # Publishers
    cells.append(cell("pubA", "Publisher A", ENDPOINT,  60, 180, 130, 60))
    cells.append(cell("pubB", "Publisher B", ENDPOINT,  60, 270, 130, 60))
    cells.append(cell("pubC", "Publisher C", ENDPOINT,  60, 360, 130, 60))

    # Bus container
    cells.append(cell("bus_pat", "<b>Message Bus</b>", BUS_FRAME, 260, 145, 540, 320))

    # 4 channel icons
    cells.append(cell("ch_psc", "Pub-Sub Channel" + NL + "(broadcast)",
                      eip_shape("messageChannel"), 290, 200, 220, 60))
    cells.append(cell("ch_p2p", "Point-to-Point" + NL + "(1 receiver)",
                      eip_shape("messageChannel"), 540, 200, 220, 60))
    cells.append(cell("ch_exp", "TTL Channel" + NL + "(expiration)",
                      eip_shape("messExp"), 290, 380, 220, 60))
    cells.append(cell("ch_dlc", "Dead Letter Channel" + NL + "(captura fallos)",
                      eip_shape("deadLetterChannel"), 540, 380, 220, 60))

    # Consumers
    cells.append(cell("conA", "Consumer 1", ENDPOINT, 870, 180, 130, 60))
    cells.append(cell("conB", "Consumer 2", ENDPOINT, 870, 270, 130, 60))
    cells.append(cell("conC", "Consumer 3", ENDPOINT, 870, 360, 130, 60))

    # Edges
    cells.append(edge("ep1", "pubA", "ch_psc"))
    cells.append(edge("ep2", "pubB", "ch_p2p"))
    cells.append(edge("ep3", "pubC", "ch_exp"))
    cells.append(edge("ec1", "ch_psc", "conA"))
    cells.append(edge("ec2", "ch_psc", "conB"))
    cells.append(edge("ec3", "ch_p2p", "conC"))
    cells.append(edge("ed1", "ch_exp", "ch_dlc", "[expired]", EDGE_DASHED))

    cells.append(cell("cap1",
        "Múltiples publishers/consumers comparten un Message Bus que ofrece varios tipos de Channel: "
        "broadcast (Pub-Sub), 1-a-1 (Point-to-Point), TTL (Expiration) y captura de muertos (Dead Letter). "
        "Cada Channel tiene su semántica de entrega.",
        CAPTION, 1040, 200, 500, 220))

    # ===== Divider =====
    cells.append(horizontal_divider("div", 510))
    cells.append(cell("div_lbl", "Aplicación al Sistema de Pañol — Bus RabbitMQ",
                      SECTION, 40, 530, 800, 24))

    # ===== Application =====
    # Servicios publicadores
    cells.append(cell("s_auth",  "auth-svc",       ENDPOINT_REAL,  60, 600, 130, 50))
    cells.append(cell("s_inv",   "inventory-svc",  ENDPOINT_REAL,  60, 660, 130, 50))
    cells.append(cell("s_req",   "request-svc",    ENDPOINT_REAL,  60, 720, 130, 50))
    cells.append(cell("s_loan",  "loan-svc",       ENDPOINT_REAL,  60, 780, 130, 50))
    cells.append(cell("s_risk",  "ai-risk-svc",    ENDPOINT_REAL,  60, 840, 130, 50))

    # Bus container
    cells.append(cell("bus_app", "<b>RabbitMQ — domain.* exchanges</b>", BUS_FRAME,
                      260, 580, 540, 360))

    # 4 named exchanges
    cells.append(cell("ex_events",   "domain.events" + NL + "(topic) — Pub-Sub",
                      eip_shape("messageChannel"), 290, 630, 220, 60))
    cells.append(cell("ex_commands", "domain.commands" + NL + "(direct) — P2P",
                      eip_shape("messageChannel"), 540, 630, 220, 60))
    cells.append(cell("ex_delayed",  "domain.delayed" + NL + "(x-delayed) — TTL",
                      eip_shape("messExp"), 290, 820, 220, 60))
    cells.append(cell("ex_dlx",      "domain.dlx" + NL + "(fanout) — DLC",
                      eip_shape("deadLetterChannel"), 540, 820, 220, 60))

    # Consumers
    cells.append(cell("c_notif",   "notification-svc",  ENDPOINT_REAL, 870, 600, 150, 50))
    cells.append(cell("c_riskc",   "ai-risk-svc",       ENDPOINT_REAL, 870, 660, 150, 50))
    cells.append(cell("c_reports", "reports-svc",       ENDPOINT_REAL, 870, 720, 150, 50))
    cells.append(cell("c_reqcomp", "request-svc" + NL + "(compensación)",
                      ENDPOINT_REAL, 870, 820, 150, 60))

    # Edges representativas
    cells.append(edge("ep4", "s_auth",  "ex_events",   "user.*"))
    cells.append(edge("ep5", "s_inv",   "ex_events",   "stock.*"))
    cells.append(edge("ep6", "s_req",   "ex_events",   "request.*"))
    cells.append(edge("ep7", "s_loan",  "ex_commands", "risk.score"))
    cells.append(edge("ep8", "s_req",   "ex_delayed",  "TTL=15min"))
    cells.append(edge("ec4", "ex_events",   "c_notif"))
    cells.append(edge("ec5", "ex_events",   "c_riskc"))
    cells.append(edge("ec6", "ex_events",   "c_reports"))
    cells.append(edge("ec7", "ex_commands", "c_riskc"))
    cells.append(edge("ed2", "ex_delayed",  "ex_dlx",  "[expired]", EDGE_DASHED))
    cells.append(edge("ed3", "ex_dlx",      "c_reqcomp", "request.expired"))

    cells.append(cell("cap2",
        "El bus de Pañol son 4 exchanges RabbitMQ. domain.events (topic) implementa Pub-Sub con routing keys; "
        "domain.commands (direct) implementa Point-to-Point con cola por servicio; "
        "domain.delayed implementa Message Expiration con plugin x-delayed-message; "
        "domain.dlx (fanout) captura mensajes muertos.",
        CAPTION, 1040, 600, 500, 280))

    write_drawio("EIP-01-topologia-mensajeria.drawio", "".join(cells),
                 page_w=1580, page_h=980, page_name="EIP-01 Topología de mensajería")


def main():
    print("Generando EIP-01 (Topologia de mensajeria) para validacion...")
    eip_01_topologia_mensajeria()
    # eip_02_pubsub()
    # eip_03_expiration_dlc()
    # eip_04_request_reply()
    # eip_05_outbox_idempotent()
    print("OK")

if __name__ == "__main__":
    main()
