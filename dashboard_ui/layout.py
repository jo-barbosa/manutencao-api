import base64
from pathlib import Path
import streamlit as st

# Localiza a pasta raiz do projeto (um nível acima de dashboard_ui)
BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "dashboard_ui" / "assets" / "IKEA_logo.png"


def get_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def render_header():
    if LOGO_PATH.exists():
        img_b64 = get_image_base64(LOGO_PATH)
        header_html = f"""
        <div style="display: flex; align-items: center; justify-content: space-between; padding-bottom: 10px; border-bottom: 2px solid #f0f2f6; margin-bottom: 20px;">
            <img src="data:image/png;base64,{img_b64}" style="height: 45px; object-fit: contain;">
            <span style="color: #6c757d; font-size: 0.95rem; font-weight: 500;">
                ⚙️ Sistema de Gestão de ações
            </span>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
    else:
        st.title("IKEA Industry Paços de Ferreira")
        st.divider()