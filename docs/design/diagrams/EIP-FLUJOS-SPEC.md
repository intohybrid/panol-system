# Especificación EIP — Flujos funcionales del Sistema de Pañol

**Propósito:** este documento describe cómo armar 5 diagramas EIP (uno por flujo crítico del sistema) usando los íconos oficiales de Hohpe disponibles en la paleta de drawio.

**Cómo usar:** abrí drawio, habilitá las librerías `EIP / *` (Construction, Routing, Transformation, Channels, Endpoints, Systems, System Management). Cada flujo abajo lista los nodos y las flechas. Arrastrás el ícono indicado a la posición sugerida y conectás según la tabla de edges.

**Paletas EIP usadas (todas en `More Shapes → Networking → EIP`):**

- Aggregator, Canonical Data Model, Composed Message Processor, Content-Based Router, Content Enricher, Message Translator, Messaging Bridge, Normalizer, Pipes and Filters, Point-to-Point Channel, Process Manager, Recipient List, Splitter, Routing Slip.
- Como fondo (cuando el ícono específico no existe): Message Channel (genérico), Message Broker.

**Convención común a los 5 diagramas:**

- Actores (Alumno, Pañolero, Coord) → ícono de actor UML chico arriba a la izquierda.
- Microservicios → rectángulo redondeado verde claro `#d5e8d4` (label = nombre del servicio).
- Bases de datos → cilindro amarillo `#fff2cc`.
- Sistemas externos (OpenAI) → rectángulo rojo claro `#f8cecc`.
- **Íconos EIP** → tal cual se arrastran de la paleta, sin colores extra. Son los protagonistas visuales.
- Flechas: sólida negra = HTTP síncrono. Sólida naranja punteada = AMQP. Roja punteada = camino de error.

---

## Flujo 1 — Crear solicitud (alumno arma carrito y confirma)

**Negocio:** el alumno selecciona ítems, valida disponibilidad, confirma. El sistema reserva stock con TTL, persiste atómicamente y publica el evento para que múltiples consumidores reaccionen.

**EIPs aplicados:** Splitter · Pipes and Filters · Recipient List · Canonical Data Model.

### Layout sugerido

```
[Alumno]
   │
   ▼
[web-portal]
   │
   ▼
[api-gateway]
   │
   ▼
[request-svc]
   │
   ├──────────────────────────────┐
   │                              ▼
   ▼                       ⟦ Splitter ⟧
[validar usuario activo]   (request.items[N])
                                 │
                                 ▼
                          [inventory-svc]
                          (reserva 1 unidad por ítem)
                                 │
                                 ▼
                          ⟦ request_db ⟧
                          INSERT requests + outbox_events
                                 │
                                 ▼
                          ⟦ Pipes and Filters ⟧
                          outbox → relay → broker → handler
                                 │
                                 ▼
                          ⟦ Recipient List ⟧
                          domain.events / request.created
                                 │
                  ┌──────────────┼──────────────┐
                  ▼              ▼              ▼
           [notification-svc] [ai-risk-svc] [reports-svc]
              avisa pañolero  recalcula      proyección
                              perfil riesgo
```

### Nodos a colocar

| # | Tipo | Ícono drawio | Label |
|---|---|---|---|
| 1 | Actor | UML Actor | `Alumno` |
| 2 | Frontend | Rectángulo redondeado azul | `web-portal` |
| 3 | Servicio | Rectángulo verde | `api-gateway` |
| 4 | Servicio | Rectángulo verde | `request-svc` |
| 5 | **EIP** | **Splitter** (paleta EIP/Routing) | `Splitter — request.items[N] → N reservas` |
| 6 | Servicio | Rectángulo verde | `inventory-svc` |
| 7 | DB | Cilindro amarillo | `request_db` |
| 8 | **EIP** | **Pipes and Filters** (paleta EIP/Routing) | `Outbox → Relay → Broker` |
| 9 | **EIP** | **Recipient List** (paleta EIP/Routing) | `domain.events  routing_key=request.created` |
| 10 | Servicio | Rectángulo verde | `notification-svc` |
| 11 | Servicio | Rectángulo verde | `ai-risk-svc` |
| 12 | Servicio | Rectángulo verde | `reports-svc` |
| 13 | Nota | Sticky note | `Canonical Data Model: el evento sigue el schema definido en libs/events (versión x-schema-version=1.0)` |

