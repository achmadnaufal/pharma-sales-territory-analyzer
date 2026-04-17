"""Tests for src.data_loader."""

from __future__ import annotations

import pandas as pd
import pytest

from src.data_loader import (
    REQUIRED_COLUMNS,
    filter_by_date_range,
    filter_by_territory,
    load_sales_data,
    unique_values,
)


def test_load_sales_data_returns_dataframe(csv_path):
    df = load_sales_data(csv_path)
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 20


def test_load_sales_data_has_required_columns(sample_df):
    for col in REQUIRED_COLUMNS:
        assert col in sample_df.columns


def test_load_sales_data_parses_dates(sample_df):
    assert pd.api.types.is_datetime64_any_dtype(sample_df["date"])


def test_load_sales_data_numeric_types(sample_df):
    assert pd.api.types.is_integer_dtype(sample_df["prescriptions"])
    assert pd.api.types.is_integer_dtype(sample_df["visits"])
    assert pd.api.types.is_float_dtype(sample_df["revenue_idr"])


def test_load_sales_data_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_sales_data(tmp_path / "missing.csv")


def test_load_sales_data_invalid_schema(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("foo,bar\n1,2\n")
    with pytest.raises(ValueError, match="Missing required columns"):
        load_sales_data(bad)


def test_filter_by_territory_subset(tiny_df):
    result = filter_by_territory(tiny_df, ["T1"])
    assert set(result["territory"].unique()) == {"T1"}
    assert len(result) == 3


def test_filter_by_territory_empty_returns_all(tiny_df):
    result = filter_by_territory(tiny_df, [])
    assert len(result) == len(tiny_df)


def test_filter_by_territory_returns_copy(tiny_df):
    result = filter_by_territory(tiny_df, ["T1"])
    result.loc[result.index[0], "revenue_idr"] = 99.0
    # mutation on result should not leak into tiny_df
    assert tiny_df["revenue_idr"].iloc[0] == 1000.0


def test_filter_by_date_range_bounds(tiny_df):
    result = filter_by_date_range(
        tiny_df,
        pd.Timestamp("2026-02-01"),
        pd.Timestamp("2026-02-28"),
    )
    assert result["date"].dt.month.unique().tolist() == [2]


def test_filter_by_date_range_invalid():
    empty = pd.DataFrame({"date": pd.to_datetime([])})
    with pytest.raises(ValueError):
        filter_by_date_range(empty, pd.Timestamp("2026-03-01"), pd.Timestamp("2026-01-01"))


def test_unique_values_sorted(tiny_df):
    result = unique_values(tiny_df, "territory")
    assert result == ["T1", "T2"]


def test_unique_values_missing_column(tiny_df):
    with pytest.raises(KeyError):
        unique_values(tiny_df, "does_not_exist")
