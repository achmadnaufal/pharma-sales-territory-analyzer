"""Tests for src.optimization."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analytics import rep_scorecard
from src.optimization import cluster_centroids, cluster_territories, workload_balance_score


def test_cluster_territories_shape(sample_df):
    result = cluster_territories(sample_df, n_clusters=3)
    assert "cluster" in result.columns
    assert result["cluster"].nunique() == 3


def test_cluster_territories_caps_k_at_hcp_count(tiny_df):
    # tiny_df has 6 HCPs but only 2 unique geo points → KMeans collapses to 2
    result = cluster_territories(tiny_df, n_clusters=10)
    assert result["cluster"].nunique() <= 6
    assert len(result) == 6


def test_cluster_territories_invalid():
    df = pd.DataFrame({"hcp_id": [], "latitude": [], "longitude": []})
    with pytest.raises(ValueError):
        cluster_territories(df, n_clusters=0)


def test_cluster_territories_empty():
    df = pd.DataFrame({
        "hcp_id": ["H1"],
        "hcp_name": ["Dr A"],
        "territory": ["T"],
        "city": ["Jakarta"],
        "latitude": [None],
        "longitude": [None],
    })
    result = cluster_territories(df, n_clusters=2)
    assert result.empty


def test_cluster_territories_deterministic(sample_df):
    r1 = cluster_territories(sample_df, n_clusters=3, random_state=7)
    r2 = cluster_territories(sample_df, n_clusters=3, random_state=7)
    pd.testing.assert_series_equal(r1["cluster"], r2["cluster"])


def test_cluster_centroids_columns(sample_df):
    clusters = cluster_territories(sample_df, n_clusters=2)
    centroids = cluster_centroids(clusters)
    assert set(["cluster", "latitude", "longitude", "hcp_count"]).issubset(centroids.columns)
    assert len(centroids) == 2


def test_cluster_centroids_empty():
    empty = pd.DataFrame(columns=["cluster", "hcp_id", "latitude", "longitude"])
    result = cluster_centroids(empty)
    assert result.empty


def test_workload_balance_perfect():
    scorecard = pd.DataFrame({"revenue_idr": [100.0, 100.0, 100.0]})
    assert workload_balance_score(scorecard) == pytest.approx(1.0)


def test_workload_balance_imbalanced():
    scorecard = pd.DataFrame({"revenue_idr": [10.0, 1000.0]})
    score = workload_balance_score(scorecard)
    assert 0.0 <= score < 1.0


def test_workload_balance_empty():
    assert workload_balance_score(pd.DataFrame({"revenue_idr": []})) == 0.0


def test_workload_balance_from_real_df(sample_df):
    card = rep_scorecard(sample_df)
    score = workload_balance_score(card)
    assert 0.0 <= score <= 1.0
