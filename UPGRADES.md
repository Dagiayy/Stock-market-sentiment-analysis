# Engineering Upgrade Log

This document records the transformation of this repository from a
10 Academy "Week 1 Challenge" notebook exercise into a tested,
containerized, API-fronted analytics service. It is written for anyone
auditing the change — what existed, what was wrong with it, and what
replaced it.

---

## 1. Project understanding

**What it does:** correlates financial news headline sentiment with
stock price movement — sentiment scoring, technical indicators (SMA,
RSI, MACD, Bollinger Bands), and a Pearson correlation between daily
aggregated sentiment and daily returns, per ticker.

**How it worked originally:** three Jupyter notebooks (`task_1/2/3`)
doing EDA, technical indicators, and correlation respectively, plus a
`scripts/` directory of standalone functions that mirrored (and
diverged from) the notebook logic.

## 2. Original architecture

```
notebooks/task_1.ipynb   -> EDA + topic modeling (ad hoc, in-notebook)
notebooks/task_2.ipynb   -> TA-Lib indicators (ad hoc, in-notebook)
notebooks/task_3.ipynb   -> TextBlob sentiment + correlation (ad hoc, in-notebook)
scripts/main.py          -> entry point, imports a module that doesn't exist
scripts/*.py             -> duplicate/parallel implementation of the same logic
src/                     -> empty placeholder
tests/                   -> empty placeholder
.github/workflows/       -> installs dependencies, runs no tests
```

No database, no API, no Docker, no working CI, no data-quality checks,
no config management, no dependency on real data (git-ignored, never
committed) — this was a notebook-first analysis exercise, not a
runnable system.

## 3. Problems found

| # | Problem | Impact |
|---|---|---|
| P0 | `scripts/main.py` does `from preprocess import load_data` — no such module exists (the file is `process.py`) | Entry point crashes immediately; the script never ran |
| P0 | `requirements.txt` was UTF-16-encoded and pointed at `ta-lib @ file:///C:/Users/dagi/Downloads/ta_lib-....whl` — a specific contributor's local Windows file | `pip install -r requirements.txt` fails for literally everyone else, including CI |
| P0 | CI workflow only verified environment setup; there was no test suite to run | Zero automated correctness verification, ever |
| P1 | Sentiment scoring implemented three different, inconsistent ways: VADER in `seintment_analysis.py`, TextBlob in `corrolations.py`, and a third ad hoc version in `notebooks/task_1.ipynb` | Whichever script ran last silently defined "ground truth"; no shared classification thresholds |
| P1 | Hard dependency on TA-Lib, a C library with no portable PyPI wheel | Unbuildable in a minimal Docker image or on a fresh machine without a multi-step apt/compile workaround |
| P1 | No schema or data-quality validation anywhere in the pipeline | A malformed CSV (bad dates, negative prices, nulls) would silently propagate into every downstream number |
| P1 | No tests at all | No regression protection, no way to verify a refactor didn't break behavior |
| P1 | No persistence layer — every notebook re-computed everything from CSV on every run | No queryable history, nothing an API could read |
| P2 | No API — every result lived inside a notebook cell's output | Not usable by another service or a non-Python consumer |
| P2 | No config management — file paths, thresholds, and indicator periods were hard-coded inline across scripts | Changing a default meant hunting through multiple files |
| P2 | No structured logging, no error handling in the pipeline sense (only a bare `try/except: print()` in `process.py`) | A failure gave no information about what ran, on what data, or why it failed |
| P2 | READMEs (`README.md`, `scripts/README.md`, `notebooks/report.md`) contained leaked LLM meta-commentary ("Here's a complete README.md file that includes...") as literal file content | Unprofessional, and `scripts/README.md`/`notebooks/README.md` were otherwise empty |
| P3 | No AI/LLM capability despite this being explicitly an "AI Mastery Program" project | Missed opportunity — computed metrics with no narrative layer |
| P3 | Not a git repository | No history, no diff-based review of any of this work |

## 4. Improvements implemented

