# Diagramas — Sistema de Pañol

Catálogo de los 19 diagramas que acompañan la documentación de arquitectura. Todos en formato `.drawio` (compatible con [diagrams.net](https://app.diagrams.net) y draw.io desktop).

## Cómo abrir

- **Online**: arrastrar el archivo a `https://app.diagrams.net` o usar `File → Open from → Device`.
- **Desktop**: descargar [draw.io desktop](https://github.com/jgraph/drawio-desktop/releases) y abrir el archivo.
- **VS Code**: extensión `Draw.io Integration` (`hediet.vscode-drawio`) para edición inline.

## Cómo regenerar

Los diagramas se generan desde `generate_drawio.py`. Para volver a producirlos (por ejemplo si cambia la nomenclatura de microservicios):

```bash
cd docs/design/diagrams
python3 generate_drawio.py
```

Esto sobrescribe los `.drawio`. **No editar manualmente los archivos generados** si se planea regenerar — los cambios se perderán. Para retoques visuales finales (colores, layout pulido) se puede:

1. Generar el archivo con el script (estructura y semántica).
2. Abrir en draw.io y pulir layout.
3. Guardar manteniendo extensión `.drawio`.
4. Eliminar la entrada del script o aceptar que ediciones manuales se perderán al regenerar.

## Inventario

### Grupo A — Estructurales (UML)

| Archivo | Tipo | Qué muestra |
|---|---|---|
| `DC-01-contexto.drawio` | Diagrama de Contexto UML (estilo C4-N1) | El sistema como caja única, 3 actores (alumno, pañolero, administrador) y 3 sistemas externos (LDAP/SSO UNAB, OpenAI API, email diferido). |
| `DC-02-componentes.drawio` | Diagrama de Componentes UML | 8 microservicios + 2 frontends + RabbitMQ + 6 bases PostgreSQL + OpenAI. Diferencia sólida (HTTP) y punteada naranja (eventos AMQP). |
| `DC-03-despliegue.drawio` | Diagrama de Despliegue UML | Nodos físicos: navegador/tótem, ingress, host de aplicaciones (containers), host de datos, host de mensajería, host de observabilidad. Cloud-agnóstico. |

### Grupo B — Comportamiento (Secuencia UML)

| Archivo | CU | Qué muestra |
|---|---|---|
| `SEQ-01-login.drawio` | CU1 | Login con JWT + refresh token. Camino feliz + credenciales inválidas (alt fragment). |
| `SEQ-02-crear-solicitud.drawio` | CU2 | Alumno arma carrito → request-svc valida stock → publica `request.created` con TTL 15min → notification-svc avisa al pañolero. |
| `SEQ-03-materializar-prestamo.drawio` | CU3 + CU6 | Pañolero valida en tótem → loan-svc consulta scoring (RC.11) → publica `loan.created` → inventory-svc reduce stock → notification-svc emite ticket PDF. Saga coreografiada. |
| `SEQ-04-devolucion.drawio` | CU4 | Pañolero registra devolución → loan-svc cierra préstamo → publica `loan.closed` → inventory-svc repone stock → notif al alumno. Cubre devolución parcial (opt fragment). |
| `SEQ-05-asistente-mcp.drawio` | CU7 | Alumno chatea → ai-assistant-svc → guardrail RC.15 → OpenAI con function calling → invoca tools MCP (`search_catalog`, `check_availability`) → respuesta natural + acción sugerida. |
| `SEQ-06-compensacion-ttl.drawio` | Saga error path | Reserva expira en `domain.delayed` → DLX captura → `request.expired` → request-svc cancela y libera stock → notif al alumno. Idempotent receiver. |

### Grupo C — Integración (EIP, shapes oficiales Hohpe)

Todos usan `shape=mxgraph.eip.*` con la nomenclatura oficial del libro de Hohpe.

| Archivo | Patrón principal | Qué muestra |
|---|---|---|
| `EIP-01-topologia-mensajeria.drawio` | Mensajería global | 4 exchanges RabbitMQ (`domain.events`, `domain.commands`, `domain.delayed`, `domain.dlx`) + 7 colas + bindings. Vista panorámica del bus. |
| `EIP-02-pubsub-content-router.drawio` | Publish-Subscribe + Content-Based Router | `request.created` se publica una vez; routing keys lo dirigen a 4 consumidores (notification, ai-risk, auth, audit). |
| `EIP-03-message-expiration-dlc.drawio` | Message Expiration + Dead Letter Channel | Reserva con TTL=15min en delayed exchange. Si vence, DLX la captura y dispara compensación. |
| `EIP-04-request-reply-correlation.drawio` | Request-Reply + Correlation Identifier | loan-svc envía request con `correlation_id` y `reply_to` a ai-risk-svc. Reply asíncrona vuelve por cola temporal. |
| `EIP-05-outbox-idempotent-receiver.drawio` | Transactional Outbox + Idempotent Receiver | Servicio escribe BD + tabla `outbox_events` en una transacción. Relay polling publica al broker. Consumer deduplica con `processed_events`. |

### Grupo D — Modelo de datos (ERD)

Generado por `generate_erd.py` (script aparte del `generate_drawio.py` para aislar el cambio).

| Archivo | Tipo | Qué muestra |
|---|---|---|
| `ERD-01-modelo-datos.drawio` | Entidad-Relación con polyglot por servicio | 8 swimlanes (uno por base PostgreSQL) con sus tablas, atributos clave, FK locales (líneas sólidas) y referencias lógicas cross-DB (líneas punteadas). 44 tablas, 28 relaciones. Incluye outbox/processed_events de cada servicio y las 6 proyecciones de `reports_db` (CQRS, ADR-015). |

### Grupo E — Máquinas de estado UML

Cubren el ciclo de vida de cada entidad principal según se contrata en `docs/architecture/08-estados-entidades.md`. Estados terminales con doble borde (`strokeWidth=3`). Notación: `disparador [guard] / efecto`.

| Archivo | Entidad | Servicio dueño | Qué muestra |
|---|---|---|---|
| `STATE-01-usuario.drawio` | Usuario | `auth-svc` | `CREADO → PENDIENTE_CAMBIO_CLAVE → ACTIVO`, ciclos de bloqueo (morosidad RC.01 y administrativo RC.10), estado terminal `INACTIVO`. |
| `STATE-02-solicitud.drawio` | Solicitud | `request-svc` | RC.16 completo: `BORRADOR`, `PENDIENTE`, `PENDIENTE_APROBACION`, `APROBADA`, terminales `MATERIALIZADA`/`MATERIALIZADA_PARCIAL`/`VENCIDA`/`CANCELADA`/`RECHAZADA`. Incluye el disparador delayed `request.expire`. |
| `STATE-03-prestamo.drawio` | Préstamo | `loan-svc` | RC.17: `EN_CURSO` → `DEVUELTO`/`DEVUELTO_CON_FALTANTE`/`ANULADO`, con el flag transitorio `ATRASADO`. |
| `STATE-04-recurso.drawio` | Recurso | `inventory-svc` | RC.18: `ACTIVO ↔ EN_MANTENCION`, terminal `BAJA`. Nota sobre por qué NORMAL/BAJO/CRITICO no son estados del recurso. |
| `STATE-05-reserva-stock.drawio` | Reserva de stock | `inventory-svc` | `ACTIVA` → `CONSUMIDA`/`LIBERADA_PARCIAL`/`LIBERADA_POR_EXPIRACION`/`LIBERADA_POR_CANCELACION`. Cobertura de ADR-010 y RC.12. |

## Trazabilidad

Cada diagrama está vinculado a documentos de `docs/architecture/`:

| Diagrama | Doc relacionado |
|---|---|
| DC-01, DC-02 | `00-overview.md`, `02-topologia-microservicios.md`, `07-microservicios-responsabilidades.md` |
| DC-03 | `02-topologia-microservicios.md` (sección despliegue) |
| SEQ-* | `05-saga-coreografiada.md`, `06-ia-mcp.md` |
| EIP-* | `04-eip-catalog.md`, `03-eventos-dominio.md` |
| ERD-01 | `10-modelo-datos.md`, `02-topologia-microservicios.md`, `07-microservicios-responsabilidades.md`, ADR-002, ADR-015 |
| STATE-* | `08-estados-entidades.md`, `05-reglas-de-negocio.md` (RC.16/RC.17/RC.18) |

Y a casos de uso de `docs/requirements/`:

| Diagrama | CU |
|---|---|
| SEQ-01 | CU1 — Login y autenticación |
| SEQ-02 | CU2 — Solicitud de préstamo |
| SEQ-03 | CU3 + CU6 — Validación + scoring |
| SEQ-04 | CU4 — Devolución |
| SEQ-05 | CU7 — Asistente conversacional |
| STATE-01 | CU1, CU2 (usuarios, bloqueo) |
| STATE-02 | CU2 — Solicitud |
| STATE-03 | CU3, CU4 — Préstamo, devolución |
| STATE-04 | CU3 (administración de inventario) |
| STATE-05 | CU2, CU3 (reserva y consumo de stock) |

## Pendiente de actualización

Los siguientes diagramas fueron creados antes de incorporar `reports-svc` (ADR-015) y **aún no lo muestran** como componente:

- `DC-01-contexto.drawio` (menciona 3 sistemas externos; reports-svc no es externo, pero conviene actualizar leyenda)
- `DC-02-componentes.drawio` (muestra 8 microservicios; debe pasar a 9)
- `DC-03-despliegue.drawio` (nodos de aplicación deberían incluir reports-svc)
- `EIP-01-topologia-mensajeria.drawio` (reports-svc no aparece como consumer en el bus)
- `EIP-02-pubsub-content-router.drawio` (cuando el ejemplo usa `request.created`, falta la rama a reports-svc)

La actualización de estos diagramas está planificada como tarea separada y no forma parte de la entrega que agregó los STATE-* y reports-svc a la documentación escrita.

## Exportación a PNG/SVG (para PPT)

Para incrustar en la presentación final:

```
File → Export as → PNG (o SVG)
```

Recomendado: SVG para presentación (escalable sin pérdida) o PNG @300dpi para impresión.

Si se prefiere automatizar la exportación, draw.io desktop permite:

```bash
drawio-desktop --export --format svg --output ./png/ DC-01-contexto.drawio
```

(Ver `drawio-desktop --help` para opciones de batch.)

## Convenciones visuales

- **Verde claro** (`#d5e8d4`) — componente interno del sistema.
- **Azul claro** (`#dae8fc`) — actor o sistema central / lifeline.
- **Rojo claro** (`#f8cecc`) — sistema externo (LDAP, OpenAI, email).
- **Amarillo claro** (`#fff2cc`) — base de datos (cilindro) o nota.
- **Naranja claro** (`#ffe6cc`) — broker / canal de mensajería.
- **Sólida** — flujo síncrono HTTP / lectura BD.
- **Punteada naranja** — flujo asincrónico AMQP.
- **Punteada roja** — camino de error / DLX.
- **Punteada gris** — retorno (sequence diagrams).
