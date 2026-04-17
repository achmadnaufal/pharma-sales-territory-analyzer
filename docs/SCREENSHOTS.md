# Screenshots & Views

This document describes each view in the Pharma Sales Territory Analyzer dashboard.

---

## Sidebar

**Filters**
- **Territory** multi-select (10 Indonesian territories)
- **Date range** picker (default: full data span)
- Filter summary shows row count and selected territory count

---

## Page 1 — Overview (always-visible KPI row)

Four KPI cards at the top of every tab:

| Card | Metric |
|---|---|
| Total Revenue | Sum of `revenue_idr` (formatted as Rp) |
| Prescriptions | Sum of `prescriptions` |
| HCP Visits | Sum of `visits` |
| Unique HCPs | `nunique` of `hcp_id` |

---

## Page 2 — Territory Map

- **Chart type**: Plotly `scatter_mapbox` (open-street-map tiles)
- **Markers**: one per territory; **size** = revenue, **color** = coverage ratio (Viridis scale)
- **Zoom**: centered on Indonesia (zoom 3.8)
- **Hover**: city, province, revenue, prescriptions, HCP count, coverage
- Below the map: sortable table of per-territory aggregates

## Page 3 — HCP Coverage Matrix

- **Chart type**: Plotly `Heatmap` (Blues colorscale)
- **Rows**: HCPs, **columns**: products, **cells**: total visits
- **Slider**: under-covered HCP threshold (1–15 visits)
- **Table**: HCPs below the threshold with specialty and territory

## Page 4 — Prescription Forecast

- **Chart type**: Plotly line chart
  - Solid blue: historical monthly prescriptions
  - Dashed orange: forecast
  - Shaded orange band: 95% confidence interval
- **Slider**: forecast horizon (1–12 months)
- **KPIs**: trend slope (scripts/month), intercept, R²
- **Table**: monthly aggregates

## Page 5 — Rep Scorecard

- **Workload Balance Score** (0–1) derived from coefficient of variation of rep revenue
- **Bar chart**: revenue per rep, colored by coverage % (RdYlGn)
- **Table**: rank_revenue, rank_coverage, avg_script_value, HCPs reached
- **Donut chart**: product revenue mix

## Page 6 — Territory Optimization

- **Chart type**: Plotly `scatter_mapbox` with HCPs colored by proposed cluster
- **Overlay**: black centroid markers per cluster
- **Slider**: desired number of territories (2–8)
- **Table**: cluster centroids (lat/lon, HCP count)

---

## Data schema (`demo/sample_data.csv`)

| Column | Type | Notes |
|---|---|---|
| date | date | ISO-8601 |
| rep_id, rep_name | string | Indonesian names |
| territory | string | e.g. `T-JKT-01` |
| city, province | string | Indonesian geography |
| latitude, longitude | float | For map rendering |
| hcp_id, hcp_name, hcp_specialty | string | HCP metadata |
| product | string | 6 SKUs |
| prescriptions | int | Monthly prescriptions |
| revenue_idr | float | Rupiah |
| visits, target_visits | int | For coverage ratio |
