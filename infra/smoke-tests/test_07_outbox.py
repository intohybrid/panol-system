"""
Smoke test 07 — Transactional Outbox + Idempotent Receiver.

Valida:
  - Una transacción atómica de Postgres escribe el cambio de negocio + una
    fila en la tabla `outbox_events`.
  - Un relay polling lee filas no publicadas, las publica al broker y las
    marca como publicadas.
  - El consumer suscrito al evento valida con la tabla `processed_events`
    (Idempotent Receiver) que cada `event_id` se procesa una sola vez aunque
    llegue duplicado.

Mapea a EIP-05 — Transactional Outbox + Idempotent Receiver. Es el patrón
canónico que TODOS los publishers de eventos del sistema usarán.
"""

from __future__ import annotations

import json
import sys
import time
import uuid

import pika
import psycopg

import config


TEST_NAME = "test_07_outbox"
DB = "auth_db"
ROUTING_KEY = "smoke.outbox.user_created"
TIMEOUT_SECONDS = 5


def setup_outbox_tables(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS outbox_events;")
        cur.execute("DROP TABLE IF EXISTS processed_events;")
        cur.execute(
            """
            CREATE TABLE outbox_events (
                event_id UUID PRIMARY KEY,
                routing_key TEXT NOT NULL,
                payload JSONB NOT NULL,
                published_at TIMESTAMPTZ
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE processed_events (
                event_id UUID PRIMARY KEY,
                processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
    conn.commit()


def teardown_outbox_tables(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS outbox_events;")
        cur.execute("DROP TABLE IF EXISTS processed_events;")
    conn.commit()


def make_amqp_connection() -> pika.BlockingConnection:
    creds = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD)
    params = pika.ConnectionParameters(
        host=config.RABBITMQ_HOST,
        port=config.RABBITMQ_PORT,
        virtual_host=config.RABBITMQ_VHOST,
        credentials=creds,
    )
    return pika.BlockingConnection(params)


def relay_polling_publish(pg_conn, amqp_channel) -> int:
    """Lee outbox_events no publicados, los publica y los marca."""
    published_count = 0
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT event_id, routing_key, payload FROM outbox_events "
            "WHERE published_at IS NULL FOR UPDATE SKIP LOCKED;"
        )
        rows = cur.fetchall()

    for event_id, routing_key, payload in rows:
        amqp_channel.basic_publish(
            exchange=config.EXCHANGE_EVENTS,
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
                message_id=str(event_id),
                headers={"x-event-id": str(event_id)},
            ),
        )
        with pg_conn.cursor() as cur:
            cur.execute(
                "UPDATE outbox_events SET published_at = NOW() WHERE event_id = %s;",
                (event_id,),
            )
        published_count += 1
    pg_conn.commit()
    return published_count


def run() -> tuple[bool, str]:
    pg_conn = None
    amqp_conn = None
    try:
        pg_conn = psycopg.connect(config.postgres_dsn(DB))
        setup_outbox_tables(pg_conn)

        # Acto 1: simulación de operación de negocio + inserción en outbox
        event_id_1 = uuid.uuid4()
        event_id_2 = uuid.uuid4()
        payload_1 = {"event_id": str(event_id_1), "user_id": "U-1", "email": "a@x.cl"}
        payload_2 = {"event_id": str(event_id_2), "user_id": "U-2", "email": "b@x.cl"}

        with pg_conn.cursor() as cur:
            cur.execute(
                "INSERT INTO outbox_events (event_id, routing_key, payload) VALUES (%s, %s, %s::jsonb);",
                (str(event_id_1), ROUTING_KEY, json.dumps(payload_1)),
            )
            cur.execute(
                "INSERT INTO outbox_events (event_id, routing_key, payload) VALUES (%s, %s, %s::jsonb);",
                (str(event_id_2), ROUTING_KEY, json.dumps(payload_2)),
            )
        pg_conn.commit()

        # Acto 2: relay polling publica los eventos
        amqp_conn = make_amqp_connection()
        amqp_ch = amqp_conn.channel()

        result = amqp_ch.queue_declare(queue="", exclusive=True)
        consumer_queue = result.method.queue
        amqp_ch.queue_bind(
            exchange=config.EXCHANGE_EVENTS,
            queue=consumer_queue,
            routing_key=ROUTING_KEY,
        )

        published = relay_polling_publish(pg_conn, amqp_ch)
        if published != 2:
            return False, f"se esperaban 2 eventos publicados, fueron {published}"

        # Acto 3: idempotent consumer
        processed_payloads: list[dict] = []

        def on_event(ch, method, properties, body):
            event_id = properties.headers.get("x-event-id") if properties.headers else None
            if event_id is None:
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                return
            try:
                with pg_conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO processed_events (event_id) VALUES (%s) "
                        "ON CONFLICT (event_id) DO NOTHING RETURNING event_id;",
                        (event_id,),
                    )
                    inserted = cur.fetchone()
                pg_conn.commit()
                if inserted is not None:
                    processed_payloads.append(json.loads(body))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception:
                pg_conn.rollback()
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        amqp_ch.basic_consume(queue=consumer_queue, on_message_callback=on_event)

        deadline = time.time() + TIMEOUT_SECONDS
        while len(processed_payloads) < 2 and time.time() < deadline:
            amqp_conn.process_data_events(time_limit=0.2)

        if len(processed_payloads) != 2:
            return False, f"se esperaban 2 eventos procesados, fueron {len(processed_payloads)}"

        # Acto 4: simular duplicado y verificar dedupe
        amqp_ch.basic_publish(
            exchange=config.EXCHANGE_EVENTS,
            routing_key=ROUTING_KEY,
            body=json.dumps(payload_1),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
                headers={"x-event-id": str(event_id_1)},
            ),
        )

        deadline = time.time() + 2
        before = len(processed_payloads)
        while time.time() < deadline:
            amqp_conn.process_data_events(time_limit=0.2)

        if len(processed_payloads) != before:
            return False, f"el evento duplicado se proceso dos veces ({len(processed_payloads)} vs {before})"

        with pg_conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM processed_events;")
            count = cur.fetchone()[0]
        if count != 2:
            return False, f"processed_events tiene {count} filas, se esperaban 2"

        return True, f"outbox publica 2 eventos, idempotent receiver dedupea duplicado, processed_events={count}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"
    finally:
        if pg_conn is not None and not pg_conn.closed:
            try:
                teardown_outbox_tables(pg_conn)
            finally:
                pg_conn.close()
        if amqp_conn is not None and not amqp_conn.is_closed:
            amqp_conn.close()


if __name__ == "__main__":
    ok, msg = run()
    print(f"[{TEST_NAME}] {'OK' if ok else 'FAIL'} — {msg}")
    sys.exit(0 if ok else 1)
