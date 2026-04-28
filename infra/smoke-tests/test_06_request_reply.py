"""
Smoke test 06 — Request-Reply con Correlation Identifier.

Valida:
  - Cliente publica un comando en `domain.commands` con `correlation_id` y
    `reply_to` apuntando a una cola temporal exclusiva.
  - Servidor consume el comando, procesa y responde a la cola `reply_to` con el
    mismo `correlation_id`.
  - Cliente recibe la respuesta y la matchea por correlation_id.

Mapea a EIP-04 — Request-Reply + Correlation Identifier (Hohpe). Sustenta el
patrón loan-svc → ai-risk-svc para scoring sincrónico durante materialización.
"""

from __future__ import annotations

import json
import sys
import threading
import time
import uuid

import pika

import config


TEST_NAME = "test_06_request_reply"
COMMAND_QUEUE = "smoke.cmd.scoring"
COMMAND_KEY = "smoke.cmd.scoring"
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


def run_server(stop_event: threading.Event) -> None:
    """Servidor: consume comandos y responde a reply_to."""
    connection = make_connection()
    channel = connection.channel()
    channel.queue_delete(queue=COMMAND_QUEUE)
    channel.queue_declare(queue=COMMAND_QUEUE, durable=False)
    channel.queue_bind(
        exchange=config.EXCHANGE_COMMANDS,
        queue=COMMAND_QUEUE,
        routing_key=COMMAND_KEY,
    )

    def on_message(ch, method, properties, body):
        request = json.loads(body)
        # "Procesar" el request: simular un score
        response = {"loan_id": request["loan_id"], "score": 0.87, "reasons": ["smoke"]}
        ch.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            body=json.dumps(response),
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id,
                content_type="application/json",
            ),
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=COMMAND_QUEUE, on_message_callback=on_message)

    while not stop_event.is_set():
        connection.process_data_events(time_limit=0.2)

    channel.queue_delete(queue=COMMAND_QUEUE)
    connection.close()


def run() -> tuple[bool, str]:
    stop_event = threading.Event()
    server_thread = threading.Thread(target=run_server, args=(stop_event,), daemon=True)
    server_thread.start()
    time.sleep(0.5)  # darle tiempo al servidor a registrarse

    try:
        connection = make_connection()
        channel = connection.channel()

        # Cola temporal exclusiva para la respuesta
        result = channel.queue_declare(queue="", exclusive=True)
        reply_queue = result.method.queue

        correlation_id = str(uuid.uuid4())
        responses: dict[str, dict] = {}

        def on_response(ch, method, properties, body):
            if properties.correlation_id == correlation_id:
                responses[correlation_id] = json.loads(body)
                ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue=reply_queue, on_message_callback=on_response)

        # Publica el request
        channel.basic_publish(
            exchange=config.EXCHANGE_COMMANDS,
            routing_key=COMMAND_KEY,
            body=json.dumps({"loan_id": "L-1234"}),
            properties=pika.BasicProperties(
                content_type="application/json",
                correlation_id=correlation_id,
                reply_to=reply_queue,
            ),
        )

        # Espera la respuesta
        deadline = time.time() + TIMEOUT_SECONDS
        while correlation_id not in responses and time.time() < deadline:
            connection.process_data_events(time_limit=0.2)

        connection.close()
        stop_event.set()
        server_thread.join(timeout=2)

        if correlation_id not in responses:
            return False, f"no llegó respuesta en {TIMEOUT_SECONDS}s"
        response = responses[correlation_id]
        if response.get("loan_id") != "L-1234":
            return False, f"loan_id en respuesta inesperado: {response}"
        if "score" not in response:
            return False, f"respuesta no contiene score: {response}"

        return True, f"request-reply OK (score={response['score']})"
    except Exception as exc:  # noqa: BLE001
        stop_event.set()
        return False, f"{type(exc).__name__}: {exc}"


if __name__ == "__main__":
    ok, msg = run()
    print(f"[{TEST_NAME}] {'OK' if ok else 'FAIL'} — {msg}")
    sys.exit(0 if ok else 1)
