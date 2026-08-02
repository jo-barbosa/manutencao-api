from datetime import date, timedelta
from sqlmodel import Session, select
from services.manutencao_service.database import engine
from services.manutencao_service.models import Acao, StatusAcao, Impacto

def bootstrap_manutencao_data():
    """Popula a base de dados do Manutencao-Service apenas se não existirem ações registadas."""
    with Session(engine) as session:
        existing = session.exec(select(Acao)).first()
        if existing:
            print("ℹ️ [Manutencao-Service Bootstrap] A base de dados já contém ações. Bootstrap ignorado.")
            return

        print("🌱 [Manutencao-Service Bootstrap] A popular ações de manutenção iniciais...")
        today = date.today()

        acoes = [
            Acao(
                descricao="Substituição preventiva dos rolamentos da Prensa Hidráulica H5",
                impacto=Impacto.TOTAL,
                status=StatusAcao.ABERTA,
                data_criacao=today - timedelta(days=2),
                data_prevista_conclusao=today + timedelta(days=5),
                sistema_id=2,
                responsavel_id=2
            ),
            Acao(
                descricao="Recalibração dos sensores ópticos do Braço Robótico de Paletização",
                impacto=Impacto.PARCIAL,
                status=StatusAcao.ABERTA,
                data_criacao=today - timedelta(days=1),
                data_prevista_conclusao=today + timedelta(days=3),
                sistema_id=3,
                responsavel_id=3
            ),
            Acao(
                descricao="Inspeção de rotina e atualização de firmware no Controlador PLC S7-1500",
                impacto=Impacto.NENHUM,
                status=StatusAcao.FECHADA,
                data_criacao=today - timedelta(days=10),
                data_prevista_conclusao=today - timedelta(days=4),
                data_conclusao=today - timedelta(days=4),
                comentario_fecho="Firmware v2.4 instalado e verificado com testes de bancada.",
                sistema_id=4,
                responsavel_id=1
            ),
            Acao(
                descricao="Limpeza e lubrificação da Inspeção D14",
                impacto=Impacto.NENHUM,
                status=StatusAcao.FECHADA,
                data_criacao=today - timedelta(days=15),
                data_prevista_conclusao=today - timedelta(days=7),
                data_conclusao=today - timedelta(days=7),
                comentario_fecho="Limpeza concluída e níveis de óleo repostos.",
                sistema_id=1,
                responsavel_id=4
            )
        ]

        session.add_all(acoes)
        session.commit()
        print("✅ [Manutencao-Service Bootstrap] Ações de manutenção criadas com sucesso!")
