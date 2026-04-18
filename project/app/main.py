"""Streamlit dashboard entry point — layout only, no business logic."""
import sys
from pathlib import Path

_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import streamlit as st
from utils.data_loader import load_orders, apply_filters
from utils.metrics import (
    compute_total_orders,
    compute_selected_orders,
    compute_selected_ratio,
    compute_owners_below_threshold,
    compute_total_unique_owners,
    compute_crate_distribution,
    compute_owner_ratios,
    filter_last_12_months,
    compute_rolling_ranks,
    compute_top_performers,
)
from utils.charts import (
    build_donut_chart,
    build_training_bar_chart,
    build_top_performers_chart,
    build_bump_chart,
)

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Orders Dashboard", layout="wide")

# ── Force white background everywhere + green sidebar ────────────────────
st.markdown(
    """
    <style>
    /* Main app: white background */
    .stApp {
        background-color: #ffffff !important;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
    }
    [data-testid="stHeader"] {
        background-color: #ffffff !important;
    }

    /* Sidebar: green background */
    [data-testid="stSidebar"] {
        background-color: #2d6a4f !important;
    }
    /* Sidebar: all labels, headers, text → white */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stSliderTickBarMin"],
    [data-testid="stSidebar"] [data-testid="stSliderTickBarMax"],
    [data-testid="stSidebar"] [data-testid="stThumbValue"] {
        color: #ffffff !important;
    }
    /* Sidebar slider: white bar and thumb */
    [data-testid="stSidebar"] [data-baseweb="slider"] > div > div:first-child {
        background: rgba(255,255,255,0.35) !important;
        height: 8px !important;
        border-radius: 4px !important;
    }
    [data-testid="stSidebar"] [data-baseweb="slider"] [role="progressbar"] > div {
        background: #ffffff !important;
        height: 8px !important;
        border-radius: 4px !important;
    }
    [data-testid="stSidebar"] [data-baseweb="slider"] [role="slider"] {
        background-color: #ffffff !important;
        border: 3px solid #ffffff !important;
        box-shadow: 0 0 4px rgba(0,0,0,0.3) !important;
        width: 22px !important;
        height: 22px !important;
    }

    /* Tab text */
    .stTabs [data-baseweb="tab"] {
        color: #1a1a2e !important;
    }

    /* Main area sliders: dark for contrast on white */
    [data-testid="stMain"] [data-baseweb="slider"] [role="slider"] {
        background-color: #1a1a2e !important;
        border-color: #1a1a2e !important;
    }
    [data-testid="stMain"] [data-baseweb="slider"] [role="progressbar"] > div {
        background-color: #1a1a2e !important;
    }
    /* Main area radio: dark circle, visible text */
    [data-testid="stMain"] [role="radiogroup"] label > div:first-child > div {
        border-color: #1a1a2e !important;
    }
    [data-testid="stMain"] [role="radiogroup"] [aria-checked="true"] > div:first-child > div {
        background-color: #1a1a2e !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

all_crate_types = sorted(df_raw["crate_type"].unique().tolist())
selected_crates = st.sidebar.multiselect(
    "Crate types", options=all_crate_types, default=all_crate_types
)

threshold = st.sidebar.slider(
    "Crate ratio threshold (%)", min_value=0, max_value=60, value=60, step=1
)

# ── Apply date filter ────────────────────────────────────────────────────
df = apply_filters(df_raw, (start_date, end_date), all_crate_types)

if set(selected_crates) == set(all_crate_types):
    crate_label = "All Crates"
elif len(selected_crates) == 1:
    crate_label = selected_crates[0]
else:
    crate_label = " + ".join(selected_crates)


# ── Helpers ──────────────────────────────────────────────────────────────
def kpi_card(label: str, value: str, bg: str = "#f0f2f6", text_color: str = "#1a1a2e"):
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


def threshold_style(ratio, thresh):
    if ratio >= thresh:
        return "#2d6a4f", "#ffffff"
    elif ratio >= thresh * 0.7:
        return "#e9c46a", "#1a1a2e"
    else:
        return "#e63946", "#ffffff"


def training_kpi_style(below_count, total_owners):
    if total_owners == 0:
        return "#f0f2f6", "#1a1a2e"
    pct = below_count / total_owners
    if pct > 0.5:
        return "#e63946", "#ffffff"
    elif pct >= 0.25:
        return "#e9c46a", "#1a1a2e"
    else:
        return "#2d6a4f", "#ffffff"


# ── KPI row ──────────────────────────────────────────────────────────────
total_orders = compute_total_orders(df)
selected_orders = compute_selected_orders(df, selected_crates)
selected_ratio = compute_selected_ratio(df, selected_crates)

# Owners needing training uses the same date-filtered data
owners_below = compute_owners_below_threshold(df, selected_crates, threshold)
total_owners = compute_total_unique_owners(df)

ratio_bg, ratio_tc = threshold_style(selected_ratio, threshold)
training_bg, training_tc = training_kpi_style(owners_below, total_owners)

# Date label for chart titles
import datetime
date_label = f"{start_date.strftime('%b %Y')} – {end_date.strftime('%b %Y')}"

col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi_card("Total Orders", str(total_orders))
with col2:
    kpi_card(f"{crate_label} Orders", str(selected_orders))
with col3:
    kpi_card(f"{crate_label} Ratio", f"{selected_ratio:.1f}%", bg=ratio_bg, text_color=ratio_tc)
with col4:
    kpi_card("Owners Needing Training", f"{owners_below} / {total_owners}", bg=training_bg, text_color=training_tc)

# ── Tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🍩 Crate Distribution",
    "📉 Training Needs",
    "🏆 Top Performers",
])

# ── Tab 1 ────────────────────────────────────────────────────────────────
with tab1:
    crate_dist = compute_crate_distribution(df)
    st.plotly_chart(build_donut_chart(crate_dist), use_container_width=True)

# ── Tab 2 ────────────────────────────────────────────────────────────────
with tab2:
    owner_ratios = compute_owner_ratios(df, selected_crates)
    if owner_ratios.empty:
        st.info("No data with current filters.")
    else:
        st.plotly_chart(
            build_training_bar_chart(owner_ratios, threshold, crate_label, date_label),
            use_container_width=True,
        )

# ── Tab 3: Bump chart + total bar chart ──────────────────────────────────
with tab3:
    ranks = compute_rolling_ranks(df, selected_crates, window=3, top_n=5)
    if ranks.empty:
        st.info("Not enough data for the bump chart with current filters.")
    else:
        st.plotly_chart(
            build_bump_chart(ranks, crate_label, 3),
            use_container_width=True,
        )

    st.divider()
    st.subheader("Total Orders (Full Period)")
    top_performers = compute_top_performers(df, selected_crates, top_n=5)
    if top_performers.empty:
        st.info("No data for top performers with current filters.")
    else:
        st.plotly_chart(
            build_top_performers_chart(top_performers, crate_label),
            use_container_width=True,
        )
