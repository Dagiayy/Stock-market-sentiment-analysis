# data/

This directory is git-ignored (datasets don't belong in version
control). It is created empty; the application populates it at
runtime.

Expected layout for real data:

```
data/
├── raw_analyst_ratings.csv     # financial news headlines (Kaggle "raw_analyst_ratings" dataset)
├── yfinance_data/
│   ├── AAPL_historical_data.csv
│   ├── TSLA_historical_data.csv
│   └── ...
└── processed/
    └── analytics.duckdb        # written by the pipeline; safe to delete and regenerate
```

**Nothing here is required.** If `raw_analyst_ratings.csv` is absent,
`stock-sentiment run` generates a deterministic synthetic news dataset;
if a ticker's price CSV is absent, prices are downloaded live via
`yfinance`, falling back to a synthetic price series if that also
fails (e.g. no network). This is why the pipeline and test suite work
immediately after `git clone` with no data setup step.
