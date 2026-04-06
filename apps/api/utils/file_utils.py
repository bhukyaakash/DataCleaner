import os
import uuid
from pathlib import Path

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".json"}

def validate_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def get_job_dir(base: str, job_id: str) -> str:
    path = os.path.join(base, job_id)
    os.makedirs(path, exist_ok=True)
    return path
