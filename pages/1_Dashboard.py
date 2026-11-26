import pandas as pd
import plotly.express as px
import streamlit as st

from modules.data_loader import detect_columns, load_job_dataset, load_resume_dataset
from modules.skills_extractor import SOFT_SKILLS, TECHNICAL_SKILLS
from modules.ui import setup_page
from modules.visualizations import chart_layout, recommendation_chart


setup_page("Dashboard")
st.markdown("<div class='eyebrow'>CAREER INTELLIGENCE</div>", unsafe_allow_html=True)
st.title("Career dashboard")
st.caption("Explore the job-market dataset and your current resume analysis in one place.")

jobs, jobs_error = load_job_dataset()
resumes, resumes_error = load_resume_dataset()

if jobs_error:
    st.error(jobs_error)
if resumes_error:
    st.warning(resumes_error)

job_count = len(jobs) if jobs is not None else 0
category_count = 0
if resumes is not None:
    category_col = detect_columns(resumes, ["category", "resume_category", "job_category", "label"])
    category_count = resumes[category_col].nunique() if category_col else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Listings in dataset", f"{job_count:,}", help="Historical Kaggle records; verify current availability before applying.")
m2.metric("Resume categories", f"{category_count:,}")
m3.metric("Skills recognized", f"{len(TECHNICAL_SKILLS) + len(SOFT_SKILLS)}")
m4.metric("Resume status", "Analyzed" if "resume" in st.session_state else "Not uploaded")

if jobs is not None and not jobs.empty:
    industry_col = detect_columns(jobs, ["industry", "job_category", "category"])
    title_col = detect_columns(jobs, ["jobtitle", "job_title", "title", "role"])
    location_col = detect_columns(jobs, ["joblocation_address", "location", "job_location"])
    date_col = detect_columns(jobs, ["postdate", "posted_date", "date"])

    left, right = st.columns([1.7, 1])
    with left:
        st.markdown(
            "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Role landscape</h3>"
            "<div class='dashboard-subtitle'>Most represented industries in the Kaggle job listings</div></div>"
            "<span class='data-tag'>DATASET</span></div></div>",
            unsafe_allow_html=True,
        )
        if industry_col:
            industries = jobs[industry_col].astype(str).str.strip()
            industries = industries[industries.ne("")].value_counts().head(9).sort_values()
            fig = px.bar(
                x=industries.values, y=industries.index, orientation="h",
                color=industries.values,
                color_continuous_scale=["#394a73", "#7666e8", "#41c99b"],
                labels={"x": "Listings", "y": ""},
            )
            fig.update_layout(title="", coloraxis_showscale=False, yaxis={"automargin": True})
            st.plotly_chart(chart_layout(fig, 340), use_container_width=True)
        else:
            st.info("The job dataset does not include an industry/category column.")

    with right:
        st.markdown(
            "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Location signals</h3>"
            "<div class='dashboard-subtitle'>Most frequent listed locations</div></div></div></div>",
            unsafe_allow_html=True,
        )
        if location_col:
            locations = (
                jobs[location_col].fillna("").astype(str).str.split(",").explode().str.strip()
            )
            locations = locations[locations.str.len().gt(1)].value_counts().head(7).sort_values()
            fig = px.bar(
                x=locations.values, y=locations.index, orientation="h",
                color_discrete_sequence=["#8170f8"],
                labels={"x": "Mentions", "y": ""},
            )
            fig.update_layout(title="", yaxis={"automargin": True})
            st.plotly_chart(chart_layout(fig, 340), use_container_width=True)
        else:
            st.info("The job dataset does not include a location column.")

    bottom_left, bottom_right = st.columns([1.25, 1])
    with bottom_left:
        st.markdown(
            "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Posting timeline</h3>"
            "<div class='dashboard-subtitle'>Records by month in the source dataset</div></div></div></div>",
            unsafe_allow_html=True,
        )
        if date_col:
            dates = pd.to_datetime(jobs[date_col], errors="coerce", utc=True).dropna()
            if not dates.empty:
                monthly = dates.dt.strftime("%Y-%m").value_counts().sort_index()
                fig = px.area(
                    x=monthly.index, y=monthly.values,
                    color_discrete_sequence=["#8b70f8"],
                    labels={"x": "Posting month", "y": "Listings"},
                )
                fig.update_traces(
                    line={"color": "#8b70f8", "width": 2},
                    fillcolor="rgba(139,112,248,.18)",
                )
                fig.update_layout(title="")
                st.plotly_chart(chart_layout(fig, 285), use_container_width=True)
            else:
                st.info("No valid posting dates were found in this dataset.")
        else:
            st.info("The job dataset does not include posting dates.")

    with bottom_right:
        st.markdown(
            "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Your profile</h3>"
            "<div class='dashboard-subtitle'>Current session summary</div></div></div></div>",
            unsafe_allow_html=True,
        )
        resume = st.session_state.get("resume")
        if resume:
            st.markdown(f"**{resume.get('name') or 'Resume profile'}**")
            st.write(f"{len(resume.get('technical_skills', []))} technical skills detected")
            st.write(f"{len(resume.get('education', []))} education entries detected")
            if st.button("Open resume analysis", use_container_width=True):
                st.switch_page("pages/3_Resume_Analysis.py")
        else:
            st.write("Upload a PDF to build your profile and compare it with these dataset listings.")
            if st.button("Upload resume", type="primary", use_container_width=True):
                st.switch_page("pages/2_Resume_Upload.py")

if "recommendations" in st.session_state and not st.session_state["recommendations"].empty:
    st.markdown("### Recent role matches")
    st.caption("Compatibility scores compare resume content with dataset descriptions; they are not hiring probabilities.")
    st.plotly_chart(recommendation_chart(st.session_state["recommendations"].head(5)), use_container_width=True)
