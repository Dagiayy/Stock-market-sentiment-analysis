"""Headline sentiment scoring.

The original project computed sentiment three different ways in three
different files (VADER in one script, TextBlob in another, with no
shared classification logic), producing inconsistent labels depending
on which script last ran. This module is the single source of truth:
one ``SentimentAnalyzer`` protocol, two interchangeable backends, and
one classification rule.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Protocol

import pandas as pd

from stock_sentiment.config import settings
from stock_sentiment.logging_config import get_logger

logger = get_logger(__name__)


class SentimentBackend(Protocol):
    def score(self, text: str) -> float: ...


class VaderBackend:
    """Lexicon-based scorer tuned for short, informal text like headlines."""

    def __init__(self) -> None:
        self._analyzer = _get_vader_analyzer()

    def score(self, text: str) -> float:
        return self._analyzer.polarity_scores(text)["compound"]


class TextBlobBackend:
    """Polarity via TextBlob's pattern-based lexicon; useful as a second opinion."""

    def score(self, text: str) -> float:
        from textblob import TextBlob

        return float(TextBlob(text).sentiment.polarity)


@lru_cache(maxsize=1)
def _get_vader_analyzer():
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer

    try:
        return SentimentIntensityAnalyzer()
    except LookupError:
        logger.info("VADER lexicon not found locally; downloading it now")
        nltk.download("vader_lexicon", quiet=True)
        return SentimentIntensityAnalyzer()


def get_backend(name: str | None = None) -> SentimentBackend:
    backend_name = (name or settings.sentiment_backend).lower()
    if backend_name == "vader":
        return VaderBackend()
    if backend_name == "textblob":
        return TextBlobBackend()
    raise ValueError(f"Unknown sentiment backend: {backend_name!r}")


def classify(score: float) -> str:
    if score > settings.sentiment_positive_threshold:
        return "Positive"
    if score < settings.sentiment_negative_threshold:
        return "Negative"
    return "Neutral"


def score_text(text: str, backend: str | None = None) -> float:
    return get_backend(backend).score(text)


def score_headlines(news: pd.DataFrame, backend: str | None = None, text_column: str = "cleaned_headline") -> pd.DataFrame:
    """Add ``sentiment_score`` and ``sentiment`` columns to a news DataFrame."""
    if text_column not in news.columns:
        text_column = "headline"

    analyzer = get_backend(backend)
    result = news.copy()
    result["sentiment_score"] = result[text_column].astype(str).apply(analyzer.score)
    result["sentiment"] = result["sentiment_score"].apply(classify)
    return result
