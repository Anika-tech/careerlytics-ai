import re
import numpy as np
import pandas as pd
from urllib.parse import urlencode
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .text_preprocessing import clean_text
from .skills_extractor import extract_technical_skills
from .data_loader import detect_columns


def parse_experience(text):
    if not isinstance(text, str):
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)", text.lower())
    if match:
        return (float(match.group(1)), float(match.group(2)))
    match = re.search(r"\b(\d+(?:\.\d+)?)\s*\+\s*(?:years?)?", text.lower())
    if match:
        value = float(match.group(1))
        return (value, value + 20)
    match = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b", text.lower())
    if match:
        value = float(match.group(1))
        return (0, value)
    return None


def build_apply_search_url(job_title, company="", location=""):
    query = " ".join(
        str(value).strip()
        for value in (job_title, company, location)
        if value and str(value).strip()
    )
    return "https://www.google.com/search?" + urlencode({"q": f"site:naukri.com {query}"})


@st.cache_resource(show_spinner=False)
def _prepare_job_index(jobs_df):
    title_col = detect_columns(jobs_df, ["job_title", "jobtitle", "title", "role", "designation", "job_role"])
    company_col = detect_columns(jobs_df, ["company", "company_name", "employer"])
    location_col = detect_columns(jobs_df, ["location", "job_location", "joblocation_address", "city"])
    experience_col = detect_columns(jobs_df, ["experience", "experience_required", "experience_level"])
    description_col = detect_columns(jobs_df, ["job_description", "jobdescription", "description", "jobdetails", "jd", "skills"])
    if not title_col:
        title_col = jobs_df.columns[0]
    if not description_col:
        description_col = jobs_df.columns[min(1, len(jobs_df.columns) - 1)]

    jobs = jobs_df.copy()
    jobs["_title"] = jobs[title_col].astype(str) if title_col else ""
    jobs["_company"] = jobs[company_col].astype(str) if company_col else "Not specified"
    jobs["_location"] = jobs[location_col].astype(str) if location_col else "Not specified"
    jobs["_experience"] = jobs[experience_col].astype(str) if experience_col else "Not specified"
    jobs["_description"] = jobs[description_col].fillna("").astype(str)
    jobs["_combined"] = (
        jobs["_title"] + " " + jobs["_description"] + " " +
        (jobs["_company"] if company_col else "")
    ).map(clean_text)

    vectorizer = TfidfVectorizer(
        max_features=8000,
        min_df=2,
        stop_words="english",
        ngram_range=(1, 1),
        dtype=np.float32,
    )
    matrix = vectorizer.fit_transform(jobs["_combined"].tolist())
    job_records = jobs[["_title", "_company", "_location", "_experience", "_description"]].to_dict("records")
    skills_by_job = [set(extract_technical_skills(text)) for text in jobs["_combined"]]
    experience_by_job = [parse_experience(value) for value in jobs["_experience"]]
    return vectorizer, matrix, job_records, skills_by_job, experience_by_job


def recommend_jobs(resume_text, jobs_df, top_n=10, resume_skills=None, predicted_category=None):
    if jobs_df is None or jobs_df.empty:
        return pd.DataFrame()

    vectorizer, job_matrix, job_records, skills_by_job, experience_by_job = _prepare_job_index(jobs_df)
    resume_vector = vectorizer.transform([clean_text(resume_text)])
    similarities = cosine_similarity(resume_vector, job_matrix).flatten()

    candidate_skills = set(resume_skills or extract_technical_skills(resume_text))
    candidate_exp = parse_experience(resume_text)
    records = []
    category_text = clean_text(predicted_category) if predicted_category else ""
    for idx, row in enumerate(job_records):
        required_skills = skills_by_job[idx]
        matching = sorted(candidate_skills & required_skills, key=str.lower)
        missing = sorted(required_skills - candidate_skills, key=str.lower)
        skill_score = len(matching) / len(required_skills) if required_skills else 0.0

        category_score = 0.0
        if category_text:
            title_text = clean_text(row["_title"])
            category_score = 1.0 if category_text and category_text in title_text else 0.0

        experience_score = 0.0
        job_exp = experience_by_job[idx]
        if candidate_exp and job_exp:
            candidate_mid = sum(candidate_exp) / 2
            minimum = job_exp[0]
            maximum = job_exp[1]
            if minimum <= candidate_mid <= maximum:
                experience_score = 1.0
            elif candidate_mid >= minimum:
                experience_score = 0.75
            else:
                experience_score = max(0.0, 1 - (minimum - candidate_mid) / 5)
        elif candidate_exp is None:
            experience_score = 0.5

        weights = {"similarity": 0.50, "skill": 0.30, "category": 0.10, "experience": 0.10}
        if not candidate_exp:
            weights["experience"] = 0.0
            weights["similarity"] = 0.50 / 0.9
            weights["skill"] = 0.30 / 0.9
            weights["category"] = 0.10 / 0.9
        score = (
            float(similarities[idx]) * weights["similarity"] +
            skill_score * weights["skill"] +
            category_score * weights["category"] +
            experience_score * weights["experience"]
        )
        records.append({
            "job_title": row["_title"],
            "company": row["_company"],
            "location": row["_location"],
            "experience": row["_experience"],
            "description": row["_description"],
            "compatibility": round(score * 100, 1),
            "similarity": round(float(similarities[idx]) * 100, 1),
            "matching_skills": matching,
            "missing_skills": missing,
        })

    return pd.DataFrame(records).sort_values("compatibility", ascending=False).head(top_n).reset_index(drop=True)
