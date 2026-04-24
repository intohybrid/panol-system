# Revisión de requerimientos — Informe de hallazgos

## Propósito y metodología

Este informe es la revisión exhaustiva de los ocho archivos de `docs/requirements/` contrastados contra tres fuentes:

1. **Enunciado del Caso 11** (`uploads/Caso11.docx`) — texto original del caso.
2. **Rúbrica de evaluación** (`uploads/VideoRubricaMCI.pdf`) — 10 criterios (100 pts) + 5 condiciones mínimas.
3. **Coherencia cruzada interna** — IDs, referencias, trazabilidad y consistencia con los docs de arquitectura ya escritos (`00-overview`, `01-stack`, `02-topologia`).

Los hallazgos se clasifican por severidad:

- **CRÍTICO** — riesgo de perder puntos en la rúbrica, contradicción seria o bloqueo para la defensa.
- **MAYOR** — inconsistencia material, gap de cobertura, error de fidelidad al caso.
- **MENOR** — pequeñas inconsistencias, typos, descuidos de formato.
- **OBSERVACIÓN** — sugerencia de mejora, no un error.

Cada hallazgo lleva un ID `HG.NN` para referenciarlo al momento de corregir.

---

## Sección 1 — Hallazgos CRÍTICOS

### HG.01 — Gap: préstamo/solicitud a nombre de otro alumno no está capturado

**Dónde**: no existe RF/CU que lo cubra.

**Qué dice el caso** (Características del producto, literal):
> "El pañolero podrá generar una solicitud a nombre de un alumno relacionándola al RUT de éste si es que el alumno se ve imposibilitado para realizarla por sí mismo la acción de Solicitud por imponderables como por ejemplo problemas de accesibilidad (Discapacidad o imposibilidad tecnológica, bajo nivel de desconocimiento de los recursos que requiere y debe ser asesorado en la solicitud)."

**Impacto**: es un requerimiento funcional explícito del enunciado. Si no se captura, la rúbrica puede leerlo como omisión del alcance. Además, el caso indica el Coordinador también podría crearla ("Actores involucrados: CU4 Crear Solicitudes por medio del Sistema Web — Pañolero, Coordinador").

**Propuesta**: agregar `RF-C.13 — Solicitud en nombre de otro usuario` (o `RF.5-alt`), vincularla al CU4 como flujo alterno adicional y mencionarla en trazabilidad. Tocar también la responsabilidad del Pañolero en `01-actores-y-roles.md`.

---

### HG.02 — Contradicción entre actor principal de RF.2 y RS-JC.1 (quién crea qué perfil)

**Dónde**: `02-requerimientos-funcionales.md` RF.2 vs `03-requerimientos-sistema.md` RS-JC.1.

**Qué pasa**:
- RF.2 dice: "permitir al Jefe de Carrera administrar usuarios de los perfiles **Coordinador y Pañolero**".
- RS-JC.1 dice: "Puede crear usuarios de los perfiles Coordinador, Pañolero, Docente y Alumno".
- El caso (RS del Jefe, literal): "Crear nuevos Usuarios según los perfiles detallados anteriormente (No podrá crear perfiles ajenos a estas categorías por medio del administrador)".

**Impacto**: el Jefe sí puede crear todos los perfiles no-Jefe. RF.2 está restringido de más y queda inconsistente con RS-JC.1 y con el caso.

**Propuesta**: ampliar RF.2 a "perfiles administrativos (Coordinador, Pañolero) y, por extensión transitiva con RF.3, también Docente y Alumno", o explicitar que RF.2 se ocupa de perfiles **administrativos** y RF.3 de perfiles **académicos** (Docente/Alumno) — con nota aclaratoria de que el Jefe tiene alcance total sobre ambos.

---

### HG.03 — Contradicción de tamaño de imagen de recurso: 150×100 (caso) vs 150×150 (nuestro)

**Dónde**: múltiples archivos.

| Archivo | Valor | Correcto según caso |
|---|---|---|
| `02-requerimientos-funcionales.md` RF.4 | 150×100 px | ✓ |
| `03-requerimientos-sistema.md` RS-PN.1 | 150×150 px | ✗ |
| `04-casos-de-uso.md` CU3 paso 2 | 150×150 px | ✗ |
| `05-reglas-de-negocio.md` RC.09 | 150×150 px | ✗ |

**Qué dice el caso** (RS Pañolero, literal): "Es sólo una Imagen asociada al producto y no debe exceder los 150x100 pixeles de tamaño."

