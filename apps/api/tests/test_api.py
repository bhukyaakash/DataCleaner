import pytest
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def make_csv_bytes():
    return b"name,age,salary\nAlice,25,50000\nBob,,60000\nAlice,25,50000\n"


def test_upload_csv():
    csv_data = make_csv_bytes()
    files = {"file": ("test.csv", io.BytesIO(csv_data), "text/csv")}
    options = json.dumps({
        "remove_duplicates": True,
        "missing_numeric": "median",
        "missing_categorical": "unknown",
        "handle_outliers": "clip",
    })
    data = {"options": options}
    response = client.post("/api/upload", files=files, data=data)
    assert response.status_code == 200
    body = response.json()
    assert "job_id" in body
    return body["job_id"]


def test_upload_invalid_extension():
    files = {"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")}
    response = client.post("/api/upload", files=files, data={"options": "{}"})
    assert response.status_code == 400


def test_job_not_found():
    response = client.get("/api/jobs/nonexistent-id")
    assert response.status_code == 404


def test_full_pipeline():
    import time
    # Upload
    csv_data = b"id,name,age,salary\n1,Alice,25,50000\n2,Bob,,60000\n1,Alice,25,50000\n3,Charlie,35,\n"
    files = {"file": ("data.csv", io.BytesIO(csv_data), "text/csv")}
    options = json.dumps({"remove_duplicates": True, "missing_numeric": "median", "missing_categorical": "unknown"})
    upload_resp = client.post("/api/upload", files=files, data={"options": options})
    assert upload_resp.status_code == 200
    job_id = upload_resp.json()["job_id"]

    # Poll for completion (TestClient runs background tasks synchronously in some versions)
    max_wait = 10
    for _ in range(max_wait):
        status_resp = client.get(f"/api/jobs/{job_id}")
        assert status_resp.status_code == 200
        status = status_resp.json()["status"]
        if status in ("completed", "failed"):
            break
        time.sleep(1)

    # Check completed
    assert status_resp.json()["status"] == "completed"

    # Download CSV
    csv_resp = client.get(f"/api/jobs/{job_id}/download/csv")
    assert csv_resp.status_code == 200

    # Download JSON
    json_resp = client.get(f"/api/jobs/{job_id}/download/json")
    assert json_resp.status_code == 200

    # Download PDF
    pdf_resp = client.get(f"/api/jobs/{job_id}/download/pdf")
    assert pdf_resp.status_code == 200
