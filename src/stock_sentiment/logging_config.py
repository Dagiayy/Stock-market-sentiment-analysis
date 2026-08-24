"""Structured logging setup shared by the CLI, pipeline, and API.

Emits either human-readable text (default, good for local dev) or
single-line JSON (``LOG_JSON=true``, good for log aggregators) so the
same code behaves well on a laptop and in a container.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any

from stock_sentiment.config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        extra = getattr(record, "extra_fields", None)
        if extra:
            payload.update(extra)
        return json.dumps(payload)


_CONFIGURED = False


def configure_logging(level: str | None = None, json_output: bool | None = None) -> None:
    """Idempotently configure the root logger. Safe to call multiple times."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    resolved_level = (level or settings.log_level).upper()
    use_json = settings.log_json if json_output is None else json_output

    handler = logging.StreamHandler(stream=sys.stdout)
    if use_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
        )

    root = logging.getLogger()
    root.setLevel(resolved_level)
    root.handlers = [handler]
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
