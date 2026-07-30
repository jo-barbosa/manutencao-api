import streamlit as st
from dashboard_ui import api_client

st.set_page_config(
    page_title="Consola de Manutenção Fabril - Home",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gestão de Estado da Sessão / Autenticação
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None


# ==========================================
# ECRÃ DE LOGIN (Caso não esteja autenticado)
# ==========================================
if not st.session_state.token or not st.session_state.user:
    st.title("🔑 Consola de Manutenção - Autenticação")
    st.subheader("Por favor, inicie sessão com a sua conta de operador.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email do Operador", value="jorge.barbosa@inter.ikea.com")
            password = st.text_input("Password", type="password", value="dummy")
            submeter_login = st.form_submit_button("Entrar no Sistema")

            if submeter_login:
                try:
                    data = api_client.login(email.strip(), password.strip())
                    st.session_state.token = data["accessToken"]
                    st.session_state.user = data["user"]
                    st.success(f"Bem-vindo, {data['user']['nome']}!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao efetuar login: {e}")
    st.stop()


# ==========================================
# BARRA LATERAL (Sidebar)
# ==========================================
user = st.session_state.user
if user:
    st.sidebar.title(f"👤 {user.get('nome', 'Operador')}")
    st.sidebar.caption(f"📧 {user.get('email', '')}")

    if st.sidebar.button("Terminar Sessão", use_container_width=True):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

st.sidebar.divider()
st.sidebar.info("🔌 Conectado ao Backend FastAPI (`manutencao-api`)")


# ==========================================
# HOMEPAGE / PAINEL DE BOAS-VINDAS
# ==========================================
st.title("🏭 Visão Geral da Operação Fabril")
st.caption(f"Sessão ativa de: **{user.get('nome', 'Operador')}** | Utilize a barra lateral para navegar entre as secções da aplicação.")

# Obter dados de métricas rápidas
sistemas = api_client.get_sistemas_status()
acoes = api_client.get_acoes()

total_sistemas = len(sistemas)
parados = sum(1 for s in sistemas if s.get("estado") == "PARADO")
degradados = sum(1 for s in sistemas if s.get("estado") == "DEGRADADO")
operacionais = sum(1 for s in sistemas if s.get("estado") == "OPERACIONAL")
acoes_abertas = sum(1 for a in acoes if a.get("status") == "ABERTA")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Equipamentos Totais", total_sistemas)
col2.metric("🟢 Operacionais", operacionais)
col3.metric("🟡 Degradados", degradados)
col4.metric("🔴 Parados", parados)
col5.metric("🛠️ Ações Abertas", acoes_abertas)

st.markdown("---")
st.subheader("📌 Guia Rápido de Navegação")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
    - 🤖 **Ponto de Situação (IA):** Resumo executivo inteligente e briefing para o teu turno.
    - ➕ **Registar Ação:** Reportar avaria ou intervenção em equipamento.
    - 🔄 **Gestão de Ações:** Editar ou encerrar ações de manutenção ativas.
    """)

with col_b:
    st.markdown("""
    - 📊 **Análise & Status:** Tabela em tempo real e pesquisa de intervenções.
    - ⚙️ **Estrutura & Equipamentos:** Cadastrar novas linhas, sistemas e fornecedores.
    - 📜 **Histórico de Auditoria:** Feed cronológico de operações efetuadas.
    """)