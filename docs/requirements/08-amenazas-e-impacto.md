# Amenazas e impacto

## Propósito

Este documento articula los riesgos relevantes del Sistema de Pañol y el impacto esperado de su operación. Cubre directamente el criterio **"Contexto, problema, propuesta, amenazas e impacto"** de la rúbrica (10 pts), complementando a `00-contexto.md`, que ya cubre contexto/problema/propuesta, y a `06-supuestos-contradicciones-dudas.md`, que trata los supuestos y las contradicciones internas.

La unidad de análisis es el MVP tal como está alcanzado en `00-contexto.md`. Las amenazas que se activan solo en escenarios de roadmap (multi-sede, SSO federado) se señalan y se excluyen del diseño inicial.

---

## Sección A — Amenazas

### AM.01 — Dependencia del proveedor de LLM

**Descripción**: el asistente conversacional (`ai-assistant-svc`) usa OpenAI como proveedor. Cambios unilaterales de la API, corte de servicio o cambio de política de precios afectan la experiencia del portal.

**Probabilidad / Impacto**: media / alto.

**Mitigación**:
- Cliente MCP (Model Context Protocol) desacopla el dominio del proveedor: el `ai-assistant-svc` habla con OpenAI vía cliente, pero las tools MCP quedan genéricas. Cambiar a otro LLM con soporte de function calling es un swap de cliente.
- Degradación elegante (DQ.07): si la API falla, el asistente devuelve un mensaje sugiriendo armar la solicitud manualmente; el portal sigue operando.
- Presupuesto mensual acotado en el proveedor, con alertas a 70% y 100% del techo.

### AM.02 — Pérdida o robo de recursos por fallas del flujo operativo

**Descripción**: un préstamo materializado en el tótem pero no devuelto, o una devolución con faltantes no trazados, erosiona el inventario y el presupuesto de la Escuela.

**Probabilidad / Impacto**: alta / alto.

**Mitigación**:
- RC.17: estados de préstamo explícitos (`EN_CURSO`, `DEVUELTO`, `DEVUELTO_CON_FALTANTE`), sin zonas grises.
- RC.01: regla determinística de morosidad, aplicación automática del bloqueo.
- RF.13: reporte de pérdidas y devoluciones fuera de plazo por recurso y usuario, visible al Jefe.
- RF-C.09: PIN por acción sensible en el tótem, para evitar que un tercero registre una entrega sin que el Pañolero lo sepa.

### AM.03 — Tratamiento de datos personales (Ley 19.628)

**Descripción**: el sistema maneja RUT, correo y teléfono de alumnos y docentes. La Ley 19.628 (Chile) establece obligaciones de responsable de datos, registro de tratamiento, derechos ARCO y medidas de seguridad proporcionales al nivel de sensibilidad.

**Probabilidad / Impacto**: baja (en un contexto académico) / medio (si se materializara un incidente, afecta la relación con la Escuela).

**Mitigación**:
- RNF-PRV.1: medidas mínimas (almacenamiento justificado, `audit_log`, baja lógica, sin compartir con terceros).
- SP.06: se declara explícitamente que el MVP no alcanza cumplimiento formal; la figura de responsable de datos, política publicada y procedimientos ARCO quedan en roadmap.
- bcrypt con factor ≥ 12 (RNF-SEC.2), HTTPS obligatorio (RNF-SEC.1), rate-limit en login (RNF-SEC.3).

### AM.04 — Indisponibilidad en ventana de horario punta

**Descripción**: si el sistema cae durante las dos primeras semanas de cada semestre (pico de préstamos para laboratorios), la operación del pañol retrocede a papel y lápiz y se pierde trazabilidad del período.

**Probabilidad / Impacto**: media / medio.

**Mitigación**:
- RNF-DIS.1: disponibilidad objetivo 99.5% en horario operativo, con ventanas de mantenimiento fuera de clases.
- RNF-BK.1: respaldos diarios con retención de 30 días.
- Arquitectura stateless y escalable horizontalmente (RNF-ESC.1) para absorber picos.
- Operación degradada documentada: si el broker falla, los frontends muestran aviso y las acciones críticas se postergan (el pañol puede mantener un cuaderno de respaldo como última línea).

### AM.05 — Resistencia al cambio del Pañolero

