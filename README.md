# Pharma Sales Territory Analyzer

[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)

Streamlit dashboard for **pharma sales territory analysis** in Indonesia — HCP coverage, prescription volume trends, territory optimization, and rep performance ranking.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the Streamlit app
streamlit run app.py

# 3. Open the browser
# Streamlit will auto-open http://localhost:8501
```

## Features

- **Territory Map** — Interactive Plotly Mapbox with coverage-ratio color scale across Indonesian provinces.
- **HCP Coverage Matrix** — Visit heatmap per HCP × product with under-covered-HCP flagging.
- **Prescription Trend Forecasting** — Linear-regression forecast with 95% confidence band (1–12 months).
- **Rep Performance Scorecard** — Revenue rank, coverage %, avg script value, workload balance score.
- **Territory Optimization** — KMeans clustering of HCP geography to propose rebalanced territories.

## Sample Output

Loaded from `demo/sample_data.csv` (30 rows spanning 10 reps, 10 territories, 6 products across Jakarta, Surabaya, Bandung, Medan, Makassar, Denpasar, Yogyakarta, Semarang, Palembang):

| Metric | Value |
|---|---|
| Total Revenue | Rp 551,900,000 |
| Prescriptions | 1,024 |
| Unique HCPs | 30 |
| Territories | 10 |
| Products | 6 |

See [`docs/SCREENSHOTS.md`](docs/SCREENSHOTS.md) for page-by-page descriptions.

## Tech Stack

- **Streamlit** — UI and interactivity
- **Pandas** — Data aggregation and transformation
- **Plotly** — Interactive maps, heatmaps, charts
- **Scikit-learn** — Linear regression forecasting + KMeans clustering
- **pytest** — Test suite (5 test files, 40+ tests)

## Project Structure

```
pharma-sales-territory-analyzer/
├── app.py                      # Streamlit entry point
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # CSV loading + filtering
│   ├── analytics.py            # Territory / rep / HCP aggregations
│   ├── forecasting.py          # Linear-regression monthly forecast
│   └── optimization.py         # KMeans territory clustering
├── demo/
│   └── sample_data.csv         # 30 rows of Indonesian sample data
├── tests/
│   ├── conftest.py
│   ├── test_data_loader.py
│   ├── test_analytics.py
│   ├── test_forecasting.py
│   ├── test_optimization.py
│   └── test_integration.py
├── docs/
│   └── SCREENSHOTS.md          # Page-by-page view descriptions
├── requirements.txt
├── LICENSE                     # MIT
└── README.md
```

## Testing

```bash
pytest -q
```

## License

MIT — see [LICENSE](./LICENSE).
