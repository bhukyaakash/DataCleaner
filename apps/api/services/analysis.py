import pandas as pd
import numpy as np
from typing import Dict, Any

def generate_quality_issues(summary: Dict[str, Any]) -> list:
    issues = []
    before = summary.get("before", {})
    after = summary.get("after", {})

    dupes = summary.get("duplicates_removed", 0)
    if dupes > 0:
        issues.append(f"{dupes} duplicate rows were found and removed")

    missing_before = before.get("missing_by_column", {})
    for col, count in missing_before.items():
        if count > 0:
            issues.append(f"Column '{col}' had {count} missing values (handled)")

    outliers = summary.get("outliers_handled", 0)
    if outliers > 0:
        issues.append(f"{outliers} outlier values were handled in numeric columns")

    rows_lost = before.get("rows", 0) - after.get("rows", 0)
    if rows_lost > 0:
        issues.append(f"{rows_lost} rows were removed during cleaning")

    return issues
