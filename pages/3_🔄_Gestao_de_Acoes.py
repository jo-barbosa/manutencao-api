import streamlit as st
from dashboard_ui.auth_guard import check_authentication
from dashboard_ui.views.gestao_acoes_view import render_gestao_acoes_view

st.set_page_config(page_title="Gestão de Ações", page_icon="🔄", layout="wide")

check_authentication()
render_gestao_acoes_view()
