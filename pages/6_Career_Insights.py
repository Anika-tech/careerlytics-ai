import streamlit as st
import pandas as pd
from modules.ui import setup_page, page_header
from modules.data_loader import load_job_dataset
from modules.visualizations import category_chart
from modules.skills_extractor import extract_technical_skills

setup_page("Career Insights")
page_header("MARKET INTELLIGENCE", "Career insights", "Explore role distribution and recurring skill signals in the local job dataset.")

job_df, error = load_job_dataset()
if error:
    st.error(error)
elif "resume" not in st.session_state:
    st.info("Upload a resume to unlock profile-oriented insights.")
else:
    resume = st.session_state["resume"]
    title_col = next((c for c in job_df.columns if str(c).lower().strip() in
                      ("job_title", "title", "role", "designation", "job_role")), job_df.columns[0])

    counts = job_df[title_col].astype(str).str.extract(r"^([^(/,|-]+)", expand=False).str.strip().value_counts().head(12)
    left, right = st.columns([1.4, 1])
    with left:
        st.plotly_chart(category_chart(counts), use_container_width=True)
    with right:
        st.markdown("<div class='glass-card'><h3>Profile Signals</h3>", unsafe_allow_html=True)
        st.write("**Predicted category:**", st.session_state.get("resume_category") or "Not available")
        if "recommendations" in st.session_state:
            top_roles = st.session_state["recommendations"].head(5)["job_title"].tolist()
            st.write("**Most compatible roles:**")
            for role in top_roles:
                st.write(f"- {role}")
        st.markdown("</div>", unsafe_allow_html=True)

    text_columns = [c for c in job_df.columns if any(k in str(c).lower() for k in ("description", "skill", "detail", "title"))]
    combined = " ".join(job_df[text_columns].astype(str).agg(" ".join, axis=1).tolist()) if text_columns else ""
    frequency = {}
    for skill in extract_technical_skills(combined):
        frequency[skill] = combined.lower().count(skill.lower())
    frequent = pd.Series(frequency).sort_values(ascending=False).head(15)

    st.markdown("### Skills Frequently Required")
    if not frequent.empty:
        for skill, count in frequent.items():
            st.progress(min(1.0, count / max(frequent.values)), text=f"{skill.title()} · {count} mentions")
    else:
        st.write("No recognized skills found in the available job text.")
