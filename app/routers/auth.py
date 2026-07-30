from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import Session, select
from app.database import get_session
from app.models import Superuser
from app.security import (
    verify_password,
    hash_password,
    create_access_token,
    decode_access_token,
    MASTER_RESET_KEY
)

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ==========================================
# SCHEMAS (Modelos de Pedido JSON)
# ==========================================

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterUserRequest(BaseModel):
    nome: str
    email: str
    password: str


class ChangePasswordRequest(BaseModel):
    password_atual: str
    nova_password: str


class ResetPasswordRequest(BaseModel):
    email: str
    master_key: str
    nova_password: str


# ==========================================
# DEPENDÊNCIA DE AUTENTICAÇÃO
# ==========================================

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> Superuser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = session.exec(select(Superuser).where(Superuser.email == email)).first()
    if user is None:
        raise credentials_exception

    return user


# ==========================================
# ENDPOINTS
# ==========================================

@router.post("/login")
def login(credentials: LoginRequest, session: Session = Depends(get_session)):
    """Login com Email e Password em JSON."""
    user = session.exec(select(Superuser).where(Superuser.email == credentials.email)).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ou password incorretos"
        )

    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})

    return {
        "accessToken": access_token,
        "tokenType": "bearer",
        "user": {
            "id": user.id,
            "nome": user.nome,
            "email": user.email
        }
    }


@router.get("/me")
def obter_perfil_atual(current_user: Superuser = Depends(get_current_user)):
    """Retorna os dados do utilizador atualmente logado."""
    return current_user


@router.post("/register", status_code=status.HTTP_201_CREATED)
def criar_utilizador(user_data: RegisterUserRequest, session: Session = Depends(get_session)):
    """Cria um novo utilizador na base de dados com password encriptada."""
    existente = session.exec(select(Superuser).where(Superuser.email == user_data.email)).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este email já está registado na plataforma."
        )

    novo_user = Superuser(
        nome=user_data.nome,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )

    session.add(novo_user)
    session.commit()
    session.refresh(novo_user)

    return {
        "mensagem": "Utilizador criado com sucesso",
        "user": {"id": novo_user.id, "nome": novo_user.nome, "email": novo_user.email}
    }


@router.put("/change-password")
def alterar_password(
    data: ChangePasswordRequest,
    session: Session = Depends(get_session),
    current_user: Superuser = Depends(get_current_user)
):
    """Permite que um utilizador autenticado altere a sua própria password."""
    if not verify_password(data.password_atual, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A password atual está incorreta."
        )

    current_user.password_hash = hash_password(data.nova_password)
    session.add(current_user)
    session.commit()

    return {"mensagem": "Password alterada com sucesso!"}


@router.post("/reset-password")
def reset_password_com_chave_mestra(data: ResetPasswordRequest, session: Session = Depends(get_session)):
    """Redefine a password de qualquer utilizador usando a chave mestra (definida no .env)."""
    if data.master_key != MASTER_RESET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave mestra inválida ou não autorizada."
        )

    user = session.exec(select(Superuser).where(Superuser.email == data.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilizador com este email não encontrado."
        )

    user.password_hash = hash_password(data.nova_password)
    session.add(user)
    session.commit()

    return {"mensagem": f"Password do utilizador '{data.email}' redefinida com sucesso!"}