"""
Smoke test 05 — Dead Letter Channel.

Valida:
  - Una cola con argumento `x-dead-letter-exchange = domain.dlx` reenvía a la
    DLX cualquier mensaje que se rechace con `basic_nack(requeue=False)`.
  - El consumer suscrito a la DLX captura el mensaje muerto.

Mapea a EIP — Dead Letter Channel (Hohpe). Sustenta auditoría de errores y la
reconciliación nocturna (US-048).
"""

from __future__ import annotations

import json
import sys
import time
import uuid

import pika

import config


TEST_NAME = "test_05_dlx"
WORK_QUEUE = "smoke.dlx.work"
DLX_QUEUE = "smoke.dlx.audit"
ROUTING_KEY = "smoke.test.dlx"
TIMEOUT_SECONDS = 5


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
    connection = None
    try:
        connection = make_connection()
        channel = connection.channel()

        # Cleanup en caso de runs previos
        channel.queue_delete(queue=WORK_QUEUE)
        channel.queue_delete(queue=DLX_QUEUE)

        # Cola de trabajo con DLX configurada
        channel.queue_declare(
            queue=WORK_QUEUE,
            durable=False,
            arguments={
                "x-dead-letter-exchange": config.EXCHANGE_DLX,
                "x-message-ttl": 60000,  # 60s para no acumular si algo falla
            },
        )
        channel.queue_bind(
            exchange=config.EXCHANGE_EVENTS,
            queue=WORK_QUEUE,
            routing_key=ROUTING_KEY,
        )

        # Cola de auditoría suscrita a la DLX (fanout)
        channel.queue_declare(queue=DLX_QUEUE, durable=False)
        channel.queue_bind(exchange=config.EXCHANGE_DLX, queue=DLX_QUEUE)

        # Publica un mensaje al work queue
        message_id = str(uuid.uuid4())
        channel.basic_publish(
            exchange=config.EXCHANGE_EVENTS,
            routing_key=ROUTING_KEY,
            body=json.dumps({"id": message_id, "type": "smoke.dlx"}),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
                message_id=message_id,
            ),
        )

        # Consumer del work queue: rechaza con nack(requeue=False) → debe ir a DLX
        method, _, body = channel.basic_get(queue=WORK_QUEUE, auto_ack=False)
        deadline = time.time() + TIMEOUT_SECONDS
        while method is None and time.time() < deadline:
            time.sleep(0.2)
            method, _, body = channel.basic_get(queue=WORK_QUEUE, auto_ack=False)

        if method is None:
            return False, "el mensaje no llegó al work queue"

        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        # Esperar y consumir desde DLX
        time.sleep(0.5)
        method_dlx, _, body_dlx = channel.basic_get(queue=DLX_QUEUE, auto_ack=True)
        deadline = time.time() + TIMEOUT_SECONDS
        while method_dlx is None and time.time() < deadline:
            time.sleep(0.2)
            method_dlx, _, body_dlx = channel.basic_get(queue=DLX_QUEUE, auto_ack=True)

        if method_dlx is None:
            return False, "el mensaje rechazado no llegó a la DLX"

        captured = json.loads(body_dlx)
        if captured["id"] != message_id:
            return False, f"id en DLX no coincide ({captured['id']} != {message_id})"

        # Cleanup
        channel.queue_delete(queue=WORK_QUEUE)
        channel.queue_delete(queue=DLX_QUEUE)

        return True, "mensaje rechazado capturado correctamente por domain.dlx"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"
    finally:
        if connection and not connection.is_closed:
            connection.close()


if __name__ == "__main__":
    ok, msg = run()
    print(f"[{TEST_NAME}] {'OK' if ok else 'FAIL'} — {msg}")
    sys.exit(0 if ok else 1)
