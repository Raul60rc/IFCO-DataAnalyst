"""Load and validate the cleaned orders CSV."""
import pandas as pd
from pathlib import Path

EXPECTED_COLUMNS = [
    "order_id", "date", "company_id", "company_name", "crate_type",
    "sales_owner", "has_contact", "contact_name", "sales_owner_count",
]


def load_orders() -> pd.DataFrame:
    """Load the cleaned orders CSV and validate its schema."""
    csv_path = Path(__file__).parent.parent / "data" / "orders.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Orders CSV not found at {csv_path}")

    df = pd.read_csv(csv_path, parse_dates=["date"])

    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    df["has_contact"] = df["has_contact"].astype(bool)
    df["sales_owner_count"] = df["sales_owner_count"].astype(int)
    return df


def apply_filters(
    df: pd.DataFrame,
    date_range: tuple,
    crate_types: list[str],
) -> pd.DataFrame:
    """Apply sidebar filters to the dataframe."""
    filtered = df[
        (df["date"] >= pd.Timestamp(date_range[0]))
        & (df["date"] <= pd.Timestamp(date_range[1]))
    ]
    if crate_types:
        filtered = filtered[filtered["crate_type"].isin(crate_types)]
    return filtered
