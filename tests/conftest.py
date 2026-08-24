from __future__ import annotations

import pandas as pd
import pytest

from stock_sentiment.data.sample_data import generate_sample_news, generate_sample_prices


@pytest.fixture(autouse=True)
def _isolated_settings(tmp_path, monkeypatch):
    """Every test gets its own data dir / DuckDB file — no shared state, no network writes."""
    from stock_sentiment.config import settings

    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "raw_news_path", tmp_path / "raw_analyst_ratings.csv")
    monkeypatch.setattr(settings, "raw_prices_dir", tmp_path / "yfinance_data")
    monkeypatch.setattr(settings, "duckdb_path", tmp_path / "analytics.duckdb")
    monkeypatch.setattr(settings, "anthropic_api_key", None)
    yield settings


@pytest.fixture
def sample_news() -> pd.DataFrame:
    return generate_sample_news(tickers=["AAPL", "TSLA"], n_days=30, articles_per_day=2)


@pytest.fixture
def sample_prices() -> pd.DataFrame:
    return generate_sample_prices("AAPL", n_days=60)
