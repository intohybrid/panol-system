# PPT — Script del expositor

**Sistema de Pañol — UNAB Viña del Mar.** Lo que se dice en voz alta al presentar cada slide. Para el contenido visible en cada slide ver `PPT-slides.md`.

**Convenciones del script:**

- Tiempo objetivo entre paréntesis (`~30 s`).
- Tono conversacional, primera persona plural ("nosotros decidimos…").
- Frases cortas, evitar leer el slide.
- En *cursiva* las acciones físicas o pausas (cambiar de slide, señalar visual, etc.).

**Tiempo total objetivo:** 12–14 min para los 30 slides + 2–3 min de demo en vivo (slide 28).

---

## Slide 1 — Portada *(~15 s)*

"Buenas tardes. Presentamos el Caso 11: el Sistema de Pañol de la Escuela de Informática UNAB Viña del Mar. Una plataforma distribuida con inteligencia artificial diseñada con metodología LeSS y dos tendencias de MIT: Design FullStack y Design AI."

*Avanzar al siguiente slide.*

---

## Slide 2 — Agenda *(~25 s)*

"La presentación tiene cuatro bloques. Primero el problema de negocio. Luego cómo lo abordamos: con qué metodología y qué tendencias. Después el detalle del software con sus diagramas y decisiones técnicas. Y cerramos con el prototipo funcional, las amenazas y nuestras conclusiones. Catorce minutos en total, más una demo corta de dos minutos al final."

---

## Slide 3 — Contexto organizacional *(~30 s)*

"El pañol es la bodega de herramientas e instrumentos de la escuela. Tiene cuatro actores con roles distintos: alumnos que solicitan, pañoleros que entregan, coordinadores que aprueban casos especiales y el jefe de carrera que tiene visión global. Manejamos del orden de quinientos alumnos y quinientos recursos en rotación constante. Hoy todo se hace en papel, sin sistema digital."

---

## Slide 4 — El problema actual *(~30 s)*

"El registro actual es manual en cuaderno. Eso significa: cero trazabilidad histórica, pérdidas que nadie detecta porque nadie las cuenta, ningún reporte de gestión, y lo más serio para la rúbrica RC.01 — bloquear a un alumno por morosidad es imposible de auditar. Si el pañolero dice que devolvió, no hay forma de demostrar lo contrario semanas después."

*Señalar visual: ANTES papel manchado / DESPUÉS dashboard digital.*

---

## Slide 5 — La propuesta *(~30 s)*

"Proponemos tres interfaces sobre un solo backend. Un portal web para alumnos y docentes. Un tótem touch en el mostrador donde opera el pañolero. Y un asistente conversacional con MCP y GPT-4o-mini que ayuda al alumno a elegir recursos antes de solicitarlos. Todo con trazabilidad end-to-end vía Grafana y bloqueo automático por morosidad respaldado por la regla RC.01."

---

## Slide 6 — Requerimientos principales *(~25 s)*

"Catorce requerimientos funcionales, dieciocho reglas de contenido, diez no funcionales. Los empaquetamos en once épicas, cincuenta user stories distribuidas en tres sprints de dos semanas. Las reglas críticas que dominan el diseño son: RC.01 sobre morosidad, RC.06 sobre TTL de reservas, RC.16 sobre estados de la solicitud. La trazabilidad RF a CU a US a Sprint está en el documento de trazabilidad."

---

## Slide 7 — Supuestos, contradicciones y restricciones *(~30 s)*

"Tomamos cuatro decisiones explícitas frente al enunciado. Primero, abandonamos el stack MERN del enunciado: vamos con Postgres y NestJS porque el dominio es transaccional, eso está justificado en ADR-002 y ADR-003. Segundo, la IA es opcional: si OpenAI cae, el flujo principal funciona; eso está en ADR-007. Tercero, diseñamos cloud-agnóstico, sin lock-in. Cuarto, el tótem es físico, no móvil: la regla RC.14 lo exige."

---

## Slide 8 — Metodología LeSS *(~25 s)*

"Elegimos LeSS porque escala Scrum a dos equipos sin agregar proceso. Mantenemos un solo backlog, un Product Owner único, y las ceremonias clave son compartidas: planning entre los dos equipos, review única. Sprints de dos semanas. Cero overhead burocrático. La metodología se adapta al tamaño del equipo, no al revés."

