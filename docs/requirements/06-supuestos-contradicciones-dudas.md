# Supuestos, contradicciones y dudas

## Propósito

Documento que cubre el bloque "Supuestos, contradicciones y marco de decisión" de la rúbrica (10 pts). Consolida los supuestos declarados, las contradicciones identificadas en el enunciado del Caso 11 (con su resolución explícita) y la lista de dudas pendientes de validación.

---

## Sección A — Supuestos declarados

Cada supuesto se asume cierto a los efectos del proyecto y está acompañado de su justificación. Si se invalida, la decisión asociada debe reabrirse.

| ID | Supuesto | Justificación |
|---|---|---|
| SP.01 | La Escuela beneficiaria es la Escuela de Informática UNAB, Sede Viña del Mar. | El enunciado deja la elección al equipo; se escoge por coherencia disciplinar con el equipo ejecutor (MCI). Nombre canónico en todos los documentos: "Escuela de Informática UNAB, Sede Viña del Mar". |
| SP.02 | Cada escuela opera **un único pañol** con un tótem único. | El enunciado sugiere "un pañol" en singular; se confirma como alcance MVP. Multi-pañol queda en roadmap. |
| SP.03 | El pañol atiende en horario académico: lunes a viernes, 08:00 a 20:00. | Supuesto operativo razonable; se refleja en `RNF-DIS.1`. |
| SP.04 | Los docentes patrocinadores validan préstamos especiales de alumnos con respuesta dentro de 24 horas. | Permite diseñar el flujo de aprobación sin estados intermedios ambiguos. |
| SP.05 | El canal de notificaciones es exclusivamente in-app. | Decisión del equipo (ADR-007); correo en roadmap. |
| SP.06 | Los datos personales (RUT, correo, teléfono) son tratados con medidas mínimas orientadas a Ley 19.628, sin certificación formal. | Proyecto académico; cumplimiento formal excede alcance (`RNF-PRV.1`). |
| SP.07 | El TTL de reserva por defecto es 4 horas. | Balance entre fricción del alumno y rotación de stock. Configurable (`RC.06`). |
| SP.08 | El tótem no tiene periférico de lectura QR ni lector de código de barras en el MVP. | ADR-QR. Roadmap lo contempla. |
| SP.09 | El sistema NO se integra automáticamente con el Sistema Académico (SIS) de la Universidad. | Carga de alumnos es por Excel/CSV importado manualmente por el Coordinador. |
| SP.10 | Un recurso es una tipología con stock agregado; no hay trackeo de instancia física individual. | Simplifica el modelo de datos. Instancias únicas quedan en roadmap. |
| SP.11 | El asistente conversacional usa OpenAI como proveedor de LLM, a través de un cliente que adapta OpenAI function calling a un servidor MCP. | Decisión de stack del equipo. El MCP desacopla el motor LLM del dominio y permitiría reemplazarlo a futuro. |
| SP.12 | La carga de trabajo esperada del MVP no excede 50 usuarios simultáneos y 5.000 alumnos activos en total. | Base de los RNF de performance y escalabilidad. |
| SP.13 | El campo `nombres` del importador Excel/CSV admite uno o varios nombres separados por espacio. | El Caso 11 usa "Nombre 1" (singular) en la plantilla; en la práctica existen personas con más de un nombre. Se trata como una sola columna de texto libre. |

---

## Sección B — Contradicciones y errores del enunciado, con resolución

Se relevaron durante la lectura del Caso 11 y se resuelven explícitamente para que el equipo trabaje sobre una base consistente. Ninguna resolución altera el espíritu del caso.

### CN.01 — Doble numeración de RF.9

**Hallazgo**: el enunciado lista dos requerimientos distintos con el identificador `RF.9`: uno sobre "consultar préstamos gestionados en el día" y otro sobre "generar reportes detallados por perfil".

**Resolución**: se renumera el segundo como `RF.9b`. El sentido de ambos se conserva.

