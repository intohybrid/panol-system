# ADR-012 — QR y código de barras como roadmap, fuera del MVP

- **Estado**: Aceptada para MVP
- **Fecha**: 2026-04-25
- **Decisores**: Equipo Magíster

## Contexto

El Caso 11 sugiere (sin exigirlo explícitamente) la identificación rápida de solicitudes, préstamos y recursos mediante códigos legibles por máquina. Un flujo natural en el pañol sería: el alumno llega con su ticket PDF impreso o en el teléfono; el Pañolero escanea el QR del ticket en el tótem y la solicitud se ubica automáticamente sin tipear un identificador. Lo mismo con los recursos: cada equipo con código de barras permitiría descontar stock con un escaneo.

La implementación real requiere decisiones que van más allá del software:

- Periférico físico: lector USB o cámara web apuntando a un mousepad.
- Etiquetado físico de cada recurso del inventario (estampado, adhesivo resistente).
- Proceso operativo de emisión y reposición de etiquetas por cada alta/baja.
- Estándar del código (QR, Code-128, DataMatrix) y formato del payload.

## Decisión

El MVP **no implementa** lectura de QR ni de código de barras. El tótem ubica solicitudes tipeando documento o ID correlativo. Los tickets PDF se generan con el ID en texto plano legible, sin QR incrustado (ni siquiera visual — ver `DQ.03`).

El diseño del sistema contempla la evolución:

- El ID correlativo ya es estable y único (`RC.07`).
- Los eventos (`loan.issued`, `loan.returned`) llevan el `ticketId` como campo explícito.
- El modelo del recurso admite un campo `codigo_externo` opcional para el futuro código físico.

Incorporar lectores en una fase posterior se reduce a: (a) conectar el periférico, (b) agregar el handler de input en el tótem, (c) enriquecer el ticket PDF con QR (librería `qrcode`), (d) enriquecer la impresión de inventario con etiquetas.

## Alternativas consideradas

### QR incrustado en el PDF desde el inicio

- **Pros**: costo técnico bajo (agregar librería de QR y generar la imagen).
- **Contras**: si no se va a escanear, el QR es decoración. No aporta al flujo y sí genera expectativa equivocada en el usuario y en los evaluadores ("si tiene QR, por qué no lo escanean").

### Código de barras Code-128 para recursos (sin QR para tickets)

- **Pros**: permite contar recursos individualmente.
- **Contras**: el MVP modela recursos por **tipología con stock agregado** (`SP.10`, "no hay trackeo de instancia física individual"). Un código de barras por tipología sería meramente un identificador de catálogo, no aportaría sobre el nombre del recurso. El trackeo por instancia es otra decisión más amplia, fuera de alcance.

### Implementar escáner software con cámara web

- **Pros**: sin hardware extra.
- **Contras**: depende de iluminación, calidad de cámara, calibración. Experiencia inconsistente. Para un MVP con prioridad de mostrar dominio y patrones, no vale el tiempo.

## Decisión justificada

QR y código de barras son una mejora de UX que no agrega poder arquitectónico ni evidencia EIP/SAGA/IA. Incluirlos dilata el MVP sin fortalecer la defensa técnica del proyecto. Mantenerlos en roadmap deja el diseño preparado y concentra el esfuerzo del equipo en los componentes que sí pesan en la rúbrica.

## Consecuencias

- El tótem busca solicitudes por tipeo de documento (RUT/DNI/Pasaporte) o ID correlativo (`PRE-AAAA-NNNNNN`).
- Los tickets PDF tienen el ID legible y copiable; el diseño del PDF deja espacio reservado para QR futuro.
- El modelo de recurso incluye `codigo_externo` nullable desde el MVP para no requerir migración en la fase que agregue lectores.
- Roadmap explícito post-MVP: **Fase 2 — Trazabilidad física**: periférico, etiquetado, QR en ticket, instancias individuales de recursos de alto valor.
- Defensa en mesa redonda: "MVP con alcance controlado. QR y código de barras son mejora incremental con punto de extensión previsto, no rediseño".
