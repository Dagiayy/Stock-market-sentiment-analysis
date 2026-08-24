from __future__ import annotations

from stock_sentiment.data.sample_data import generate_sample_news
from stock_sentiment.features.text_topics import fit_topic_model


def test_fit_topic_model_returns_requested_topic_count():
    news = generate_sample_news(tickers=["AAPL", "TSLA", "GOOG"], n_days=60, articles_per_day=2)
    result = fit_topic_model(news["headline"].str.lower().tolist(), n_topics=4)

    assert len(result.topics) == 4
    assert result.document_topics.shape[0] == len(news)
    assert result.document_topics.shape[1] == 4
    for topic in result.topics:
        assert topic.startswith("Topic")
