# PPT — Contenido visible en slides

**Sistema de Pañol — UNAB Viña del Mar.** Solo el texto que aparece en pantalla. Para lo que se dice oralmente al presentar cada slide, ver `PPT-script.md`.

**Convenciones:**

- Bullets cortos, una idea por línea, sin párrafos.
- Cada slide tiene su `Visual:` con la referencia al asset (SVG/PNG/screenshot).
- Cada slide indica el criterio de la rúbrica (`C1`–`C10`) que cubre.

---

## Slide 1 — Portada

**Sistema de Pañol UNAB**
*Plataforma distribuida con IA · LeSS · MIT Design FullStack + AI*

- Caso 11 — Magíster en Ingeniería en Informática
- Equipo: [Nombres]
- Fecha: [Fecha de entrega]

**Visual:** `images/icon-panol.svg` centrado · ~200×200px.
**Rúbrica:** —

---

## Slide 2 — Agenda

**Lo que vas a ver — 4 bloques en 14 min**

- 1 · Negocio y problema (3 min)
- 2 · Metodología y plataforma (3 min)
- 3 · Arquitectura, IA y EIP (5 min)
- 4 · Prototipo y cierre (3 min)

**Visual:** Línea de tiempo horizontal con los 4 bloques + duración.
**Rúbrica:** —

---

## Slide 3 — Contexto organizacional

**Pañol UNAB Viña del Mar — Escuela de Informática**

- 4 actores: Alumno · Pañolero · Coordinador · Jefe de Carrera
- ~500 alumnos · ~500 recursos
- Préstamos diarios, alta rotación
- Sin sistema digital actual

**Visual:** `images/icon-panol.svg` (decorativo) + tabla 4 roles × permisos clave.
**Rúbrica:** C1

---

## Slide 4 — El problema actual

**Lo que duele hoy**

- Registro manual en cuaderno
- Cero trazabilidad histórica
- Pérdidas no detectables
- Sin reportes de gestión
- Bloqueo por morosidad imposible de auditar

**Visual:** `images/before-after.svg` fullbleed.
**Rúbrica:** C1

---

## Slide 5 — La propuesta

**3 interfaces, 1 backend, IA integrada**

- Portal web para alumnos y docentes
- Tótem touch para pañoleros
- Asistente conversacional (MCP + GPT-4o-mini)
- Trazabilidad end-to-end con Grafana
- Bloqueo automático por morosidad

**Visual:** `images/mockup-three-uis.svg` fullbleed.
**Rúbrica:** C1, C2

---

## Slide 6 — Requerimientos principales

**14 RF · 18 RC · 10 RNF**

- 11 épicas, 50 user stories
- 3 sprints (64 + 107 + 94 puntos)
- Reglas de negocio críticas: RC.01 (morosidad), RC.06 (TTL reservas), RC.16 (estados solicitud)
- Trazabilidad RF → CU → US → Sprint

**Visual:** Mapa mental épicas + tabla de tipos de requerimiento.
**Rúbrica:** C2

---

## Slide 7 — Supuestos, contradicciones y restricciones

**Decisiones explícitas**

- Stack MERN del enunciado → Postgres + NestJS (ADR-002, ADR-003)
- IA opcional, no bloquea operación (ADR-007)
- Cloud-agnóstico: Docker compose + EKS/AKS/GKE (ADR-009)
- Tótem físico ≠ móvil (RC.14)

**Visual:** Tabla 2×2 (supuestos / contradicciones / restricciones / dudas).
**Rúbrica:** C2

---

## Slide 8 — Metodología principal: LeSS

**Por qué LeSS**

- Escala Scrum a 2 equipos sin proceso pesado
- 1 backlog · 1 PO · ceremonias compartidas
- Sprints cortos (2 semanas)
- Cero overhead burocrático

**Visual:** Diagrama LeSS — 2 equipos, 1 backlog, 1 PO.
**Rúbrica:** C3

---

## Slide 9 — LeSS vs RUP — descartamos RUP

**Por qué no RUP**

- Pesado y orientado a documentación
- Iteraciones largas (4–6 sem)
- Roles fragmentados (analista, arquitecto, dev separados)
- No calza con 2 equipos pequeños

**Visual:** Tabla comparativa + ✕ sobre RUP.
**Rúbrica:** C3

---

## Slide 10 — LeSS vs SAFe — descartamos SAFe

**Por qué no SAFe**

- Diseñado para 50–125 personas
- 4 niveles (Team/Program/Solution/Portfolio)
- Sobre-engineering para 2 equipos
- Burocracia mata velocidad MVP

**Visual:** Tabla + niveles SAFe tachados.
**Rúbrica:** C3

---

## Slide 11 — LeSS aplicado al caso

**Cómo lo ejecutamos**

- 2 equipos × 4–5 personas
- Equipo A: transaccional (auth, inventory, request, loan)
- Equipo B: experiencia (frontends, IA, reports, notif)
- Planning Two-Team + Review única
- 3 sprints de 2 semanas

