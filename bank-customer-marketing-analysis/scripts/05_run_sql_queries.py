from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import DB_PATH, SQL_RESULT_DIR, ensure_directories  # noqa: E402


def main() -> None:
    ensure_directories()
    if not DB_PATH.exists():
        raise FileNotFoundError("SQLite 数据库不存在，请先运行 python scripts/04_load_sqlite.py")
    sql_files = sorted((ROOT / "sql").glob("*.sql"))
    if not sql_files:
        raise FileNotFoundError("sql/ 目录下没有找到 .sql 查询文件")

    with sqlite3.connect(DB_PATH) as conn:
        for sql_file in sql_files:
            query = sql_file.read_text(encoding="utf-8").strip()
            if not query or query.startswith("-- TODO"):
                continue
            try:
                result = __import__("pandas").read_sql_query(query, conn)
            except Exception as exc:
                raise RuntimeError(f"SQL 执行失败：{sql_file.name}\n{exc}") from exc
            out_path = SQL_RESULT_DIR / f"{sql_file.stem}.csv"
            result.to_csv(out_path, index=False, encoding="utf-8-sig")
            print(f"{sql_file.name} -> {out_path.relative_to(ROOT)} ({len(result):,} rows)")

    print("SQL 查询结果导出完成。建议抽查 CSV，并与 Python 统计口径核对。")


if __name__ == "__main__":
    main()
