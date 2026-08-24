# Stock Market Sentiment Analysis

A production-structured platform that correlates financial news
sentiment with equity price movement: it scores headline sentiment,
computes technical indicators from OHLCV price data, measures the
statistical correlation between the two, and can narrate the results
in plain English via an LLM. Ships as an installable Python package, a
batch pipeline, a REST API, and a Docker image.

Originally a 10 Academy AI Mastery Week 1 challenge notebook exercise;
rebuilt as a small but real analytics service. See
[`UPGRADES.md`](UPGRADES.md) for the full before/after engineering
changelog.

## Why this exists

News sentiment is a commonly cited (and commonly overstated) signal in
quantitative finance. Rather than assert that headline sentiment
predicts returns, this project builds the instrumentation to actually
*test* that claim per ticker — same-day and lagged Pearson correlation
with a sample size and significance flag attached — instead of eyeballing
a plot. That instrumentation (ingest → validate → score → correlate →
report) is reusable for any headline+price dataset, not just the one
included as a demo.

## Architecture

```
                 ┌─────────────────────────────────────────────┐
                 │                  data sources                 │
                 │  news CSV (or synthetic)   yfinance (or synthetic) │
                 └───────────────┬─────────────────┬───────────┘
                                 ▼                 ▼
                         ┌───────────────────────────┐
                         │   data/ ingest + validate    │  pandera schemas,
                         │   (schema + quality checks)  │  null/dup/outlier report
                         └──────────────┬────────────┘
                                        ▼
                         ┌───────────────────────────┐
                         │        features/            │  VADER/TextBlob sentiment,
                         │  sentiment · indicators ·    │  SMA/EMA/RSI/MACD/BBANDS,
                         │  topics                      │  TF-IDF + LDA topics
                         └──────────────┬────────────┘
                                        ▼
                         ┌───────────────────────────┐
                         │        analysis/            │  Pearson correlation (+lag,
                         │  correlation · eda · trends  │  significance), EDA summaries
                         └──────────────┬────────────┘
                                        ▼
                    ┌──────────────────┴──────────────────┐
                    ▼                                      ▼
          ┌───────────────────┐                 ┌───────────────────────┐
          │  DuckDB (data/processed) │           │   ai/ insight_generator │
          │  persisted per-ticker     │           │   (Claude narrative,     │
          │  prices + news tables     │           │   template fallback)     │
          └─────────┬─────────┘                 └───────────┬───────────┘
                    │                                        │
                    └───────────────┬────────────────────────┘
                                    ▼
                         ┌───────────────────────────┐
                         │         api/ (FastAPI)       │  /sentiment /indicators
                         │  + cli.py (`stock-sentiment`) │  /correlation /insights
                         └───────────────────────────┘  /reports  /health
```

**Layers**, each independently testable and swappable:

| Layer | Module | Responsibility |
|---|---|---|
| Ingestion | `data/ingest.py`, `data/sample_data.py` | Load news/price CSVs or download prices via `yfinance`; falls back to a deterministic synthetic dataset so the project runs with zero setup. |
| Validation | `data/schemas.py`, `data/validation.py` | Pandera schema contracts + a data-quality report (nulls, duplicates, outliers, `high < low` sanity checks). |
| Storage | `data/storage.py` | Embedded DuckDB warehouse — no server to operate, SQL-queryable, Parquet-friendly. |
| Features | `features/sentiment.py`, `features/technical_indicators.py`, `features/text_topics.py` | Pluggable sentiment backends (VADER/TextBlob), pure-pandas technical indicators, TF-IDF+LDA topic modeling. |
| Analysis | `analysis/correlation.py`, `analysis/eda.py`, `analysis/trends.py` | Sentiment↔return correlation (with lag + significance), reusable EDA summaries, time-series aggregation. |
| AI | `ai/insight_generator.py` | Turns pre-computed metrics into a narrative summary via Claude; degrades to a deterministic template with no API key. |
| Orchestration | `pipeline.py`, `cli.py` | End-to-end batch run with structured logging and a machine-readable run report. |
| API | `api/` | FastAPI service exposing every layer above as a stateless (or DuckDB-backed) endpoint. |

### Design decisions (and what was deliberately *not* added)

- **DuckDB, not Postgres.** Single-user, file-sized analytical workload — an embedded columnar store gives SQL and speed with zero ops.
- **No vector DB / RAG.** The AI layer explains eight pre-computed numbers, it doesn't need semantic search over a document corpus.
- **TA-Lib dropped.** The original `requirements.txt` pointed at a contributor's local Windows `.whl` file — uninstallable elsewhere, and a multi-step apt/compile dance in CI/Docker. SMA/EMA/RSI/MACD/Bollinger are standard formulas; `features/technical_indicators.py` is a small, exact, dependency-free pandas implementation.
- **No Kafka/Spark/Kubernetes.** Daily news headlines and daily OHLCV bars for a handful of tickers is a "pandas on a laptop" problem, not a distributed-systems problem.

## Getting started

```bash
git clone <this repo>
cd Stock-market-sentiment-analysis-main
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python scripts/download_nltk_data.py                 # one-time: VADER lexicon
```

