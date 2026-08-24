from __future__ import annotations

import pandas as pd

from stock_sentiment.data.validation import profile_news, profile_prices


def test_profile_news_flags_duplicates_and_nulls():
    news = pd.DataFrame(
        {
            "headline": ["a headline", "a headline", None],
            "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02"]),
            "stock": ["AAPL", "AAPL", "AAPL"],
        }
    )
    report = profile_news(news)
    assert report.row_count == 3
    assert report.duplicate_rows >= 1
    assert not report.is_clean
    assert any("duplicate" in issue for issue in report.issues)


def test_profile_news_clean_dataset_has_no_issues():
    news = pd.DataFrame(
        {
            "headline": ["a", "b", "c"],
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "stock": ["AAPL", "TSLA", "GOOG"],
        }
    )
    report = profile_news(news)
    assert report.is_clean


def test_profile_prices_flags_high_less_than_low():
    prices = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "open": [10.0, 10.0],
            "high": [9.0, 12.0],
            "low": [11.0, 9.0],
            "close": [10.0, 10.5],
            "volume": [100.0, 200.0],
        }
    )
    report = profile_prices(prices)
    assert any("high < low" in issue for issue in report.issues)


def test_profile_empty_dataframe():
    report = profile_news(pd.DataFrame())
    assert not report.is_clean
    assert report.row_count == 0
