import streamlit as st

from modules.skill_gap import calculate_skill_gap
from modules.ui import setup_page
from modules.visualizations import skill_gap_chart, skill_radar_chart


setup_page("Skill Gap")
st.markdown("<div class='eyebrow'>CAREER DEVELOPMENT</div>", unsafe_allow_html=True)
st.title("Your skills")
st.caption("Compare skills detected in your resume with those found in recommended job listings.")

if "resume" not in st.session_state:
    st.info("Upload a resume to review your skill profile.")
    if st.button("Upload resume", type="primary"):
        st.switch_page("pages/2_Resume_Upload.py")
    st.stop()
if "recommendations" not in st.session_state or st.session_state["recommendations"].empty:
    st.info("Generate job recommendations first so skill comparisons are based on real listings.")
    if st.button("Open job matches"):
        st.switch_page("pages/4_Job_Recommendations.py")
    st.stop()

resume = st.session_state["resume"]
recommendations = st.session_state["recommendations"]
required = set()
for _, job in recommendations.iterrows():
    required.update(job["matching_skills"])
    required.update(job["missing_skills"])

gap = calculate_skill_gap(resume["technical_skills"], required)
match_rate = round(100 * len(gap["matching"]) / len(required)) if required else 0

left, center, right = st.columns([1.05, 1.7, 1.1])
with left:
    st.markdown(
        "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Profile snapshot</h3>"
        "<div class='dashboard-subtitle'>Detected from your uploaded resume</div></div>"
        "<span class='status-dot'></span></div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"### {resume.get('name') or 'Your profile'}")
    st.caption(st.session_state.get("resume_category") or "Category not classified")
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.write("**Technical skills**")
    skill_tags = " ".join(
        f"<span class='data-tag'>{skill}</span>" for skill in resume["technical_skills"][:20]
    )
    st.markdown(skill_tags or "<span class='metric-note'>No technical skills detected.</span>", unsafe_allow_html=True)
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.metric("Role skill overlap", f"{match_rate}%")
    st.caption("Share of detected requirements across the recommended role set.")
    st.markdown("</div>", unsafe_allow_html=True)

with center:
    st.markdown(
        "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Skills against target roles</h3>"
        "<div class='dashboard-subtitle'>Current detected skills compared with job listing requirements</div></div></div></div>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        skill_radar_chart(resume["technical_skills"], sorted(required, key=str.lower)),
        use_container_width=True,
        config={"displayModeBar": False},
    )
    st.plotly_chart(
        skill_gap_chart(gap),
        use_container_width=True,
        config={"displayModeBar": False},
    )

with right:
    st.markdown(
        "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Learning focus</h3>"
        "<div class='dashboard-subtitle'>Topics related to skills found in recommended listings</div></div></div></div>",
        unsafe_allow_html=True,
    )
    if gap["suggestions"]:
        for item in gap["suggestions"][:8]:
            with st.expander(item["skill"].title()):
                for topic in item["topics"]:
                    st.write(f"- {topic}")
    else:
        st.success("No missing skill keywords were detected for these roles.")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("#### Recommended roles")
    for _, job in recommendations.head(5).iterrows():
        st.write(f"**{job['job_title']}**")
        st.caption(f"{job['compatibility']:.1f}% compatibility · {job['company']}")

st.markdown("### Skill summary")
matched_col, missing_col = st.columns(2)
with matched_col:
    st.markdown(
        "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Matching skills</h3>"
        "<div class='dashboard-subtitle'>Detected in resume and in at least one recommended listing</div></div></div></div>",
        unsafe_allow_html=True,
    )
    st.write(", ".join(gap["matching"]) or "No direct overlap detected.")
with missing_col:
    st.markdown(
        "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Other role requirements</h3>"
        "<div class='dashboard-subtitle'>Keywords seen in listings but not detected in the resume</div></div></div></div>",
        unsafe_allow_html=True,
    )
    st.write(", ".join(gap["missing"]) or "No missing keywords detected.")

st.caption("A missing keyword is not proof of missing ability. Suggestions are study topics, not endorsements of specific courses.")