### Edges

| Desde | Hacia | Label | Tipo |
|---|---|---|---|
| 1 | 2 | `inicia sesión + arma carrito` | sólida |
| 2 | 3 | `POST /requests + JWT` | sólida |
| 3 | 4 | `proxy` | sólida |
| 4 | 5 | `valida y divide ítems` | sólida |
| 5 | 6 | `reserveStock(itemId)` (1 por ítem) | sólida |
| 4 | 7 | `INSERT misma TX` | sólida |
| 7 | 8 | — | sólida |
| 8 | 9 | `publish` | naranja punteada (AMQP) |
| 9 | 10 | `consume` | naranja punteada |
| 9 | 11 | `consume` | naranja punteada |
| 9 | 12 | `consume` | naranja punteada |

---

## Flujo 2 — Materializar préstamo (pañolero entrega los recursos)

**Negocio:** pañolero confirma en el tótem que la solicitud se entrega físicamente. Antes de materializar, consulta scoring de riesgo del alumno. Si el score es OK, crea el préstamo y publica el evento que descuenta stock y dispara notificaciones.

**EIPs aplicados:** Point-to-Point Channel · Process Manager · Recipient List · Message Translator.

### Layout sugerido

```
[Pañolero]
   │
   ▼
[tótem]
   │
   ▼
[api-gateway]
   │
   ▼
[loan-svc] ────────────────────────────┐
   │                                    ▼
   │                          ⟦ Process Manager ⟧
   │                          gestiona estado:
   │                          PENDIENTE → APROBANDO → MATERIALIZADA
   │                                    │
   │                                    ▼
   │                          ⟦ Point-to-Point Channel ⟧
   │                          domain.commands  routing_key=risk.score
   │                          correlation_id=L-1234
   │                                    │
   │                                    ▼
   │                          [ai-risk-svc]
   │                          (score=0.87)
   │                                    │
   │                                    ▼
   │                          ⟦ Point-to-Point Channel ⟧
   │                          queue.reply.loan (temporal)
   │                                    │
   ▼ ◄─────────────────────────────────┘
[crea préstamo + outbox]
   │
   ▼
⟦ Message Translator ⟧
domain event interno → ticket DTO para PDF
   │
   ▼
⟦ Recipient List ⟧
domain.events  routing_key=loan.issued
   │
   ┌──────────────┬──────────────┬──────────────┐
   ▼              ▼              ▼              ▼
[inventory-svc] [notification] [request-svc]  [reports-svc]
descuenta      genera ticket   marca solicit.  proyección
stock real     PDF             MATERIALIZADA
```

### Nodos a colocar

| # | Tipo | Ícono drawio | Label |
|---|---|---|---|
| 1 | Actor | UML Actor | `Pañolero` |
| 2 | Frontend | Rectángulo azul | `tótem` |
| 3 | Servicio | Rectángulo verde | `api-gateway` |
| 4 | Servicio | Rectángulo verde | `loan-svc` |
| 5 | **EIP** | **Process Manager** (paleta EIP/Routing) | `Process Manager — saga préstamo` |
| 6 | **EIP** | **Point-to-Point Channel** (paleta EIP/Channels) | `domain.commands / risk.score  correlation_id=L-1234` |
| 7 | Servicio | Rectángulo verde | `ai-risk-svc` |
| 8 | **EIP** | **Point-to-Point Channel** | `queue.reply.loan (temporal)  correlation_id=L-1234` |
| 9 | DB | Cilindro amarillo | `loan_db (loans + outbox)` |
| 10 | **EIP** | **Message Translator** (paleta EIP/Transformation) | `Domain event → Ticket DTO` |
| 11 | **EIP** | **Recipient List** | `domain.events  routing_key=loan.issued` |
| 12 | Servicio | Rectángulo verde | `inventory-svc` |
| 13 | Servicio | Rectángulo verde | `notification-svc` |
| 14 | Servicio | Rectángulo verde | `request-svc` |
| 15 | Servicio | Rectángulo verde | `reports-svc` |

### Edges

