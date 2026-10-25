from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from src.common import (  # noqa: E402
    CHART_DIR, TABLE_DIR, PROCESSED_PATH, ensure_directories,
    load_raw_data, clean_and_engineer, conversion_summary,
)

GROUP_FIELDS = [
    "job", "marital", "education", "default", "housing", "loan", "contact",
    "month", "poutcome", "age_group", "balance_segment", "campaign_group",
    "previous_contacted",
]


def set_chart_style() -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.size"] = 11
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 11


def save_bar_chart(summary: pd.DataFrame, title: str, xlabel: str, output: Path,
                   category_order: list[str] | None = None, min_records: int = 1,
                   rate_column: str = "conversion_rate_pct") -> None:
    data = summary.loc[summary["marketing_records"] >= min_records].copy()
    if category_order:
        ordered = {value: i for i, value in enumerate(category_order)}
        data["_order"] = data["segment"].astype(str).map(ordered).fillna(999)
        data = data.sort_values("_order")
    else:
        data = data.sort_values(rate_column, ascending=True)
    if data.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 5.5), constrained_layout=True)
    bars = ax.barh(data["segment"].astype(str), data[rate_column], color="#2864F0", alpha=0.88)
    ax.set_title(title, loc="left", pad=12, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    ax.grid(axis="x", linestyle="--", alpha=0.25)
    ax.set_axisbelow(True)
    max_rate = max(float(data[rate_column].max()), 1.0)
    ax.set_xlim(0, max_rate * 1.25)
    for bar, count, rate in zip(bars, data["marketing_records"], data[rate_column]):
        ax.text(bar.get_width() + max_rate * 0.015, bar.get_y() + bar.get_height() / 2,
                f"{rate:.1f}%  (n={count:,})", va="center", fontsize=9, color="#26364A")
    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#D6DEE8")
    fig.savefig(output, dpi=180, facecolor="white")
    plt.close(fig)


def main() -> None:
    ensure_directories()
    if PROCESSED_PATH.exists():
        df = pd.read_csv(PROCESSED_PATH, encoding="utf-8-sig")
    else:
        df = clean_and_engineer(load_raw_data())
        df.to_csv(PROCESSED_PATH, index=False, encoding="utf-8-sig")

    total = int(len(df))
    subscribed = int(df["target"].sum())
    summary_rows = [
        {"metric": "marketing_records", "value": total, "definition": "Number of rows in the dataset; not a distinct-customer count."},
        {"metric": "subscribed_records", "value": subscribed, "definition": "Rows with y = yes."},
        {"metric": "not_subscribed_records", "value": total - subscribed, "definition": "Rows with y = no."},
        {"metric": "conversion_rate_pct", "value": round(subscribed / total * 100, 2) if total else np.nan, "definition": "Subscribed records / all marketing records."},
        {"metric": "mean_age", "value": round(float(df["age"].mean()), 2), "definition": "Mean age across records."},
        {"metric": "median_balance", "value": round(float(df["balance"].median()), 2), "definition": "Median account balance; currency units follow the dataset documentation."},
        {"metric": "mean_campaign_contacts", "value": round(float(df["campaign"].mean()), 2), "definition": "Mean contacts during this campaign for a record."},
        {"metric": "previously_contacted_records_pct", "value": round(float(df["previous_contacted"].eq("Previously contacted").mean() * 100), 2), "definition": "Share of rows with pdays >= 0."},
    ]
    pd.DataFrame(summary_rows).to_csv(TABLE_DIR / "overall_kpis.csv", index=False, encoding="utf-8-sig")

    summaries = {}
    for field in GROUP_FIELDS:
        result = conversion_summary(df, field)
        summaries[field] = result
        result.to_csv(TABLE_DIR / f"conversion_by_{field}.csv", index=False, encoding="utf-8-sig")

    set_chart_style()
    save_bar_chart(summaries["job"], "Conversion Rate by Job", "Conversion rate (%)",
                   CHART_DIR / "01_conversion_by_job.png", min_records=100)
    save_bar_chart(summaries["age_group"], "Conversion Rate by Age Group", "Conversion rate (%)",
                   CHART_DIR / "02_conversion_by_age_group.png",
                   category_order=["18-24", "25-34", "35-44", "45-54", "55-64", "65+", "unknown"])
    save_bar_chart(summaries["contact"], "Conversion Rate by Contact Channel", "Conversion rate (%)",
                   CHART_DIR / "03_conversion_by_contact.png")
    save_bar_chart(summaries["campaign_group"], "Conversion Rate by Campaign Contact Frequency", "Conversion rate (%)",
                   CHART_DIR / "04_conversion_by_campaign_frequency.png",
                   category_order=["1 contact", "2 contacts", "3 contacts", "4-5 contacts", "6+ contacts", "unknown"])
    save_bar_chart(summaries["poutcome"], "Conversion Rate by Previous Campaign Outcome", "Conversion rate (%)",
                   CHART_DIR / "05_conversion_by_previous_outcome.png")
    save_bar_chart(summaries["balance_segment"], "Conversion Rate by Balance Segment", "Conversion rate (%)",
                   CHART_DIR / "06_conversion_by_balance_segment.png",
                   category_order=["Negative balance", "0-999", "1,000-4,999", "5,000+", "unknown"])

    print("分析完成。核心输出：")
    print(f"- KPI 表：{TABLE_DIR / 'overall_kpis.csv'}")
    print(f"- 分组结果：{TABLE_DIR / 'conversion_by_*.csv'}")
    print(f"- 图表：{CHART_DIR}")
    print("提示：分组转化率描述相关性，不代表该属性或联络方式导致转化；小样本组应谨慎解释。")


if __name__ == "__main__":
    main()
