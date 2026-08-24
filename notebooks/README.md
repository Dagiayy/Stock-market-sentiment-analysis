# notebooks/

Exploratory notebooks from the original analysis. They are kept as a
historical record of the initial research and are **not** part of the
production pipeline — the same logic now lives, tested, in
`src/stock_sentiment/` (see the root README).

| Notebook | Contents |
|---|---|
| `task_1.ipynb` | Exploratory data analysis of the news headline dataset: descriptive stats, publisher activity, publication-time distribution, and an initial LDA topic model. |
| `task_2.ipynb` | Technical-indicator analysis (SMA/RSI/MACD) over per-ticker OHLCV price data. |
| `task_3.ipynb` | Correlation analysis between daily aggregated news sentiment and daily stock returns. |
| `eda(financial_analysis).ipynb` | Empty placeholder from the original project; not used. |
| `report.md` | Narrative write-up of the original findings. |

To reproduce this analysis with real data, place the Kaggle
`raw_analyst_ratings.csv` file at `data/raw_analyst_ratings.csv` and
per-ticker OHLCV CSVs under `data/yfinance_data/`, then either open a
notebook here or run `stock-sentiment run` to get the same analysis
via the production pipeline (which additionally validates the data,
persists results to DuckDB, and can generate an AI narrative summary).
