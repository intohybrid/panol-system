# Casos de uso

## Propósito

Casos de uso expandidos en plantilla completa (estilo Cockburn / IEEE 830). Cada CU incluye actores, precondiciones, postcondiciones, flujo principal, flujos alternos y excepciones. Son la base para los diagramas de secuencia en `docs/design/diagrams/`.

## Listado

| ID | Nombre | RF asociados |
|---|---|---|
| CU1 | Autenticar usuario | RF.1, RF-C.10 |
| CU2 | Administrar usuarios y perfiles | RF.2, RF.3, RF-C.12 |
| CU3 | Administrar inventario | RF.4, RF-C.08 |
| CU4 | Crear solicitud web (estándar) | RF.5, RF-C.01, RF-C.02, RF-C.04, RF-C.11, RF-C.13 |
| CU4b | Crear solicitud con asistente conversacional | RF-C.03 |
| CU4c | Solicitar y aprobar préstamo Especial multi-día | RF-C.05 |
| CU5 | Materializar préstamo, devolución y anulación | RF.6, RF.7, RF.8, RF-C.06, RF-C.07, RF-C.09 |
| CU6 | Emitir alertas automáticas (stock y morosidad) | RF.11, RF.12, RF.14 |
| CU7 | Generar reportes | RF.9b, RF.13 |

---

## CU1 — Autenticar usuario

**Actor principal**: cualquier usuario humano (Jefe de Carrera, Coordinador, Pañolero, Docente, Alumno).
**Precondiciones**: el usuario existe en la base de datos y no está dado de baja.
**Postcondiciones**: el usuario obtiene un JWT válido y es redirigido a la vista de su rol. Si es el primer login, la aplicación fuerza el cambio de clave antes de continuar.

**Flujo principal**:
1. El usuario ingresa su identificador (RUT normalizado) y su clave en el formulario del portal o del tótem.
2. El sistema valida las credenciales: `auth-svc` busca el usuario, verifica la clave con bcrypt y verifica que no esté dado de baja.
3. El sistema emite un JWT firmado con los claims: `sub`, `role`, `schoolId`, `iat`, `exp`.
4. La UI almacena el JWT y redirige a la vista correspondiente al rol.
5. El sistema muestra un saludo personalizado: "Bienvenido {nombre}. Usuario {rol}" (RS.3).
6. El sistema registra la acción en el log de auditoría.

**Flujo alterno A — Primer login**:
4a. El sistema detecta que la clave es la inicial autogenerada y redirige al formulario de cambio obligatorio de clave.
4b. El usuario ingresa la nueva clave dos veces; el sistema valida complejidad mínima y la persiste hasheada.
4c. El sistema redirige al flujo principal paso 5.

**Excepciones**:
- **E1 — Credenciales inválidas**: el sistema devuelve un error genérico ("usuario o clave incorrectos") sin revelar cuál falló. Incrementa contador de intentos fallidos.
- **E2 — Rate-limit alcanzado**: tras 5 intentos en 1 minuto el sistema bloquea el identificador por 15 minutos.
- **E3 — Usuario dado de baja**: el sistema devuelve error de acceso sin distinguir de E1.
- **E4 — Usuario bloqueado por morosidad**: el sistema autentica pero redirige a una vista de "cuenta bloqueada" con motivo y no permite crear solicitudes.

---

## CU2 — Administrar usuarios y perfiles

**Actor principal**: Jefe de Carrera (para todos los perfiles); Coordinador (solo para Alumnos y Docentes).
**Precondiciones**: el actor está autenticado con rol autorizado.
**Postcondiciones**: el usuario es creado, modificado o dado de baja lógicamente en la base. El cambio se emite como evento de dominio.

**Flujo principal — Creación individual**:
1. El actor accede a la vista de administración de usuarios en el portal.
2. Selecciona "Crear usuario" y el perfil correspondiente.
3. Ingresa los datos: documento (tipo y valor), nombres, apellidos, carrera, teléfono, correo.
4. El sistema valida unicidad del documento y normaliza el formato.
5. El sistema crea el usuario con clave inicial autogenerada ({documento} + sufijo) y flag `requiere_cambio_clave = true`.
6. `auth-svc` emite `user.created`.
7. La UI confirma la creación y entrega (muestra) la clave inicial al actor para comunicarla offline al usuario creado.

**Flujo alterno A — Importación masiva de alumnos** (solo Coordinador/Jefe):
1. El actor accede a "Importar alumnos" y carga el Excel/CSV con los campos requeridos (RS-CC.2).
2. El sistema valida el archivo: encabezados, formato de RUT, duplicados internos.
3. El sistema procesa cada fila: si hay error, la marca y continúa.
4. El sistema genera claves iniciales masivamente y produce un archivo de resultado descargable con: creados, errores con motivo.
5. Los usuarios creados quedan con `requiere_cambio_clave = true`.

