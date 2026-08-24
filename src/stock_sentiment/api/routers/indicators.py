from __future__ import annotations

import pandas as pd
from fastapi import APIRouter

from stock_sentiment.api.models import IndicatorsRequest, IndicatorsResponse
from stock_sentiment.features.technical_indicators import add_all_indicators

router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.post("/compute", response_model=IndicatorsResponse)
def compute(request: IndicatorsRequest) -> IndicatorsResponse:
    df = pd.DataFrame([bar.model_dump() for bar in request.bars]).sort_values("date")
    enriched = add_all_indicators(df)
    rows = enriched.where(enriched.notna(), None).to_dict(orient="records")
    return IndicatorsResponse(ticker=request.ticker, rows=rows)
