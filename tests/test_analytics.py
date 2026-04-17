"""Tests for src.analytics."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analytics import (
    hcp_coverage_matrix,
    monthly_trend,
    product_mix,
    rep_scorecard,
    territory_summary,
    under_covered_hcps,
)


def test_territory_summary_columns(tiny_df):
    summary = territory_summary(tiny_df)
    expected = {
        "territory", "city", "province", "revenue_idr",
        "prescriptions", "visits", "target_visits",
        "hcp_count", "latitude", "longitude", "coverage_ratio",
    }
    assert expected.issubset(set(summary.columns))


def test_territory_summary_aggregates(tiny_df):
    summary = territory_summary(tiny_df).set_index("territory")
    assert summary.loc["T1", "revenue_idr"] == 6000.0
    assert summary.loc["T2", "prescriptions"] == 75


def test_territory_summary_coverage_ratio(tiny_df):
    summary = territory_summary(tiny_df).set_index("territory")
    # T1 visits: 2+3+4=9, target: 5+5+5=15 → 0.6
    assert summary.loc["T1", "coverage_ratio"] == pytest.approx(0.6, rel=1e-3)


def test_territory_summary_empty():
    empty = pd.DataFrame({
        "territory": [], "city": [], "province": [],
        "revenue_idr": [], "prescriptions": [], "visits": [],
        "target_visits": [], "hcp_id": [], "latitude": [], "longitude": [],
    })
    result = territory_summary(empty)
    assert result.empty


def test_hcp_coverage_matrix_shape(tiny_df):
    matrix = hcp_coverage_matrix(tiny_df)
    assert "hcp_id" in matrix.columns
    assert "X" in matrix.columns
    assert "Y" in matrix.columns
    assert len(matrix) == 6


def test_hcp_coverage_matrix_values(tiny_df):
    matrix = hcp_coverage_matrix(tiny_df).set_index("hcp_id")
    # H1 → product X, 2 visits
    assert matrix.loc["H1", "X"] == 2
    assert matrix.loc["H1", "Y"] == 0


def test_rep_scorecard_ranks(tiny_df):
    card = rep_scorecard(tiny_df)
    assert set(["rank_revenue", "rank_coverage", "coverage_pct"]).issubset(card.columns)
    assert card["rank_revenue"].min() == 1


def test_rep_scorecard_sorted(tiny_df):
    card = rep_scorecard(tiny_df)
    # sorted descending by revenue
    revenues = card["revenue_idr"].tolist()
    assert revenues == sorted(revenues, reverse=True)


def test_rep_scorecard_avg_script_value(tiny_df):
    card = rep_scorecard(tiny_df).set_index("rep_id")
    # R1: 6000 revenue / 60 scripts = 100
    assert card.loc["R1", "avg_script_value"] == pytest.approx(100.0)


def test_monthly_trend_rows(tiny_df):
    trend = monthly_trend(tiny_df)
    assert len(trend) == 3
    assert list(trend.columns) == ["month", "prescriptions", "revenue_idr"]


def test_monthly_trend_empty_df():
    empty = pd.DataFrame({"date": pd.to_datetime([]), "prescriptions": [], "revenue_idr": []})
    result = monthly_trend(empty)
    assert result.empty


def test_product_mix_share_sums_to_100(tiny_df):
    mix = product_mix(tiny_df)
    assert mix["share_pct"].sum() == pytest.approx(100.0, rel=1e-3)


def test_product_mix_sorted_desc(tiny_df):
    mix = product_mix(tiny_df)
    revenues = mix["revenue_idr"].tolist()
    assert revenues == sorted(revenues, reverse=True)


def test_under_covered_hcps_threshold(tiny_df):
    gaps = under_covered_hcps(tiny_df, min_visits=4)
    # visits per HCP: H1=2, H2=3, H3=4, H4=3, H5=4, H6=5 → below 4: H1, H2, H4
    assert len(gaps) == 3


def test_under_covered_hcps_invalid_threshold(tiny_df):
    with pytest.raises(ValueError):
        under_covered_hcps(tiny_df, min_visits=-1)


def test_analytics_immutability(tiny_df):
    original = tiny_df.copy()
    territory_summary(tiny_df)
    rep_scorecard(tiny_df)
    hcp_coverage_matrix(tiny_df)
    pd.testing.assert_frame_equal(tiny_df, original)
