import streamlit as st

from modules.data_loader import load_job_dataset
from modules.job_recommender import build_apply_search_url, recommend_jobs
from modules.ui import setup_page
from modules.visualizations import recommendation_chart, score_gauge, skill_radar_chart


setup_page("Job Recommendations")
st.markdown("<div class='eyebrow'>ROLE DISCOVERY</div>", unsafe_allow_html=True)
st.title("Job matches")
st.caption("Explore roles ranked by resume and listing similarity. Compatibility is not a hiring probability.")

if "resume" not in st.session_state:
    st.info("Upload a resume to discover matching roles.")
    if st.button("Upload resume", type="primary"):
        st.switch_page("pages/2_Resume_Upload.py")
    st.stop()

jobs, job_error = load_job_dataset()
if job_error:
    st.error(job_error)
    st.stop()

if st.button("Refresh top 10 matches", type="primary"):
    with st.spinner("Ranking jobs against your resume. The first run builds a reusable local index."):
        st.session_state["recommendations"] = recommend_jobs(
            st.session_state["resume"]["text"],
            jobs,
            top_n=10,
            resume_skills=st.session_state["resume"]["technical_skills"],
            predicted_category=st.session_state.get("resume_category"),
        )

if "recommendations" not in st.session_state:
    st.markdown(
        "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Ready to explore?</h3>"
        "<div class='dashboard-subtitle'>Rank the real listings in the downloaded Kaggle dataset against your profile.</div></div></div></div>",
        unsafe_allow_html=True,
    )
    st.stop()

recommendations = st.session_state["recommendations"]
if recommendations.empty:
    st.warning("No job recommendations were returned for this resume.")
    st.stop()

f1, f2, f3, f4, f5 = st.columns([1.2, 1, 1, 1, 1])
title_filter = f1.text_input("Role")
location_filter = f2.text_input("Location")
company_filter = f3.text_input("Company")
experience_filter = f4.text_input("Experience")
minimum = f5.slider("Minimum match", 0, 100, 0)

filtered = recommendations.copy()
if title_filter:
    filtered = filtered[filtered["job_title"].str.contains(title_filter, case=False, na=False)]
if location_filter:
    filtered = filtered[filtered["location"].str.contains(location_filter, case=False, na=False)]
if company_filter:
    filtered = filtered[filtered["company"].str.contains(company_filter, case=False, na=False)]
if experience_filter:
    filtered = filtered[filtered["experience"].str.contains(experience_filter, case=False, na=False)]
filtered = filtered[filtered["compatibility"] >= minimum].sort_values("compatibility", ascending=False)

if filtered.empty:
    st.warning("No matches meet these filters. Adjust the filters or lower the minimum score.")
    st.stop()

best = filtered.iloc[0]
matching_count = len(best["matching_skills"])
missing_count = len(best["missing_skills"])
k1, k2, k3, k4 = st.columns(4)
k1.metric("Roles shown", len(filtered))
k2.metric("Best compatibility", f"{best['compatibility']:.1f}%")
k3.metric("Skills matched in top role", matching_count)
k4.metric("More skills detected in listing", missing_count)

list_col, insight_col = st.columns([1.45, 1])
with list_col:
    st.markdown("### Ranked opportunities")
    for position, (_, job) in enumerate(filtered.iterrows(), start=1):
        with st.container(border=True):
            title_col, score_col = st.columns([4, 1])
            with title_col:
                st.markdown(f"#### {position:02d} · {job['job_title']}")
                st.caption(f"{job['company']}  ·  {job['location']}  ·  Experience: {job['experience']}")
            with score_col:
                st.metric("Match", f"{job['compatibility']:.1f}%")

            match_tags = " ".join(
                f"<span class='data-tag'>{skill}</span>" for skill in job["matching_skills"][:8]
            )
            st.markdown(match_tags or "<span class='metric-note'>No direct skill overlap detected.</span>", unsafe_allow_html=True)

            with st.expander("Description and skill details"):
                st.write(job["description"][:1200] or "No description was included in this listing.")
                d1, d2 = st.columns(2)
                d1.write("**Matching skills**")
                d1.write(", ".join(job["matching_skills"]) or "None detected")
                d2.write("**Other detected listing skills**")
                d2.write(", ".join(job["missing_skills"][:12]) or "None detected")

            st.link_button(
                "Find & Apply on Naukri",
                build_apply_search_url(job["job_title"], job["company"], job["location"]),
            )
            st.caption("Opens a Naukri-focused web search; the dataset does not provide direct application links.")

with insight_col:
    st.markdown("### Match signals")
    st.plotly_chart(
        score_gauge(best["compatibility"], "Top role compatibility"),
        use_container_width=True,
        config={"displayModeBar": False},
    )
    st.plotly_chart(
        recommendation_chart(filtered),
        use_container_width=True,
        config={"displayModeBar": False},
    )
    selected_index = st.selectbox(
        "Compare skills for role",
        options=list(range(len(filtered))),
        format_func=lambda index: str(filtered.iloc[index]["job_title"]),
    )
    selected = filtered.iloc[selected_index]
    target_skills = selected["matching_skills"] + selected["missing_skills"]
    st.plotly_chart(
        skill_radar_chart(
            st.session_state["resume"]["technical_skills"],
            target_skills,
            f"Skills · {selected['job_title'][:32]}",
        ),
        use_container_width=True,
        config={"displayModeBar": False},
    )
