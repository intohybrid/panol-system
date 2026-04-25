# Presentación Final — Sistema de Pañol (Caso 11)

> Contenido completo de la presentación para el video final del proyecto integrador.
> Cada slide incluye: título, bullets/cuerpo, notas del expositor (locución sugerida ~20-30 seg), visual y mapeo a la rúbrica.

**Equipo:** Magíster en Ingeniería en Informática — UNAB
**Caso:** 11 — Sistema de Pañol, Escuela de Informática UNAB Viña del Mar
**Metodología:** LeSS básico
**Tendencias seleccionadas:** MIT Design FullStack + MIT Design AI
**Plataforma:** Jira

**Total:** 29 slides | Duración estimada del video: 12–14 min

---

## Mapa de cobertura de la rúbrica

| Criterio | Pts | Slides |
|---|---|---|
| C1 Contexto y problema | 10 | 3, 4, 6 |
| C2 Metodología principal | 20 | 8, 9, 10, 11, 13 |
| C3 Plataforma de gestión | 10 | 12, 13 |
| C4 Supuestos / contradicciones / marco de decisión | 10 | 7, 26 |
| C5 Alternativas y descarte | 15 | 9, 10, 18, 26 |
| C6 EIP en el diseño | 10 | 23, 24, 25 |
| C7 Tendencias (≥2) | 10 | 14, 15, 16, 17, 18, 22 |
| C8 Contexto / problema / propuesta / amenazas / impacto | 10 | 3, 4, 5, 7, 19, 20, 21, 27 |
| C9 Prototipo funcional | 10 | 21, 28 |
| C10 Calidad expositiva | 5 | 1, 2, 29 (estructura global) |

**Condiciones mínimas obligatorias** — todas cubiertas: plataforma con evidencia (12-13), alternativas justificadas (9-10, 18, 26), prototipo demostrable (28), EIP aplicado no solo nombrado (23-25), tendencias integradas al caso y prototipo (14-17, 22).

---

# PARTE 0 — APERTURA

---

## Slide 1 — Portada

**Título:** Sistema de Pañol — UNAB Viña del Mar

**Subtítulo:** Plataforma digital con IA para la gestión de préstamos del pañol de la Escuela de Informática

**Cuerpo:**
- Caso 11 — Proyecto Integrador
- Magíster en Ingeniería en Informática — UNAB
- Tópicos de Ingeniería
- Equipo: [Nombres del equipo]
- Fecha: [Fecha de entrega]

**Notas del expositor (~15 seg):**
"Buenas tardes. Presentamos el Caso 11: el Sistema de Pañol de la Escuela de Informática UNAB Viña del Mar. Una plataforma distribuida con inteligencia artificial diseñada con metodología LeSS, MIT Design FullStack y MIT Design AI."

**Visual:** [Imagen institucional UNAB] + ícono o foto del pañol + logos discretos de las tendencias usadas

**Rúbrica:** —

---

## Slide 2 — Agenda

**Título:** Lo que vas a ver

**Cuerpo:** 4 bloques en línea de tiempo:

1. **El negocio y el problema** — qué pasa hoy en el pañol y por qué hay que intervenir (~3 min)
2. **Metodología y tendencias** — LeSS, Jira, MIT Design FullStack y Design AI (~4 min)
3. **Diseño del software** — arquitectura, casos de uso, EIP y ADRs (~4 min)
4. **Prototipo y cierre** — demo funcional, amenazas, impacto, conclusiones (~3 min)

**Notas del expositor (~20 seg):**
"La presentación tiene cuatro bloques. Primero el problema de negocio. Luego cómo lo abordamos: con qué metodología y qué tendencias. Después el detalle del software con sus diagramas y decisiones técnicas. Y cerramos con el prototipo funcional, las amenazas y nuestras conclusiones."

**Visual:** Línea de tiempo horizontal con los 4 bloques numerados y duración aproximada

**Rúbrica:** C10

---

# PARTE 1 — EL NEGOCIO

---

## Slide 3 — Contexto organizacional

**Título:** El pañol de la Escuela de Informática UNAB

**Cuerpo:**
- **Universidad:** Universidad Andrés Bello, sede Viña del Mar
- **Unidad:** Escuela de Informática (carreras de Ingeniería Civil Informática e Ingeniería de Ejecución en Informática)
- **Pañol:** bodega de equipos electrónicos, herramientas e instrumentos de medición que la escuela presta a alumnos para sus laboratorios y proyectos
- **Volumen estimado:** 600+ alumnos activos, 400-600 préstamos por mes en peak académico
- **Actores principales:**
  - **Alumnos** — solicitan equipos para clases y proyectos
  - **Pañoleros** — entregan, validan, reciben devoluciones
  - **Administradores** — gestionan catálogo, usuarios, parámetros
  - **Director de carrera** — visibilidad de gestión

**Notas del expositor (~25 seg):**
"El pañol es la bodega donde la Escuela de Informática presta multímetros, osciloscopios, protoboards y todo el equipamiento que un alumno de informática necesita para sus laboratorios. Tiene tres tipos de actores: el alumno que pide, el pañolero que opera, y la administración que gestiona el catálogo. En peak académico se mueven entre 400 y 600 préstamos al mes."

**Visual:** [Imagen del pañol o foto referencial] + diagrama simple de actores con stick figures (4 roles)

**Rúbrica:** C1, C8

---

## Slide 4 — El problema actual

**Título:** Lo que hoy duele

**Cuerpo:**
- **Registro en papel y planillas Excel** — el pañolero anota el RUT y los items en una libreta
- **Sin trazabilidad histórica del alumno** — no sabemos quién tiene historial de atrasos
- **Mermas no detectadas a tiempo** — un equipo perdido aparece semanas después
- **Atrasos sin sanción automática** — depende de la memoria del pañolero
- **Sin visibilidad de stock en tiempo real** — el alumno llega y descubre que no hay
- **Sin asistencia al alumno** — quien no sabe qué pedir, pide mal o se va sin
- **Riesgo operativo** — si el pañolero falta, el sistema se detiene

**Notas del expositor (~25 seg):**
"Hoy el proceso es manual. Se anota en papel, no hay historial, las pérdidas se descubren tarde, los atrasos no se sancionan de manera consistente. Y para el alumno la experiencia es frustrante: llega y no hay stock, o no sabe qué necesita exactamente. Todo el sistema depende de una persona y su libreta."

**Visual:** [Imagen de cuaderno/libreta de registro manual] o ilustración "antes / después"

**Rúbrica:** C1, C8

---

## Slide 5 — La propuesta

**Título:** Pañol digital con IA y arquitectura distribuida

**Cuerpo:** Tres pilares:

1. **Self-service web + tótem físico** — el alumno arma su solicitud en la web; el pañolero valida y materializa en un tótem en el mostrador
2. **Microservicios con eventos** — 8 servicios desacoplados sobre RabbitMQ; cada uno escalable y desplegable independiente
3. **Inteligencia artificial integrada**
   - Scoring de riesgo predictivo (Random Forest) que apoya la decisión del pañolero
   - Asistente conversacional con MCP que guía al alumno

