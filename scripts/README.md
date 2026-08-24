# scripts/

Small operational one-off scripts. All reusable analysis logic lives in
the installable package at `src/stock_sentiment/` — see the root
[README](../README.md) for the pipeline CLI and API.

| Script | Purpose |
|---|---|
| `download_nltk_data.py` | Pre-fetches the VADER lexicon and TextBlob/NLTK tokenizer data. Run once after `pip install`; also run automatically during the Docker image build. |

> The previous version of this directory (`download.py`, `process.py`,
> `seintment_analysis.py`, `topic_modeling.py`, `trend_analysis.py`,
> `indicators.py`, `corrolations.py`) contained the project's original,
> duplicated implementation (sentiment scoring alone was implemented
> three different ways across three files, and `main.py` imported a
> module — `preprocess`— that didn't exist). That logic has been
> consolidated, fixed, and tested in `src/stock_sentiment/`; see
> `UPGRADES.md` for the full list of changes.
