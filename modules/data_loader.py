import pandas as pd
import streamlit as st
from config import RESUME_DATASET, JOB_DATASET


def detect_columns(df, candidates):
    def normalize(value):
        return "".join(ch for ch in str(value).lower().strip() if ch.isalnum())

    normalized = {normalize(c): c for c in df.columns}
    for candidate in candidates:
        key = normalize(candidate)
        if key in normalized:
            return normalized[key]
    return None


@st.cache_data(show_spinner=False)
def _read_csv(path_string, filename, modified_time, file_size):
    try:
        df = pd.read_csv(path_string)
        df = df.drop_duplicates().fillna("")
        return df, None
    except Exception as exc:
        return None, f"Could not read {filename}: {exc}"


def load_csv(path):
    if not path.exists():
        return None, f"Required file not found: {path.name}. Place it in data/raw/"
    stat = path.stat()
    return _read_csv(str(path), path.name, stat.st_mtime_ns, stat.st_size)


def load_resume_dataset():
    return load_csv(RESUME_DATASET)


def load_job_dataset():
    return load_csv(JOB_DATASET)
