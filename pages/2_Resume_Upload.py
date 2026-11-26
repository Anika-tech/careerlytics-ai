import streamlit as st
from modules.ui import setup_page, page_header
from modules.resume_parser import extract_pdf_text, parse_resume_text

setup_page("Resume Upload")
page_header("SOURCE DOCUMENT", "Upload your resume", "The PDF is processed locally and is not retained permanently.")

uploaded = st.file_uploader("Drop your resume PDF here", type=["pdf"], accept_multiple_files=False)

if uploaded:
    if uploaded.size > 10 * 1024 * 1024:
        st.error("Please upload a PDF smaller than 10 MB.")
    elif not uploaded.name.lower().endswith(".pdf"):
        st.error("Only PDF files are supported.")
    else:
        if st.button("Analyze PDF", type="primary"):
            try:
                text = extract_pdf_text(uploaded)
                parsed = parse_resume_text(text)
                st.session_state["resume"] = parsed
                st.success("Resume text extracted successfully.")
            except ValueError as exc:
                st.warning(str(exc))
            except Exception as exc:
                st.error(f"Unable to parse this PDF: {exc}")

if "resume" in st.session_state:
    resume = st.session_state["resume"]
    c1, c2 = st.columns(2)
    c1.text_input("Detected name", value=resume["name"] or "")
    c1.text_input("Email", value=resume["email"] or "")
    c2.text_input("Phone", value=resume["phone"] or "")
    c2.write(f"**Technical skills:** {', '.join(resume['technical_skills']) or 'None detected'}")
    c1.write(f"**Soft skills:** {', '.join(resume['soft_skills']) or 'None detected'}")
    c2.write(f"**Education:** {', '.join(resume['education']) or 'Not explicitly detected'}")
    with st.expander("Review extracted resume text"):
        st.text_area("Extracted text", resume["text"], height=260)
