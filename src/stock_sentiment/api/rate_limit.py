"""Minimal in-memory fixed-window rate limiter.

A single-process API without a shared cache doesn't need Redis for
this — a per-client sliding window kept in a dict is enough to stop
accidental hammering and is trivial to reason about. Swap for a
Redis-backed limiter only if/when the API is horizontally scaled.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from stock_sentiment.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int | None = None):
        super().__init__(app)
        self.limit = requests_per_minute or settings.api_rate_limit_per_minute
        self._hits: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        client_id = request.client.host if request.client else "unknown"
        now = time.monotonic()
        window = self._hits[client_id]

        while window and now - window[0] > 60:
            window.popleft()

        if len(window) >= self.limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again shortly."},
            )

        window.append(now)
        return await call_next(request)
