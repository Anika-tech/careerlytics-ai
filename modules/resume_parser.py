import re
import fitz
from .skills_extractor import extract_technical_skills, extract_soft_skills


def extract_pdf_text(uploaded_file):
    data = uploaded_file.getvalue()
    text_parts = []
    with fitz.open(stream=data, filetype="pdf") as document:
        for page in document:
            text_parts.append(page.get_text("text"))
    text = "\n".join(text_parts).strip()
    if not text:
        raise ValueError("This PDF appears to contain scanned images or no selectable text.")
    return text


def parse_resume_text(text):
    result = {"name": None, "email": None, "phone": None, "technical_skills": [],
              "soft_skills": [], "education": [], "projects": [], "certifications": [],
              "experience": "", "text": text}
    email_match = re.search(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", text)
    if email_match:
        result["email"] = email_match.group(0)
    phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,5}\)?[-.\s]?)\d{6,10}", text)
    if phone_match:
        result["phone"] = phone_match.group(0)

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        for line in lines[:8]:
            if len(line.split()) <= 5 and not any(c in line for c in "@+0123456789"):
                result["name"] = line
                break

    result["technical_skills"] = extract_technical_skills(text)
    result["soft_skills"] = extract_soft_skills(text)
    lower = text.lower()

    degree_pattern = re.compile(
        r"\b(?:b[\.,]?\s?(?:tech|e|sc|a)\b|m[\.,]?\s?(?:tech|e|sc|ba|sc)\b|"
        r"bachelor(?:'s)?|master(?:'s)?|b\.?e\.?|m\.?e\.?|bca|mca|diploma)\b",
        re.I,
    )
    for line in lines:
        if degree_pattern.search(line) and line not in result["education"]:
            result["education"].append(line)

    section_patterns = {
        "projects": r"(?:projects?|portfolio)",
        "certifications": r"(?:certifications?|licenses?|courses?)",
        "experience": r"(?:experience|employment|work history)",
    }
    sections = {}
    for key, pattern in section_patterns.items():
        match = re.search(rf"(?im)^[ \t]*{pattern}\b", text)
        if match:
            sections[key] = match.start()

    positions = sorted(sections.items(), key=lambda item: item[1])
    for index, (key, start) in enumerate(positions):
        end = positions[index + 1][1] if index + 1 < len(positions) else len(text)
        content = text[start:end].strip()
        if key == "projects":
            result["projects"] = [line for line in content.splitlines()[1:] if len(line.strip()) > 5][:8]
        elif key == "certifications":
            result["certifications"] = [line for line in content.splitlines()[1:] if len(line.strip()) > 5][:8]
        else:
            result["experience"] = content[:2500]

    return result