**Descripción**: el usuario operacional diario es el Pañolero, que hoy opera en papel. Un sistema percibido como lento, complejo o inseguro se abandona y vuelve a la planilla.

**Probabilidad / Impacto**: alta / alto (si se materializa, el proyecto muere aunque funcione técnicamente).

**Mitigación**:
- RNF-PERF.3: materialización de préstamo en < 2 s.
- RS.4 modificado: la sesión del Pañolero no caduca por inactividad durante el turno (reduce fricción); la seguridad se cubre con el PIN de acción sensible.
- UI del tótem diseñada como kiosko fullscreen, con flujo "un recurso a la vez" y feedback inmediato.
- Fase de acompañamiento en la puesta en marcha: uno del equipo presente en el pañol durante la primera semana.

### AM.06 — Falla del tótem físico

**Descripción**: si el equipo del tótem se daña o se desconecta, no hay cómo materializar préstamos.

**Probabilidad / Impacto**: baja / alto (bloqueante).

**Mitigación**:
- El tótem es un dispositivo comodity (PC/tablet). La app se reinstala rápido desde el repo.
- Los datos viven en el backend, no en el tótem: un reemplazo físico recupera el estado tras el login.
- Como procedimiento de respaldo declarado, el Pañolero puede autenticarse transitoriamente desde otro computador conectado a la red del pañol hasta reponer el dispositivo.

### AM.07 — Inyección y entradas maliciosas

**Descripción**: el portal recibe inputs de usuarios que pueden incluir intentos de XSS, SQL injection, abuso del asistente o del importador Excel/CSV.

**Probabilidad / Impacto**: media / alto.

**Mitigación**:
- RNF-SEC.4: RBAC estricto por endpoint.
- RNF-SEC.5: protección CSRF + XSS.
- Prisma ORM como capa parametrizada: SQL injection queda fuera del modelo de riesgo.
- Sanitización del Excel en `auth-svc` antes de persistir: validación de formato, duplicados, tipos.
- El asistente (`ai-assistant-svc`) opera con tools MCP restringidas a lectura de catálogo y sugerencias; no ejecuta acciones destructivas en el dominio.

### AM.08 — Sesgo y degradación del scoring de riesgo

**Descripción**: el modelo de scoring de `ai-risk-svc` se entrena con datos históricos del pañol. Existe riesgo de reproducir sesgos presentes en la operación manual anterior (por carrera, por horario, por profesor) y de degradar su poder predictivo con el tiempo.

**Probabilidad / Impacto**: media / medio.

**Mitigación**:
- RC.11: el scoring no bloquea. Solo marca "revisar"; la decisión final es del Pañolero.
- DQ.05: se deja explícita la decisión de no auto-rechazar con base en el score.
- Baseline v1: reglas heurísticas sin entrenamiento (número de atrasos + número de faltantes ponderados por tipo de recurso). Permite operar sin datos históricos y sin sesgo.
- Reentrenamiento periódico documentado como procedimiento en roadmap.

### AM.09 — Escalada de costos operativos del LLM

**Descripción**: con mayor adopción del asistente, el consumo de tokens de OpenAI crece linealmente con el uso.

**Probabilidad / Impacto**: media / medio.

**Mitigación**:
- Presupuesto mensual con alertas (AM.01).
- Cache agresivo de prompts frecuentes en `ai-assistant-svc`.
- Rate-limit por usuario/día en el asistente (configurable).
- Opción de desactivar el asistente completo sin romper el flujo (es una capa opcional sobre CU4).

### AM.10 — Contradicción con futuros sistemas de la universidad

**Descripción**: si en el futuro la universidad impone su propio SSO u obliga a sincronizar con el SIS, el MVP necesitará adaptaciones.

**Probabilidad / Impacto**: media (roadmap 2–3 años) / bajo.

**Mitigación**:
- `auth-svc` es un microservicio aislado, pensado para ser reemplazado por un adaptador de SSO sin tocar el resto (ADR-013 declara SSO como roadmap).
- La importación Excel es reemplazable por un job de sincronización con el SIS sin cambios en `request-svc` ni `loan-svc`.

---

## Sección B — Impacto esperado

El impacto se mide en dos dimensiones: operacional (qué cambia para la Escuela y sus usuarios) y estratégica (qué capacidades habilita hacia adelante).

