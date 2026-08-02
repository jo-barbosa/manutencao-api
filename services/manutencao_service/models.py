from datetime import date
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field

class StatusAcao(str, Enum):
    ABERTA = "ABERTA"
    FECHADA = "FECHADA"

class Impacto(str, Enum):
    TOTAL = "TOTAL"
    PARCIAL = "PARCIAL"
    NENHUM = "NENHUM"

class Acao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    descricao: str
    status: StatusAcao = Field(default=StatusAcao.ABERTA)
    impacto: Impacto = Field(default=Impacto.NENHUM)
    data_criacao: date = Field(default_factory=date.today)
    data_prevista_conclusao: Optional[date] = None
    data_conclusao: Optional[date] = None
    comentario_fecho: Optional[str] = None
    sistema_id: Optional[int] = None
    responsavel_id: Optional[int] = None
