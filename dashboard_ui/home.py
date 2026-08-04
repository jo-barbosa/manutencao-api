import streamlit as st
from dashboard_ui import api_client, layout

user = st.session_state.get("user")
layout.render_header()

st.title("🏭 Visão Geral dos Sistemas")

if user:
    st.caption(f"Sessão ativa de: **{user.get('nome')}** (`{user.get('email')}`) | Utilize a barra lateral para navegar entre as secções da aplicação.")
else:
    st.caption("Visão geral em tempo real dos sistemas. Inicie sessão na barra lateral para aceder a todas as funcionalidades da aplicação.")

# ==========================================
# 1º SECÇÃO: MÉTRICAS GERAIS DOS EQUIPAMENTOS
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
# 2º SECÇÃO: ESTADO DOS EQUIPAMENTOS EM TEMPO REAL (3 COLUNAS - 1 POR FÁBRICA)
# ==========================================
st.subheader("🏭 Estado dos Equipamentos")

fabricas_raw = api_client.get_fabricas()
# Obter até 3 fábricas para as 3 colunas
if fabricas_raw:
    fabricas_nomes = [f["nome"] for f in fabricas_raw[:3]]
else:
    # Fallback para fábricas existentes nos sistemas registados
    fabricas_nomes = list(dict.fromkeys([s["fabrica"] for s in sistemas if s.get("fabrica")]))[:3]

# Garantir exatamente 3 colunas (1 por fábrica)
cols_fabrica = st.columns(3)

def render_status_badge(estado: str) -> str:
    """Gera o HTML do quadrado semáforo à direita da mini-tabela."""
    if estado == "PARADO":
        bg_color = "#DC2626"
        icon = "🔴"
        label = "PARADO"
    elif estado == "DEGRADADO":
        bg_color = "#D97706"
        icon = "🟡"
        label = "DEGRADADO"
    else:
        bg_color = "#059669"
        icon = "🟢"
        label = "OPERACIONAL"

    return f"""
    <div style="
        background-color: {bg_color};
        color: white;
        border-radius: 8px;
        height: 100%;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 11px;
        text-align: center;
        padding: 4px;
        margin: auto;
    ">
        <span style="font-size: 20px; line-height: 1.2;">{icon}</span>
        <span style="letter-spacing: 0.5px;">{label}</span>
    </div>
    """

# Agrupar sistemas por fábrica
sistemas_por_fabrica = {}
for item in sistemas:
    fab = item.get("fabrica", "Outras")
    if fab not in sistemas_por_fabrica:
        sistemas_por_fabrica[fab] = []
    sistemas_por_fabrica[fab].append(item)

# Preencher cada uma das 3 colunas de fábrica
for idx in range(3):
    with cols_fabrica[idx]:
        if idx < len(fabricas_nomes):
            nome_fabrica = fabricas_nomes[idx]
            st.markdown(f"### 🏢 {nome_fabrica}")

            sistemas_fab = sistemas_por_fabrica.get(nome_fabrica, [])
            if sistemas_fab:
                for sys in sistemas_fab:
                    with st.container(border=True):
                        c_info, c_badge = st.columns([3, 1.2])
                        with c_info:
                            st.markdown(f"**⚙️ {sys['nome_sistema']}**")
                            st.markdown(f"<small>📍 **Linha:** {sys['linha']}</small>", unsafe_allow_html=True)
                            st.markdown(f"<small>🔧 **Fornecedor:** {sys['fornecedor']}</small>", unsafe_allow_html=True)
                        with c_badge:
                            st.markdown(render_status_badge(sys["estado"]), unsafe_allow_html=True)
            else:
                st.caption("Nenhum equipamento registado nesta fábrica.")
        else:
            st.markdown("### 🏢 (Sem Fábrica)")
            st.caption("Sem dados.")
