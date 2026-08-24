from __future__ import annotations

import pandas as pd
import pytest
from pandera.errors import SchemaError

from stock_sentiment.data.schemas import NewsSchema, PriceSchema


def test_news_schema_accepts_valid_frame():
    df = pd.DataFrame(
        {
            "headline": ["hello world"],
            "date": pd.to_datetime(["2024-01-01"]),
        }
    )
    NewsSchema.validate(df)  # should not raise


def test_news_schema_rejects_empty_headline():
    df = pd.DataFrame({"headline": [""], "date": pd.to_datetime(["2024-01-01"])})
    with pytest.raises(SchemaError):
        NewsSchema.validate(df)


def test_price_schema_rejects_negative_price():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "open": [-1.0],
            "high": [10.0],
            "low": [1.0],
            "close": [5.0],
            "volume": [100.0],
        }
    )
    with pytest.raises(SchemaError):
        PriceSchema.validate(df)


def test_price_schema_accepts_valid_frame():
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "open": [10.0],
            "high": [12.0],
            "low": [9.0],
            "close": [11.0],
            "volume": [1000.0],
        }
    )
    PriceSchema.validate(df)  # should not raise
