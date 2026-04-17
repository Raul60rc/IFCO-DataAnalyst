# 📦 Orders Dashboard

Streamlit dashboard for analyzing crate order data, sales owner performance,
and plastic crate adoption across the organization.

## Project Structure

```
project/
├── app/
│   └── main.py                  ← Streamlit entry point (layout only)
├── utils/
│   ├── data_loader.py           ← Loads and validates the cleaned CSV
│   ├── metrics.py               ← All business logic (pure pandas)
│   └── charts.py                ← All Plotly figure builders
├── tests/
│   └── test_metrics.py          ← pytest tests with synthetic data
├── data/
│   └── orders.csv               ← Cleaned dataset
├── .streamlit/
│   └── config.toml              ← Theme configuration
├── export_data.py               ← Script to generate cleaned CSV from raw data
├── requirements.txt
├── Dockerfile
└── README.md
```

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app/main.py
```

## Docker

```bash
docker build -t orders-dashboard .
docker run -p 8501:8501 orders-dashboard
```

Then open http://localhost:8501.

## Run Tests

```bash
pytest tests/ -v
```

## KPI Conditional Formatting

The dashboard uses color-coded KPI cards based on the plastic ratio threshold
(configurable via the sidebar slider, default 30%):

| Condition                              | Background | Text  |
|----------------------------------------|------------|-------|
| ratio >= threshold                     | Green `#2d6a4f` | White |
| threshold × 0.7 <= ratio < threshold  | Amber `#e9c46a` | Dark  |
| ratio < threshold × 0.7               | Red `#e63946`   | White |

The same color scheme applies to per-owner bars in the Training Needs tab.

## Assumptions

- **Last 12 months**: Computed relative to `df['date'].max()`, not the current
  system date. This ensures reproducible results regardless of when the
  dashboard is viewed.
- **Rolling 3-month window**: Uses `min_periods=1`, so the first month still
  produces a value (just that single month's count). Months where an owner has
  zero plastic orders in the entire 3-month window are excluded — the line
  breaks rather than dropping to zero.
- **Sparse months**: If an owner has no orders in a given month, that month
  contributes 0 to the rolling sum. The owner only disappears from the chart
  when the full 3-month window has zero plastic orders.
- **Top-5 ties**: When multiple owners tie on rolling count, the top 5 are
  selected by pandas default sort stability (first encountered wins). This is
  deterministic but arbitrary among tied owners.
- **Duplicate order_ids**: The exploded dataset has one row per sales_owner per
  order. All KPIs use `nunique("order_id")` to avoid double-counting orders
  shared by multiple sales owners.
