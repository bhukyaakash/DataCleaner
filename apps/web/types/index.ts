export type JobStatus = "pending" | "processing" | "completed" | "failed";

export interface CleaningOptions {
  remove_duplicates: boolean;
  missing_numeric: "median" | "mean" | "zero" | "drop";
  missing_categorical: "mode" | "unknown" | "drop";
  normalize_types: boolean;
  handle_outliers: "clip" | "remove" | "none";
  user_notes: string;
}

export interface JobSummary {
  before: {
    rows: number;
    columns: number;
    missing_by_column: Record<string, number>;
    dtypes: Record<string, string>;
  };
  after: {
    rows: number;
    columns: number;
    missing_by_column: Record<string, number>;
    dtypes: Record<string, string>;
  };
  duplicates_removed: number;
  outliers_handled: number;
  steps: string[];
  stats: Record<string, {
    mean: number | null;
    median: number | null;
    std: number | null;
    min: number | null;
    max: number | null;
  }>;
  correlations: Array<{ col1: string; col2: string; correlation: number }>;
  cleaning_options: CleaningOptions;
}

export interface Job {
  job_id: string;
  status: JobStatus;
  filename: string;
  created_at: string;
  completed_at: string | null;
  error: string | null;
  summary: JobSummary | null;
}
