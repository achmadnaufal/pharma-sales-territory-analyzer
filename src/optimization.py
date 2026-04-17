"""Territory optimization via KMeans clustering of HCP geography."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


def cluster_territories(
    df: pd.DataFrame,
    n_clusters: int = 4,
    random_state: int = 42,
) -> pd.DataFrame:
    """Group HCPs geographically and return cluster assignments.

    Returns a DataFrame with hcp_id, territory, latitude, longitude, cluster.
    """
    if n_clusters < 1:
        raise ValueError("n_clusters must be >= 1")

    unique_hcps = (
        df.dropna(subset=["latitude", "longitude"])
        .drop_duplicates(subset=["hcp_id"])
        .loc[:, ["hcp_id", "hcp_name", "territory", "city", "latitude", "longitude"]]
        .reset_index(drop=True)
    )
    if unique_hcps.empty:
        return unique_hcps.assign(cluster=pd.Series(dtype=int))

    k = min(n_clusters, len(unique_hcps))
    coords = unique_hcps[["latitude", "longitude"]].to_numpy(dtype=float)
    model = KMeans(n_clusters=k, random_state=random_state, n_init=10).fit(coords)
    return unique_hcps.assign(cluster=model.labels_.astype(int)).copy()


def cluster_centroids(clusters: pd.DataFrame) -> pd.DataFrame:
    """Compute centroid lat/lon per cluster."""
    if clusters.empty:
        return pd.DataFrame(columns=["cluster", "latitude", "longitude", "hcp_count"])
    centroids = (
        clusters.groupby("cluster", as_index=False)
        .agg(
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            hcp_count=("hcp_id", "nunique"),
        )
    )
    return centroids.copy()


def workload_balance_score(scorecard: pd.DataFrame) -> float:
    """Return 0-1 score where 1 means perfectly balanced rep workload.

    Based on the coefficient of variation of revenue across reps (inverted).
    """
    if scorecard.empty or scorecard["revenue_idr"].sum() == 0:
        return 0.0
    values = scorecard["revenue_idr"].to_numpy(dtype=float)
    mean = float(values.mean())
    std = float(values.std(ddof=0))
    if mean == 0:
        return 0.0
    cv = std / mean
    return float(np.clip(1.0 - cv, 0.0, 1.0))