**Flujo alterno B — Modificación**:
1. El actor selecciona un usuario existente.
2. Modifica campos no críticos (teléfono, correo, carrera).
3. El sistema persiste y emite `user.updated`.

**Flujo alterno C — Baja lógica**:
1. El actor selecciona un usuario y confirma "Dar de baja".
2. El sistema marca `status = INACTIVO`, mantiene todos los registros históricos y emite `user.deactivated`.
3. El usuario no puede volver a autenticarse.

**Excepciones**:
- **E1 — Documento duplicado**: se rechaza la creación.
- **E2 — Permisos insuficientes**: un Coordinador que intenta crear un Pañolero recibe error 403.

---

## CU3 — Administrar inventario

**Actor principal**: Pañolero (alta y modificación), Jefe de Carrera (alta, modificación y baja).
**Precondiciones**: el actor está autenticado con rol autorizado.
**Postcondiciones**: el recurso queda registrado, modificado, en mantención o dado de baja lógicamente. El cambio se emite como evento.

**Flujo principal — Alta de recurso**:
1. El actor accede a "Inventario" y selecciona "Agregar recurso".
2. Ingresa: nombre, categoría (Material / Herramienta / Equipo), detalle, cantidad inicial, imagen (≤ 150x100 px, ≤ 120 KB).
3. El sistema valida los límites de imagen y el rango de cantidad.
4. El sistema crea el recurso con ID autogenerado y stock igual a la cantidad inicial.
5. `inventory-svc` emite `inventory.resource-created` y `stock.changed`.

**Flujo alterno A — Poner en mantención**:
1. El actor selecciona un recurso.
2. Marca "En Mantención" con motivo.
3. El sistema cambia el estado a `EN_MANTENCION`; el recurso se vuelve invisible para nuevas solicitudes pero no se da de baja.

**Flujo alterno B — Baja lógica** (solo Jefe de Carrera):
1. El actor selecciona un recurso y confirma baja.
2. El sistema marca `status = BAJA`, mantiene registros históricos y emite `inventory.resource-deactivated`.

**Excepciones**:
- **E1 — Imagen excede límites**: se rechaza el alta con mensaje específico.
- **E2 — Intento de baja con préstamos activos**: el sistema advierte y requiere confirmación explícita; los préstamos activos no se afectan.

---

## CU4 — Crear solicitud web (estándar)

**Actor principal**: Alumno o Docente.
**Precondiciones**: el actor está autenticado, no está bloqueado, y existe al menos un recurso disponible.
**Postcondiciones**: la solicitud queda creada con reserva de stock TTL. Se emite `request.created`.

**Flujo principal**:
1. El actor accede al portal y selecciona "Nueva solicitud".
2. Navega el catálogo de recursos disponibles, agregando ítems a la solicitud con su cantidad.
3. Al confirmar, el sistema ejecuta el workflow de validación (RF-C.04):
   - `request-svc` pregunta a `auth-svc` por el estado del usuario (activo, no bloqueado).
   - `request-svc` pregunta a `inventory-svc` por disponibilidad real de cada ítem.
   - `request-svc` pregunta a `ai-risk-svc` por el score de riesgo.
4. Si las tres respuestas son positivas, `request-svc` crea la solicitud en estado `PENDIENTE` y emite `request.created` con TTL de reserva.
5. `inventory-svc` reacciona al evento reservando el stock.
6. El sistema confirma al actor la creación y muestra el detalle con la hora límite de retiro.

**Flujo alterno A — Score elevado sin blacklist**:
3a. `ai-risk-svc` devuelve score por sobre el umbral pero el usuario no está bloqueado.
4a. `request-svc` crea la solicitud con flag `revisar = true`; el pañolero verá la solicitud destacada.
5a. Sigue el flujo normal.

**Flujo alterno B — Modificar antes de enviar**:
2a. Antes de confirmar, el actor puede agregar, quitar o cambiar cantidad de ítems.

**Flujo alterno C — Solicitud en nombre de otro usuario** (RF-C.13):
1c. Un Pañolero desde el tótem o un Coordinador desde el portal selecciona "Crear solicitud para otro usuario" y busca al solicitante por documento (RUT, DNI o pasaporte).
2c. El sistema verifica que el solicitante esté activo y no bloqueado; si está bloqueado, rechaza la operación con el motivo del bloqueo.
3c. El operador arma la solicitud como en el flujo principal, en nombre del solicitante buscado.
4c. Al confirmar, `request-svc` crea la solicitud con `usuario_id = {solicitante}`, `creada_por_operador = true`, `operador_id = {operador}`. El resto del flujo es idéntico.
5c. Se registra entrada en `audit_log` con ambos actores.

