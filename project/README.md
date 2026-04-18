# 📦 Orders Dashboard

Streamlit dashboard for analyzing crate order data, sales owner performance,
and crate type adoption across the organization.

## Project Structure

```
project/
├── app/
│   ├── main.py                  ← Streamlit entry point (layout only)
│   └── assets/
│       └── ifco_logo.svg        ← IFCO logo displayed in sidebar
├── utils/
│   ├── data_loader.py           ← Loads and validates the cleaned CSV
│   ├── metrics.py               ← All business logic (pure pandas)
│   └── charts.py                ← All Plotly figure builders
├── tests/
│   └── test_metrics.py          ← pytest tests with synthetic data
├── notebooks/
│   └── dataRead.ipynb           ← Data exploration and cleaning notebook
├── data/
│   └── orders.csv               ← Cleaned dataset (153 rows, 62 unique orders)
├── .streamlit/
│   └── config.toml              ← Theme configuration (light mode, green primary)
├── export_data.py               ← Script to generate cleaned CSV from raw data
├── requirements.txt
├── Dockerfile
└── README.md
```

## Run Locally

```bash
cd project
pip install -r requirements.txt
python -m streamlit run app/main.py
```

Important: run from the `project/` directory so `.streamlit/config.toml` is picked up.

## Docker

```bash
cd project
docker build -t orders-dashboard .
docker run -p 8501:8501 orders-dashboard
```

Then open http://localhost:8501.

## Run Tests

```bash
cd project
pytest tests/ -v
```

## Dashboard Features

### Sidebar Filters
- **Date range**: filter orders by date
- **Crate types**: multi-select (Plastic, Wood, Metal) — all charts and KPIs react dynamically
- **Crate ratio threshold**: slider 0–60%, default 60%

### KPI Row (4 cards)
- **Total Orders**: unique order count for the date range
- **[Crate] Orders**: unique orders matching selected crate types
- **[Crate] Ratio**: percentage of orders matching selected crate types
- **Owners Needing Training**: count of owners below threshold / total owners

### Tab 1 — Crate Distribution
Donut chart showing order count and percentage per crate type.

### Tab 2 — Training Needs
Horizontal bar chart of per-owner crate ratio (last 12 months).
Owners below the threshold line need the most training.
Sorted with lowest ratio at the top for immediate visibility.

### Tab 3 — Top Performers
- **Bump chart**: monthly leaderboard showing rank shifts over the last 12 months
  (rolling 3-month window, top 5 most consistent performers)
- **Total orders bar chart**: overall order count per owner for the full period

## KPI Conditional Formatting

### Crate Ratio KPI

| Condition                              | Background | Text  |
|----------------------------------------|------------|-------|
| ratio >= threshold                     | Green `#2d6a4f` | White |
| threshold × 0.7 <= ratio < threshold  | Amber `#e9c46a` | Dark  |
| ratio < threshold × 0.7               | Red `#e63946`   | White |

### Owners Needing Training KPI

| Condition                                        | Background | Text  |
|--------------------------------------------------|------------|-------|
| owners below threshold > 50% of total owners     | Red `#e63946`   | White |
| owners below threshold between 25–50% of total   | Amber `#e9c46a` | Dark  |
| owners below threshold < 25% of total owners     | Green `#2d6a4f` | White |

### Training Needs Bar Chart

The same green/amber/red color scheme applies to each owner's bar.
Owners below the dashed threshold line need the most training on the
selected crate type sales.

## Assumptions

- **Last 12 months**: Computed relative to `df['date'].max()`, not the current
  system date. This ensures reproducible results regardless of when the
  dashboard is viewed. Applied to both Training Needs and the Bump Chart.
- **Rolling 3-month window**: Uses `min_periods=1`, so the first month still
  produces a value (just that single month's count). Months where an owner has
  zero orders for the selected crate types in the entire 3-month window are
  excluded — the line breaks rather than dropping to zero.
- **Top-5 filtering**: From all owners who ever appear in the top 5 for any
  month, only the 5 who appear most frequently are shown. This reduces noise
  and highlights the most consistent performers.
- **Sparse months**: If an owner has no orders in a given month, that month
  contributes 0 to the rolling sum. The owner only disappears from the chart
  when the full 3-month window has zero orders for the selected crate types.
- **Top-5 ties**: When multiple owners tie on rolling count, ties are broken
  alphabetically. This is deterministic and consistent.
- **Duplicate order_ids**: The exploded dataset has one row per sales_owner per
  order. All KPIs use `nunique("order_id")` to avoid double-counting orders
  shared by multiple sales owners.
- **Unknown contacts**: 14 orders (34 exploded rows) have no contact data in
  the source CSV and no matching company_id to fill from. These are marked as
  `contact_name = "Unknown"` and `has_contact = False`.
- **Crate type agnostic**: All KPIs, charts, and metrics dynamically adapt to
  whichever crate types are selected in the sidebar filter.
