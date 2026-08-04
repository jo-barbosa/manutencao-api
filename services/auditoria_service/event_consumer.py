import os
import json
import time
import threading
import pika
from datetime import datetime
from sqlmodel import Session
from services.auditoria_service.database import engine
from services.auditoria_service.models import RegistoAuditoria

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
EXCHANGE_NAME = "manutencao_events"

def processar_mensagem(ch, method, properties, body):
    try:
        data = json.loads(body.decode('utf-8'))
        routing_key = method.routing_key
        print(f"📥 [Auditoria Consumer] Evento recebido [{routing_key}]: {data}")

        user_email = data.get("utilizador_email") or data.get("user_email") or "Sistema / Operador"

        if routing_key == "acao.criada":
            acao_realizada = "CRIAR_ACAO"
            detalhes = f"Ação ID #{data.get('acao_id')} criada para Sistema #{data.get('sistema_id')} ('{data.get('descricao')}', Impacto: {data.get('impacto')})"
        elif routing_key == "acao.fechada":
            acao_realizada = "FECHAR_ACAO"
            detalhes = f"Ação ID #{data.get('acao_id')} encerrada. Comentário: '{data.get('comentario_fecho', 'Sem comentário')}'"
        elif routing_key == "acao.atualizada":
            acao_realizada = "EDITAR_ACAO"
            detalhes = f"Ação ID #{data.get('acao_id')} atualizada ('{data.get('descricao')}', Status: {data.get('status')})"
        else:
            acao_realizada = data.get("acao_realizada", routing_key.upper().replace(".", "_"))
            detalhes = data.get("detalhes", str(data))

        timestamp_raw = data.get("timestamp")
        dt = datetime.fromisoformat(timestamp_raw) if timestamp_raw else datetime.now()

        log = RegistoAuditoria(
            utilizador_email=user_email,
            acao_realizada=acao_realizada,
            detalhes=detalhes,
            timestamp=dt
        )

        with Session(engine) as session:
            session.add(log)
            session.commit()
            print(f"💾 [Auditoria Consumer] Log registado com sucesso (ID #{log.id})")

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"❌ Erro ao guardar registo de auditoria: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_rabbitmq_consumer():
    max_retries = int(os.getenv("RABBITMQ_MAX_RETRIES", "5"))
    retry_delay = int(os.getenv("RABBITMQ_RETRY_DELAY", "5"))
    retry_count = 0

    while retry_count < max_retries:
        try:
            retry_count += 1
            print(f"🔄 [Auditoria Consumer] Tentativa de conexão a '{RABBITMQ_HOST}' ({retry_count}/{max_retries})...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=600, blocked_connection_timeout=300)
            )
            channel = connection.channel()
            channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)

            result = channel.queue_declare(queue='auditoria_queue', durable=True)
            queue_name = result.method.queue
            channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key='#')

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=queue_name, on_message_callback=processar_mensagem)

            print(f"🐰 [Auditoria Consumer] Conectado e a aguardar eventos em '{RABBITMQ_HOST}'...")
            channel.start_consuming()
        except Exception as e:
            print(f"⚠️ [Auditoria Consumer] Conexão a '{RABBITMQ_HOST}' falhou ({retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                time.sleep(retry_delay)
            else:
                print(f"🛑 [Auditoria Consumer] Limite de tentativas atingido. Modo offline ativado.")

def start_auditoria_consumer_thread():
    thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    thread.start()
