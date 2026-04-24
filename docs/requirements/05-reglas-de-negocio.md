# Reglas de negocio

## Propósito

Este documento recoge las reglas de negocio del sistema. Algunas se derivan directamente del Caso 11 (explícitas o implícitas en la prosa), otras son decisiones del equipo documentadas aquí para tener un único punto de verdad. Toda regla lleva ID estable (`RC.NN`) y puede ser referenciada desde RF, RS y casos de uso.

## Clasificación

- **RC.01 a RC.09**: reglas derivadas del Caso 11.
- **RC.10 en adelante**: reglas complementarias del equipo.

---

## RC.01 — Regla de morosidad

Un usuario se considera **moroso** si cumple al menos una de las siguientes condiciones, evaluadas sobre el historial del **semestre académico en curso**:

- Durante el semestre en curso, tiene al menos **1 devolución** con atraso mayor a **24 horas** respecto del plazo pactado.
- Durante el semestre en curso, tiene al menos **2 devoluciones** con atraso mayor a **6 horas** cada una.
- Durante el semestre en curso, tiene al menos **1 ítem** reportado como `FALTANTE` en una devolución cerrada.

El bloqueo es automático y persiste hasta que:
- El Coordinador o Jefe de Carrera lo levanten manualmente, **o**
- Se cumpla un período de cooling-off configurable (por defecto 30 días desde el último incidente).

Los tres umbrales (24h, 6h, semestre) son parámetros configurables por la Escuela a través del perfil de Jefe de Carrera (RS-JC.5).

> *Nota sobre "tipo de recurso":* el Caso 11 indica que la regla puede depender de "tiempo, tipo y cantidad de recursos". En este diseño, **tiempo** y **cantidad** se modelan en los tres umbrales determinísticos de RC.01. El **tipo** (Material / Herramienta / Equipo) se incorpora como factor de ponderación en el scoring predictivo RC.11 (`ai-risk-svc`), que marca la solicitud como "revisar" sin bloquear automáticamente. Esta división separa la regla fija y auditable (RC.01) de la señal heurística (RC.11).

## RC.02 — Duración de préstamos

- **Préstamo estándar**: se presta y devuelve el mismo día, antes del cierre del pañol.
- **Préstamo Especial multi-día**: hasta **7 días** calendario por defecto; el máximo es configurable por la Escuela. Requiere aprobación explícita de Jefe o Coordinador.

## RC.03 — Tipos de recurso

Todo recurso del inventario se clasifica obligatoriamente en una de tres categorías:

- **Material**: consumibles o semiconsumibles (cables, conectores, components descartables).
- **Herramienta**: reutilizables no-electrónicos (pinzas, destornilladores, pelacables).
- **Equipo**: reutilizables electrónicos o de alto valor (switches, routers, osciloscopios, Raspberry Pi).

La categoría determina defaults de umbral de stock, duración de préstamo sugerida y reglas de autorización para solicitudes especiales.

## RC.04 — Identificación de usuario

El identificador primario de un usuario es el par `(documento_tipo, documento_valor)` normalizado, donde:

- `documento_tipo ∈ {RUT, DNI, PASAPORTE}`
- `documento_valor` se normaliza sin puntos y con guión (si aplica).

Usuarios sin RUT chileno (alumnos extranjeros) se registran con `DNI` o `PASAPORTE`.

## RC.05 — Niveles de stock

Los umbrales de alerta por recurso se calculan sobre el **máximo histórico** del stock y son configurables:

- **NORMAL**: stock actual > 30% del máximo.
- **BAJO**: stock actual entre 10% y 30% del máximo (alerta informativa).
- **CRÍTICO**: stock actual < 10% del máximo (alerta prioritaria, requiere acción).

El máximo histórico se recalcula cada vez que un alta de stock lo supera.

## RC.06 — TTL de reserva

Al crear una solicitud, se reserva stock por un TTL configurable:

- **Solicitud estándar**: 4 horas por defecto, hasta 12 horas máximo.
- **Solicitud Especial**: TTL igual al plazo de retiro acordado en la aprobación.

Si el TTL expira sin materialización, la reserva se libera automáticamente.

## RC.07 — Ticket correlativo

El ID de préstamo es un correlativo autoincremental por pañol, con prefijo de año calendario:

`PRE-{AAAA}-{NNNNNN}` — por ejemplo `PRE-2026-000042`.

El ID de devolución es el mismo ID de préstamo con sufijo `-DEV`.

## RC.08 — Restricción de bloqueo por rol

- El **Pañolero** solo puede bloquear a usuarios Alumnos.
- El **Coordinador** puede bloquear Alumnos y Docentes.
- El **Jefe de Carrera** puede bloquear Alumnos, Docentes, Coordinadores y Pañoleros.
- **Ningún rol** puede bloquear al Jefe de Carrera desde la aplicación.

> *Nota:* el Caso 11 literalmente indica que el Pañolero "no podrá bloquear las cuentas de usuarios de Docentes o de Jefes de Carrera". La extensión de este diseño, que agrega la restricción también para Coordinadores, se justifica por jerarquía operativa (el Coordinador supervisa al Pañolero en la estructura de RS del caso). Se documenta como endurecimiento razonable, no como desviación de alcance.