**Impacto**: inconsistencia interna + posible desviación no declarada del enunciado. Si se decide dejar 150×150 (cuadrada, más intuitiva), debe documentarse como modificación en `06-supuestos-contradicciones-dudas.md` y en RF.4 (tag `[MODIFICADO]`).

**Propuesta**: decidir (recomiendo **respetar 150×100** para fidelidad al caso) y propagar el valor decidido a los cuatro archivos. Alternativa: mantener 150×150 y agregar contradicción CN.09 al archivo de supuestos.

---

## Sección 2 — Hallazgos MAYORES

### HG.04 — Coordinador crea Docentes: decisión no explícita

**Dónde**: `02-requerimientos-funcionales.md` RF.3, `04-casos-de-uso.md` CU2, `01-actores-y-roles.md`.

**Qué pasa**:
- RF.3 dice "permitir al Coordinador (y al Jefe de Carrera) crear, modificar y dar de baja usuarios de los perfiles **Docente y Alumno**".
- CU2 dice "Coordinador (solo para Alumnos y Docentes)".
- El caso (RS Coordinador, literal): "Ingresar al Sistema a los Usuarios **Alumnos** en forma individual". No menciona Docentes en el alcance del Coordinador.

**Impacto**: le damos al Coordinador una capacidad no explícita en el enunciado. Puede ser una extensión razonable, pero no está documentada como decisión del equipo.

**Propuesta**: dos opciones excluyentes:
1. Restringir el alcance del Coordinador solo a Alumnos (como el caso), y dejar la creación de Docentes al Jefe de Carrera.
2. Mantener la extensión actual y agregarla a `06-supuestos-contradicciones-dudas.md` como `AD.10` con justificación (ej.: reparto de carga operativa).

---

### HG.05 — Pañolero: permiso de bloqueo no coincide con el caso

**Dónde**: `03-requerimientos-sistema.md` RS-PN.6 y `05-reglas-de-negocio.md` RC.08.

**Qué pasa**:
- RS-PN.6 dice: "No puede bloquear Docentes, **Coordinadores** ni al Jefe de Carrera".
- El caso (RS Pañolero literal): "No podrá bloquear las cuentas de usuarios de Docentes o de Jefes de Carrera". (No menciona Coordinadores.)
- RC.08 dice: "El Pañolero solo puede bloquear a usuarios Alumnos". Esto implícitamente restringe también a Coordinadores; es una extensión razonable pero no fiel al caso.

**Impacto**: Bajo, pero es una inconsistencia documentable. Es poco realista que un Pañolero bloquee a un Coordinador, así que la extensión es defendible.

**Propuesta**: mantener la restricción actual (no puede bloquear Coord) y agregar nota explícita en RC.08 de que se restringe más allá del caso por lógica operativa.

---

### HG.06 — Ambigüedad sobre qué servicio evalúa la regla de morosidad (RC.01)

**Dónde**: `04-casos-de-uso.md` CU6 y `07-trazabilidad.md` Matriz Regla ↔ Servicio.

**Qué pasa**:
- CU6 Flujo Alerta y bloqueo de moroso paso 2: "`ai-risk-svc` (**o** `auth-svc`, **según diseño**) evalúa la regla de morosidad (RC.01)". Ambigüedad no resuelta.
- `07-trazabilidad.md` Matriz Regla ↔ Servicio: "RC.01 | `ai-risk-svc`, `auth-svc`".
- `05-reglas-de-negocio.md` Notas: "Las reglas que afectan el flujo de autorización (RC.01, RC.10, RC.11, RC.15) se ejecutan en **request-svc** con información consolidada de auth-svc y ai-risk-svc". (Tercer servicio mencionado.)