**Excepciones**:
- **E1 — Usuario bloqueado**: el sistema rechaza la solicitud y muestra el motivo del bloqueo.
- **E2 — Stock insuficiente**: el sistema informa qué ítems no tienen stock y permite al usuario ajustar la solicitud.
- **E3 — TTL vencido sin materialización** (se activa después, en CU5): la reserva expira y la solicitud pasa a `VENCIDA`.
- **E4 — Operador sin permiso** (flujo C): un rol sin facultad para crear solicitudes de terceros recibe error 403.

---

## CU4b — Crear solicitud con asistente conversacional

**Actor principal**: Alumno o Docente.
**Precondiciones**: el actor está autenticado y no bloqueado.
**Postcondiciones**: se crea una solicitud en estado `PENDIENTE` con el detalle sugerido por el asistente y aceptado por el usuario.

**Flujo principal**:
1. El actor entra al portal y abre el chat del asistente.
2. Describe su actividad en lenguaje natural. Ejemplo: "necesito armar una red con tres switches y medir latencia entre hosts".
3. El asistente (`ai-assistant-svc`, que corre un servidor MCP + cliente OpenAI):
   - Llama a la tool `consultar_inventario` via MCP.
   - Llama a la tool `sugerir_recursos_por_actividad` con la descripción del usuario.
   - Obtiene una lista de recursos propuestos con justificación.
4. El asistente muestra la propuesta al usuario, con cada ítem y su cantidad.
5. El usuario puede aceptar, editar o descartar ítems.
6. Al confirmar, la solicitud se crea como en CU4 a partir del paso 3 del flujo principal.

**Flujo alterno A — Conversación multi-turno**:
3a. El asistente pide aclaraciones (cantidad de hosts, nivel de experiencia) antes de proponer.
3b. El usuario responde y el asistente itera la propuesta.

**Excepciones**:
- **E1 — Ítem sugerido sin stock**: el asistente propone alternativas equivalentes.
- **E2 — Falla de la API del LLM**: el asistente degrada graciosamente y sugiere al usuario armar la solicitud manualmente.

---

## CU4c — Solicitar y aprobar préstamo Especial multi-día

**Actor principal**: Docente (solicita), Jefe de Carrera o Coordinador (aprueba). Alumno puede solicitar solo con patrocinio docente.
**Precondiciones**: el actor está autenticado y no bloqueado.
**Postcondiciones**: la solicitud queda en estado `APROBADA` o `RECHAZADA`.

**Flujo principal**:
1. El actor crea la solicitud siguiendo CU4 pero marca "Préstamo Especial multi-día" e indica la duración (hasta 7 días por defecto).
2. `request-svc` crea la solicitud en estado `PENDIENTE_APROBACION`.
3. `notification-svc` envía notificación in-app al Jefe y Coordinador.
4. El aprobador revisa la solicitud y confirma aprobación o rechazo con motivo.
5. Si aprueba: la solicitud pasa a `APROBADA`, se emite `request.approved`, y el ciclo continúa como en CU4 (reserva de stock con TTL extendido).
6. Si rechaza: la solicitud pasa a `RECHAZADA` y el solicitante recibe notificación.

**Flujo alterno A — Solicitud de Alumno con patrocinio docente**:
1a. El Alumno indica el docente patrocinador al crear la solicitud.
1b. El sistema notifica al docente para que confirme el patrocinio antes de que entre a aprobación administrativa.

**Excepciones**:
- **E1 — Duración excede el máximo configurado**: se rechaza en validación.

---

## CU5 — Materializar préstamo, registrar devolución y anulación

**Actor principal**: Pañolero.
**Precondiciones**: existe una solicitud en estado `PENDIENTE` o `APROBADA` dentro de su ventana de TTL; el solicitante está físicamente presente en ventanilla.
**Postcondiciones**: la solicitud pasa a `PRESTADA`, el stock queda descontado, se emite ticket PDF.

**Flujo principal — Materializar préstamo**:
1. El solicitante llega al pañol con su RUT o ID de solicitud.
2. El Pañolero abre el tótem, busca la solicitud y la visualiza en detalle.
3. El Pañolero marca ítem por ítem cuáles están disponibles en ventanilla.
4. El Pañolero confirma la materialización e ingresa su PIN de 4 dígitos (RF-C.09).
5. `loan-svc` crea el préstamo con ID correlativo y emite `loan.issued`.
6. `inventory-svc` descuenta definitivamente el stock reservado de los ítems entregados y libera la reserva de los no entregados.
7. `notification-svc` genera el ticket PDF con el detalle y lo entrega a la cuenta in-app del solicitante (RS.2).
8. El tótem muestra confirmación y queda listo para la siguiente atención.