**Visual:** Cadencia 6 semanas con sprints + hitos.
**Rúbrica:** C3

---

## Slide 12 — Plataforma de gestión: Jira

**Estándar de la industria**

- 1 proyecto: PNL — Sistema de Pañol UNAB
- 50 user stories, 11 épicas, 3 sprints
- 53 etiquetas (`team:*`, `RF:*`, `tipo:*`)
- Story points Fibonacci
- Importación vía API REST (`import_to_jira.py`)

**Visual:** [TODO `images/jira-backlog.png`] — vista Backlog + tablero Sprint 1.
**Rúbrica:** C3

---

## Slide 13 — Trazabilidad RF → US en Jira

**De requerimiento a código en 1 click**

- Cada US tiene tag `RF:RF.N`
- Filtro JQL: `labels = "RF:RF.4"`
- Cada épica agrupa US por dominio
- Sprint = etiqueta + asignación a sprint nativo

**Visual:** Tabla extracto + [TODO `images/jira-jql-filter.png`].
**Rúbrica:** C2, C3

---

## Slide 14 — MIT Design FullStack — concepto

**Una sola filosofía atravesando todas las capas**

- TypeScript end-to-end
- OpenAPI versionado
- Eventos AMQP con `x-schema-version`
- OpenTelemetry desde día 1

**Visual:** Capas vertical (UI→API→Domain→Data→Infra→Ops) con flechas bidireccionales.
**Rúbrica:** C7

---

## Slide 15 — MIT Design FullStack — aplicación

**Dónde se ve en el sistema**

- Monorepo con libs compartidas
- Mismos tipos en frontend y backend
- Contratos generados, no escritos a mano
- Observabilidad embebida, no agregada después

**Visual:** [TODO `images/DC-02-componentes.png`] con etiquetas resaltadas: TypeScript · OpenAPI · AMQP versionado · OTel.
**Rúbrica:** C7

---

## Slide 16 — MIT Design AI — concepto

**IA como diseño, no como feature**

- Drivers explicables, no caja negra
- Fallback obligatorio
- Human-in-the-loop (override del pañolero)
- Guardrails (RC.15: no asistir a morosos)

**Visual:** Diagrama conceptual: IA centro + 6 dimensiones (datos, ética, explicabilidad, fallback, HITL, UX).
**Rúbrica:** C7

---

## Slide 17 — MIT Design AI — aplicación

**Dos usos concretos**

- **Asistente:** MCP + GPT-4o-mini · 6 tools de dominio
- **Scoring:** modelo ONNX · drivers visibles · score [0,1]
- Override del pañolero registrado en audit
- Guardrail de morosidad sobre el asistente

**Visual:** [TODO `images/SEQ-05-asistente-mcp.png`] miniatura + 6 tools listadas + drivers ejemplo.
**Rúbrica:** C7

---

## Slide 18 — Por qué Design FullStack + AI y no las otras

**Las 4 tendencias evaluadas**

- ✓ Design FullStack — encaja, factible MVP
- ✓ Design AI — encaja, factible MVP
- ✗ Math — encaja parcial, no factible MVP
- ✗ Quantum — no encaja con el problema

**Visual:** Matriz 2×2 (encaje × factibilidad).
**Rúbrica:** C7

---

## Slide 19 — Arquitectura: visión general

**El sistema en 1 diagrama**

- 1 sistema central
- 4 actores
- 3 sistemas externos: LDAP UNAB · OpenAI · email diferido
- 1 cliente web · 1 cliente tótem

**Visual:** [TODO `images/DC-01-contexto.png`] fullbleed.
**Rúbrica:** C5

---

## Slide 20 — Topología de microservicios

**9 servicios + 2 frontends + RabbitMQ + 8 Postgres**

- api-gateway (BFF)
- auth · inventory · request · loan
- notification · ai-risk · ai-assistant · reports
- domain.events / commands / delayed / dlx

**Visual:** [TODO `images/DC-02-componentes.png`] fullbleed.
**Rúbrica:** C5

---

## Slide 21 — Flujo crítico: solicitud → materialización

**El happy path en 8 pasos**

- Alumno arma carrito en portal
- request-svc reserva stock con TTL
- Pañolero valida en tótem
- loan-svc consulta scoring (RC.11)
- Préstamo materializado · ticket PDF generado

**Visual:** [TODO `images/SEQ-02-crear-solicitud.png`] + [TODO `images/SEQ-03-materializar-prestamo.png`] lado a lado.
**Rúbrica:** C5, C8

---

## Slide 22 — IA en acción: scoring + asistente

**Conversacional + decisional**

- Asistente: MCP tools + RC.15 guardrail
- Scoring: features sin sesgo · drivers visibles
- Latencia objetivo: ≤2 s asistente · ≤500 ms scoring
- Override siempre disponible

