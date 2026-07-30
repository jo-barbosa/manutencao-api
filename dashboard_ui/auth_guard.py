import streamlit as st


def check_authentication():
    """
    Guarda de Autenticação para as Páginas Nativas do Streamlit.
    Redireciona/Bloqueia utilizadores não autenticados.
    """
    if not st.session_state.get("token") or not st.session_state.get("user"):
        st.title("🔑 Acesso Restrito")
        st.warning("É necessário iniciar sessão para aceder a esta secção da consola de manutenção.")
        st.info("👈 Por favor, clique na página **Home (dashboard)** na barra lateral para fazer login.")
        st.stop()