---

## Slide 9 — LeSS vs RUP *(~20 s)*

"Descartamos RUP. Es pesado, orientado a documentación voluminosa, con iteraciones largas de cuatro a seis semanas y roles fragmentados — analista, arquitecto, desarrollador como gente distinta. No calza con dos equipos pequeños y un MVP de seis semanas."

---

## Slide 10 — LeSS vs SAFe *(~20 s)*

"Descartamos SAFe por la razón opuesta: está diseñado para cincuenta a ciento veinticinco personas, con cuatro niveles — Team, Program, Solution, Portfolio. Para nosotros sería sobre-engineering. La burocracia mataría la velocidad del MVP."

---

## Slide 11 — LeSS aplicado al caso *(~30 s)*

"Tenemos dos equipos de cuatro a cinco personas cada uno. Equipo A toma el núcleo transaccional: auth, inventory, request, loan. Equipo B toma la experiencia: frontends, IA, reports y notification. Hacemos Planning Two-Team al inicio de cada sprint y Review única al cierre. Tres sprints de dos semanas para llegar al MVP demostrable."

---

## Slide 12 — Plataforma Jira *(~25 s)*

"La plataforma elegida es Jira. Es el estándar de la industria, tiene JQL, integración con CI/CD y reportes nativos. Cargamos las cincuenta user stories con sus épicas, sprints, equipos y story points usando un script Python que llama a la API REST. La trazabilidad RF-a-story queda en las etiquetas de cada issue."

*Señalar el screenshot del Backlog.*

---

## Slide 13 — Trazabilidad RF → US en Jira *(~25 s)*

"De requerimiento a código en un click. Cada user story tiene una etiqueta `RF:` con el número del requerimiento que satisface. Una query JQL — por ejemplo `labels = RF:RF.4` — me devuelve todas las US ligadas a ese RF. Las épicas agrupan por dominio. Los sprints son nativos de Jira. Trazabilidad sin spreadsheets externos."

---

## Slide 14 — MIT Design FullStack — concepto *(~30 s)*

"MIT Design FullStack no es lo mismo que un desarrollador fullstack. Es un enfoque de diseño donde todas las capas se piensan simultáneamente desde el día cero: UX, API, datos, infra, observabilidad. Su clave es la coherencia: stack único de extremo a extremo, contratos explícitos, cloud-agnóstico, y telemetría incorporada al MVP, no agregada después."

---

## Slide 15 — MIT Design FullStack — aplicación *(~30 s)*

"Lo aplicamos así: TypeScript end-to-end, mismos tipos en frontend y backend gracias al monorepo. OpenAPI versionado por servicio. Eventos AMQP con header `x-schema-version`. OpenTelemetry desde día uno con trace-id propagado por headers AMQP. Los contratos no se escriben a mano, se generan."

*Señalar las etiquetas resaltadas en el diagrama de componentes.*

---

## Slide 16 — MIT Design AI — concepto *(~25 s)*

"Design AI exige tratar a la IA como diseño, no como feature. Lo que se pide explícitamente: drivers explicables — no caja negra. Fallback obligatorio si el modelo no responde o no decide. Human-in-the-loop: el operador puede sobreescribir. Y guardrails — en nuestro caso RC.15: el asistente no ayuda a usuarios bloqueados por morosidad."

---

## Slide 17 — MIT Design AI — aplicación *(~30 s)*

"Tenemos dos usos concretos. El asistente conversacional usa MCP con GPT-4o-mini y seis tools de dominio: buscar catálogo, verificar disponibilidad, sugerir recursos por actividad, crear borrador, revisar mi historial, explicar reglas. El scoring usa un modelo ONNX con drivers visibles — el pañolero ve por qué dio ese score. El override del pañolero queda registrado en el audit."

---

## Slide 18 — Por qué Design FullStack + AI *(~30 s)*

"Evaluamos las cuatro tendencias del listado. Design FullStack y Design AI calzan con nuestro problema y son factibles para un MVP de seis semanas. Math Design encaja parcial pero no es factible: requeriría modelos matemáticos de optimización que no podemos entrenar a tiempo. Quantum no encaja con el problema. Por eso elegimos las dos primeras."

