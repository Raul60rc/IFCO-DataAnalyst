"""Streamlit dashboard entry point — layout only, no business logic."""
import sys
from pathlib import Path

# Ensure project root is on sys.path so utils can be imported
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import streamlit as st
from utils.data_loader import load_orders, apply_filters
from utils.metrics import (
    compute_total_orders,
    compute_plastic_orders,
    compute_plastic_ratio,
    compute_owners_below_threshold,
    compute_crate_distribution,
    compute_owner_plastic_ratios,
    filter_last_12_months,
    compute_rolling_top5,
)
from utils.charts import (
    build_donut_chart,
    build_training_bar_chart,
    build_rolling_top5_chart,
)

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Orders Dashboard", layout="wide")
st.title("📦 Orders Dashboard")

# ── Load data ────────────────────────────────────────────────────────────
df_raw = load_orders()

# ── Sidebar filters ──────────────────────────────────────────────────────
st.sidebar.header("Filters")

min_date = df_raw["date"].min().date()
max_date = df_raw["date"].max().date()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
# Ensure we always have a tuple of two dates
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

all_crate_types = sorted(df_raw["crate_type"].unique().tolist())
selected_crates = st.sidebar.multiselect(
    "Crate types", options=all_crate_types, default=all_crate_types
)

threshold = st.sidebar.slider(
    "Plastic ratio threshold (%)", min_value=10, max_value=60, value=30, step=1
)

# ── Apply filters ────────────────────────────────────────────────────────
df = apply_filters(df_raw, (start_date, end_date), selected_crates)


# ── Helper: conditional KPI card ─────────────────────────────────────────
def kpi_card(label: str, value: str, bg: str = "#f0f2f6", text_color: str = "#1a1a2e"):
    """Render a styled KPI metric card."""
    st.markdown(
        f"""
        <div style="
            background-color: {bg};
            padding: 1rem 1.2rem;
            border-radius: 0.6rem;
            text-align: center;
        ">
            <p style="margin:0; font-size:0.85rem; color:{text_color};">{label}</p>
            <p style="margin:0; font-size:1.8rem; font-weight:700; color:{text_color};">{value}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def threshold_style(ratio: float, thresh: float):
    """Return (bg_color, text_color) based on ratio vs threshold."""
    if ratio >= thresh:
        return "#2d6a4f", "#ffffff"
    elif ratio >= thresh * 0.7:
        return "#e9c46a", "#1a1a2e"
    else:
        return "#e63946", "#ffffff"


# ── KPI row ──────────────────────────────────────────────────────────────
total_orders = compute_total_orders(df)
plastic_orders = compute_plastic_orders(df)
plastic_ratio = compute_plastic_ratio(df)
owners_below = compute_owners_below_threshold(df, threshold)

ratio_bg, ratio_tc = threshold_style(plastic_ratio, threshold)
owners_bg, owners_tc = ("#e63946", "#ffffff") if owners_below > 0 else ("#2d6a4f", "#ffffff")

col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi_card("Total Orders", str(total_orders))
with col2:
    kpi_card("Plastic Orders", str(plastic_orders))
with col3:
    kpi_card("Plastic Ratio", f"{plastic_ratio:.1f}%", bg=ratio_bg, text_color=ratio_tc)
with col4:
    kpi_card("Owners Below Threshold", str(owners_below), bg=owners_bg, text_color=owners_tc)

# ── Tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🍩 Crate Distribution",
    "📉 Training Needs",
    "🏆 Top 5 Performers",
])

# ── Tab 1: Donut chart ──────────────────────────────────────────────────
with tab1:
    crate_dist = compute_crate_distribution(df)
    plastic_share = compute_plastic_ratio(df)
    ps_bg, ps_tc = threshold_style(plastic_share, threshold)
    kpi_card("Plastic Share", f"{plastic_share:.1f}%", bg=ps_bg, text_color=ps_tc)
    st.plotly_chart(build_donut_chart(crate_dist), use_container_width=True)

# ── Tab 2: Training needs (last 12 months) ──────────────────────────────
with tab2:
    df_12m = filter_last_12_months(df)
    owner_ratios = compute_owner_plastic_ratios(df_12m)
    if owner_ratios.empty:
        st.info("No data for the last 12 months with current filters.")
    else:
        st.plotly_chart(
            build_training_bar_chart(owner_ratios, threshold),
            use_container_width=True,
        )

# ── Tab 3: Rolling top 5 ────────────────────────────────────────────────
with tab3:
    top5 = compute_rolling_top5(df)
    if top5.empty:
        st.info("Not enough data for rolling top-5 chart with current filters.")
    else:
        st.plotly_chart(
            build_rolling_top5_chart(top5),
            use_container_width=True,
        )
