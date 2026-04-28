"""
Smoke test 03 — RabbitMQ Publish-Subscribe básico.

Valida:
  - Conexión AMQP con credenciales del .env.
  - Existencia del exchange `domain.events` (declarado en definitions.json).
  - Publish-Subscribe con routing key específica.
  - Consumer recibe el mensaje publicado.

Mapea a EIP-02 — Publish-Subscribe (Hohpe).
"""

from __future__ import annotations

import json
import sys
import threading
import time
import uuid

import pika

import config


TEST_NAME = "test_03_rabbitmq_basic"
ROUTING_KEY = "smoke.test.basic"
TIMEOUT_SECONDS = 5


def make_connection() -> pika.BlockingConnection:
    creds = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PASSWORD)
    params = pika.ConnectionParameters(
        host=config.RABBITMQ_HOST,
        port=config.RABBITMQ_PORT,
        virtual_host=config.RABBITMQ_VHOST,
        credentials=creds,
        heartbeat=30,
        blocked_connection_timeout=5,
    )
    return pika.BlockingConnection(params)


def run() -> tuple[bool, str]:
    try:
        connection = make_connection()
        channel = connection.channel()

        # Verifica passively que el exchange existe (no lo recrea)
        channel.exchange_declare(
            exchange=config.EXCHANGE_EVENTS, exchange_type="topic", passive=True
        )

        # Cola exclusiva temporal para este consumer
        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(
            exchange=config.EXCHANGE_EVENTS,
            queue=queue_name,
            routing_key=ROUTING_KEY,
        )

        received: list[dict] = []
        message_id = str(uuid.uuid4())

        def on_message(ch, method, properties, body):
            received.append(json.loads(body))
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue=queue_name, on_message_callback=on_message)

        # Consumer en thread aparte
        def consume():
            deadline = time.time() + TIMEOUT_SECONDS
            while time.time() < deadline and not received:
                connection.process_data_events(time_limit=0.5)

        consumer_thread = threading.Thread(target=consume)
        consumer_thread.start()

        # Publisher
        time.sleep(0.2)  # darle tiempo al consumer a estar listo
        pub_conn = make_connection()
        pub_ch = pub_conn.channel()
        payload = {"id": message_id, "type": "smoke.basic", "data": "hello"}
        pub_ch.basic_publish(
            exchange=config.EXCHANGE_EVENTS,
            routing_key=ROUTING_KEY,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
                message_id=message_id,
            ),
        )
        pub_conn.close()

        consumer_thread.join(timeout=TIMEOUT_SECONDS + 1)
        connection.close()

        if not received:
            return False, f"no se recibió mensaje en {TIMEOUT_SECONDS}s"
        if received[0]["id"] != message_id:
            return False, f"id no coincide: esperado {message_id}, recibido {received[0]['id']}"
        return True, f"publish→consume OK (key={ROUTING_KEY})"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


if __name__ == "__main__":
    ok, msg = run()
    print(f"[{TEST_NAME}] {'OK' if ok else 'FAIL'} — {msg}")
    sys.exit(0 if ok else 1)
