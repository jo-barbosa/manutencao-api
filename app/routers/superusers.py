from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from app.database import get_session
from app.models import Superuser

router = APIRouter(prefix="/api/superusers", tags=["Superusers & Operadores"])


class SuperuserDTO(BaseModel):
    id: int
    nome: str
    email: str


@router.get("", response_model=List[SuperuserDTO])
def listar_superusers(session: Session = Depends(get_session)):
    """Lista todos os operadores/superutilizadores registados (retorna DTO seguro sem password)."""
    users = session.exec(select(Superuser)).all()
    return [SuperuserDTO(id=u.id, nome=u.nome, email=u.email) for u in users]


@router.get("/{id}", response_model=SuperuserDTO)
def obter_superuser_por_id(id: int, session: Session = Depends(get_session)):
    """Obtém detalhes de um operador por ID."""
    user = session.get(Superuser, id)
    if not user:
        raise HTTPException(status_code=404, detail="Operador não encontrado")
    return SuperuserDTO(id=user.id, nome=user.nome, email=user.email)
