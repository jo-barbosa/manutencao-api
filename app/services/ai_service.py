import os
from dotenv import load_dotenv

load_dotenv()

try:
    import httpx
    from openai import OpenAI

    http_client = httpx.Client(verify=False)
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY", "dummy"),
        http_client=http_client
    )
    AI_AVAILABLE = True
except Exception:
    AI_AVAILABLE = False
    client = None

MODELO_FREE = "openrouter/free"


def gerar_pds_geral_ia(dados_sistemas: list) -> str | None:
    """Gera um resumo executivo de toda a fábrica usando o OpenRouter com fallback automático."""
    if not AI_AVAILABLE or not os.getenv("OPENROUTER_API_KEY"):
        parados = [s for s in dados_sistemas if s.get("impacto") == "TOTAL"]
        degradados = [s for s in dados_sistemas if s.get("impacto") == "PARCIAL"]

        res = "### 🏢 Ponto de Situação dos Sistemas\n\n"
        if parados:
            res += f"🔴 **Sistemas Parados ({len(parados)}):** " + ", ".join(s.get("sistema", "") for s in parados) + "\n\n"
        if degradados:
            res += f"🟡 **Sistemas Degradados ({len(degradados)}):** " + ", ".join(s.get("sistema", "") for s in degradados) + "\n\n"
        if not parados and not degradados:
            res += "🟢 **Todos os sistemas operacionais.**\n\n"
        return res

    prompt = f"""
    És um assistente sénior de manutenção industrial numa fábrica.
    Com base no seguinte estado atual dos sistemas e ações pendentes:
    {dados_sistemas}

    Cria um Ponto de Situação em Markdown, curto e direto ao ponto:
    1. 🔴 **Sistemas Parados** (se existirem).
    2. 🟡 **Sistemas Degradados** (se existirem).
    3. 🟢 **Resumo Geral da Operação**.

    Usa um tom profissional, sucinto e focado em prioridades operacionais.
    """

    try:
        completion = client.chat.completions.create(
            model=MODELO_FREE,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Relatório Automático (OpenRouter Indisponível): {e}"


def gerar_pds_operador_ia(nome_operador: str, acoes_operador: list) -> str | None:
    """Gera uma mensagem personalizada para o operador com fallback."""
    if not AI_AVAILABLE or not os.getenv("OPENROUTER_API_KEY"):
        count = len(acoes_operador)
        return f"### 👤 Boas-vindas, {nome_operador}!\n\nTens **{count}** ações de manutenção atribuídas ao teu turno."

    prompt = f"""
    És um assistente de manutenção. O operador/técnico '{nome_operador}' acabou de fazer login.
    Estas são as ações de manutenção atribuídas a ele:
    {acoes_operador}

    Escreve uma mensagem de boas-vindas amigável e direta em Markdown:
    - Cumprimenta o {nome_operador}.
    - Resume brevemente quais são as suas tarefas prioritárias para o turno.
    - Se não tiver tarefas pendentes, deseja-lhe um bom turno sem avarias.
    """

    try:
        completion = client.chat.completions.create(
            model=MODELO_FREE,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"### 👤 Olá {nome_operador}!\n\nTens {len(acoes_operador)} ações pendentes."