### Impacto operacional

**IM.01 — Reducción del tiempo de atención en ventanilla**
Objetivo: atender un préstamo estándar en menos de dos minutos reloj. Con la operación manual actual, el mismo préstamo puede tomar cinco o más minutos, dependiendo de la disponibilidad del pañolero y del registro en papel.

**IM.02 — Trazabilidad completa del ciclo de vida**
Cada recurso tiene un historial auditable: qué solicitud, qué préstamo, qué devolución, qué usuario, qué estado final. Soportado por `audit_log` (RNF-AUD.1) y por los estados explícitos de solicitud, préstamo y recurso (RC.16, RC.17, RC.18).

**IM.03 — Detección automática y temprana de morosidad**
RF.14 + RC.01 reemplazan la decisión ad-hoc del pañolero por una regla determinística, auditable y configurable. Reduce fricción humana y sesgo. Permite al Jefe revisar y ajustar los umbrales en función de la realidad de cada semestre.

**IM.04 — Visibilidad del stock en tiempo real**
Consultas simples que hoy toman minutos ("¿cuántos osciloscopios están prestados?", "¿qué recurso tiene stock crítico?") se resuelven en segundos desde cualquier perfil autorizado.

**IM.05 — Reducción de fricción en la experiencia del alumno**
El alumno consulta disponibilidad on-line y llega al pañol con la solicitud lista. El asistente conversacional apoya a quienes no conocen el catálogo. El historial personal mantiene al alumno informado sin depender del pañolero.

**IM.06 — Base para decisiones del Jefe de Carrera**
Reportes estructurados (RF.13, RS-JC.4) alimentan decisiones de renovación de inventario, asignación de presupuesto, y política de préstamos. Hoy estos reportes son inexistentes.

### Impacto estratégico

**IM.07 — Cumplimiento regulatorio como piso defensivo**
RNF-PRV.1 deja a la Escuela en una posición defendible respecto de Ley 19.628, aunque no certificada. Reduce riesgo reputacional en caso de incidente.

**IM.08 — Base técnica para evolución natural**
La arquitectura event-driven con microservicios permite incorporar QR, SSO, multi-sede y sincronización con SIS como agregados independientes, sin reescritura. Cada uno tiene ADR que documenta el procedimiento.

**IM.09 — Valor pedagógico para la Escuela**
El proyecto mismo es caso de estudio: los estudiantes de Ingeniería Civil Informática pueden ver un diseño event-driven real, con EIP explícitos, IA integrada al dominio y metodología LeSS documentada. El repo queda como material didáctico.

**IM.10 — Reducción de pérdidas de inventario (dimensión económica)**
Si la hipótesis operacional se cumple (mejor trazabilidad → menos pérdidas), el sistema paga su mantención anual. Este número es proyectable: con costos promedio de reposición de recursos electrónicos, una reducción del 10% en pérdidas cubre la operación del stack cloud y las licencias OpenAI del MVP.

---

## Sección C — Síntesis para la defensa

Para el video y la mesa redonda, la tesis articulada es:

**Contexto**: Escuela de Informática UNAB, Sede Viña del Mar, con operación manual del pañol y problemas medibles de visibilidad, morosidad, reportes y experiencia de alumno.

**Problema**: los cuatro problemas documentados en `00-contexto.md` sección "Problema".

**Propuesta**: sistema event-driven con nueve microservicios (ocho transaccionales + `reports-svc` como read-model CQRS), integración explícita de EIP, IA aplicada al dominio (asistente + scoring), y metodología LeSS en Taiga.

**Amenazas** (clasificadas arriba): dependencia LLM, pérdida de recursos, datos personales, disponibilidad, resistencia al cambio, fallas físicas, inyección, sesgo del scoring, costos LLM, futuros sistemas universitarios. Cada una con mitigación anclada en un requerimiento concreto.

**Impacto**: cuantificable (IM.01 a IM.06) y estratégico (IM.07 a IM.10), medible desde la primera semana de operación.

La rúbrica pide que estos cuatro bloques estén articulados entre sí. Este documento cumple esa articulación: cada amenaza apunta a un RF/RNF/RC concreto que la mitiga, y cada impacto apunta a un RF o a un ADR que lo habilita.
