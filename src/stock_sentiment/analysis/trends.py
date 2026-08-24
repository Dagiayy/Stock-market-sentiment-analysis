"""Time-series aggregation of sentiment and topic signals.

Pure data transforms (no plotting) so they are testable and reusable
by both the API and any notebook/report that wants the numbers.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def sentiment_trend(news: pd.DataFrame) -> pd.DataFrame:
    """Daily count of each sentiment label."""
    trend = (
        news.groupby([pd.to_datetime(news["date"]).dt.date, "sentiment"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
        .rename(columns={"date": "date"})
    )
    return trend


def topic_trend(news: pd.DataFrame, document_topics: np.ndarray, n_topics: int) -> pd.DataFrame:
    """Average topic probability per day."""
    topic_df = pd.DataFrame(document_topics, columns=[f"topic_{i}" for i in range(n_topics)])
    topic_df["date"] = pd.to_datetime(news["date"]).dt.date.values
    return topic_df.groupby("date").mean().reset_index()
