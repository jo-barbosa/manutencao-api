import os
from pathlib import Path
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_URL = f"sqlite:///{BASE_DIR / 'database.db'}"

# Obtém a URL da BD a partir de variáveis de ambiente (.env ou Docker)
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

# Normaliza URL do PostgreSQL para SQLAlchemy (postgres:// -> postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configuração condicional consoante o SGBD
is_sqlite = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

# Criar Engine da Base de Dados
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)


def create_db_and_tables():
    """Cria todas as tabelas na BD se ainda não existirem."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Injeta a sessão de base de dados para os endpoints FastAPI."""
    with Session(engine) as session:
        yield session