from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Fabrica, Linha, Sistema, Fornecedor, RegistoAuditoria, Superuser
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api", tags=["Estrutura Fabril & Fornecedores"])


# ==========================================
# 1. LEITURA (GET)
# ==========================================

@router.get("/fabricas", response_model=List[Fabrica])
def listar_fabricas(session: Session = Depends(get_session)):
    return session.exec(select(Fabrica)).all()


@router.get("/fabricas/{fabrica_id}/linhas", response_model=List[Linha])
def listar_linhas_por_fabrica(fabrica_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Linha).where(Linha.fabrica_id == fabrica_id)).all()


@router.get("/linhas/{linha_id}/sistemas", response_model=List[Sistema])
def listar_sistemas_por_linha(linha_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Sistema).where(Sistema.linha_id == linha_id)).all()


@router.get("/fornecedores", response_model=List[Fornecedor])
def listar_fornecedores(session: Session = Depends(get_session)):
    return session.exec(select(Fornecedor)).all()


@router.get("/sistemas/status")
def obter_status_sistemas(session: Session = Depends(get_session)):
    sistemas = session.exec(select(Sistema)).all()
    resultado = []
    for s in sistemas:
        resultado.append({
            "id": s.id,
            "nome_sistema": s.nome,
            "estado": s.estado_atual,
            "linha": s.linha.nome if s.linha else "N/A",
            "fabrica": s.linha.fabrica.nome if s.linha and s.linha.fabrica else "N/A",
            "fornecedor": s.fornecedor.nome if s.fornecedor else "N/A"
        })
    return resultado


# ==========================================
# 2. CRIAÇÃO / ESCRITA (POST)
# ==========================================

@router.post("/fabricas", response_model=Fabrica, status_code=status.HTTP_201_CREATED)
def criar_fabrica(
        fabrica: Fabrica,
        session: Session = Depends(get_session),
        current_user: Superuser = Depends(get_current_user)
):
    session.add(fabrica)

    # Registar na Auditoria
    log = RegistoAuditoria(
        utilizador_email=current_user.email,
        acao_realizada="CRIAR_FABRICA",
        detalhes=f"Criada a fábrica '{fabrica.nome}' (Localização: {fabrica.localizacao})"
    )
    session.add(log)

    session.commit()
    session.refresh(fabrica)
    return fabrica


@router.post("/linhas", response_model=Linha, status_code=status.HTTP_201_CREATED)
def criar_linha(
        linha: Linha,
        session: Session = Depends(get_session),
        current_user: Superuser = Depends(get_current_user)
):
    fabrica = session.get(Fabrica, linha.fabrica_id)
    if not fabrica:
        raise HTTPException(status_code=404, detail="Fábrica associada não encontrada.")

    session.add(linha)

    log = RegistoAuditoria(
        utilizador_email=current_user.email,
        acao_realizada="CRIAR_LINHA",
        detalhes=f"Criada a linha '{linha.nome}' na fábrica '{fabrica.nome}'"
    )
    session.add(log)

    session.commit()
    session.refresh(linha)
    return linha


@router.post("/sistemas", response_model=Sistema, status_code=status.HTTP_201_CREATED)
def criar_sistema(
        sistema: Sistema,
        session: Session = Depends(get_session),
        current_user: Superuser = Depends(get_current_user)
):
    linha = session.get(Linha, sistema.linha_id)
    if not linha:
        raise HTTPException(status_code=404, detail="Linha associada não encontrada.")

    session.add(sistema)

    log = RegistoAuditoria(
        utilizador_email=current_user.email,
        acao_realizada="CRIAR_SISTEMA",
        detalhes=f"Criado o sistema '{sistema.nome}' na linha '{linha.nome}'"
    )
    session.add(log)

    session.commit()
    session.refresh(sistema)
    return sistema


@router.post("/fornecedores", response_model=Fornecedor, status_code=status.HTTP_201_CREATED)
def criar_fornecedor(
        fornecedor: Fornecedor,
        session: Session = Depends(get_session),
        current_user: Superuser = Depends(get_current_user)
):
    session.add(fornecedor)

    log = RegistoAuditoria(
        utilizador_email=current_user.email,
        acao_realizada="CRIAR_FORNECEDOR",
        detalhes=f"Criado o fornecedor '{fornecedor.nome}'"
    )
    session.add(log)

    session.commit()
    session.refresh(fornecedor)
    return fornecedor