from datetime import date
import streamlit as st
from dashboard_ui import api_client
from dashboard_ui.components.cascade_selectors import render_cascade_selectors


def render_registar_acao_view():
    st.header("➕ Registar Nova Ação de Manutenção")
    st.caption("Preencha a avaria ou intervenção programada. O estado do equipamento será atualizado automaticamente.")

    st.subheader("1. Localização do Equipamento")
    _, _, selected_sistema_id = render_cascade_selectors(
        key_prefix="reg_acao",
        show_all_option=False
    )

    st.subheader("2. Detalhes da Ação")
    with st.form("form_registar_acao"):
        descricao = st.text_area("Descrição da Avaria / Intervenção", placeholder="Descreva a avaria detetada e componentes afetados...")

        col1, col2 = st.columns(2)
        with col1:
            impacto = st.selectbox("Impacto Operacional", ["TOTAL", "PARCIAL", "NENHUM"])
        with col2:
            data_prevista = st.date_input("Data Prevista de Conclusão", value=date.today())

        # Seleção de responsável (Operador)
        superusers = api_client.get_superusers()
        superuser_options = {}
        for su in superusers:
            superuser_options[f"{su['nome']} ({su['email']})"] = su["id"]

        current_user = st.session_state.get("user")
        default_index = 0
        if current_user and superuser_options:
            for idx, key in enumerate(superuser_options.keys()):
                if superuser_options[key] == current_user.get("id"):
                    default_index = idx
                    break

        responsavel_label = st.selectbox(
            "Técnico Responsável",
            options=list(superuser_options.keys()) if superuser_options else ["Sem operadores disponíveis"],
            index=default_index if superuser_options else 0
        )

        submeter = st.form_submit_button("Submeter Ação")

        if submeter:
            if not selected_sistema_id:
                st.error("Por favor, selecione um sistema válido.")
            elif not descricao.strip():
                st.warning("Por favor, introduza a descrição da avaria.")
            else:
                payload = {
                    "descricao": descricao.strip(),
                    "impacto": impacto,
                    "sistema_id": selected_sistema_id,
                    "data_prevista_conclusao": str(data_prevista)
                }

                resp = api_client.criar_acao(payload)
                if resp.status_code in (200, 201):
                    st.success("✅ Ação registada com sucesso! O estado do equipamento foi recalculado.")
                    st.balloons()
                else:
                    st.error(f"Erro ao registar ação: {resp.text}")