**Beneficios esperados:**
- Operativo: -80% tiempo de validación (estimado)
- Gestión: trazabilidad completa, alertas automáticas
- Alumno: experiencia fluida, ayuda contextual

**Notas del expositor (~25 seg):**
"Nuestra propuesta tiene tres pilares. Primero, una experiencia digital de doble cara: el alumno arma su solicitud en la web, el pañolero la materializa en un tótem físico en el mostrador. Segundo, una arquitectura de microservicios con bus de eventos que desacopla y escala. Y tercero, IA integrada: scoring para predecir riesgo de atraso, y un asistente conversacional para guiar al alumno."

**Visual:** [Imagen mockup combinado: pantalla web + tótem + chat del asistente]

**Rúbrica:** C8

---

## Slide 6 — Requerimientos principales

**Título:** Lo que el sistema debe hacer

**Cuerpo:**

| Tipo | Cantidad | Ejemplos destacados |
|---|---|---|
| RF (funcionales) | 14 | autenticación, catálogo, solicitudes, materialización, devoluciones, scoring IA, asistente IA |
| RF-C (cross-cutting) | 13 | trazabilidad, observabilidad, seguridad, idempotencia, audit log |
| RC (reglas de negocio) | 18 | RC.11 umbrales scoring (0.7 / 0.4), RC.16 transición de estados, RC.18 cálculo de atraso, RC.15 bloqueo de usuarios |
| RS (reglas de seguridad) | varias | RS.3 PIN para acciones sensibles, RS.4 JWT con rotación |
| **CU principales** | **7** | login, solicitar préstamo, validar/materializar, devolver, alta de usuarios/catálogo, scoring, asistente |

Mapeados a 11 épicas: `auth`, `inventario`, `solicitudes`, `prestamos`, `notificaciones`, `ia`, `gestion`, `reportes`, `portal`, `totem`, `plataforma`.

**Notas del expositor (~20 seg):**
"El sistema cubre 14 requerimientos funcionales, 13 transversales, 18 reglas de negocio y 7 casos de uso principales, organizados en 11 épicas. Todo trazable: cada user story del backlog apunta al requerimiento que implementa."

**Visual:** Mapa mental simple de las 11 épicas + tabla con los 4 tipos de requerimientos

**Rúbrica:** C1, C8

---

## Slide 7 — Supuestos, contradicciones y restricciones

**Título:** El marco de decisión

**Cuerpo:** Tabla 4 columnas:

**Supuestos (qué damos por verdadero):**
- Red WiFi de la escuela es estable durante horario académico
- Alumnos tienen smartphone con browser actualizado
- Hay un pañolero presente en horario de atención
- El catálogo cambia poco: alta de items < 1 vez por semana

**Contradicciones (tensiones reales):**
- UX simple para alumno ↔ control estricto exigido por administración
- Asistente IA proactivo ↔ usuarios tradicionales reticentes a "chatear con un bot"
- Microservicios desacoplados ↔ equipo pequeño con 3 sprints de plazo
- Self-service ↔ rol del pañolero como guardián del proceso

**Restricciones:**
- Equipo: 4 personas, 2 Feature Teams
- Plazo: 6 semanas (3 sprints de 2 semanas)
- Sin presupuesto cloud (debe correr en hardware on-premise o local)
- Stack base sugerido: MERN (modificado a TypeScript + PostgreSQL)
- Sin acceso a datos históricos reales para entrenar modelos

**Amenazas (riesgos que monitoreamos):**
- Modelo IA con bias por entrenamiento sintético inicial
- Dependencia de OpenAI API (latencia, costo, disponibilidad)
- RabbitMQ como single point of failure si no se replica
- Resistencia al cambio de los pañoleros actuales

**Notas del expositor (~30 seg):**
"Antes de decidir, declaramos el marco. Asumimos red estable y alumnos con celular. Reconocemos contradicciones reales — la UX simple y el control estricto pelean entre sí. Tenemos restricciones duras: 4 personas, 6 semanas, sin presupuesto cloud. Y amenazas que monitoreamos: bias del modelo, dependencia de OpenAI, broker como punto único, y la resistencia humana al cambio. Cada decisión técnica que verán a continuación responde a estas restricciones."

**Visual:** Tabla 2×2 (4 cuadrantes) o 4 columnas paralelas, sin diagrama

**Rúbrica:** C4, C8

---

# PARTE 2 — METODOLOGÍA Y TENDENCIAS

---

## Slide 8 — Metodología principal: LeSS

**Título:** LeSS — Large-Scale Scrum básico

**Cuerpo:**

**Qué es LeSS:** una extensión mínima de Scrum para múltiples equipos trabajando sobre un producto único. Creado por Craig Larman y Bas Vodde.

**Principios fundacionales (los que más nos importan):**
- **Un solo Product Backlog** — todos los equipos trabajan del mismo backlog
- **Un solo Product Owner** — una sola voz prioriza
- **Feature Teams** — equipos cross-funcionales que pueden tomar cualquier feature, no equipos por componente
- **Definition of Done compartida** — la barrera de calidad es única
- **Sprint Review única** — todos los equipos demuestran juntos

**Variantes:**
- LeSS básico: 2-8 equipos. Ceremonias compartidas livianas.
- LeSS Huge: 8+ equipos con Area Product Owners.

**Nuestra elección:** LeSS básico — encaja con 2 Feature Teams.

**Notas del expositor (~25 seg):**
"LeSS, Large-Scale Scrum, es una extensión mínima de Scrum para múltiples equipos. Mantiene un solo backlog, un solo PO, y exige Feature Teams: equipos cross-funcionales que pueden tomar cualquier story, no equipos partidos por componente. Para nuestro caso elegimos LeSS básico, que es la variante para 2 a 8 equipos."

**Visual:** Diagrama del modelo LeSS — 2 equipos, 1 backlog, 1 PO, ceremonias compartidas

**Rúbrica:** C2

---

## Slide 9 — LeSS vs RUP — por qué descartamos RUP

**Título:** Por qué no RUP

**Cuerpo:** Comparación específica:

| Dimensión | RUP | LeSS | Veredicto |
|---|---|---|---|
| **Filosofía** | Iterativo pero pesado en fases (Inception, Elaboration, Construction, Transition) | Iterativo ligero, sprints de 2 semanas | LeSS es más rápido para producir valor visible |
| **Roles** | 30+ roles especializados (Software Architect, Configuration Manager, Test Designer, etc.) | 3 roles (PO, SM, Equipo) | Equipo de 4 no soporta 30 roles |
| **Artefactos** | Documentación extensa (Vision, Use Cases, SAD, Test Plan, etc.) por fase | Backlog + DoR/DoD + ADRs incrementales | RUP genera overhead documental que no podemos sostener |
| **Adaptabilidad** | Cambios cuestan más en fases avanzadas | Cambios cada 2 semanas | LeSS encaja mejor con problema poco explorado |
| **Adopción** | Requiere training formal | Curva más suave | Equipo no tiene experiencia previa con RUP |

**Conclusión:** RUP fue diseñado para grandes proyectos de larga duración con equipos jerárquicos. **Nuestro caso (4 personas, 6 semanas, problema en exploración) es exactamente lo opuesto.**

