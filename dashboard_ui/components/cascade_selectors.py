from typing import Tuple, Optional, List, Dict, Any
import streamlit as st
from dashboard_ui import api_client


def render_cascade_selectors(
    key_prefix: str = "cascade",
    show_all_option: bool = True
) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Renderiza 3 selectboxes encadeados (Fábrica -> Linha -> Sistema).
    Retorna a tupla (fabrica_id, linha_id, sistema_id).
    """
    col1, col2, col3 = st.columns(3)

    # 1. Fábrica
    fabricas = api_client.get_fabricas()
    fabrica_options: Dict[str, Optional[int]] = {}
    if show_all_option:
        fabrica_options["Todas as Fábricas"] = None
    for f in fabricas:
        fabrica_options[f"{f['nome']} ({f.get('localizacao', 'N/A')})"] = f["id"]

    with col1:
        sel_fabrica_label = st.selectbox(
            "Fábrica",
            options=list(fabrica_options.keys()),
            key=f"{key_prefix}_fabrica"
        )
        selected_fabrica_id = fabrica_options[sel_fabrica_label]

    # 2. Linha (filtrada pela fábrica)
    linhas = api_client.get_linhas(selected_fabrica_id)
    linha_options: Dict[str, Optional[int]] = {}
    if show_all_option:
        linha_options["Todas as Linhas"] = None
    for l in linhas:
        linha_options[l["nome"]] = l["id"]

    with col2:
        sel_linha_label = st.selectbox(
            "Linha",
            options=list(linha_options.keys()) if linha_options else ["Nenhuma linha encontrada"],
            key=f"{key_prefix}_linha"
        )
        selected_linha_id = linha_options.get(sel_linha_label) if linha_options else None

    # 3. Sistema (filtrado pela linha)
    sistemas = api_client.get_sistemas(selected_linha_id)
    sistema_options: Dict[str, Optional[int]] = {}
    if show_all_option:
        sistema_options["Todos os Sistemas"] = None
    for s in sistemas:
        sistema_options[f"{s['nome']} (Estado: {s['estado_atual']})"] = s["id"]

    with col3:
        sel_sistema_label = st.selectbox(
            "Sistema / Equipamento",
            options=list(sistema_options.keys()) if sistema_options else ["Nenhum sistema encontrado"],
            key=f"{key_prefix}_sistema"
        )
        selected_sistema_id = sistema_options.get(sel_sistema_label) if sistema_options else None

    return selected_fabrica_id, selected_linha_id, selected_sistema_id
