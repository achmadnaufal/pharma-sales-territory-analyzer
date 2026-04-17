"""Tests for src.forecasting."""

from __future__ import annotations

import pandas as pd
import pytest

from src.forecasting import ForecastResult, forecast_prescriptions


def test_forecast_returns_result(tiny_df):
    result = forecast_prescriptions(tiny_df, periods=3)
    assert isinstance(result, ForecastResult)


def test_forecast_horizon(tiny_df):
    result = forecast_prescriptions(tiny_df, periods=4)
    assert len(result.forecast) == 4


def test_forecast_history_months(tiny_df):
    result = forecast_prescriptions(tiny_df, periods=1)
    assert len(result.history) == 3


def test_forecast_columns(tiny_df):
    result = forecast_prescriptions(tiny_df, periods=2)
    assert {"month", "prescriptions", "lower", "upper"}.issubset(result.forecast.columns)


def test_forecast_lower_leq_upper(tiny_df):
    result = forecast_prescriptions(tiny_df, periods=3)
    assert (result.forecast["lower"] <= result.forecast["upper"]).all()


def test_forecast_slope_positive_for_increasing_trend(tiny_df):
    # tiny_df: monthly totals increase 25 → 45 → 65
    result = forecast_prescriptions(tiny_df, periods=2)
    assert result.slope > 0


def test_forecast_r2_range(tiny_df):
    result = forecast_prescriptions(tiny_df, periods=2)
    assert 0.0 <= result.r2 <= 1.0


def test_forecast_invalid_periods(tiny_df):
    with pytest.raises(ValueError):
        forecast_prescriptions(tiny_df, periods=0)


def test_forecast_empty_df():
    empty = pd.DataFrame({"date": pd.to_datetime([]), "prescriptions": []})
    result = forecast_prescriptions(empty, periods=3)
    assert result.forecast.empty


def test_forecast_single_month():
    one = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-15"]),
        "prescriptions": [50],
    })
    result = forecast_prescriptions(one, periods=2)
    assert len(result.forecast) == 2
    assert result.forecast["prescriptions"].iloc[0] == 50.0


def test_forecast_dataclass_is_frozen(tiny_df):
    result = forecast_prescriptions(tiny_df, periods=1)
    with pytest.raises(Exception):
        result.slope = 99.0  # type: ignore[misc]
