import streamlit as st
from modules.ui import setup_page, page_header
from modules.data_loader import load_resume_dataset, load_job_dataset

setup_page("About")
page_header("PROJECT OVERVIEW", "About CAREERLYTICS AI", "Decode Your Potential. Discover Your Next Opportunity.")

st.markdown("""
### Objective
CAREERLYTICS AI helps students and job seekers understand resume content, identify skill gaps,
and explore locally available job opportunities.

### Proposed solution
The system combines document parsing, NLP, TF-IDF, cosine similarity, supervised category
classification, skill extraction, and weighted compatibility ranking. It is decision-support
software and does not automate hiring decisions.

### Technology
- Streamlit and custom CSS
- Python, Pandas, NumPy
- PyMuPDF
- Scikit-learn TF-IDF and Logistic Regression
- Plotly
- Joblib

### Workflow
PDF upload → text extraction → profile parsing → resume quality and category analysis →
job similarity and skill matching → ranked recommendations → skill-gap learning suggestions

### Limitations
Extraction quality depends on resume formatting. Scanned PDFs require OCR, which is not enabled
by default. Missing keywords do not prove an absence of proficiency. The uploaded PDF is held in
memory only. Recommendations are not guaranteed hiring probabilities or ATS scores.
""")

resume_df, resume_error = load_resume_dataset()
job_df, job_error = load_job_dataset()

st.markdown("### Dataset Information")
c1, c2 = st.columns(2)
for col, title, df, error in [
    (c1, "Updated Resume Dataset", resume_df, resume_error),
    (c2, "Jobs on Naukri.com", job_df, job_error),
]:
    with col:
        st.markdown(f"<div class='glass-card'><h3>{title}</h3>", unsafe_allow_html=True)
        if error:
            st.error(error)
        else:
            st.write(f"**Records:** {len(df):,}")
            st.write(f"**Columns:** {len(df.columns)}")
            st.write(f"**Missing values:** {int(df.isna().sum().sum())}")
            st.write(f"**Duplicate rows after load:** 0")
            st.write("**Preprocessing status:** Loaded and cleaned")
        st.markdown("</div>", unsafe_allow_html=True)

st.info("Dataset sources: Updated Resume Dataset and Jobs on Naukri.com from Kaggle.")
