import streamlit as st
from dashboard_ui import api_client

st.set_page_config(
    page_title="Consola de Manutenção Fabril",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Gestão de Estado da Sessão / Autenticação
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None


# Definir Páginas com st.Page
home_page = st.Page("dashboard_ui/home.py", title="Dashboard", icon="🏭", default=True)
reg_page = st.Page("dashboard_ui/views/registar_page.py", title="Registar Ação", icon="➕")
gestao_page = st.Page("dashboard_ui/views/gestao_page.py", title="Gestão de Ações", icon="🔄")
analise_page = st.Page("dashboard_ui/views/analise_page.py", title="Análise & Status", icon="📊")
est_page = st.Page("dashboard_ui/views/estrutura_page.py", title="Estrutura & Equipamentos", icon="⚙️")
audit_page = st.Page("dashboard_ui/views/auditoria_page.py", title="Histórico de Auditoria", icon="📜")


# 1. Configurar Navegação Dinâmica
user = st.session_state.get("user")
is_logged_in = bool(st.session_state.get("token") and user)

if is_logged_in:
    # QUANDO LOGADO: Mostra todas as opções organizadas com a palavra "Dashboard" idêntica às restantes!
    pages_map = {
        "Navegação": [home_page],
        "Operação Fabril": [reg_page, gestao_page],
        "Gestão & Consulta": [analise_page, est_page, audit_page]
    }
else:
    # QUANDO NÃO LOGADO: Esconde todas as outras páginas e mostra APENAS o "Dashboard"!
    pages_map = [home_page]

pg = st.navigation(pages_map)


# 2. Renderizar Barra Lateral (Perfil ou Login Form)
st.sidebar.divider()

if not is_logged_in:
    st.sidebar.title("🔑 Iniciar Sessão")
    with st.sidebar.form("sidebar_login_form"):
        email = st.text_input("Email", value="admin@empresa.com")
        password = st.text_input("Password", type="password", value="admin123")
        submeter_login = st.form_submit_button("Entrar", use_container_width=True)

        if submeter_login:
            try:
                data = api_client.login(email.strip(), password.strip())
                st.session_state.token = data["access_token"]
                st.session_state.user = data["user"]
                st.success(f"Bem-vindo, {data['user']['nome']}!")
                st.rerun()
            except Exception as e:
                st.error(f"Credenciais inválidas ou erro no login: {e}")
else:
    st.sidebar.title(f"👤 {user.get('nome', 'Operador')}")
    st.sidebar.caption(f"📧 {user.get('email', '')}")

    if st.sidebar.button("Terminar Sessão", use_container_width=True):
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.pop("pds_operador_texto", None)
        st.rerun()

# 3. Executar a Página Selecionada
pg.run()