# Reporte de revisión de entregables — Sistema de Pañol

**Fecha:** 25 de abril de 2026
**Branch revisada:** `feature/ppt` (3 commits adelante de `master`)
**Alcance:** todo `docs/` del repositorio `panol-system`.
**Objetivo:** consolidar el estado de los artefactos generados hasta ahora, identificar lo que falta y proponer reordenar la ejecución pendiente para que los diagramas estén disponibles antes de generar la presentación.

---

## 1. Resumen ejecutivo

El proyecto tiene **toda la documentación escrita lista** (requirements, architecture, ADRs, standards, agile, contenido de la presentación) y un **catálogo completo de 19 diagramas en `.drawio`**. Lo que aún **no existe** son dos artefactos derivados que dependen de lo anterior:

1. **Imágenes exportadas** de los diagramas (`.png` o `.svg`) — necesarias para incrustarlas en la presentación y en cualquier render externo.
2. **Archivo final de presentación `.pptx`** — el contenido está completo en `docs/presentation/PPT-content.md` (29 slides, ~14 min de duración estimada), pero la presentación entregable aún no se ha materializado.

Hay además trabajo **pendiente sin commitear** (`git status` muestra ~38 archivos modificados en la branch `feature/ppt`), lo cual es consistente con que la sesión anterior cerró antes de empaquetar el último deliverable.

**Recomendación operativa:** invertir el orden de las dos tareas pendientes — generar primero los diagramas como imágenes y luego construir la `.pptx`, para que la presentación pueda referenciar las imágenes ya producidas.

---

## 2. Inventario de entregables

### 2.1 Requirements (`docs/requirements/`) — completo

| Archivo | Líneas | Estado |
|---|---:|---|
| `00-contexto.md` | 96 | OK |
| `01-actores-y-roles.md` | 121 | OK |
| `02-requerimientos-funcionales.md` | 187 | OK |
| `03-requerimientos-sistema.md` | 151 | OK |
| `04-casos-de-uso.md` | 294 | OK — 7 CU principales |
| `05-reglas-de-negocio.md` | 167 | OK |
| `06-supuestos-contradicciones-dudas.md` | 123 | OK |
| `07-trazabilidad.md` | 153 | OK — matriz RF↔CU↔US |
| `08-amenazas-e-impacto.md` | 184 | OK |
| `_revision-hallazgos.md` | 328 | Hallazgos clasificados HG.NN; varios resueltos en commits posteriores |

**Observaciones**
- `_revision-hallazgos.md` contiene hallazgos críticos como HG.01 (préstamo en nombre de otro alumno), HG.02 (alcance JC sobre perfiles), HG.03 (150×100 vs 150×150). Conviene revisar la traza de cuáles ya quedaron corregidos en los archivos definitivos antes de la mesa redonda.

### 2.2 Architecture (`docs/architecture/`) — completo

10 documentos (`00-overview` … `09-despliegue-uis`) que cubren visión, stack, topología, eventos, EIP, saga coreografiada, IA+MCP, responsabilidades por microservicio, máquinas de estado y despliegue de UIs. El último incorporado es `09-despliegue-uis.md` (commit "Se agrega defnicion para UI"), que documenta la decisión del ADR-016.

### 2.3 ADRs (`docs/design/adrs/`) — 16 + README, completo

Numerados ADR-001 a ADR-016, todos en formato MADR breve. El README mantiene la tabla maestra. ADR-014 a ADR-016 son las decisiones más recientes (coordinador-administra-docentes, reports-svc CQRS, despliegue UIs path-routing).

### 2.4 Diagramas (`docs/design/diagrams/`) — 19 `.drawio` + script generador

| Grupo | # | Archivos |
|---|---:|---|
| A. Estructurales (UML) | 3 | DC-01-contexto, DC-02-componentes, DC-03-despliegue |
| B. Comportamiento (Secuencia UML) | 6 | SEQ-01-login, SEQ-02-crear-solicitud, SEQ-03-materializar-prestamo, SEQ-04-devolucion, SEQ-05-asistente-mcp, SEQ-06-compensacion-ttl |
| C. Integración (EIP shapes Hohpe) | 5 | EIP-01-topologia-mensajeria, EIP-02-pubsub-content-router, EIP-03-message-expiration-dlc, EIP-04-request-reply-correlation, EIP-05-outbox-idempotent-receiver |
| D. Máquinas de estado | 5 | STATE-01-usuario, STATE-02-solicitud, STATE-03-prestamo, STATE-04-recurso, STATE-05-reserva-stock |

**Estado:** todos los `.drawio` están bien formados (cada uno contiene `<mxGraphModel>`). El README documenta cómo regenerarlos desde `generate_drawio.py`.

**Pendiente declarado en el propio README**: actualizar 5 diagramas estructurales (DC-01, DC-02, DC-03, EIP-01, EIP-02) para reflejar el `reports-svc` agregado en ADR-015 — pasar de 8 a 9 microservicios visibles. Esto NO bloquea la exportación a imágenes, pero es decisión del usuario si se actualiza ahora o después.

**No existen aún**: las imágenes derivadas (`.png` / `.svg`) que la presentación necesita.

### 2.5 Standards (`docs/standards/`) — completo

| Archivo | Líneas |
|---|---:|
| `00-coding-standards.md` | 481 |
| `01-hexagonal-architecture.md` | 900 |
| `02-testing-strategy.md` | 582 |

Plus `hexagonal-template/README.md` con plantilla por microservicio.

### 2.6 Agile (`docs/agile/`) — completo

- `backlog.csv` — 50 user stories distribuidas en 3 sprints (64 + 107 + 94 puntos).
- `taiga-dump.json` — dump completo del proyecto compatible con Taiga Project Importer.
- `jira-import.csv` y `jira-import-minimal.csv` — alternativa para Jira Cloud.
- `import_to_jira.py` — script Python para crear epics/sprints/stories vía API REST de Jira.
- `generate_taiga_dump.py` y `generate_jira_csv.py` — generadores reproducibles desde el CSV maestro.
- `README.md`, `jira-import.md`, `jira-import-via-api.md` — documentación de uso.

### 2.7 Presentación (`docs/presentation/`) — contenido sí, archivo `.pptx` no

- `PPT-content.md` (992 líneas, ~52 KB): guion completo de **29 slides** con título, cuerpo, notas del expositor, visual sugerido y mapeo a la rúbrica (C1-C10). Cubre todas las condiciones mínimas obligatorias y referencia explícitamente los diagramas que cada slide debe incluir (ver tabla "Diagramas requeridos" al final).
- **No existe** un `.pptx` ni imágenes exportadas en esta carpeta.

---

## 3. Brechas y dependencias

| Brecha | Bloquea | Recomendación |
|---|---|---|
| Imágenes de los 19 diagramas (`.png`/`.svg`) | Generación de la `.pptx`, render del README en GitHub | **Generar primero** — input directo de la presentación |
| Archivo `.pptx` con los 29 slides | Entrega final del video | Generar **después** de las imágenes |
| Cambios sin commitear en `feature/ppt` (38 archivos modificados) | Reproducibilidad del estado actual | Commit y push antes de continuar; conviene revisar el diff |
| `reports-svc` no aparece todavía en 5 diagramas estructurales (DC-01..03, EIP-01..02) | No bloquea la PPT, sí bloquea perfecta coherencia visual | Decisión del usuario: actualizar ahora o documentar como nota en la slide |
| Hallazgos del `_revision-hallazgos.md` aún no marcados como resueltos | Trazabilidad de las correcciones para defensa | Conviene un pase de "estado HG.NN: resuelto/abierto" |

---

## 4. Cobertura de la rúbrica del video

`PPT-content.md` declara cobertura completa de C1 a C10 con mapeo slide-a-criterio (sección "Mapa de cobertura" al inicio). Cada uno de los 10 criterios tiene al menos un slide asignado, y las **5 condiciones mínimas obligatorias** quedan cubiertas (plataforma con evidencia, alternativas justificadas, prototipo demostrable, EIP aplicado no solo nombrado, tendencias integradas al caso y prototipo). Solo queda transformar el contenido en archivo `.pptx` y agregar las imágenes.

---

## 5. Estado de Git

```
On branch feature/ppt
Your branch is up to date with 'origin/feature/ppt'.

Changes not staged for commit: 38 archivos modificados
  - docs/agile/* (10 archivos)
  - docs/architecture/00..09 (7 modificados)
  - docs/design/adrs/ADR-010..016 + README (8)
  - docs/design/diagrams/STATE-01..05 + README (6)
  - docs/requirements/07, 08, _revision-hallazgos (3)
  - docs/standards/00, 01, 02, hexagonal-template (4)
```

**Recomendación:** revisar el diff con `git diff` antes de commitear; varios de estos cambios pueden estar relacionados con el ADR-015 (reports-svc) y los `STATE-*` recién creados.

---

## 6. Conclusión

La documentación escrita está completa y consistente; el cuello de botella son los **dos artefactos derivados** que aún no se han producido: imágenes de diagramas y `.pptx`. Como el `.pptx` necesita las imágenes incrustadas, lo lógico es **invertir el orden de ejecución previsto** y generar primero los diagramas como `.png`/`.svg`, y luego ensamblar la presentación.

Esto es lo que se propone reflejar en la lista de tareas pendientes (ver `docs/REORDEN-TAREAS.md` adjunto). **No se ejecuta ninguna de esas tareas** — solo se reordenan a la espera de confirmación del usuario.
