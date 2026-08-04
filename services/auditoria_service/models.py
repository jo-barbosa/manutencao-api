from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class RegistoAuditoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    utilizador_email: str
    acao_realizada: str
    detalhes: str
    timestamp: datetime = Field(default_factory=datetime.now)
