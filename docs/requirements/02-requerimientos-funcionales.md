# Requerimientos funcionales

## Propósito

Lista consolidada de los requerimientos funcionales del sistema. Se organiza en dos secciones: los **requerimientos originales del Caso 11**, reescritos con mayor precisión pero conservando numeración e intención del enunciado; y los **requerimientos complementarios** derivados de las decisiones del equipo que no figuran en el caso original.

Cada requerimiento lleva:
- **ID**: identificador estable.
- **Etiqueta**: `[ORIGINAL]` si proviene del Caso 11 sin cambios sustantivos, `[MODIFICADO]` si se ajustó por decisión del equipo, con referencia a la modificación.
- **Descripción**: enunciado verificable.
- **Actor principal**.
- **CU asociados**: casos de uso que lo implementan.

---

## Sección A — Requerimientos del Caso 11

### RF.1 — Autenticación y acceso
**[ORIGINAL]** El sistema debe permitir autenticar usuarios mediante identificador (RUT normalizado) y clave, y otorgar o denegar acceso según el perfil asignado. Aplica a todos los perfiles: Jefe de Carrera, Coordinador, Pañolero, Docente y Alumno.
**Actor principal**: Todos los roles humanos.
**CU**: CU1.

### RF.2 — Administración de perfiles administrativos
**[ORIGINAL]** El sistema debe permitir al Jefe de Carrera administrar los perfiles administrativos del pañol — Coordinador y Pañolero — con las operaciones de crear, modificar información y dar de baja lógica. La baja no elimina el registro de la base de datos. Por extensión transitiva con RF.3, el Jefe de Carrera también puede administrar perfiles Docente y Alumno; el caso original se interpreta así (RS del Jefe: "Crear nuevos Usuarios según los perfiles detallados anteriormente").

**Actor principal**: Jefe de Carrera.
**CU**: CU2.

### RF.3 — Administración de alumnos y docentes
**[MODIFICADO]** El sistema debe permitir al Coordinador y al Jefe de Carrera crear, modificar y dar de baja usuarios de los perfiles Docente y Alumno. Debe soportar también la creación masiva de alumnos mediante importación desde archivo Excel o CSV con los campos: RUT, primer apellido, segundo apellido, nombres, carrera, teléfono, correo del alumno.

> *Ajuste respecto al caso original:* el enunciado atribuye al Coordinador solo el ingreso de **Alumnos** ("Ingresar al Sistema a los Usuarios Alumnos"). Por decisión del equipo (ver AD.10 en `06-supuestos-contradicciones-dudas.md`), se extiende al Coordinador también la administración de Docentes para distribuir carga operativa. El Jefe mantiene alcance total.

**Actor principal**: Coordinador, Jefe de Carrera.
**CU**: CU2.

### RF.4 — Administración del inventario
**[ORIGINAL]** El sistema debe permitir al Pañolero (y al Jefe de Carrera) administrar el inventario del pañol: dar de alta recursos, modificar información no crítica, dar de baja recursos (no eliminación física). Cada recurso tiene los atributos: ID, nombre, categoría (Material, Herramienta, Equipo), detalle, cantidad disponible, imagen. La imagen no excede 150x100 píxeles ni 120 KB.
**Actor principal**: Pañolero, Jefe de Carrera.
**CU**: CU3.

### RF.5 — Creación de solicitudes web
**[ORIGINAL]** El sistema debe permitir a Alumnos y Docentes crear y guardar solicitudes de uno o varios recursos del pañol desde el portal web, con la cantidad requerida por cada recurso y la fecha de retiro prevista.
**Actor principal**: Alumno, Docente.
**CU**: CU4.

### RF.6 — Consulta y validación de solicitudes en el tótem
**[ORIGINAL]** El sistema local debe permitir al Pañolero consultar en tiempo real las solicitudes web activas y validarlas como paso previo a la materialización en préstamo.
**Actor principal**: Pañolero.
**CU**: CU4.

### RF.7 — Materialización de solicitud en préstamo
**[ORIGINAL]** El sistema local debe permitir al Pañolero revisar el detalle de una solicitud web, marcar ítem por ítem los recursos disponibles en ventanilla, y materializar el préstamo sobre el subconjunto disponible. Los ítems marcados como no disponibles quedan registrados en la solicitud como "no entregados".

> *Nota:* el enunciado del Caso 11 utiliza los términos "validar" (RF.6) y "editar" (RF.7) de forma ambigua. La resolución está en `06-supuestos-contradicciones-dudas.md` (CN.05): validar = revisar detalle completo; editar = marcar ítem por ítem la disponibilidad real. No se permite al Pañolero modificar los ítems solicitados por el usuario; solo marcar cuáles se entregan efectivamente (préstamo parcial, RF-C.06).

**Actor principal**: Pañolero.
**CU**: CU4.

### RF.8 — Registro de préstamos y devoluciones
**[ORIGINAL]** El sistema debe registrar cada préstamo materializado y cada devolución procesada, con fecha y hora precisas, ID correlativo de préstamo, detalle de recursos entregados y estado de cada recurso al devolver.
**Actor principal**: Pañolero (Sistema emite registros automáticamente).
**CU**: CU5.

