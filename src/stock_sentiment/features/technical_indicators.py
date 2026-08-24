"""Technical indicators, implemented in pure pandas/numpy.

The original project depended on TA-Lib, a C library with no wheel on
PyPI for most platforms (the committed ``requirements.txt`` even
pointed at a local Windows ``.whl`` file on one contributor's laptop —
uninstallable for anyone else, and unbuildable in a minimal Docker
image without a multi-step apt/compile dance in CI). SMA, EMA, RSI,
MACD, and Bollinger Bands are standard, well-defined formulas; a small
pandas implementation is exact, portable, and dependency-free.
"""
from __future__ import annotations

import pandas as pd

from stock_sentiment.config import settings


def sma(series: pd.Series, period: int | None = None) -> pd.Series:
    return series.rolling(window=period or settings.sma_period).mean()


def ema(series: pd.Series, period: int | None = None) -> pd.Series:
    return series.ewm(span=period or settings.ema_period, adjust=False).mean()


def rsi(series: pd.Series, period: int | None = None) -> pd.Series:
    period = period or settings.rsi_period
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    result = 100 - (100 / (1 + rs))
    # No losses in the window -> maximally overbought; no gains -> maximally oversold.
    result = result.fillna(100)
    result = result.mask((avg_gain == 0) & (avg_loss != 0), 0)
    return result


def macd(
    series: pd.Series,
    fast_period: int | None = None,
    slow_period: int | None = None,
    signal_period: int | None = None,
) -> pd.DataFrame:
    fast = ema(series, fast_period or settings.macd_fast)
    slow = ema(series, slow_period or settings.macd_slow)
    macd_line = fast - slow
    signal_line = macd_line.ewm(span=signal_period or settings.macd_signal, adjust=False).mean()
    return pd.DataFrame(
        {"macd": macd_line, "macd_signal": signal_line, "macd_histogram": macd_line - signal_line}
    )


def bollinger_bands(
    series: pd.Series, period: int | None = None, num_std: float = 2.0
) -> pd.DataFrame:
    period = period or settings.bollinger_period
    middle = sma(series, period)
    std = series.rolling(window=period).std()
    return pd.DataFrame(
        {
            "bb_upper": middle + num_std * std,
            "bb_middle": middle,
            "bb_lower": middle - num_std * std,
        }
    )


def daily_returns(series: pd.Series) -> pd.Series:
    return series.pct_change() * 100


def add_all_indicators(prices: pd.DataFrame, price_column: str = "close") -> pd.DataFrame:
    """Return a copy of ``prices`` enriched with every indicator this module defines."""
    df = prices.copy()
    close = df[price_column]

    df["sma"] = sma(close)
    df["ema"] = ema(close)
    df["rsi"] = rsi(close)
    df = pd.concat([df, macd(close), bollinger_bands(close)], axis=1)
    df["daily_return"] = daily_returns(close)
    return df
