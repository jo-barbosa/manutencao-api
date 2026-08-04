from typing import List
import strawberry
from sqlmodel import Session, select
from services.auditoria_service.database import engine
from services.auditoria_service.models import RegistoAuditoria

@strawberry.type
class RegistoAuditoriaType:
    id: int
    utilizador_email: str
    acao_realizada: str
    detalhes: str
    timestamp: str

@strawberry.type
class Query:
    @strawberry.field
    def auditoria(self) -> List[RegistoAuditoriaType]:
        with Session(engine) as session:
            stmt = select(RegistoAuditoria).order_by(RegistoAuditoria.timestamp.desc())
            registos = session.exec(stmt).all()
            return [
                RegistoAuditoriaType(
                    id=r.id,
                    utilizador_email=r.utilizador_email,
                    acao_realizada=r.acao_realizada,
                    detalhes=r.detalhes,
                    timestamp=r.timestamp.isoformat() if r.timestamp else ""
                )
                for r in registos
            ]

schema = strawberry.Schema(query=Query)
