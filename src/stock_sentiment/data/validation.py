"""Data-quality checks that run after schema validation.

Schema validation (``schemas.py``) answers "is this the right shape?".
This module answers "is this data any good?" — nulls, duplicates,
outliers, and date-range sanity — and returns a structured report
instead of raising, so callers can decide whether to warn or abort.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from stock_sentiment.config import settings


@dataclass
class DataQualityReport:
    dataset: str
    row_count: int
    column_null_counts: dict[str, int] = field(default_factory=dict)
    duplicate_rows: int = 0
    outlier_counts: dict[str, int] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.issues

    def as_dict(self) -> dict:
        return {
            "dataset": self.dataset,
            "row_count": self.row_count,
            "column_null_counts": self.column_null_counts,
            "duplicate_rows": self.duplicate_rows,
            "outlier_counts": self.outlier_counts,
            "issues": self.issues,
            "is_clean": self.is_clean,
        }


def _iqr_outlier_count(series: pd.Series, multiplier: float) -> int:
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return 0
    q1, q3 = numeric.quantile(0.25), numeric.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
    return int(((numeric < lower) | (numeric > upper)).sum())


def profile_news(df: pd.DataFrame) -> DataQualityReport:
    report = DataQualityReport(dataset="news", row_count=len(df))
    if df.empty:
        report.issues.append("dataset is empty")
        return report

    report.column_null_counts = {c: int(df[c].isna().sum()) for c in df.columns}
    dup_subset = [c for c in ("headline", "date", "stock") if c in df.columns]
    report.duplicate_rows = int(df.duplicated(subset=dup_subset or None).sum())

    for col, null_count in report.column_null_counts.items():
        if col == "headline" and null_count > 0:
            report.issues.append(f"{null_count} rows missing 'headline'")
    if report.duplicate_rows:
        report.issues.append(f"{report.duplicate_rows} duplicate rows detected")
    if "date" in df.columns:
        bad_dates = int(df["date"].isna().sum())
        if bad_dates:
            report.issues.append(f"{bad_dates} rows with unparseable dates")
    return report


def profile_prices(df: pd.DataFrame) -> DataQualityReport:
    report = DataQualityReport(dataset="prices", row_count=len(df))
    if df.empty:
        report.issues.append("dataset is empty")
        return report

    report.column_null_counts = {c: int(df[c].isna().sum()) for c in df.columns}
    report.duplicate_rows = int(df.duplicated(subset=["date"]).sum()) if "date" in df.columns else 0

    for col in ("open", "high", "low", "close", "volume"):
        if col in df.columns:
            report.outlier_counts[col] = _iqr_outlier_count(df[col], settings.outlier_iqr_multiplier)

    if {"high", "low"}.issubset(df.columns) and (df["high"] < df["low"]).any():
        bad = int((df["high"] < df["low"]).sum())
        report.issues.append(f"{bad} rows where high < low")
    if report.duplicate_rows:
        report.issues.append(f"{report.duplicate_rows} duplicate trading dates")
    return report
