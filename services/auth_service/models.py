from typing import Optional, List
from sqlmodel import SQLModel, Field

class Superuser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    email: str = Field(unique=True, index=True)
    password_hash: str
