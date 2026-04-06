from fastapi import APIRouter, HTTPException
from routers.upload import get_jobs

router = APIRouter()

@router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    jobs = get_jobs()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/jobs/{job_id}/summary")
async def get_summary(job_id: str):
    jobs = get_jobs()
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    return job.get("summary", {})
