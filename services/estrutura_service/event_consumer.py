import os
import json
import asyncio
import threading
import time
import pika
from sqlmodel import Session
from services.estrutura_service.database import engine
from services.estrutura_service.models import Sistema, EstadoSistema

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
EXCHANGE_NAME = "manutencao_events"
QUEUE_NAME = "estrutura_status_queue"

def recalcular_estado_sistema_do_evento(sistema_id: int, novo_estado: str):
    """Atualiza o estado do sistema com base no evento de manutenção recebido via RabbitMQ."""
    with Session(engine) as session:
        sistema = session.get(Sistema, sistema_id)
        if sistema:
            if novo_estado in EstadoSistema.__members__:
                sistema.estado_atual = EstadoSistema[novo_estado]
            else:
                sistema.estado_atual = EstadoSistema.OPERACIONAL
            session.add(sistema)
            session.commit()
            print(f"🔄 [RabbitMQ Consumer] Estado do Sistema #{sistema_id} atualizado para {sistema.estado_atual}")

def callback(ch, method, properties, body):
    try:
        data = json.loads(body.decode("utf-8"))
        print(f"📥 [RabbitMQ Consumer] Evento recebido [{method.routing_key}]: {data}")
        sistema_id = data.get("sistema_id")
        novo_estado = data.get("estado_calculado", "OPERACIONAL")
        if sistema_id:
            recalcular_estado_sistema_do_evento(sistema_id, novo_estado)
    except Exception as e:
        print(f"❌ Error processing RabbitMQ message: {e}")

def start_rabbitmq_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=600, blocked_connection_timeout=300)
            )
            channel = connection.channel()
            channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
            channel.queue_declare(queue=QUEUE_NAME, durable=True)

            for routing_key in ["acao.criada", "acao.atualizada", "acao.fechada"]:
                channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=routing_key)

            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
            print(f"🐰 [RabbitMQ Consumer] A aguardar eventos em {RABBITMQ_HOST}...")
            channel.start_consuming()
        except Exception as e:
            print(f"⚠️ [RabbitMQ Consumer] Conexão falhou ({e}), tentando novamente em 5s...")
            time.sleep(5)

def run_consumer_in_background():
    thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    thread.start()
