"""Read-only access to the latest persisted pipeline output (DuckDB)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from stock_sentiment.data.storage import AnalyticsStore

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/tickers")
def list_tickers() -> dict:
    store = AnalyticsStore()
    tables = store.list_tables()
    tickers = sorted({t.split("_", 1)[1].upper() for t in tables if t.startswith("prices_")})
    return {"tickers": tickers}


@router.get("/{ticker}/prices")
def ticker_prices(ticker: str, limit: int = 90) -> dict:
    store = AnalyticsStore()
    table = f"prices_{ticker.lower()}"
    if table not in store.list_tables():
        raise HTTPException(status_code=404, detail=f"No stored data for ticker '{ticker}'")
    df = store.read_table(table).tail(limit)
    return {"ticker": ticker.upper(), "rows": df.where(df.notna(), None).to_dict(orient="records")}
