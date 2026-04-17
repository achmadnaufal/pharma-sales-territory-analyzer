"""Shared pytest fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SAMPLE_CSV = ROOT / "demo" / "sample_data.csv"


@pytest.fixture(scope="session")
def csv_path() -> Path:
    """Path to the bundled sample CSV."""
    return SAMPLE_CSV


@pytest.fixture(scope="session")
def sample_df() -> pd.DataFrame:
    """Loaded sample DataFrame."""
    from src.data_loader import load_sales_data
    return load_sales_data(SAMPLE_CSV)


@pytest.fixture()
def tiny_df() -> pd.DataFrame:
    """Small hand-crafted DataFrame for unit tests."""
    return pd.DataFrame({
        "date": pd.to_datetime([
            "2026-01-01", "2026-02-01", "2026-03-01",
            "2026-01-01", "2026-02-01", "2026-03-01",
        ]),
        "rep_id": ["R1", "R1", "R1", "R2", "R2", "R2"],
        "rep_name": ["Alice", "Alice", "Alice", "Bob", "Bob", "Bob"],
        "territory": ["T1", "T1", "T1", "T2", "T2", "T2"],
        "city": ["Jakarta"] * 3 + ["Surabaya"] * 3,
        "province": ["DKI"] * 3 + ["Jatim"] * 3,
        "latitude": [-6.2, -6.2, -6.2, -7.2, -7.2, -7.2],
        "longitude": [106.8, 106.8, 106.8, 112.7, 112.7, 112.7],
        "hcp_id": ["H1", "H2", "H3", "H4", "H5", "H6"],
        "hcp_name": ["Dr A", "Dr B", "Dr C", "Dr D", "Dr E", "Dr F"],
        "hcp_specialty": ["Cardio", "Neuro", "Cardio", "Pedi", "Onco", "Derma"],
        "product": ["X", "Y", "X", "Y", "X", "Y"],
        "prescriptions": [10, 20, 30, 15, 25, 35],
        "revenue_idr": [1000.0, 2000.0, 3000.0, 1500.0, 2500.0, 3500.0],
        "visits": [2, 3, 4, 3, 4, 5],
        "target_visits": [5, 5, 5, 5, 5, 5],
    })
