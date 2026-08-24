"""FastAPI application factory and entry point."""
from __future__ import annotations

import time
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from stock_sentiment import __version__
from stock_sentiment.api.models import HealthResponse
from stock_sentiment.api.rate_limit import RateLimitMiddleware
from stock_sentiment.api.routers import correlation, indicators, insights, reports, sentiment
from stock_sentiment.config import settings
from stock_sentiment.logging_config import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.api_title,
    version=__version__,
    description=(
        "Sentiment, technical-indicator, correlation, and AI-narrative endpoints "
        "for equity news analytics."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.monotonic()
    response = await call_next(request)
    duration_ms = (time.monotonic() - start) * 1000
    logger.info(
        "%s %s -> %d (%.1fms)", request.method, request.url.path, response.status_code, duration_ms
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(sentiment.router)
app.include_router(indicators.router)
app.include_router(correlation.router)
app.include_router(insights.router)
app.include_router(reports.router)


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=datetime.now(timezone.utc), version=__version__)


@app.get("/", tags=["health"])
def root() -> dict:
    return {"service": settings.api_title, "version": __version__, "docs": "/docs"}
