# IA: scoring de riesgo y asistente conversacional

## Propósito

Este documento describe cómo el sistema integra dos capacidades de inteligencia artificial — un scoring predictivo de riesgo de morosidad y un asistente conversacional para armar solicitudes — y por qué cada una se trata como microservicio con contrato claro y no como librería incrustada en otro servicio. Cubre la sección "Uso de IA" exigida por la rúbrica del trabajo final del MIT Design Full Stack + MIT Design AI.

## Principio rector

La IA en este sistema es una pieza más del dominio, no la novedad central. Se la trata con la misma disciplina que a cualquier otro componente: contrato explícito, fallback definido, testabilidad, separación clara de responsabilidades. Si la pieza de IA falla o se desactiva, el flujo principal sigue funcionando — degradado, pero correcto.

---

## Capacidad 1: scoring de riesgo (`ai-risk-svc`)

### Qué resuelve

La regla determinística RC.01 detecta morosos *después* del incumplimiento. El scoring agrega una capa preventiva: estimar la probabilidad de que un usuario incumpla *antes* de aceptar la solicitud, para que el sistema pueda pedir aprobación adicional o denegar (RC.11).

### Modelo

| Decisión | Elección | Justificación |
|---|---|---|
| **Tipo de modelo** | Random Forest binario | Tabular, pocos features, interpretable. No se justifica deep learning. |
| **Framework de entrenamiento** | scikit-learn (Python) | Estándar de la industria para tabular; el equipo lo conoce. |
| **Serving** | onnxruntime-node (modelo exportado a ONNX) | Mantiene el stack en Node sin servidor Python adicional. Latencia < 50 ms p99. |
| **Datos de entrenamiento** | Sintéticos para el MVP | El dataset real no existe aún. Se generan datos sintéticos con perfiles realistas (alumnos puntuales, alumnos olvidadizos, alumnos morosos crónicos). En producción se reentrena con datos propios. |

### Features de entrada

| Feature | Origen | Por qué importa |
|---|---|---|
| `historial_atrasos_30d` | `loan-svc` | Patrón reciente. |
| `historial_perdidas_semestre` | `loan-svc` + `stock.lost` | Historial de pérdidas declaradas. |
| `cantidad_recursos_solicitados` | `request-svc` | Más recursos → más superficie de error. |
| `tipo_recursos` | `inventory-svc` | Equipos > Herramientas > Materiales en costo. |
| `dia_semana_solicitud` | calculado | Final de semestre tiene patrones distintos a inicio. |
| `carrera` | `auth-svc` | Carreras con más prácticas tienen patrones distintos. |
| `años_en_la_universidad` | `auth-svc` | Alumnos nuevos no tienen historial; el modelo lo trata como prior neutro. |
| `prestamos_activos_actuales` | `loan-svc` | Pila de obligaciones abiertas. |

Los features se construyen en `request-svc` antes del Request-Reply, no dentro de `ai-risk-svc`. Esto desacopla el modelo del esquema de datos del dominio.

### Contrato de servicio

Endpoint AMQP `risk.score` (Request-Reply):

**Request**
```json
{
  "userId": "uuid",
  "features": {
    "historial_atrasos_30d": 1,
    "historial_perdidas_semestre": 0,
    "cantidad_recursos_solicitados": 2,
    "tipo_recursos": ["EQUIPO", "MATERIAL"],
    "dia_semana_solicitud": 4,
    "carrera": "ICCI",
    "anios_universidad": 3,
    "prestamos_activos_actuales": 0
  },
  "modelVersion": "auto"
}
```

**Response**
```json
{
  "score": 0.23,
  "drivers": [
    {"feature": "historial_atrasos_30d", "contribution": 0.18},
    {"feature": "tipo_recursos", "contribution": 0.05}
  ],
  "modelVersion": "v1.2.0",
  "scoredAt": "2026-04-23T10:14:32Z"
}
```

`drivers` lista los 3 features que más empujaron el score, derivados con SHAP local. Permite explicar la decisión al alumno y al pañolero ("tu solicitud tiene riesgo medio porque tuviste un atraso reciente"). Es requisito del criterio de transparencia del bloque IA de la rúbrica.

### Aplicación del score (RC.11)

