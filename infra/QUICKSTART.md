# Quickstart — Levantar y verificar la infraestructura

Guía paso a paso para correr la infraestructura local del Sistema de Pañol y validar que todo quedó OK. Pensado para la primera vez.

Para detalles operativos (logs, restart, troubleshooting), ver `README.md` en este mismo directorio.

---

## 0. Prerrequisitos

```powershell
docker --version           # 20.x o superior
docker compose version     # v2.x
python --version           # 3.10+
```

Docker Desktop debe estar **corriendo** antes de continuar.

---

## 1. Levantar los contenedores

```powershell
cd "C:\Users\intoh\Documents\Claude\Projects\Tópicos de Ingeniería\panol-system\infra"
copy .env.example .env
docker compose up -d
```

La primera vez tarda 2–3 min (descarga imágenes + build de RabbitMQ con plugin de delayed-message). Las siguientes veces son segundos.

---

## 2. Verificar que todos los servicios están healthy

```powershell
docker compose ps
```

Esperás ver los 5 servicios en `Up` o `(healthy)`. RabbitMQ tarda ~30 s extra en hacer el bootstrap del plugin — si aparece `(starting)`, esperá un poco y revisá de nuevo.

| Container | Estado esperado |
|---|---|
| `panol-postgres` | Up (healthy) |
| `panol-mongo` | Up (healthy) |
| `panol-rabbitmq` | Up (healthy) |
| `panol-adminer` | Up |
| `panol-mongo-express` | Up |

Si algo queda `unhealthy`, mirá `docker compose logs <servicio> --tail 30`.

---

## 3. Verificación manual en el navegador

Abrir las tres URLs y comprobar lo indicado en cada una.

### 3.1 RabbitMQ Management UI

- **URL:** http://localhost:15672
- **Usuario:** `panol`
- **Contraseña:** `panol`

**Verificar:** ir a la pestaña **Exchanges** → deben aparecer los 4 exchanges del proyecto:

| Nombre | Tipo |
|---|---|
| `domain.events` | topic |
| `domain.commands` | direct |
| `domain.delayed` | x-delayed-message |
| `domain.dlx` | fanout |

Si falta alguno, las definiciones no se cargaron. Reiniciar con `docker compose restart rabbitmq`.

### 3.2 Adminer (UI de PostgreSQL)

- **URL:** http://localhost:8080
- **Sistema:** `PostgreSQL`
- **Servidor:** `postgres`  *(ojo: NO `localhost` — Adminer corre dentro de la red Docker)*
- **Usuario:** `panol`
- **Contraseña:** `panol`
- **Base de datos:** dejar vacío al hacer login

**Verificar:** una vez dentro, en el panel izquierdo deben listarse las **8 bases** del proyecto:

- `auth_db`
- `inventory_db`
- `request_db`
- `loan_db`
- `notification_db`
- `ai_risk_db`
- `ai_assistant_db`
- `reports_db`

### 3.3 Mongo Express

- **URL:** http://localhost:8081
- **Usuario:** `panol`
- **Contraseña:** `panol`

**Verificar:** se abre la pantalla principal de Mongo Express con las bases del sistema (`admin`, `config`, `local`). No debe pedir credenciales adicionales.

---

## 4. Smoke tests Python

Una vez los 3 paneles abren OK, validar la infra de forma automatizada con los 7 smoke tests.

```powershell
cd smoke-tests
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_all.py
```

**Output esperado:**

```
Sistema de Pañol — smoke tests de infraestructura
Ejecutando 7 tests…

  → corriendo test_01_postgres… OK (0.42s)
  → corriendo test_02_mongo… OK (0.18s)
  → corriendo test_03_rabbitmq_basic… OK (0.83s)
  → corriendo test_04_delayed_exchange… OK (3.21s)
  → corriendo test_05_dlx… OK (1.05s)
  → corriendo test_06_request_reply… OK (1.44s)
  → corriendo test_07_outbox… OK (3.12s)

========================================================================
Resultado: 7/7 OK
========================================================================
```

**Cada test cubre un patrón EIP del catálogo:**

| Test | Qué valida | EIP |
|---|---|---|
| 01_postgres | Conexión + 7 bases + DDL/DML/transacciones | — (capa base) |
| 02_mongo | CRUD + índice único | — (capa base) |
| 03_rabbitmq_basic | Publish-Subscribe sobre `domain.events` | EIP-02 |
| 04_delayed_exchange | TTL con header `x-delay` | EIP-03 (Message Expiration) |
| 05_dlx | Mensaje rechazado cae en `domain.dlx` | Dead Letter Channel |
| 06_request_reply | `correlation_id` + `reply_to` | EIP-04 |
| 07_outbox | Outbox + Idempotent Receiver con dedupe | EIP-05 |

---

## 5. Bajar la infra al terminar

```powershell
docker compose down       # detiene los contenedores, mantiene los datos
docker compose down -v    # detiene Y borra los volúmenes (resetea todo)
```

---

## Troubleshooting rápido

| Problema | Solución |
|---|---|
| Puerto 5432, 27017, 5672, 8080, 8081 o 15672 ocupado | Cambiar el puerto en `.env` y `docker compose down && docker compose up -d` |
| `pip install psycopg2-binary` falla en Python 3.14 | Avisar — cambiamos a `psycopg[binary]` (psycopg3) |
| Plugin delayed-message no carga | `docker compose logs rabbitmq` debe mostrar `Plugin rabbitmq_delayed_message_exchange started`. Si no, rebuild con `docker compose build --no-cache rabbitmq` |
| Adminer da "could not translate host name" | Estás usando `localhost` en lugar de `postgres` como servidor |
| Mongo Express muestra error 500 | Esperar 30 s adicionales — Mongo a veces tarda en aceptar conexiones tras el healthcheck |
| Test 04 (delayed_exchange) falla con "el mensaje llegó muy temprano" | El plugin no está activo. Ver fila anterior. |

---

## Credenciales — resumen para copiar

```
PostgreSQL:    localhost:5432    panol / panol
MongoDB:       localhost:27017   panol / panol
RabbitMQ AMQP: localhost:5672    panol / panol
RabbitMQ UI:   http://localhost:15672    panol / panol
Adminer:       http://localhost:8080     server=postgres user=panol pass=panol
Mongo Express: http://localhost:8081     panol / panol
```

> Estas credenciales son **solo para desarrollo local**. Para producción se reemplazan por secretos generados y rotados.
