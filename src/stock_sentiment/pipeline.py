"""End-to-end batch pipeline: ingest -> validate -> feature -> analyze -> persist -> report.

This is the single orchestration point the CLI, tests, and (indirectly,
via the DuckDB store it writes to) the API all rely on. Every step logs
what ran, on what data, how long it took, and whether it succeeded —
so a failed run is diagnosable from the log alone.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import pandas as pd

from stock_sentiment.analysis.correlation import (
    aggregate_daily_sentiment,
    correlate_sentiment_with_returns,
)
from stock_sentiment.analysis.eda import sentiment_distribution
from stock_sentiment.config import settings
from stock_sentiment.data.ingest import download_prices, load_news
from stock_sentiment.data.storage import AnalyticsStore
from stock_sentiment.data.validation import profile_news, profile_prices
from stock_sentiment.features.sentiment import score_headlines
from stock_sentiment.features.technical_indicators import add_all_indicators
from stock_sentiment.features.text_topics import fit_topic_model
from stock_sentiment.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class PipelineRunReport:
    started_at: float
    duration_seconds: float = 0.0
    news_rows: int = 0
    tickers_processed: list[str] = field(default_factory=list)
    data_quality_issues: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    succeeded: bool = False
    error: str | None = None

    def as_dict(self) -> dict:
        return {
            "started_at": self.started_at,
            "duration_seconds": round(self.duration_seconds, 3),
            "news_rows": self.news_rows,
            "tickers_processed": self.tickers_processed,
            "data_quality_issues": self.data_quality_issues,
            "metrics": self.metrics,
            "succeeded": self.succeeded,
            "error": self.error,
        }


def run_pipeline(
    tickers: list[str] | None = None,
    news_path: str | None = None,
    store: AnalyticsStore | None = None,
    persist: bool = True,
) -> PipelineRunReport:
    tickers = tickers or settings.default_tickers
    store = store or AnalyticsStore()
    report = PipelineRunReport(started_at=time.time())

    try:
        logger.info("Pipeline run starting for tickers=%s", tickers)

        # 1. Ingest + validate news
        news = load_news(news_path)
        news_quality = profile_news(news)
        report.news_rows = len(news)
        report.data_quality_issues.extend(f"news: {i}" for i in news_quality.issues)
        logger.info("Loaded %d news rows (%d quality issues)", len(news), len(news_quality.issues))

        # 2. Feature engineering: sentiment + topics
        news = score_headlines(news)
        topic_result = None
        if len(news) >= 10:
            topic_result = fit_topic_model(news["cleaned_headline"].tolist())
            logger.info("Fit LDA topic model: %s", topic_result.topics)

        # 3. Per-ticker: prices + indicators + correlation
        price_data = download_prices(tickers)
        per_ticker_metrics: dict[str, dict] = {}

        for ticker in tickers:
            prices = price_data.get(ticker)
            if prices is None or prices.empty:
                logger.warning("No price data for %s; skipping", ticker)
                continue

            price_quality = profile_prices(prices)
            report.data_quality_issues.extend(f"{ticker} prices: {i}" for i in price_quality.issues)

            enriched = add_all_indicators(prices)

            ticker_news = news[news.get("stock", "") == ticker] if "stock" in news.columns else news
            daily_sentiment = aggregate_daily_sentiment(ticker_news)
            correlation = correlate_sentiment_with_returns(daily_sentiment, enriched, ticker=ticker)

            per_ticker_metrics[ticker] = {
                "sentiment_distribution": sentiment_distribution(ticker_news),
                "correlation": correlation.as_dict(),
                "latest_close": float(enriched["close"].iloc[-1]),
                "latest_rsi": None if pd.isna(enriched["rsi"].iloc[-1]) else float(enriched["rsi"].iloc[-1]),
            }
            report.tickers_processed.append(ticker)

            if persist:
                store.write_table(f"prices_{ticker.lower()}", enriched)
                store.write_table(f"news_{ticker.lower()}", ticker_news)

        report.metrics = {"tickers": per_ticker_metrics}
        if topic_result is not None:
            report.metrics["topics"] = topic_result.topics

        if persist:
            store.write_table("news_all", news)

        report.succeeded = True
    except Exception as exc:  # noqa: BLE001 - captured in the report for observability
        logger.exception("Pipeline run failed: %s", exc)
        report.error = str(exc)
        report.succeeded = False
    finally:
        report.duration_seconds = time.time() - report.started_at
        logger.info(
            "Pipeline run finished in %.2fs (succeeded=%s, tickers=%d)",
            report.duration_seconds,
            report.succeeded,
            len(report.tickers_processed),
        )

    return report
