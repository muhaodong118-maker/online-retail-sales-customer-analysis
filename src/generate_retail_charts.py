from pathlib import Path
import sqlite3
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# If this file is placed in <project>/src/, ROOT points to <project>.
# If run from elsewhere, the script tries to find the project by looking for outputs/retail_analysis.db.
HERE = Path(__file__).resolve()
if HERE.parent.name == "src":
    ROOT = HERE.parent.parent
elif (HERE.parent / "outputs" / "retail_analysis.db").exists():
    ROOT = HERE.parent
else:
    ROOT = Path.cwd()

DB_PATH = ROOT / "outputs" / "retail_analysis.db"
FIG_DIR = ROOT / "outputs" / "figures"

EXCLUDED_STOCK_CODES = {"DOT", "POST", "M"}


def money(value: float, decimals: int = 0) -> str:
    """Format revenue as GBP for chart labels."""
    return f"£{value:,.{decimals}f}"


def load_monthly_data(conn: sqlite3.Connection) -> tuple[pd.DataFrame, pd.Timestamp]:
    """Load monthly revenue, orders and identified customers from the clean sales table."""
    query = """
        SELECT
            substr(InvoiceDate, 1, 7) AS month,
            SUM(Revenue) AS revenue,
            SUM(Quantity) AS units_sold,
            COUNT(DISTINCT InvoiceNo) AS order_count,
            COUNT(DISTINCT CustomerID) AS identified_customers
        FROM sales
        GROUP BY substr(InvoiceDate, 1, 7)
        ORDER BY month
    """
    monthly = pd.read_sql_query(query, conn)
    max_date_text = pd.read_sql_query(
        "SELECT MAX(InvoiceDate) AS max_invoice_date FROM sales", conn
    ).iloc[0]["max_invoice_date"]

    if monthly.empty or pd.isna(max_date_text):
        raise ValueError("The sales table is empty. Run `python src/analyze.py` first.")

    monthly["month_dt"] = pd.to_datetime(monthly["month"] + "-01", errors="coerce")
    monthly["revenue"] = pd.to_numeric(monthly["revenue"], errors="coerce")
    monthly["order_count"] = pd.to_numeric(monthly["order_count"], errors="coerce")
    monthly["identified_customers"] = pd.to_numeric(
        monthly["identified_customers"], errors="coerce"
    )
    monthly["aov"] = monthly["revenue"] / monthly["order_count"].replace(0, np.nan)
    monthly["mom_growth_pct"] = monthly["revenue"].pct_change() * 100
    max_date = pd.to_datetime(max_date_text, errors="coerce")
    if pd.isna(max_date):
        raise ValueError(f"Could not parse latest invoice date: {max_date_text!r}")
    return monthly, max_date


