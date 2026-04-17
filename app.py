"""Pharma Sales Territory Analyzer — Streamlit dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics import (
    hcp_coverage_matrix,
    monthly_trend,
    product_mix,
    rep_scorecard,
    territory_summary,
    under_covered_hcps,
)
from src.data_loader import filter_by_date_range, filter_by_territory, load_sales_data, unique_values
from src.forecasting import forecast_prescriptions
from src.optimization import cluster_centroids, cluster_territories, workload_balance_score

DATA_PATH = Path(__file__).parent / "demo" / "sample_data.csv"


def format_idr(value: float) -> str:
    """Format number as Indonesian Rupiah."""
    return f"Rp {value:,.0f}"


@st.cache_data(show_spinner=False)
def get_data(path: str) -> pd.DataFrame:
    """Cached data loader."""
    return load_sales_data(path)


def render_sidebar(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Render sidebar filters and return filtered data."""
    st.sidebar.header("Filters")
    territories = unique_values(df, "territory")
    selected_territories = st.sidebar.multiselect(
        "Territory",
        options=territories,
        default=territories,
    )
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    else:
        start, end = pd.Timestamp(min_date), pd.Timestamp(max_date)

    filtered = filter_by_date_range(df, start, end)
    filtered = filter_by_territory(filtered, selected_territories)
    return filtered, selected_territories


def render_overview(df: pd.DataFrame) -> None:
    """KPI overview row."""
    total_revenue = float(df["revenue_idr"].sum())
    total_scripts = int(df["prescriptions"].sum())
    total_visits = int(df["visits"].sum())
    total_hcps = df["hcp_id"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", format_idr(total_revenue))
    col2.metric("Prescriptions", f"{total_scripts:,}")
    col3.metric("HCP Visits", f"{total_visits:,}")
    col4.metric("Unique HCPs", f"{total_hcps:,}")


def render_territory_map(df: pd.DataFrame) -> None:
    """Interactive territory map view."""
    st.subheader("Territory Map — Indonesia")
    summary = territory_summary(df)
    if summary.empty:
        st.info("No territory data available for the selected filters.")
        return

    fig = px.scatter_mapbox(
        summary,
        lat="latitude",
        lon="longitude",
        size="revenue_idr",
        color="coverage_ratio",
        color_continuous_scale="Viridis",
        size_max=50,
        zoom=3.8,
        hover_name="territory",
        hover_data={
            "city": True,
            "province": True,
            "revenue_idr": ":,.0f",
            "prescriptions": True,
            "hcp_count": True,
            "coverage_ratio": ":.2f",
            "latitude": False,
            "longitude": False,
        },
        mapbox_style="open-street-map",
        height=520,
    )
    fig.update_layout(margin={"l": 0, "r": 0, "t": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        summary.style.format({
            "revenue_idr": "Rp {:,.0f}",
            "coverage_ratio": "{:.2f}",
        }),
        use_container_width=True,
    )


def render_hcp_coverage(df: pd.DataFrame) -> None:
    """HCP coverage matrix page."""
    st.subheader("HCP Coverage Matrix")
    matrix = hcp_coverage_matrix(df)
    if matrix.empty:
        st.info("No HCP data available.")
        return

    product_cols = [c for c in matrix.columns if c not in {"hcp_id", "hcp_name", "hcp_specialty"}]
    heat = matrix[product_cols].to_numpy()
    fig = go.Figure(
        data=go.Heatmap(
            z=heat,
            x=product_cols,
            y=matrix["hcp_name"],
            colorscale="Blues",
            hoverongaps=False,
            colorbar={"title": "Visits"},
        )
    )
    fig.update_layout(
        height=620,
        xaxis_title="Product",
        yaxis_title="HCP",
        margin={"l": 10, "r": 10, "t": 30, "b": 10},
    )
    st.plotly_chart(fig, use_container_width=True)

    min_visits = st.slider("Under-covered HCP threshold (visits)", 1, 15, 7)
    gaps = under_covered_hcps(df, min_visits=min_visits)
    st.caption(f"{len(gaps)} HCPs below {min_visits} total visits.")
    st.dataframe(gaps, use_container_width=True)


def render_forecast(df: pd.DataFrame) -> None:
    """Prescription trend forecasting page."""
    st.subheader("Prescription Trend & Forecast")
    periods = st.slider("Forecast horizon (months)", 1, 12, 3)
    result = forecast_prescriptions(df, periods=periods)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=result.history["month"],
        y=result.history["prescriptions"],
        mode="lines+markers",
        name="Historical",
        line={"color": "#1f77b4", "width": 3},
    ))
    fig.add_trace(go.Scatter(
        x=result.forecast["month"],
        y=result.forecast["prescriptions"],
        mode="lines+markers",
        name="Forecast",
        line={"color": "#ff7f0e", "width": 3, "dash": "dash"},
    ))
    fig.add_trace(go.Scatter(
        x=pd.concat([result.forecast["month"], result.forecast["month"][::-1]]),
        y=pd.concat([result.forecast["upper"], result.forecast["lower"][::-1]]),
        fill="toself",
        fillcolor="rgba(255,127,14,0.2)",
        line={"color": "rgba(255,255,255,0)"},
        hoverinfo="skip",
        showlegend=True,
        name="95% CI",
    ))
    fig.update_layout(
        height=480,
        xaxis_title="Month",
        yaxis_title="Prescriptions",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Trend slope", f"{result.slope:+.1f}/month")
    col2.metric("Intercept", f"{result.intercept:.1f}")
    col3.metric("R²", f"{result.r2:.3f}")

    st.markdown("##### Monthly aggregates")
    trend = monthly_trend(df)
    st.dataframe(
        trend.style.format({"revenue_idr": "Rp {:,.0f}"}),
        use_container_width=True,
    )


def render_rep_scorecard(df: pd.DataFrame) -> None:
    """Rep performance scorecard page."""
    st.subheader("Rep Performance Scorecard")
    scorecard = rep_scorecard(df)
    if scorecard.empty:
        st.info("No rep data available.")
        return

    balance = workload_balance_score(scorecard)
    st.metric("Workload Balance Score", f"{balance:.2f}", help="1.00 = perfectly balanced")

    fig = px.bar(
        scorecard,
        x="rep_name",
        y="revenue_idr",
        color="coverage_pct",
        color_continuous_scale="RdYlGn",
        text="revenue_idr",
        hover_data=["territory", "prescriptions", "hcp_reached"],
        height=440,
    )
    fig.update_traces(texttemplate="Rp %{text:,.0f}", textposition="outside")
    fig.update_layout(xaxis_title="Rep", yaxis_title="Revenue (IDR)")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        scorecard.style.format({
            "revenue_idr": "Rp {:,.0f}",
            "avg_script_value": "Rp {:,.0f}",
            "coverage_pct": "{:.1f}%",
        }),
        use_container_width=True,
    )

    st.markdown("##### Product mix")
    mix = product_mix(df)
    pie = px.pie(mix, values="revenue_idr", names="product", hole=0.4, height=360)
    st.plotly_chart(pie, use_container_width=True)


