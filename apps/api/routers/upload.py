import os
import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
import aiofiles

from models.schemas import CleaningOptions, JobStatus
from utils.file_utils import validate_extension, MAX_FILE_SIZE, get_job_dir

router = APIRouter()

# In-memory job store (for MVP)
jobs: Dict[str, Dict[str, Any]] = {}

def get_jobs():
    return jobs

@router.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: str = Form(default="{}")
):
    # Validate extension
    if not validate_extension(file.filename or ""):
        raise HTTPException(status_code=400, detail="Unsupported file type. Use CSV, XLSX, or JSON.")

    # Read content and check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB")

    # Parse options
    try:
        options_dict = json.loads(options)
        cleaning_options = CleaningOptions(**options_dict)
    except Exception:
        cleaning_options = CleaningOptions()

    job_id = str(uuid.uuid4())
    upload_dir = get_job_dir("uploads", job_id)
    upload_path = os.path.join(upload_dir, file.filename)

    async with aiofiles.open(upload_path, "wb") as f:
        await f.write(content)

    jobs[job_id] = {
        "job_id": job_id,
        "status": JobStatus.pending,
        "filename": file.filename,
        "upload_path": upload_path,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "error": None,
        "summary": None,
        "options": cleaning_options.model_dump(),
    }

    background_tasks.add_task(process_job, job_id, upload_path, file.filename, cleaning_options)

    return {"job_id": job_id, "status": "pending", "filename": file.filename}


async def process_job(job_id: str, upload_path: str, filename: str, options: CleaningOptions):
    from services.cleaning import load_dataframe, clean_dataframe
    from services.report import build_pdf_report
    import pandas as pd

    jobs[job_id]["status"] = JobStatus.processing

    try:
        # Load
        df = load_dataframe(upload_path, filename)

        # Clean
        cleaned_df, summary = clean_dataframe(df, options)

        # Save outputs
        output_dir = get_job_dir("outputs", job_id)

        # CSV
        csv_path = os.path.join(output_dir, "cleaned.csv")
        cleaned_df.to_csv(csv_path, index=False)

        # XLSX
        xlsx_path = os.path.join(output_dir, "cleaned.xlsx")
        cleaned_df.to_excel(xlsx_path, index=False, engine="openpyxl")

        # JSON
        json_path = os.path.join(output_dir, "cleaned.json")
        cleaned_df.to_json(json_path, orient="records", indent=2, default_handler=str)

        # PDF
        report_dir = get_job_dir("reports", job_id)
        pdf_path = os.path.join(report_dir, "report.pdf")
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        build_pdf_report(pdf_path, filename, summary, timestamp)

        jobs[job_id]["status"] = JobStatus.completed
        jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        jobs[job_id]["summary"] = summary

    except Exception as e:
        jobs[job_id]["status"] = JobStatus.failed
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