| Desde | Hacia | Label | Tipo |
|---|---|---|---|
| 1→2→3→4 | (cadena) | `materialize(:requestId)` | sólida |
| 4 | 5 | `inicia saga` | sólida |
| 5 | 6 | `pide score` | naranja punteada |
| 6 | 7 | `consume comando` | naranja punteada |
| 7 | 8 | `responde con score` | naranja punteada |
| 8 | 5 | `correlation match` | naranja punteada |
| 5 | 9 | `INSERT loan + outbox` | sólida |
| 9 | 10 | `relay → translator` | naranja punteada |
| 10 | 11 | `publish loan.issued` | naranja punteada |
| 11 | 12,13,14,15 | `consume` cada uno | naranja punteada |

---

## Flujo 3 — Devolución y bloqueo por morosidad

**Negocio:** pañolero registra la devolución marcando estado de cada ítem (BUENO/DAÑADO/FALTANTE). Si hubo atraso o pérdida, eventualmente el sistema bloquea al alumno por RC.01 (reglas: 2 atrasos o 1 faltante en el semestre).

**EIPs aplicados:** Content-Based Router · Aggregator · Recipient List.

### Layout sugerido

```
[Pañolero]
   │
   ▼
[tótem]
   │
   ▼
[api-gateway]
   │
   ▼
[loan-svc]
cierra préstamo + outbox
   │
   ▼
⟦ Content-Based Router ⟧
clasifica items: BUENO | DAÑADO | FALTANTE
   │           │           │
   ▼           ▼           ▼
+stock      +stock        stock.lost
domain.events: loan.returned (+ opcional: stock.lost)
   │
   ▼
⟦ Recipient List ⟧
   │
   ├──────────────┬──────────────┐
   ▼              ▼              ▼
[inventory-svc] [notification]  [reports-svc]
                 al alumno

  ───── (si hay atraso o pérdida) ─────
   │
   ▼
domain.events: loan.overdue
   │
   ▼
⟦ Aggregator ⟧
auth-svc agrega N eventos loan.overdue por usuario
evalúa RC.01: ¿2 atrasos? ¿1 faltante?
   │
   ▼ (si aplica)
domain.events: user.blocked  reason=MOROSIDAD
   │
   ▼
⟦ Recipient List ⟧
   │
   ├──────────────┬──────────────┐
   ▼              ▼              ▼
[request-svc]  [notification]   [reports-svc]
cancela        notifica al      proyección
pendientes     usuario          de bloqueos
```

### Nodos a colocar

| # | Tipo | Ícono drawio | Label |
|---|---|---|---|
| 1 | Actor | UML Actor | `Pañolero` |
| 2 | Frontend | Rectángulo azul | `tótem` |
| 3 | Servicio | Rectángulo verde | `api-gateway` |
| 4 | Servicio | Rectángulo verde | `loan-svc` |
| 5 | **EIP** | **Content-Based Router** (paleta EIP/Routing) | `Routing por estadoDevolucion: BUENO / DAÑADO / FALTANTE` |
| 6 | **EIP** | **Recipient List** | `domain.events  loan.returned` |
| 7 | Servicio | Rectángulo verde | `inventory-svc` |
| 8 | Servicio | Rectángulo verde | `notification-svc` |
| 9 | Servicio | Rectángulo verde | `reports-svc` |
| 10 | **EIP** | **Aggregator** (paleta EIP/Routing) | `Aggregator — auth-svc evalúa RC.01: 2 atrasos OR 1 faltante en el semestre` |
| 11 | **EIP** | **Recipient List** | `domain.events  user.blocked` |
| 12 | Servicio | Rectángulo verde | `request-svc` |
| 13 | Servicio | Rectángulo verde | `notification-svc` (la 2da vez puede ser referencia) |
| 14 | Servicio | Rectángulo verde | `reports-svc` (idem) |

### Edges

| Desde | Hacia | Label | Tipo |
|---|---|---|---|
| 1→2→3→4 | (cadena) | `return(:loanId, items[])` | sólida |
| 4 | 5 | `evalúa cada ítem` | sólida |
| 5 | 6 | `publish loan.returned` | naranja punteada |
| 6 | 7,8,9 | `consume` cada uno | naranja punteada |
| 4 | 10 | `loan.overdue` (cuando aplica) | naranja punteada |
| 10 | 11 | `publish user.blocked` cuando RC.01 se cumple | naranja punteada |
| 11 | 12,13,14 | `consume` | naranja punteada |

---

## Flujo 4 — Compensación de reserva (la solicitud venció)

**Negocio:** la reserva de stock vive con un TTL de 15 min. Si el préstamo no se materializa en ese tiempo, se libera el stock y se notifica al alumno. Es un saga compensatorio coreografiado por el broker (TTL en domain.delayed → DLX → handler).

