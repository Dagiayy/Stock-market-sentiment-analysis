FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml requirements.txt ./
COPY src ./src
COPY scripts ./scripts

RUN pip install --upgrade pip && \
    pip install -e . && \
    python scripts/download_nltk_data.py

COPY README.md ./

RUN useradd --create-home --uid 1000 appuser && \
    mkdir -p /app/data/processed && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

ENTRYPOINT ["stock-sentiment"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8000"]
