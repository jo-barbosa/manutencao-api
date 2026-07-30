import streamlit as st
import requests

# Configuração da Página
st.set_page_config(
    page_title="Gestão de Manutenção - Fábrica",
    page_icon="🛠️",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000/api"

# ==========================================
# GESTÃO DA SESSÃO / AUTENTICAÇÃO
# ==========================================
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None


def get_headers():
    """Devolve o cabeçalho HTTP com o Token JWT se o utilizador estiver logado."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


# ==========================================
# ECRÃ DE LOGIN (Se não estiver autenticado)
# ==========================================
if not st.session_state.token:
    st.title("🔑 Login - Sistema de Manutenção")

    with st.form("login_form"):
        email = st.text_input("Email", value="jorge.barbosa@inter.ikea.com")
        password = st.text_input("Password", type="password", value="dummy")
        submit = st.form_submit_button("Entrar")

        if submit:
            try:
                response = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": email, "password": password}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["accessToken"]
                    st.session_state.user = data["user"]
                    st.success(f"Bem-vindo, {data['user']['nome']}!")
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
            except Exception as e:
                st.error(f"Erro ao ligar à API: {e}")
    st.stop()

# ==========================================
# BARRA LATERAL (Sidebar)
# ==========================================
st.sidebar.title(f"👤 {st.session_state.user['nome']}")
st.sidebar.caption(st.session_state.user['email'])

if st.sidebar.button("Terminar Sessão"):
    st.session_state.token = None
    st.session_state.user = None
    st.rerun()

st.sidebar.divider()
st.sidebar.info("Conectado ao backend FastAPI")

# ==========================================
# INTERFACE PRINCIPAL (Tabs)
# ==========================================
st.title("🛠️ Painel de Operações de Manutenção")

tab_pds, tab_criar_acao, tab_sistemas = st.tabs([
    "🤖 Ponto de Situação (IA)",
    "➕ Registar Ação",
    "🏭 Estado dos Sistemas"
])

# ------------------------------------------
# TAB 1: PDS da IA
# ------------------------------------------
with tab_pds:
    st.header("Ponto de Situação Executivo (OpenRouter)")

    if st.button("🔄 Atualizar / Gerar Novo PDS"):
        with st.spinner("A consultar a IA..."):
            res = requests.get(f"{API_URL}/pds/geral")
            if res.status_code == 200:
                st.session_state["pds_texto"] = res.json()["pds"]
            else:
                st.error("Erro ao gerar o PDS.")

    if "pds_texto" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state["pds_texto"])
    else:
        st.info("Clica no botão acima para carregar o resumo inteligente da fábrica.")

# ------------------------------------------
# TAB 2: Criar Ação de Manutenção
# ------------------------------------------
with tab_criar_acao:
    st.header("Registar Nova Ação de Manutenção")

    # Procurar a lista de sistemas para preencher o Selectbox
    res_sistemas = requests.get(f"{API_URL}/sistemas/status")
    sistemas_opcoes = {}
    if res_sistemas.status_code == 200:
        for s in res_sistemas.json():
            sistemas_opcoes[f"{s['nome_sistema']} ({s['linha']} - {s['fabrica']})"] = s["id"]

    with st.form("form_nova_acao"):
        descricao = st.text_area("Descrição da Avaria / Intervenção")
        impacto = st.selectbox("Impacto Operacional", ["TOTAL", "PARCIAL", "NENHUM"])

        sistema_selecionado = st.selectbox(
            "Sistema Afetado",
            options=list(sistemas_opcoes.keys()) if sistemas_opcoes else ["Nenhum sistema encontrado"]
        )

        data_prevista = st.date_input("Data Prevista para Conclusão")

        submeter_acao = st.form_submit_button("Criar Ação")

        if submeter_acao:
            if not descricao:
                st.warning("Por favor, introduz a descrição.")
            elif not sistemas_opcoes:
                st.error("Sem sistemas disponíveis.")
            else:
                payload = {
                    "descricao": descricao,
                    "impacto": impacto,
                    "sistema_id": sistemas_opcoes[sistema_selecionado],
                    "data_prevista_conclusao": str(data_prevista)
                }

                res = requests.post(f"{API_URL}/acoes", json=payload, headers=get_headers())

                if res.status_code in (200, 201):
                    st.success("Ação registada com sucesso! O estado do sistema foi atualizado.")
                else:
                    st.error(f"Erro ao criar ação: {res.text}")

# ------------------------------------------
# TAB 3: Estado dos Sistemas
# ------------------------------------------
with tab_sistemas:
    st.header("Visão Geral dos Equipamentos")

    if st.button("🔄 Atualizar Lista"):
        st.rerun()

    res = requests.get(f"{API_URL}/sistemas/status")
    if res.status_code == 200:
        dados = res.json()


        # Mapeamento visual de cores para o estado
        def cor_estado(estado):
            if estado == "PARADO":
                return "🔴 PARADO"
            elif estado == "DEGRADADO":
                return "🟡 DEGRADADO"
            return "🟢 OPERACIONAL"


        tabela_dados = []
        for item in dados:
            tabela_dados.append({
                "ID": item["id"],
                "Sistema": item["nome_sistema"],
                "Estado": cor_estado(item["estado"]),
                "Linha": item["linha"],
                "Fábrica": item["fabrica"],
                "Fornecedor": item["fornecedor"]
            })

        st.dataframe(tabela_dados, use_container_width=True)
    else:
        st.error("Não foi possível carregar o estado dos sistemas.")