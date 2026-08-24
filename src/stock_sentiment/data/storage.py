"""Embedded analytical storage layer (DuckDB).

A single-user analytics tool with a modest (news + daily prices)
dataset does not warrant a database server. DuckDB gives us SQL,
columnar performance, and Parquet interoperability with zero
operational overhead — a file on disk is the whole deployment.
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from stock_sentiment.config import settings
from stock_sentiment.logging_config import get_logger

logger = get_logger(__name__)


class AnalyticsStore:
    """Thin wrapper around a DuckDB file for the pipeline's outputs."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else settings.duckdb_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(str(self.db_path))

    def write_table(self, name: str, df: pd.DataFrame, *, mode: str = "replace") -> None:
        """Persist a DataFrame as a table. ``mode`` is 'replace' or 'append'."""
        with self._connect() as con:
            con.register("df_view", df)
            if mode == "replace":
                con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM df_view")
            else:
                con.execute(f"CREATE TABLE IF NOT EXISTS {name} AS SELECT * FROM df_view LIMIT 0")
                con.execute(f"INSERT INTO {name} SELECT * FROM df_view")
        logger.info("Wrote %d rows to table '%s' (%s)", len(df), name, self.db_path)

    def read_table(self, name: str) -> pd.DataFrame:
        with self._connect() as con:
            try:
                return con.execute(f"SELECT * FROM {name}").fetch_df()
            except duckdb.CatalogException:
                return pd.DataFrame()

    def query(self, sql: str) -> pd.DataFrame:
        with self._connect() as con:
            return con.execute(sql).fetch_df()

    def list_tables(self) -> list[str]:
        with self._connect() as con:
            return [row[0] for row in con.execute("SHOW TABLES").fetchall()]
