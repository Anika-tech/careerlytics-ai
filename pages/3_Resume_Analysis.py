import streamlit as st

from modules.data_loader import load_resume_dataset
from modules.resume_classifier import predict_category, train_resume_classifier
from modules.ui import setup_page
from modules.visualizations import (
    recommendation_skill_heatmap,
    score_gauge,
    skill_mix_chart,
    skill_radar_chart,
)


setup_page("AI Resume Analysis")
st.markdown("<div class='eyebrow'>PROFILE INTELLIGENCE</div>", unsafe_allow_html=True)
st.title("At a glance")
st.caption("A structured view of the profile information extracted from your resume.")

if "resume" not in st.session_state:
    st.info("Upload a PDF resume to generate your analysis.")
    if st.button("Go to resume upload", type="primary"):
        st.switch_page("pages/2_Resume_Upload.py")
    st.stop()

resume = st.session_state["resume"]
sections = {
    "Contact details": bool(resume.get("email") or resume.get("phone")),
    "Education": bool(resume.get("education")),
    "Experience": bool(resume.get("experience")),
    "Projects": bool(resume.get("projects")),
    "Certifications": bool(resume.get("certifications")),
    "Technical skills": bool(resume.get("technical_skills")),
}
quality = min(
    100,
    25
    + sum(sections.values()) * 9
    + min(len(resume.get("technical_skills", [])), 8) * 2
    + min(len(resume.get("soft_skills", [])), 5),
)

resume_df, resume_error = load_resume_dataset()
if "resume_category" not in st.session_state:
    st.session_state["resume_category"] = None
if st.session_state["resume_category"] is None and not resume_error:
    with st.spinner("Classifying resume against the supplied resume dataset..."):
        try:
            _, _, metrics = train_resume_classifier(resume_df)
            st.session_state["classifier_metrics"] = metrics
            st.session_state["resume_category"] = predict_category(resume["text"])
        except (ValueError, OSError) as exc:
            st.warning(f"Resume classification is unavailable: {exc}")

summary, profile, match = st.columns([1.1, 1.4, 1.15])
with summary:
    st.plotly_chart(score_gauge(quality), use_container_width=True, config={"displayModeBar": False})
    st.caption("Content completeness indicator only — not an ATS score.")
with profile:
    st.markdown(
        "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Candidate profile</h3>"
        "<div class='dashboard-subtitle'>Extracted from the uploaded document</div></div>"
        "<span class='status-dot'></span></div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"### {resume.get('name') or 'Resume profile'}")
    st.write(resume.get("email") or "Email not detected")
    st.write(resume.get("phone") or "Phone not detected")
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.write("**Predicted resume category**")
    st.write(st.session_state.get("resume_category") or "Not available")
    st.write("**Education**")
    st.write(", ".join(resume.get("education", [])) or "No education entry detected")
    st.markdown("</div>", unsafe_allow_html=True)
with match:
    recs = st.session_state.get("recommendations")
    if recs is not None and not recs.empty:
        best = recs.iloc[0]
        st.markdown(
            "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Top role match</h3>"
            "<div class='dashboard-subtitle'>Dataset compatibility, not hiring probability</div></div>"
            "<span class='data-tag'>TOP MATCH</span></div></div>",
            unsafe_allow_html=True,
        )
        st.metric("Compatibility", f"{best['compatibility']:.1f}%")
        st.write(best["job_title"])
        st.caption(f"{best['company']} · {best['location']}")
    else:
        st.markdown(
            "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Job match</h3>"
            "<div class='dashboard-subtitle'>Compare this profile with the job dataset</div></div></div></div>",
            unsafe_allow_html=True,
        )
        st.write("Generate recommendations to see a role-specific compatibility score.")
        if st.button("Explore job matches", use_container_width=True):
            st.switch_page("pages/4_Job_Recommendations.py")

if "classifier_metrics" in st.session_state:
    metrics = st.session_state["classifier_metrics"]
    st.markdown("#### Resume category model evaluation")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accuracy", f"{metrics['accuracy']:.1%}")
    c2.metric("Precision", f"{metrics['precision']:.1%}")
    c3.metric("Recall", f"{metrics['recall']:.1%}")
    c4.metric("F1-score", f"{metrics['f1']:.1%}")

st.markdown("### Skill profile")
skill_col, heat_col = st.columns([1, 1.45])
with skill_col:
    st.plotly_chart(
        skill_mix_chart(resume.get("technical_skills", []), resume.get("soft_skills", [])),
        use_container_width=True,
        config={"displayModeBar": False},
    )
with heat_col:
    recs = st.session_state.get("recommendations")
    if recs is not None and not recs.empty:
        st.plotly_chart(
            recommendation_skill_heatmap(recs, resume.get("technical_skills", [])),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    else:
        st.plotly_chart(
            skill_radar_chart(resume.get("technical_skills", []), []),
            use_container_width=True,
            config={"displayModeBar": False},
        )

section_col, project_col, experience_col = st.columns([1, 1.1, 1.1])
with section_col:
    st.markdown(
        "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Profile checklist</h3>"
        "<div class='dashboard-subtitle'>Sections detected from the document</div></div></div></div>",
        unsafe_allow_html=True,
    )
    for label, present in sections.items():
        st.write(f"{'●' if present else '○'}  {label}")

with project_col:
    st.markdown(
        "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Projects & credentials</h3>"
        "<div class='dashboard-subtitle'>Extracted resume sections</div></div></div></div>",
        unsafe_allow_html=True,
    )
    st.write("**Projects**")
    for item in resume.get("projects", [])[:4]:
        st.write(f"- {item}")
    if not resume.get("projects"):
        st.caption("No project section detected.")
    st.write("**Certifications**")
    for item in resume.get("certifications", [])[:4]:
        st.write(f"- {item}")
    if not resume.get("certifications"):
        st.caption("No certification section detected.")

with experience_col:
    st.markdown(
        "<div class='dashboard-panel'><div class='dashboard-heading'><div><h3>Experience</h3>"
        "<div class='dashboard-subtitle'>Extracted text, not independently verified</div></div></div></div>",
        unsafe_allow_html=True,
    )
    st.write(resume.get("experience", "")[:1200] or "No experience section detected.")

report_lines = [
    "CAREERLYTICS AI - Resume Profile",
    f"Name: {resume.get('name') or 'Not detected'}",
    f"Email: {resume.get('email') or 'Not detected'}",
    f"Phone: {resume.get('phone') or 'Not detected'}",
    f"Predicted category: {st.session_state.get('resume_category') or 'Not available'}",
    f"Content completeness indicator: {quality}/100 (not an ATS score)",
    f"Technical skills: {', '.join(resume.get('technical_skills', []))}",
    f"Soft skills: {', '.join(resume.get('soft_skills', []))}",
]
st.download_button(
    "Download profile summary",
    "\n".join(report_lines),
    file_name="careerlytics_resume_summary.txt",
    mime="text/plain",
)
