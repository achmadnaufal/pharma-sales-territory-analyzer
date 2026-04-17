"""End-to-end smoke tests exercising multiple modules."""

from __future__ import annotations

import importlib

import pandas as pd

from src.analytics import (
    hcp_coverage_matrix,
    monthly_trend,
    product_mix,
    rep_scorecard,
    territory_summary,
)
from src.data_loader import filter_by_territory, load_sales_data
from src.forecasting import forecast_prescriptions
from src.optimization import cluster_territories, workload_balance_score


def test_sample_csv_has_expected_row_count(csv_path):
    raw = pd.read_csv(csv_path)
    assert 20 <= len(raw) <= 40


def test_full_pipeline_runs(sample_df):
    filtered = filter_by_territory(sample_df, ["T-JKT-01", "T-SBY-01"])
    ts = territory_summary(filtered)
    rs = rep_scorecard(filtered)
    hc = hcp_coverage_matrix(filtered)
    mt = monthly_trend(filtered)
    pm = product_mix(filtered)
    clusters = cluster_territories(filtered, n_clusters=2)
    forecast = forecast_prescriptions(filtered, periods=2)

    assert not ts.empty
    assert not rs.empty
    assert not hc.empty
    assert not mt.empty
    assert not pm.empty
    assert not clusters.empty
    assert len(forecast.forecast) == 2


def test_all_reps_have_positive_revenue(sample_df):
    card = rep_scorecard(sample_df)
    assert (card["revenue_idr"] > 0).all()


def test_all_territories_present(sample_df):
    summary = territory_summary(sample_df)
    assert summary["territory"].nunique() == sample_df["territory"].nunique()


def test_forecast_on_real_data(sample_df):
    forecast = forecast_prescriptions(sample_df, periods=4)
    assert len(forecast.history) >= 1
    assert (forecast.forecast["prescriptions"] >= 0).all()


def test_workload_balance_with_real_data(sample_df):
    card = rep_scorecard(sample_df)
    score = workload_balance_score(card)
    assert 0.0 <= score <= 1.0


def test_indonesian_provinces_in_sample(sample_df):
    provinces = set(sample_df["province"].unique())
    # At least a few Indonesian provinces should be present
    assert len(provinces & {
        "DKI Jakarta", "Jawa Timur", "Jawa Barat",
        "Sumatera Utara", "Sulawesi Selatan", "Bali",
    }) >= 4


def test_app_module_importable():
    module = importlib.import_module("app")
    assert hasattr(module, "main")
    assert hasattr(module, "format_idr")


def test_format_idr():
    module = importlib.import_module("app")
    assert module.format_idr(1500000) == "Rp 1,500,000"
