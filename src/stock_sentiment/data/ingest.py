"""Data ingestion: news headlines and OHLCV prices, from disk or the network.

Every loader normalizes column names to a consistent lowercase schema
(``date``, ``open``, ``high``, ``low``, ``close``, ``volume`` /
``headline``, ``url``, ``publisher``, ``date``, ``stock``) so downstream
code never has to guess a source's casing conventions again.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from stock_sentiment.config import settings
from stock_sentiment.data.sample_data import generate_sample_news, generate_sample_prices
from stock_sentiment.logging_config import get_logger

logger = get_logger(__name__)

_PUNCT_RE = re.compile(r"[^\w\s]")


def _clean_headline(text: str) -> str:
    return _PUNCT_RE.sub("", str(text)).lower().strip()


def load_news(file_path: str | Path | None = None, *, allow_sample_fallback: bool = True) -> pd.DataFrame:
    """Load and clean the financial-news headline dataset.

    Falls back to a deterministic synthetic dataset when no real file
    is present, so the pipeline is runnable immediately after clone.
    """
    path = Path(file_path) if file_path else settings.raw_news_path

    if not path.exists():
        if not allow_sample_fallback:
            raise FileNotFoundError(f"News data not found at {path}")
        logger.warning("No news data found at %s; generating synthetic sample dataset", path)
        news = generate_sample_news(settings.default_tickers)
    else:
        try:
            news = pd.read_csv(path)
        except Exception as exc:  # noqa: BLE001 - surfaced to caller via empty frame + log
            logger.error("Failed to read news CSV at %s: %s", path, exc)
            return pd.DataFrame()

    news.columns = [c.strip().lower() for c in news.columns]
    news = news.loc[:, ~news.columns.str.contains(r"^unnamed")]

    if "headline" not in news.columns:
        raise ValueError("News dataset must contain a 'headline' column")

    news["headline"] = news["headline"].astype(str)
    news["cleaned_headline"] = news["headline"].apply(_clean_headline)
    news["date"] = pd.to_datetime(news["date"], errors="coerce", utc=False)

    before = len(news)
    news = news.dropna(subset=["date"]).reset_index(drop=True)
    dropped = before - len(news)
    if dropped:
        logger.info("Dropped %d news rows with unparseable dates", dropped)

    return news


def load_prices_from_csv(file_path: str | Path) -> pd.DataFrame:
    path = Path(file_path)
    prices = pd.read_csv(path)
    prices.columns = [c.strip().lower() for c in prices.columns]
    rename_map = {"adj close": "adj_close"}
    prices = prices.rename(columns=rename_map)
    prices["date"] = pd.to_datetime(prices["date"], errors="coerce")
    prices = prices.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    for col in ("open", "high", "low", "close", "volume"):
        if col in prices.columns:
            prices[col] = pd.to_numeric(prices[col], errors="coerce")
    return prices


def load_prices_dir(directory: str | Path | None = None) -> dict[str, pd.DataFrame]:
    """Load every ``<TICKER>_historical_data.csv``-style file in a directory."""
    dir_path = Path(directory) if directory else settings.raw_prices_dir
    if not dir_path.exists():
        return {}

    result: dict[str, pd.DataFrame] = {}
    for csv_file in sorted(dir_path.glob("*.csv")):
        ticker = csv_file.stem.split("_")[0].upper()
        try:
            result[ticker] = load_prices_from_csv(csv_file)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to load price file %s: %s", csv_file, exc)
    return result


def download_prices(
    tickers: list[str] | None = None, period: str = "1y", *, allow_sample_fallback: bool = True
) -> dict[str, pd.DataFrame]:
    """Download historical OHLCV data for each ticker via yfinance.

    Falls back to synthetic price series (per-ticker, seeded) if the
    network/API is unavailable, so pipelines never hard-fail offline.
    """
    tickers = tickers or settings.default_tickers
    result: dict[str, pd.DataFrame] = {}

    yf = globals().get("yf")
    if yf is None:
        try:
            import yfinance as yf
        except ImportError:
            yf = None
            logger.warning("yfinance not installed; using synthetic price data")

    for ticker in tickers:
        df = None
        if yf is not None:
            try:
                raw = yf.download(ticker, period=period, progress=False, auto_adjust=False)
                if raw is not None and not raw.empty:
                    if isinstance(raw.columns, pd.MultiIndex):
                        raw.columns = raw.columns.get_level_values(0)
                    raw = raw.reset_index()
                    raw.columns = [str(c).strip().lower() for c in raw.columns]
                    df = raw
            except Exception as exc:  # noqa: BLE001
                logger.warning("yfinance download failed for %s: %s", ticker, exc)

        if df is None or df.empty:
            if not allow_sample_fallback:
                continue
            logger.info("Using synthetic price series for %s", ticker)
            df = generate_sample_prices(ticker)

        result[ticker] = df

    return result
