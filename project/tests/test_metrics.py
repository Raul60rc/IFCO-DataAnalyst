"""Pytest tests for utils.metrics — uses synthetic DataFrames."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import pytest
from utils.metrics import (
    compute_selected_ratio,
    compute_selected_orders,
    compute_owner_ratios,
    compute_owners_below_threshold,
    filter_last_12_months,
    compute_top_performers,
    compute_total_orders,
)


def _make_df(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df


# ── test_plastic_ratio_basic ─────────────────────────────────────────────
class TestPlasticRatioBasic:
    def test_plastic_ratio_basic(self):
        df = _make_df([
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": "X"},
            {"order_id": "B", "crate_type": "Wood", "sales_owner": "X"},
            {"order_id": "C", "crate_type": "Plastic", "sales_owner": "Y"},
            {"order_id": "D", "crate_type": "Metal", "sales_owner": "Y"},
        ])
        assert compute_selected_ratio(df, ["Plastic"]) == pytest.approx(50.0)

    def test_all_plastic(self):
        df = _make_df([
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": "X"},
            {"order_id": "B", "crate_type": "Plastic", "sales_owner": "Y"},
        ])
        assert compute_selected_ratio(df, ["Plastic"]) == pytest.approx(100.0)

    def test_no_plastic(self):
        df = _make_df([
            {"order_id": "A", "crate_type": "Wood", "sales_owner": "X"},
            {"order_id": "B", "crate_type": "Metal", "sales_owner": "Y"},
        ])
        assert compute_selected_ratio(df, ["Plastic"]) == pytest.approx(0.0)

    def test_multi_crate_selection(self):
        df = _make_df([
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": "X"},
            {"order_id": "B", "crate_type": "Wood", "sales_owner": "X"},
            {"order_id": "C", "crate_type": "Metal", "sales_owner": "Y"},
        ])
        assert compute_selected_ratio(df, ["Plastic", "Wood"]) == pytest.approx(66.67, rel=0.01)


# ── test_plastic_ratio_zero_orders ───────────────────────────────────────
class TestPlasticRatioZeroOrders:
    def test_empty_dataframe(self):
        df = pd.DataFrame(columns=["order_id", "crate_type", "sales_owner"])
        assert compute_selected_ratio(df, ["Plastic"]) == 0.0


# ── test_plastic_ratio_null_owner ────────────────────────────────────────
class TestPlasticRatioNullOwner:
    def test_null_sales_owner_still_counted(self):
        df = _make_df([
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": None},
            {"order_id": "B", "crate_type": "Wood", "sales_owner": "X"},
        ])
        assert compute_selected_ratio(df, ["Plastic"]) == pytest.approx(50.0)

    def test_all_null_owners(self):
        df = _make_df([
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": None},
            {"order_id": "B", "crate_type": "Plastic", "sales_owner": None},
        ])
        assert compute_selected_ratio(df, ["Plastic"]) == pytest.approx(100.0)


# ── test_top_performers ─────────────────────────────────────────────────
class TestTopPerformers:
    def test_top5_basic(self):
        df = _make_df([
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": "X"},
            {"order_id": "B", "crate_type": "Plastic", "sales_owner": "X"},
            {"order_id": "C", "crate_type": "Plastic", "sales_owner": "Y"},
            {"order_id": "D", "crate_type": "Wood", "sales_owner": "X"},
        ])
        result = compute_top_performers(df, ["Plastic"], top_n=5)
        assert result.iloc[0]["sales_owner"] == "X"
        assert result.iloc[0]["order_count"] == 2
        assert result.iloc[1]["sales_owner"] == "Y"
        assert result.iloc[1]["order_count"] == 1

    def test_limits_to_n(self):
        rows = []
        for i in range(8):
            for j in range(i + 1):
                rows.append({
                    "order_id": f"O_{i}_{j}",
                    "crate_type": "Plastic",
                    "sales_owner": f"Owner_{i}",
                })
        df = _make_df(rows)
        result = compute_top_performers(df, ["Plastic"], top_n=3)
        assert len(result) == 3
        assert result.iloc[0]["sales_owner"] == "Owner_7"

    def test_multi_crate(self):
        df = _make_df([
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": "X"},
            {"order_id": "B", "crate_type": "Wood", "sales_owner": "X"},
            {"order_id": "C", "crate_type": "Metal", "sales_owner": "Y"},
        ])
        result = compute_top_performers(df, ["Plastic", "Wood"], top_n=5)
        assert result.iloc[0]["sales_owner"] == "X"
        assert result.iloc[0]["order_count"] == 2

    def test_empty(self):
        df = pd.DataFrame(columns=["order_id", "crate_type", "sales_owner"])
        result = compute_top_performers(df, ["Plastic"], top_n=5)
        assert result.empty

    def test_null_owners_excluded(self):
        df = _make_df([
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": None},
            {"order_id": "B", "crate_type": "Plastic", "sales_owner": "X"},
        ])
        result = compute_top_performers(df, ["Plastic"], top_n=5)
        assert len(result) == 1
        assert result.iloc[0]["sales_owner"] == "X"


# ── test_duplicate_order_ids ─────────────────────────────────────────────
class TestDuplicateOrderIds:
    def test_duplicates_not_double_counted(self):
        df = _make_df([
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": "X"},
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": "Y"},
            {"order_id": "B", "crate_type": "Wood", "sales_owner": "X"},
        ])
        assert compute_total_orders(df) == 2
        assert compute_selected_orders(df, ["Plastic"]) == 1
        assert compute_selected_ratio(df, ["Plastic"]) == pytest.approx(50.0)

    def test_owner_ratios_with_duplicates(self):
        df = _make_df([
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": "X"},
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": "Y"},
            {"order_id": "B", "crate_type": "Wood", "sales_owner": "X"},
            {"order_id": "B", "crate_type": "Wood", "sales_owner": "Y"},
        ])
        ratios = compute_owner_ratios(df, ["Plastic"])
        x_ratio = ratios[ratios["sales_owner"] == "X"]["ratio"].values[0]
        y_ratio = ratios[ratios["sales_owner"] == "Y"]["ratio"].values[0]
        assert x_ratio == pytest.approx(50.0)
        assert y_ratio == pytest.approx(50.0)

    def test_owners_below_threshold(self):
        df = _make_df([
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": "X"},
            {"order_id": "B", "crate_type": "Wood", "sales_owner": "X"},
            {"order_id": "C", "crate_type": "Wood", "sales_owner": "Y"},
            {"order_id": "D", "crate_type": "Wood", "sales_owner": "Y"},
        ])
        assert compute_owners_below_threshold(df, ["Plastic"], 30) == 1
        assert compute_owners_below_threshold(df, ["Plastic"], 60) == 2

    def test_top_performers_deduplicates(self):
        """Same order shared by two owners — each owner counts it once."""
        df = _make_df([
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": "X"},
            {"order_id": "A", "crate_type": "Plastic", "sales_owner": "Y"},
        ])
        result = compute_top_performers(df, ["Plastic"], top_n=5)
        assert result.iloc[0]["order_count"] == 1
        assert result.iloc[1]["order_count"] == 1