**Impacto**: la regla determinística de morosidad RC.01 (umbrales fijos sobre atraso y faltantes) es conceptualmente distinta del scoring predictivo RC.11. Mezclarlas en `ai-risk-svc` confunde la frontera. Decisión arquitectural pendiente que debe cerrarse antes de los diagramas de secuencia (#8).

**Propuesta**: dejar la regla determinística RC.01 en `loan-svc` (evento `loan.overdue`) + `auth-svc` (aplica `user.blocked`). Mantener `ai-risk-svc` únicamente para RC.11 (scoring predictivo). Ajustar CU6 y la matriz en `07-trazabilidad.md`.

---

### HG.07 — Inconsistencia interna en `07-trazabilidad.md`: Servicio ↔ RF no cuadra con RF ↔ Servicio

**Dónde**: `07-trazabilidad.md`, dos matrices.

**Qué pasa**:
- Matriz RF ↔ Servicio dice: RF.13 → `inventory-svc, loan-svc`. RF.9b → `loan-svc, inventory-svc`.
- Matriz Servicio ↔ RF (misma sección) dice: `loan-svc` implementa RF.7, RF.8, RF.9, RF-C.05, RF-C.06, RF-C.07. **No lista ni RF.13 ni RF.9b**.

**Impacto**: la trazabilidad tiene dos "direcciones" que no cierran. Revisor de rúbrica podría detectarlo.

**Propuesta**: agregar RF.9b y RF.13 a la fila de `loan-svc` en la Matriz Servicio ↔ RF. Verificar también que las otras filas (request-svc, notification-svc, etc.) reflejen completamente la otra matriz.

---

### HG.08 — Typo en RF-C.02: "sinecrónicamente"

**Dónde**: `02-requerimientos-funcionales.md` RF-C.02.

**Qué pasa**: "consulta **sinecrónicamente** al servicio de scoring" → debería ser "sincrónicamente" (o mejor: "de manera sincrónica").

**Impacto**: puramente de redacción, pero queda visible en un documento formal.

**Propuesta**: reemplazar por "de manera sincrónica".

---

### HG.09 — Gap vs rúbrica criterio 8: falta "amenazas e impacto" como bloque dedicado

**Dónde**: no existe.

**Qué dice la rúbrica** (criterio 8, 10 pts, Nivel 4): "Presenta claramente contexto, problema, propuesta, **amenazas e impacto**, articulándolos entre sí y con el diseño de solución."

**Impacto**: el `00-contexto.md` cubre contexto/problema/propuesta, pero no aborda amenazas (riesgos técnicos, operativos, regulatorios) ni impacto (qué cambia para la Escuela). `06-supuestos-contradicciones-dudas.md` menciona una amenaza aislada (Ley 19.628). Este bloque es directamente evaluable y vale 10 pts.

**Propuesta**: agregar `00-contexto.md` una sección "Amenazas e impacto" **o** crear `08-amenazas-e-impacto.md` con:
- **Amenazas**: dependencia de proveedores LLM, riesgo de pérdida de recursos por fallas operativas, datos personales (Ley 19.628), disponibilidad en horario punta, resistencia al cambio del pañolero.
- **Impacto**: mejora en trazabilidad, reducción de pérdidas, baseline para decisiones del Jefe, experiencia del alumno.

---

## Sección 3 — Hallazgos MENORES

### HG.10 — Dos filas de trazabilidad con guión en lugar de listado

**Dónde**: `07-trazabilidad.md` Matriz RF ↔ CU.

**Qué pasa**: RF.9, RF.9b, RF.13 tienen "—" en columna Reglas. Técnicamente correcto (no aplican reglas específicas), pero queda visualmente inconsistente frente a las otras filas.

**Propuesta**: cambiar "—" por "N/A" o agregar regla si corresponde (por ejemplo, RF.13 podría referenciar RC.05 para niveles de stock en el reporte).

---

### HG.11 — RC.01 no menciona "tipo de recurso" como criterio

**Dónde**: `05-reglas-de-negocio.md` RC.01.

**Qué dice el caso** (RF.14 literal): "alguna regla por definir en base a **tiempo, tipo y cantidad** de recursos".

**Qué tiene RC.01**: umbrales de tiempo (24h, 6h) + cantidad de devoluciones + ítems faltantes. No usa "tipo de recurso" como factor.

**Impacto**: el caso deja la regla abierta ("por definir"). Nuestra definición es razonable, pero omite una dimensión que el caso menciona explícitamente.

**Propuesta**: agregar como nota en RC.01 que el **tipo** (Material / Herramienta / Equipo) afecta el peso del atraso vía scoring (RC.11), no vía RC.01. O bien agregar un cuarto criterio en RC.01 que pondere por tipo (ej.: atraso de 2h en Equipo es equivalente a atraso de 6h en Material).

---

### HG.12 — "Al menos uno" ambiguo en RC.01

**Dónde**: `05-reglas-de-negocio.md` RC.01.

**Qué pasa**: "Tiene al menos **1 devolución** con atraso mayor a 24 horas" — no queda claro si la ventana es el semestre en curso, todos los semestres, o una ventana móvil. El bullet lo dice ("dentro del semestre académico en curso") pero la redacción obliga a leer dos veces.

**Propuesta**: reformular los tres bullets para que cada uno incluya explícitamente la ventana temporal.

---

### HG.13 — "Escuela de Informática UNAB Sede Viña del Mar" escrita con variantes

**Dónde**: múltiples archivos.

**Variantes detectadas**:
- `00-contexto.md`: "Escuela de Informática de la Universidad Andrés Bello, Sede Viña del Mar".
- `06-supuestos-contradicciones-dudas.md` SP.01: "Escuela beneficiaria es Informática UNAB Sede Viña del Mar".
- `01-actores-y-roles.md`: "Escuela de Informática de la UNAB, Sede Viña del Mar".

**Impacto**: cosmético. Conviene un nombre canónico para que todos los documentos lo referencien igual.

**Propuesta**: adoptar "**Escuela de Informática UNAB, Sede Viña del Mar**" como forma canónica y uniformar.

---

### HG.14 — RF.7 "editar la solicitud" vs realidad operativa

**Dónde**: `02-requerimientos-funcionales.md` RF.7.

**Qué dice el caso** (RF.7 literal): "revisar el detalle de la solicitud, **editar la solicitud** para validar los recursos reales en stock, marcar los que sean de préstamo disponible en ese momento y luego registrar la solicitud como préstamo".

**Qué tiene RF.7**: "marcar ítem por ítem los recursos disponibles en ventanilla, y materializar el préstamo sobre el subconjunto disponible". No menciona "editar" explícitamente.

**Impacto**: el caso habla de editar (implica poder cambiar ítems). Nosotros solo permitimos marcar disponibilidad. La contradicción CN.05 en `06-supuestos` lo aclara pero el RF.7 no lo enlaza. Bueno sería enlazarlo.

**Propuesta**: agregar al RF.7 el enlace explícito: "(ver resolución de la contradicción CN.05 en `06-supuestos-contradicciones-dudas.md`)".

---

### HG.15 — Campo "teléfono" inconsistente

**Dónde**: importación Excel.

**Qué pasa**:
- Caso (RS-CC.2): "|Rut | Apellido 1| Apellido 2|Nombre 1|Carrera |Teléfono| Correo Alumno |".
- Nuestro RS-CC.2: "RUT, primer apellido, segundo apellido, nombre, carrera, teléfono, correo".

**Impacto**: el caso dice "Nombre 1" (singular, solo un nombre). Nuestro dice "nombre" (ambiguo, podría ser un solo nombre o más de uno). Mínimo pero afecta el parser del importador.

**Propuesta**: decidir el contrato: un solo campo "nombre" o "nombres" que admita uno o varios separados por espacio. Documentar en RF.3 o en una regla RC complementaria.

---

## Sección 4 — Observaciones (no son errores)

### HG.16 — Profundizar matriz RS ↔ RF por rol

La matriz de `07-trazabilidad.md` sección "Por rol" está resumida ("RS-JC.1 a RS-JC.5 → crear usuarios, dar de baja, admin inventario, reportes, configurar"). Serviría una tabla más granular RS individual → RF individual → CU.

### HG.17 — Glossario de términos

Términos como "solicitud", "préstamo", "reserva", "materialización", "validación" se usan consistentemente pero conviene un glosario corto en un archivo aparte o en `00-contexto.md` para la defensa y para acelerar la lectura del revisor.

### HG.18 — Referencias a ADRs que aún no existen

Varios archivos referencian ADR-001…ADR-013 (especialmente `06-supuestos-contradicciones-dudas.md` Sección D). Esos ADRs aún no están escritos (task #1). Mientras no existan, los links son "a futuro". No es un defecto; es una nota para la fase de arquitectura.

### HG.19 — RF-C.11 Historial personal podría precisar alcance

`RF-C.11` dice: "Alumnos y Docentes pueden consultar el historial completo de sus solicitudes y préstamos". No especifica rango (último semestre, últimos 12 meses, desde siempre). Para consistencia con RC.01 (ventana semestral) conviene acotar.

### HG.20 — Rúbrica criterio 5 "Alternativas descartadas y seleccionadas"

`06-supuestos-contradicciones-dudas.md` sección D lista 9 decisiones con ADR pendiente. La rúbrica pide "mejor solución, mejor alternativa y peor caso" con criterios técnicos, metodológicos y de negocio. Los ADRs (task #1) deberán incluir explícitamente esas tres alternativas por decisión para rascar Nivel 4.

---

## Sección 5 — Mapa rúbrica ↔ cobertura actual

| Criterio rúbrica | Pts | Dónde está en requirements/ | Estado |
|---|---|---|---|
| 1. Contexto del caso y claridad del problema | 10 | `00-contexto.md` | ✓ Cubierto |
| 2. Metodología (LeSS) | 20 | fuera de requirements | Pendiente (task #3 + docs/standards) |
| 3. Uso plataforma (Taiga) | 10 | fuera de requirements | Pendiente (task #3) |
| 4. Supuestos, contradicciones, marco de decisión | 10 | `06-supuestos-contradicciones-dudas.md` | ✓ Cubierto |
| 5. Alternativas, descarte, justificación | 15 | `06` Sección D + ADRs pendientes | Parcial (faltan ADRs) |
| 6. Enterprise Integration Patterns | 10 | fuera de requirements | Pendiente (task #1, #9) |
| 7. Tecnologías seleccionadas (MIT AI + Full Stack) | 10 | RF-C.02, RF-C.03 + stack | ✓ Cubierto transversalmente |
| 8. Contexto, problema, propuesta, amenazas, impacto | 10 | `00-contexto.md` parcial | Parcial (ver HG.09) |
| 9. Prototipo funcional | 10 | fuera de requirements | Pendiente |
| 10. Calidad de video | 5 | fuera de requirements | Pendiente |

**Condiciones mínimas obligatorias**: de las 5, las que tocan requirements son la #2 (alternativas con justificación) y la #5 (tecnologías integradas). La #2 está parcial (HG.09 y ADRs pendientes). La #5 está cubierta.

---

## Sección 6 — Resumen por archivo

| Archivo | Hallazgos | Severidad máxima |
|---|---|---|
| `00-contexto.md` | HG.13, HG.09 (indirecto) | Mayor (por HG.09) |
| `01-actores-y-roles.md` | HG.04 (indirecto), HG.13 | Mayor |
| `02-requerimientos-funcionales.md` | HG.01, HG.02, HG.03, HG.04, HG.08, HG.14 | Crítico |
| `03-requerimientos-sistema.md` | HG.02, HG.03, HG.05, HG.15 | Crítico (por HG.03) |
| `04-casos-de-uso.md` | HG.01, HG.03, HG.04, HG.06 | Crítico |
| `05-reglas-de-negocio.md` | HG.03, HG.06, HG.11, HG.12 | Crítico (por HG.03) |
| `06-supuestos-contradicciones-dudas.md` | HG.04 (requiere AD.10), HG.13 | Mayor |
| `07-trazabilidad.md` | HG.06, HG.07, HG.10, HG.16 | Mayor |

---

## Sección 7 — Priorización sugerida para corrección

**Bloque 1 — Obligatorio antes de pasar a arquitectura** (son los que afectan decisiones técnicas aguas abajo):

1. HG.06 (morosidad: decidir servicio que evalúa RC.01) — impacta diagramas de secuencia y topología.
2. HG.03 (imagen 150×100 vs 150×150) — decisión y propagación.
3. HG.01 (solicitud a nombre de otro) — agregar RF y tocar CU4.
4. HG.02 (RF.2 alcance Jefe) — reescribir RF.2 y RF.3.
5. HG.07 (trazabilidad inconsistente) — arreglar Matriz Servicio ↔ RF.

**Bloque 2 — Recomendado antes del video**:

6. HG.09 (amenazas e impacto) — 10 pts de rúbrica directa.
7. HG.04 (Coord crea Docentes) — decisión + AD.10.
8. HG.05 (Pañolero bloqueo Coord) — nota aclaratoria.
9. HG.08 (typo) — trivial.
10. HG.14 (RF.7 enlace a CN.05) — trivial.
11. HG.10-13, HG.15 — pulido final.

**Bloque 3 — Nice to have**:

12. HG.16 (matriz RS ↔ RF granular) — opcional.
13. HG.17 (glosario) — opcional pero aporta al video.
14. HG.19 (alcance historial) — opcional.
15. HG.20 — se cierra al escribir los ADRs (task #1).

---

## Conclusión

El cuerpo de requerimientos está **estructuralmente sólido y bien conectado con la rúbrica**. Los ocho archivos se leen como un sistema coherente, con trazabilidad y tono uniforme. Los hallazgos críticos no son errores de fondo sino gaps de cobertura (HG.01, HG.09) y contradicciones contra el caso que requieren decisión explícita y documentación (HG.02, HG.03).

Corrigiendo el Bloque 1 (cinco decisiones) el cuerpo queda listo para ingresar al **COMO** (arquitectura + ADRs). Corrigiendo también el Bloque 2 el material cubre directamente los criterios 1, 4, 5, 7 y 8 de la rúbrica.

Tiempo estimado de corrección: Bloque 1 en ~45 min, Bloque 2 en ~30 min, Bloque 3 en ~15 min.
