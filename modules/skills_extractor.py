import re
from functools import lru_cache


TECHNICAL_SKILLS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "html", "css",
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
    "sql", "mysql", "postgresql", "mongodb", "redis", "aws", "azure", "gcp",
    "docker", "kubernetes", "git", "github", "linux", "tensorflow", "pytorch",
    "scikit-learn", "pandas", "numpy", "machine learning", "deep learning",
    "nlp", "data analysis", "data visualization", "tableau", "power bi",
]

SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem-solving",
    "problem solving", "adaptability", "critical thinking", "time management",
    "creativity", "collaboration", "presentation", "decision-making",
]


@lru_cache(maxsize=16)
def _skill_index(skills):
    ordered = sorted(skills, key=len, reverse=True)
    alternatives = "|".join(re.escape(skill.lower()) for skill in ordered)
    pattern = re.compile(r"(?<![a-z0-9])(?:" + alternatives + r")(?![a-z0-9])", re.I)
    canonical = {skill.lower(): skill for skill in skills}
    return pattern, canonical


def extract_skills(text, skills=None):
    if not isinstance(text, str):
        return []
    source = skills or TECHNICAL_SKILLS
    pattern, canonical = _skill_index(tuple(source))
    matches = {match.group(0).lower() for match in pattern.finditer(text)}
    return sorted((canonical[match] for match in matches), key=str.lower)


def extract_technical_skills(text):
    return extract_skills(text, TECHNICAL_SKILLS)


def extract_soft_skills(text):
    return extract_skills(text, SOFT_SKILLS)
