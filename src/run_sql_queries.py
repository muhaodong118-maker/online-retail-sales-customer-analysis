from pathlib import Path
import re
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "outputs" / "retail_analysis.db"
SQL_PATH = ROOT / "sql" / "queries.sql"
OUT_DIR = ROOT / "outputs" / "tables"


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError("SQLite database not found. Run `python src/analyze.py` first.")
    sql_text = SQL_PATH.read_text(encoding="utf-8")
    # Remove line comments before splitting the read-only SQL statements.
    sql_text = re.sub(r"--[^\n]*", "", sql_text)
    statements = [part.strip() for part in sql_text.split(";") if part.strip()]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        for i, statement in enumerate(statements, start=1):
            frame = pd.read_sql_query(statement, conn)
            output = OUT_DIR / f"sql_q{i}_result.csv"
            frame.to_csv(output, index=False)
            print(f"Q{i}: {len(frame):,} rows -> {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
