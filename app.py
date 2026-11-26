import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import ASSET_DIR
from modules.auth import render_auth_gate

st.set_page_config(
    page_title="CAREERLYTICS AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = ASSET_DIR / "styles.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

if not render_auth_gate():
    st.stop()

st.switch_page("pages/1_Dashboard.py")
