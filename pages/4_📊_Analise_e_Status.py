import streamlit as st
from dashboard_ui.auth_guard import check_authentication
from dashboard_ui.views.analise_status_view import render_analise_status_view

st.set_page_config(page_title="Análise & Status", page_icon="📊", layout="wide")

check_authentication()
render_analise_status_view()
