# Panol System — Guía del Demo Funcional (Mock-First)

Este documento centraliza las instrucciones para levantar el demo funcional del sistema utilizando **infraestructura simulada**. Las APIs son reales y están listas para conectarse a las aplicaciones frontend, pero la persistencia y la mensajería ocurren en memoria para facilitar la portabilidad del demo.

## 1. Estrategia de Simulación

Para que el demo sea "zero-dependencies" (sin Docker obligatorio), implementamos la arquitectura hexagonal con:
- **Persistencia**: `InMemoryRepositories` (Arrays de objetos en memoria).
- **Mensajería**: `EventEmitter2` (Eventos locales síncronos/asíncronos dentro del mismo proceso para simular RabbitMQ).
- **IA**: Mocks de respuestas o llamadas directas a OpenAI (requiere API Key).

## 2. Microservicios a Levantar

Cada servicio corre en un puerto específico para ser consumido por el **API Gateway**:

| Servicio | Puerto | Rol en el Demo |
|---|---|---|
| `api-gateway` | 3000 | Punto único de conexión para las UIs. |
| `auth-svc` | 3001 | Login con usuarios hardcoded (Alumno/Pañolero). |
| `inventory-svc` | 3002 | CRUD de recursos en memoria. |
| `request-svc` | 3003 | Creación de solicitudes y lógica de reserva. |
| `loan-svc` | 3004 | Materialización de préstamos y devoluciones. |
| `ai-assistant-svc` | 3005 | Asistente IA (Mock o OpenAI). |

---

## 3. Instrucciones de Ejecución

### Paso 1: Instalación
```bash
# Desde la raíz del proyecto
pnpm install
```

### Paso 2: Ejecución de Servicios
Puedes levantar todos los servicios en paralelo usando Turbo:
```bash
pnpm dev
```

O levantar uno específico para pruebas:
```bash
pnpm --filter auth-svc dev
```

---

## 4. Endpoints Principales del Demo (vía Gateway :3000)

- `POST /auth/login`: Autenticación simulada.
- `GET /inventory/resources`: Listado de recursos disponibles.
- `POST /requests`: Crear nueva solicitud.
- `POST /loans/:id/issue`: Materializar préstamo (Tótem).
- `POST /loans/:id/return`: Registrar devolución (Tótem).

---

## 5. Hoja de Ruta de Implementación

1. [ ] Crear `package.json` raíz con configuración de workspaces.
2. [ ] Implementar el `api-gateway` con proxy hacia los puertos de los servicios.
3. [ ] Crear esqueletos de servicios con la capa de `infrastructure/outbound/persistence/in-memory`.
4. [ ] Implementar el `SharedEventBus` local para la comunicación entre servicios.
