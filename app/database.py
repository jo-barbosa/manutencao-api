from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session

# Garante que a BD fica SEMPRE guardada na raiz do projeto, independentemente de onde executas o comando
BASE_DIR = Path(__file__).resolve().parent.parent
sqlite_file_name = BASE_DIR / "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session