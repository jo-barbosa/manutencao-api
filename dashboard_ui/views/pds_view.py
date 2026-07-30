import streamlit as st
from dashboard_ui import api_client


def render_pds_view():
    st.header("🤖 Ponto de Situação por Inteligência Artificial (OpenRouter)")
    st.caption("Resumos inteligentes gerados com base no estado real da fábrica e ações pendentes.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏢 PDS Geral da Fábrica")
        if st.button("🔄 Atualizar / Gerar PDS Geral", key="btn_pds_geral"):
            with st.spinner("A consultar a IA (OpenRouter)..."):
                texto = api_client.get_pds_geral()
                if texto:
                    st.session_state["pds_geral_texto"] = texto
                else:
                    st.error("Não foi possível gerar o PDS Geral.")

        if "pds_geral_texto" in st.session_state:
            st.markdown("---")
            st.markdown(st.session_state["pds_geral_texto"])
        else:
            st.info("Clica no botão acima para carregar o resumo executivo da operação.")

    with col2:
        st.subheader("👤 PDS do Teu Turno (Operador)")
        current_user = st.session_state.get("user")
        if current_user:
            user_id = current_user.get("id")
            if st.button(f"🔄 Gerar Briefing para {current_user.get('nome')}", key="btn_pds_op"):
                with st.spinner("A preparar o teu briefing de turno..."):
                    texto_op = api_client.get_pds_operador(user_id)
                    if texto_op:
                        st.session_state["pds_operador_texto"] = texto_op
                    else:
                        st.error("Erro ao gerar briefing de operador.")

            if "pds_operador_texto" in st.session_state:
                st.markdown("---")
                st.markdown(st.session_state["pds_operador_texto"])
            else:
                st.info("Clica acima para ver a tua mensagem personalizada e tarefas atribuídas.")
