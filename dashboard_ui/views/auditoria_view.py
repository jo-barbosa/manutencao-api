import streamlit as st
from dashboard_ui import api_client


def render_auditoria_view():
    st.header("📜 Histórico de Auditoria & Logs")
    st.caption("Registo cronológico de todas as operações efetuadas pelos operadores na plataforma.")

    if st.button("🔄 Atualizar Logs", key="btn_refresh_audit"):
        st.rerun()

    logs = api_client.get_auditoria()
    if not logs:
        st.info("Ainda não existem registos de auditoria gravados na base de dados.")
        return

    st.subheader(f"Total de Operações Registadas ({len(logs)})")

    # Exibir em tabela formatada
    st.dataframe(logs, use_container_width=True)

    st.markdown("---")
    st.subheader("Linha do Tempo Recente")

    for log in logs[:15]:
        ts = log.get("timestamp", "").replace("T", " ")[:19]
        user = log.get("utilizador_email", "Desconhecido")
        acao = log.get("acao_realizada", "AÇÃO")
        detalhes = log.get("detalhes", "")

        icon = "🟢" if "CRIAR" in acao else ("🟡" if "EDITAR" in acao else "🔵")

        with st.container(border=True):
            st.markdown(f"**{icon} {acao}** — {detalhes}")
            st.caption(f"⏱️ {ts} | 👤 {user}")

