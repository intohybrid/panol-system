# Requerimientos de sistema

## Propósito

Especificaciones no funcionales y restricciones operativas del sistema, organizadas en tres bloques: requerimientos generales del sistema, requerimientos por rol (derivados del Caso 11) y requerimientos no funcionales.

---

## Sección A — Requerimientos generales del sistema

### RS.1 — Alertas automáticas de stock
**[ORIGINAL]** El sistema genera alertas al Pañolero cuando el stock de un recurso cruza los niveles Normal, Bajo o Crítico según los umbrales definidos en `05-reglas-de-negocio.md` (RC.05).

### RS.2 — Ticket de respaldo automático
**[MODIFICADO]** El sistema genera automáticamente un ticket PDF con el detalle de cada préstamo y cada devolución, y lo entrega a la cuenta in-app del usuario solicitante (bandeja en el portal web).

### RS.3 — Saludo personalizado al ingresar
**[ORIGINAL]** El sistema muestra al ingresar el nombre completo y el rol del usuario autenticado. Ejemplo: "Bienvenido Esteban Solís. Usuario Alumno".

### RS.4 — Cierre automático de sesión por inactividad
**[MODIFICADO]** El sistema cierra la sesión automáticamente tras 5 minutos de inactividad para todos los perfiles excepto el Pañolero en el tótem. Para el Pañolero, la sesión permanece abierta durante el turno, pero toda acción sensible requiere reingreso del PIN (RF-C.09).

---

## Sección B — Requerimientos por rol

### Jefe de Carrera

**RS-JC.1 [ORIGINAL]** Puede crear usuarios de los perfiles Coordinador, Pañolero, Docente y Alumno. No puede crear perfiles fuera de este conjunto.

**RS-JC.2 [ORIGINAL]** Puede dar de baja o modificar la información de cualquier usuario. La baja es lógica; los registros permanecen en la base.

**RS-JC.3 [ORIGINAL]** Puede dar de alta, modificar y dar de baja recursos del inventario. La baja es lógica; no se eliminan registros.

**RS-JC.4 [ORIGINAL]** Puede generar los siguientes reportes:
- Reporte general de stock: disponible y no disponible al momento actual.
- Reporte de recursos más y menos solicitados por período.
- Reporte de devoluciones fuera de plazo, agrupado por recurso y por usuario.
- Reporte de recursos con mayor tasa de pérdida o baja.

**RS-JC.5 [COMPLEMENTARIO]** Puede configurar los parámetros operativos de la escuela: TTL de reserva, umbrales de stock, días máximos de préstamo Especial, umbral de scoring, sufijo de clave inicial.

### Coordinador de Carrera

**RS-CC.1 [ORIGINAL]** Puede crear usuarios Alumnos individualmente desde la interfaz de administración.

**RS-CC.2 [ORIGINAL]** Puede importar alumnos masivamente desde un archivo Excel/CSV con los campos: RUT, primer apellido, segundo apellido, nombres, carrera, teléfono, correo. El campo `nombres` admite uno o varios nombres separados por espacio (ver SP.13 en `06-supuestos-contradicciones-dudas.md`). Al importar, la clave inicial se autogenera según RF-C.10.

**RS-CC.3 [ORIGINAL]** Puede bloquear o desbloquear usuarios morosos (Alumnos y Docentes), con campo obligatorio de texto que explica el motivo. La acción queda en el log de auditoría.

**RS-CC.4 [ORIGINAL]** Puede generar los mismos reportes que el Jefe de Carrera (ver RS-JC.4).

### Pañolero

**RS-PN.1 [ORIGINAL]** Puede ingresar productos al sistema de inventario con los campos: ID, nombre, categoría, detalle, cantidad, imagen. La imagen no excede 150x100 píxeles ni 120 KB.

**RS-PN.2 [ORIGINAL]** Puede consultar en el tótem los reportes diarios de solicitudes on-line activas del día.

**RS-PN.3 [ORIGINAL]** Puede validar una solicitud, editar el detalle para marcar ítem por ítem la disponibilidad real, y registrar el préstamo correspondiente.

**RS-PN.4 [ORIGINAL]** Puede dar de baja o anular préstamos asignados a un usuario que no se presenta a retirar los recursos. La acción queda registrada con el ID del pañolero y el motivo.

**RS-PN.5 [ORIGINAL]** Puede consultar los mismos reportes de estado de préstamos que el Coordinador.

**RS-PN.6 [ORIGINAL]** Puede bloquear a Alumnos morosos por motivo administrativo o de ventanilla. No puede bloquear Docentes, Coordinadores ni al Jefe de Carrera.

### Docente y Alumno

**RS-DA.1 [ORIGINAL]** Puede crear solicitudes web con el detalle de los recursos a retirar.

**RS-DA.2 [COMPLEMENTARIO]** Puede interactuar con el asistente conversacional para armar solicitudes asistidas.

