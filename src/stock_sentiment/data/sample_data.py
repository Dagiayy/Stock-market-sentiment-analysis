"""Deterministic synthetic-data generator.

The original Kaggle "raw_analyst_ratings" news dataset is not
redistributable and is git-ignored, so a clone of this repository has
no data to run against out of the box. This module generates a small,
realistic, seeded synthetic dataset (news headlines + OHLCV prices) so
the full pipeline, tests, and API demos all work with zero setup.
Real data (see ``ingest.py``) is used automatically instead whenever
it is present on disk.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

_POSITIVE_TEMPLATES = [
    "{ticker} shares surge after earnings beat expectations",
    "{ticker} announces record quarterly revenue growth",
    "Analysts upgrade {ticker} to 'buy' citing strong outlook",
    "{ticker} stock rallies on positive guidance",
    "{ticker} beats consensus estimates, raises full-year forecast",
]
_NEGATIVE_TEMPLATES = [
    "{ticker} shares tumble after disappointing earnings report",
    "{ticker} downgraded amid weakening demand concerns",
    "{ticker} stock falls on guidance cut",
    "Analysts warn of headwinds facing {ticker}",
    "{ticker} misses revenue targets, shares slide",
]
_NEUTRAL_TEMPLATES = [
    "{ticker} to report quarterly earnings next week",
    "{ticker} announces new product lineup",
    "{ticker} holds investor day, outlines strategy",
    "{ticker} appoints new chief financial officer",
    "{ticker} files annual report with regulators",
]
_PUBLISHERS = ["Reuters", "Bloomberg", "MarketWatch", "CNBC", "Yahoo Finance"]


def generate_sample_news(
    tickers: list[str], n_days: int = 120, articles_per_day: int = 3, seed: int = 42
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    end = pd.Timestamp.today().normalize()
    dates = pd.bdate_range(end=end, periods=n_days)

    rows = []
    templates = _POSITIVE_TEMPLATES + _NEGATIVE_TEMPLATES + _NEUTRAL_TEMPLATES
    weights = (
        [1.4] * len(_POSITIVE_TEMPLATES)
        + [1.0] * len(_NEGATIVE_TEMPLATES)
        + [1.2] * len(_NEUTRAL_TEMPLATES)
    )
    weights = np.array(weights) / sum(weights)

    for date in dates:
        for ticker in tickers:
            n_articles = rng.poisson(articles_per_day) or 1
            for _ in range(n_articles):
                template = rng.choice(templates, p=weights)
                rows.append(
                    {
                        "headline": template.format(ticker=ticker),
                        "url": f"https://example.com/news/{ticker.lower()}-{date.strftime('%Y%m%d')}",
                        "publisher": rng.choice(_PUBLISHERS),
                        "date": date + pd.Timedelta(hours=int(rng.integers(9, 16))),
                        "stock": ticker,
                    }
                )
    return pd.DataFrame(rows).sort_values("date").reset_index(drop=True)


def generate_sample_prices(ticker: str, n_days: int = 120, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed + abs(hash(ticker)) % 1000)
    end = pd.Timestamp.today().normalize()
    dates = pd.bdate_range(end=end, periods=n_days)

    daily_returns = rng.normal(loc=0.0006, scale=0.018, size=n_days)
    close = 100 * np.exp(np.cumsum(daily_returns))
    open_ = close * (1 + rng.normal(0, 0.003, n_days))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.004, n_days)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.004, n_days)))
    volume = rng.integers(1_000_000, 20_000_000, n_days).astype(float)

    return pd.DataFrame(
        {
            "date": dates,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )
