# Reorden de tareas pendientes — Sistema de Pañol

**Decisión:** generar los **diagramas como imágenes (`.png`/`.svg`) ANTES** de generar la presentación `.pptx`, para que la `.pptx` pueda incrustarlas directamente.

**Estado:** propuesta — ninguna de las tareas se ejecuta hasta que el usuario confirme la revisión.

---

## Orden anterior (a descartar)

| # | Tarea | Output |
|---:|---|---|
| 1 | Generar `.pptx` final desde `PPT-content.md` | `docs/presentation/Panol-Sistema.pptx` |
| 2 | Generar imágenes de los diagramas (`.png`/`.svg`) desde los `.drawio` | `docs/design/diagrams/png/*.png` |

**Problema:** la `.pptx` necesita las imágenes incrustadas; producirla antes obliga a hacerla en dos pasadas (estructura primero, retoque con imágenes después) y deja una versión intermedia sin valor.

---

## Orden nuevo (propuesto)

| # | Tarea | Depende de | Output esperado |
|---:|---|---|---|
| 1 | **Exportar diagramas a imágenes** (`.png` 300dpi y `.svg`) desde los 19 `.drawio` | — | `docs/design/diagrams/png/<nombre>.png` y `/svg/<nombre>.svg` |
| 2 | **Verificar set mínimo de imágenes** referenciadas por la PPT (DC-01, DC-02, SEQ-02, SEQ-03, SEQ-05, EIP-01, EIP-02, EIP-03, EIP-05) | 1 | Listado de presencia/ausencia |
| 3 | **Generar `.pptx` final** desde `PPT-content.md` incrustando las imágenes producidas en el paso 1 | 1, 2 | `docs/presentation/Panol-Sistema.pptx` |
| 4 | **Revisión visual del deck** (pase rápido por las 29 slides) | 3 | Lista de ajustes (si los hay) |
| 5 | **Commit + push** del estado consolidado | 1, 3, 4 | Branch `feature/ppt` actualizada |

**Beneficios del nuevo orden:**

- Una sola pasada en la generación de la `.pptx` — sin versión intermedia descartable.
- Las imágenes quedan disponibles también para el README, GitHub renderizado, y para cualquier documento auxiliar (rúbrica, reporte) que las necesite.
- Si un diagrama necesita actualizarse (p. ej. agregar `reports-svc` a DC-02), se detecta antes de armar la PPT y se evita reincrustar imágenes ya pegadas.

---

## Notas operativas para cuando se ejecute

1. La exportación se puede hacer con `drawio-desktop` en modo CLI:
   ```bash
   drawio-desktop --export --format svg --output docs/design/diagrams/svg/  docs/design/diagrams/*.drawio
   drawio-desktop --export --format png --scale 2 --output docs/design/diagrams/png/  docs/design/diagrams/*.drawio
   ```
   Si no hay disponibilidad de `drawio-desktop`, alternativa con script Python (`drawio-export` package o re-renderizar desde `mxgraph` headless). En cualquier caso, **no editar los `.drawio` manualmente** — están bajo control de `generate_drawio.py`.

2. Antes del paso 3, decidir si se actualizan los 5 diagramas estructurales pendientes para incluir `reports-svc` (ver `docs/design/diagrams/README.md` sección "Pendiente de actualización"). Es independiente del reorden, pero conviene hacerlo en la misma ventana de trabajo si se va a producir la imagen final.

3. El skill `pptx` debe leerse **antes** de comenzar el paso 3 — los formatos profesionales requieren plantilla, título, layout consistente y notas del expositor.

---

## Pendientes paralelos no afectados por este reorden

- Resolver y commitear los 38 archivos modificados aún en working tree.
- Marcar como resueltos los hallazgos del `_revision-hallazgos.md` que ya estén corregidos en los archivos definitivos.
- Eventualmente: actualizar los 5 diagramas (DC-01..03, EIP-01..02) para reflejar `reports-svc` (ADR-015).
