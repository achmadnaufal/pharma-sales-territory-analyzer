"""Analytics functions for sales, coverage, and rep performance."""

from __future__ import annotations

import pandas as pd


def territory_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate by territory: revenue, prescriptions, visits, HCPs."""
    grouped = (
        df.groupby(["territory", "city", "province"], as_index=False)
        .agg(
            revenue_idr=("revenue_idr", "sum"),
            prescriptions=("prescriptions", "sum"),
            visits=("visits", "sum"),
            target_visits=("target_visits", "sum"),
            hcp_count=("hcp_id", "nunique"),
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
        )
        .assign(
            coverage_ratio=lambda d: (
                d["visits"] / d["target_visits"].where(d["target_visits"] > 0, 1)
            ).round(3),
        )
    )
    return grouped.copy()


def hcp_coverage_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return a wide matrix of visits per HCP per product."""
    pivot = pd.pivot_table(
        df,
        index=["hcp_id", "hcp_name", "hcp_specialty"],
        columns="product",
        values="visits",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()
    pivot.columns.name = None
    return pivot.copy()


def rep_scorecard(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-rep KPIs with ranking."""
    base = (
        df.groupby(["rep_id", "rep_name", "territory"], as_index=False)
        .agg(
            revenue_idr=("revenue_idr", "sum"),
            prescriptions=("prescriptions", "sum"),
            visits=("visits", "sum"),
            target_visits=("target_visits", "sum"),
            hcp_reached=("hcp_id", "nunique"),
        )
        .assign(
            coverage_pct=lambda d: (
                d["visits"] / d["target_visits"].where(d["target_visits"] > 0, 1) * 100.0
            ).round(1),
            avg_script_value=lambda d: (
                d["revenue_idr"] / d["prescriptions"].where(d["prescriptions"] > 0, 1)
            ).round(0),
        )
    )
    ranked = base.assign(
        rank_revenue=base["revenue_idr"].rank(ascending=False, method="min").astype(int),
        rank_coverage=base["coverage_pct"].rank(ascending=False, method="min").astype(int),
    ).sort_values("revenue_idr", ascending=False, ignore_index=True)
    return ranked.copy()


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate prescriptions and revenue by month."""
    if df.empty:
        return pd.DataFrame(columns=["month", "prescriptions", "revenue_idr"])
    monthly = (
        df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
        .groupby("month", as_index=False)
        .agg(
            prescriptions=("prescriptions", "sum"),
            revenue_idr=("revenue_idr", "sum"),
        )
        .sort_values("month", ignore_index=True)
    )
    return monthly.copy()


def product_mix(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue breakdown by product."""
    mix = (
        df.groupby("product", as_index=False)
        .agg(
            revenue_idr=("revenue_idr", "sum"),
            prescriptions=("prescriptions", "sum"),
        )
        .assign(
            share_pct=lambda d: (d["revenue_idr"] / d["revenue_idr"].sum() * 100).round(2),
        )
        .sort_values("revenue_idr", ascending=False, ignore_index=True)
    )
    return mix.copy()


def under_covered_hcps(df: pd.DataFrame, min_visits: int = 7) -> pd.DataFrame:
    """Identify HCPs with total visits below threshold."""
    if min_visits < 0:
        raise ValueError("min_visits must be non-negative")
    totals = (
        df.groupby(["hcp_id", "hcp_name", "hcp_specialty", "territory"], as_index=False)
        .agg(total_visits=("visits", "sum"))
    )
    return totals.loc[totals["total_visits"] < min_visits].copy()
