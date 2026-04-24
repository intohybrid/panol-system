# Contexto del caso

## Propósito

Este documento describe el dominio organizacional del Sistema de Pañol, el problema que resuelve, los objetivos y el alcance del MVP. Es el punto de entrada a `docs/requirements/` y la base del bloque "Contexto del caso de estudio y claridad del problema" de la rúbrica.

## Dominio organizacional

El sistema se desarrolla para la **Escuela de Informática de la Universidad Andrés Bello, Sede Viña del Mar**. La escuela imparte carreras de Ingeniería Civil Informática e Ingeniería en Ejecución en Computación e Informática, ambas con un componente práctico fuerte que requiere el uso frecuente de recursos físicos compartidos: equipos de redes (routers, switches), instrumental electrónico (protoboards, osciloscopios portátiles, multímetros), kits de prototipado (Arduino, Raspberry Pi, sensores IoT) y herramientas de taller (set de pinzas, destornilladores, cables).

Estos recursos se conservan en un espacio físico denominado "pañol", administrado por un encargado (pañolero) bajo la supervisión de un Coordinador de Carrera y con responsabilidad final del Jefe de Carrera. La Escuela opera hoy con un registro manual de préstamos y devoluciones, basado en una planilla en papel y una hoja de cálculo auxiliar. Este mecanismo es operativamente funcional en escala pequeña pero presenta deficiencias evidentes en trazabilidad, alertas, reportes y control de morosidad.

## Problema

La operación manual del pañol genera cuatro problemas medibles:

1. **Pérdida de visibilidad**. No existe información consolidada sobre qué recurso está prestado, a quién, desde cuándo, y cuándo debería devolverse. Consultas simples como "¿cuántos osciloscopios están en uso ahora mismo?" toman minutos y dependen de la memoria del pañolero.
2. **Falta de control de morosidad**. No hay mecanismo sistemático para detectar alumnos con historial de devoluciones tardías o pérdidas de recursos. Las decisiones de bloqueo se toman caso por caso y dependen del criterio del pañolero.
3. **Reportes inexistentes**. Información relevante para la gestión de la Escuela —recursos más solicitados, niveles de stock crítico, tasas de pérdida por categoría— no se produce porque no hay datos estructurados que la alimenten.
4. **Fricción en la experiencia del alumno**. El alumno no sabe anticipadamente si el recurso que necesita está disponible, lo que lo obliga a ir físicamente al pañol y potencialmente perder tiempo.

## Tótem de atención

El **tótem** es el computador o tablet físico montado en el mostrador del pañol, a través del cual el pañolero opera el sistema durante el turno de atención. El enunciado del caso lo define como "tótem de atención físicamente emplazado en Pañol". Funcionalmente:

- Es un dispositivo único y fijo por pañol.
- Corre la aplicación local (`apps/totem/`) en modo fullscreen tipo kiosko, sin navegador visible.
- Mantiene sesión de pañolero durante todo el turno; las acciones sensibles (validar solicitud, registrar préstamo, registrar devolución, dar de baja) requieren reingreso de un PIN de cuatro dígitos.
- Es el único canal desde el que se materializa una solicitud en préstamo. El portal web no ejecuta esa operación.
- En el MVP no incluye periféricos (QR, lector de código de barras); el diseño los contempla como evolución.

## Objetivos

1. Automatizar el ciclo completo: solicitud web → validación en pañol → préstamo → devolución → cierre.
2. Centralizar la información de inventario, solicitudes y préstamos en una única base de datos consultable en tiempo real por todos los roles.
3. Generar automáticamente alertas de stock bajo y de morosidad, sin requerir revisión manual.
4. Producir reportes estructurados que alimenten decisiones de gestión del Jefe de Carrera.
5. Integrar capacidades de IA para asistir al alumno al armar su solicitud y para estimar riesgo de morosidad antes de autorizar un préstamo.
6. Dejar documentado un diseño evolutivo que permita agregar QR, SSO y multi-sede sin reescritura.

## Alcance del MVP

El MVP cubre:

