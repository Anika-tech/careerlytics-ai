# CAREERLYTICS AI

AI-Based Resume Analyzer and Job Recommendation System.

## Setup

```powershell
cd CAREERLYTICS_AI
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Dataset setup

Download these Kaggle datasets:

- **Updated Resume Dataset**: `UpdatedResumeDataSet.csv`
- **Jobs on Naukri.com**: `naukri_com-job_sample.csv`

Place both CSV files in `data/raw/`. Dataset files are intentionally not included in this repository; the application does not invent records or silently substitute sample data.

The resume dataset can contain personal information. Review and handle it locally; do not commit resume records, trained model artifacts, account databases, or secrets. The jobs dataset is marked **CC BY-NC-SA 4.0** on Kaggle and is intended for non-commercial use with attribution and share-alike terms. Check the dataset's current terms before using or redistributing it.

Dataset links:

- https://www.kaggle.com/datasets/jillanisofttech/updated-resume-dataset
- https://www.kaggle.com/datasets/PromptCloudHQ/jobs-on-naukricom

Without these files, dataset-dependent pages will show the required-file message and classification/recommendation features will not be available.

## Local accounts

The app supports local email/password sign-up, login, and logout. Accounts are stored in
`data/users.sqlite3`; passwords are stored as salted PBKDF2-HMAC-SHA256 hashes, never as
plaintext. Authentication state is session-only. Resume content is cleared from session memory
when the user logs out. There is no email verification or password-recovery flow.

## Tests

```powershell
python -m unittest tests/test_modules.py
```