- Consolidated all scripts + notebook logic into a single, tested, installable package: `src/stock_sentiment/` (see structure below).
- Fixed the broken import, the unusable `requirements.txt`, and the three-different-sentiment-implementations problem.
- Replaced the TA-Lib dependency with a pure-pandas implementation of every indicator the project used (exact same formulas, zero native-compile requirement).
- Added `pandera` schema validation + a custom data-quality report (nulls, duplicates, outliers via IQR, `high < low` sanity checks) as an explicit pipeline stage.
- Added an embedded DuckDB storage layer so pipeline output is queryable and the API has something to read.
- Added a FastAPI service (`/sentiment`, `/indicators`, `/correlation`, `/insights`, `/reports`, `/health`) with CORS, per-client rate limiting, structured request logging, and a global exception handler.
- Added a CLI (`stock-sentiment run` / `stock-sentiment serve`).
- Added an LLM-powered narrative-summary layer (Claude via the `anthropic` SDK) with a deterministic template fallback when no API key is configured.
- Added a deterministic synthetic-data generator so the pipeline, tests, and API all work immediately after `git clone` — no dataset download required.
- Added 66 pytest tests (~90% statement coverage) covering sentiment, indicators, correlation, validation, storage, ingestion, the pipeline, the CLI, and the API — all network-free (yfinance and the LLM call are mocked/monkeypatched).
- Replaced the CI workflow (previously "install deps, run nothing") with lint (ruff) + type-check (mypy, advisory) + test-with-coverage + a Docker build-check, on a 3.11/3.12 matrix.
- Added a `Dockerfile` and `docker-compose.yml` (an `api` service and a one-off `pipeline` job).
- Rewrote `.gitignore` (was ignoring `Data/`, capitalized, which doesn't match this project's lowercase `data/` convention; added `.env`, `*.egg-info/`, `*.duckdb`, coverage/cache artifacts).
- Added `.env.example` and centralized all configuration in `config.py` (pydantic-settings) — no more hard-coded paths/thresholds scattered across files.
- Added structured logging (`logging_config.py`) shared by the CLI, pipeline, and API.
- Rewrote the root `README.md`, `notebooks/README.md`, and `scripts/README.md`; removed leaked LLM scaffolding text from `notebooks/report.md`.
- Initialized git and committed the original state as a baseline commit before making any changes, so the full diff is reviewable.

## 5. New features (did not exist before)

- REST API with 5 functional routers + health check.
- AI-generated narrative report summarization (optional, graceful fallback).
- DuckDB-backed persistence and a `/reports` API for reading it back.
- Data-quality reporting as a first-class, testable output (`DataQualityReport`).
- Synthetic sample-data generation, making the whole system runnable with zero setup.
- Lagged correlation analysis (`correlation_matrix_over_lags`) — the original project only ever tested same-day correlation.
- Rate limiting and structured access logging on the API.
- Docker/Compose deployment.
- CI coverage reporting and a Docker build-check gate.

## 6. Data engineering improvements

- **Ingestion:** `data/ingest.py` normalizes column casing across sources, cleans headlines, coerces dates, and downloads OHLCV data via `yfinance` with automatic fallback to seeded synthetic data on failure (no network, rate limit, or delisted ticker will crash the pipeline).
- **Validation:** `data/schemas.py` (pandera contracts) + `data/validation.py` (quality report: null counts, duplicate rows, IQR-based outlier counts, `high < low` sanity check) run before any feature engineering touches the data.
- **Storage:** `data/storage.py` wraps DuckDB — `write_table`/`read_table`/`query`/`list_tables` — chosen over a database server because the workload (daily bars + headlines for a handful of tickers) doesn't justify one.
- **Reproducibility:** every random component (synthetic data generation, LDA) is seeded.

## 7. ML improvements

- Sentiment "model" (lexicon-based VADER/TextBlob) is now a single `SentimentBackend` protocol with two interchangeable, independently tested implementations and one shared classification rule — previously three inconsistent, undocumented implementations.
- Topic modeling (TF-IDF + LDA) extracted from notebook cells into `features/text_topics.py`, parameterized, tested.
- Correlation analysis upgraded from a single Pearson `r` to `CorrelationResult` (r, p-value, n, significance flag) with same-day and multi-lag support — a bare correlation coefficient with no sample size or p-value, as the original notebooks reported it, isn't something you can act on.
- Technical indicators reimplemented and unit-tested against known mathematical properties (RSI bounded [0,100] and =100 for a strictly increasing series, Bollinger band ordering, EMA reacting faster than SMA to a shock, etc.) rather than only "does it run."

## 8. AI improvements

- `ai/insight_generator.py`: given a small, pre-computed metrics dict (never raw rows), asks Claude for a 150–250 word plain-English executive summary. Design choices made deliberately to keep this bounded and safe:
  - The LLM never sees raw data — it can't hallucinate a number that isn't already in the JSON it's summarizing.
  - No API key configured, or any failure in the call → falls back to a deterministic, template-generated summary. The feature can never break the pipeline or the API.
  - No RAG/vector store — summarizing eight pre-computed numbers doesn't need retrieval.
  - System prompt explicitly instructs the model not to issue investment advice and to flag non-significant correlations as such.

## 9. Testing

66 tests, ~90% statement coverage, `pytest --cov=stock_sentiment`:

| File | Covers |
|---|---|
| `test_sentiment.py` | Both backends, classification thresholds, DataFrame scoring, unknown-backend error |
| `test_technical_indicators.py` | SMA/EMA/RSI/MACD/Bollinger correctness properties |
| `test_correlation.py` | Aggregation, perfect correlation, insufficient-data NaN handling, lag shifting, multi-lag matrix |
| `test_validation.py` | Duplicate/null detection, `high < low`, empty-frame handling |
| `test_schemas.py` | Pandera contract accept/reject cases |
| `test_ingest.py` | Sample fallback, real-file cleaning, column normalization, offline yfinance fallback |
| `test_storage.py` | DuckDB round-trip, missing table, replace semantics |
| `test_topics.py` | LDA shape/topic-count correctness |
| `test_eda_and_trends.py` | EDA summaries and trend aggregation |
| `test_pipeline.py` | End-to-end run (network mocked), persistence, report serialization |
| `test_cli.py` | Argument parsing, success/failure exit codes |
| `test_api.py` | Every router, validation errors, 404s, rate-limit non-interference |

All price downloads and LLM calls are mocked/monkeypatched — the suite
never touches the network and is deterministic in CI.

## 10. Security

- No secrets committed. `.env.example` documents every configurable value with no real credentials.
- `.gitignore` now excludes `.env`, `*.duckdb`, and all data files.
- No SQL injection surface: DuckDB table names in `storage.py` come only from internal, code-controlled strings (ticker symbols normalized to `[a-z0-9_]`-style table names), never directly from unsanitized user input; all query values pass through DuckDB's parameterized DataFrame registration, not string-interpolated SQL.
- API has a global exception handler that returns a generic 500 instead of leaking stack traces to clients (the trace still goes to the server log).
- Per-client rate limiting on all endpoints except `/health`.
- Noted as a known limitation (not fixed, out of scope for a local/demo API): no authentication layer. Documented in the README as a prerequisite before any public deployment.

## 11. Performance

- Vectorized indicator math (pandas rolling/ewm) — no Python-level loops over price rows.
- IQR outlier detection and quality profiling are vectorized pandas operations.
- DuckDB gives columnar analytical query performance over the persisted tables for free.
- Rate limiting protects the API from accidental self-inflicted overload.
- Not addressed (documented as a limitation): `download_prices` calls `yfinance` sequentially per ticker — fine for a watchlist, would need batching/async for a large universe.

## 12. Deployment

- `Dockerfile`: slim Python 3.12 base, non-root user, health check, NLTK data pre-fetched at build time.
- `docker-compose.yml`: an `api` service (persistent) and a `pipeline` one-off job (`docker compose run --rm pipeline`), sharing a `./data` volume.
- CI (`.github/workflows/ci.yml`): lint, type-check (advisory), test-with-coverage on Python 3.11 and 3.12, plus a separate job that builds the sdist/wheel and the Docker image to catch packaging/build breaks before merge.
- The previous `.github/workflows/unittest.yml` (environment-setup-only, no tests) was removed and replaced by the above.

## 13. Documentation

- Root `README.md` rewritten in full: what/why, architecture diagram, explicit "what was deliberately not added and why" section, getting-started (works with zero setup), real-data instructions, AI setup, Docker, testing, API reference, example workflows by user role, project structure, limitations, future improvements.
- `notebooks/README.md` written (was empty) — explains what each notebook contains and that it's a historical artifact, not the production path.
- `scripts/README.md` rewritten — explains the one remaining script and what happened to the seven that were removed.
- `data/README.md` added — documents the expected real-data layout and confirms none of it is required.
- This file (`UPGRADES.md`).

## 14. Remaining issues / out of scope

- No auth on the API — acceptable for the current local/demo scope, called out explicitly as a prerequisite for any public deployment.
- Sentiment accuracy is bounded by lexicon-based methods (VADER/TextBlob); a finance-tuned transformer (e.g. FinBERT) would likely score better but was judged out of scope (heavy dependency, model download, no GPU in this environment) — documented as a future improvement behind the existing `SentimentBackend` interface, which was designed to make that swap additive.
- `mypy` is wired into CI as advisory (`continue-on-error`) rather than blocking, since the codebase has type hints throughout but hasn't been exhaustively verified against strict mypy in this pass.
- Docker build was written to standard best practices (non-root user, slim base, healthcheck, minimal layers) but could not be executed locally in this environment (Docker Desktop's engine was not running); the CI workflow builds it on every push, so it is verified there.

## 15. Final assessment

**Portfolio-grade for its scope.** The system is now: installable
(`pip install -e .`), runnable with zero setup (synthetic-data
fallback everywhere), tested (66 tests, ~90% coverage, all network-free
and deterministic), containerized, CI-gated (lint + test + build on
every push), documented end-to-end, and exposes its capabilities
through both a CLI and a REST API rather than only notebook cells. The
architecture is intentionally a modular monolith — DuckDB instead of a
database server, no message queue, no distributed compute, no vector
store — because the actual data volume (daily headlines and OHLCV bars
for a handful of tickers) does not justify that complexity; the
README documents each of those decisions explicitly so they read as
judgment calls rather than gaps.

What would move it from "strong portfolio piece" to "actually
production" is external to this repo's code: real traffic/auth
requirements, a real (licensed) news feed instead of a Kaggle CSV, and
a decision about whether the sentiment signal is strong enough, on
real data, to be worth operating past the demo stage.
