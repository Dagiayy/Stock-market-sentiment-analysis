from __future__ import annotations

import pandas as pd
import pytest

from stock_sentiment.features.sentiment import classify, get_backend, score_headlines


@pytest.mark.parametrize("backend_name", ["vader", "textblob"])
def test_positive_headline_scores_positive(backend_name):
    backend = get_backend(backend_name)
    score = backend.score("stocks soar as company reports excellent, outstanding record profit")
    assert score > 0
    assert classify(score) == "Positive"


@pytest.mark.parametrize("backend_name", ["vader", "textblob"])
def test_negative_headline_scores_negative(backend_name):
    backend = get_backend(backend_name)
    score = backend.score("shares plunge as company reports terrible, disastrous awful loss")
    assert score < 0
    assert classify(score) == "Negative"


def test_classify_thresholds():
    assert classify(0.5) == "Positive"
    assert classify(-0.5) == "Negative"
    assert classify(0.0) == "Neutral"


def test_unknown_backend_raises():
    with pytest.raises(ValueError):
        get_backend("not-a-real-backend")


def test_score_headlines_adds_columns():
    news = pd.DataFrame({"cleaned_headline": ["great earnings beat", "terrible awful crash"]})
    result = score_headlines(news)
    assert {"sentiment_score", "sentiment"}.issubset(result.columns)
    assert result.loc[0, "sentiment"] == "Positive"
    assert result.loc[1, "sentiment"] == "Negative"


def test_score_headlines_falls_back_to_headline_column():
    news = pd.DataFrame({"headline": ["great earnings beat expectations"]})
    result = score_headlines(news)
    assert result.loc[0, "sentiment"] == "Positive"
