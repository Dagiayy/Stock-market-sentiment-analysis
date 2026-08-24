from __future__ import annotations

from fastapi import APIRouter

from stock_sentiment.ai.insight_generator import generate_summary
from stock_sentiment.api.models import InsightRequest, InsightResponse

router = APIRouter(prefix="/insights", tags=["insights"])


@router.post("/generate", response_model=InsightResponse)
def generate(request: InsightRequest) -> InsightResponse:
    result = generate_summary(request.metrics)
    return InsightResponse(summary=result.summary, source=result.source, model=result.model)
