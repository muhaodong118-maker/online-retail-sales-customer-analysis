from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    "scripts/01_data_quality.py",
    "scripts/02_preprocess.py",
    "scripts/03_analysis.py",
    "scripts/04_load_sqlite.py",
    "scripts/05_run_sql_queries.py",
]


def main() -> None:
    raw_path = ROOT / "data" / "raw" / "bank-full.csv"
    if not raw_path.exists():
        print("没有找到原始数据。请先运行：python scripts/download_data.py")
        raise SystemExit(1)
    for script in SCRIPTS:
        print(f"\n{'=' * 12} Running {script} {'=' * 12}")
        subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, check=True)
    print("\nPipeline 完成。现在可以运行：streamlit run app.py")


if __name__ == "__main__":
    main()
