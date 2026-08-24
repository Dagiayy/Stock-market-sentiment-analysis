"""Schema contracts for every dataset that enters the pipeline.

Using pandera lets us fail fast, at the ingestion boundary, with a
precise error message instead of letting a malformed row silently
corrupt a downstream feature or metric.
"""
from __future__ import annotations

import pandera.pandas as pa
from pandera.pandas import Check, Column, DataFrameSchema

NewsSchema = DataFrameSchema(
    {
        "headline": Column(str, Check.str_length(min_value=1), nullable=False),
        "url": Column(str, nullable=True, required=False),
        "publisher": Column(str, nullable=True, required=False),
        "date": Column(pa.DateTime, nullable=False),
        "stock": Column(str, nullable=True, required=False),
    },
    strict=False,
    coerce=False,
)

PriceSchema = DataFrameSchema(
    {
        "date": Column(pa.DateTime, nullable=False),
        "open": Column(float, Check.ge(0), nullable=False),
        "high": Column(float, Check.ge(0), nullable=False),
        "low": Column(float, Check.ge(0), nullable=False),
        "close": Column(float, Check.ge(0), nullable=False),
        "volume": Column(float, Check.ge(0), nullable=True),
    },
    strict=False,
    coerce=True,
)
