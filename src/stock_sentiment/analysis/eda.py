"""Reusable exploratory-data-analysis summaries for the news dataset.

Turns the ad-hoc cell-by-cell exploration in ``notebooks/task_1.ipynb``
into functions that return plain data structures (dicts/DataFrames),
so the same analysis can back a notebook, the API, or a report without
being copy-pasted.
"""
from __future__ import annotations

import pandas as pd


def headline_length_stats(news: pd.DataFrame) -> dict:
    lengths = news["headline"].astype(str).str.len()
    return {
        "mean": float(lengths.mean()),
        "median": float(lengths.median()),
        "std": float(lengths.std()),
        "min": int(lengths.min()),
        "max": int(lengths.max()),
    }


def publisher_activity(news: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if "publisher" not in news.columns:
        return pd.DataFrame(columns=["publisher", "article_count"])
    counts = (
        news.groupby("publisher").size().reset_index(name="article_count")
        .sort_values("article_count", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    return counts


def publication_time_distribution(news: pd.DataFrame) -> dict:
    dates = pd.to_datetime(news["date"])
    by_day_of_week = dates.dt.day_name().value_counts().to_dict()
    by_hour = dates.dt.hour.value_counts().sort_index().to_dict()
    return {"by_day_of_week": by_day_of_week, "by_hour": by_hour}


def articles_per_month(news: pd.DataFrame) -> pd.DataFrame:
    dates = pd.to_datetime(news["date"])
    monthly = dates.dt.to_period("M").value_counts().sort_index()
    return monthly.rename_axis("month").reset_index(name="article_count").assign(
        month=lambda d: d["month"].astype(str)
    )


def articles_per_stock(news: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    if "stock" not in news.columns:
        return pd.DataFrame(columns=["stock", "article_count"])
    counts = (
        news.groupby("stock").size().reset_index(name="article_count")
        .sort_values("article_count", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    return counts


def sentiment_distribution(news: pd.DataFrame) -> dict:
    if "sentiment" not in news.columns:
        return {}
    return news["sentiment"].value_counts().to_dict()