**EIPs aplicados:** Process Manager · Routing Slip · Recipient List.

> Nota: la lista que pasaste no incluye Message Expiration ni Dead Letter Channel directamente. El comportamiento de TTL queda **encapsulado en el Process Manager**, que es el responsable de la coordinación temporal del saga. La existencia técnica de `domain.delayed` y `domain.dlx` se documenta en la nota lateral, pero el ícono EIP que representa el patrón es el Process Manager (porque administra la línea de tiempo del proceso).

### Layout sugerido

```
[origen: Flujo 1, paso 9 publica TTL]
                    │
                    ▼
        ⟦ Process Manager ⟧
        saga: cuenta 15 min;
        si no llega loan.issued con requestId,
        dispara compensación.
                    │
                    ▼
        ⟦ Routing Slip ⟧
        itinerario de compensación:
        1) marcar request VENCIDA
        2) liberar reserva
        3) notificar al alumno
                    │
        ┌───────────┼───────────────┐
        ▼           ▼               ▼
  [request-svc]  [inventory-svc] [notification-svc]
  state=VENCIDA  reserva → LIBERADA  notif "tu reserva venció"
                    │
                    ▼
        ⟦ Recipient List ⟧
        domain.events  request.expired
                    │
                    ▼
        [reports-svc]
        contador de expiraciones
```

### Nodos a colocar

| # | Tipo | Ícono drawio | Label |
|---|---|---|---|
| 1 | Nota inicial | Sticky note | `Origen: domain.delayed (TTL=15min) emitido en Flujo 1` |
| 2 | **EIP** | **Process Manager** (paleta EIP/Routing) | `Process Manager — saga TTL  espera loan.issued ≤ 15min` |
| 3 | **EIP** | **Routing Slip** (paleta EIP/Routing) | `Itinerario compensación:  1) VENCIDA  2) liberar  3) notificar` |
| 4 | Servicio | Rectángulo verde | `request-svc` |
| 5 | Servicio | Rectángulo verde | `inventory-svc` |
| 6 | Servicio | Rectángulo verde | `notification-svc` |
| 7 | **EIP** | **Recipient List** | `domain.events  request.expired` |
| 8 | Servicio | Rectángulo verde | `reports-svc` |
| 9 | Nota lateral | Sticky note | `Implementación técnica del TTL: exchange domain.delayed (plugin x-delayed-message) + domain.dlx para captura de timeout. El Process Manager observa la entrega tardía del DLX como señal del timeout.` |

### Edges

| Desde | Hacia | Label | Tipo |
|---|---|---|---|
| 1 | 2 | `entrada del PM` | naranja punteada |
| 2 | 3 | `timeout disparado` | roja punteada |
| 3 | 4 | `1. UPDATE state=VENCIDA` | sólida |
| 3 | 5 | `2. liberar reserva` | sólida |
| 3 | 6 | `3. notificar` | sólida |
| 4 | 7 | `publish request.expired` | naranja punteada |
| 7 | 8 | `consume` | naranja punteada |

---

## Flujo 5 — Asistente conversacional con MCP

**Negocio:** el alumno chatea con el asistente. Antes de responder, el asistente verifica que el usuario no esté bloqueado (RC.15), invoca tools MCP para enriquecer la respuesta con catálogo y disponibilidad, y opcionalmente crea un borrador de solicitud.

**EIPs aplicados:** Process Manager · Content Enricher · Message Translator · Normalizer.

### Layout sugerido

```
[Alumno]
   │
   ▼
[web-portal /chat]
   │
   ▼
[api-gateway]
   │
   ▼
[ai-assistant-svc]
guardrail RC.15 (rechaza si user.blocked)
   │
   ▼
⟦ Process Manager ⟧
multi-turn: alumno ↔ LLM ↔ tool ↔ LLM
mantiene contexto + correlation
   │
   ▼
[OpenAI API]
gpt-4o-mini (function calling)
   │
   ▼ (tool_call)
⟦ Message Translator ⟧
function call JSON  →  comando interno (HTTP/AMQP)
   │
   ▼
⟦ Content Enricher ⟧
agrega data desde inventory-svc + ai-risk-svc:
- stock disponible por recurso
- perfil de riesgo del alumno
   │
   ▼
[inventory-svc]  (búsqueda catálogo)
[ai-risk-svc]    (perfil riesgo)
   │
   ▼
⟦ Normalizer ⟧
normaliza respuestas heterogéneas (Mongo + Postgres + scoring)
a un schema único para el LLM
   │
   ▼
[OpenAI API]
respuesta natural + acción sugerida
   │
   ▼
[ai-assistant-svc]
stream tokens
   │
   ▼
[web-portal /chat]
muestra respuesta + botón "crear borrador"
   │
   ▼
[opcional] alumno confirma → request-svc.draft
```

