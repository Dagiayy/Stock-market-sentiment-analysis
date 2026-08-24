from __future__ import annotations

from fastapi import APIRouter, HTTPException

from stock_sentiment.api.models import SentimentItem, SentimentRequest, SentimentResponse
from stock_sentiment.features.sentiment import classify, get_backend

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


@router.post("/analyze", response_model=SentimentResponse)
def analyze(request: SentimentRequest) -> SentimentResponse:
    try:
        backend = get_backend(request.backend)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    results = []
    for text in request.texts:
        score = backend.score(text)
        results.append(SentimentItem(text=text, sentiment_score=score, sentiment=classify(score)))
    return SentimentResponse(results=results)
