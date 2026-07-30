import streamlit as st
from dashboard_ui.auth_guard import check_authentication
from dashboard_ui.views.registar_acao_view import render_registar_acao_view

st.set_page_config(page_title="Registar Ação", page_icon="➕", layout="wide")

check_authentication()
render_registar_acao_view()
