"""Prescription trend forecasting using linear regression."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


@dataclass(frozen=True)
class ForecastResult:
    """Immutable forecast result container."""

    history: pd.DataFrame
    forecast: pd.DataFrame
    slope: float
    intercept: float
    r2: float


def forecast_prescriptions(
    df: pd.DataFrame,
    periods: int = 3,
) -> ForecastResult:
    """Fit a linear trend on monthly prescriptions and extrapolate.

    `periods` is the number of months to project beyond the last observation.
    """
    if periods < 1:
        raise ValueError("periods must be >= 1")
    if df.empty:
        empty = pd.DataFrame(columns=["month", "prescriptions"])
        return ForecastResult(
            history=empty,
            forecast=empty.assign(lower=[], upper=[]),
            slope=0.0,
            intercept=0.0,
            r2=0.0,
        )

    monthly = (
        df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
        .groupby("month", as_index=False)
        .agg(prescriptions=("prescriptions", "sum"))
        .sort_values("month", ignore_index=True)
    )

    if len(monthly) < 2:
        last_month = monthly["month"].iloc[0]
        last_value = float(monthly["prescriptions"].iloc[0])
        future_months = pd.date_range(
            start=last_month + pd.offsets.MonthBegin(1),
            periods=periods,
            freq="MS",
        )
        forecast = pd.DataFrame({
            "month": future_months,
            "prescriptions": [last_value] * periods,
            "lower": [last_value * 0.9] * periods,
            "upper": [last_value * 1.1] * periods,
        })
        return ForecastResult(
            history=monthly.copy(),
            forecast=forecast,
            slope=0.0,
            intercept=last_value,
            r2=0.0,
        )

    x = np.arange(len(monthly)).reshape(-1, 1)
    y = monthly["prescriptions"].to_numpy(dtype=float)
    model = LinearRegression().fit(x, y)
    fitted = model.predict(x)
    residuals = y - fitted
    sigma = float(residuals.std(ddof=1)) if len(residuals) > 1 else 0.0

    last_month = monthly["month"].iloc[-1]
    future_months = pd.date_range(
        start=last_month + pd.offsets.MonthBegin(1),
        periods=periods,
        freq="MS",
    )
    future_x = np.arange(len(monthly), len(monthly) + periods).reshape(-1, 1)
    future_y = model.predict(future_x)
    margin = 1.96 * sigma

    forecast = pd.DataFrame({
        "month": future_months,
        "prescriptions": np.round(future_y, 1),
        "lower": np.round(np.maximum(future_y - margin, 0.0), 1),
        "upper": np.round(future_y + margin, 1),
    })
    return ForecastResult(
        history=monthly.copy(),
        forecast=forecast,
        slope=float(model.coef_[0]),
        intercept=float(model.intercept_),
        r2=float(model.score(x, y)),
    )
