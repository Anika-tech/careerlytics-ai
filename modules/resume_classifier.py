import joblib
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from config import MODEL_DIR
from .text_preprocessing import clean_text
from .data_loader import detect_columns


@st.cache_resource(show_spinner=False)
def train_resume_classifier(df):
    text_col = detect_columns(df, ["resume", "resume_text", "text", "resume_details"])
    category_col = detect_columns(df, ["category", "resume_category", "job_category", "label"])
    if not text_col or not category_col:
        raise ValueError("Resume dataset requires a text column and a category/label column.")

    df = df[[text_col, category_col]].copy()
    df = df[df[text_col].astype(str).str.strip().ne("")]
    df = df[df[category_col].astype(str).str.strip().ne("")]
    if df.shape[0] < 10 or df[category_col].nunique() < 2:
        raise ValueError("Not enough valid records or categories to train the classifier.")

    X = df[text_col].astype(str).map(clean_text)
    y = df[category_col].astype(str)
    test_size = 0.2 if len(df) >= 20 else 0.25
    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=stratify
    )

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), sublinear_tf=True)
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    model = LogisticRegression(max_iter=2000, class_weight="balanced")
    model.fit(X_train_tfidf, y_train)
    predictions = model.predict(X_test_tfidf)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, predictions, average="weighted", zero_division=0
    )
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "labels": sorted(y.unique()),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=sorted(y.unique())).tolist(),
    }
    joblib.dump(model, MODEL_DIR / "resume_classifier.joblib")
    joblib.dump(vectorizer, MODEL_DIR / "resume_tfidf.joblib")
    return model, vectorizer, metrics


def predict_category(text):
    model_path = MODEL_DIR / "resume_classifier.joblib"
    vector_path = MODEL_DIR / "resume_tfidf.joblib"
    if not model_path.exists() or not vector_path.exists():
        return None
    model = joblib.load(model_path)
    vectorizer = joblib.load(vector_path)
    return model.predict(vectorizer.transform([clean_text(text)]))[0]
