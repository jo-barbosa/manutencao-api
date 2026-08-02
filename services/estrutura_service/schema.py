from typing import List, Optional
import strawberry
from sqlmodel import Session, select
from services.estrutura_service.database import engine
from services.estrutura_service.models import Fabrica, Linha, Sistema, Fornecedor, EstadoSistema

@strawberry.type
class FornecedorType:
    id: int
    nome: str
    contacto: Optional[str] = None

@strawberry.type
class FabricaType:
    id: int
    nome: str
    localizacao: Optional[str] = None

@strawberry.type
class LinhaType:
    id: int
    nome: str
    fabrica_id: Optional[int] = None
    fabrica_nome: Optional[str] = None

@strawberry.type
class SistemaStatusType:
    id: int
    nome_sistema: str
    estado: str
    linha: str
    fabrica: str
    fornecedor: str

@strawberry.type
class SistemaType:
    id: int
    nome: str
    estado_atual: str
    linha_id: Optional[int] = None
    fornecedor_id: Optional[int] = None

@strawberry.type
class Query:
    @strawberry.field
    def fabricas(self) -> List[FabricaType]:
        with Session(engine) as session:
            fabs = session.exec(select(Fabrica)).all()
            return [FabricaType(id=f.id, nome=f.nome, localizacao=f.localizacao) for f in fabs]

    @strawberry.field
    def linhas(self, fabrica_id: Optional[int] = None) -> List[LinhaType]:
        with Session(engine) as session:
            stmt = select(Linha)
            if fabrica_id:
                stmt = stmt.where(Linha.fabrica_id == fabrica_id)
            linhas = session.exec(stmt).all()
            return [
                LinhaType(
                    id=l.id,
                    nome=l.nome,
                    fabrica_id=l.fabrica_id,
                    fabrica_nome=l.fabrica.nome if l.fabrica else "N/A"
                )
                for l in linhas
            ]

    @strawberry.field
    def sistemas(self, linha_id: Optional[int] = None) -> List[SistemaType]:
        with Session(engine) as session:
            stmt = select(Sistema)
            if linha_id:
                stmt = stmt.where(Sistema.linha_id == linha_id)
            sistemas = session.exec(stmt).all()
            return [
                SistemaType(
                    id=s.id,
                    nome=s.nome,
                    estado_atual=s.estado_atual.value if hasattr(s.estado_atual, 'value') else str(s.estado_atual),
                    linha_id=s.linha_id,
                    fornecedor_id=s.fornecedor_id
                )
                for s in sistemas
            ]

    @strawberry.field
    def sistemas_status(self) -> List[SistemaStatusType]:
        with Session(engine) as session:
            sistemas = session.exec(select(Sistema)).all()
            resultado = []
            for s in sistemas:
                resultado.append(SistemaStatusType(
                    id=s.id,
                    nome_sistema=s.nome,
                    estado=s.estado_atual.value if hasattr(s.estado_atual, 'value') else str(s.estado_atual),
                    linha=s.linha.nome if s.linha else "N/A",
                    fabrica=s.linha.fabrica.nome if s.linha and s.linha.fabrica else "N/A",
                    fornecedor=s.fornecedor.nome if s.fornecedor else "N/A"
                ))
            return resultado

    @strawberry.field
    def fornecedores(self) -> List[FornecedorType]:
        with Session(engine) as session:
            forns = session.exec(select(Fornecedor)).all()
            return [FornecedorType(id=f.id, nome=f.nome, contacto=f.contacto) for f in forns]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def criar_fabrica(self, nome: str, localizacao: Optional[str] = None) -> FabricaType:
        with Session(engine) as session:
            fab = Fabrica(nome=nome, localizacao=localizacao)
            session.add(fab)
            session.commit()
            session.refresh(fab)
            return FabricaType(id=fab.id, nome=fab.nome, localizacao=fab.localizacao)

    @strawberry.mutation
    def criar_linha(self, nome: str, fabrica_id: int) -> LinhaType:
        with Session(engine) as session:
            linha = Linha(nome=nome, fabrica_id=fabrica_id)
            session.add(linha)
            session.commit()
            session.refresh(linha)
            return LinhaType(id=linha.id, nome=linha.nome, fabrica_id=linha.fabrica_id)

    @strawberry.mutation
    def criar_sistema(self, nome: str, linha_id: int, fornecedor_id: Optional[int] = None) -> SistemaType:
        with Session(engine) as session:
            sis = Sistema(nome=nome, linha_id=linha_id, fornecedor_id=fornecedor_id)
            session.add(sis)
            session.commit()
            session.refresh(sis)
            return SistemaType(
                id=sis.id,
                nome=sis.nome,
                estado_atual=sis.estado_atual.value if hasattr(sis.estado_atual, 'value') else str(sis.estado_atual),
                linha_id=sis.linha_id,
                fornecedor_id=sis.fornecedor_id
            )

    @strawberry.mutation
    def criar_fornecedor(self, nome: str, contacto: Optional[str] = None) -> FornecedorType:
        with Session(engine) as session:
            forn = Fornecedor(nome=nome, contacto=contacto)
            session.add(forn)
            session.commit()
            session.refresh(forn)
            return FornecedorType(id=forn.id, nome=forn.nome, contacto=forn.contacto)

    @strawberry.mutation
    def editar_fornecedor(self, id: int, nome: str, contacto: Optional[str] = None) -> Optional[FornecedorType]:
        with Session(engine) as session:
            forn = session.get(Fornecedor, id)
            if not forn:
                return None
            forn.nome = nome
            forn.contacto = contacto
            session.add(forn)
            session.commit()
            session.refresh(forn)
            return FornecedorType(id=forn.id, nome=forn.nome, contacto=forn.contacto)

schema = strawberry.Schema(query=Query, mutation=Mutation)
