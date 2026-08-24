from __future__ import annotations

from fastapi.testclient import TestClient

from stock_sentiment.api.main import app
from stock_sentiment.data.sample_data import generate_sample_prices

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()


def test_sentiment_analyze_endpoint():
    response = client.post(
        "/sentiment/analyze",
        json={"texts": ["stocks surge on strong earnings", "shares crash amid scandal"]},
    )
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 2
    assert results[0]["sentiment"] == "Positive"
    assert results[1]["sentiment"] == "Negative"


def test_sentiment_analyze_rejects_empty_list():
    response = client.post("/sentiment/analyze", json={"texts": []})
    assert response.status_code == 422


def test_sentiment_analyze_rejects_unknown_backend():
    response = client.post("/sentiment/analyze", json={"texts": ["hi"], "backend": "bogus"})
    assert response.status_code == 422


def test_indicators_compute_endpoint():
    prices = generate_sample_prices("AAPL", n_days=40)
    bars = [
        {
            "date": row.date.strftime("%Y-%m-%d"),
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
        }
        for row in prices.itertuples()
    ]
    response = client.post("/indicators/compute", json={"ticker": "AAPL", "bars": bars})
    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert len(body["rows"]) == len(bars)
    assert "rsi" in body["rows"][-1]


def test_correlation_compute_endpoint():
    daily_sentiment = [{"date": f"2024-01-{d:02d}", "mean_sentiment": d / 10} for d in range(1, 11)]
    daily_returns = [{"date": f"2024-01-{d:02d}", "daily_return": d / 10} for d in range(1, 11)]

    response = client.post(
        "/correlation/compute",
        json={"ticker": "AAPL", "daily_sentiment": daily_sentiment, "daily_returns": daily_returns},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["pearson_r"] == 1.0
    assert body["n_observations"] == 10


def test_insights_generate_falls_back_to_template_without_api_key():
    response = client.post(
        "/insights/generate",
        json={"metrics": {"tickers": {"AAPL": {"sentiment_distribution": {"Positive": 5}}}}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "template"
    assert "AAPL" in body["summary"]


def test_reports_tickers_empty_when_no_data():
    response = client.get("/reports/tickers")
    assert response.status_code == 200
    assert response.json() == {"tickers": []}


def test_reports_prices_404_for_unknown_ticker():
    response = client.get("/reports/ZZZZ/prices")
    assert response.status_code == 404


def test_rate_limit_headers_do_not_block_normal_usage():
    for _ in range(5):
        response = client.get("/health")
        assert response.status_code == 200
