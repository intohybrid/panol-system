# ADR-011 — PIN de 4 dígitos en tótem con sesión persistente

- **Estado**: Aceptada
- **Fecha**: 2026-04-25
- **Decisores**: Equipo Magíster

## Contexto

`RS.4` establece que el sistema cierra la sesión automáticamente tras 5 minutos de inactividad **para todos los perfiles**. Aplicar esa regla al Pañolero en el tótem crea un problema operativo real: el Pañolero atiende en ventanilla durante horas, intercala períodos de inactividad breves (esperar a un alumno), y un cierre cada 5 minutos obligaría a reloguear con usuario y clave decenas de veces por turno, interrumpiendo la atención.

Por el otro lado, dejar la sesión del tótem abierta todo el turno sin ninguna barrera crea un riesgo de seguridad obvio: cualquiera que se acerque al tótem mientras el Pañolero atiende a otro alumno puede ejecutar acciones sensibles (validar una solicitud, dar de baja un recurso).

Hay que resolver la tensión entre UX de ventanilla y seguridad de acciones críticas.

## Decisión

Dos capas de autenticación para el Pañolero en el tótem:

1. **Sesión de turno**: el Pañolero se loguea al inicio del turno con usuario y clave. La sesión permanece abierta durante todo el turno sin cierre por inactividad. Esto es una excepción explícita a `RS.4` (`RC.14`).
2. **PIN de 4 dígitos para acciones sensibles**: toda acción que modifique estado crítico requiere reingreso del PIN, incluso con la sesión abierta (`RF-C.09`). Acciones que requieren PIN:
   - Validar una solicitud.
   - Materializar un préstamo.
   - Registrar una devolución.
   - Anular un préstamo.
   - Dar de baja un recurso.

El PIN se define en el primer login del Pañolero y se guarda hasheado (bcrypt, factor ≥ 12) en `auth-svc`. Tiene bloqueo temporal tras 3 intentos fallidos.

Esta decisión aplica exclusivamente al tótem. Los demás perfiles (Portal web de Alumno, Docente, Coordinador, Jefe) siguen la regla `RS.4` estándar de 5 minutos de inactividad.

## Alternativas consideradas

### Solo sesión de turno (sin PIN)

- **Pros**: máxima comodidad operativa.
- **Contras**: riesgo de suplantación evidente. Cualquiera puede validar solicitudes o materializar préstamos aprovechando la ausencia del Pañolero. Incompatible con una mínima auditoría.

### Sesión con timeout corto tradicional (regla `RS.4` sin excepción)

- **Pros**: consistencia absoluta con la regla general.
- **Contras**: fricción operativa inaceptable. Reloguear cada 5 minutos de inactividad con usuario + clave completa rompe el flujo de atención y empuja a soluciones malas (contraseñas débiles, contraseñas compartidas, notas pegadas en el tótem).

### Tarjeta física / token hardware

- **Pros**: seguridad alta.
- **Contras**: requiere periféricos (lector NFC/USB), agrega costo operativo, es sobreingeniería para el MVP. Aplicable en roadmap si se justifica.

### Biometría (huella, cara)

- **Pros**: comodidad y seguridad.
- **Contras**: dependencia de hardware del tótem, implicaciones regulatorias (Ley 19.628, datos biométricos), complejidad fuera de scope.

## Decisión justificada

El PIN corto con reconfirmación por acción sensible es el patrón que usan sistemas operativos de cajero en retail, sistemas de autoatención médica y muchos POS: resuelve el 90% del riesgo con una fricción mínima en el flujo principal (las acciones sensibles son una minoría del tiempo de atención).

Mantiene el cumplimiento de `RS.4` como regla general, documentando la excepción del Pañolero como decisión explícita (`RC.14`) y no como descuido.

## Consecuencias

- `auth-svc` expone dos flujos de autenticación para el Pañolero: `login` (devuelve JWT de sesión) y `verifyPin` (devuelve un token corto de 60 s para autorizar la acción sensible).
- Cada endpoint del tótem que ejecuta acción sensible pide el token de PIN como header adicional y lo valida en el API Gateway.
- UX: el PIN se pide en un modal ligero, no en pantalla completa; la acción se ejecuta inmediatamente tras la validación.
- Si el PIN se olvida, el Coordinador lo resetea (genera PIN temporal que el Pañolero debe cambiar al usarlo).
- Auditoría: cada acción sensible queda registrada con el ID del Pañolero, timestamp y `pinVerifiedAt` en `audit_log` (`RNF-AUD.1`).
- Defensa en mesa redonda: "balance entre UX de ventanilla y control de acciones críticas. Es la solución que equivale al patrón sudo en Linux o a la reautenticación en admin panels bancarios".