---

## Slide 19 — Arquitectura: visión general *(~30 s)*

"Esto es el sistema en un diagrama. Una caja central — el Sistema de Pañol — con cuatro actores conectados. Tres sistemas externos: LDAP/SSO de UNAB para autenticación, OpenAI para el asistente, y email diferido para roadmap. Dos clientes: portal web y tótem. Sin más entradas ni salidas."

---

## Slide 20 — Topología de microservicios *(~40 s)*

"Detrás del gateway viven nueve microservicios. Auth maneja identidad. Inventory maneja stock y reservas. Request maneja el ciclo de la solicitud con su TTL. Loan es el núcleo transaccional. Notification maneja in-app y ticket PDF. Ai-risk hace scoring. Ai-assistant es el conversacional. Reports es el read-model CQRS. Y entre todos, RabbitMQ con cuatro exchanges: domain.events, commands, delayed y dlx. Cada servicio tiene su Postgres dedicada."

---

## Slide 21 — Flujo crítico *(~40 s)*

"El happy path tiene ocho pasos. El alumno arma carrito en el portal. Request-svc valida usuario activo y stock disponible, reserva con TTL de quince minutos. Cuando el alumno aparece físicamente, el pañolero ve la solicitud en el tótem. Loan-svc consulta scoring a ai-risk-svc — esa consulta es la regla RC.11. Si el score es aceptable, materializa el préstamo. Notification-svc genera el ticket PDF que el alumno recibe en su bandeja in-app. Stock se descuenta atómicamente."

---

## Slide 22 — IA en acción *(~30 s)*

"La IA tiene dos puntos de aplicación. El asistente conversacional es streaming, latencia objetivo dos segundos, con guardrail RC.15 — no asiste a morosos. El scoring es síncrono cuando el pañolero materializa, latencia objetivo medio segundo, con drivers visibles. El override del pañolero está siempre disponible. Si rechaza la sugerencia del modelo, queda registrado para auditar el bias."

---

## Slide 23 — EIP catálogo aplicado *(~35 s)*

"Aplicamos el catálogo de Hohpe — Enterprise Integration Patterns — explícitamente. Pub-Sub Channel para los eventos de dominio. Point-to-Point Channel para los comandos. Message Expiration con plugin x-delayed-message para el TTL de reservas. Dead Letter Channel para captura de fallos. Y patrones de routing y transformación: Recipient List, Splitter, Aggregator, Process Manager, Content-Based Router, Translator, Enricher, Normalizer. Cada patrón resuelve un dolor real, no es teoría."

---

## Slide 24 — EIP en acción: Devolución y Compensación *(~35 s)*

"Dos flujos críticos. La devolución usa Content-Based Router para clasificar items por estado — bueno, dañado, faltante. Después un Aggregator en auth-svc evalúa la regla RC.01 con N eventos loan.overdue: si el alumno acumula dos atrasos o un faltante en el semestre, queda bloqueado. La compensación de reserva vencida usa Process Manager para la coordinación temporal y Routing Slip para el itinerario de tres pasos: marcar vencida, liberar reserva, notificar. Ambos son idempotentes."

---

## Slide 25 — EIP en acción: Outbox + Idempotent Receiver *(~35 s)*

"Sin Outbox no hay saga confiable. La misma transacción que cambia el estado del agregado escribe la fila en `outbox_events`. Un relay polling lee filas no publicadas y las despacha al broker. El consumer chequea la tabla `processed_events` antes de procesar — si ya está, descarta. Esto convierte el at-least-once de RabbitMQ en effectively exactly-once. Sobrevive reintentos, broker caído, replays."

---

## Slide 26 — ADRs *(~40 s)*

"Tomamos dieciséis decisiones arquitectónicas, cada una documentada como ADR en formato MADR. Tres destacadas: PostgreSQL en vez de MongoDB porque el dominio exige ACID y joins. RabbitMQ en vez de Kafka porque nuestro throughput está muy por debajo de donde Kafka brilla, y RabbitMQ tiene delayed exchange y DLX nativos. Saga coreografiada en vez de orquestada porque siete casos de uso no justifican un Temporal. Cada decisión tiene contexto, alternativas, decisión y consecuencias."

