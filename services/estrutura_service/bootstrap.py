from sqlmodel import Session, select
from services.estrutura_service.database import engine
from services.estrutura_service.models import Fabrica, Linha, Sistema, Fornecedor, EstadoSistema

def bootstrap_estrutura_data():
    """Popula a base de dados do Estrutura-Service apenas se não existirem fábricas registadas."""
    with Session(engine) as session:
        existing = session.exec(select(Fabrica)).first()
        if existing:
            print("ℹ️ [Estrutura-Service Bootstrap] A base de dados já contém a estrutura fabril. Bootstrap ignorado.")
            return

        print("🌱 [Estrutura-Service Bootstrap] A popular estrutura fabril inicial...")

        # 1. Criar Fábricas
        f1 = Fabrica(nome="PIGMENT", localizacao="PFF / BOF")
        f2 = Fabrica(nome="NORDIC", localizacao="Linha Seca")
        f3 = Fabrica(nome="PACOS_1", localizacao="Pavilhão Principal")
        session.add_all([f1, f2, f3])
        session.commit()
        for f in [f1, f2, f3]:
            session.refresh(f)

        # 2. Criar Linhas
        l1 = Linha(nome="Linha 1", fabrica_id=f1.id)
        l2 = Linha(nome="Linha 2", fabrica_id=f1.id)
        l3 = Linha(nome="Linha Seca 1", fabrica_id=f2.id)
        l4 = Linha(nome="Linha de Embalamento", fabrica_id=f3.id)
        session.add_all([l1, l2, l3, l4])
        session.commit()
        for l in [l1, l2, l3, l4]:
            session.refresh(l)

        # 3. Criar Fornecedores
        forn1 = Fornecedor(nome="Baumer Inspection", contacto="suporte@baumer.com")
        forn2 = Fornecedor(nome="Siemens Automation", contacto="contacto@siemens.com")
        forn3 = Fornecedor(nome="ABB Robotics", contacto="suporte.pt@abb.com")
        forn4 = Fornecedor(nome="Bosch Rexroth", contacto="assistencia@boschrexroth.pt")
        session.add_all([forn1, forn2, forn3, forn4])
        session.commit()
        for forn in [forn1, forn2, forn3, forn4]:
            session.refresh(forn)

        # 4. Criar Sistemas
        s1 = Sistema(nome="Inspeção D14", estado_atual=EstadoSistema.OPERACIONAL, linha_id=l1.id, fornecedor_id=forn1.id)
        s2 = Sistema(nome="Prensa Hidráulica H5", estado_atual=EstadoSistema.PARADO, linha_id=l1.id, fornecedor_id=forn4.id)
        s3 = Sistema(nome="Braço Robótico de Paletização", estado_atual=EstadoSistema.DEGRADADO, linha_id=l2.id, fornecedor_id=forn3.id)
        s4 = Sistema(nome="Controlador PLC S7-1500", estado_atual=EstadoSistema.OPERACIONAL, linha_id=l3.id, fornecedor_id=forn2.id)
        s5 = Sistema(nome="Empacotadora Automática", estado_atual=EstadoSistema.OPERACIONAL, linha_id=l4.id, fornecedor_id=forn2.id)

        session.add_all([s1, s2, s3, s4, s5])
        session.commit()

        print("✅ [Estrutura-Service Bootstrap] Estrutura fabril criada com sucesso!")
