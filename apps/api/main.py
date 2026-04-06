import os
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import upload, jobs, download

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure directories exist
    for d in ["uploads", "outputs", "reports"]:
        os.makedirs(d, exist_ok=True)
    yield

app = FastAPI(
    title="DataCleaner API",
    version="1.0.0",
    lifespan=lifespan
)

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(download.router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
