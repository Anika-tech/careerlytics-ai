from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODEL_DIR = BASE_DIR / "models"
ASSET_DIR = BASE_DIR / "assets"

RESUME_DATASET = RAW_DATA_DIR / "UpdatedResumeDataSet.csv"
JOB_DATASET = RAW_DATA_DIR / "naukri_com-job_sample.csv"

for directory in (DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_DIR, ASSET_DIR):
    directory.mkdir(parents=True, exist_ok=True)
