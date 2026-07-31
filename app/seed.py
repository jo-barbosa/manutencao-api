from datetime import timedelta, date
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
        #FOIL
        linha1 = Linha(nome="Linha 1", fabrica_id=fabrica2.id)
        linha2 = Linha(nome="Linha 2", fabrica_id=fabrica2.id)
        linha10 = Linha(nome="FSL", fabrica_id=fabrica2.id)
        linha11 = Linha(nome="Complete Line", fabrica_id=fabrica2.id)
        linha12 = Linha(nome="4Side", fabrica_id=fabrica2.id)
        session.add(linha1)
        session.add(linha2)
        session.add(linha10)
        session.add(linha11)
        session.add(linha12)
        #L&P
        linha5 = Linha(nome="Linha 1", fabrica_id=fabrica3.id)
        linha6 = Linha(nome="Linha 2", fabrica_id=fabrica3.id)
        linha7 = Linha(nome="Linha 3", fabrica_id=fabrica3.id)
        linha8 = Linha(nome="Masterframe", fabrica_id=fabrica3.id)
        linha9 = Linha(nome="Coldpress Auto", fabrica_id=fabrica3.id)
        session.add(linha5)
        session.add(linha6)
        session.add(linha7)
        session.add(linha8)
        session.add(linha9)
        #PFF - 12 linhas
        linha13 = Linha(nome="Linha 57-1", fabrica_id=fabrica1.id)
        linha14 = Linha(nome="Linha 57-2", fabrica_id=fabrica1.id)
        linha15 = Linha(nome="Linha 57-3", fabrica_id=fabrica1.id)
        linha16 = Linha(nome="Linha 58", fabrica_id=fabrica1.id)
        linha17 = Linha(nome="Linha 27", fabrica_id=fabrica1.id)
        linha18 = Linha(nome="Linha 22", fabrica_id=fabrica1.id)
        linha19 = Linha(nome="Linha 25", fabrica_id=fabrica1.id)
        linha20 = Linha(nome="Linha 21", fabrica_id=fabrica1.id)
        linha21 = Linha(nome="Linha 37", fabrica_id=fabrica1.id)
        linha22 = Linha(nome="Linha 52", fabrica_id=fabrica1.id)
        session.add(linha13)
        session.add(linha14)
        session.add(linha15)
        session.add(linha16)
        session.add(linha17)
        session.add(linha18)
        session.add(linha19)
        session.add(linha20)
        session.add(linha21)
        session.add(linha22)
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
        sistema3 = Sistema(
            nome="Polishapes",
            estado_atual=EstadoSistema.OPERACIONAL,
            linha_id=linha8.id,
            fornecedor_id=fornecedor1.id
        )
        sistema4 = Sistema(
            nome="Polishapes",
            estado_atual=EstadoSistema.OPERACIONAL,
            linha_id=linha9.id,
            fornecedor_id=fornecedor1.id
        )
        session.add(sistema1)
        session.add(sistema2)
        session.add(sistema3)
        session.add(sistema4)
        session.commit()



        print("✅ Base de dados populada com sucesso!")


if __name__ == "__main__":
    popular_base_de_dados()