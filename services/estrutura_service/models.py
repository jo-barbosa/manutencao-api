from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class EstadoSistema(str, Enum):
    OPERACIONAL = "OPERACIONAL"
    DEGRADADO = "DEGRADADO"
    PARADO = "PARADO"

class Fornecedor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    contacto: Optional[str] = None
    sistemas: List["Sistema"] = Relationship(back_populates="fornecedor")

class Fabrica(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    localizacao: Optional[str] = None
    linhas: List["Linha"] = Relationship(back_populates="fabrica")

class Linha(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    fabrica_id: Optional[int] = Field(default=None, foreign_key="fabrica.id")
    fabrica: Optional[Fabrica] = Relationship(back_populates="linhas")
    sistemas: List["Sistema"] = Relationship(back_populates="linha")

class Sistema(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    estado_atual: EstadoSistema = Field(default=EstadoSistema.OPERACIONAL)
    linha_id: Optional[int] = Field(default=None, foreign_key="linha.id")
    linha: Optional[Linha] = Relationship(back_populates="sistemas")
    fornecedor_id: Optional[int] = Field(default=None, foreign_key="fornecedor.id")
    fornecedor: Optional[Fornecedor] = Relationship(back_populates="sistemas")
