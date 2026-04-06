# DataCleaner

> AI-powered data cleaning platform — upload, clean, analyze, and download your data in seconds.

---

## What is DataCleaner?

DataCleaner is a production-ready fullstack web application that lets users:

1. **Upload** CSV, XLSX, or JSON files (no signup required)
2. **Configure** cleaning options from a modern UI
3. **Process** data through a robust cleaning + analysis pipeline
4. **Download** outputs in CSV, XLSX, JSON, or a PDF summary report

Built with **Next.js + FastAPI** in a monorepo structure.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser / Client                      │
│              Next.js 14 (TypeScript + Tailwind)         │
│         Upload → Configure → Monitor → Download         │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP / REST
┌───────────────────────▼─────────────────────────────────┐
│                   FastAPI Backend                        │
│                                                          │
│   POST /api/upload    ──▶  Background Job Worker        │
│   GET  /api/jobs/{id} ──▶  In-memory Job Store          │
│   GET  /api/jobs/{id}/download/{format}                 │
│                                                          │
│   Pipeline: Load → Deduplicate → Normalize →            │
│             Impute Missing → Handle Outliers →          │
│             Generate Stats + PDF Report                  │
└─────────────────────────────────────────────────────────┘

apps/
├── api/       FastAPI Python backend
└── web/       Next.js TypeScript frontend

infra/
└── docker-compose.yml

docs/
├── API.md
├── PIPELINE.md
└── DEPLOYMENT.md
```

---

## Quick Start

### Option A: Docker Compose (Recommended)

```bash
git clone https://github.com/bhukyaakash/DataCleaner.git
cd DataCleaner/infra
docker compose up --build
```

- Web UI: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option B: Run Locally (No Docker)

**Backend:**
```bash
cd apps/api
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

**Frontend (new terminal):**
```bash
cd apps/web
npm install
cp .env.example .env.local
npm run dev
```

Then open http://localhost:3000

---

## Features

### Upload
- Drag & drop or file picker
- Supported: CSV, XLSX, JSON
- Max file size: 50MB (configurable)
- Auto encoding detection (UTF-8 / Latin-1)

### Cleaning Options
| Option | Description |
|--------|-------------|
| Remove Duplicates | Drop exact row duplicates |
| Normalize Types | Coerce numeric strings + parse dates |
| Numeric Missing | median / mean / zero / drop rows |
| Categorical Missing | mode / fill "Unknown" / drop rows |
| Outlier Handling | IQR clip / remove / none |

### Analysis
- Row/column counts before and after
- Missing values by column
- Data type map before/after
- Duplicate + outlier counts
- Descriptive stats per numeric column
- Top 5 feature correlations

### Downloads
- Cleaned dataset as **CSV**
- Cleaned dataset as **XLSX**
- Cleaned dataset as **JSON**
- **PDF summary report** with stats, quality issues, correlations

---

## Project Structure

```
DataCleaner/
├── apps/
│   ├── api/               FastAPI Python backend
│   │   ├── main.py
│   │   ├── routers/       upload, jobs, download
│   │   ├── services/      cleaning, analysis, report
│   │   ├── models/        Pydantic schemas
│   │   ├── utils/         file validation helpers
│   │   ├── tests/         unit + integration tests
│   │   └── requirements.txt
│   └── web/               Next.js TypeScript frontend
│       ├── app/           pages + layout
│       ├── types/         TypeScript interfaces
│       └── lib/           API client
├── infra/
│   └── docker-compose.yml
└── docs/
    ├── API.md
    ├── PIPELINE.md
    └── DEPLOYMENT.md
```

---

## Environment Variables

### Backend (`apps/api/.env`)
| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed frontend origins |
| `MAX_FILE_SIZE_MB` | `50` | Max upload size in MB |

### Frontend (`apps/web/.env.local`)
| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/upload` | Upload file + start job |
| `GET` | `/api/jobs/{id}` | Get job status |
| `GET` | `/api/jobs/{id}/summary` | Get job summary |
| `GET` | `/api/jobs/{id}/download/csv` | Download cleaned CSV |
| `GET` | `/api/jobs/{id}/download/xlsx` | Download cleaned XLSX |
| `GET` | `/api/jobs/{id}/download/json` | Download cleaned JSON |
| `GET` | `/api/jobs/{id}/download/pdf` | Download PDF report |

Full API documentation: [docs/API.md](docs/API.md)

---

## Running Tests

```bash
cd apps/api
pip install -r requirements.txt
python -m pytest tests/ -v
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| CORS error in browser | Check `CORS_ORIGINS` in `apps/api/.env` |
| Upload rejected (413) | Increase `MAX_FILE_SIZE_MB` env var |
| Job stuck in "processing" | Check API console for parsing errors |
| PDF report missing | Verify `reportlab` installed |
| Docker compose fails | Run `docker compose down -v` then re-build |

More: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## Roadmap

- [ ] Persistent job store (SQLite/PostgreSQL)
- [ ] File preview in browser
- [ ] User authentication
- [ ] Async task queue (Celery + Redis)
- [ ] Cloud file storage (S3/R2)
- [ ] ML-based anomaly detection
- [ ] LLM-powered insights
- [ ] Kubernetes deployment

---

## License

MIT © 2024 DataCleaner
