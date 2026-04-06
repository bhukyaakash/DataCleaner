from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from enum import Enum

class MissingNumericStrategy(str, Enum):
    median = "median"
    mean = "mean"
    zero = "zero"
    drop = "drop"

class MissingCategoricalStrategy(str, Enum):
    mode = "mode"
    unknown = "unknown"
    drop = "drop"

class OutlierStrategy(str, Enum):
    clip = "clip"
    remove = "remove"
    none = "none"

class CleaningOptions(BaseModel):
    remove_duplicates: bool = True
    missing_numeric: MissingNumericStrategy = MissingNumericStrategy.median
    missing_categorical: MissingCategoricalStrategy = MissingCategoricalStrategy.unknown
    normalize_types: bool = True
    handle_outliers: OutlierStrategy = OutlierStrategy.clip
    user_notes: Optional[str] = None

class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    filename: str
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None