### RF.9 — Consulta de préstamos del día
**[ORIGINAL]** El sistema debe permitir al Pañolero y al Coordinador consultar los préstamos gestionados en el día en curso, con filtros por estado: en curso, devuelto, vencido, anulado.
**Actor principal**: Pañolero, Coordinador.
**CU**: CU5.

### RF.9b — Generación de reportes por perfil
**[ORIGINAL]** El sistema debe generar reportes detallados por cada perfil de usuario para apoyar su toma de decisiones. El detalle por perfil se especifica en `03-requerimientos-sistema.md`.

> *Nota:* El enunciado del Caso 11 duplicó el identificador RF.9. Se renumera el segundo como RF.9b para evitar colisión.

**Actor principal**: Todos los roles administrativos (Jefe, Coordinador, Pañolero).
**CU**: CU7.

### RF.10 — Ticket de respaldo de préstamo y devolución
**[MODIFICADO]** El sistema debe generar automáticamente un ticket PDF con el detalle de cada préstamo y de cada devolución, y entregarlo a la cuenta del usuario solicitante como notificación in-app descargable desde su bandeja en el portal.

> *Ajuste respecto al caso original:* el enunciado original menciona tanto "cuenta de usuario" como "correo". Por decisión de diseño (ver ADR-007), todas las notificaciones son in-app en el MVP y el correo queda en roadmap. El ticket sigue siendo PDF con ID correlativo, descargable por el solicitante.

**Actor principal**: Sistema.
**CU**: CU5.

### RF.11 — Alerta de morosos a administradores del pañol
**[MODIFICADO]** El sistema debe emitir automáticamente alertas in-app al Pañolero, Coordinador y Jefe de Carrera cuando un usuario cruza el umbral de morosidad definido en `05-reglas-de-negocio.md` (RC.01).

> *Ajuste respecto al caso original:* el enunciado original menciona "alerta automática de morosos a correo". Por decisión de diseño, la alerta es in-app en el MVP (ADR-007). El canal correo queda en roadmap.

**Actor principal**: Sistema.
**CU**: CU6.

### RF.12 — Alerta de stock bajo
**[ORIGINAL]** El sistema debe emitir automáticamente alertas al Pañolero cuando el stock de un recurso cae a los niveles Bajo o Crítico definidos en `05-reglas-de-negocio.md` (RC.05).
**Actor principal**: Sistema.
**CU**: CU6.

### RF.13 — Reportes de gestión del pañol
**[ORIGINAL]** El sistema debe producir los siguientes reportes, accesibles por Jefe de Carrera y Coordinador: reporte general de stock disponible y no disponible; recursos más y menos solicitados; devoluciones fuera de plazo por recurso y por usuario; recursos con más pérdidas o dados de baja.
**Actor principal**: Jefe de Carrera, Coordinador.
**CU**: CU7.

### RF.14 — Bloqueo automático de morosos
**[ORIGINAL]** El sistema debe bloquear automáticamente a los usuarios que cumplan la regla de morosidad (`RC.01`), impidiéndoles crear nuevas solicitudes hasta que la situación se regularice y el bloqueo se levante manualmente (Coordinador, Jefe) o automáticamente (cuando se venza la ventana de evaluación).
**Actor principal**: Sistema.
**CU**: CU5, CU6.

---

## Sección B — Requerimientos complementarios

Derivados de las decisiones del equipo (arquitectura event-driven, integración de IA, seguridad operativa del tótem, reglas de negocio finas). Identificadores prefijados con `RF-C` para distinguirlos de los originales.

### RF-C.01 — Reserva de stock con TTL
La creación de una solicitud web provoca una reserva temporal del stock solicitado, sin descontarlo aún del inventario. La reserva expira automáticamente si no se materializa en préstamo dentro del TTL configurado (por defecto 4 horas; configurable por el Jefe de Carrera). Al expirar, el stock reservado se libera y la solicitud queda en estado "vencida".
**Actor principal**: Sistema.
**CU**: CU4.

### RF-C.02 — Scoring de riesgo de morosidad
Al crear una solicitud, el sistema consulta de manera sincrónica al servicio de scoring (`ai-risk-svc`) para obtener un puntaje de riesgo de morosidad del solicitante en relación con los recursos requeridos. El score no decide solo; alimenta el workflow de validación junto con el estado de blacklist.
**Actor principal**: Sistema.
**CU**: CU4.

### RF-C.03 — Asistente conversacional de solicitudes
El portal web incluye un asistente conversacional que ayuda al Alumno y al Docente a armar una solicitud a partir de una descripción de la actividad (ej.: "necesito armar una red con tres switches y medir latencia"). El asistente consulta inventario y solicitudes en tiempo real mediante un servidor MCP (Model Context Protocol) y propone un borrador de solicitud que el usuario puede aceptar o modificar antes de enviar.
**Actor principal**: Alumno, Docente.
**CU**: CU4b (nuevo).

