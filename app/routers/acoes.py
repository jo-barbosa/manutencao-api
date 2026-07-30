from typing import List, Optional
from datetime import date  # 👈 Importante para a conversão de datas
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, SQLModel
from app.database import get_session
from app.models import Acao, Sistema, EstadoSistema, Impacto, StatusAcao, RegistoAuditoria, Superuser
from app.routers.auth import get_current_user


router = APIRouter(prefix="/api/acoes", tags=["Ações de Manutenção"])


# 1. Schemas para Ações
class AcaoCreate(SQLModel):
    descricao: str
    impacto: Impacto
    sistema_id: int
    data_prevista_conclusao: Optional[date] = None


class AcaoUpdate(SQLModel):
    descricao: Optional[str] = None
    impacto: Optional[Impacto] = None
    sistema_id: Optional[int] = None
    responsavel_id: Optional[int] = None
    data_prevista_conclusao: Optional[date] = None
    status: Optional[StatusAcao] = None


class AcaoFechar(SQLModel):
    data_conclusao: Optional[date] = None
    comentario: Optional[str] = None


def recalcular_estado_sistema(session: Session, sistema_id: int):
    """Recalcula o estado do sistema com base nas ações de manutenção atualmente ABERTAS."""
    sistema = session.get(Sistema, sistema_id)
    if not sistema:
        return

    acoes_abertas = session.exec(
        select(Acao).where(Acao.sistema_id == sistema_id, Acao.status == StatusAcao.ABERTA)
    ).all()

    if any(a.impacto == Impacto.TOTAL for a in acoes_abertas):
        sistema.estado_atual = EstadoSistema.PARADO
    elif any(a.impacto == Impacto.PARCIAL for a in acoes_abertas):
        sistema.estado_atual = EstadoSistema.DEGRADADO
    else:
        sistema.estado_atual = EstadoSistema.OPERACIONAL

    session.add(sistema)


@router.get("", response_model=List[Acao])
def listar_acoes(session: Session = Depends(get_session)):
    return session.exec(select(Acao)).all()


@router.get("/{id}", response_model=Acao)
def obter_acao_por_id(id: int, session: Session = Depends(get_session)):
    acao = session.get(Acao, id)
    if not acao:
        raise HTTPException(status_code=404, detail="Ação não encontrada")
    return acao


@router.post("", response_model=Acao)
def criar_acao(
    acao_in: AcaoCreate,
    session: Session = Depends(get_session),
    current_user: Superuser = Depends(get_current_user)
):
    sistema = session.get(Sistema, acao_in.sistema_id)
    if not sistema:
        raise HTTPException(status_code=404, detail="Sistema não encontrado")

    acao = Acao.model_validate(
        acao_in,
        update={"responsavel_id": current_user.id}
    )

    session.add(acao)
    session.commit()
    session.refresh(acao)

    # Recalcula estado do sistema afetado
    recalcular_estado_sistema(session, sistema.id)

    log = RegistoAuditoria(
        utilizador_email=current_user.email,
        acao_realizada="CRIAR_ACAO",
        detalhes=f"Ação ID {acao.id} criada para o sistema '{sistema.nome}' (Impacto: {acao.impacto})"
    )
    session.add(log)
    session.commit()
    session.refresh(acao)

    return acao


@router.put("/{id}/fechar", response_model=Acao)
def fechar_acao(
    id: int,
    fechar_in: Optional[AcaoFechar] = None,
    session: Session = Depends(get_session),
    current_user: Superuser = Depends(get_current_user)
):
    acao = session.get(Acao, id)
    if not acao:
        raise HTTPException(status_code=404, detail="Ação de manutenção não encontrada")

    if acao.status == StatusAcao.FECHADA:
        raise HTTPException(status_code=400, detail="A ação já se encontra fechada.")

    data_conclusao = (fechar_in.data_conclusao if fechar_in and fechar_in.data_conclusao else date.today())
    comentario = (fechar_in.comentario if fechar_in and fechar_in.comentario else None)

    acao.status = StatusAcao.FECHADA
    acao.data_conclusao = data_conclusao

    detalhes_log = f"Ação ID {id} encerrada em {data_conclusao} por {current_user.email}"
    if comentario:
        detalhes_log += f" | Comentário: {comentario}"

    session.add(acao)
    session.commit()

    # Recalcular estado do sistema (se já não houver ações abertas, regressa a OPERACIONAL)
    if acao.sistema_id:
        recalcular_estado_sistema(session, acao.sistema_id)

    log = RegistoAuditoria(
        utilizador_email=current_user.email,
        acao_realizada="FECHAR_ACAO",
        detalhes=detalhes_log
    )
    session.add(log)
    session.commit()
    session.refresh(acao)

    return acao


@router.put("/{id}", response_model=Acao)
def editar_acao(
    id: int,
    acao_in: AcaoUpdate,
    session: Session = Depends(get_session),
    current_user: Superuser = Depends(get_current_user)
):
    acao = session.get(Acao, id)
    if not acao:
        raise HTTPException(status_code=404, detail="Ação de manutenção não encontrada")

    sistema_antigo_id = acao.sistema_id

    update_data = acao_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(acao, field, value)

    session.add(acao)
    session.commit()

    # Recalcula estado do sistema atual e antigo (caso tenha mudado de sistema)
    if acao.sistema_id:
        recalcular_estado_sistema(session, acao.sistema_id)
    if sistema_antigo_id and sistema_antigo_id != acao.sistema_id:
        recalcular_estado_sistema(session, sistema_antigo_id)

    log = RegistoAuditoria(
        utilizador_email=current_user.email,
        acao_realizada="EDITAR_ACAO",
        detalhes=f"Ação ID {id} atualizada por {current_user.email}"
    )
    session.add(log)
    session.commit()
    session.refresh(acao)

    return acao