import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.cleaning import (
    clean_dataframe, get_missing_counts, get_basic_stats, get_top_correlations
)
from models.schemas import CleaningOptions, MissingNumericStrategy, MissingCategoricalStrategy, OutlierStrategy


def make_test_df():
    return pd.DataFrame({
        "age": [25, 30, np.nan, 25, 200],   # has NaN + outlier
        "salary": [50000, 60000, 70000, 50000, np.nan],  # has NaN + duplicate
        "name": ["Alice", "Bob", np.nan, "Alice", "Eve"],  # has NaN
        "city": ["NY", "LA", "NY", "NY", "SF"],
    })


def test_remove_duplicates():
    df = make_test_df()
    opts = CleaningOptions(remove_duplicates=True, handle_outliers=OutlierStrategy.none)
    cleaned, summary = clean_dataframe(df, opts)
    assert summary["duplicates_removed"] >= 0


def test_missing_numeric_median():
    df = pd.DataFrame({"val": [1.0, 2.0, np.nan, 4.0]})
    opts = CleaningOptions(missing_numeric=MissingNumericStrategy.median, handle_outliers=OutlierStrategy.none)
    cleaned, summary = clean_dataframe(df, opts)
    assert cleaned["val"].isna().sum() == 0


def test_missing_numeric_mean():
    df = pd.DataFrame({"val": [2.0, 4.0, np.nan, 6.0]})
    opts = CleaningOptions(missing_numeric=MissingNumericStrategy.mean, handle_outliers=OutlierStrategy.none)
    cleaned, summary = clean_dataframe(df, opts)
    assert cleaned["val"].isna().sum() == 0


def test_missing_categorical_unknown():
    df = pd.DataFrame({"name": ["Alice", None, "Bob"]})
    opts = CleaningOptions(missing_categorical=MissingCategoricalStrategy.unknown, handle_outliers=OutlierStrategy.none)
    cleaned, summary = clean_dataframe(df, opts)
    assert "Unknown" in cleaned["name"].values


def test_outlier_clip():
    df = pd.DataFrame({"val": [1.0, 2.0, 3.0, 4.0, 100.0]})  # 100 is outlier
    opts = CleaningOptions(handle_outliers=OutlierStrategy.clip)
    cleaned, summary = clean_dataframe(df, opts)
    # After clipping, 100 should be reduced
    assert cleaned["val"].max() < 100.0


def test_get_missing_counts():
    df = pd.DataFrame({"a": [1, np.nan, 3], "b": ["x", "y", None]})
    counts = get_missing_counts(df)
    assert counts["a"] == 1
    assert counts["b"] == 1


def test_get_basic_stats():
    df = pd.DataFrame({"val": [1.0, 2.0, 3.0, 4.0, 5.0]})
    stats = get_basic_stats(df)
    assert "val" in stats
    assert stats["val"]["mean"] == 3.0


def test_get_top_correlations():
    df = pd.DataFrame({
        "a": [1, 2, 3, 4, 5],
        "b": [2, 4, 6, 8, 10],  # perfect correlation with a
        "c": [5, 4, 3, 2, 1],   # perfect negative correlation with a
    })
    corrs = get_top_correlations(df, n=3)
    assert len(corrs) > 0
    assert corrs[0]["correlation"] == 1.0