Nothing else is required — no dataset, no API key, no database to
provision. Run the pipeline immediately:

```bash
stock-sentiment run --tickers AAPL,TSLA
```

This downloads real prices for AAPL/TSLA via `yfinance` (falling back
to a synthetic series if offline), generates a deterministic synthetic
news dataset (real data is used automatically once present — see
`data/README.md`), scores sentiment, fits a topic model, computes
correlation, and prints a JSON run report.

Run the API:

```bash
stock-sentiment serve --reload
# -> http://127.0.0.1:8000/docs (interactive OpenAPI docs)
```

### With real data

Drop the Kaggle `raw_analyst_ratings.csv` at
`data/raw_analyst_ratings.csv` and/or per-ticker OHLCV CSVs under
`data/yfinance_data/` — see `data/README.md` for the exact expected
shape. The pipeline and notebooks use real data automatically whenever
it's present, no config changes needed.

### With AI-generated narrative summaries

```bash
cp .env.example .env
# set ANTHROPIC_API_KEY=sk-ant-...
```

Without a key, `/insights/generate` (and any pipeline report that asks
for a narrative) returns a deterministic template summary instead —
the feature degrades gracefully rather than failing.

### Docker

```bash
docker compose up api          # API on http://localhost:8000
docker compose run --rm pipeline   # one-off batch run, writes to ./data
```

## Running tests

```bash
pytest --cov=stock_sentiment --cov-report=term-missing
ruff check src tests
```

66 tests, ~90% statement coverage, no network access required (price
downloads and LLM calls are mocked/monkeypatched; everything else runs
against seeded synthetic data). CI (`.github/workflows/ci.yml`) runs
this matrix on Python 3.11/3.12 plus a Docker build-check on every
push/PR.

## API reference (selected)

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Liveness check |
| `/sentiment/analyze` | POST | Score a batch of headlines (`{"texts": [...]}`) |
| `/indicators/compute` | POST | Compute SMA/EMA/RSI/MACD/Bollinger over a supplied OHLCV series |
| `/correlation/compute` | POST | Pearson correlation (with optional lag) between supplied sentiment and return series |
| `/insights/generate` | POST | Narrative summary over a pre-computed metrics dict (LLM or template) |
| `/reports/tickers` | GET | Tickers with persisted pipeline output |
| `/reports/{ticker}/prices` | GET | Latest persisted, indicator-enriched price rows for a ticker |

Full interactive docs at `/docs` once the server is running. Requests
are rate-limited (60/min/client by default, configurable) and every
request is structured-logged with method, path, status, and latency.

## Example workflow

1. **Analyst** runs `stock-sentiment run --tickers AAPL,MSFT,NVDA` to refresh sentiment/correlation for a watchlist; the JSON run report goes straight into a notebook or dashboard.
2. **Engineer integrating a trading tool** calls `POST /correlation/compute` directly with their own return series to get a same-day and lagged correlation with significance, without adopting this project's data pipeline.
3. **Portfolio manager** reads `GET /reports/{ticker}/prices` for the latest indicator snapshot, then `POST /insights/generate` with the day's metrics for a plain-English summary to include in a note.

## Project structure

```
.
├── src/stock_sentiment/     # the installable package (see table above)
├── tests/                   # pytest suite (unit + API), synthetic fixtures only
├── scripts/                 # one-off operational scripts (NLTK data fetch)
├── notebooks/                # original exploratory analysis (historical; see notebooks/README.md)
├── data/                     # git-ignored; raw + processed data lives here at runtime
├── Dockerfile, docker-compose.yml
├── pyproject.toml            # package + tool config (ruff, pytest, mypy)
├── requirements.txt          # plain pip mirror of pyproject dependencies
├── .env.example
└── .github/workflows/ci.yml
```

## Limitations

- The bundled correlation numbers are demonstrative — they run against synthetic news paired with real (or synthetic) prices, and headline-level VADER/TextBlob sentiment is a weak signal on its own. Real conclusions require the real Kaggle dataset and a longer history.
- `download_prices` calls `yfinance` synchronously and sequentially per ticker; fine for a watchlist of tickers, would need batching/async for hundreds.
- No auth on the API (single-user/local/demo scope) — add an API-key or OAuth dependency before exposing it publicly.
- Topic modeling (LDA) is unsupervised and unlabeled; topic quality on short headlines is limited compared to a transformer-based approach.

## Possible future improvements

- FinBERT (or another finance-tuned transformer) as an additional sentiment backend for higher accuracy than lexicon-based VADER/TextBlob, behind the same `SentimentBackend` interface.
- Async/batched price downloads for larger ticker universes.
- A scheduled pipeline run (cron/Airflow) instead of on-demand CLI invocation, once there's a real recurring-ingestion need.
- API auth + per-key rate limits if the API moves beyond local/demo use.

## References

- [VADER Sentiment](https://github.com/cjhutto/vaderSentiment)
- [TextBlob Documentation](https://textblob.readthedocs.io/en/dev/)
- [DuckDB](https://duckdb.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [yfinance](https://github.com/ranaroussi/yfinance)

## Author

Dagmawi Ayenew
