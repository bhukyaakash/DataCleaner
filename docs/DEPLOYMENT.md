# Deployment Guide

## Local Development (No Docker)

### Prerequisites
- Python 3.11+
- Node.js 20+
- npm 10+

### 1. Start the API

```bash
cd apps/api
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8000
```

API available at: http://localhost:8000
API docs (Swagger): http://localhost:8000/docs

### 2. Start the Web App

```bash
cd apps/web
npm install
cp .env.example .env.local
npm run dev
```

Web app available at: http://localhost:3000

---

## Docker Compose (Recommended)

### Prerequisites
- Docker 24+
- Docker Compose v2+

### Quick Start

```bash
cd infra
docker compose up --build
```

This starts:
- API at http://localhost:8000
- Web at http://localhost:3000

### Stop services

```bash
docker compose down
```

### Clean up volumes (removes all uploaded/processed files)

```bash
docker compose down -v
```

---

## Environment Variables

### API (`apps/api/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
| `MAX_FILE_SIZE_MB` | `50` | Max upload size in megabytes |

### Web (`apps/web/.env.local`)

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API base URL |

---

## Production Deployment Checklist

1. **API**
   - Set `CORS_ORIGINS` to your production frontend domain
   - Mount persistent volumes for `uploads/`, `outputs/`, `reports/`
   - Add a reverse proxy (nginx/caddy) in front of uvicorn
   - Set `workers` in uvicorn for multi-core: `uvicorn main:app --workers 4`

2. **Web**
   - Set `NEXT_PUBLIC_API_URL` to your production API URL
   - Enable Next.js output: `standalone` in `next.config.js`

3. **Storage**
   - Replace local file storage with S3/GCS/R2 for production
   - Implement a cleanup cron job to purge old job artifacts

4. **Monitoring**
   - Add Sentry for error tracking
   - Add Prometheus metrics endpoint
   - Set up log aggregation (Loki/CloudWatch)

---

## File Cleanup Strategy

Job artifacts are stored in:
- `apps/api/uploads/{job_id}/`
- `apps/api/outputs/{job_id}/`
- `apps/api/reports/{job_id}/`

**Recommended cleanup (manual for MVP):**
```bash
# Delete artifacts older than 7 days
find apps/api/uploads -mtime +7 -exec rm -rf {} +
find apps/api/outputs -mtime +7 -exec rm -rf {} +
find apps/api/reports -mtime +7 -exec rm -rf {} +
```

**Future**: implement an automatic TTL-based cleanup task on job completion.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS errors in browser | Set `CORS_ORIGINS` in API `.env` to match your web origin |
| File upload fails (413) | Increase `MAX_FILE_SIZE_MB` env var |
| PDF download empty | Ensure `reportlab` is installed (`pip install reportlab`) |
| XLSX download fails | Ensure `openpyxl` is installed |
| Job stuck in "processing" | Check API logs; likely a parsing error in the input file |
| Docker build fails | Run `docker compose down -v` then `docker compose up --build` |