### CN.02 — Salto en numeración del perfil Docente/Alumno

**Hallazgo**: la sección RS del perfil Docente/Alumno pasa de `RS.1` a `RS.3` sin un `RS.2`.

**Resolución**: se corrige la numeración al redactar `03-requerimientos-sistema.md`: RS-DA.1 (crear solicitud), RS-DA.2 (asistente conversacional, nuevo), RS-DA.3 (historial personal).

### CN.03 — "Alta y baja" vs "no se pueden borrar usuarios"

**Hallazgo**: RF.2 habla de "alta, baja o modificación" de usuarios, y RS.2 del Jefe de Carrera dice "No se pueden borrar los Usuarios de la BD".

**Resolución**: "Baja" se interpreta como **borrado lógico** (`status = INACTIVO`), no borrado físico. Los registros históricos permanecen en la base.

### CN.04 — Ticket a "correo" vs "cuenta del sistema"

**Hallazgo**: el enunciado menciona tanto que el ticket se entrega "a la cuenta del usuario" como "a su correo". Además habla de "mensaje de texto al correo".

**Resolución**: por decisión del equipo (ADR-007), el MVP entrega notificaciones y tickets **solo in-app**, en la bandeja persistente del portal web. El ticket PDF sigue siendo descargable desde ahí. El correo queda en roadmap.

### CN.05 — Semántica de "validar" y "editar" solicitud

**Hallazgo**: RF.6 habla de "consultar y validar" mientras que RF.7 habla de "revisar, editar, marcar disponibles y registrar préstamo". La diferencia operativa entre "validar" y "editar" no queda clara.

**Resolución**: se interpreta como un único flujo en dos momentos — validar = revisar detalle; editar = marcar ítem por ítem disponibilidad real en ventanilla. Se implementa en CU5, con soporte para préstamo parcial (RF-C.06).

### CN.06 — Definición de "moroso"

**Hallazgo**: RF.14 menciona una "regla por definir en base a tiempo, tipo y cantidad de recursos".

**Resolución**: el equipo define la regla en `RC.01` con umbrales concretos y configurables.

### CN.07 — Comunicación de clave inicial tras importación Excel

**Hallazgo**: el enunciado indica que "al cargar los usuarios se genera la clave del usuario automáticamente", pero no especifica cómo se comunica al alumno. Sin canal de correo, el problema es real.

**Resolución**: la clave inicial es determinística (`{documento_valor}{sufijo_escuela}`) y el usuario es forzado a cambiarla en el primer login (`RC.13`, `RF-C.10`). El Coordinador puede resetearla desde su panel.

### CN.08 — Solicitud Especial: duración máxima

**Hallazgo**: el enunciado dice que la duración máxima es "administrable o parametrizable" pero no da default.

**Resolución**: default de **7 días** (`RC.02`), configurable por la Escuela.

---

## Sección C — Dudas pendientes de validación

Puntos que convendría confirmar con el docente o el cliente ficticio antes de congelar alcance. Si no hay respuesta a tiempo, se toma el default del equipo indicado.