**Notas del expositor (~30 seg):**
"RUP es muy bueno para proyectos largos, equipos jerárquicos y dominio bien conocido. Pero exige fases pesadas, treinta roles especializados, y mucha documentación por fase. Con cuatro personas, seis semanas y un problema que recién estamos explorando, RUP nos asfixia. Lo descartamos por overhead que no podemos absorber."

**Visual:** Tabla comparativa estilo "vs" + ícono X grande sobre RUP

**Rúbrica:** C2, C5

---

## Slide 10 — LeSS vs SAFe — por qué descartamos SAFe

**Título:** Por qué no SAFe

**Cuerpo:**

| Dimensión | SAFe | LeSS | Veredicto |
|---|---|---|---|
| **Escala objetivo** | 50-125+ personas (Essential SAFe) | 2-8 equipos (10-50 personas) | SAFe es para escala que no tenemos |
| **Roles adicionales** | RTE, System Architect, Business Owner, Solution Train Engineer, Product Management | Solo PO + SM × N | SAFe inventa roles que para 4 personas son ridículos |
| **Cadencia** | PI Planning de 2 días cada 8-12 semanas | Sprint Planning Two-Team (4 hrs cada 2 semanas) | PI Planning consumiría más tiempo que el sprint mismo |
| **Niveles** | Team / Program / Large Solution / Portfolio | Solo Team + coordinación liviana | SAFe agrega niveles que no necesitamos |
| **Filosofía** | "Agile a escala empresarial con gobernanza" | "Solo lo necesario para escalar Scrum" | LeSS prioriza descentralización |

**Conclusión:** SAFe nació para empresas grandes que quieren transformación ágil con gobernanza. **No somos una empresa grande.** Adoptar SAFe sería ceremonia sin sustancia.

**Cita relevante (Larman & Vodde):** *"More with less."* La idea central de LeSS es lograr más eliminando ceremonia y rol innecesario, no agregándolos.

**Notas del expositor (~30 seg):**
"SAFe es excelente para empresas de cien o más personas que necesitan gobernanza y alineamiento entre múltiples Agile Release Trains. Nuestro proyecto tiene cuatro personas. Adoptar SAFe sería pegar un PI Planning de dos días sobre un sprint de dos semanas — más tiempo en ceremonia que en código. Por eso también lo descartamos."

**Visual:** Tabla comparativa + diagrama esquemático de los niveles de SAFe (Team/Program/Solution/Portfolio) tachado

**Rúbrica:** C2, C5

---

## Slide 11 — LeSS aplicado al caso

**Título:** LeSS aplicado: 2 Feature Teams, 3 sprints, 50 user stories, 265 puntos

**Cuerpo:**

**Estructura del equipo:**
- **Team A** — foco preferente: auth, solicitudes, préstamos, devoluciones, portal (~50 puntos/sprint)
- **Team B** — foco preferente: inventario, notificaciones, IA, reportes, plataforma, tótem (~50 puntos/sprint)
- **PO único** + 1 Scrum Master por equipo (rol rotativo)

**Cadencia de los 3 sprints (2 semanas cada uno):**

| Sprint | US | Pts | Foco |
|---|---|---|---|
| Sprint 0 | 14 | 64 | Plataforma + auth + catálogo base |
| Sprint 1 | 19 | 107 | Flujo solicitud → préstamo → devolución + asistente MVP |
| Sprint 2 | 17 | 94 | IA, gestión, reportes, consolidación |

**Ceremonias compartidas:**
- Sprint Planning Two-Team (4 hrs)
- Daily Scrum por equipo (15 min)
- Backlog Refinement compartido
- **Sprint Review única** — un solo demo
- Retrospectiva por equipo + Overall Retro

**DoR y DoD globales** documentados en `docs/agile/README.md`.

**Notas del expositor (~30 seg):**
"Aplicado al caso, dos Feature Teams de dos personas cada uno, con foco preferente pero cualquiera puede tomar cualquier story. Tres sprints de dos semanas: el cero arma plataforma, el uno construye el flujo principal, el dos cierra con IA y reportes. 50 user stories, 265 puntos totales. Definition of Ready y Definition of Done compartidas y documentadas."

**Visual:** Diagrama de cadencia (línea de tiempo de 6 semanas con sprints + hitos) o tabla de los 3 sprints

**Rúbrica:** C2

---

## Slide 12 — Plataforma de gestión: Jira

**Título:** Evidencia del proceso en Jira

**Cuerpo:**

**Por qué Jira:**
- Estándar de facto en industria — el equipo lo va a usar al egresar
- JQL para queries avanzadas (`project = PNL AND sprint in openSprints() AND assignee = currentUser()`)
- Integración nativa con CI/CD, Confluence, Slack
- Reportes burndown, velocity, control charts incluidos
- Roadmap visual entre épicas

**Lo que cargamos:**
- 1 proyecto: **Sistema de Pañol — UNAB Viña del Mar**
- 50 user stories distribuidas en 3 sprints (Epic Link + Sprint asignado)
- 11 épicas con prefijo `epic:*`
- 53 etiquetas (`team:A/B`, `tipo:negocio/tecnica`, `RF:*`, `sprint:*`)
- Story points (Fibonacci) por US visibles para el rol Equipo
- Importación vía CSV + API REST (script `import_to_jira.py`)

**Notas del expositor (~25 seg):**
"La plataforma elegida es Jira. Es el estándar de la industria, tiene JQL, integración con CI/CD, reportes nativos. Cargamos las 50 user stories con sus épicas, sprints, equipos y story points usando un script Python que llama a la API REST. La trazabilidad RF a story queda en las etiquetas de cada issue."

**Visual:** [Screenshot de Jira — vista de Backlog con sprints + tablero del Sprint 1] — capturar al momento de grabar el video

**Rúbrica:** C3

---

## Slide 13 — Trazabilidad RF → US en Jira

**Título:** Cada user story apunta a un requerimiento

**Cuerpo:**

**Cómo se logra la trazabilidad:**
- Cada US tiene la etiqueta `RF:<código>` (ej. `RF:RF.4`, `RF:RC.11`, `RF:RS.3`)
- Filtros JQL en Jira: `labels = "RF:RF.4"` muestra todas las US que implementan ese requerimiento
- La matriz completa vive en `docs/requirements/07-trazabilidad.md`

**Extracto representativo (10 de 50):**

| US | Subject | Épica | Sprint | RF cubierto |
|---|---|---|---|---|
| US-008 | Login con email + password | auth | 0 | RS.3, RS.4 |
| US-014 | CRUD catálogo equipos | inventario | 0 | RF.6 |
| US-018 | Crear solicitud de préstamo | solicitudes | 1 | RF.7 |
| US-020 | TTL de reserva 15 min | solicitudes | 1 | RC.16 |
| US-024 | Materializar préstamo en tótem | prestamos | 1 | RF.8 |
| US-025 | Devolver préstamo | prestamos | 1 | RF.9 |
| US-032 | Asistente conversacional MVP | ia | 1 | RF.IA.2 |
| US-038 | Scoring predictivo | ia | 2 | RF.IA.1, RC.11 |
| US-042 | Bloqueo automático por morosidad | gestion | 2 | RC.15 |
| US-047 | Reporte gestión mensual | reportes | 2 | RF.RG.2 |