**RS-DA.3 [ORIGINAL]** Puede consultar su historial personal de solicitudes y préstamos.

> *Nota:* El enunciado original del Caso 11 contenía un salto de numeración (de RS.1 a RS.3). Se corrige asignando RS-DA.2 al requerimiento del asistente y promoviendo el historial a RS-DA.3.

---

## Sección C — Requerimientos no funcionales

### Seguridad

**RNF-SEC.1** Todo tráfico entre cliente y servidor usa HTTPS. El sistema no acepta conexiones en HTTP plano en ambientes distintos al de desarrollo local.

**RNF-SEC.2** Las claves de usuario se almacenan hasheadas con bcrypt (factor de costo ≥ 12). No existe punto en el sistema donde la clave en texto plano quede persistente.

**RNF-SEC.3** El login está protegido por rate-limit de 5 intentos por minuto por IP y por 10 intentos por hora por identificador de usuario. Superado el umbral se aplica un bloqueo temporal de 15 minutos.

**RNF-SEC.4** El acceso a recursos del sistema se controla mediante RBAC (control de acceso basado en roles). Cada endpoint valida que el rol del JWT incluya el permiso necesario.

**RNF-SEC.5** El sistema protege contra CSRF en los endpoints que modifican estado, y contra XSS en todas las entradas de texto libre.

**RNF-SEC.6** Las acciones sensibles en el tótem (validar solicitud, materializar préstamo, registrar devolución, dar de baja recurso, anular préstamo) requieren PIN de reconfirmación (RF-C.09).

### Privacidad

**RNF-PRV.1** El sistema aplica las siguientes medidas mínimas orientadas al cumplimiento de la Ley 19.628 (Protección de Datos Personales, Chile):
- Datos personales (RUT, correo, teléfono) se almacenan únicamente cuando son necesarios para la operación del sistema.
- Los accesos a datos personales quedan registrados en el log de auditoría (`audit_log`) con usuario, timestamp y acción.
- La baja de usuario es lógica; los datos permanecen por el período mínimo necesario y se marcan como inactivos, no se exponen en interfaces operativas.
- No se comparten datos personales con terceros.

> *Nota:* El cumplimiento formal y completo de la Ley 19.628 requiere trabajo organizacional y legal (figura de responsable de datos, política publicada, procedimientos ARCO formales) que queda fuera del alcance del MVP. Se declara como amenaza y se menciona en el bloque correspondiente del video.

### Disponibilidad

**RNF-DIS.1** El sistema ofrece una disponibilidad objetivo de 99.5% en el horario operativo de la Escuela (lunes a viernes, 08:00 a 20:00 hora local).

**RNF-DIS.2** Fuera del horario operativo el sistema puede entrar en ventanas de mantenimiento planificadas, comunicadas con 48 horas de anticipación.

### Performance

**RNF-PERF.1** El p95 de tiempo de respuesta en consulta de disponibilidad de inventario es inferior a 500 ms bajo carga normal (hasta 50 usuarios simultáneos).

**RNF-PERF.2** El p95 de tiempo de respuesta en creación de solicitud web es inferior a 1 s.

**RNF-PERF.3** La operación de materialización de préstamo en el tótem completa en menos de 2 s (incluye emisión de ticket PDF y publicación de eventos).

### Auditoría

**RNF-AUD.1** Toda acción que modifica estado relevante (creación de usuario, bloqueo/desbloqueo, alta/baja de recurso, materialización de préstamo, devolución, ajuste de stock) se registra en la tabla `audit_log` con: usuario actor, timestamp, acción, entidad afectada, payload antes/después.

### Observabilidad

**RNF-OBS.1** Todos los servicios están instrumentados con OpenTelemetry. Los traces se propagan entre servicios vía header de correlación HTTP y AMQP.

**RNF-OBS.2** Los logs estructurados (JSON) incluyen: trace-id, usuario (si aplica), servicio, nivel, mensaje, contexto de negocio.

### Mantenibilidad

**RNF-MNT.1** El código cumple las convenciones definidas en `docs/standards/`.

**RNF-MNT.2** La cobertura de pruebas por servicio es ≥ 70% en módulos de dominio, con pruebas unitarias y de integración.

**RNF-MNT.3** Cada microservicio puede levantarse, buildearse y testearse en aislamiento vía su propio `Dockerfile` y comandos del monorepo.

### Escalabilidad

**RNF-ESC.1** Los microservicios son stateless y escalan horizontalmente detrás del broker y del API Gateway (competing consumers pattern).

**RNF-ESC.2** El diseño soporta, sin cambios estructurales, crecimiento hasta 5.000 alumnos activos y 10 pañoles simultáneos.

### Respaldo

**RNF-BK.1** La base de datos se respalda diariamente con política de retención de 30 días en el MVP (parametrizable).

---

## Trazabilidad

La matriz RS ↔ RF ↔ CU ↔ Rol consta en `07-trazabilidad.md`.
