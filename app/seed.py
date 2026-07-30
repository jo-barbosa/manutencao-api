from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.security import hash_password
from app.database import engine, create_db_and_tables
from app.models import (
    Fabrica, Linha, Sistema, Fornecedor, Superuser, Acao,
    EstadoSistema, StatusAcao, Impacto
)


def popular_base_de_dados():
    # 1. Garante que as tabelas existem na BD
    create_db_and_tables()

    with Session(engine) as session:
        # 2. Verifica se a BD já tem dados para evitar duplicados
        fabrica_existente = session.exec(select(Fabrica)).first()
        if fabrica_existente:
            print("⚠️ A base de dados já contém dados. Seed cancelado.")
            return

        print("🌱 A iniciar a população de dados de exemplo...")

        # ==========================================
        # A. FORNECEDORES
        # ==========================================
        fornecedor1 = Fornecedor(nome="Polishapes", contacto="joao.simoes@polishapes.com")
        fornecedor2 = Fornecedor(nome="Baumer", contacto="service@baumerinspection.com")
        fornecedor3 = Fornecedor(nome="Limab", contacto="jakob.nystrom@limab.se")

        session.add(fornecedor1)
        session.add(fornecedor2)
        session.add(fornecedor3)
        session.commit()  # Commit para gerar os IDs

        # ==========================================
        # B. SUPERUSERS / RESPONSÁVEIS
        # ==========================================
        user1 = Superuser(nome="Jorge Barbosa", email="jorge.barbosa@inter.ikea.com", password_hash=hash_password("dummy"))
        user2 = Superuser(nome="Hélder Vieira", email="helder.vieira@inter.ikea.com", password_hash=hash_password("dummy"))
        user3 = Superuser(nome="Hélio Machado", email="helio.machado1@inter.ikea.com", password_hash=hash_password("dummy"))

        session.add(user1)
        session.add(user2)
        session.add(user3)
        session.commit()

        # ==========================================
        # C. ESTRUTURA FABRIL (Fábrica -> Linha -> Sistema)
        # ==========================================

        # 1. Fábrica
        fabrica1 = Fabrica(nome="Pigment", localizacao="PFF")
        fabrica2 = Fabrica(nome="FOIL", localizacao="BOF")
        fabrica3 = Fabrica(nome="L&P", localizacao="BOF")
        session.add(fabrica1)
        session.add(fabrica2)
        session.add(fabrica3)
        session.commit()

        # 2. Linhas associadas à Fábrica
        linha1 = Linha(nome="Linha 1", fabrica_id=fabrica2.id)
        linha2 = Linha(nome="Linha 2", fabrica_id=fabrica2.id)
        linha3 = Linha(nome="Linha 3", fabrica_id=fabrica2.id)
        linha4 = Linha(nome="Linha 4", fabrica_id=fabrica2.id)
        session.add(linha1)
        session.add(linha2)
        session.add(linha3)
        session.add(linha4)
        session.commit()

        # 3. Sistemas associados às Linhas e Fornecedores
        sistema1 = Sistema(
            nome="Limab",
            estado_atual=EstadoSistema.OPERACIONAL,
            linha_id=linha1.id,
            fornecedor_id=fornecedor3.id
        )
        sistema2 = Sistema(
            nome="Baumer Inspection D12",
            estado_atual=EstadoSistema.OPERACIONAL,
            linha_id=linha2.id,
            fornecedor_id=fornecedor2.id
        )
        session.add(sistema1)
        session.add(sistema2)
        session.commit()

        # ==========================================
        # D. AÇÕES DE MANUTENÇÃO (Exemplos Iniciais)
        # ==========================================
        acao1 = Acao(
            comentario="Ação de teste",
            status=StatusAcao.ABERTA,
            impacto=Impacto.NENHUM,
            data_criacao=datetime.now(),
            data_prevista_conclusao=datetime.now() + timedelta(days=2),
            sistema_id=sistema1.id,
            responsavel_id=user1.id
        )

        acao2 = Acao(
            comentario="Ação de teste 2",
            status=StatusAcao.ABERTA,
            impacto=Impacto.NENHUM,
            data_criacao=datetime.now(),
            data_prevista_conclusao=datetime.now() + timedelta(hours=12),
            sistema_id=sistema2.id,
            responsavel_id=user1.id
        )


        session.add(acao1)
        session.add(acao2)
        session.commit()

        print("✅ Base de dados populada com sucesso!")


if __name__ == "__main__":
    popular_base_de_dados()