**Notas del expositor (~20 seg):**
"Cada user story tiene una etiqueta que apunta al requerimiento que implementa. En Jira esto permite filtros JQL para verificar cobertura: ¿qué stories cubren el RF de scoring? ¿Qué requerimientos no tienen story aún? La matriz completa en setenta filas vive en el documento de trazabilidad."

**Visual:** Tabla extracto + [Screenshot de Jira con filtro JQL aplicado mostrando US filtradas por etiqueta `RF:*`]

**Rúbrica:** C2, C3

---

## Slide 14 — MIT Design FullStack — concepto

**Título:** Tendencia 1: MIT Design FullStack

**Cuerpo:**

**Qué es Design FullStack en MIT:**
Un enfoque de diseño de producto que abarca **todas las capas simultáneamente** desde el día uno: experiencia de usuario, lógica de aplicación, modelo de datos, infraestructura, observabilidad y operaciones.

**Principios clave:**
1. **Stack único de extremo a extremo** — el mismo lenguaje (TypeScript) atraviesa frontend, backend, scripts y tests, reduciendo fricción cognitiva
2. **Diseño contractual entre capas** — APIs versionadas, schemas validados, eventos con contrato explícito
3. **Cloud-agnóstico por defecto** — diseñar para correr en cualquier proveedor o on-premise; evitar lock-in
4. **Observabilidad desde día 1** — tracing, métricas, logs estructurados son parte del MVP, no algo que se agrega "después"
5. **Continuous everything** — CI/CD, infraestructura como código, base de datos como código (migrations versionadas)

**Diferencia con "fullstack tradicional":**
Fullstack tradicional = un dev que toca front y back. Design FullStack = **el producto entero pensado como sistema integrado** desde la primera decisión.

**Notas del expositor (~25 seg):**
"MIT Design FullStack no es lo mismo que un desarrollador fullstack. Es un enfoque de diseño donde todas las capas se piensan simultáneamente desde el día cero: UX, API, datos, infra, observabilidad. Su clave es la coherencia: stack único de extremo a extremo, contratos explícitos, cloud-agnóstico, y telemetría incorporada al MVP, no agregada después."

**Visual:** Diagrama vertical de capas (UI → API → Domain → Data → Infra → Ops) con flechas bidireccionales que indican "diseño simultáneo"

**Rúbrica:** C7

---

## Slide 15 — MIT Design FullStack — aplicación al caso

**Título:** Cómo lo aplicamos en el Sistema de Pañol

**Cuerpo:**

**Stack único TypeScript de punta a punta:**
- Frontend web (Next.js 14) — TypeScript
- Frontend tótem (Vite + React) — TypeScript
- API Gateway + 8 microservicios (NestJS 10) — TypeScript
- Scripts (importación, migrations, seeds) — TypeScript / Python
- Tests E2E (Playwright) — TypeScript

**Contratos explícitos entre capas:**
- OpenAPI spec por cada microservicio (auto-generado desde controllers NestJS)
- Schemas de eventos AMQP versionados (header `x-schema-version`)
- Prisma 5 como single source of truth del modelo de datos

**Cloud-agnóstico por diseño:**
- Docker Compose para desarrollo y mesa redonda
- Mismos containers desplegables a EKS / AKS / GKE sin cambios
- Sin lock-in a servicios propietarios (no SQS, no DynamoDB, no Cosmos DB)
- ADR-009 documenta esta decisión

**Observabilidad desde día 1 (Sprint 0):**
- OpenTelemetry collector como parte del stack base
- Trazas distribuidas con `x-trace-id` propagado en HTTP y AMQP
- Grafana + Tempo desde el Sprint 0 — no se "agrega" después

**Notas del expositor (~30 seg):**
"En la práctica esto se traduce en: TypeScript en todas las capas — front, back, scripts y tests; un único lenguaje. Contratos explícitos: OpenAPI auto-generado, schemas de eventos versionados, Prisma como fuente única del modelo. Cloud-agnóstico: docker-compose para la demo, los mismos containers van a Kubernetes sin tocar código. Y observabilidad ya en el Sprint 0: OpenTelemetry, trazas distribuidas, Grafana — no es un agregado tardío, es parte de la plataforma base."

**Visual:** [Diagrama DC-02 Componentes] con etiquetas resaltadas en cada capa: "TypeScript", "OpenAPI", "AMQP versionado", "OTel"

**Rúbrica:** C7

---

## Slide 16 — MIT Design AI — concepto

**Título:** Tendencia 2: MIT Design AI

**Cuerpo:**

**Qué es Design AI en MIT:**
Un enfoque para incorporar IA como **ciudadano de primera clase del diseño** del producto, no como un add-on tecnológico. Pensar el modelo, los datos, los sesgos, la explicabilidad y los casos de fallo desde el inicio.

**Principios clave:**
1. **IA como decisión de diseño, no como feature aislado** — el modelo es parte de la arquitectura, no un servicio externo opaco
2. **Datos primero** — diseñar el pipeline de datos antes de elegir el algoritmo
3. **Explicabilidad obligatoria** — el modelo debe poder explicar su decisión a un humano (drivers, feature importance)
4. **Bias mitigation by design** — pensar el sesgo desde la fase de feature engineering, no como auditoría posterior
5. **Fallback determinístico** — qué pasa cuando el modelo no responde, no entrenó bien, o se degradó
6. **Human-in-the-loop** — para decisiones de impacto, el humano tiene la última palabra
7. **Interfaces conversacionales como UI** — los LLMs cambian cómo el usuario interactúa con sistemas complejos

**Diferencia con "agregar IA":**
Agregar IA = "tenemos un sistema, ¿le ponemos un chatbot?". Design AI = "el sistema necesita predecir riesgo y guiar al alumno; eso son decisiones arquitectónicas que afectan datos, eventos y UI".

**Notas del expositor (~25 seg):**
"MIT Design AI propone tratar la IA como una decisión arquitectónica, no como un agregado. Sus principios incluyen: pensar los datos antes que el algoritmo, exigir explicabilidad — el modelo debe explicar por qué decide lo que decide —, mitigar el bias en feature engineering, tener fallback determinístico cuando el modelo falla, mantener humano-en-el-loop para decisiones de impacto, y considerar las interfaces conversacionales como una UI legítima del sistema."

**Visual:** Diagrama conceptual: IA en el centro, rodeada por datos, ética/bias, explicabilidad, fallback, human-in-the-loop, UX conversacional

**Rúbrica:** C7

---

## Slide 17 — MIT Design AI — aplicación al caso

**Título:** Cómo lo aplicamos en el Sistema de Pañol

**Cuerpo:**

