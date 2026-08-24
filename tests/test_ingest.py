from __future__ import annotations

import pandas as pd

from stock_sentiment.data.ingest import download_prices, load_news, load_prices_from_csv


def test_load_news_falls_back_to_sample_when_file_missing(tmp_path):
    news = load_news(tmp_path / "does_not_exist.csv")
    assert not news.empty
    assert {"headline", "cleaned_headline", "date"}.issubset(news.columns)


def test_load_news_cleans_and_parses_real_file(tmp_path):
    csv_path = tmp_path / "news.csv"
    pd.DataFrame(
        {
            "Unnamed: 0": [0, 1],
            "headline": ["Stocks Surge!!", "Bad News..."],
            "date": ["2024-01-01", "not-a-date"],
            "stock": ["AAPL", "TSLA"],
        }
    ).to_csv(csv_path, index=False)

    news = load_news(csv_path)
    assert len(news) == 1  # the unparseable date row is dropped
    assert "unnamed: 0" not in news.columns
    assert news.iloc[0]["cleaned_headline"] == "stocks surge"


def test_load_prices_from_csv_normalizes_columns(tmp_path):
    csv_path = tmp_path / "AAPL_historical_data.csv"
    pd.DataFrame(
        {
            "Date": ["2024-01-01", "2024-01-02"],
            "Open": [100, 101],
            "High": [102, 103],
            "Low": [99, 100],
            "Close": [101, 102],
            "Volume": [1000, 1100],
        }
    ).to_csv(csv_path, index=False)

    prices = load_prices_from_csv(csv_path)
    assert list(prices.columns[:6]) == ["date", "open", "high", "low", "close", "volume"]
    assert prices["close"].iloc[0] == 101


def test_download_prices_falls_back_without_network(monkeypatch):
    import stock_sentiment.data.ingest as ingest_module

    class _BrokenYfinance:
        @staticmethod
        def download(*args, **kwargs):
            raise ConnectionError("no network in test")

    monkeypatch.setattr(ingest_module, "yf", _BrokenYfinance, raising=False)

    result = download_prices(["AAPL"])
    assert "AAPL" in result
    assert not result["AAPL"].empty
