"""
Smoke test 04 — Message Expiration (delayed exchange).

Valida:
  - El plugin `rabbitmq_delayed_message_exchange` está habilitado.
  - El exchange `domain.delayed` (tipo x-delayed-message) está disponible.
  - Un mensaje con header `x-delay=3000` llega ~3s después de publicado, NO antes.

Mapea a EIP-03 — Message Expiration. Sustenta el TTL de reservas (RC.16) y
los retries diferidos.
"""

from __future__ import annotations

import json
import sys
import threading
import time
import uuid

import pika

import config


TEST_NAME = "test_04_delayed_exchange"
ROUTING_KEY = "smoke.test.delayed"
DELAY_MS = 3000
TOLERANCE_LOWER_MS = 2500  # no debe llegar antes de 2.5s
TOLERANCE_UPPER_MS = 5000  # debe llegar antes de 5s


def make_connection() -> pika.BlockingConnection:
    creds = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD)
    params = pika.ConnectionParameters(
        host=config.RABBITMQ_HOST,
        port=config.RABBITMQ_PORT,
        virtual_host=config.RABBITMQ_VHOST,
        credentials=creds,
    )
    return pika.BlockingConnection(params)


def run() -> tuple[bool, str]:
    try:
        connection = make_connection()
        channel = connection.channel()

        # Verifica que el exchange delayed exista (passive — no lo recrea)
        channel.exchange_declare(
            exchange=config.EXCHANGE_DELAYED,
            exchange_type="x-delayed-message",
            passive=True,
        )

        # Cola exclusiva bound al delayed
        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(
            exchange=config.EXCHANGE_DELAYED,
            queue=queue_name,
            routing_key=ROUTING_KEY,
        )

        received_at: list[float] = []
        message_id = str(uuid.uuid4())

        def on_message(ch, method, properties, body):
            received_at.append(time.time())
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue=queue_name, on_message_callback=on_message)

        # Publish con x-delay header
        published_at = time.time()
        channel.basic_publish(
            exchange=config.EXCHANGE_DELAYED,
            routing_key=ROUTING_KEY,
            body=json.dumps({"id": message_id, "type": "smoke.delayed"}),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
                message_id=message_id,
                headers={"x-delay": DELAY_MS},
            ),
        )

        # Consumer espera hasta TOLERANCE_UPPER_MS + 1s
        deadline = published_at + (TOLERANCE_UPPER_MS / 1000.0) + 1
        while time.time() < deadline and not received_at:
            connection.process_data_events(time_limit=0.2)

        connection.close()

        if not received_at:
            return False, f"el mensaje no llegó en {TOLERANCE_UPPER_MS+1000}ms"

        elapsed_ms = (received_at[0] - published_at) * 1000
        if elapsed_ms < TOLERANCE_LOWER_MS:
            return (
                False,
                f"el mensaje llegó muy temprano ({elapsed_ms:.0f}ms < {TOLERANCE_LOWER_MS}ms) — el plugin podría no estar activo",
            )
        if elapsed_ms > TOLERANCE_UPPER_MS:
            return False, f"el mensaje llegó muy tarde ({elapsed_ms:.0f}ms > {TOLERANCE_UPPER_MS}ms)"

        return True, f"delayed delivery OK (target {DELAY_MS}ms, real {elapsed_ms:.0f}ms)"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


if __name__ == "__main__":
    ok, msg = run()
    print(f"[{TEST_NAME}] {'OK' if ok else 'FAIL'} — {msg}")
    sys.exit(0 if ok else 1)
