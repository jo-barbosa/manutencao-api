from datetime import date
import streamlit as st
from dashboard_ui import api_client


def pad_or_truncate(text: str, length: int) -> str:
    """Garante que a string tem exatamente 'length' caracteres (trunca com ... ou preenche com espaços)."""
    text_str = str(text) if text is not None else ""
    if len(text_str) > length:
        return text_str[:length - 3] + "..."
    return text_str.ljust(length)


def render_gestao_acoes_view():
    st.header("🔄 Gestão de Ações (Editar & Fechar)")
    st.caption("Clique na linha da ação que pretende gerir para abrir o painel de alteração e encerramento.")

    # CSS Customizado para Alinhamento Tabular à Esquerda Monospaced e Seleção Neutra em Cinzento
    st.markdown("""
    <style>
    div[data-testid="stButton"] {
        width: 100% !important;
    }
    div[data-testid="stButton"] > button {
        font-family: 'Fira Code', 'Courier New', Consolas, monospace !important;
        font-size: 13px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        align-items: center !important;
        white-space: pre !important;
        padding-left: 14px !important;
        padding-right: 14px !important;
        width: 100% !important;
        border-radius: 6px !important;
    }
    div[data-testid="stButton"] > button p {
        text-align: left !important;
        justify-content: flex-start !important;
        width: 100% !important;
        font-family: 'Fira Code', 'Courier New', Consolas, monospace !important;
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #4A5568 !important;
        color: #FFFFFF !important;
        border-color: #718096 !important;
        font-weight: bold !important;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #2D3748 !important;
        border-color: #4A5568 !important;
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

    acoes = api_client.get_acoes()
    if not acoes:
        st.info("Não existem ações de manutenção registadas na plataforma.")
        return

    # Mapeamento de Sistemas para obter nomes de Fábrica, Linha e Sistema
    sistemas_status = api_client.get_sistemas_status()
    map_sistemas = {s["id"]: s for s in sistemas_status} if sistemas_status else {}

    # Filtro de Estado e Pesquisa (ABERTA por defeito)
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_status = st.selectbox("Filtrar por Status", ["ABERTA", "FECHADA", "TODAS"], index=0)
    with col_f2:
        busca_texto = st.text_input("🔍 Procurar por Descrição / ID / Equipamento", "")

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

    st.subheader(f"📋 Ações ({len(acoes_filtradas)}) — Clique numa linha para gerir")

    if not acoes_filtradas:
        st.warning("Nenhuma ação encontrada com os filtros selecionados.")
        return

    # Manter id da ação selecionada em session_state
    selected_id = st.session_state.get("selected_acao_id")

    # Validar se a ação selecionada existe na lista atual
    valid_ids = [a["id"] for a in acoes_filtradas]
    if selected_id not in valid_ids:
        selected_id = valid_ids[0]
        st.session_state["selected_acao_id"] = selected_id

    # Lista de Botões de Linha Inteira com Alinhamento Tabular
    for a in acoes_filtradas:
        is_selected = (a["id"] == selected_id)
        impacto_icon = "🔴" if a.get("impacto") == "TOTAL" else ("🟡" if a.get("impacto") == "PARCIAL" else "🟢")

        # Obter nomes de Fábrica, Linha e Sistema
        sis_info = map_sistemas.get(a.get("sistema_id"), {})
        nome_fabrica = sis_info.get("fabrica", "N/A")
        nome_linha = sis_info.get("linha", "N/A")
        nome_sistema = sis_info.get("nome_sistema", "N/A")

        # Formatação compacta para colunas secundárias e máxima largura para a Descrição
        col_id = pad_or_truncate(f"#{a['id']}", 3)
        col_status = pad_or_truncate(a.get("status", "ABERTA"), 7)
        col_fabrica = pad_or_truncate(nome_fabrica, 8)
        col_linha = pad_or_truncate(nome_linha, 8)
        col_sistema = pad_or_truncate(nome_sistema, 18)
        col_impacto = pad_or_truncate(a.get("impacto", "NENHUM"), 7)
        col_desc = pad_or_truncate(a.get("descricao", ""), 75)
        col_dt = a.get('data_criacao', '')[:10]

        # Constrói o texto da linha-botão
        btn_label = f"{impacto_icon} {col_id} │ {col_status} │ {col_fabrica} │ {col_linha} │ {col_sistema} │ {col_impacto} │ {col_desc} │ {col_dt}"

        if st.button(
            btn_label,
            key=f"btn_row_table_{a['id']}",
            type="primary" if is_selected else "secondary",
            use_container_width=True
        ):
            st.session_state["selected_acao_id"] = a["id"]
            st.rerun()

    # Identificar a ação selecionada e o respetivo equipamento
    acao = next((a for a in acoes_filtradas if a["id"] == selected_id), acoes_filtradas[0])
    sis_sel = map_sistemas.get(acao.get("sistema_id"), {})

    st.markdown("---")
    st.subheader(f"🛠️ Painel de Gestão: Ação #{acao['id']} — {acao.get('descricao', '')[:50]}")

    col_info1, col_info2, col_info3 = st.columns(3)
    with col_info1:
        st.markdown(f"**ID da Ação:** #{acao['id']}")
        st.markdown(f"**Status Atual:** `{acao.get('status')}`")
        st.markdown(f"**Impacto:** `{acao.get('impacto')}`")
    with col_info2:
        st.markdown(f"**Fábrica:** `{sis_sel.get('fabrica', 'N/A')}`")
        st.markdown(f"**Linha:** `{sis_sel.get('linha', 'N/A')}`")
        st.markdown(f"**Sistema:** `{sis_sel.get('nome_sistema', 'N/A')}`")
    with col_info3:
        st.markdown(f"**Data Criação:** {acao.get('data_criacao', 'N/A')}")
        st.markdown(f"**Prev. Conclusão:** {acao.get('data_prevista_conclusao', 'N/A')}")

    st.markdown(f"**Descrição Completa:** {acao.get('descricao')}")
    if acao.get("comentario_fecho"):
        st.markdown(f"**Comentário de Fecho:** {acao.get('comentario_fecho')}")
    if acao.get("data_conclusao"):
        st.markdown(f"**Data de Conclusão:** {acao.get('data_conclusao')}")

    tab_fechar, tab_editar = st.tabs(["✅ Fechar Ação", "✏️ Editar Ação"])

    with tab_fechar:
        if acao.get("status") == "FECHADA":
            st.success("Esta ação já se encontra encerrada.")
        else:
            with st.form(f"form_fechar_{acao['id']}"):
                st.write("### Encerrar Ação de Manutenção")
                data_conclusao = st.date_input("Data de Conclusão", value=date.today(), key=f"dc_{acao['id']}")
                comentario = st.text_area("Comentário Final / Observações do Técnico", placeholder="Descreva os trabalhos efetuados...", key=f"com_{acao['id']}")

                submeter_fecho = st.form_submit_button("Encerrar Ação e Recalcular Equipamento")

                if submeter_fecho:
                    resp = api_client.fechar_acao(
                        acao_id=acao["id"],
                        data_conclusao=str(data_conclusao),
                        comentario=comentario.strip() if comentario else None
                    )
                    if resp.status_code == 200:
                        st.success(f"✅ Ação #{acao['id']} encerrada com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"Erro ao fechar ação: {resp.text}")

    with tab_editar:
        with st.form(f"form_editar_{acao['id']}"):
            st.write("### Editar Dados da Ação")
            nova_desc = st.text_area("Descrição", value=acao.get("descricao", ""), key=f"desc_{acao['id']}")

            impacto_index = 0
            if acao.get("impacto") in ["TOTAL", "PARCIAL", "NENHUM"]:
                impacto_index = ["TOTAL", "PARCIAL", "NENHUM"].index(acao.get("impacto"))

            novo_impacto = st.selectbox(
                "Impacto",
                ["TOTAL", "PARCIAL", "NENHUM"],
                index=impacto_index,
                key=f"imp_{acao['id']}"
            )
            novo_status = st.selectbox(
                "Status",
                ["ABERTA", "FECHADA"],
                index=0 if acao.get("status") == "ABERTA" else 1,
                key=f"st_{acao['id']}"
            )

            default_date = date.today()
            if acao.get("data_prevista_conclusao"):
                try:
                    default_date = date.fromisoformat(acao.get("data_prevista_conclusao"))
                except ValueError:
                    pass

            data_prev = st.date_input("Data Prevista Conclusão", value=default_date, key=f"dp_{acao['id']}")

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
