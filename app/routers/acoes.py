from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Acao, Sistema, EstadoSistema, Impacto, RegistoAuditoria, Superuser
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/acoes", tags=["Ações de Manutenção"])


@router.get("", response_model=List[Acao])
def listar_acoes(session: Session = Depends(get_session)):
    return session.exec(select(Acao)).all()


@router.post("", response_model=Acao)
def criar_acao(
    acao: Acao,
    session: Session = Depends(get_session),
    current_user: Superuser = Depends(get_current_user)  # 👈 Exige login e descobre quem é o operador
):
    sistema = session.get(Sistema, acao.sistema_id)
    if not sistema:
        raise HTTPException(status_code=404, detail="Sistema não encontrado")

    # 1. Aplica regra de impacto no sistema
    if acao.impacto == Impacto.TOTAL:
        sistema.estado_atual = EstadoSistema.PARADO
    elif acao.impacto == Impacto.PARCIAL:
        sistema.estado_atual = EstadoSistema.DEGRADADO
    elif acao.impacto == Impacto.NENHUM:
        sistema.estado_atual = EstadoSistema.OPERACIONAL

    # Associar o responsável atual à ação
    acao.responsavel_id = current_user.id

    # 2. Criar o Registo de Auditoria
    log = RegistoAuditoria(
        utilizador_email=current_user.email,
        acao_realizada="CRIAR_ACAO",
        detalhes=f"Ação criada para o sistema '{sistema.nome}' (Impacto: {acao.impacto.value})"
    )

    session.add(acao)
    session.add(sistema)
    session.add(log)
    session.commit()
    session.refresh(acao)

    return acao