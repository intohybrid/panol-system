# Infraestructura local — Sistema de Pañol

Servicios base que cualquier microservicio del MVP necesita para arrancar:
PostgreSQL (7 bases), MongoDB (catálogo), RabbitMQ (4 exchanges), más UIs de
inspección (Adminer, Mongo Express).

Todo se levanta con `docker compose`. No hay nada específico de cloud
(ADR-009: cloud-agnóstico). Para producción, los mismos contenedores corren
en EKS / AKS / GKE / on-premise sin cambios.

## Requisitos previos

- Docker Desktop 4.x o Docker Engine 24+ con `docker compose` v2.
- Linux/macOS/Windows (WSL2). En Windows nativo usar Docker Desktop con WSL2 backend.
- ~2 GB de RAM disponible para los contenedores en idle.

## Cómo levantar

```bash
cd infra
cp .env.example .env       # ajustar credenciales si fuera necesario
docker compose up -d
```

Esperar ~30s a que todos los healthchecks queden en `healthy`:

```bash
docker compose ps
```

## Endpoints disponibles

| Servicio | URL / puerto | Credenciales |
|---|---|---|
| PostgreSQL | `localhost:5432` | `panol` / `panol` |
| MongoDB | `localhost:27017` | `panol` / `panol` |
| RabbitMQ AMQP | `localhost:5672` | `panol` / `panol` |
| RabbitMQ Management UI | http://localhost:15672 | `panol` / `panol` |
| Adminer (Postgres UI) | http://localhost:8080 | server: `postgres`, user/pass: `panol` |
| Mongo Express | http://localhost:8081 | basic auth: `panol` / `panol` |

## Bases creadas en Postgres

- `auth_db` — auth-svc
- `inventory_db` — inventory-svc
- `request_db` — request-svc
- `loan_db` — loan-svc
- `notification_db` — notification-svc
- `ai_risk_db` — ai-risk-svc
- `ai_assistant_db` — ai-assistant-svc
- `reports_db` — reports-svc (read-model CQRS, ADR-015)

## Exchanges declarados en RabbitMQ

Cargados desde `rabbitmq/definitions.json` al primer arranque:

| Exchange | Tipo | Propósito |
|---|---|---|
| `domain.events` | topic | Bus principal de eventos de dominio. Routing keys `user.*`, `inventory.*`, `request.*`, `loan.*`, etc. |
| `domain.commands` | direct | Patrón Request-Reply (EIP-04) para comandos con respuesta. |
| `domain.delayed` | x-delayed-message | Message Expiration (EIP-03) — TTL de reservas, retries diferidos. |
| `domain.dlx` | fanout | Dead Letter Channel — captura mensajes muertos para auditoría/reconciliación. |

## Validar la infra

Después de levantar todo, correr la suite de smoke tests:

```bash
cd smoke-tests
pip install -r requirements.txt
python run_all.py
```

Cada test mapea a un patrón EIP del catálogo (ver
`docs/architecture/04-eip-catalog.md`). Si los 7 pasan, la infra está lista
para que los microservicios se conecten.

## Bajar todo

```bash
docker compose down       # detiene contenedores, mantiene volúmenes
docker compose down -v    # detiene Y borra volúmenes (datos perdidos)
```

## Operaciones útiles

```bash
# Ver logs en vivo
docker compose logs -f rabbitmq

# Re-iniciar un servicio individual
docker compose restart postgres

# Ejecutar comando dentro de un contenedor
docker compose exec postgres psql -U panol -d auth_db
docker compose exec mongodb mongosh -u panol -p panol --authenticationDatabase admin

# Forzar reload de definitions.json en RabbitMQ
docker compose down rabbitmq && docker compose up -d rabbitmq
```

## Troubleshooting

**El plugin de delayed-message no carga.** Revisar `docker compose logs rabbitmq` — debería decir `Plugin rabbitmq_delayed_message_exchange started`. Si falla, verificar que el `Dockerfile` haya descargado el `.ez` correctamente (necesita acceso a internet en el build).

**Adminer no conecta a Postgres.** Usar `postgres` (nombre del servicio) como host, NO `localhost`. Adminer corre dentro de la red Docker.

**Puerto 5432 ocupado.** Hay otro Postgres local. Cambiar `POSTGRES_PORT` en `.env` y reiniciar.

**Mongo Express muestra error 500.** Esperar 30s adicionales — Mongo a veces tarda en aceptar conexiones aun cuando el healthcheck pasa.

## Próximas evoluciones

- Sprint 2: agregar OpenTelemetry Collector + Tempo + Loki + Grafana (US-049).
- Producción: reemplazar Adminer/Mongo Express por herramientas internas (no exponer en la red final).