| Rango | Acción de `request-svc` |
|---|---|
| `score < 0.4` | Aceptar normalmente. |
| `0.4 ≤ score < 0.7` | Aceptar pero requiere aprobación manual del Coord para préstamos `Especiales` (RF-C.05). Para préstamos normales, aceptar con flag `riesgo_medio` que aparece en el tótem al pañolero. |
| `score ≥ 0.7` | Rechazar, mostrar al alumno los `drivers` como explicación, sugerir contactar al Coord. |

Los umbrales son configurables por el Jefe de Carrera (RS-JC.5) sin requerir despliegue.

### Fallback ante caída del servicio

Si `ai-risk-svc` no responde dentro del timeout (1.5 s), `request-svc` aplica score neutro `0.5` y registra una métrica `risk_score_degraded_total`. La solicitud avanza por el flujo normal con flag `riesgo_no_calculado`. El sistema no se bloquea por caída de IA.

### Reentrenamiento

Cada semestre, un job offline toma los datos reales de préstamos cerrados, etiqueta como "incumplió" / "cumplió" según RC.01, reentrena el modelo y valida en hold-out. Si la AUC mejora, se publica como nueva versión del modelo (v1.3, v1.4...). El versionado del modelo va en el header del evento `risk.scored` para auditabilidad.

### Sesgo y explicabilidad

El modelo se entrena con `carrera` y `anios_universidad` como features. Existe un riesgo de sesgo discriminatorio: alumnos de carreras con peor historial agregado podrían recibir scores sistemáticamente más altos. Mitigaciones documentadas en `08-amenazas-e-impacto.md` (AM.08):

- Auditoría semestral de equidad: comparar score promedio por carrera y por género; si la diferencia excede umbral, revisar features.
- Drivers transparentes: el alumno ve qué feature empuja su score y puede impugnar.
- El Jefe puede reducir el peso de features sensibles ajustando el modelo.

---

## Capacidad 2: asistente conversacional (`ai-assistant-svc`)

### Qué resuelve

Un alumno que necesita armar una solicitud puede no conocer el catálogo del pañol, no saber qué recurso específico requiere para una práctica concreta o equivocarse en cantidades. El asistente conversa con él, consulta el inventario en tiempo real, sugiere recursos adecuados y arma un borrador de solicitud que el alumno solo confirma. Cubre RF-C.03.

### Arquitectura: MCP + OpenAI Function Calling

El asistente se construye con dos piezas:

1. **Servidor MCP** (`@modelcontextprotocol/sdk`) que expone "tools" del dominio al cliente LLM. El servidor MCP es un microservicio que NestJS levanta junto con `ai-assistant-svc`.
2. **Cliente LLM** que consume las tools MCP y las traduce a OpenAI function calling. El cliente vive también en `ai-assistant-svc` y se comunica con la API de OpenAI (gpt-4o o equivalente).

```
Portal Web (chat) ──HTTP──> api-gateway ──HTTP──> ai-assistant-svc
                                                       │
                                                       ├─ Cliente OpenAI (function calling)
                                                       │       │
                                                       │       │ tool_call("consultar_inventario", {...})
                                                       │       ▼
                                                       └─ Servidor MCP local
                                                               │
                                                               │ AMQP / HTTP
                                                               ▼
                                                       inventory-svc, request-svc, auth-svc
```

### Tools MCP expuestas

| Tool | Qué hace | Backend |
|---|---|---|
| `consultar_inventario(filtros)` | Lista recursos disponibles con filtros (categoría, nombre, disponibilidad mínima). | `inventory-svc` (consulta directa). |
| `validar_disponibilidad(items, fecha)` | Verifica si los ítems están disponibles para la fecha solicitada. | `inventory-svc` (Request-Reply). |
| `sugerir_recursos_por_actividad(actividad)` | Dada una actividad libre ("práctica de redes capa 2"), sugiere recursos relevantes. | RAG sobre tabla `actividades_recursos` mantenida por el Pañolero. |
| `crear_solicitud_borrador(items, fecha)` | Crea una solicitud en estado `BORRADOR`, devuelve el ID. La confirmación final la hace el alumno explícitamente. | `request-svc`. |
| `consultar_mi_historial()` | Devuelve el historial del usuario logueado. | `loan-svc` + `request-svc`. |
| `consultar_estado_solicitud(requestId)` | Devuelve el estado actual. | `request-svc`. |