### Nodos a colocar

| # | Tipo | Ícono drawio | Label |
|---|---|---|---|
| 1 | Actor | UML Actor | `Alumno` |
| 2 | Frontend | Rectángulo azul | `web-portal /chat` |
| 3 | Servicio | Rectángulo verde | `api-gateway` |
| 4 | Servicio | Rectángulo verde | `ai-assistant-svc  guardrail RC.15` |
| 5 | **EIP** | **Process Manager** | `Process Manager — multi-turn LLM` |
| 6 | Externo | Rectángulo rojo | `OpenAI API  gpt-4o-mini  function calling` |
| 7 | **EIP** | **Message Translator** | `JSON function call → HTTP/AMQP command` |
| 8 | **EIP** | **Content Enricher** | `enriquece query con catálogo + perfil riesgo` |
| 9 | Servicio | Rectángulo verde | `inventory-svc` |
| 10 | Servicio | Rectángulo verde | `ai-risk-svc` |
| 11 | **EIP** | **Normalizer** (paleta EIP/Transformation) | `Normalizer — schemas heterogéneos → schema único LLM` |
| 12 | Servicio | Rectángulo verde | `request-svc.draft` (opcional) |

### Edges

| Desde | Hacia | Label | Tipo |
|---|---|---|---|
| 1→2→3→4 | (cadena) | `mensaje del alumno + JWT` | sólida |
| 4 | 5 | `inicia conversación` | sólida |
| 5 | 6 | `prompt + tools disponibles` | sólida |
| 6 | 7 | `tool_call(function, args)` | sólida |
| 7 | 8 | `comando interno` | sólida |
| 8 | 9 | `searchCatalog` | sólida |
| 8 | 10 | `getRiskProfile` | sólida |
| 9,10 | 11 | `responses` | sólida |
| 11 | 6 | `tool_result normalizado` | sólida |
| 6 | 4 | `respuesta natural` | sólida |
| 4 | 2 | `stream tokens` | sólida |
| 2 | 12 | `[opcional] confirmar` | sólida |

---

## Resumen — patrones EIP usados a través de los 5 flujos

| Pattern | Aparece en flujo | Rol |
|---|---|---|
| Aggregator | 3 | auth-svc evalúa RC.01 con N eventos loan.overdue |
| Canonical Data Model | 1 (nota) | libs/events define schemas compartidos versionados |
| Content Enricher | 5 | asistente enriquece query con catálogo + perfil |
| Content-Based Router | 3 | clasifica items devueltos por estado |
| Message Translator | 2, 5 | DTO ticket; function call JSON → comando interno |
| Normalizer | 5 | unifica schemas heterogéneos antes del LLM |
| Pipes and Filters | 1 | outbox → relay → broker → consumer |
| Point-to-Point Channel | 2 | request-reply con correlation entre loan-svc y ai-risk-svc |
| Process Manager | 2, 4, 5 | sagas y conversación multi-turn |
| Recipient List | 1, 2, 3, 4 | fan-out de eventos de dominio |
| Routing Slip | 4 | itinerario de compensación |
| Splitter | 1 | request con N items → N reservaciones |

**12 patterns canónicos de Hohpe aplicados a 5 flujos del sistema.** Cada flujo es independiente y demuestra al menos 2 patterns en composición.

---

## Próximos pasos

1. Abrí drawio, habilitá las librerías EIP.
2. Para cada flujo, creá una página nueva con el nombre `EIP-<n>-<flujo>`.
3. Arrastrá los íconos según la tabla "Nodos a colocar" del flujo.
4. Conectá según la tabla "Edges".
5. Cuando termines un flujo, podés exportar a PNG/SVG para incrustar en la PPT.

Si algún paso no calza con la realidad del demo, anotalo y lo ajustamos en este MD para mantener consistencia.
