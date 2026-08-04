from datetime import datetime, timedelta
from sqlmodel import Session, select
from services.auditoria_service.database import engine
from services.auditoria_service.models import RegistoAuditoria

def bootstrap_auditoria_data():
    with Session(engine) as session:
        count = session.exec(select(RegistoAuditoria)).first()
        if not count:
            now = datetime.now()
            logs = [
                RegistoAuditoria(
                    utilizador_email="jorge.barbosa@inter.ikea.com",
                    acao_realizada="BOOTSTRAP_SISTEMA",
                    detalhes="Inicialização da infraestrutura de auditoria em microserviços",
                    timestamp=now - timedelta(hours=2)
                ),
                RegistoAuditoria(
                    utilizador_email="jorge.barbosa@inter.ikea.com",
                    acao_realizada="CRIAR_FABRICA",
                    detalhes="Fábrica 'IKEA Paços de Ferreira' configurada na plataforma",
                    timestamp=now - timedelta(hours=1, minutes=45)
                ),
                RegistoAuditoria(
                    utilizador_email="helder.vieira@inter.ikea.com",
                    acao_realizada="CRIAR_ACAO",
                    detalhes="Ação ID #1 criada para Cortadora CNC (Impacto: PARCIAL)",
                    timestamp=now - timedelta(minutes=30)
                )
            ]
            session.add_all(logs)
            session.commit()
            print("📜 [Auditoria-Service] Povoamento inicial de registos de auditoria efetuado.")