---

## Slide 27 — Amenazas e impacto *(~30 s)*

"Las amenazas las trabajamos explícitamente. Bias del modelo: features prohibidas, drivers visibles, override humano. Dependencia OpenAI: el asistente es opcional, el flujo core funciona sin él. RabbitMQ caído: outbox pattern lo absorbe. Resistencia humana: el tótem preserva el rol del pañolero como validador, no lo reemplaza. El impacto positivo esperado: ochenta por ciento menos tiempo de validación, trazabilidad completa, cincuenta por ciento menos mermas no detectadas."

---

## Slide 28 — Prototipo funcional *(~35 s + demo en vivo 2–3 min)*

"El prototipo es ejecutable. La demo de dos minutos cubre el ciclo completo: login del alumno, conversación con el asistente que sugiere recursos, solicitud creada, validación en el tótem con scoring visible, materialización con ticket PDF y devolución. Cerramos con el caso de error: una solicitud no validada en TTL, y el DLX disparando la compensación automática."

*Cambiar a la pantalla del demo. Ejecutar `npm run demo` (ya levantado). Mostrar los flujos en vivo siguiendo el guion del slide 28.*

---

## Slide 28b — Demo vs Producción *(~30 s)*

"Antes de pasar a las conclusiones, una nota de honestidad técnica. Lo que acaban de ver corre en modo mock-first: in-memory en vez de Postgres, HTTP síncrono entre servicios en vez de RabbitMQ. Eso es deliberado — la demo necesita arrancar en sesenta segundos. La arquitectura objetivo, la del MVP final, es la que está documentada: ocho bases Postgres, RabbitMQ con cuatro exchanges, EIP completos. Y eso ya lo validamos con siete smoke tests automatizados que pasan en verde. La diferencia entre demo y producción está mapeada en `ARQUITECTURA-DEMO.md`, divergencia por divergencia, con su justificación."

---

## Slide 29 — Conclusiones y próximos pasos *(~35 s)*

"Tres aprendizajes. Uno: LeSS funciona muy bien para dos equipos si el PO es único y disciplinado; las ceremonias compartidas son el antídoto contra la divergencia. Dos: los EIP no son teoría académica, cada patrón que aplicamos resolvió un dolor real — outbox, expiration, idempotent receiver. Tres: Design AI exige drivers explicables y fallback, no basta con que el modelo prediga bien."

"Próximos pasos: reentrenamiento con datos reales tras un mes, integración email, replicar a otras escuelas, migrar a Temporal cuando crezcamos a más de veinte casos de uso."

"El Pañol no es un CRUD digital. Es plataforma con inteligencia, observable, evolutiva. Gracias."

---

# Anexo — Tiempos por bloque

| Bloque | Slides | Tiempo |
|---|---|---|
| Apertura | 1–2 | 0:40 |
| Negocio | 3–7 | 2:25 |
| Metodología LeSS | 8–11 | 1:35 |
| Plataforma Jira | 12–13 | 0:50 |
| Tendencias MIT | 14–18 | 2:25 |
| Arquitectura + IA | 19–22 | 2:20 |
| EIP | 23–25 | 1:45 |
| ADRs + Amenazas | 26–27 | 1:10 |
| Prototipo + demo | 28 + 28b | 1:05 + 2:30 demo |
| Cierre | 29 | 0:35 |
| **Total** | | **~14:50 + demo** |

# Anexo — Checklist pre-grabación

- [ ] Tener Jira proyecto cargado y los 2 screenshots tomados
- [ ] `cd app && npm run demo` levantado y verde
- [ ] (Opcional) `cd infra && docker compose up -d` para mostrar EIPs reales en Grafana
- [ ] Las 14 imágenes en `docs/presentation/images/` (4 SVG + 10 PNG/screenshots)
- [ ] OpenAI API key activa si se va a demostrar el asistente con LLM real
- [ ] Caso TTL probado (puede requerir bajar TTL a 30 seg para que vence en demo)
- [ ] Cronometrar 1 vez antes de grabar el video final
