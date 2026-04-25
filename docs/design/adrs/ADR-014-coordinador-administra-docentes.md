# ADR-014 — Coordinador puede administrar usuarios Docentes

- **Estado**: Aceptada
- **Fecha**: 2026-04-25
- **Decisores**: Equipo Magíster

## Contexto

El Caso 11, en el bloque RS del Coordinador de Carrera, describe literalmente:

> "Ingresar al Sistema a los Usuarios Alumnos (Individual o Masivo) o bajas de éstos..."

El enunciado atribuye al Coordinador únicamente la administración de **Alumnos**. Por simetría con el RS del Jefe de Carrera ("Crear nuevos Usuarios según los perfiles detallados anteriormente"), la gestión de Docentes quedaría exclusivamente en manos del Jefe.

Al modelar los flujos operativos (casos de uso CU2, alertas, bloqueos, aprobación de préstamos Especiales `RF-C.05`, reportes `RF.13`), surge una tensión:

- El Coordinador ya gestiona **el día a día** de la relación con los docentes: recibe sus solicitudes de préstamo Especial, bloquea y desbloquea morosos (RS-CC.3, también aplica a Docentes), ve los reportes que involucran a Docentes.
- Concentrar el alta/baja/modificación de Docentes exclusivamente en el Jefe de Carrera crea un cuello de botella operativo. El Jefe atiende decisiones estratégicas; pedir que cada actualización menor de un Docente (cambio de teléfono, baja por término de contrato) pase por él es fricción innecesaria.

## Decisión

Se **extiende** el alcance operativo del Coordinador: además de Alumnos, puede crear, modificar y dar de baja usuarios **Docentes**. El Jefe de Carrera mantiene alcance total (Coordinador, Pañolero, Docente, Alumno) como contrapeso jerárquico.

Esta extensión queda explicitada en `RF.3` como `[MODIFICADO]` respecto del Caso 11, con referencia a este ADR y a `AD.10` en `06-supuestos-contradicciones-dudas.md`.

El Coordinador **no** puede:
- Crear, modificar o dar de baja otros Coordinadores ni Pañoleros (eso queda para el Jefe).
- Bloquear a Docentes, Coordinadores ni al Jefe (`RC.08` define la matriz de bloqueo; Coordinador solo bloquea Alumnos y Docentes, y esto también es extensión complementaria).

## Alternativas consideradas

### Atenerse literalmente al Caso 11 (solo Alumnos para el Coordinador)

- **Pros**: fidelidad máxima al enunciado.
- **Contras**: cuello de botella operativo identificado. Requiere que todo cambio de un Docente pase por el Jefe, rompiendo el espíritu del rol (el Coordinador es quien ya interactúa con Docentes en préstamos y reportes).

### Unificar los perfiles Coordinador y Jefe

- **Pros**: elimina ambigüedad de alcance.
- **Contras**: rompe la jerarquía explícita del Caso 11. Pierde un control interno (el Jefe como nivel de aprobación superior y auditor).

### Permitir al Coordinador gestionar también Coordinadores y Pañoleros

- **Pros**: autonomía operativa total.
- **Contras**: rompe el contrapeso jerárquico. Elimina un rol ("Jefe que controla a sus delegados") y abre la puerta a que un Coordinador rogue degrade el acceso de sus pares o del Pañolero.

## Decisión justificada

La extensión propuesta es el mínimo ajuste necesario para eliminar el cuello de botella sin descomponer la jerarquía. Mantiene tres niveles de autoridad claros:

- **Jefe**: alcance total, incluyendo perfiles administrativos (Coord y Pañolero).
- **Coordinador**: alcance sobre perfiles de negocio (Alumno y Docente).
- **Pañolero**: alcance sobre recursos del inventario y operación del tótem.

Es coherente con la práctica habitual de jerarquías académicas donde el coordinador de carrera gestiona operativamente a toda la comunidad académica bajo su responsabilidad, reservando las decisiones sobre personal administrativo al jefe.

## Consecuencias

- `RF.3` queda marcado `[MODIFICADO]` con referencia a este ADR.
- RBAC en `auth-svc`: el rol `COORDINADOR` gana permisos `user:docente:create`, `user:docente:update`, `user:docente:deactivate`.
- El rol `COORDINADOR` **no gana** `user:coordinador:*` ni `user:panolero:*`.
- La importación masiva Excel/CSV sigue siendo Alumnos only (Docentes se gestionan de a uno por su baja volumetría).
- Cada acción sobre Docentes queda en `audit_log` con el ID del Coordinador como actor, para trazabilidad (`RNF-AUD.1`).
- Defensa en mesa redonda: "desviación consciente del enunciado, documentada en ADR-014 y `06-supuestos-contradicciones-dudas.md`. Resuelve un cuello operativo sin romper la jerarquía del Caso 11".
