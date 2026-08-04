import os
from sqlmodel import SQLModel, create_engine

DATABASE_URL = os.getenv("AUDITORIA_DATABASE_URL", "sqlite:///./data/auditoria.db")

if "sqlite" in DATABASE_URL and "///" in DATABASE_URL:
    db_path = DATABASE_URL.split("///")[-1]
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

def init_db():
    SQLModel.metadata.create_all(engine)
