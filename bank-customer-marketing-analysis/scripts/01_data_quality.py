from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd  # noqa: E402
from src.common import RAW_PATH, TABLE_DIR, ensure_directories, load_raw_data  # noqa: E402


def main() -> None:
    ensure_directories()
    df = load_raw_data()

    unknown_rows = []
    for col in df.select_dtypes(include=["object", "string"]).columns:
        values = df[col].astype("string").str.strip().str.lower()
        unknown_rows.append({
            "field": col,
            "unknown_records": int(values.eq("unknown").sum()),
            "blank_records": int(values.eq("").sum()),
            "missing_records": int(df[col].isna().sum()),
            "unique_values_including_unknown": int(df[col].nunique(dropna=False)),
        })
    unknown_df = pd.DataFrame(unknown_rows).sort_values("unknown_records", ascending=False)

    field_profile = pd.DataFrame({
        "field": df.columns,
        "dtype": [str(df[col].dtype) for col in df.columns],
        "non_null_records": [int(df[col].notna().sum()) for col in df.columns],
        "missing_records": [int(df[col].isna().sum()) for col in df.columns],
        "unique_values": [int(df[col].nunique(dropna=False)) for col in df.columns],
    })
    if "y" in df.columns:
        field_profile.loc[field_profile["field"].eq("y"), "target_class"] = "yes/no target"

    summary = {
        "source_file": str(RAW_PATH.relative_to(ROOT)),
        "row_count": int(len(df)),
        "column_count": int(df.shape[1]),
        "exact_duplicate_rows": int(df.duplicated().sum()),
        "total_missing_cells": int(df.isna().sum().sum()),
        "target_yes_records": int(df["y"].astype(str).str.lower().eq("yes").sum()),
        "target_no_records": int(df["y"].astype(str).str.lower().eq("no").sum()),
        "target_conversion_rate_pct": round(float(df["y"].astype(str).str.lower().eq("yes").mean() * 100), 2),
        "interpretation": "A row is a marketing record, not a guaranteed unique customer; the dataset has no customer ID.",
    }

    (TABLE_DIR / "data_quality_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    unknown_df.to_csv(TABLE_DIR / "data_quality_categorical_profile.csv", index=False, encoding="utf-8-sig")
    field_profile.to_csv(TABLE_DIR / "data_quality_field_profile.csv", index=False, encoding="utf-8-sig")

    print("=== 数据质量检查 ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\n已输出：{TABLE_DIR / 'data_quality_summary.json'}")
    print(f"已输出：{TABLE_DIR / 'data_quality_categorical_profile.csv'}")
    print(f"已输出：{TABLE_DIR / 'data_quality_field_profile.csv'}")
    print("说明：unknown 保留为明确类别；是否去重需要根据业务含义判断，不在此处自动删除。")


if __name__ == "__main__":
    main()
