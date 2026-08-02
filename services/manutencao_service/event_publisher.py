import os
import json
import pika
from sqlmodel import Session, select
from services.manutencao_service.database import engine
from services.manutencao_service.models import Acao, StatusAcao, Impacto

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
EXCHANGE_NAME = "manutencao_events"

def calcular_estado_sistema(sistema_id: int) -> str:
    """Calcula o estado derivado das ações abertas para determinado sistema."""
    with Session(engine) as session:
        acoes_abertas = session.exec(
            select(Acao).where(Acao.sistema_id == sistema_id, Acao.status == StatusAcao.ABERTA)
        ).all()
        if any(a.impacto == Impacto.TOTAL for a in acoes_abertas):
            return "PARADO"
        elif any(a.impacto == Impacto.PARCIAL for a in acoes_abertas):
            return "DEGRADADO"
        return "OPERACIONAL"

def publicar_evento_manutencao(routing_key: str, acao: Acao):
    """Publica um evento em RabbitMQ sobre a alteração de uma Ação de Manutenção."""
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=600, blocked_connection_timeout=300)
        )
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)

        estado_calculado = calcular_estado_sistema(acao.sistema_id) if acao.sistema_id else "OPERACIONAL"

        payload = {
            "acao_id": acao.id,
            "descricao": acao.descricao,
            "status": acao.status.value if hasattr(acao.status, 'value') else str(acao.status),
            "impacto": acao.impacto.value if hasattr(acao.impacto, 'value') else str(acao.impacto),
            "sistema_id": acao.sistema_id,
            "responsavel_id": acao.responsavel_id,
            "estado_calculado": estado_calculado
        }

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(
                delivery_mode=2,  # faz a mensagem persistente
                content_type='application/json'
            )
        )
        print(f"📤 [RabbitMQ Publisher] Evento publicado [{routing_key}]: {payload}")
        connection.close()
    except Exception as e:
        print(f"⚠️ [RabbitMQ Publisher] Não foi possível enviar mensagem para o RabbitMQ ({e})")
