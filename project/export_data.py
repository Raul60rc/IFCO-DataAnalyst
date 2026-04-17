"""
Export script: reads raw orders.csv, cleans it, and saves to project/data/orders.csv.
"""
import json
import pandas as pd
from pathlib import Path


def parse_contact_data(raw: str) -> dict | None:
    """Parse the contact_data JSON string into a dict with first/last name."""
    if pd.isna(raw) or str(raw).strip() == "":
        return None
    try:
        s = str(raw).strip()
        parsed = json.loads(s)
        if isinstance(parsed, list):
            parsed = parsed[0] if parsed else {}
        first = parsed.get("contact_name", "")
        last = parsed.get("contact_surname", "")
        return {"first": first, "last": last}
    except json.JSONDecodeError:
        return None


def main():
    root = Path(__file__).parent.parent
    raw_path = root / "data-engineering-test" / "resources" / "orders.csv"
    out_dir = Path(__file__).parent / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "orders.csv"

    # 1. Read with semicolon separator
    df = pd.read_csv(raw_path, sep=";")

    # 2. Rename salesowners -> sales_owners
    df = df.rename(columns={"salesowners": "sales_owners"})

    # 3. Parse date from dd.mm.yy to datetime
    df["date"] = pd.to_datetime(df["date"], format="%d.%m.%y")

    # 4. Parse contact_data JSON, fill empty from matching company_id,
    #    extract "FirstName LastName" as contact_name
    df["_parsed_contact"] = df["contact_data"].apply(parse_contact_data)

    # Build a lookup: company_id -> first non-null parsed contact
    company_contact = {}
    for _, row in df.iterrows():
        cid = row["company_id"]
        parsed = row["_parsed_contact"]
        if parsed is not None and cid not in company_contact:
            company_contact[cid] = parsed

    # Fill missing contacts from company_id lookup
    def resolve_contact(row):
        parsed = row["_parsed_contact"]
        if parsed is not None:
            return parsed
        return company_contact.get(row["company_id"])

    df["_resolved_contact"] = df.apply(resolve_contact, axis=1)

    def format_contact_name(parsed):
        if parsed is None:
            return "Unknown"
        first = str(parsed.get("first", "")).strip()
        last = str(parsed.get("last", "")).strip()
        full = f"{first} {last}".strip()
        return full if full else "Unknown"

    df["contact_name"] = df["_resolved_contact"].apply(format_contact_name)
    df["has_contact"] = df["_resolved_contact"].notnull()

    # 5. Fix company name inconsistencies: same company_id -> most frequent name
    most_frequent_name = (
        df.groupby("company_id")["company_name"]
        .agg(lambda x: x.value_counts().index[0])
    )
    df["company_name"] = df["company_id"].map(most_frequent_name)

    # 6. Explode sales_owners (comma-separated) into one row per owner per order
    df["sales_owner"] = df["sales_owners"].str.split(",")
    df = df.explode("sales_owner")
    df["sales_owner"] = df["sales_owner"].str.strip()

    # 7. Add sales_owner_count (number of owners per original order)
    owner_counts = df.groupby("order_id")["sales_owner"].transform("count")
    df["sales_owner_count"] = owner_counts.astype(int)

    # Select final columns
    final_cols = [
        "order_id", "date", "company_id", "company_name", "crate_type",
        "sales_owner", "has_contact", "contact_name", "sales_owner_count",
    ]
    df = df[final_cols].reset_index(drop=True)

    df.to_csv(out_path, index=False)
    print(f"Exported {len(df)} rows to {out_path}")
    print(f"Unique orders: {df['order_id'].nunique()}")
    print(f"Columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
