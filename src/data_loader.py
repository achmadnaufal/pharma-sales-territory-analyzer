"""Data loading and preprocessing utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Final

import pandas as pd

REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "date",
    "rep_id",
    "rep_name",
    "territory",
    "city",
    "province",
    "latitude",
    "longitude",
    "hcp_id",
    "hcp_name",
    "hcp_specialty",
    "product",
    "prescriptions",
    "revenue_idr",
    "visits",
    "target_visits",
)


def load_sales_data(csv_path: str | Path) -> pd.DataFrame:
    """Load the pharma sales CSV and enforce schema.

    Returns an immutable-style DataFrame copy with parsed dates.
    Raises ValueError when required columns are missing.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")

    raw = pd.read_csv(path)
    missing = set(REQUIRED_COLUMNS) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    enriched = raw.assign(
        date=pd.to_datetime(raw["date"], errors="coerce"),
        prescriptions=pd.to_numeric(raw["prescriptions"], errors="coerce").fillna(0).astype(int),
        revenue_idr=pd.to_numeric(raw["revenue_idr"], errors="coerce").fillna(0.0).astype(float),
        visits=pd.to_numeric(raw["visits"], errors="coerce").fillna(0).astype(int),
        target_visits=pd.to_numeric(raw["target_visits"], errors="coerce").fillna(0).astype(int),
        latitude=pd.to_numeric(raw["latitude"], errors="coerce"),
        longitude=pd.to_numeric(raw["longitude"], errors="coerce"),
    )
    if enriched["date"].isna().any():
        raise ValueError("Column 'date' contains unparsable values.")
    return enriched.copy()


def filter_by_territory(df: pd.DataFrame, territories: list[str]) -> pd.DataFrame:
    """Return a new DataFrame filtered to the given territories."""
    if not territories:
        return df.copy()
    return df.loc[df["territory"].isin(territories)].copy()


def filter_by_date_range(
    df: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.DataFrame:
    """Return a new DataFrame bounded by start/end inclusive."""
    if start > end:
        raise ValueError("start date must be <= end date")
    mask = (df["date"] >= start) & (df["date"] <= end)
    return df.loc[mask].copy()


def unique_values(df: pd.DataFrame, column: str) -> list[str]:
    """Return sorted unique non-null values for a column."""
    if column not in df.columns:
        raise KeyError(f"column not found: {column}")
    return sorted(df[column].dropna().astype(str).unique().tolist())
