from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from stock_sentiment.analysis.correlation import (
    aggregate_daily_sentiment,
    correlate_sentiment_with_returns,
    correlation_matrix_over_lags,
)


def test_aggregate_daily_sentiment_groups_by_day():
    news = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-01", "2024-01-02"]),
            "sentiment_score": [0.5, -0.1, 0.3],
        }
    )
    daily = aggregate_daily_sentiment(news)
    assert len(daily) == 2
    row = daily.loc[daily["date"] == pd.Timestamp("2024-01-01")].iloc[0]
    assert row["mean_sentiment"] == pytest.approx(0.2)
    assert row["article_count"] == 2


def test_perfect_positive_correlation_detected():
    dates = pd.date_range("2024-01-01", periods=20, freq="D")
    sentiment = pd.DataFrame({"date": dates, "mean_sentiment": np.linspace(-1, 1, 20)})
    returns = pd.DataFrame({"date": dates, "daily_return": np.linspace(-1, 1, 20)})

    result = correlate_sentiment_with_returns(sentiment, returns, ticker="TEST")
    assert result.pearson_r == pytest.approx(1.0, abs=1e-6)
    assert result.n_observations == 20
    assert result.is_significant()


def test_insufficient_data_returns_nan():
    sentiment = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=2), "mean_sentiment": [0.1, 0.2]})
    returns = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=2), "daily_return": [1.0, 2.0]})

    result = correlate_sentiment_with_returns(sentiment, returns, ticker="TEST")
    assert np.isnan(result.pearson_r)
    assert not result.is_significant()


def test_lagged_correlation_shifts_dates():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    sentiment = pd.DataFrame({"date": dates, "mean_sentiment": np.arange(10)})
    # returns[i] should align with sentiment[i] when lag_days=1 shifts returns back by 1 day
    returns = pd.DataFrame({"date": dates + pd.Timedelta(days=1), "daily_return": np.arange(10)})

    same_day = correlate_sentiment_with_returns(sentiment, returns, lag_days=0)
    lagged = correlate_sentiment_with_returns(sentiment, returns, lag_days=1)

    assert same_day.n_observations == 0 or same_day.n_observations < lagged.n_observations
    assert lagged.n_observations == 10
    assert lagged.pearson_r == pytest.approx(1.0, abs=1e-6)


def test_correlation_matrix_over_lags_returns_expected_length():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    sentiment = pd.DataFrame({"date": dates, "mean_sentiment": np.arange(10)})
    returns = pd.DataFrame({"date": dates, "daily_return": np.arange(10)})

    results = correlation_matrix_over_lags(sentiment, returns, ticker="TEST", max_lag=3)
    assert len(results) == 4
    assert [r.lag_days for r in results] == [0, 1, 2, 3]
