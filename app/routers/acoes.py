from typing import List, Optional
from datetime import date  # 👈 Importante para a conversão de datas
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, SQLModel
from app.database import get_session
from app.models import Acao, Sistema, EstadoSistema, Impacto, RegistoAuditoria, Superuser
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/acoes", tags=["Ações de Manutenção"])


# 1. Schema específico para a criação da Ação
class AcaoCreate(SQLModel):
    descricao: str
    impacto: Impacto
    sistema_id: int
    data_prevista_conclusao: Optional[date] = None  # 👈 Garante que o Pydantic converte a string 'YYYY-MM-DD' em date


@router.get("", response_model=List[Acao])
def listar_acoes(session: Session = Depends(get_session)):
    return session.exec(select(Acao)).all()


@router.post("", response_model=Acao)
def criar_acao(
    acao_in: AcaoCreate,  # 👈 Recebe o schema de criação
    session: Session = Depends(get_session),
    current_user: Superuser = Depends(get_current_user)
):
    sistema = session.get(Sistema, acao_in.sistema_id)
    if not sistema:
        raise HTTPException(status_code=404, detail="Sistema não encontrado")

    # 2. Aplica regra de impacto no sistema
    if acao_in.impacto == Impacto.TOTAL:
        sistema.estado_atual = EstadoSistema.PARADO
    elif acao_in.impacto == Impacto.PARCIAL:
        sistema.estado_atual = EstadoSistema.DEGRADADO
    elif acao_in.impacto == Impacto.NENHUM:
        sistema.estado_atual = EstadoSistema.OPERACIONAL

    # 3. Transforma o schema no modelo de base de dados (Acao) e injeta o responsavel_id
    acao = Acao.model_validate(
        acao_in,
        update={"responsavel_id": current_user.id}
    )

    # 4. Criar o Registo de Auditoria
    log = RegistoAuditoria(
        utilizador_email=current_user.email,
        acao_realizada="CRIAR_ACAO",
        detalhes=f"Ação criada para o sistema '{sistema.nome}' (Impacto: {acao.impacto})"
    )

    session.add(acao)
    session.add(sistema)
    session.add(log)
    session.commit()
    session.refresh(acao)

    return acao