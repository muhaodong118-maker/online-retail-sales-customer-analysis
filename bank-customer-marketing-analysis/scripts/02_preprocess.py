from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import (  # noqa: E402
    PROCESSED_PATH,
    ensure_directories,
    load_raw_data,
    clean_and_engineer,
)


def main() -> None:
    ensure_directories()
    raw = load_raw_data()
    processed = clean_and_engineer(raw)
    processed.to_csv(PROCESSED_PATH, index=False, encoding="utf-8-sig")
    print(f"原始记录数：{len(raw):,}")
    print(f"清洗后记录数：{len(processed):,}")
    print(f"新增字段：age_group, balance_segment, campaign_group, previous_contacted, target")
    print(f"已保存：{PROCESSED_PATH}")
    print("本步骤不删除重复行、不删除负余额、不将 unknown 替换为众数；所有规则需在 README 中解释。")


if __name__ == "__main__":
    main()
