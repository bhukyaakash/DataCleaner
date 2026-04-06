# Data Cleaning Pipeline

## Overview

The DataCleaner pipeline processes uploaded files through a series of configurable stages. Each stage is logged and included in the job summary.

---

## Supported Input Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| CSV | `.csv` | Auto-detects encoding (UTF-8, Latin-1 fallback) |
| Excel | `.xlsx` | Uses openpyxl engine |
| JSON | `.json` | Expects records-oriented array |

---

## Pipeline Stages

### Stage 1: File Loading & Schema Detection

- File is read into a Pandas DataFrame.
- Data types are inferred automatically.
- Row/column counts and missing value counts are recorded as "before" metrics.

### Stage 2: Duplicate Removal

If `remove_duplicates = true`:
- Exact row duplicates are dropped using `df.drop_duplicates()`.
- Count of removed duplicates is recorded.

### Stage 3: Type Normalization

If `normalize_types = true`:
- **Numeric coercion**: Object columns where >50% of values are numeric are coerced to `float64`.
- **Date parsing**: Object columns where >50% of values parse as dates are converted to `datetime64`.
- Columns that fail both checks remain as `object` type.

### Stage 4: Missing Value Handling — Numeric Columns

Applied to all `float64` / `int64` columns:

| Strategy | Behavior |
|----------|----------|
| `median` | Fill with column median (default) |
| `mean` | Fill with column mean |
| `zero` | Fill with 0 |
| `drop` | Drop rows where this column has missing values |

### Stage 5: Missing Value Handling — Categorical Columns

Applied to all `object` / `category` columns (and datetime columns):

| Strategy | Behavior |
|----------|----------|
| `unknown` | Fill with the string `"Unknown"` (default) |
| `mode` | Fill with the most frequent value |
| `drop` | Drop rows where this column has missing values |

### Stage 6: Outlier Handling

Applied to all numeric columns using the **IQR method**:
- Lower bound = Q1 − 1.5 × IQR
- Upper bound = Q3 + 1.5 × IQR

| Strategy | Behavior |
|----------|----------|
| `clip` | Clip values to [lower, upper] bounds (default) |
| `remove` | Drop rows with outlier values |
| `none` | No outlier handling |

---

## Analysis & Summary Generation

After cleaning, the pipeline computes:

### Descriptive Statistics
For each numeric column:
- Mean, Median, Standard Deviation, Min, Max

### Feature Correlations
- Pearson correlation matrix on numeric columns
- Top 5 absolute correlations returned
- Columns with < 2 numeric features: skipped

### Quality Issues Report
Human-readable list of issues fixed:
- Duplicate row count
- Missing values per column
- Outlier count
- Rows removed

---

## Output Formats

| Format | Notes |
|--------|-------|
| CSV | `pandas.to_csv(index=False)` |
| XLSX | `pandas.to_excel(engine="openpyxl")` |
| JSON | `pandas.to_json(orient="records", indent=2)` |
| PDF | ReportLab-generated report with all stats |

---

## Limitations (v1 MVP)

- In-memory job store (jobs lost on API restart)
- No streaming for large files; entire file loaded into memory
- No ML models — purely statistical/rule-based pipeline
- Single-file processing only
- No background task queue (uses FastAPI BackgroundTasks)

---

## Future Enhancements

- ML-based anomaly detection
- Schema inference with Pandera/Great Expectations
- LLM-powered natural language insights
- Async job queue (Celery/Redis)
- Parquet and SQL input support