## RC.09 — Imagen de recurso

La imagen asociada a un recurso tiene las siguientes restricciones:

- Tamaño máximo: 150x100 píxeles (ancho × alto), según el Caso 11 literal.
- Peso máximo: 120 KB.
- Formatos aceptados: PNG, JPG, WebP.
- Solo una imagen por recurso.

## RC.10 — Blacklist manual

Un usuario puede ser bloqueado manualmente por Coordinador o Jefe de Carrera incluso sin cumplir RC.01, con motivo obligatorio registrado en `audit_log`. Al levantar el bloqueo manual queda también registrado quién lo hizo y cuándo.

## RC.11 — Scoring y umbral

El scoring de riesgo devuelve un valor entre 0 y 1. El umbral de "riesgo elevado" está configurado por defecto en **0.7** y es ajustable por el Jefe de Carrera. Un score sobre el umbral no bloquea la solicitud; solo la marca para revisión reforzada del Pañolero.

## RC.12 — Concurrencia sobre stock

La reserva de stock usa **lock optimista con campo `version`**. Si dos solicitudes simultáneas compiten por el último ejemplar, una tiene éxito (incrementa versión) y la otra recibe error de concurrencia, debiendo reintentarse con stock recalculado.

## RC.13 — Cambio obligatorio de clave

La clave inicial de un usuario recién creado es `{documento_valor}{sufijo_escuela}`, donde el sufijo es configurable. En el primer login, el usuario es forzado a cambiarla antes de acceder a cualquier funcionalidad (ver RF-C.10).

## RC.14 — Sesión del pañolero

La sesión del Pañolero en el tótem no caduca por inactividad (se exceptúa de RS.4). Para mitigar el riesgo de acceso no autorizado, toda acción sensible (validar, materializar, devolver, anular, dar de baja) requiere reingreso del PIN de 4 dígitos del Pañolero (RF-C.09).

## RC.15 — Moroso bloqueado: alcance de permisos

Un usuario bloqueado por morosidad:

- **Puede** autenticarse y ver su perfil, su historial y el catálogo (modo lectura).
- **No puede** crear nuevas solicitudes ni modificar solicitudes pendientes.
- **No puede** interactuar con el asistente conversacional para crear una solicitud (el asistente muestra el mensaje de bloqueo).

## RC.16 — Estados de solicitud

Una solicitud transita los siguientes estados, en este orden:

- `PENDIENTE` (creada, con reserva TTL, esperando materialización)
- `PENDIENTE_APROBACION` (solo para Préstamo Especial multi-día)
- `APROBADA` (solo para Especial, post-aprobación)
- `RECHAZADA` (Especial rechazada por administrador)
- `PRESTADA` (materializada en el tótem)
- `DEVUELTA` (cerrada)
- `VENCIDA` (TTL expirado sin materialización)
- `CANCELADA` (cancelada por el solicitante antes de materializar)

Los estados terminales son `DEVUELTA`, `VENCIDA`, `RECHAZADA`, `CANCELADA`. No hay transiciones desde ellos.

## RC.17 — Estados de préstamo

Un préstamo transita los siguientes estados:

- `EN_CURSO` (recursos entregados, no devueltos aún)
- `DEVUELTO` (cerrado correctamente)
- `DEVUELTO_CON_FALTANTE` (cerrado con al menos un ítem en estado `FALTANTE` o `DAÑADO_MAYOR`)
- `ANULADO` (anulado por Pañolero antes de materializarse realmente)

## RC.18 — Estados de recurso

Un recurso del inventario puede estar en uno de estos estados:

- `ACTIVO` (disponible o potencialmente prestable)
- `EN_MANTENCION` (temporalmente no asignable)
- `BAJA` (fuera del inventario permanentemente, pero registro histórico conservado)

---

## Notas de interpretación y coherencia

- Toda regla con valores por defecto (`RC.01`, `RC.02`, `RC.05`, `RC.06`, `RC.11`, `RC.13`) es configurable a nivel de Escuela. El mecanismo de configuración es el mismo: `RS-JC.5`.
- La regla determinística de morosidad (`RC.01`) se **detecta** en `loan-svc` (dueño del estado del préstamo y de los atrasos), que emite `user.should-block`. `auth-svc` **persiste** el bloqueo y emite `user.blocked`.
- El scoring predictivo (`RC.11`) vive en `ai-risk-svc`. Es consultado de manera sincrónica desde `request-svc` al crear la solicitud; no bloquea, solo marca `revisar = true`.
- Las reglas de autorización en tiempo de solicitud (`RC.10`, `RC.15`) se aplican en `request-svc` con información consolidada de `auth-svc` (estado del usuario) y `ai-risk-svc` (score).
- Las reglas transaccionales (`RC.06`, `RC.12`, `RC.16`, `RC.17`) se aplican en `loan-svc` y `inventory-svc` con apoyo del broker.