Cada tool tiene esquema JSON de entrada y salida formal. El LLM las "ve" como funciones invocables; MCP traduce esas invocaciones a llamadas reales sobre los servicios de dominio.

### Por qué MCP y no llamadas directas a OpenAI Function Calling

OpenAI Function Calling permite que el LLM invoque funciones, pero esas funciones quedan acopladas al cliente. MCP introduce un protocolo estándar entre el LLM y las tools, con tres beneficios:

1. **Reemplazabilidad del modelo**. Hoy es OpenAI; mañana puede ser Anthropic, Google, o un modelo on-prem. Las tools no cambian.
2. **Reusabilidad fuera del chat**. Las mismas tools MCP las puede usar Claude Desktop, otro asistente interno o un script de operaciones. Define una interfaz pública del dominio para LLMs.
3. **Evidencia de patrones**. La rúbrica valora abstracciones limpias. Mostrar MCP como capa de adaptación es un punto técnico defendible.

### Por qué cliente OpenAI dentro del mismo servicio

Se podría imaginar al servidor MCP en `ai-assistant-svc` y un cliente MCP separado en otra app. Para el MVP, ambos viven en el mismo servicio porque el flujo de portal → asistente → tools es de baja latencia y no se gana nada con la separación. El diseño deja preparado el split (las tools están detrás de la interfaz MCP estándar, no acopladas al cliente).

### Fallback ante caída del servicio

Si `ai-assistant-svc` no responde, el portal oculta el chat y muestra el formulario tradicional de solicitud. El alumno arma su solicitud manualmente. El sistema no depende del asistente para funcionar (RF.5 sigue cubierto por la UI tradicional).

### Memoria conversacional

El asistente guarda el historial de la conversación en una tabla `assistant_conversations` con TTL de 7 días. La memoria se pasa al LLM como contexto en cada turno. No se almacenan datos sensibles (todos los IDs son del propio usuario logueado).

### Costos y guardrails

- Cada conversación tiene presupuesto máximo de tokens (configurable, por defecto 8 K). Pasado el presupuesto, el chat se cierra y se ofrece reanudar con contexto resumido.
- Rate limit por usuario: 30 mensajes por hora. Evita uso abusivo.
- Las respuestas del LLM nunca ejecutan acciones de escritura sin confirmación explícita del alumno: `crear_solicitud_borrador` produce un BORRADOR, no una solicitud confirmada. La confirmación es un click separado en el portal. Esto aísla el riesgo de alucinaciones.

### Bloqueo de morosos (RC.15)

Si el usuario tiene `user.blocked` activo, el portal no muestra el chat. Adicionalmente, el servidor MCP rechaza todas las tools de escritura para usuarios bloqueados, como defensa en profundidad.

---

## Tabla resumen IA × dominio

| Capacidad | Servicio | Patrón EIP | Latencia objetivo | Acción si falla |
|---|---|---|---|---|
| Scoring de riesgo | `ai-risk-svc` | Request-Reply síncrono | < 200 ms p99 | Score neutro 0.5 + flag |
| Asistente conversacional | `ai-assistant-svc` | HTTP cliente → MCP → AMQP/HTTP | < 3 s por turno | Ocultar chat, formulario tradicional |
| Reentrenamiento de scoring | Job offline | N/A | Semestral | N/A |
| Memoria conversacional | Postgres en `ai-assistant-svc` | N/A | < 50 ms | Conversación nueva |

---

## Cobertura de la rúbrica

El criterio "Uso de IA" del MIT Design AI exige que la IA no sea un decorado y que su integración esté pensada con disciplina de ingeniería: contratos, fallbacks, observabilidad, ética. Los puntos cubiertos:

- **No es un decorado**. Las dos capacidades resuelven problemas concretos (RC.11 y RF-C.03).
- **Contratos explícitos**. Endpoint AMQP de scoring, tools MCP del asistente.
- **Fallbacks**. Score neutro y formulario tradicional. El sistema no depende de IA para funcionar.
- **Observabilidad**. Métrica `risk_score_degraded_total`, traces de cada conversación, costos en tokens registrados.
- **Ética y sesgo**. Auditoría semestral de equidad del scoring, drivers transparentes, política de no acción de escritura sin confirmación.
