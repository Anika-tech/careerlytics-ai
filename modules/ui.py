from pathlib import Path
import sys
import streamlit as st
from modules.auth import clear_user_session, render_auth_gate

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def setup_page(title):
    st.set_page_config(page_title=f"{title} | CAREERLYTICS AI", page_icon="✨", layout="wide")
    css = ROOT / "assets" / "styles.css"
    if css.exists():
        st.markdown(f"<style>{css.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    if not render_auth_gate():
        st.stop()

    with st.sidebar:
        st.markdown("<div class='brand'><span class='brand-mark'>CA</span><div><b>CAREERLYTICS</b><small>AI CAREER INTELLIGENCE</small></div></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.page_link("pages/1_Dashboard.py", label="Dashboard", icon="📊")
        st.page_link("pages/2_Resume_Upload.py", label="Resume Upload", icon="📄")
        st.page_link("pages/3_Resume_Analysis.py", label="AI Analysis", icon="✨")
        st.page_link("pages/4_Job_Recommendations.py", label="Job Matches", icon="🎯")
        st.page_link("pages/5_Skill_Gap_Analysis.py", label="Skill Gap", icon="🧩")
        st.page_link("pages/6_Career_Insights.py", label="Career Insights", icon="📈")
        st.page_link("pages/7_About.py", label="About & Datasets", icon="ℹ️")
        st.markdown("---")
        st.caption(f"Signed in as {st.session_state['authenticated_user']}")
        if st.button("Log out", use_container_width=True):
            clear_user_session()
            st.rerun()


def page_header(kicker, title, subtitle):
    st.markdown(f"<div class='eyebrow'>{kicker}</div><h1>{title}</h1><p style='color:#97a1b7'>{subtitle}</p>", unsafe_allow_html=True)
