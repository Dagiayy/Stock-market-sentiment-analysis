from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from stock_sentiment.features.technical_indicators import (
    add_all_indicators,
    bollinger_bands,
    daily_returns,
    ema,
    macd,
    rsi,
    sma,
)


@pytest.fixture
def close_series() -> pd.Series:
    rng = np.random.default_rng(0)
    return pd.Series(100 + np.cumsum(rng.normal(0, 1, 100)))


def test_sma_matches_manual_rolling_mean(close_series):
    result = sma(close_series, period=10)
    expected = close_series.rolling(10).mean()
    pd.testing.assert_series_equal(result, expected)


def test_ema_reacts_faster_than_sma_to_a_shock():
    flat = pd.Series([100.0] * 30 + [200.0] * 10)
    sma_result = sma(flat, period=10)
    ema_result = ema(flat, period=10)
    assert ema_result.iloc[31] > sma_result.iloc[31]


def test_rsi_is_bounded_0_100(close_series):
    result = rsi(close_series, period=14)
    valid = result.dropna()
    assert (valid >= 0).all() and (valid <= 100).all()


def test_rsi_is_100_for_strictly_increasing_series():
    increasing = pd.Series(range(1, 30))
    result = rsi(increasing, period=14)
    assert result.iloc[-1] == pytest.approx(100)


def test_macd_columns_present(close_series):
    result = macd(close_series)
    assert list(result.columns) == ["macd", "macd_signal", "macd_histogram"]
    assert len(result) == len(close_series)


def test_bollinger_bands_ordering(close_series):
    bands = bollinger_bands(close_series, period=20)
    valid = bands.dropna()
    assert (valid["bb_upper"] >= valid["bb_middle"]).all()
    assert (valid["bb_middle"] >= valid["bb_lower"]).all()


def test_daily_returns_first_value_is_nan():
    series = pd.Series([100.0, 110.0, 99.0])
    result = daily_returns(series)
    assert pd.isna(result.iloc[0])
    assert result.iloc[1] == pytest.approx(10.0)


def test_add_all_indicators_preserves_row_count(sample_prices):
    enriched = add_all_indicators(sample_prices)
    assert len(enriched) == len(sample_prices)
    for col in ("sma", "ema", "rsi", "macd", "bb_upper", "daily_return"):
        assert col in enriched.columns
