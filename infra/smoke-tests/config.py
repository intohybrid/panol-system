"""
Configuración compartida para los smoke tests.
Lee de variables de entorno (con defaults sensatos) o de un .env si existe.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env del directorio infra/ si existe
INFRA_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = INFRA_ROOT / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


# ─── Postgres ────────────────────────────────────────────────────────────
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "panol")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "panol")
# Las 8 bases creadas por el init script (database-per-service, ADR-002)
POSTGRES_DATABASES = [
    "auth_db",
    "inventory_db",
    "request_db",
    "loan_db",
    "notification_db",
    "ai_risk_db",
    "ai_assistant_db",
    "reports_db",
]


def postgres_dsn(database: str = "postgres") -> str:
    return (
        f"host={POSTGRES_HOST} port={POSTGRES_PORT} "
        f"user={POSTGRES_USER} password={POSTGRES_PASSWORD} dbname={database}"
    )


# ─── MongoDB ─────────────────────────────────────────────────────────────
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USER = os.getenv("MONGO_USER", "panol")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "panol")


def mongo_uri() -> str:
    return (
        f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}"
        f"@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
    )


# ─── RabbitMQ ────────────────────────────────────────────────────────────
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "panol")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "panol")
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

# Exchanges declarados por definitions.json
EXCHANGE_EVENTS = "domain.events"
EXCHANGE_COMMANDS = "domain.commands"
EXCHANGE_DELAYED = "domain.delayed"
EXCHANGE_DLX = "domain.dlx"
