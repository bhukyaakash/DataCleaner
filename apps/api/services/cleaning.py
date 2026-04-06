import pandas as pd
import numpy as np
from models.schemas import CleaningOptions, MissingNumericStrategy, MissingCategoricalStrategy, OutlierStrategy
from typing import Dict, Any, Tuple
import json

def load_dataframe(filepath: str, filename: str) -> pd.DataFrame:
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        try:
            return pd.read_csv(filepath, encoding="utf-8")
        except UnicodeDecodeError:
            return pd.read_csv(filepath, encoding="latin-1")
    elif ext == "xlsx":
        return pd.read_excel(filepath, engine="openpyxl")
    elif ext == "json":
        return pd.read_json(filepath)
    raise ValueError(f"Unsupported file type: {ext}")

def get_dtype_map(df: pd.DataFrame) -> Dict[str, str]:
    return {col: str(dtype) for col, dtype in df.dtypes.items()}

def get_missing_counts(df: pd.DataFrame) -> Dict[str, int]:
    return {col: int(df[col].isna().sum()) for col in df.columns}

def get_basic_stats(df: pd.DataFrame) -> Dict[str, Any]:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    stats = {}
    for col in numeric_cols:
        try:
            s = df[col].dropna()
            stats[col] = {
                "mean": round(float(s.mean()), 4) if len(s) else None,
                "median": round(float(s.median()), 4) if len(s) else None,
                "std": round(float(s.std()), 4) if len(s) else None,
                "min": round(float(s.min()), 4) if len(s) else None,
                "max": round(float(s.max()), 4) if len(s) else None,
            }
        except Exception:
            pass
    return stats

def get_top_correlations(df: pd.DataFrame, n: int = 5) -> list:
    numeric = df.select_dtypes(include=[np.number])
    if numeric.shape[1] < 2:
        return []
    try:
        corr = numeric.corr().abs()
        pairs = []
        cols = corr.columns.tolist()
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                val = corr.iloc[i, j]
                if not np.isnan(val):
                    pairs.append((cols[i], cols[j], round(float(val), 4)))
        pairs.sort(key=lambda x: x[2], reverse=True)
        return [{"col1": a, "col2": b, "correlation": c} for a, b, c in pairs[:n]]
    except Exception:
        return []

def handle_outliers_iqr(df: pd.DataFrame, strategy: OutlierStrategy) -> Tuple[pd.DataFrame, int]:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    total_removed = 0
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outlier_mask = (df[col] < lower) | (df[col] > upper)
        count = int(outlier_mask.sum())
        if strategy == OutlierStrategy.clip:
            df[col] = df[col].clip(lower=lower, upper=upper)
        elif strategy == OutlierStrategy.remove:
            df = df[~outlier_mask]
        total_removed += count
    return df, total_removed

def clean_dataframe(df: pd.DataFrame, options: CleaningOptions) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    steps = []

    # Before stats
    before_rows = len(df)
    before_cols = len(df.columns)
    before_missing = get_missing_counts(df)
    before_dtypes = get_dtype_map(df)

    # 1. Remove duplicates
    dupes_removed = 0
    if options.remove_duplicates:
        before = len(df)
        df = df.drop_duplicates()
        dupes_removed = before - len(df)
        steps.append(f"Removed {dupes_removed} duplicate rows")

    # 2. Type normalization
    if options.normalize_types:
        for col in df.columns:
            if df[col].dtype == object:
                # Try numeric coercion
                coerced = pd.to_numeric(df[col], errors="coerce")
                if coerced.notna().sum() / max(len(df), 1) > 0.5:
                    df[col] = coerced
                    steps.append(f"Column '{col}' coerced to numeric")
                else:
                    # Try date parsing
                    try:
                        parsed = pd.to_datetime(df[col], errors="coerce")
                        if parsed.notna().sum() / max(len(df), 1) > 0.5:
                            df[col] = parsed
                            steps.append(f"Column '{col}' parsed as datetime")
                    except Exception:
                        pass

    # 3. Missing values - numeric
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for col in numeric_cols:
        missing = df[col].isna().sum()
        if missing == 0:
            continue
        if options.missing_numeric == MissingNumericStrategy.median:
            df[col] = df[col].fillna(df[col].median())
        elif options.missing_numeric == MissingNumericStrategy.mean:
            df[col] = df[col].fillna(df[col].mean())
        elif options.missing_numeric == MissingNumericStrategy.zero:
            df[col] = df[col].fillna(0)
        elif options.missing_numeric == MissingNumericStrategy.drop:
            df = df.dropna(subset=[col])
        if missing > 0:
            steps.append(f"Filled {missing} missing values in numeric column '{col}' ({options.missing_numeric})")

    # 4. Missing values - categorical
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    # Also include datetime handled as object
    for col in df.columns:
        if col not in numeric_cols:
            if col not in cat_cols:
                cat_cols.append(col)
    cat_cols = [c for c in cat_cols if c in df.columns]

    for col in cat_cols:
        if col not in df.columns:
            continue
        missing = df[col].isna().sum()
        if missing == 0:
            continue
        if options.missing_categorical == MissingCategoricalStrategy.mode:
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                df[col] = df[col].fillna(mode_val[0])
        elif options.missing_categorical == MissingCategoricalStrategy.unknown:
            df[col] = df[col].fillna("Unknown")
        elif options.missing_categorical == MissingCategoricalStrategy.drop:
            df = df.dropna(subset=[col])
        if missing > 0:
            steps.append(f"Filled {missing} missing values in categorical column '{col}' ({options.missing_categorical})")

    # 5. Outliers
    outliers_handled = 0
    if options.handle_outliers != OutlierStrategy.none:
        df, outliers_handled = handle_outliers_iqr(df, options.handle_outliers)
        if outliers_handled > 0:
            steps.append(f"Handled {outliers_handled} outlier values ({options.handle_outliers})")

    after_rows = len(df)
    after_cols = len(df.columns)
    after_missing = get_missing_counts(df)
    after_dtypes = get_dtype_map(df)

    summary = {
        "before": {
            "rows": before_rows,
            "columns": before_cols,
            "missing_by_column": before_missing,
            "dtypes": before_dtypes,
        },
        "after": {
            "rows": after_rows,
            "columns": after_cols,
            "missing_by_column": after_missing,
            "dtypes": after_dtypes,
        },
        "duplicates_removed": dupes_removed,
        "outliers_handled": outliers_handled,
        "steps": steps,
        "stats": get_basic_stats(df),
        "correlations": get_top_correlations(df),
        "cleaning_options": options.model_dump(),
    }

    return df, summary
