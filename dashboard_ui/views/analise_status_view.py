import streamlit as st
from dashboard_ui import api_client
from dashboard_ui.components.cascade_selectors import render_cascade_selectors


def render_analise_status_view():
    st.header("📊 Análise de Status & Equipamentos")

    tab_equipamentos, tab_analise_acoes = st.tabs([
        "🏭 Estado dos Equipamentos",
        "🔍 Consulta Avançada de Ações"
    ])

    with tab_equipamentos:
        st.subheader("Visão Geral dos Sistemas Fabris")
        if st.button("🔄 Atualizar Lista de Sistemas", key="btn_refresh_sistemas"):
            st.rerun()

        dados = api_client.get_sistemas_status()
        if dados:
            def cor_estado(estado):
                if estado == "PARADO":
                    return "🔴 PARADO"
                elif estado == "DEGRADADO":
                    return "🟡 DEGRADADO"
                return "🟢 OPERACIONAL"

            # Ordenar por fábrica, linha e depois sistema
            dados_ordenados = sorted(
                dados,
                key=lambda x: (
                    (x.get("fabrica") or "").lower(),
                    (x.get("linha") or "").lower(),
                    (x.get("nome_sistema") or "").lower()
                )
            )

            tabela_dados = []
            for item in dados_ordenados:
                tabela_dados.append({
                    "Fábrica": item["fabrica"],
                    "Linha": item["linha"],
                    "Sistema": item["nome_sistema"],
                    "Estado Atual": cor_estado(item["estado"]),
                })

            st.dataframe(tabela_dados, use_container_width=True)
        else:
            st.warning("Não foi possível carregar a lista de sistemas.")

    with tab_analise_acoes:
        st.subheader("Filtros Multi-dimensionais de Ações")

        sel_fabrica_id, sel_linha_id, sel_sistema_id = render_cascade_selectors(
            key_prefix="analise_filtros",
            show_all_option=True
        )

        col1, col2 = st.columns(2)
        with col1:
            filtro_status = st.selectbox("Status da Ação", ["TODAS", "ABERTA", "FECHADA"], index=0, key="analise_status")
        with col2:
            superusers = api_client.get_superusers()
            su_options = {"Todos os Operadores": None}
            su_dict = {}
            for su in superusers:
                su_options[f"{su['nome']} ({su['email']})"] = su["id"]
                su_dict[su["id"]] = su["nome"]

            sel_su_label = st.selectbox("Técnico Responsável", options=list(su_options.keys()), key="analise_su")
            selected_su_id = su_options[sel_su_label]

        # Mapeamento dos sistemas para obter nome, linha e fábrica por ID
        sistemas_status = api_client.get_sistemas_status()
        sistemas_dict = {
            s["id"]: {
                "nome": s.get("nome_sistema", "N/A"),
                "linha": s.get("linha", "N/A"),
                "fabrica": s.get("fabrica", "N/A")
            }
            for s in sistemas_status
        }

        # Procurar ações e filtrar localmente
        acoes = api_client.get_acoes()

        if sel_sistema_id:
            acoes = [a for a in acoes if a.get("sistema_id") == sel_sistema_id]
        if filtro_status != "TODAS":
            acoes = [a for a in acoes if a.get("status") == filtro_status]
        if selected_su_id:
            acoes = [a for a in acoes if a.get("responsavel_id") == selected_su_id]

        st.subheader(f"Resultados Encontrados ({len(acoes)})")

        if not acoes:
            st.info("Nenhuma ação corresponde aos critérios de pesquisa selecionados.")
        else:
            for acao in acoes:
                status_icon = "🔴" if acao.get("impacto") == "TOTAL" else ("🟡" if acao.get("impacto") == "PARCIAL" else "🟢")
                with st.container(border=True):
                    col_t1, col_t2 = st.columns([3, 1])
                    with col_t1:
                        st.markdown(f"#### {status_icon} Ação #{acao['id']} — `{acao.get('status')}`")
                    with col_t2:
                        st.markdown(f"**Impacto:** `{acao.get('impacto')}`")

                    st.markdown(f"**Descrição:** {acao.get('descricao')}")

                    # Obter dados do sistema e responsável
                    sis_id = acao.get("sistema_id")
                    sis_info = sistemas_dict.get(sis_id, {})
                    sis_nome = sis_info.get("nome", "N/A")
                    sis_linha = sis_info.get("linha", "N/A")
                    sis_fabrica = sis_info.get("fabrica", "N/A")
                    sistema_str = f"{sis_nome} ({sis_linha} - {sis_fabrica})" if sis_info else f"Sistema #{sis_id}"

                    resp_id = acao.get("responsavel_id")
                    resp_nome = su_dict.get(resp_id, "Não atribuído") if resp_id else "Não atribuído"

                    data_conclusao_str = f" | 🏁 Conclusão: {acao.get('data_conclusao')}" if acao.get("data_conclusao") else ""
                    st.caption(
                        f"**Sistema:** {sistema_str} | "
                        f"**Responsável:** {resp_nome} | "
                        f"📅 Criação: {acao.get('data_criacao')} | Previsão: {acao.get('data_prevista_conclusao')}{data_conclusao_str}"
                    )

