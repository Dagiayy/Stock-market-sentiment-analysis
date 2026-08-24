from __future__ import annotations

import pytest

from stock_sentiment import pipeline as pipeline_module
from stock_sentiment.data.sample_data import generate_sample_prices
from stock_sentiment.data.storage import AnalyticsStore


@pytest.fixture(autouse=True)
def _no_network_prices(monkeypatch):
    """Never hit yfinance/network in tests -- use deterministic synthetic prices."""

    def fake_download_prices(tickers, period="1y", allow_sample_fallback=True):
        return {t: generate_sample_prices(t) for t in tickers}

    monkeypatch.setattr(pipeline_module, "download_prices", fake_download_prices)


def test_pipeline_runs_end_to_end(tmp_path):
    store = AnalyticsStore(db_path=tmp_path / "run.duckdb")
    report = pipeline_module.run_pipeline(tickers=["AAPL", "TSLA"], store=store)

    assert report.succeeded
    assert report.error is None
    assert report.news_rows > 0
    assert set(report.tickers_processed) == {"AAPL", "TSLA"}
    assert "AAPL" in report.metrics["tickers"]
    assert "correlation" in report.metrics["tickers"]["AAPL"]


def test_pipeline_persists_to_duckdb(tmp_path):
    store = AnalyticsStore(db_path=tmp_path / "run.duckdb")
    pipeline_module.run_pipeline(tickers=["AAPL"], store=store)

    tables = store.list_tables()
    assert "prices_aapl" in tables
    assert "news_all" in tables


def test_pipeline_can_skip_persistence(tmp_path):
    store = AnalyticsStore(db_path=tmp_path / "run.duckdb")
    report = pipeline_module.run_pipeline(tickers=["AAPL"], store=store, persist=False)

    assert report.succeeded
    assert store.list_tables() == []


def test_pipeline_report_serializes_to_dict(tmp_path):
    store = AnalyticsStore(db_path=tmp_path / "run.duckdb")
    report = pipeline_module.run_pipeline(tickers=["AAPL"], store=store)
    payload = report.as_dict()
    assert payload["succeeded"] is True
    assert "duration_seconds" in payload
