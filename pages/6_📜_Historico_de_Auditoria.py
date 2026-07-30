import streamlit as st
from dashboard_ui.auth_guard import check_authentication
from dashboard_ui.views.auditoria_view import render_auditoria_view

st.set_page_config(page_title="Histórico de Auditoria", page_icon="📜", layout="wide")

check_authentication()
render_auditoria_view()
