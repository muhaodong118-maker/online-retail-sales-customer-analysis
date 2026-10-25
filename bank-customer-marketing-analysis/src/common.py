from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
CHART_DIR = OUTPUT_DIR / "charts"
SQL_RESULT_DIR = OUTPUT_DIR / "sql_results"
DB_PATH = OUTPUT_DIR / "bank_marketing.db"
RAW_PATH = RAW_DIR / "bank-full.csv"
PROCESSED_PATH = PROCESSED_DIR / "bank_marketing_clean.csv"

REQUIRED_COLUMNS = [
    "age", "job", "marital", "education", "default", "balance", "housing",
    "loan", "contact", "day", "month", "duration", "campaign", "pdays",
    "previous", "poutcome", "y",
]
NUMERIC_COLUMNS = ["age", "balance", "day", "duration", "campaign", "pdays", "previous"]
CATEGORICAL_COLUMNS = [
    "job", "marital", "education", "default", "housing", "loan", "contact",
    "month", "poutcome", "y",
]


def ensure_directories() -> None:
    for path in [RAW_DIR, PROCESSED_DIR, OUTPUT_DIR, TABLE_DIR, CHART_DIR, SQL_RESULT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def load_raw_data(path: Path | str = RAW_PATH) -> pd.DataFrame:
    """Read the original UCI bank-full.csv file (semicolon-delimited)."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(
            f"找不到原始数据：{source}\n请先运行：python scripts/download_data.py"
        )
    df = pd.read_csv(source, sep=";", encoding="utf-8-sig")
    df.columns = [str(col).strip().lower() for col in df.columns]
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"数据字段不完整，缺少字段：{missing}。请确认使用的是 UCI bank-full.csv。")
    return df


def clean_and_engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize data types and add transparent, rule-based analysis fields.

    'unknown' remains an explicit category instead of being silently imputed.
    Negative balance is retained because it can be a valid account condition.
    pdays < 0 is treated as no previous campaign contact in the source data.
    """
    out = df.copy()
    out.columns = [str(col).strip().lower() for col in out.columns]
    missing = sorted(set(REQUIRED_COLUMNS) - set(out.columns))
    if missing:
        raise ValueError(f"缺少必要字段：{missing}")

    for col in CATEGORICAL_COLUMNS:
        out[col] = out[col].astype("string").str.strip().str.lower()
        out[col] = out[col].fillna("unknown").replace("", "unknown")

    for col in NUMERIC_COLUMNS:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    # Preserve y for readability and add a numeric helper for calculations.
    out["target"] = out["y"].map({"yes": 1, "no": 0})
    if out["target"].isna().any():
        unexpected = sorted(out.loc[out["target"].isna(), "y"].astype(str).unique().tolist())
        raise ValueError(f"目标字段 y 出现非预期取值：{unexpected}；预期取值只有 yes/no。")
    out["target"] = out["target"].astype("int8")

    out["age_group"] = pd.cut(
        out["age"],
        bins=[0, 25, 35, 45, 55, 65, np.inf],
        labels=["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
        right=False,
    ).astype("string")
    out["age_group"] = out["age_group"].fillna("unknown")

    out["balance_segment"] = pd.cut(
        out["balance"],
        bins=[-np.inf, 0, 1000, 5000, np.inf],
        labels=["Negative balance", "0-999", "1,000-4,999", "5,000+"],
        right=False,
    ).astype("string")
    out["balance_segment"] = out["balance_segment"].fillna("unknown")

    out["campaign_group"] = pd.cut(
        out["campaign"],
        bins=[0, 1, 2, 3, 5, np.inf],
        labels=["1 contact", "2 contacts", "3 contacts", "4-5 contacts", "6+ contacts"],
        right=True,
    ).astype("string")
    out["campaign_group"] = out["campaign_group"].fillna("unknown")

    out["previous_contacted"] = np.where(
        out["pdays"] < 0,
        "No previous contact",
        "Previously contacted",
    )

    # Keep duration in the analytical table for post-call description only.
    # Do not use it for any pre-call targeting decision: it is only known after the call.
    return out


def conversion_summary(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Return record counts and conversion rate for each group."""
    if group_col not in df.columns:
        raise KeyError(f"分组字段不存在：{group_col}")
    grouped = (
        df.groupby(group_col, dropna=False, observed=False)
        .agg(
            marketing_records=("target", "size"),
            subscribed_records=("target", "sum"),
            conversion_rate=("target", "mean"),
        )
        .reset_index()
        .rename(columns={group_col: "segment"})
    )
    grouped["not_subscribed_records"] = grouped["marketing_records"] - grouped["subscribed_records"]
    grouped["conversion_rate_pct"] = (grouped["conversion_rate"] * 100).round(2)
    grouped = grouped.drop(columns=["conversion_rate"])
    return grouped.sort_values("conversion_rate_pct", ascending=False, na_position="last")


def require_processed_data() -> pd.DataFrame:
    if not PROCESSED_PATH.exists():
        raise FileNotFoundError(
            f"找不到清洗后的数据：{PROCESSED_PATH}\n请先运行：python run_pipeline.py"
        )
    df = pd.read_csv(PROCESSED_PATH, encoding="utf-8-sig")
    if "target" not in df.columns:
        raise ValueError("清洗数据缺少 target 字段，请重新运行 python run_pipeline.py")
    return df
