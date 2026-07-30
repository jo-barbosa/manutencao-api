import streamlit as st
from dashboard_ui.auth_guard import check_authentication
from dashboard_ui.views.estrutura_view import render_estrutura_view

st.set_page_config(page_title="Estrutura & Equipamentos", page_icon="⚙️", layout="wide")

check_authentication()
render_estrutura_view()
