import os
import re
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from routers.upload import get_jobs

router = APIRouter()

_UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

@router.get("/jobs/{job_id}/download/{format}")
async def download_file(job_id: str, format: str):
    if not _UUID_RE.match(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    jobs = get_jobs()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")

    format = format.lower()
    if format not in ("csv", "xlsx", "json", "pdf"):
        raise HTTPException(status_code=400, detail="Format must be csv, xlsx, json, or pdf")

    filename = job["filename"].rsplit(".", 1)[0]

    if format == "pdf":
        path = os.path.join("reports", job_id, "report.pdf")
        media_type = "application/pdf"
        dl_name = f"{filename}_report.pdf"
    else:
        path = os.path.join("outputs", job_id, f"cleaned.{format}")
        if format == "csv":
            media_type = "text/csv"
            dl_name = f"{filename}_cleaned.csv"
        elif format == "xlsx":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            dl_name = f"{filename}_cleaned.xlsx"
        else:
            media_type = "application/json"
            dl_name = f"{filename}_cleaned.json"

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(path=path, media_type=media_type, filename=dl_name)