def make_sales_trend(conn: sqlite3.Connection) -> None:
    """Chart 1: monthly revenue trend, with November growth and partial December noted."""
    monthly, max_date = load_monthly_data(conn)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.plot(monthly["month_dt"], monthly["revenue"], marker="o", linewidth=2)
    ax.set_title("Monthly Sales Revenue Trend", fontsize=16, pad=16)
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (GBP; before costs)")
    ax.grid(axis="y", alpha=0.25)
    ax.set_xticks(monthly["month_dt"])
    ax.set_xticklabels(monthly["month"], rotation=45, ha="right")
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _pos: f"£{x / 1_000_000:.1f}M" if x >= 1_000_000 else f"£{x / 1_000:.0f}K")
    )

    # Dynamic November annotation: avoid hard-coding performance figures in the chart.
    nov = monthly.loc[monthly["month"] == "2011-11"]
    if not nov.empty:
        row = nov.iloc[0]
        previous = monthly.loc[monthly["month"] == "2011-10"]
        order_growth = np.nan
        customer_growth = np.nan
        aov_growth = np.nan
        if not previous.empty:
            prev = previous.iloc[0]
            if prev["order_count"]:
                order_growth = (row["order_count"] / prev["order_count"] - 1) * 100
            if prev["identified_customers"]:
                customer_growth = (row["identified_customers"] / prev["identified_customers"] - 1) * 100
            if prev["aov"]:
                aov_growth = (row["aov"] / prev["aov"] - 1) * 100

        growth = row["mom_growth_pct"]
        note_lines = [f"Nov revenue: {money(row['revenue'])}"]
        if pd.notna(growth):
            note_lines.append(f"Revenue MoM: {growth:+.1f}%")
        if pd.notna(order_growth):
            note_lines.append(f"Orders: {order_growth:+.1f}%")
        if pd.notna(customer_growth):
            note_lines.append(f"Identified customers: {customer_growth:+.1f}%")
        if pd.notna(aov_growth):
            note_lines.append(f"AOV: {aov_growth:+.1f}%")

        ax.annotate(
            "\n".join(note_lines),
            xy=(row["month_dt"], row["revenue"]),
            xytext=(-145, -85),
            textcoords="offset points",
            arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=0.12"},
            bbox={"boxstyle": "round,pad=0.5", "alpha": 0.9},
            fontsize=9,
        )

    # The latest month is partial if the data ends before the end of that calendar month.
    latest_month = max_date.strftime("%Y-%m")
    latest_month_start = max_date.replace(day=1)
    next_month_start = latest_month_start + pd.offsets.MonthBegin(1)
    if max_date.normalize() < (next_month_start - pd.Timedelta(days=1)).normalize():
        partial = monthly.loc[monthly["month"] == latest_month]
        if not partial.empty:
            row = partial.iloc[0]
            ax.annotate(
                f"{latest_month}: partial month\ndata through {max_date.strftime('%d %b %Y')}",
                xy=(row["month_dt"], row["revenue"]),
                xytext=(-8, 28),
                textcoords="offset points",
                ha="right",
                arrowprops={"arrowstyle": "->"},
                fontsize=9,
            )

    fig.text(
        0.01, 0.01,
        "Revenue = Quantity × UnitPrice; cancelled invoices and non-positive quantity/price rows are excluded by the preparation script.",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = FIG_DIR / "monthly_sales_trend.png"
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")

    print("\nMonthly sales summary:")
    display_cols = ["month", "revenue", "order_count", "identified_customers", "aov", "mom_growth_pct"]
    print(monthly[display_cols].round(2).to_string(index=False))
    print(f"Latest transaction date in database: {max_date}")


def make_product_top10(conn: sqlite3.Connection) -> None:
    """Chart 2: top 10 product lines by revenue after excluding DOT, POST and M codes."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    excluded_sql = ", ".join(f"'{code}'" for code in sorted(EXCLUDED_STOCK_CODES))
    query = f"""
        SELECT
            TRIM(CAST(StockCode AS TEXT)) AS stock_code,
            COALESCE(NULLIF(TRIM(Description), ''), '(No description)') AS description,
            SUM(Revenue) AS revenue,
            SUM(Quantity) AS units_sold,
            COUNT(DISTINCT InvoiceNo) AS order_count
        FROM sales
        WHERE UPPER(TRIM(CAST(StockCode AS TEXT))) NOT IN ({excluded_sql})
        GROUP BY TRIM(CAST(StockCode AS TEXT)), COALESCE(NULLIF(TRIM(Description), ''), '(No description)')
        ORDER BY revenue DESC
    """
    products = pd.read_sql_query(query, conn)
    if products.empty:
        raise ValueError("No product rows left after filtering. Check the sales table and filters.")

    top10 = products.head(10).copy()
    overall_revenue = pd.read_sql_query("SELECT SUM(Revenue) AS total_revenue FROM sales", conn).iloc[0]["total_revenue"]
    top10_revenue = float(top10["revenue"].sum())
    top10_share = top10_revenue / float(overall_revenue) * 100 if overall_revenue else np.nan

    # Labels include stock code to distinguish products with similar descriptions.
    top10["label"] = top10.apply(
        lambda r: f"{r['stock_code']} | {str(r['description'])[:34]}", axis=1
    )
    plot_df = top10.sort_values("revenue", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7.2))
    bars = ax.barh(plot_df["label"], plot_df["revenue"])
    ax.bar_label(bars, labels=[money(v) for v in plot_df["revenue"]], padding=3, fontsize=8)
    ax.set_title("Top 10 Product Lines by Revenue", fontsize=16, pad=16)
    ax.set_xlabel("Revenue (GBP; before costs)")
    ax.set_ylabel("Product code and description")
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    ax.set_xlim(0, float(plot_df["revenue"].max()) * 1.24)
    fig.text(
        0.01, 0.01,
        f"Method: re-rank all product lines after excluding stock codes DOT, POST and M. Top 10 = {money(top10_revenue, 2)} ({top10_share:.2f}% of total sales revenue). Revenue is not profit.",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    out = FIG_DIR / "top10_product_revenue.png"
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")

    print("\nFiltered and re-ranked product Top 10:")
    print(top10[["stock_code", "description", "revenue", "units_sold", "order_count"]].round(2).to_string(index=False))
    print(f"Top 10 revenue: {top10_revenue:,.2f} GBP")
    print(f"Share of all sales revenue: {top10_share:.2f}%")
    print("Expected from your current summary: 966,985.94 GBP and approximately 9.09%.")
    if abs(top10_revenue - 966_985.94) > 0.02:
        print("WARNING: result differs from the provided final total. Check the database version, cleaning rules, exclusion filter and grouping keys.")


def make_customer_repeat_chart(conn: sqlite3.Connection) -> None:
    """Chart 3: one-time vs repeat customer share and their share of identified-customer revenue."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    # Build customer metrics from the clean sales table to avoid relying on a partial Top-N export.
    customer_query = """
        SELECT
            TRIM(CAST(CustomerID AS TEXT)) AS customer_id,
            InvoiceNo,
            Revenue
        FROM sales
        WHERE CustomerID IS NOT NULL
          AND TRIM(CAST(CustomerID AS TEXT)) <> ''
    """
    customer_lines = pd.read_sql_query(customer_query, conn)
    if customer_lines.empty:
        raise ValueError("No identified customer records found in sales table.")

    customers = customer_lines.groupby("customer_id", as_index=False).agg(
        order_count=("InvoiceNo", "nunique"),
        monetary_revenue=("Revenue", "sum"),
    )
    customers["customer_type"] = np.where(
        customers["order_count"] == 1,
        "One-time customer",
        "Repeat customer",
    )
    summary = customers.groupby("customer_type", as_index=False).agg(
        customer_count=("customer_id", "nunique"),
        revenue=("monetary_revenue", "sum"),
    )
    total_customers = int(customers["customer_id"].nunique())
    identified_revenue = float(customers["monetary_revenue"].sum())
    summary["customer_share_pct"] = summary["customer_count"] / total_customers * 100
    summary["identified_revenue_share_pct"] = summary["revenue"] / identified_revenue * 100

    order = ["One-time customer", "Repeat customer"]
    summary["customer_type"] = pd.Categorical(summary["customer_type"], categories=order, ordered=True)
    summary = summary.sort_values("customer_type")

    categories = [str(x) for x in summary["customer_type"]]
    customer_shares = summary["customer_share_pct"].to_numpy()
    revenue_shares = summary["identified_revenue_share_pct"].to_numpy()
    x = np.arange(len(categories))
    width = 0.34

    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    bars1 = ax.bar(x - width / 2, customer_shares, width, label="Share of identified customers")
    bars2 = ax.bar(x + width / 2, revenue_shares, width, label="Share of identified-customer revenue")
    ax.bar_label(bars1, labels=[f"{v:.2f}%" for v in customer_shares], padding=3, fontsize=9)
    ax.bar_label(bars2, labels=[f"{v:.2f}%" for v in revenue_shares], padding=3, fontsize=9)
    ax.set_title("One-time vs Repeat Customers", fontsize=16, pad=16)
    ax.set_ylabel("Share (%)")
    ax.set_xticks(x, categories)
    ax.set_ylim(0, max(float(max(customer_shares)), float(max(revenue_shares))) * 1.22)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=1)
    fig.text(
        0.01, 0.01,
        f"Repeat = at least 2 distinct invoices during the dataset period. Revenue share denominator: identified customers only ({money(identified_revenue, 2)}). This is not monthly retention.",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.09, 1, 1))
    out = FIG_DIR / "customer_repeat_analysis.png"
    fig.savefig(out, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out}")

    print("\nCustomer repeat summary:")
    print(summary[["customer_type", "customer_count", "customer_share_pct", "revenue", "identified_revenue_share_pct"]].round(2).to_string(index=False))
    print(f"Identified customers: {total_customers:,}")
    print(f"Identified-customer revenue: {identified_revenue:,.2f} GBP")


def main() -> None:
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}", file=sys.stderr)
        print("First run `python src/analyze.py` from the project root to create outputs/retail_analysis.db.", file=sys.stderr)
        raise SystemExit(1)

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        make_sales_trend(conn)
        make_product_top10(conn)
        make_customer_repeat_chart(conn)

    print("\nDone. Three charts saved under:")
    print(FIG_DIR)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
