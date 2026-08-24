"""Sentiment <-> price-return correlation analysis.

Computes same-day and lagged Pearson correlations between daily
aggregated news sentiment and stock returns, with the sample size and
a significance estimate attached — a bare correlation coefficient
without ``n`` or a p-value is not trustworthy enough to act on.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class CorrelationResult:
    ticker: str
    lag_days: int
    pearson_r: float
    p_value: float
    n_observations: int

    def is_significant(self, alpha: float = 0.05) -> bool:
        return self.n_observations >= 3 and not np.isnan(self.p_value) and self.p_value < alpha

    def as_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "lag_days": self.lag_days,
            "pearson_r": None if np.isnan(self.pearson_r) else round(self.pearson_r, 4),
            "p_value": None if np.isnan(self.p_value) else round(self.p_value, 4),
            "n_observations": self.n_observations,
            "is_significant": self.is_significant(),
        }


def aggregate_daily_sentiment(news: pd.DataFrame, date_col: str = "date", score_col: str = "sentiment_score") -> pd.DataFrame:
    daily = (
        news.assign(**{date_col: pd.to_datetime(news[date_col]).dt.normalize()})
        .groupby(date_col)[score_col]
        .agg(mean_sentiment="mean", article_count="count")
        .reset_index()
    )
    return daily


def correlate_sentiment_with_returns(
    daily_sentiment: pd.DataFrame,
    prices: pd.DataFrame,
    ticker: str = "",
    lag_days: int = 0,
    date_col: str = "date",
    sentiment_col: str = "mean_sentiment",
    return_col: str = "daily_return",
) -> CorrelationResult:
    """Correlate sentiment on day T with returns on day T + ``lag_days``.

    ``lag_days=0`` tests the "does today's news move today's price"
    hypothesis; positive values test whether news leads price action.
    """
    sentiment = daily_sentiment[[date_col, sentiment_col]].copy()
    sentiment[date_col] = pd.to_datetime(sentiment[date_col]).dt.normalize()

    price_returns = prices[[date_col, return_col]].copy()
    price_returns[date_col] = pd.to_datetime(price_returns[date_col]).dt.normalize()
    if lag_days:
        price_returns[date_col] = price_returns[date_col] - pd.Timedelta(days=lag_days)

    merged = pd.merge(sentiment, price_returns, on=date_col, how="inner").dropna(
        subset=[sentiment_col, return_col]
    )

    if len(merged) < 3:
        return CorrelationResult(ticker, lag_days, float("nan"), float("nan"), len(merged))

    r, p = stats.pearsonr(merged[sentiment_col], merged[return_col])
    return CorrelationResult(ticker, lag_days, float(r), float(p), len(merged))


def correlation_matrix_over_lags(
    daily_sentiment: pd.DataFrame, prices: pd.DataFrame, ticker: str, max_lag: int = 3
) -> list[CorrelationResult]:
    return [
        correlate_sentiment_with_returns(daily_sentiment, prices, ticker=ticker, lag_days=lag)
        for lag in range(0, max_lag + 1)
    ]
