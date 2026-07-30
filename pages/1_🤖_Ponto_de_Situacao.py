import streamlit as st
from dashboard_ui.auth_guard import check_authentication
from dashboard_ui.views.pds_view import render_pds_view

st.set_page_config(page_title="Ponto de Situação (IA)", page_icon="🤖", layout="wide")

check_authentication()
render_pds_view()
