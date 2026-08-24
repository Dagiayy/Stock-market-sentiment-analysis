"""Centralized, environment-driven configuration.

All tunables live here so nothing is hard-coded deeper in the codebase.
Values are read from the process environment / a local ``.env`` file
(never committed — see ``.env.example``).
"""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    # --- Filesystem layout -------------------------------------------------
    data_dir: Path = REPO_ROOT / "data"
    raw_news_path: Path = REPO_ROOT / "data" / "raw_analyst_ratings.csv"
    raw_prices_dir: Path = REPO_ROOT / "data" / "yfinance_data"
    duckdb_path: Path = REPO_ROOT / "data" / "processed" / "analytics.duckdb"

    # --- Domain defaults -----------------------------------------------------
    default_tickers: list[str] = ["AAPL", "AMZN", "TSLA", "GOOG", "META"]
    lda_topics: int = 5
    rsi_period: int = 14
    sma_period: int = 20
    ema_period: int = 20
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    bollinger_period: int = 20
    outlier_iqr_multiplier: float = 1.5

    # --- Sentiment engine ----------------------------------------------------
    sentiment_backend: str = "vader"  # "vader" | "textblob"
    sentiment_positive_threshold: float = 0.05
    sentiment_negative_threshold: float = -0.05

    # --- AI / LLM --------------------------------------------------------------
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"
    ai_insights_enabled: bool = True
    ai_max_tokens: int = 1024

    # --- API ---------------------------------------------------------------
    api_title: str = "Stock Sentiment Analysis API"
    api_cors_origins: list[str] = ["*"]
    api_rate_limit_per_minute: int = 60

    # --- Observability -------------------------------------------------------
    log_level: str = "INFO"
    log_json: bool = False


settings = Settings()