- Portal web para alumnos y docentes (crear solicitudes, consultar historial, recibir notificaciones in-app, recibir ticket PDF de préstamo y devolución).
- Tótem para el pañolero (validar solicitudes, registrar préstamos y devoluciones, dar de alta/baja recursos del inventario).
- Administración (Jefe de Carrera y Coordinador: crear usuarios, importar alumnos desde Excel, bloquear/desbloquear morosos, aprobar préstamos especiales, consultar reportes).
- Asistente conversacional en el portal, que consulta el inventario y ayuda a armar solicitudes mediante Model Context Protocol.
- Scoring de riesgo de morosidad integrado al flujo de validación de la solicitud.
- Notificaciones in-app y ticket PDF descargable desde el portal.

Quedan fuera del MVP:

- Envío por correo electrónico (notificaciones y tickets son in-app).
- Escaneo de código QR o de barras en el tótem (requiere periférico físico).
- SSO federado con la infraestructura de identidad de la universidad.
- Operación multi-sede con replicación entre pañoles.
- Persistencia poliglota (MongoDB para catálogo, Postgres para transaccional).

Cada exclusión está argumentada en su ADR correspondiente en `docs/design/adrs/`.

## Restricciones

- **Tiempo del proyecto**: el entregable debe estar listo antes de la fecha de la mesa redonda final del ramo.
- **Equipo**: 2 equipos Feature según modelo LeSS básico, con los roles definidos en `docs/standards/methodology/`.
- **Stack obligatorio**: MERN adaptado a PostgreSQL, NestJS, RabbitMQ, TypeScript, Prisma, Next.js, Vite+React. Detalle y justificación en `docs/architecture/01-stack-tecnologico.md`.
- **Metodología**: LeSS con evidencia en Taiga (backlog único, dos equipos Feature, sprints de dos semanas).
- **Cloud-agnóstico**: el diseño no se ata a AWS, Azure ni GCP.

## Beneficiario

Escuela de Informática UNAB, Sede Viña del Mar. En términos operativos, los usuarios directos son los alumnos y docentes de las carreras de Informática, el pañolero de turno, el coordinador de carrera y el jefe de carrera.

## Amenazas e impacto

El análisis completo de amenazas (técnicas, operativas, regulatorias) y de impacto (operacional y estratégico) está en `08-amenazas-e-impacto.md`. Es el documento que cubre directamente el criterio "Contexto, problema, propuesta, amenazas e impacto" de la rúbrica, articulando cada amenaza con el RF/RNF/RC que la mitiga y cada impacto con el requerimiento que lo habilita.

## Glosario rápido

Términos del dominio que se usan a lo largo de los documentos, definidos aquí como referencia única.

- **Pañol**: espacio físico de la Escuela donde se resguardan los recursos prestables. Administrado por un Pañolero.
- **Pañolero**: rol operativo que atiende en ventanilla y opera el tótem durante su turno.
- **Tótem**: computador o tablet físico emplazado en el mostrador del pañol, que corre la aplicación local. Definido en la sección "Tótem de atención" de este documento.
- **Recurso**: todo ítem prestable del inventario, clasificado en Material, Herramienta o Equipo (RC.03).
- **Solicitud**: intención de retiro generada por un Alumno o Docente desde el portal, aún no materializada. Transita los estados de RC.16.
- **Préstamo**: solicitud efectivamente materializada en el tótem con entrega física de los recursos. Transita los estados de RC.17.
- **Reserva**: bloqueo temporal de stock asociado a una solicitud, con TTL configurable (RC.06). No descuenta inventario, solo lo inmoviliza.
- **Materialización**: paso operativo en el tótem que transforma una solicitud en préstamo (CU5, flujo principal).
- **Validación**: revisión de la solicitud por el Pañolero, ítem por ítem, para marcar disponibilidad real (RF.7, aclarado en CN.05).
- **Morosidad**: condición determinística definida en RC.01. Distinta del scoring predictivo (RC.11).
- **Blacklist**: conjunto de usuarios con bloqueo activo, por regla automática (RC.01) o manual (RC.10).
- **Ticket**: comprobante PDF emitido tras la materialización y tras la devolución, con ID correlativo (RC.07).
- **Outbox**: tabla local de cada microservicio donde se persisten los eventos pendientes de publicar en el broker. Garantiza la atomicidad entre el cambio en BD y la publicación.
- **Saga coreografiada**: forma de coordinar una transacción distribuida sin orquestador central. Cada servicio reacciona a eventos publicados por otros.
- **MCP (Model Context Protocol)**: protocolo para exponer "tools" de dominio a un cliente LLM. Desacopla al modelo del dominio del sistema.