### RF-C.04 — Workflow de validación con blacklist
Antes de aceptar la creación de una solicitud, el sistema evalúa: (a) si el usuario está en blacklist activa (bloqueado por Coordinador o Jefe), (b) si el scoring de riesgo supera el umbral configurado. Si (a) es verdadero, la solicitud se rechaza con mensaje. Si solo (b) se cumple, la solicitud se acepta pero se marca como "de riesgo elevado" para revisión del pañolero.
**Actor principal**: Sistema.
**CU**: CU4.

### RF-C.05 — Préstamo Especial multi-día
El sistema permite crear solicitudes de hasta 7 días de duración, marcadas como "Especiales", que requieren aprobación explícita de un Jefe de Carrera o Coordinador antes de pasar a estado "Aprobada" y poder materializarse en préstamo. El período máximo es configurable por la Escuela.
**Actor principal**: Docente (solicita), Alumno (vía patrocinio docente), Jefe/Coordinador (aprueba).
**CU**: CU4c (nuevo).

### RF-C.06 — Préstamo parcial
Si al momento de validar una solicitud en el tótem algunos ítems no están disponibles en ventanilla, el Pañolero puede materializar el préstamo solo sobre los ítems disponibles. Los ítems no disponibles quedan registrados como "no entregados" en la solicitud original.
**Actor principal**: Pañolero.
**CU**: CU4.

### RF-C.07 — Estados de devolución
Al registrar la devolución de cada ítem, el Pañolero clasifica su estado en uno de: `BUENO`, `DAÑADO_MENOR`, `DAÑADO_MAYOR`, `FALTANTE`, con la opción de agregar una observación libre. Los estados `DAÑADO_MAYOR` y `FALTANTE` activan el evento de ajuste de stock (`stock.lost`).
**Actor principal**: Pañolero.
**CU**: CU5.

### RF-C.08 — Estado "En Mantención"
Un recurso puede marcarse temporalmente como "En Mantención" por el Pañolero o Jefe de Carrera, quedando invisible para nuevas solicitudes sin necesidad de darlo de baja.
**Actor principal**: Pañolero, Jefe de Carrera.
**CU**: CU3.

### RF-C.09 — PIN de acciones sensibles en el tótem
Toda acción sensible realizada desde el tótem (validar solicitud, materializar préstamo, registrar devolución, dar de baja recurso, anular préstamo) requiere reingreso de un PIN de cuatro dígitos del Pañolero, incluso si la sesión está abierta.
**Actor principal**: Pañolero.
**CU**: CU4, CU5.

### RF-C.10 — Cambio obligatorio de clave en primer login
Al ingresar por primera vez al sistema con la clave inicial (RUT + sufijo configurable por la Escuela), el usuario es forzado a definir una clave personal antes de acceder a cualquier otra funcionalidad.
**Actor principal**: Todos los usuarios humanos.
**CU**: CU1.

### RF-C.11 — Historial personal
Alumnos y Docentes pueden consultar el historial de sus solicitudes (activas, vencidas, canceladas, aprobadas) y de sus préstamos (en curso, devueltos, con faltantes) de los **últimos 24 meses**. Para consultas más antiguas, el sistema ofrece contacto con el Coordinador. El límite de 24 meses coincide con el ciclo de carrera típico y con la ventana de auditoría.
**Actor principal**: Alumno, Docente.
**CU**: CU4.

### RF-C.12 — Identificación de usuarios sin RUT chileno
El sistema soporta usuarios identificados por RUT, DNI extranjero o pasaporte. El identificador primario en BD es el par `(documento_tipo, documento_valor)` normalizado.
**Actor principal**: Coordinador, Jefe de Carrera.
**CU**: CU2.

### RF-C.13 — Solicitud en nombre de otro usuario
El Pañolero (en el tótem) y el Coordinador (desde el portal) pueden crear una solicitud a nombre de un Alumno o Docente cuando éste se ve imposibilitado de hacerlo por sí mismo por razones de accesibilidad, desconocimiento del catálogo o no disposición del canal digital. La solicitud queda asociada al `documento` del solicitante (no al del operador) y se marca con el flag `creada_por_operador = true` y `operador_id = {usuario_actor}`, para trazabilidad y auditoría. El flujo de validación (RF-C.04), reserva de stock (RF-C.01) y scoring (RF-C.02) se aplican igual que en una solicitud auto-creada.

> *Origen:* Caso 11, Características del producto: "El pañolero podrá generar una solicitud a nombre de un alumno relacionándola al RUT de éste si es que el alumno se ve imposibilitado para realizarla por sí mismo la acción de Solicitud por imponderables como por ejemplo problemas de accesibilidad (Discapacidad o imposibilidad tecnológica, bajo nivel de desconocimiento de los recursos que requiere y debe ser asesorado en la solicitud)."

**Actor principal**: Pañolero, Coordinador (operadores); Alumno, Docente (solicitante final).
**CU**: CU4 (flujo alterno C).

---

## Trazabilidad

La matriz RF ↔ CU ↔ Rol ↔ Servicio consta en `07-trazabilidad.md`.
