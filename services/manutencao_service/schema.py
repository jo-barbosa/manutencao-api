from datetime import date
from typing import List, Optional
import strawberry
from sqlmodel import Session, select
from services.manutencao_service.database import engine
from services.manutencao_service.models import Acao, StatusAcao, Impacto
from services.manutencao_service.event_publisher import publicar_evento_manutencao

@strawberry.type
class AcaoType:
    id: int
    descricao: str
    status: str
    impacto: str
    data_criacao: str
    data_prevista_conclusao: Optional[str] = None
    data_conclusao: Optional[str] = None
    comentario_fecho: Optional[str] = None
    sistema_id: Optional[int] = None
    responsavel_id: Optional[int] = None

@strawberry.type
class Query:
    @strawberry.field
    def acoes(
        self,
        sistema_id: Optional[int] = None,
        status: Optional[str] = None,
        responsavel_id: Optional[int] = None
    ) -> List[AcaoType]:
        with Session(engine) as session:
            stmt = select(Acao)
            if sistema_id is not None:
                stmt = stmt.where(Acao.sistema_id == sistema_id)
            if status is not None and status != "TODAS":
                stmt = stmt.where(Acao.status == status)
            if responsavel_id is not None:
                stmt = stmt.where(Acao.responsavel_id == responsavel_id)

            lista = session.exec(stmt).all()
            return [
                AcaoType(
                    id=a.id,
                    descricao=a.descricao,
                    status=a.status.value if hasattr(a.status, 'value') else str(a.status),
                    impacto=a.impacto.value if hasattr(a.impacto, 'value') else str(a.impacto),
                    data_criacao=str(a.data_criacao) if a.data_criacao else "",
                    data_prevista_conclusao=str(a.data_prevista_conclusao) if a.data_prevista_conclusao else None,
                    data_conclusao=str(a.data_conclusao) if a.data_conclusao else None,
                    comentario_fecho=a.comentario_fecho,
                    sistema_id=a.sistema_id,
                    responsavel_id=a.responsavel_id
                )
                for a in lista
            ]

    @strawberry.field
    def acao_por_id(self, id: int) -> Optional[AcaoType]:
        with Session(engine) as session:
            a = session.get(Acao, id)
            if not a:
                return None
            return AcaoType(
                id=a.id,
                descricao=a.descricao,
                status=a.status.value if hasattr(a.status, 'value') else str(a.status),
                impacto=a.impacto.value if hasattr(a.impacto, 'value') else str(a.impacto),
                data_criacao=str(a.data_criacao) if a.data_criacao else "",
                data_prevista_conclusao=str(a.data_prevista_conclusao) if a.data_prevista_conclusao else None,
                data_conclusao=str(a.data_conclusao) if a.data_conclusao else None,
                comentario_fecho=a.comentario_fecho,
                sistema_id=a.sistema_id,
                responsavel_id=a.responsavel_id
            )

@strawberry.type
class Mutation:
    @strawberry.mutation
    def criar_acao(
        self,
        descricao: str,
        impacto: str,
        sistema_id: int,
        responsavel_id: Optional[int] = None,
        data_prevista_conclusao: Optional[str] = None
    ) -> AcaoType:
        with Session(engine) as session:
            dt_prev = date.fromisoformat(data_prevista_conclusao) if data_prevista_conclusao else None
            imp_enum = Impacto[impacto] if impacto in Impacto.__members__ else Impacto.NENHUM
            
            acao = Acao(
                descricao=descricao,
                impacto=imp_enum,
                sistema_id=sistema_id,
                responsavel_id=responsavel_id,
                data_prevista_conclusao=dt_prev,
                status=StatusAcao.ABERTA
            )
            session.add(acao)
            session.commit()
            session.refresh(acao)

            publicar_evento_manutencao("acao.criada", acao)

            return AcaoType(
                id=acao.id,
                descricao=acao.descricao,
                status=acao.status.value if hasattr(acao.status, 'value') else str(acao.status),
                impacto=acao.impacto.value if hasattr(acao.impacto, 'value') else str(acao.impacto),
                data_criacao=str(acao.data_criacao),
                data_prevista_conclusao=str(acao.data_prevista_conclusao) if acao.data_prevista_conclusao else None,
                sistema_id=acao.sistema_id,
                responsavel_id=acao.responsavel_id
            )

    @strawberry.mutation
    def fechar_acao(
        self,
        id: int,
        data_conclusao: Optional[str] = None,
        comentario: Optional[str] = None
    ) -> Optional[AcaoType]:
        with Session(engine) as session:
            acao = session.get(Acao, id)
            if not acao:
                return None
            
            acao.status = StatusAcao.FECHADA
            acao.data_conclusao = date.fromisoformat(data_conclusao) if data_conclusao else date.today()
            if comentario:
                acao.comentario_fecho = comentario

            session.add(acao)
            session.commit()
            session.refresh(acao)

            publicar_evento_manutencao("acao.fechada", acao)

            return AcaoType(
                id=acao.id,
                descricao=acao.descricao,
                status=acao.status.value if hasattr(acao.status, 'value') else str(acao.status),
                impacto=acao.impacto.value if hasattr(acao.impacto, 'value') else str(acao.impacto),
                data_criacao=str(acao.data_criacao),
                data_prevista_conclusao=str(acao.data_prevista_conclusao) if acao.data_prevista_conclusao else None,
                data_conclusao=str(acao.data_conclusao) if acao.data_conclusao else None,
                comentario_fecho=acao.comentario_fecho,
                sistema_id=acao.sistema_id,
                responsavel_id=acao.responsavel_id
            )

    @strawberry.mutation
    def editar_acao(
        self,
        id: int,
        descricao: Optional[str] = None,
        impacto: Optional[str] = None,
        status: Optional[str] = None,
        data_prevista_conclusao: Optional[str] = None
    ) -> Optional[AcaoType]:
        with Session(engine) as session:
            acao = session.get(Acao, id)
            if not acao:
                return None
            if descricao:
                acao.descricao = descricao
            if impacto and impacto in Impacto.__members__:
                acao.impacto = Impacto[impacto]
            if status and status in StatusAcao.__members__:
                acao.status = StatusAcao[status]
            if data_prevista_conclusao:
                acao.data_prevista_conclusao = date.fromisoformat(data_prevista_conclusao)

            session.add(acao)
            session.commit()
            session.refresh(acao)

            publicar_evento_manutencao("acao.atualizada", acao)

            return AcaoType(
                id=acao.id,
                descricao=acao.descricao,
                status=acao.status.value if hasattr(acao.status, 'value') else str(acao.status),
                impacto=acao.impacto.value if hasattr(acao.impacto, 'value') else str(acao.impacto),
                data_criacao=str(acao.data_criacao),
                data_prevista_conclusao=str(acao.data_prevista_conclusao) if acao.data_prevista_conclusao else None,
                data_conclusao=str(acao.data_conclusao) if acao.data_conclusao else None,
                comentario_fecho=acao.comentario_fecho,
                sistema_id=acao.sistema_id,
                responsavel_id=acao.responsavel_id
            )

schema = strawberry.Schema(query=Query, mutation=Mutation)
