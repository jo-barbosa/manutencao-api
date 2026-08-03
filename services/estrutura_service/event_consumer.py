import os
import json
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
        print(f"❌ Erro ao processar mensagem RabbitMQ: {e}")

def start_rabbitmq_consumer():
    """Tenta conectar ao RabbitMQ até um número máximo de vezes (MAX_RETRIES). Se falhar, para de tentar."""
    max_retries = int(os.getenv("RABBITMQ_MAX_RETRIES", "5"))
    retry_count = 0
    retry_interval = 3  # segundos entre tentativas

    while retry_count < max_retries:
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
            print(f"🐰 [RabbitMQ Consumer] Conectado e a aguardar eventos em '{RABBITMQ_HOST}'...")
            retry_count = 0  # Reseta o contador se a conexão for bem-sucedida
            channel.start_consuming()
        except Exception as e:
            retry_count += 1
            print(f"⚠️ [RabbitMQ Consumer] Conexão a '{RABBITMQ_HOST}' falhou ({retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                time.sleep(retry_interval)
            else:
                print(f"🛑 [RabbitMQ Consumer] Atingido o limite máximo de {max_retries} tentativas. Modo offline ativado (RabbitMQ desativado).")
                break

def run_consumer_in_background():
    thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    thread.start()