**Visual:** [TODO `images/SEQ-05-asistente-mcp.png`] (mitad superior) + tabla drivers de scoring (mitad inferior).
**Rúbrica:** C7, C8

---

## Slide 23 — EIP: catálogo aplicado

**Patrones de Hohpe en el sistema**

- Pub-Sub Channel — eventos de dominio
- Point-to-Point Channel — comandos
- Message Expiration — TTL reservas
- Dead Letter Channel — captura fallos
- Recipient List · Splitter · Aggregator · Process Manager · Content-Based Router · Translator · Enricher · Normalizer

**Visual:** [TODO `images/EIP-01-crear-solicitud.png`] fullbleed.
**Rúbrica:** C5, condición mínima 4

---

## Slide 24 — EIP en acción: Devolución y Compensación

**2 flujos críticos con notación EIP**

- **Devolución:** Content-Based Router (BUENO/DAÑADO/FALTANTE) + Aggregator (RC.01) + Recipient List
- **Compensación:** Process Manager (saga TTL) + Routing Slip (3 pasos) + Recipient List
- Ambos flujos son idempotentes

**Visual:** [TODO `images/EIP-03-compensacion.png`] (izq) + [TODO `images/EIP-02-devolucion.png`] (der).
**Rúbrica:** C5, condición mínima 4

---

## Slide 25 — EIP en acción: Outbox + Idempotent Receiver

**Garantía exactly-once efectiva**

- Outbox table en misma TX que cambio de negocio
- Relay polling lee y publica
- Consumer chequea processed_events antes de procesar
- Sobrevive reintentos, broker caído, replays

**Visual:** [TODO `images/EIP-05-outbox-idempotent.png`] fullbleed.
**Rúbrica:** C5, condición mínima 4

---

## Slide 26 — ADRs: las decisiones técnicas

**16 ADRs documentados (formato MADR)**

- ADR-002: Postgres en lugar de Mongo
- ADR-005: RabbitMQ en lugar de Kafka
- ADR-006: Saga coreografiada en lugar de orquestada
- ADR-009: Cloud-agnóstico
- ADR-016: Path-based routing del edge

**Visual:** Lista de los 16 ADRs como tarjetas + zoom a 3 destacados.
**Rúbrica:** C4, C5

---

## Slide 27 — Amenazas e impacto esperado

**Lo que puede fallar y cómo lo mitigamos**

- Bias del modelo IA → features prohibidas + drivers + override
- OpenAI caído → asistente degradable, core funciona
- RabbitMQ caído → outbox absorbe
- Resistencia humana → tótem preserva rol del pañolero

**Impacto esperado:** −80% tiempo validación · +100% trazabilidad · −50% mermas no detectadas.

**Visual:** Tabla 3 columnas (amenaza/mitigación/impacto) + KPIs como cards.
**Rúbrica:** C4, C8

---

## Slide 28 — Prototipo funcional

**Demo en vivo — 2-3 min**

- Login alumno → solicitud → tótem → préstamo
- Asistente conversacional sugiriendo recursos
- Notificación in-app + ticket PDF
- Trazabilidad observable
- Caso de error: TTL vencido → compensación

**Visual:** [TODO `images/prototipo-screenshot.png`] (sup) + `images/setup-fisico.svg` (inf).
**Rúbrica:** C9, condición mínima 3

---

## Slide 28b — Demo vs Producción

**Honestidad técnica: lo que ven vs lo objetivo**

| Capa | Demo | Producción |
|---|---|---|
| Persistencia | In-memory | 8 Postgres + Prisma |
| Comunicación | HTTP síncrono | RabbitMQ + 4 EIPs |
| Observabilidad | console logs | OTel + Grafana |
| Servicios | 6 | 9 hexagonales |
| Auth + UI | igual ✓ | igual ✓ |

- Demo arranca en 60 s ante el jurado
- Infra productiva validada con 7/7 smoke tests
- Divergencia mapeada en `app/ARQUITECTURA-DEMO.md`

**Visual:** [TODO `images/ARCH-01-demo-vs-produccion.png`] fullbleed.
**Rúbrica:** C5, C6, condición mínima 3

---

## Slide 29 — Conclusiones y próximos pasos

**3 takeaways**

- LeSS funciona si el PO es único y disciplinado
- EIP no son teoría, son respuestas a dolores reales
- Design AI exige drivers + fallback, no solo modelos

**Próximos pasos**

- Reentrenar modelo con datos reales tras 1 mes
- Email diferido (ADR-007 reactivado)
- Replicar a otras escuelas (Civil, Industrial)
- Migrar saga a Temporal cuando >20 CU

> *El Pañol no es un CRUD digital. Es plataforma con inteligencia, observable, evolutiva.*

**Visual:** 3 íconos takeaways + roadmap horizontal corto + cierre institucional.
**Rúbrica:** C10
