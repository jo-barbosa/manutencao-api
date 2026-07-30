from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Fabrica, Linha, Sistema

router = APIRouter(prefix="/api", tags=["Estrutura Fabril"])


# -------------------------------------------------------------
# 1. SELECTS EM CASCATA (Formulário React)
# -------------------------------------------------------------

@router.get("/fabricas", response_model=List[Fabrica])
def listar_fabricas(session: Session = Depends(get_session)):
    return session.exec(select(Fabrica)).all()


@router.get("/fabricas/{fabrica_id}/linhas", response_model=List[Linha])
def listar_linhas_por_fabrica(fabrica_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Linha).where(Linha.fabrica_id == fabrica_id)).all()


@router.get("/linhas/{linha_id}/sistemas", response_model=List[Sistema])
def listar_sistemas_por_linha(linha_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Sistema).where(Sistema.linha_id == linha_id)).all()


# -------------------------------------------------------------
# 2. STATUS DOS SISTEMAS (Ecrã Monitor / Dashboard)
# -------------------------------------------------------------

@router.get("/sistemas/status")
def obter_status_sistemas(session: Session = Depends(get_session)):
    """
    Retorna a lista completa de sistemas com o estado atual,
    nome da linha e nome da fábrica. Ideal para o ecrã de Status.
    """
    sistemas = session.exec(select(Sistema)).all()

    resultado = []
    for s in sistemas:
        resultado.append({
            "id": s.id,
            "nome_sistema": s.nome,
            "estado": s.estado_atual,
            "linha": s.linha.nome if s.linha else "N/A",
            "fabrica": s.linha.fabrica.nome if s.linha and s.linha.fabrica else "N/A"
        })

    return resultado