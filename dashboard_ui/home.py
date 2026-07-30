import streamlit as st
from dashboard_ui import api_client

user = st.session_state.get("user")

st.title("🏭 Visão Geral da Operação Fabril")

if user:
    st.caption(f"Sessão ativa de: **{user.get('nome')}** (`{user.get('email')}`) | Utilize a barra lateral para navegar entre as secções da aplicação.")
else:
    st.caption("Visão geral em tempo real da fábrica. Inicie sessão na barra lateral para aceder a todas as funcionalidades de manutenção.")

# ==========================================
# 1º SECÇÃO: PONTO DE SITUAÇÃO (PDS)
# ==========================================
if not user:
    # 🏢 SEM LOGIN: Exibe o PDS Geral da Fábrica
    st.subheader("🏢 Ponto de Situação Executivo da Fábrica (PDS Geral)")
    st.caption("Resumo inteligente do estado atual da produção e alertas operacionais.")

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🔄 Gerar PDS Geral (IA)", key="btn_pds_geral_home"):
            with st.spinner("A consultar a IA..."):
                texto = api_client.get_pds_geral()
                if texto:
                    st.session_state["pds_geral_texto"] = texto
                else:
                    st.error("Não foi possível gerar o PDS Geral.")

    if "pds_geral_texto" in st.session_state:
        with st.container(border=True):
            st.markdown(st.session_state["pds_geral_texto"])
    else:
        st.info("Clique no botão acima para carregar o resumo inteligente da operação da fábrica.")

else:
    # 👤 COM LOGIN: Exibe o PDS Pessoal do Operador que logou
    st.subheader(f"👤 Ponto de Situação do Turno — {user.get('nome')}")
    st.caption("Briefing personalizado de tarefas e prioridades de manutenção para o teu turno.")

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button(f"🔄 Gerar Briefing para {user.get('nome')}", key="btn_pds_op_home"):
            with st.spinner("A preparar o teu briefing de turno..."):
                texto_op = api_client.get_pds_operador(user.get("id"))
                if texto_op:
                    st.session_state["pds_operador_texto"] = texto_op
                else:
                    st.error("Erro ao gerar briefing de operador.")

    if "pds_operador_texto" in st.session_state:
        with st.container(border=True):
            st.markdown(st.session_state["pds_operador_texto"])
    else:
        st.info(f"Clique no botão acima para gerar o teu briefing personalizado de turno, {user.get('nome')}.")

st.markdown("---")

# ==========================================
# 2º SECÇÃO: SEMÁFOROS / MÉTRICAS DOS EQUIPAMENTOS
# ==========================================
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

# ==========================================
# 3º SECÇÃO: LISTA DOS EQUIPAMENTOS EM TEMPO REAL
# ==========================================
st.subheader("🏭 Estado dos Equipamentos em Tempo Real")

if sistemas:
    def cor_estado(estado):
        if estado == "PARADO":
            return "🔴 PARADO"
        elif estado == "DEGRADADO":
            return "🟡 DEGRADADO"
        return "🟢 OPERACIONAL"

    tabela_dados = []
    for item in sistemas:
        tabela_dados.append({
            "ID": item["id"],
            "Equipamento / Sistema": item["nome_sistema"],
            "Estado Atual": cor_estado(item["estado"]),
            "Linha": item["linha"],
            "Fábrica": item["fabrica"],
            "Fornecedor": item["fornecedor"]
        })

    st.dataframe(tabela_dados, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum sistema registado na base de dados.")
