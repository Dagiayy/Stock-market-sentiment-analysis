from __future__ import annotations

from stock_sentiment.analysis import eda, trends
from stock_sentiment.data.sample_data import generate_sample_news
from stock_sentiment.features.sentiment import score_headlines
from stock_sentiment.features.text_topics import fit_topic_model


def _scored_news():
    news = generate_sample_news(tickers=["AAPL", "TSLA"], n_days=40, articles_per_day=2)
    return score_headlines(news)


def test_headline_length_stats():
    news = _scored_news()
    stats = eda.headline_length_stats(news)
    assert stats["min"] <= stats["mean"] <= stats["max"]


def test_publisher_activity():
    news = _scored_news()
    result = eda.publisher_activity(news, top_n=3)
    assert len(result) <= 3
    assert list(result.columns) == ["publisher", "article_count"]


def test_publication_time_distribution():
    news = _scored_news()
    dist = eda.publication_time_distribution(news)
    assert "by_day_of_week" in dist
    assert "by_hour" in dist


def test_articles_per_month_and_per_stock():
    news = _scored_news()
    monthly = eda.articles_per_month(news)
    per_stock = eda.articles_per_stock(news)
    assert "article_count" in monthly.columns
    assert set(per_stock["stock"]) <= {"AAPL", "TSLA"}


def test_sentiment_distribution():
    news = _scored_news()
    dist = eda.sentiment_distribution(news)
    assert set(dist.keys()) <= {"Positive", "Negative", "Neutral"}


def test_sentiment_distribution_missing_column_returns_empty():
    news = generate_sample_news(tickers=["AAPL"], n_days=5)
    assert eda.sentiment_distribution(news) == {}


def test_sentiment_trend_shape():
    news = _scored_news()
    trend = trends.sentiment_trend(news)
    assert "date" in trend.columns


def test_topic_trend_shape():
    news = _scored_news()
    topic_result = fit_topic_model(news["headline"].str.lower().tolist(), n_topics=3)
    trend = trends.topic_trend(news, topic_result.document_topics, n_topics=3)
    assert {"topic_0", "topic_1", "topic_2", "date"}.issubset(trend.columns)
