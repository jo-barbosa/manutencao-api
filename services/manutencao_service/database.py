import os
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.getenv("MANUTENCAO_DATABASE_URL", "sqlite:///./data/manutencao.db")

if "sqlite" in DATABASE_URL and "///" in DATABASE_URL:
    db_path = DATABASE_URL.split("///")[-1]
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
