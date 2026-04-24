# Actores y roles

## Propósito

Describe los actores que interactúan con el Sistema de Pañol, sus responsabilidades y permisos. Todo RF, RS y caso de uso referencia los actores aquí definidos.

## Actores humanos

El Caso 11 define cinco perfiles de usuario. Se conservan sin modificación respecto del enunciado.

### Jefe de Carrera (Súper Administrador)

Máxima autoridad administrativa sobre el pañol de su escuela. Supervisa al pañolero y al coordinador.

**Responsabilidades funcionales:**
- Crear y configurar el pañol de la escuela.
- Crear usuarios de los perfiles Coordinador y Pañolero.
- Modificar o dar de baja usuarios de cualquier perfil.
- Dar de alta/baja recursos del inventario.
- Aprobar solicitudes "Especiales" multi-día.
- Configurar parámetros operativos: TTL de reserva, umbrales de stock, reglas de morosidad.
- Consultar todos los reportes del sistema.

**Restricciones:**
- No puede borrar usuarios físicamente (solo baja lógica).
- No puede borrar recursos del inventario (solo dar de baja).

### Coordinador de Carrera

Persona de confianza del Jefe con responsabilidad operativa sobre la gestión de usuarios y reportes.

**Responsabilidades funcionales:**
- Crear alumnos y docentes manualmente (esta última por extensión del caso, ver AD.10).
- Importar alumnos masivamente desde archivo Excel/CSV.
- Bloquear o desbloquear alumnos morosos con motivo obligatorio.
- Bloquear docentes morosos (facultad exclusiva de este rol y del Jefe).
- Aprobar solicitudes "Especiales" multi-día.
- Crear solicitudes a nombre de Alumnos o Docentes que no pueden generarlas por sí mismos (RF-C.13).
- Consultar los mismos reportes que el Jefe.

**Restricciones:**
- No puede crear ni modificar usuarios de perfiles administrativos (Jefe, Pañolero, Coordinador).
- No puede dar de alta recursos; sí puede modificar su información no crítica.

### Pañolero

Encargado directo del pañol. Atiende en ventanilla y opera el tótem durante su turno.

**Responsabilidades funcionales:**
- Ingresar productos al inventario con imagen, categoría y cantidad.
- Consultar solicitudes activas del día.
- Validar solicitudes web ítem por ítem y marcar disponibilidad real al momento de la validación.
- Registrar el préstamo una vez entregados los recursos al solicitante.
- Registrar la devolución, consignando el estado de cada recurso.
- Dar de baja o anular préstamos que no se hacen efectivos.
- Crear solicitudes en el tótem a nombre de Alumnos o Docentes que lo requieran (RF-C.13; problemas de accesibilidad, desconocimiento del catálogo, no disposición del canal digital).
- Bloquear alumnos morosos (por motivo administrativo o situación de ventanilla).
- Consultar reportes de estado de préstamos.

**Restricciones:**
- No puede bloquear usuarios docentes ni administrativos.
- No puede crear usuarios de ningún perfil.
- Acciones sensibles (validar, prestar, devolver, dar de baja) requieren PIN de reconfirmación.

### Docente

Académico de la Escuela que necesita recursos para impartir clases o laboratorios.

**Responsabilidades funcionales:**
- Crear solicitudes web de recursos.
- Consultar disponibilidad en línea antes de solicitar.
- Interactuar con el asistente conversacional para armar solicitudes.
- Consultar historial personal de solicitudes y préstamos.
- Solicitar préstamos "Especiales" multi-día, sujetos a aprobación.
- Recibir ticket PDF y notificaciones in-app.

**Restricciones:**
- No opera en el tótem.
- No puede consultar información de otros usuarios.

### Alumno

Estudiante matriculado en alguna carrera de la Escuela.

**Responsabilidades funcionales:**
- Idénticas al Docente en cuanto a flujo de solicitud, historial e interacción con el asistente.

**Restricciones:**
- No puede solicitar préstamos "Especiales" multi-día de forma autónoma; requiere que un Docente lo patrocine o que un Coordinador apruebe excepcionalmente.
- Si está marcado como moroso, puede consultar el portal en modo lectura pero no puede crear nuevas solicitudes.

## Actor automático

### Sistema

Agente no humano que ejecuta acciones automáticas desencadenadas por eventos de dominio o por el paso del tiempo.

**Responsabilidades:**
- Emitir alertas automáticas de stock bajo (niveles Normal, Bajo, Crítico).
- Emitir alertas automáticas de morosidad al detectar incumplimiento de regla (`RC.01`).
- Expirar reservas de solicitudes cuyo TTL ha transcurrido sin materialización.
- Aplicar reglas automáticas de bloqueo/desbloqueo de morosos.
- Generar tickets PDF tras la materialización del préstamo y tras el registro de la devolución.
- Calcular scoring de riesgo previo a la creación de una solicitud.
- Registrar toda acción sensible en el log de auditoría.

El Sistema como actor aparece explícitamente en los casos de uso CU6 y CU7 del Caso 11 original.

## Sistemas externos

En el MVP el sistema no se integra con sistemas externos de la universidad. En el diseño se identifican los siguientes candidatos para fases posteriores:

- **Sistema de Identidad de la Universidad** (SSO federado: Entra ID, Keycloak u OIDC equivalente).
- **Sistema Académico (SIS)** para sincronización automática de matrícula en lugar de importación Excel.
- **Sistema de correo institucional** para notificaciones fuera del canal in-app (fuera del MVP).

Estos sistemas externos aparecen marcados con borde punteado en el diagrama de contexto.

## Equipo ejecutor ficticio

Para efectos del caso de estudio, el equipo que desarrolla el sistema se describe como un grupo de Magíster en Ingeniería Informática actuando como si fueran un equipo de ingenieros industriales contratado por la Escuela de Informática UNAB, Sede Viña del Mar. La estructura de equipo sigue el modelo LeSS básico documentado en `docs/standards/methodology/`. Esta ficción narrativa satisface el contexto de la rúbrica: "equipo de ingenieros industriales desarrollando requerimientos de software".
