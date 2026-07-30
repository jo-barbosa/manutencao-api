from datetime import date
import streamlit as st
from dashboard_ui import api_client


def render_gestao_acoes_view():
    st.header("🔄 Gestão de Ações (Editar & Fechar)")
    st.caption("Consulte as intervenções ativas, atualize os seus dados ou encerre-as para repor o estado operacional.")

    acoes = api_client.get_acoes()
    if not acoes:
        st.info("Não existem ações de manutenção registadas na plataforma.")
        return

    # Filtro de Estado
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_status = st.selectbox("Filtrar por Status", ["ABERTA", "FECHADA", "TODAS"], index=0)
    with col_f2:
        busca_texto = st.text_input("🔍 Procurar por Descrição / ID", "")

    # Aplicar filtros
    acoes_filtradas = acoes
    if filtro_status != "TODAS":
        acoes_filtradas = [a for a in acoes_filtradas if a.get("status") == filtro_status]
    if busca_texto.strip():
        txt = busca_texto.strip().lower()
        acoes_filtradas = [
            a for a in acoes_filtradas
            if txt in a.get("descricao", "").lower() or txt in str(a.get("id"))
        ]

    st.subheader(f"Lista de Ações ({len(acoes_filtradas)})")

    if not acoes_filtradas:
        st.warning("Nenhuma ação encontrada com os filtros selecionados.")
        return

    # Mapeamento para Selectbox de Escolha da Ação
    acao_options = {}
    for a in acoes_filtradas:
        impacto_icon = "🔴" if a.get("impacto") == "TOTAL" else ("🟡" if a.get("impacto") == "PARCIAL" else "🟢")
        status_tag = f"[{a.get('status')}]"
        label = f"Ação #{a['id']} {status_tag} - {impacto_icon} {a['descricao'][:50]}..."
        acao_options[label] = a

    selected_label = st.selectbox("Selecione a Ação a Gerir", options=list(acao_options.keys()))
    acao = acao_options[selected_label]

    st.markdown("---")

    # Exibir Cartão da Ação Selecionada
    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.markdown(f"**ID da Ação:** #{acao['id']}")
        st.markdown(f"**Status Atual:** `{acao['status']}`")
    with col_info2:
        st.markdown(f"**Impacto:** `{acao['impacto']}`")
        st.markdown(f"**Sistema ID:** #{acao.get('sistema_id', 'N/A')}")
    with col_info3:
        st.markdown(f"**Data Criação:** {acao.get('data_criacao', 'N/A')}")
        st.markdown(f"**Prev. Conclusão:** {acao.get('data_prevista_conclusao', 'N/A')}")

    st.markdown(f"**Descrição Completa:** {acao.get('descricao')}")
    if acao.get("data_conclusao"):
        st.markdown(f"**Data de Conclusão:** {acao.get('data_conclusao')}")

    # Ações de Edição e Fecho
    tab_fechar, tab_editar = st.tabs(["✅ Fechar Ação", "✏️ Editar Ação"])

    with tab_fechar:
        if acao.get("status") == "FECHADA":
            st.success("Esta ação já se encontra encerrada.")
        else:
            with st.form(f"form_fechar_{acao['id']}"):
                st.write("### Encerrar Ação de Manutenção")
                data_conclusao = st.date_input("Data de Conclusão", value=date.today())
                comentario = st.text_area("Comentário Final / Observações do Técnico", placeholder="Descreva os trabalhos efetuados para fechar a avaria...")

                submeter_fecho = st.form_submit_button("Encerrar Ação e Recalcular Equipamento")

                if submeter_fecho:
                    resp = api_client.fechar_acao(
                        acao_id=acao["id"],
                        data_conclusao=str(data_conclusao),
                        comentario=comentario.strip() if comentario else None
                    )
                    if resp.status_code == 200:
                        st.success(f"✅ Ação #{acao['id']} encerrada com sucesso! O estado do sistema foi recalculado.")
                        st.rerun()
                    else:
                        st.error(f"Erro ao fechar ação: {resp.text}")

    with tab_editar:
        with st.form(f"form_editar_{acao['id']}"):
            st.write("### Editar Dados da Ação")
            nova_desc = st.text_area("Descrição", value=acao.get("descricao", ""))
            novo_impacto = st.selectbox(
                "Impacto",
                ["TOTAL", "PARCIAL", "NENHUM"],
                index=["TOTAL", "PARCIAL", "NENHUM"].index(acao.get("impacto", "NENHUM"))
            )
            novo_status = st.selectbox(
                "Status",
                ["ABERTA", "FECHADA"],
                index=0 if acao.get("status") == "ABERTA" else 1
            )
            data_prev = st.date_input(
                "Data Prevista Conclusão",
                value=date.fromisoformat(acao.get("data_prevista_conclusao")) if acao.get("data_prevista_conclusao") else date.today()
            )

            submeter_edicao = st.form_submit_button("Guardar Alterações")

            if submeter_edicao:
                payload = {
                    "descricao": nova_desc.strip(),
                    "impacto": novo_impacto,
                    "status": novo_status,
                    "data_prevista_conclusao": str(data_prev)
                }
                resp = api_client.editar_acao(acao["id"], payload)
                if resp.status_code == 200:
                    st.success("✅ Ação atualizada com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro ao editar ação: {resp.text}")
