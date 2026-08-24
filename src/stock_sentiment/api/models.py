"""Pydantic request/response models for the API — the wire contract."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class SentimentRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=500, description="Headlines to score")
    backend: str | None = Field(None, description="'vader' (default) or 'textblob'")


class SentimentItem(BaseModel):
    text: str
    sentiment_score: float
    sentiment: str


class SentimentResponse(BaseModel):
    results: list[SentimentItem]


class PriceBar(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None


class IndicatorsRequest(BaseModel):
    ticker: str
    bars: list[PriceBar] = Field(..., min_length=2)


class IndicatorsResponse(BaseModel):
    ticker: str
    rows: list[dict]


class CorrelationRequest(BaseModel):
    ticker: str
    daily_sentiment: list[dict] = Field(..., description="[{date, mean_sentiment}, ...]")
    daily_returns: list[dict] = Field(..., description="[{date, daily_return}, ...]")
    lag_days: int = 0


class CorrelationResponse(BaseModel):
    ticker: str
    lag_days: int
    pearson_r: float | None
    p_value: float | None
    n_observations: int
    is_significant: bool


class InsightRequest(BaseModel):
    metrics: dict = Field(..., description="Pre-computed metrics dict (e.g. pipeline report metrics)")


class InsightResponse(BaseModel):
    summary: str
    source: str
    model: str | None = None


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
