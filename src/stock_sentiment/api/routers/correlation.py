from __future__ import annotations

import pandas as pd
from fastapi import APIRouter

from stock_sentiment.analysis.correlation import correlate_sentiment_with_returns
from stock_sentiment.api.models import CorrelationRequest, CorrelationResponse

router = APIRouter(prefix="/correlation", tags=["correlation"])


@router.post("/compute", response_model=CorrelationResponse)
def compute(request: CorrelationRequest) -> CorrelationResponse:
    sentiment_df = pd.DataFrame(request.daily_sentiment)
    returns_df = pd.DataFrame(request.daily_returns)

    result = correlate_sentiment_with_returns(
        sentiment_df, returns_df, ticker=request.ticker, lag_days=request.lag_days
    )
    return CorrelationResponse(**result.as_dict())
