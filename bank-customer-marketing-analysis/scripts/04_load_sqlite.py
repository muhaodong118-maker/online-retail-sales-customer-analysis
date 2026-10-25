from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd  # noqa: E402
from src.common import DB_PATH, PROCESSED_PATH, ensure_directories, load_raw_data, clean_and_engineer  # noqa: E402


def main() -> None:
    ensure_directories()
    if PROCESSED_PATH.exists():
        df = pd.read_csv(PROCESSED_PATH, encoding="utf-8-sig")
    else:
        df = clean_and_engineer(load_raw_data())
        df.to_csv(PROCESSED_PATH, index=False, encoding="utf-8-sig")

    # SQLite stores a locally generated analytical table; raw CSV remains unchanged.
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("bank_marketing", conn, if_exists="replace", index=False)
        row_count = conn.execute("SELECT COUNT(*) FROM bank_marketing").fetchone()[0]
        column_count = conn.execute("PRAGMA table_info(bank_marketing)").fetchall()
    print(f"已创建数据库：{DB_PATH}")
    print(f"表名：bank_marketing | 记录数：{row_count:,} | 字段数：{len(column_count)}")
    print("可使用 DB Browser for SQLite 打开数据库，或运行 scripts/05_run_sql_queries.py 导出 SQL 结果。")


if __name__ == "__main__":
    main()