**Componente 1 — `ai-risk-svc`: scoring predictivo de morosidad**
- **Modelo:** Random Forest exportado a ONNX (portable, sin lock-in al runtime de entrenamiento)
- **Features:** historial de atrasos del usuario, días promedio fuera de plazo, item solicitado, día de la semana, temporada académica
- **Output:** `{ score: 0..1, drivers: [{feature, weight}, ...] }` — los drivers son obligatorios (explicabilidad)
- **Aplicación de RC.11:** score ≥ 0.7 acepta automático, 0.4-0.7 requiere PIN del pañolero, < 0.4 bloquea (override admin con auditoría)
- **Fallback determinístico:** si el modelo no responde, devuelve score = 0.5 (decisión humana sin sesgo del modelo)
- **Mitigación de bias (RF.IA.5):** features prohibidas — sexo, carrera, año académico (evita discriminación indirecta)

**Componente 2 — `ai-assistant-svc`: asistente conversacional**
- **Tecnología:** OpenAI con function calling + Model Context Protocol (MCP)
- **Tools MCP expuestas (6):** `search_catalog`, `check_availability`, `create_request`, `get_user_history`, `get_blocked_status`, `get_score_estimate`
- **Guardrails:** RC.15 — usuarios bloqueados reciben respuesta directa de error sin invocar al LLM (ahorro + seguridad)
- **Human-in-the-loop:** el asistente sugiere, nunca ejecuta sin confirmación explícita del alumno

**Notas del expositor (~30 seg):**
"En la práctica son dos componentes. Primero, scoring de riesgo: Random Forest en ONNX, con features explícitas, drivers obligatorios para explicabilidad, umbrales documentados en la regla RC.11, y fallback a 0.5 si el modelo cae. Mitigación de bias: prohibimos features como sexo o carrera. Segundo, asistente conversacional: OpenAI con function calling sobre seis tools MCP que el alumno usa con lenguaje natural. Guardrail: si el usuario está bloqueado, no llamamos al LLM, respondemos directamente."

**Visual:** [Diagrama SEQ-05 Asistente MCP] miniatura + caja con 6 tools listadas + caja con drivers de ejemplo del scoring

**Rúbrica:** C7

---

## Slide 18 — Por qué Design FullStack + Design AI y no las otras

**Título:** Tendencias descartadas: Mathematical Programming y Quantum

**Cuerpo:**

**Mathematical Programming (descartado):**
- **Qué hubiera aportado:** optimización combinatoria — ej. asignar pañoleros a turnos, optimizar reposición de stock
- **Por qué no encaja:** nuestro problema central no es de optimización con función objetivo y restricciones lineales/no-lineales. Es de **coordinación de servicios distribuidos + predicción de eventos individuales**. Math Programming brillaría si tuviéramos 50 pañoleros y 200 turnos a optimizar; tenemos 2 pañoleros y un proceso lineal.
- **Veredicto:** herramienta sobredimensionada para el problema.

**Quantum Solutions (descartado):**
- **Qué hubiera aportado:** speed-up exponencial en problemas tipo búsqueda en grafos (Grover) o muestreo (QAOA) o factorización (Shor)
- **Por qué no encaja:** el tamaño del problema (cientos de items, miles de eventos/mes) está varios órdenes de magnitud por debajo de donde quantum tiene ventaja real. Además, infraestructura cuántica (IBM Quantum, AWS Braket) tiene latencia y costo prohibitivos para un MVP.
- **Veredicto:** prematuro para el caso; sería ciencia ficción decorativa.

**Por qué Design FullStack + Design AI:**
- **Design FullStack** ataca directo nuestra restricción más fuerte: equipo pequeño construyendo un sistema distribuido en 6 semanas. Necesitamos coherencia y observabilidad desde el día 1, no después.
- **Design AI** ataca directo nuestro diferenciador: el sistema decide (scoring) y guía (asistente). Sin estos dos, el sistema sería un CRUD de pañol. Con ellos, es una plataforma con inteligencia.

**Notas del expositor (~30 seg):**
"Las cuatro tendencias del listado son: Math Programming, Design FullStack, Design AI, Quantum. Math Programming sería útil si tuviéramos un problema de optimización combinatoria — no es nuestro caso, tenemos coordinación y predicción individual. Quantum es prematuro: nuestro problema está varios órdenes de magnitud por debajo de donde quantum tiene ventaja, y la infra es prohibitiva. Design FullStack ataca nuestra restricción de equipo y plazo. Design AI ataca nuestro diferenciador: el sistema decide y guía. Por eso esas dos."

**Visual:** Matriz 2×2 — eje X: "encaje con problema", eje Y: "factibilidad MVP". Las 4 tendencias ubicadas; Design FS+AI en cuadrante superior derecho; Math y Quantum en otros cuadrantes con razón anotada.

**Rúbrica:** C5, C7

---

# PARTE 3 — DETALLE DEL SOFTWARE

---

## Slide 19 — Arquitectura: visión general

**Título:** El sistema en una sola imagen

**Cuerpo:**

- **Frontera del sistema** explícita — qué está dentro del alcance MVP y qué no
- **3 actores internos:** Alumno, Pañolero, Administrador
- **3 sistemas externos:**
  - LDAP / SSO UNAB (autenticación corporativa)
  - OpenAI API (asistente conversacional)
  - Servicio de email (notificaciones — diferido post-MVP)
- **Lo que entra al sistema:** solicitudes, validaciones, devoluciones, gestión de catálogo
- **Lo que sale:** notificaciones in-app, tickets PDF, reportes, alertas de gestión

**Notas del expositor (~20 seg):**
"En una sola imagen, el sistema. Tres actores: alumno, pañolero, administrador. Tres sistemas externos con los que dialoga: el SSO de UNAB para autenticación, OpenAI para el asistente, y un servicio de email pospuesto a post-MVP. Lo que entra son solicitudes y validaciones; lo que sale son notificaciones, tickets y reportes."

**Visual:** **[Diagrama DC-01 — Contexto del Sistema]** (fullbleed)

**Rúbrica:** C8

---

## Slide 20 — Topología de microservicios

**Título:** 8 microservicios + 2 frontends + bus de eventos

**Cuerpo:**

**Capa de presentación:**
- `web-portal` (Next.js 14) — UI alumno y administrador
- `totem` (Vite + React) — UI del pañolero en kiosko

**API Gateway (BFF):** `api-gateway` con NestJS — autenticación + ruteo

**Capa de microservicios (NestJS 10 + Prisma 5):**
- `auth-svc` — usuarios, roles, JWT
- `inventory-svc` — catálogo y stock
- `request-svc` — solicitudes y workflow
- `loan-svc` — préstamos y devoluciones
- `notification-svc` — in-app + tickets PDF
- `ai-risk-svc` — scoring (Random Forest + ONNX)
- `ai-assistant-svc` — MCP + OpenAI

**Persistencia:** PostgreSQL 16, schema por servicio (bounded context).

**Mensajería:** RabbitMQ 3.13 con 4 exchanges (`domain.events` topic, `domain.commands` direct, `domain.delayed` x-delayed-message, `domain.dlx` fanout).

**Notas del expositor (~25 seg):**
"La topología tiene tres capas. Presentación: portal web y tótem. Gateway que centraliza autenticación. Ocho microservicios con NestJS, cada uno con su schema en PostgreSQL — bounded context. Y RabbitMQ como bus de eventos con cuatro exchanges: eventos de dominio, comandos punto a punto, mensajes con TTL, y dead letter."

