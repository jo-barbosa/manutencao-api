import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Inicializa o cliente apontando para a API do OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Modelos Gratuitos recomendados no OpenRouter:
# - "meta-llama/llama-3.3-70b-instruct:free"
# - "google/gemini-2.5-flash:free"
# - "deepseek/deepseek-r1:free"
MODELO_FREE = "meta-llama/llama-3.3-70b-instruct:free"


def gerar_pds_geral_ia(dados_sistemas: list) -> str | None:
    """Gera um resumo executivo de toda a fábrica usando o OpenRouter."""

    prompt = f"""
    És um assistente sénior de manutenção industrial numa fábrica.
    Com base no seguinte estado atual dos sistemas e ações pendentes:
    {dados_sistemas}

    Cria um Ponto de Situação (PDS) Executivo em Markdown, curto e direto ao ponto:
    1. 🔴 **Sistemas Críticos / Parados** (se existirem).
    2. 🟡 **Avisos e Degradações** (se existirem).
    3. 🟢 **Resumo Geral da Operação**.

    Usa um tom profissional, sucinto e focado em prioridades operacionais.
    """

    completion = client.chat.completions.create(
        model=MODELO_FREE,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content


def gerar_pds_operador_ia(nome_operador: str, acoes_operador: list) -> str | None:
    """Gera uma mensagem personalizada de boas-vindas para o operador."""

    prompt = f"""
    És um assistente de manutenção. O operador/técnico '{nome_operador}' acabou de fazer login.
    Estas são as ações de manutenção atribuídas a ele:
    {acoes_operador}

    Escreve uma mensagem de boas-vindas amigável e direta em Markdown:
    - Cumprimenta o {nome_operador}.
    - Resume brevemente quais são as suas tarefas prioritárias para o turno.
    - Se não tiver tarefas pendentes, deseja-lhe um bom turno sem avarias.
    """

    completion = client.chat.completions.create(
        model=MODELO_FREE,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content