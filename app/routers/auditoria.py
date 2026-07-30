from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import RegistoAuditoria
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/auditoria", tags=["Auditoria & Logs"])


@router.get("", response_model=List[RegistoAuditoria])
def listar_logs(
    session: Session = Depends(get_session),
    _current_user=Depends(get_current_user)  # Apenas utilizadores autenticados podem ver os logs
):
    """Lista todos os registos de auditoria ordenados do mais recente para o mais antigo."""
    return session.exec(select(RegistoAuditoria).order_by(RegistoAuditoria.timestamp.desc())).all()