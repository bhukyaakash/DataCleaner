# DataCleaner API Reference

## Base URL

- Local: `http://localhost:8000`
- Docker: `http://localhost:8000`

---

## Endpoints

### `GET /health`

Health check for the API service.

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

### `POST /api/upload`

Upload a file and start a cleaning job.

**Request (multipart/form-data):**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | ✅ | CSV, XLSX, or JSON file (max 50MB by default) |
| `options` | JSON string | ❌ | Cleaning configuration (see below) |

**Options schema:**
```json
{
  "remove_duplicates": true,
  "missing_numeric": "median",
  "missing_categorical": "unknown",
  "normalize_types": true,
  "handle_outliers": "clip",
  "user_notes": "Optional context notes"
}
```

**Option values:**

| Field | Options | Default |
|-------|---------|---------|
| `remove_duplicates` | `true`, `false` | `true` |
| `missing_numeric` | `median`, `mean`, `zero`, `drop` | `median` |
| `missing_categorical` | `mode`, `unknown`, `drop` | `unknown` |
| `normalize_types` | `true`, `false` | `true` |
| `handle_outliers` | `clip`, `remove`, `none` | `clip` |

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "pending",
  "filename": "data.csv"
}
```

**Error responses:**
- `400` — Unsupported file type
- `413` — File too large

---

### `GET /api/jobs/{job_id}`

Get the current status and result of a job.

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "filename": "data.csv",
  "created_at": "2024-01-01T12:00:00",
  "completed_at": "2024-01-01T12:00:05",
  "error": null,
  "summary": { ... }
}
```

**Status values:** `pending` | `processing` | `completed` | `failed`

**Error responses:**
- `404` — Job not found

---

### `GET /api/jobs/{job_id}/summary`

Get the detailed cleaning summary for a completed job.

**Response:** Full summary object (see Summary Schema below).

**Error responses:**
- `404` — Job not found
- `400` — Job not completed yet

---

### `GET /api/jobs/{job_id}/download/{format}`

Download the cleaned dataset or PDF report.

**Path params:**
| Param | Values |
|-------|--------|
| `format` | `csv`, `xlsx`, `json`, `pdf` |

**Response:** Binary file download.

**Error responses:**
- `400` — Job not completed or invalid format
- `404` — Job or output file not found

---

## Summary Schema

```json
{
  "before": {
    "rows": 1000,
    "columns": 10,
    "missing_by_column": { "age": 5, "name": 0 },
    "dtypes": { "age": "float64", "name": "object" }
  },
  "after": {
    "rows": 985,
    "columns": 10,
    "missing_by_column": { "age": 0, "name": 0 },
    "dtypes": { "age": "float64", "name": "object" }
  },
  "duplicates_removed": 15,
  "outliers_handled": 3,
  "steps": ["Removed 15 duplicate rows", "Filled 5 missing values in age (median)"],
  "stats": {
    "age": {
      "mean": 34.2,
      "median": 33.0,
      "std": 8.5,
      "min": 18.0,
      "max": 75.0
    }
  },
  "correlations": [
    { "col1": "age", "col2": "salary", "correlation": 0.73 }
  ],
  "cleaning_options": { ... }
}
```
