"""Business logic — pure pandas computations, no Streamlit dependency."""
import pandas as pd


def compute_selected_ratio(df: pd.DataFrame, selected_crates: list[str]) -> float:
    """Return the ratio (0-100) of orders matching selected crate types."""
    unique_orders = df.drop_duplicates(subset="order_id")
    total = len(unique_orders)
    if total == 0:
        return 0.0
    matched = len(unique_orders[unique_orders["crate_type"].isin(selected_crates)])
    return (matched / total) * 100


def compute_selected_orders(df: pd.DataFrame, selected_crates: list[str]) -> int:
    """Count unique order_ids matching selected crate types."""
    return df[df["crate_type"].isin(selected_crates)]["order_id"].nunique()


def compute_owner_ratios(df: pd.DataFrame, selected_crates: list[str]) -> pd.DataFrame:
    """Per-owner ratio of selected crate types."""
    clean = df.dropna(subset=["sales_owner"])
    clean = clean[clean["sales_owner"].str.strip() != ""]
    total = clean.groupby("sales_owner")["order_id"].nunique().rename("total")
    matched = (
        clean[clean["crate_type"].isin(selected_crates)]
        .groupby("sales_owner")["order_id"]
        .nunique()
        .rename("matched")
    )
    result = pd.concat([total, matched], axis=1).fillna(0)
    result["matched"] = result["matched"].astype(int)
    result["ratio"] = (result["matched"] / result["total"]) * 100
    return result.reset_index()


def compute_owners_below_threshold(
    df: pd.DataFrame, selected_crates: list[str], threshold: float
) -> int:
    """Count of sales owners whose selected-crate ratio is below the threshold."""
    ratios = compute_owner_ratios(df, selected_crates)
    return int((ratios["ratio"] < threshold).sum())


def compute_total_unique_owners(df: pd.DataFrame) -> int:
    """Count total unique sales owners (excluding NaN/empty)."""
    clean = df.dropna(subset=["sales_owner"])
    clean = clean[clean["sales_owner"].str.strip() != ""]
    return clean["sales_owner"].nunique()


def filter_last_12_months(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to the last 12 months relative to df['date'].max()."""
    if df.empty:
        return df
    max_date = df["date"].max()
    cutoff = max_date - pd.DateOffset(months=12)
    return df[df["date"] > cutoff].copy()


def compute_rolling_ranks(
    df: pd.DataFrame, selected_crates: list[str], window: int = 3, top_n: int = 5
) -> pd.DataFrame:
    """
    For each calendar month, compute each owner's order count for selected
    crate types over a rolling N-month window (current month + N-1 prior).
    Rank owners per month and return top N.

    Returns DataFrame: month, sales_owner, rolling_count, rank.
    """
    if df.empty:
        return pd.DataFrame(columns=["month", "sales_owner", "rolling_count", "rank"])

    clean = df.dropna(subset=["sales_owner"])
    clean = clean[clean["sales_owner"].str.strip() != ""]
    filtered = clean[clean["crate_type"].isin(selected_crates)]

    if filtered.empty:
        return pd.DataFrame(columns=["month", "sales_owner", "rolling_count", "rank"])

    filtered = filtered.copy()
    filtered["month"] = filtered["date"].dt.to_period("M")

    monthly = (
        filtered.groupby(["month", "sales_owner"])["order_id"]
        .nunique()
        .reset_index(name="count")
    )

    all_months = sorted(monthly["month"].unique())
    all_owners = sorted(monthly["sales_owner"].unique())
    idx = pd.MultiIndex.from_product(
        [all_months, all_owners], names=["month", "sales_owner"]
    )
    full = monthly.set_index(["month", "sales_owner"]).reindex(idx, fill_value=0).reset_index()

    full = full.sort_values(["sales_owner", "month"])
    full["rolling_count"] = (
        full.groupby("sales_owner")["count"]
        .rolling(window, min_periods=1)
        .sum()
        .reset_index(level=0, drop=True)
        .astype(int)
    )

    # Drop zero-count rows
    full = full[full["rolling_count"] > 0]

    # Rank per month: highest count = rank 1, ties broken alphabetically
    full = full.sort_values(
        ["month", "rolling_count", "sales_owner"],
        ascending=[True, False, True],
    )
    full["rank"] = full.groupby("month").cumcount() + 1

    # Keep top N per month
    top = full[full["rank"] <= top_n].copy()
    top["month"] = top["month"].dt.to_timestamp()
    return top[["month", "sales_owner", "rolling_count", "rank"]].reset_index(drop=True)


def compute_top_performers(
    df: pd.DataFrame, selected_crates: list[str], top_n: int = 5
) -> pd.DataFrame:
    """Total unique orders per sales_owner for selected crate types, top N."""
    if df.empty:
        return pd.DataFrame(columns=["sales_owner", "order_count"])

    clean = df.dropna(subset=["sales_owner"])
    clean = clean[clean["sales_owner"].str.strip() != ""]
    filtered = clean[clean["crate_type"].isin(selected_crates)]

    if filtered.empty:
        return pd.DataFrame(columns=["sales_owner", "order_count"])

    counts = (
        filtered.groupby("sales_owner")["order_id"]
        .nunique()
        .reset_index(name="order_count")
        .sort_values("order_count", ascending=False)
    )
    return counts.head(top_n).reset_index(drop=True)


def compute_total_orders(df: pd.DataFrame) -> int:
    return df["order_id"].nunique()


def compute_crate_distribution(df: pd.DataFrame) -> pd.DataFrame:
    unique = df.drop_duplicates(subset="order_id")
    return unique.groupby("crate_type").size().reset_index(name="count")
