"""
Smoke test 01 — PostgreSQL.

Valida:
  - Conexión al servidor con credenciales del .env.
  - Existencia de las 8 bases declaradas en init/01-create-databases.sql.
  - Operaciones básicas (DDL + DML) sobre una base concreta (auth_db).
  - Transacción con commit y rollback.

Mapea a: ningún EIP específico — capa de persistencia base.
"""

from __future__ import annotations

import sys

import psycopg

import config


TEST_NAME = "test_01_postgres"


def check_databases_exist() -> list[str]:
    """Verifica que las 8 bases del proyecto existen."""
    conn = psycopg.connect(config.postgres_dsn("postgres"))
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            existing = {row[0] for row in cur.fetchall()}
        missing = [db for db in config.POSTGRES_DATABASES if db not in existing]
        if missing:
            raise AssertionError(f"Bases faltantes: {missing}")
        return config.POSTGRES_DATABASES
    finally:
        conn.close()


def check_basic_ddl_dml() -> None:
    """Crea una tabla temp en auth_db, inserta y consulta, luego la dropea."""
    conn = psycopg.connect(config.postgres_dsn("auth_db"))
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS smoke_users;")
            cur.execute(
                """
                CREATE TABLE smoke_users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
            cur.execute(
                "INSERT INTO smoke_users (email) VALUES (%s) RETURNING id;",
                ("smoke@test.local",),
            )
            inserted_id = cur.fetchone()[0]
            assert inserted_id == 1, f"id esperado 1, recibido {inserted_id}"

            cur.execute("SELECT email FROM smoke_users WHERE id = %s;", (inserted_id,))
            email = cur.fetchone()[0]
            assert email == "smoke@test.local"
        conn.commit()

        # Rollback de prueba
        with conn.cursor() as cur:
            cur.execute("INSERT INTO smoke_users (email) VALUES ('rollback@test.local');")
        conn.rollback()
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM smoke_users;")
            count = cur.fetchone()[0]
            assert count == 1, f"rollback fallo: {count} filas en lugar de 1"

        # Limpieza
        with conn.cursor() as cur:
            cur.execute("DROP TABLE smoke_users;")
        conn.commit()
    finally:
        conn.close()


def run() -> tuple[bool, str]:
    try:
        dbs = check_databases_exist()
        check_basic_ddl_dml()
        return True, f"8 bases OK ({', '.join(dbs)}), DDL+DML+rollback OK"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


if __name__ == "__main__":
    ok, msg = run()
    print(f"[{TEST_NAME}] {'OK' if ok else 'FAIL'} — {msg}")
    sys.exit(0 if ok else 1)
