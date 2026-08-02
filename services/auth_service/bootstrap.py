from sqlmodel import Session, select
from services.auth_service.database import engine
from services.auth_service.models import Superuser
from services.auth_service.security import get_password_hash

def bootstrap_auth_data():
    """Popula a base de dados do Auth-Service apenas se não existirem utilizadores registados."""
    with Session(engine) as session:
        existing = session.exec(select(Superuser)).first()
        if existing:
            print("ℹ️ [Auth-Service Bootstrap] A base de dados já contém utilizadores. Bootstrap ignorado.")
            return

        print("🌱 [Auth-Service Bootstrap] A popular utilizadores iniciais...")
        users = [
            Superuser(
                nome="Administrador Principal",
                email="admin@empresa.com",
                password_hash=get_password_hash("admin123")
            ),
            Superuser(
                nome="Jorge Barbosa",
                email="jorge.barbosa@inter.ikea.com",
                password_hash=get_password_hash("dummy")
            ),
            Superuser(
                nome="João Silva",
                email="joao.silva@empresa.com",
                password_hash=get_password_hash("senha123")
            ),
            Superuser(
                nome="Maria Santos",
                email="maria.santos@empresa.com",
                password_hash=get_password_hash("senha123")
            ),
            Superuser(
                nome="Pedro Almeida",
                email="pedro.almeida@empresa.com",
                password_hash=get_password_hash("senha123")
            )
        ]
        session.add_all(users)
        session.commit()
        print("✅ [Auth-Service Bootstrap] Utilizadores criados com sucesso!")