**Visual:** **[Diagrama DC-02 — Componentes]** (fullbleed)

**Rúbrica:** C8

---

## Slide 21 — Flujo crítico: solicitud → materialización

**Título:** Cómo se construye un préstamo (camino feliz)

**Cuerpo:**

**Paso 1 — El alumno arma la solicitud (web):**
- Selecciona items y fechas en el portal
- `request-svc` valida stock con `inventory-svc` (Request-Reply)
- Persiste solicitud en estado `PENDIENTE_VALIDACION`
- Publica evento `request.created` con TTL 15 min
- `notification-svc` avisa al pañolero in-app

**Paso 2 — El pañolero materializa (tótem):**
- Selecciona la solicitud en el tótem
- `loan-svc` consulta scoring a `ai-risk-svc` (RC.11)
- Persiste préstamo, publica `loan.created`
- `inventory-svc` reduce stock; `notification-svc` genera ticket PDF
- El alumno recibe el ticket in-app

**Tiempo total estimado:** < 90 segundos del alumno + < 30 segundos del pañolero.

**Saga coreografiada:** ningún orquestador central; cada servicio reacciona a eventos.

**Notas del expositor (~30 seg):**
"El flujo crítico tiene dos pasos. Primero, el alumno en la web: arma su solicitud, request-svc valida stock contra inventory-svc, persiste en estado pendiente y publica un evento con TTL de 15 minutos. Segundo, el pañolero en el tótem: selecciona la solicitud, loan-svc pide scoring a ai-risk-svc, materializa el préstamo, y publica loan.created. Inventory baja el stock, notification genera el ticket PDF. Todo coreografiado por eventos, sin orquestador central."

**Visual:** **[Diagrama SEQ-02]** y **[Diagrama SEQ-03]** lado a lado, o uno arriba y otro abajo

**Rúbrica:** C8, C9 (preview)

---

## Slide 22 — IA en acción: scoring + asistente conversacional

**Título:** Predicción + diálogo en el mismo flujo

**Cuerpo:**

**Scoring (`ai-risk-svc`) — invocado durante la materialización (CU3 + CU6):**
- Input: `{userId, items, fechas}`
- Modelo: Random Forest exportado a ONNX
- Output con drivers obligatorios — el pañolero ve qué pesó en la decisión
- Decisión según RC.11:
  - score ≥ 0.7 → aceptar automático
  - 0.4 ≤ score < 0.7 → requiere PIN del pañolero (override consciente)
  - score < 0.4 → bloquear; override solo por administrador con auditoría

**Asistente (`ai-assistant-svc`) — flujo paralelo, opcional para el alumno:**
- Alumno conversa en lenguaje natural: *"necesito multímetro y protoboard para mañana"*
- LLM (OpenAI) decide invocar tools vía function calling
- Tools MCP del backend: `search_catalog`, `check_availability`, `create_request`...
- Guardrail RC.15: usuarios bloqueados reciben respuesta sin llamar al LLM

**Notas del expositor (~30 seg):**
"Los dos componentes IA actúan en momentos distintos. El scoring se invoca durante la validación: el modelo devuelve un score con drivers explicables y la regla RC.11 decide si acepta, requiere PIN o bloquea. El asistente actúa cuando el alumno arma la solicitud: convierte lenguaje natural en llamadas estructuradas a tools MCP del backend. Si el alumno está bloqueado, ni siquiera consultamos a OpenAI — guardrail explícito."

**Visual:** **[Diagrama SEQ-05 — Asistente MCP]** (mitad superior) + diagrama simple de scoring con drivers de ejemplo (mitad inferior)

**Rúbrica:** C7, C8

---

## Slide 23 — Enterprise Integration Patterns: catálogo aplicado

**Título:** 10 patrones Hohpe en el sistema, 5 protagonistas

**Cuerpo:**

**Patrones protagonistas (cada uno resuelve un problema concreto):**

| Patrón | Problema que resuelve | Dónde se usa |
|---|---|---|
| **Publish-Subscribe Channel** | Múltiples servicios deben reaccionar a un evento sin acoplarse al productor | `domain.events` — `request.created`, `loan.created`, `loan.closed` |
| **Content-Based Router** | Distintos eventos del mismo tipo deben ir a distintos consumidores según contenido | Routing keys en RabbitMQ — ej. `request.created.high_priority` solo a auth-svc |
| **Message Expiration** | Una reserva no puede quedar pendiente para siempre | TTL 15 min en `domain.delayed` exchange |
| **Dead Letter Channel** | Eventos no procesados a tiempo o que fallan deben tener camino alternativo | `domain.dlx` fanout — dispara compensación |
| **Request-Reply** | loan-svc necesita scoring sin acoplarse síncronamente a ai-risk-svc | Comando + reply queue temporal con `correlation_id` |

**Patrones de soporte:**
- Document Message, Correlation Identifier, Idempotent Receiver, Transactional Outbox, Message Channel

**Documentación detallada:** `docs/architecture/04-eip-catalog.md`

**Notas del expositor (~30 seg):**
"Los Enterprise Integration Patterns no son decoración. Cada uno resuelve un problema concreto. Publish-Subscribe distribuye eventos sin acoplar al productor con todos sus consumidores. Content-Based Router enruta según contenido del mensaje. Message Expiration garantiza que una reserva no queda viva para siempre. Dead Letter Channel da camino alternativo a los que se vencen o fallan. Y Request-Reply nos permite pedir scoring de forma asincrónica con correlation ID. Cinco patrones protagonistas, cinco más de soporte."

**Visual:** **[Diagrama EIP-01 — Topología de mensajería]** (fullbleed) — muestra exchanges, colas, bindings

**Rúbrica:** C6

---

## Slide 24 — EIP en acción: Pub-Sub + Router + Expiration + DLC

**Título:** Cómo los patrones colaboran en un solo flujo

**Cuerpo:**

**Caso ilustrativo: una reserva expira sin validación**

1. `request-svc` publica `request.created` al exchange `domain.delayed` con TTL 15 min — **patrón Message Expiration**
2. Si el pañolero **no valida** en 15 min:
   - El broker mueve el mensaje al `domain.dlx` exchange — **patrón Dead Letter Channel**
   - `request-svc` consume `request.expired` desde `queue.expired`
   - Cancela la solicitud, libera la reserva
3. Publica `request.cancelled` al `domain.events` — **patrón Publish-Subscribe**
4. Routing keys dirigen el evento — **patrón Content-Based Router**:
   - `inventory-svc` (libera stock comprometido)
   - `notification-svc` (avisa al alumno)
   - `audit-log` (compliance)

**Caso paralelo: scoring asincrónico**

- `loan-svc` envía comando con `correlation_id` y `reply_to` — **patrón Request-Reply + Correlation ID**
- `ai-risk-svc` procesa y publica respuesta a la cola temporal
- `loan-svc` filtra la reply por `correlation_id` y continúa