**Flujo alterno A — Préstamo parcial**:
3a. Si algunos ítems no están disponibles, el Pañolero marca solo los disponibles.
5a. El préstamo se materializa solo sobre los ítems entregados; los no entregados quedan registrados en la solicitud como `no_entregado`.

**Flujo principal — Registrar devolución**:
1. El solicitante devuelve los recursos al Pañolero.
2. El Pañolero busca el préstamo por RUT o ID de ticket.
3. El Pañolero clasifica el estado de cada ítem: `BUENO`, `DAÑADO_MENOR`, `DAÑADO_MAYOR`, `FALTANTE`, con observación opcional.
4. El Pañolero confirma la devolución e ingresa su PIN.
5. `loan-svc` marca el préstamo como `DEVUELTO` y emite `loan.returned`.
6. `inventory-svc` reabre el stock para los ítems en estado `BUENO` y `DAÑADO_MENOR`.
7. Para los ítems en estado `DAÑADO_MAYOR` o `FALTANTE`, `inventory-svc` emite `stock.lost` y registra ajuste de baja.
8. `notification-svc` genera el ticket de devolución y lo entrega in-app.

**Flujo alterno B — Anulación de préstamo no efectivo**:
1. Vencido el TTL sin que el solicitante llegue, el Pañolero anula la solicitud desde el tótem (o el Sistema la anula automáticamente, ver CU6).
2. Se emite `request.expired` y `inventory-svc` libera la reserva.

**Excepciones**:
- **E1 — PIN incorrecto**: la acción no procede; se registra intento fallido.
- **E2 — Solicitud fuera de ventana TTL**: el tótem advierte al Pañolero y exige decisión: anular o recrear.
- **E3 — Devolución fuera de plazo**: el sistema marca el préstamo con flag `atraso` y lo cuenta para la regla de morosidad.

---

## CU6 — Emitir alertas automáticas

**Actor principal**: Sistema.
**Precondiciones**: suceden eventos que cruzan umbrales definidos.
**Postcondiciones**: se entregan notificaciones in-app a los destinatarios correctos y, si aplica, se bloquean usuarios.

**Flujo — Alerta de stock bajo**:
1. `inventory-svc` detecta que el stock de un recurso cayó a nivel `BAJO` o `CRITICO`.
2. Emite `stock.low` con nivel y recurso.
3. `notification-svc` consume el evento, determina destinatarios (Pañolero, Coordinador, Jefe) y empuja la notificación por WebSocket.

**Flujo — Alerta y bloqueo de moroso**:
1. `loan-svc` emite `loan.overdue` al detectar un préstamo no devuelto dentro del plazo (detección en `loan-svc` porque es el dueño del estado del préstamo).
2. `loan-svc` evalúa la regla determinística de morosidad (RC.01) sobre el historial del usuario y, si se cumple, emite `user.should-block` con motivo.
3. `auth-svc` consume el evento y persiste el bloqueo del usuario, emitiendo `user.blocked`.
4. `notification-svc` notifica al Pañolero, Coordinador y Jefe.
5. Cualquier intento posterior del usuario bloqueado de crear solicitud se rechaza en el workflow de CU4.

> *Nota:* `ai-risk-svc` **no** interviene en la evaluación de RC.01 (regla determinística). Su alcance se limita al scoring predictivo RC.11, que alimenta el flag `revisar` de la solicitud en CU4.

**Flujo — Expiración automática de reserva**:
1. `request-svc` (o el broker vía plugin delayed-message) detecta que el TTL de una reserva venció.
2. Emite `request.expired`.
3. `inventory-svc` libera la reserva.

---

## CU7 — Generar reportes

**Actor principal**: Jefe de Carrera, Coordinador, Pañolero.
**Precondiciones**: el actor está autenticado con rol autorizado.
**Postcondiciones**: se produce el reporte solicitado en pantalla y/o descargable.

**Flujo principal**:
1. El actor accede a la vista de reportes y selecciona el reporte deseado (RS-JC.4).
2. Configura parámetros: rango de fechas, carrera, categoría de recurso, según aplique.
3. El sistema consulta y agrega datos del servicio correspondiente (`inventory-svc` para stock, `loan-svc` para préstamos, etc.).
4. Muestra resultados en tabla con opciones de ordenamiento y filtrado.
5. El actor puede descargar en CSV o PDF.

**Excepciones**:
- **E1 — Rango de fechas demasiado amplio**: el sistema sugiere acotar para no degradar la UI.

---

## Trazabilidad

Matriz completa CU ↔ RF ↔ Rol ↔ Servicio en `07-trazabilidad.md`.
