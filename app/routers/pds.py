from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Acao, Sistema, Superuser, StatusAcao
from app.services.ai_service import gerar_pds_geral_ia, gerar_pds_operador_ia

router = APIRouter(prefix="/api/pds", tags=["Ponto de Situação (PDS)"])


@router.get("/geral")
def obter_pds_geral(session: Session = Depends(get_session)):
    """Gera o PDS Geral da Fábrica alimentado por IA."""
    # Procura todas as ações que ainda estão ABERTAS
    acoes_abertas = session.exec(select(Acao).where(Acao.status == StatusAcao.ABERTA)).all()

    # Prepara um resumo simplificado para enviar à IA
    dados_para_ia = []
    for acao in acoes_abertas:
        dados_para_ia.append({
            "sistema": acao.sistema.nome if acao.sistema else "Desconhecido",
            "impacto": acao.impacto,
            "descricao": acao.descricao
        })

    # Chama a IA
    resumo_markdown = gerar_pds_geral_ia(dados_para_ia)

    return {"pds": resumo_markdown}


@router.get("/operador/{superuser_id}")
def obter_pds_operador(superuser_id: int, session: Session = Depends(get_session)):
    """Gera o PDS pessoal do Operador alimentado por IA."""
    user = session.get(Superuser, superuser_id)
    if not user:
        raise HTTPException(status_code=404, detail="Operador não encontrado")

    # Procura ações ABERTAS atribuídas a este operador
    acoes_user = session.exec(
        select(Acao).where(Acao.responsavel_id == superuser_id, Acao.status == StatusAcao.ABERTA)
    ).all()

    acoes_formatadas = [
        {"sistema": a.sistema.nome if a.sistema else "N/A", "descricao": a.descricao, "impacto": a.impacto}
        for a in acoes_user
    ]

    # Chama a IA
    mensagem_markdown = gerar_pds_operador_ia(user.nome, acoes_formatadas)

    return {"operador": user.nome, "pds": mensagem_markdown}