**Notas del expositor (~30 seg):**
"Los patrones no se usan aislados, colaboran. En este flujo de compensación, primero Message Expiration: la reserva tiene TTL de 15 minutos. Si vence, Dead Letter Channel la captura. Request-svc reacciona, cancela y publica un evento de cancelación al Pub-Sub. Y el Content-Based Router lo distribuye a quienes les importa: inventory libera stock, notification avisa al alumno, audit lo registra. En paralelo, scoring usa Request-Reply asincrónico con Correlation ID."

**Visual:** Composición — **[Diagrama EIP-03]** mitad izquierda + **[Diagrama EIP-02]** mitad derecha

**Rúbrica:** C6

---

## Slide 25 — EIP en acción: Outbox + Idempotent Receiver

**Título:** Garantía de consistencia: exactly-once efectivo

**Cuerpo:**

**El problema (que muchos sistemas tienen):**
Si un servicio cambia su BD y luego publica un evento, hay dos transacciones distintas. Si el broker cae después de la BD pero antes de publicar, la BD está actualizada pero el evento se pierde — inconsistencia.

**Solución 1 — Transactional Outbox:**
- En **una sola transacción** se actualiza el agregado y se inserta una fila en `outbox_events`
- Un proceso `outbox-relay` hace polling de `outbox_events WHERE published=false`
- Publica al broker, marca como `published=true`
- **Si la transacción falla, no hay evento — sin posibilidad de inconsistencia**

**Solución 2 — Idempotent Receiver:**
- El broker garantiza "al menos una vez" — un evento puede llegar duplicado
- El consumidor consulta `processed_events` con el `correlation_id` antes de procesar
- Si ya existe, descarta el duplicado
- **"Al menos una vez" + Idempotent Receiver = "exactamente una vez efectivo"**

**Donde se aplica:** todos los servicios que publican eventos (`auth-svc`, `request-svc`, `loan-svc`, `inventory-svc`, `notification-svc`).

**Notas del expositor (~30 seg):**
"Una pregunta clásica de sistemas distribuidos: ¿qué pasa si actualizo la base de datos y luego falla la publicación al broker? Solución: transactional outbox. La misma transacción que cambia el agregado escribe el evento en una tabla outbox. Un relay separado los publica. Si la transacción falla, el evento ni siquiera existe. Del lado del consumer, idempotent receiver: tabla processed_events con correlation ID; si llega duplicado, lo descartamos. Resultado: exactly-once efectivo sobre un broker que solo garantiza at-least-once."

**Visual:** **[Diagrama EIP-05 — Outbox + Idempotent Receiver]** (fullbleed)

**Rúbrica:** C6

---

## Slide 26 — ADRs: las decisiones técnicas que tomamos

**Título:** 9 Architecture Decision Records — el por qué de cada elección

**Cuerpo:**

**Lista de los 9 ADRs (formato MADR breve):**

| ADR | Decisión | Estado |
|---|---|---|
| ADR-001 | Stack tecnológico (TypeScript + NestJS + Postgres + RabbitMQ + Next.js) | Aceptada |
| ADR-002 | PostgreSQL único en lugar de MongoDB | Aceptada |
| ADR-003 | NestJS en lugar de Express puro | Aceptada |
| ADR-004 | 8 microservicios en lugar de monolito modular | Aceptada |
| ADR-005 | RabbitMQ en lugar de Kafka | Aceptada |
| ADR-006 | Saga coreografiada en lugar de orquestada | Aceptada |
| ADR-007 | Notificaciones in-app, email diferido | Aceptada para MVP |
| ADR-008 | API Gateway propio (NestJS BFF) en lugar de Kong | Aceptada para MVP |
| ADR-009 | Diseño cloud-agnóstico, sin lock-in | Aceptada |

**Tres decisiones destacadas (justificadas en detalle):**

**ADR-002 — PostgreSQL en lugar de MongoDB:**
- *Alternativa descartada:* MongoDB del MERN original
- *Razón:* el dominio (préstamos, transacciones, integridad de stock) exige ACID y joins. CQRS para forzar Mongo agrega complejidad innecesaria.

**ADR-005 — RabbitMQ en lugar de Kafka:**
- *Alternativa descartada:* Apache Kafka
- *Razón:* nuestro throughput esperado (decenas de eventos/segundo) está varios órdenes de magnitud bajo donde Kafka brilla. RabbitMQ tiene delayed exchange y DLX nativos, justo lo que necesitamos.

**ADR-006 — Saga coreografiada en lugar de orquestada:**
- *Alternativa descartada:* orquestador Temporal o AWS Step Functions
- *Razón:* 7 CU principales con flujos cortos no justifican infra de orquestador. Documentamos el punto donde Temporal sería preferible si crecemos a 30+ CU.

**Notas del expositor (~30 seg):**
"Tomamos nueve decisiones arquitectónicas, cada una documentada como ADR en formato MADR. Tres destacadas: PostgreSQL en vez de MongoDB porque el dominio exige ACID y joins. RabbitMQ en vez de Kafka porque nuestro throughput está muy por debajo de donde Kafka brilla, y RabbitMQ tiene delayed exchange y DLX nativos. Saga coreografiada en vez de orquestada porque siete casos de uso no justifican un Temporal. Cada decisión tiene contexto, alternativas, decisión y consecuencias documentadas."

**Visual:** Lista de los 9 ADRs como tarjetas + zoom a 3 destacados con su comparativa (PG vs Mongo, RMQ vs Kafka, choreography vs orchestration)

**Rúbrica:** C4, C5

---

# PARTE 4 — VALIDACIÓN Y CIERRE

---

## Slide 27 — Amenazas, mitigaciones e impacto esperado

**Título:** Lo que puede fallar y qué hacemos al respecto

**Cuerpo:**

**Tabla de amenazas, mitigación e impacto residual:**

| Amenaza | Mitigación implementada | Impacto residual |
|---|---|---|
| Modelo IA con bias por entrenamiento sintético | Features prohibidas (sexo, carrera), drivers visibles, override del pañolero (RF.IA.5) | Bajo — auditable |
| Dependencia de OpenAI (latencia, costo, downtime) | Asistente queda no-disponible; flujo principal funciona sin él | Bajo — feature degradable |
| RabbitMQ caído (single point of failure) | Outbox pattern encola; relay reintenta hasta que el broker vuelva | Muy bajo — eventualmente consistente |
| Bajo nivel de adopción del asistente | Tótem físico fuerza el uso del sistema; el asistente solo apalanca, no es obligatorio | Medio — monitoreable con métricas |
| Resistencia del pañolero al cambio | Tótem mantiene el rol del pañolero (validador), no lo reemplaza | Bajo |
| Pérdida de datos por fallo de BD | Backups automáticos diarios + replicación en producción | Muy bajo |

**Impacto positivo esperado (medible):**
- **-80%** tiempo de validación de un préstamo
- **+100%** trazabilidad histórica de morosidad
- **-50%** mermas no detectadas (alertas automáticas)
- **+30%** uso del pañol por reducción de fricción
- Datos para mejora continua del modelo IA tras 1 mes de operación

