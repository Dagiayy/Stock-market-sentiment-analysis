from __future__ import annotations

import pandas as pd

from stock_sentiment.data.storage import AnalyticsStore


def test_write_and_read_table_roundtrip(tmp_path):
    store = AnalyticsStore(db_path=tmp_path / "test.duckdb")
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})

    store.write_table("t1", df)
    result = store.read_table("t1")

    pd.testing.assert_frame_equal(result.reset_index(drop=True), df.reset_index(drop=True))


def test_read_missing_table_returns_empty_dataframe(tmp_path):
    store = AnalyticsStore(db_path=tmp_path / "test.duckdb")
    result = store.read_table("does_not_exist")
    assert result.empty


def test_list_tables(tmp_path):
    store = AnalyticsStore(db_path=tmp_path / "test.duckdb")
    store.write_table("t1", pd.DataFrame({"a": [1]}))
    store.write_table("t2", pd.DataFrame({"a": [1]}))
    assert set(store.list_tables()) == {"t1", "t2"}


def test_write_table_replace_overwrites(tmp_path):
    store = AnalyticsStore(db_path=tmp_path / "test.duckdb")
    store.write_table("t1", pd.DataFrame({"a": [1, 2]}))
    store.write_table("t1", pd.DataFrame({"a": [9]}))
    result = store.read_table("t1")
    assert len(result) == 1
    assert result["a"].iloc[0] == 9
