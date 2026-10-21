from pathlib import Path
import sqlite3
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "outputs"
TABLE_DIR = OUT_DIR / "tables"
FIG_DIR = OUT_DIR / "figures"
DB_PATH = OUT_DIR / "retail_analysis.db"

REQUIRED_COLUMNS = [
    "InvoiceNo", "StockCode", "Description", "Quantity",
    "InvoiceDate", "UnitPrice", "CustomerID", "Country"
]


def locate_source() -> Path:
    candidates = [
        DATA_DIR / "Online Retail.xlsx",
        DATA_DIR / "online_retail.xlsx",
        DATA_DIR / "Online Retail.csv",
        DATA_DIR / "online_retail.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        "Dataset not found. Download 'Online Retail.xlsx' from the UCI source page "
        "and place it in the project's data/ folder."
    )


def load_source(path: Path) -> pd.DataFrame:
    print(f"Loading: {path.name}")
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path, encoding_errors="replace")
    else:
        df = pd.read_excel(path)
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
    return df[REQUIRED_COLUMNS].copy()


def main() -> None:
    for folder in (TABLE_DIR, FIG_DIR):
        folder.mkdir(parents=True, exist_ok=True)

    raw_path = locate_source()
    raw = load_source(raw_path)
    original_rows = len(raw)
    exact_duplicates = int(raw.duplicated().sum())

    df = raw.drop_duplicates().copy()
    df["InvoiceNo"] = df["InvoiceNo"].astype("string").str.strip()
    df["StockCode"] = df["StockCode"].astype("string").str.strip()
    df["Description"] = df["Description"].astype("string").str.strip()
    df["Country"] = df["Country"].astype("string").str.strip()
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    customer_num = pd.to_numeric(df["CustomerID"], errors="coerce")
    df["CustomerID"] = customer_num.round().astype("Int64").astype("string")
    df.loc[customer_num.isna(), "CustomerID"] = pd.NA

    missing_customer_ids = int(df["CustomerID"].isna().sum())
    invalid_dates = int(df["InvoiceDate"].isna().sum())
    cancellation_mask = df["InvoiceNo"].str.upper().str.startswith("C", na=False)
    cancellation_rows = int(cancellation_mask.sum())
    nonpositive_quantity_rows = int((df["Quantity"] <= 0).sum())
    nonpositive_price_rows = int((df["UnitPrice"] <= 0).sum())

    # Main sales analysis: completed positive-value lines only. Customer ID is not
    # required for sales trend/product/country reporting, but is required for RFM.
    sales = df.loc[
        (~cancellation_mask)
        & df["InvoiceDate"].notna()
        & df["Quantity"].gt(0)
        & df["UnitPrice"].gt(0)
    ].copy()
    sales["Revenue"] = sales["Quantity"] * sales["UnitPrice"]
    sales["Month"] = sales["InvoiceDate"].dt.to_period("M").astype(str)

    # Export clean analytical table for reproducibility and create SQLite DB.
    sales_export = sales.copy()
    sales_export["CustomerID"] = sales_export["CustomerID"].astype("object").where(
        sales_export["CustomerID"].notna(), None
    )
    with sqlite3.connect(DB_PATH) as conn:
        sales_export.to_sql("sales", conn, if_exists="replace", index=False)

    data_quality = pd.DataFrame([
        {"metric": "raw_rows", "value": original_rows},
        {"metric": "exact_duplicate_rows_removed", "value": exact_duplicates},
        {"metric": "rows_after_exact_duplicate_removal", "value": len(df)},
        {"metric": "missing_customer_id_rows", "value": missing_customer_ids},
        {"metric": "invalid_invoice_date_rows", "value": invalid_dates},
        {"metric": "cancellation_rows", "value": cancellation_rows},
        {"metric": "nonpositive_quantity_rows", "value": nonpositive_quantity_rows},
        {"metric": "nonpositive_unit_price_rows", "value": nonpositive_price_rows},
        {"metric": "rows_in_primary_sales_table", "value": len(sales)},
        {"metric": "identified_customers_in_sales_table", "value": sales["CustomerID"].nunique(dropna=True)},
    ])
    data_quality.to_csv(TABLE_DIR / "data_quality_summary.csv", index=False)

    monthly = sales.groupby("Month", as_index=False).agg(
        revenue=("Revenue", "sum"),
        units_sold=("Quantity", "sum"),
        order_count=("InvoiceNo", "nunique"),
        identified_customers=("CustomerID", "nunique"),
    )
    monthly["revenue"] = monthly["revenue"].round(2)
    monthly.to_csv(TABLE_DIR / "monthly_sales.csv", index=False)

    products = sales.groupby(["StockCode", "Description"], dropna=False, as_index=False).agg(
        revenue=("Revenue", "sum"),
        units_sold=("Quantity", "sum"),
        order_count=("InvoiceNo", "nunique"),
    ).sort_values("revenue", ascending=False)
    products["revenue"] = products["revenue"].round(2)
    products.head(100).to_csv(TABLE_DIR / "top_products.csv", index=False)

    countries = sales.groupby("Country", dropna=False, as_index=False).agg(
        revenue=("Revenue", "sum"),
        order_count=("InvoiceNo", "nunique"),
        identified_customers=("CustomerID", "nunique"),
    ).sort_values("revenue", ascending=False)
    countries["revenue"] = countries["revenue"].round(2)
    countries.head(100).to_csv(TABLE_DIR / "top_countries.csv", index=False)

    customer_sales = sales.loc[sales["CustomerID"].notna()].copy()
    if not customer_sales.empty:
        snapshot_date = customer_sales["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)
        rfm = customer_sales.groupby("CustomerID", as_index=False).agg(
            last_purchase=("InvoiceDate", "max"),
            frequency_orders=("InvoiceNo", "nunique"),
            monetary_revenue=("Revenue", "sum"),
        )
        rfm["recency_days"] = (snapshot_date - rfm["last_purchase"].dt.normalize()).dt.days
        rfm["monetary_revenue"] = rfm["monetary_revenue"].round(2)
        rfm["snapshot_date"] = snapshot_date.date().isoformat()
        rfm = rfm[["CustomerID", "snapshot_date", "recency_days", "frequency_orders", "monetary_revenue"]]
        rfm.sort_values("monetary_revenue", ascending=False).to_csv(TABLE_DIR / "customer_rfm.csv", index=False)

    # Charts are created from the same documented analytical table.
    plt.figure(figsize=(10, 5.5))
    plt.plot(monthly["Month"], monthly["revenue"], marker="o", linewidth=2)
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue (GBP, before costs)")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(FIG_DIR / "monthly_revenue.png", dpi=180)
    plt.close()

    top_products = products.head(10).sort_values("revenue", ascending=True)
    labels = top_products["Description"].fillna(top_products["StockCode"]).astype(str).str.slice(0, 38)
    plt.figure(figsize=(10, 6))
    plt.barh(labels, top_products["revenue"])
    plt.title("Top 10 Products by Revenue")
    plt.xlabel("Revenue (GBP, before costs)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "top_products.png", dpi=180)
    plt.close()

    top_countries = countries.head(10).sort_values("revenue", ascending=True)
    plt.figure(figsize=(9, 5.5))
    plt.barh(top_countries["Country"].astype(str), top_countries["revenue"])
    plt.title("Top 10 Countries by Revenue")
    plt.xlabel("Revenue (GBP, before costs)")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "top_countries.png", dpi=180)
    plt.close()

    summary = pd.DataFrame([
        {"metric": "total_revenue_gbp", "value": round(float(sales["Revenue"].sum()), 2)},
        {"metric": "unique_orders", "value": int(sales["InvoiceNo"].nunique())},
        {"metric": "identified_customers", "value": int(sales["CustomerID"].nunique(dropna=True))},
        {"metric": "units_sold", "value": int(sales["Quantity"].sum())},
        {"metric": "average_order_value_gbp", "value": round(float(sales.groupby("InvoiceNo")["Revenue"].sum().mean()), 2)},
        {"metric": "analysis_start", "value": sales["InvoiceDate"].min().date().isoformat()},
        {"metric": "analysis_end", "value": sales["InvoiceDate"].max().date().isoformat()},
    ])
    summary.to_csv(TABLE_DIR / "summary_metrics.csv", index=False)

    print("\nAnalysis complete. Review these outputs:")
    print(f"- {TABLE_DIR / 'data_quality_summary.csv'}")
    print(f"- {TABLE_DIR / 'summary_metrics.csv'}")
    print(f"- {TABLE_DIR / 'monthly_sales.csv'}")
    print(f"- {TABLE_DIR / 'top_products.csv'}")
    print(f"- {TABLE_DIR / 'top_countries.csv'}")
    print(f"- {TABLE_DIR / 'customer_rfm.csv'}")
    print(f"- {FIG_DIR}")
    print(f"- {DB_PATH}")
    print("\nNote: Revenue is not profit; customer-level analysis excludes missing CustomerID values.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