**Notas del expositor (~30 seg):**
"Las amenazas las trabajamos explícitamente. Bias del modelo: features prohibidas, drivers visibles, override humano. Dependencia OpenAI: el asistente es opcional, el flujo core funciona sin él. RabbitMQ caído: outbox pattern lo absorbe. Resistencia humana: el tótem preserva el rol del pañolero como validador, no lo reemplaza. El impacto positivo esperado: 80% menos tiempo de validación, trazabilidad completa, 50% menos mermas no detectadas, datos para mejorar el modelo tras un mes."

**Visual:** Tabla de 3 columnas (amenaza / mitigación / impacto residual) + KPIs esperados como cards

**Rúbrica:** C4, C8

---

## Slide 28 — Prototipo funcional

**Título:** Demostración en vivo

**Cuerpo:**

**Lo que se demuestra en el video (demo de 2-3 min):**

1. **Login del alumno** en el portal web (JWT)
2. **Asistente conversacional:** *"necesito multímetro y protoboard para mañana"* → asistente sugiere items, alumno confirma
3. **Solicitud creada** en estado `PENDIENTE_VALIDACION` con tracking
4. **Pañolero en el tótem** valida la solicitud
5. **Scoring decide** — pantalla muestra score + drivers + decisión
6. **Préstamo materializado** — ticket PDF generado
7. **Alumno recibe** notificación in-app con QR del ticket
8. **Devolución** — pañolero escanea QR, marca devuelto
9. **Trazabilidad observable** — Grafana muestra la traza distribuida del flujo (Tempo)
10. **Caso de error** — solicitud no validada en TTL → DLX dispara compensación

**Stack del prototipo corriendo en la mesa redonda:**
- `docker-compose up -d` levanta los 8 microservicios + Postgres + RabbitMQ + Otel + Grafana
- Frontend web en `http://localhost:3000`
- Tótem en `http://localhost:3001`
- Grafana en `http://localhost:3002`

**Notas del expositor (~35 seg):**
"El prototipo funcional es ejecutable. La demo de dos minutos cubre todo el ciclo: login del alumno, conversación con el asistente, solicitud creada, validación en el tótem con scoring visible, materialización con ticket PDF, devolución con QR. Y mostramos en Grafana la traza distribuida — un solo trace ID que atraviesa los siete microservicios involucrados. Cerramos con el caso de error: una solicitud no validada en TTL, y el DLX disparando la compensación automática. Todo en docker-compose levantado en la mesa."

**Visual:** [Screenshot combinado del prototipo: web + tótem + Grafana] + foto del setup físico durante la mesa redonda

**Rúbrica:** C9, condición mínima 3

---

## Slide 29 — Conclusiones y próximos pasos

**Título:** Lo que aprendimos y lo que sigue

**Cuerpo:**

**Tres takeaways del proyecto:**

1. **LeSS funciona muy bien para 2 equipos cuando el PO es único y disciplinado** — el riesgo principal no es la metodología, es que los equipos diverjan en interpretación; las ceremonias compartidas (Planning Two-Team, Review única) son el antídoto.

2. **EIP no son teoría, son repuestas concretas a problemas reales** — cada patrón que aplicamos resolvió un dolor específico: Outbox para consistencia, Message Expiration para reservas, Idempotent Receiver para reentregas. Sin ellos, el sistema sería frágil.

3. **MIT Design AI exige drivers explicables y fallback** — no basta con que el modelo prediga bien; tiene que poder explicar por qué predice y qué hacer si no responde. Sin esto, el sistema pierde la confianza del operador (pañolero) y del usuario final (alumno).

**Próximos pasos (post-mesa redonda):**
- Reentrenar `ai-risk-svc` con datos reales tras 1 mes de operación
- Integrar email diferido (ADR-007 reactivado)
- Multi-pañol — replicar a otras escuelas (Civil, Industrial)
- Migrar saga a Temporal cuando crezcamos a > 20 CU (ADR-006 prevé esto)

**Cierre:**
> *El Sistema de Pañol no es solo un CRUD digital. Es una plataforma con inteligencia, observable, evolutiva, construida con metodología y patrones que la industria valida.*

**Gracias por su atención.**

**Notas del expositor (~35 seg):**
"Tres aprendizajes. Uno: LeSS funciona muy bien para dos equipos si el PO es único y disciplinado; las ceremonias compartidas son el antídoto contra la divergencia. Dos: los EIP no son teoría académica, cada patrón que aplicamos resolvió un dolor real — outbox, expiration, idempotent receiver. Tres: Design AI exige drivers explicables y fallback, no basta con que el modelo prediga bien. Próximos pasos: reentrenamiento con datos reales, integración email, replicar a otras escuelas, migrar a Temporal cuando crezcamos. Gracias."

**Visual:** 3 íconos representando los 3 takeaways + roadmap horizontal corto + cierre institucional

**Rúbrica:** C10

---

# Anexo — Referencias para grabar el video

## Tiempos sugeridos por slide (target 12-14 min)

| Slides | Sección | Tiempo |
|---|---|---|
| 1-2 | Apertura | 0:30 |
| 3-7 | Negocio | 2:30 |
| 8-11 | Metodología LeSS | 2:00 |
| 12-13 | Plataforma Jira | 1:00 |
| 14-18 | Tendencias Design FS + AI | 2:30 |
| 19-22 | Arquitectura + IA | 2:00 |
| 23-25 | EIP | 1:30 |
| 26 | ADRs | 0:45 |
| 27 | Amenazas | 0:30 |
| 28 | Prototipo (con demo screen recording) | 1:30 |
| 29 | Cierre | 0:30 |
| **Total** | | **~14:15** |

## Checklist pre-grabación

- [ ] Tener Jira proyecto cargado y accesible para screenshots
- [ ] Tener prototipo corriendo en docker-compose
- [ ] Tener Grafana con traces visibles
- [ ] Exportar los 14 diagramas .drawio a PNG (o SVG) para la PPT
- [ ] Verificar que asistente con OpenAI responde en demo (API key activa)
- [ ] Probar caso de error TTL (puede requerir bajar el TTL a 30 seg para la demo)
- [ ] Cronometrar la presentación al menos 1 vez antes de grabar

## Diagramas requeridos (de `docs/design/diagrams/`)

| Slide | Diagrama |
|---|---|
| 19 | DC-01-contexto.drawio |
| 20, 15 | DC-02-componentes.drawio |
| 21 | SEQ-02 + SEQ-03 |
| 22 | SEQ-05 |
| 23 | EIP-01 |
| 24 | EIP-02 + EIP-03 |
| 25 | EIP-05 |

## Screenshots externos a capturar

| Slide | Captura |
|---|---|
| 12 | Jira — Backlog + tablero del Sprint 1 |
| 13 | Jira — Filtro JQL `labels = "RF:RF.4"` |
| 28 | Prototipo en ejecución (web + tótem + Grafana) |

## Imágenes externas necesarias

- Slide 1: Logo UNAB + ícono pañol
- Slide 3: Foto del pañol o ícono representativo
- Slide 4: Ilustración "antes con papel / después digital"
- Slide 5: Mockup combinado web + tótem + chat
- Slide 28: Foto del setup físico durante la mesa redonda

---

**Fin del contenido. Próximo paso:** generar la `.pptx` con este contenido + los diagramas exportados.