| ID | Duda | Default asumido | Impacto si se cambia |
|---|---|---|---|
| DQ.01 | ¿El Jefe de Carrera debe poder aprobar préstamos Especiales él mismo, o solo el Coordinador? | Ambos pueden. | Bajo — solo ajuste de permisos RBAC. |
| DQ.02 | ¿Cuántos pañoles por escuela en roadmap inmediato? | 1 escuela = 1 pañol en MVP; N en evolución. | Medio — modelo de datos admite múltiples pañoles desde el inicio. |
| DQ.03 | ¿El ticket PDF debe incluir QR visual para verificación presencial (aunque el tótem no lo lea aún)? | No, texto e ID correlativo. | Bajo — agregar QR al PDF es trivial con librería. |
| DQ.04 | ¿El asistente conversacional debe poder **crear** la solicitud por el usuario, o solo sugerirla? | Solo sugiere; el usuario confirma antes de enviar. | Bajo — es un cambio de flujo en frontend. |
| DQ.05 | ¿Existe un umbral mínimo de puntaje del scoring que auto-rechace la solicitud? | No. Solo marca "revisar". Decisión final del pañolero. | Medio — afecta discurso de responsabilidad ética del AI. |
| DQ.06 | ¿Los préstamos especiales bloquean completamente el stock reservado por los N días, o pueden ser desplazados por solicitudes estándar si se justifica? | Bloquean completamente. | Alto — afecta política de inventario. |
| DQ.07 | Ante falla del servicio AI (scoring o asistente), ¿el sistema permite operar sin ellos? | Sí. Degradación elegante: solicitud se crea sin score; el workflow continúa con blacklist únicamente. | Bajo — ya está previsto en los flujos. |
| DQ.08 | ¿Qué hacer con préstamos activos cuando un usuario es bloqueado? | Se mantienen activos. El bloqueo impide solo solicitudes nuevas. | Bajo. |

---

## Sección D — Contradicciones entre decisiones del equipo y caso original

Son las decisiones nuestras que se apartan del enunciado. Todas llevan justificación explícita y su ADR correspondiente.

| ID | Decisión | Se aparta de | Justificación | ADR |
|---|---|---|---|---|
| AD.01 | PostgreSQL en vez de MongoDB. | Stack MERN original. | Transacciones ACID requeridas para préstamo/devolución; relaciones ricas; reportes SQL. | ADR-002 |
| AD.02 | Microservicios reales en vez de monolito modular. | El caso no lo exige. | Necesario para aplicar EIP reales (requisito de rúbrica) y demostrar SAGA. | ADR-003 |
| AD.03 | Notificaciones in-app en vez de correo. | RF.10 y RF.11 (mencionan correo). | Reduce dependencia externa en MVP; correo en roadmap. | ADR-007 |
| AD.04 | Asistente conversacional con MCP + OpenAI. | No está en el caso. | Tecnología obligatoria del proyecto (MIT Design AI); agrega valor real al flujo del alumno. | ADR-006 |
| AD.05 | Scoring de riesgo como servicio. | No está en el caso. | Integración concreta de IA al dominio; cubre RF.14 con sofisticación mayor. | ADR-006 |
| AD.06 | Reserva con TTL configurable. | No está en el caso. | Resuelve la fricción entre solicitud on-line y materialización en ventanilla sin bloquear inventario. | ADR-010 |
| AD.07 | PIN de 4 dígitos en el tótem. | Mitiga riesgo latente en RS.4. | Permite cumplir el espíritu del caso (sesión del pañolero no caduca) sin sacrificar seguridad. | ADR-011 |
| AD.08 | Escaneo de QR/código de barras en roadmap, no MVP. | El caso no lo pide explícitamente, pero lo sugiere. | Requiere periférico físico; diseño lo contempla. | ADR-012 |
| AD.09 | SSO federado en roadmap, no MVP. | El caso no lo pide. | Dependencia de infraestructura externa de la universidad. | ADR-013 |
| AD.10 | El Coordinador puede administrar usuarios Docentes (además de Alumnos). | El caso original solo le atribuye "Ingresar al Sistema a los Usuarios Alumnos". | Distribución de carga operativa: el Coordinador ya gestiona solicitudes y bloqueos de Docentes; concentrar el alta/baja en el Jefe crea un cuello de botella. El Jefe mantiene alcance total como contrapeso. | ADR-014 |

---

## Sección E — Relación con la rúbrica

Este documento cubre de forma directa el criterio **"Supuestos, contradicciones y marco de decisión"** (10 pts, Nivel 4) de la rúbrica. Las secciones A–D están diseñadas para responder explícitamente al descriptor: "Declara explícitamente supuestos, verdades asumidas, restricciones y contradicciones, conectándolos con las decisiones del diseño".
