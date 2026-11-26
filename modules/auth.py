import hashlib
import hmac
import re
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import streamlit as st

from config import DATA_DIR

AUTH_DB = DATA_DIR / "users.sqlite3"
PBKDF2_ITERATIONS = 310_000
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalize_email(email):
    return email.strip().casefold()


@contextmanager
def _connect(database_path):
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        with connection:
            yield connection
    finally:
        connection.close()


def _password_hash(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )


def create_user(email, password, database_path=AUTH_DB):
    normalized_email = _normalize_email(email)
    if not EMAIL_PATTERN.fullmatch(normalized_email):
        return False, "Enter a valid email address."
    if len(password) < 10:
        return False, "Use a password with at least 10 characters."

    salt = secrets.token_bytes(16)
    password_hash = _password_hash(password, salt)
    try:
        with _connect(database_path) as connection:
            connection.execute(
                "INSERT INTO users (email, password_salt, password_hash) VALUES (?, ?, ?)",
                (normalized_email, salt.hex(), password_hash.hex()),
            )
    except sqlite3.IntegrityError:
        return False, "An account with that email already exists."
    return True, "Account created."


def authenticate_user(email, password, database_path=AUTH_DB):
    normalized_email = _normalize_email(email)
    with _connect(database_path) as connection:
        row = connection.execute(
            "SELECT password_salt, password_hash FROM users WHERE email = ?",
            (normalized_email,),
        ).fetchone()

    if row is None:
        return False

    salt = bytes.fromhex(row[0])
    expected_hash = bytes.fromhex(row[1])
    return hmac.compare_digest(_password_hash(password, salt), expected_hash)


def clear_user_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def render_auth_gate():
    if st.session_state.get("authenticated_user"):
        return True

    st.markdown(
        "<div class='hero'><div class='eyebrow'>CAREERLYTICS AI</div>"
        "<h1>Your career workspace,<br><span>securely yours.</span></h1>"
        "<p>Sign in or create a local account to continue. Your resume remains in session memory only.</p></div>",
        unsafe_allow_html=True,
    )

    login_tab, signup_tab = st.tabs(["Log in", "Create account"])
    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)
        if submitted:
            if authenticate_user(email, password):
                st.session_state["authenticated_user"] = _normalize_email(email)
                st.rerun()
            st.error("Email or password is incorrect.")

    with signup_tab:
        with st.form("signup_form"):
            email = st.text_input("Email address", key="signup_email")
            password = st.text_input("Password (at least 10 characters)", type="password", key="signup_password")
            confirmation = st.text_input("Confirm password", type="password", key="signup_confirmation")
            submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
        if submitted:
            if password != confirmation:
                st.error("The passwords do not match.")
            else:
                created, message = create_user(email, password)
                if created:
                    st.session_state["authenticated_user"] = _normalize_email(email)
                    st.success(message)
                    st.rerun()
                st.error(message)
    st.caption("Accounts are stored locally on this computer. Password recovery and email verification are not configured.")
    return False
