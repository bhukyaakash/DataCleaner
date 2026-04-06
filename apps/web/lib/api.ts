import axios from "axios";
import { CleaningOptions, Job } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
});

export async function uploadFile(
  file: File,
  options: CleaningOptions
): Promise<{ job_id: string; status: string; filename: string }> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("options", JSON.stringify(options));
  const res = await api.post("/api/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function getJob(jobId: string): Promise<Job> {
  const res = await api.get(`/api/jobs/${jobId}`);
  return res.data;
}

export function getDownloadUrl(jobId: string, format: "csv" | "xlsx" | "json" | "pdf"): string {
  return `${API_BASE}/api/jobs/${jobId}/download/${format}`;
}
