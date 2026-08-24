"""LLM-generated narrative summaries over already-computed metrics.

Design constraints, deliberately:

* The LLM never sees raw data or touches numbers directly — it is
  handed a small, pre-computed, structured metrics dict and asked to
  narrate it. This bounds token/cost usage, avoids hallucinated
  statistics (the numbers in the prose are the numbers we computed),
  and keeps the LLM call optional and stateless.
* No API key configured, or the call fails -> a deterministic
  template-based summary is returned instead. The feature degrades
  gracefully rather than breaking the pipeline/API.
* Structured input/output only; no chat state, no retrieval, no tool
  use. A RAG/vector-search layer would be overkill for "explain these
  eight numbers in a paragraph."
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from stock_sentiment.config import settings
from stock_sentiment.logging_config import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = (
    "You are a financial data analyst. You will be given pre-computed sentiment, "
    "correlation, and technical-indicator metrics for one or more stock tickers as "
    "JSON. Write a concise (150-250 word) executive summary in plain English. "
    "Only reference numbers present in the JSON — never invent statistics. "
    "Note explicitly when a correlation is not statistically significant. "
    "This is analytical commentary, not investment advice; do not issue buy/sell "
    "recommendations."
)


@dataclass
class InsightResult:
    summary: str
    source: str  # "llm" | "template"
    model: str | None = None


def _template_summary(metrics: dict) -> str:
    lines = ["Automated summary (template — no LLM configured):"]
    for ticker, m in metrics.get("tickers", {}).items():
        sentiment = m.get("sentiment_distribution", {})
        corr = m.get("correlation", {})
        lines.append(
            f"- {ticker}: sentiment counts {sentiment}; "
            f"same-day Pearson r={corr.get('pearson_r')} "
            f"(n={corr.get('n_observations')}, significant={corr.get('is_significant')})."
        )
    return "\n".join(lines)


def generate_summary(metrics: dict) -> InsightResult:
    """Produce a narrative summary of ``metrics``.

    ``metrics`` should be small and pre-aggregated (per-ticker
    sentiment distribution, correlation results, indicator snapshot) —
    never the raw headline/price rows.
    """
    if not settings.ai_insights_enabled or not settings.anthropic_api_key:
        logger.info("AI insights disabled or no API key configured; using template summary")
        return InsightResult(summary=_template_summary(metrics), source="template")

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=settings.ai_max_tokens,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": json.dumps(metrics, default=str)}],
        )
        text = "".join(block.text for block in response.content if block.type == "text").strip()
        if not text:
            raise ValueError("empty response from model")
        return InsightResult(summary=text, source="llm", model=settings.anthropic_model)
    except Exception as exc:  # noqa: BLE001 - any failure degrades to template
        logger.warning("LLM insight generation failed (%s); falling back to template", exc)
        return InsightResult(summary=_template_summary(metrics), source="template")