def render_optimization(df: pd.DataFrame) -> None:
    """Territory optimization via KMeans clustering."""
    st.subheader("Territory Optimization")
    n_clusters = st.slider("Proposed number of territories", 2, 8, 4)
    clusters = cluster_territories(df, n_clusters=n_clusters)
    if clusters.empty:
        st.info("Not enough geographic data.")
        return

    centroids = cluster_centroids(clusters)
    fig = px.scatter_mapbox(
        clusters,
        lat="latitude",
        lon="longitude",
        color=clusters["cluster"].astype(str),
        hover_name="hcp_name",
        hover_data=["territory", "city"],
        zoom=3.8,
        mapbox_style="open-street-map",
        height=520,
    )
    fig.add_trace(go.Scattermapbox(
        lat=centroids["latitude"],
        lon=centroids["longitude"],
        mode="markers",
        marker={"size": 18, "color": "black", "symbol": "circle"},
        name="Centroid",
        hovertext=[f"Cluster {c} · {n} HCPs" for c, n in zip(centroids["cluster"], centroids["hcp_count"])],
    ))
    fig.update_layout(margin={"l": 0, "r": 0, "t": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("##### Proposed cluster centroids")
    st.dataframe(centroids, use_container_width=True)


def main() -> None:
    """Entry point for the Streamlit app."""
    st.set_page_config(
        page_title="Pharma Sales Territory Analyzer",
        page_icon="💊",
        layout="wide",
    )
    st.title("Pharma Sales Territory Analyzer")
    st.caption("HCP coverage · Prescription trends · Territory optimization · Rep scorecard")

    try:
        df = get_data(str(DATA_PATH))
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"Failed to load data: {exc}")
        st.stop()

    filtered, selected_territories = render_sidebar(df)
    if filtered.empty:
        st.warning("No data matches the selected filters.")
        st.stop()

    st.sidebar.caption(f"Rows: {len(filtered):,} · Territories: {len(selected_territories)}")

    render_overview(filtered)

    tabs = st.tabs([
        "Territory Map",
        "HCP Coverage",
        "Forecast",
        "Rep Scorecard",
        "Optimization",
    ])
    with tabs[0]:
        render_territory_map(filtered)
    with tabs[1]:
        render_hcp_coverage(filtered)
    with tabs[2]:
        render_forecast(filtered)
    with tabs[3]:
        render_rep_scorecard(filtered)
    with tabs[4]:
        render_optimization(filtered)


if __name__ == "__main__":
    main()
