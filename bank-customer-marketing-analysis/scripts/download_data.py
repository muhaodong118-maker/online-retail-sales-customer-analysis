from __future__ import annotations

import io
import urllib.request
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common import RAW_DIR, ensure_directories  # noqa: E402

UCI_ZIP_URL = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip"


def find_member(names: list[str], filename: str) -> str | None:
    target = filename.lower()
    for name in names:
        if Path(name).name.lower() == target:
            return name
    return None


def main() -> None:
    ensure_directories()
    destination = RAW_DIR / "bank-full.csv"
    if destination.exists():
        answer = input(f"已存在 {destination}. 是否重新下载覆盖？(y/N): ").strip().lower()
        if answer != "y":
            print("保留现有数据，未重新下载。")
            return

    request = urllib.request.Request(
        UCI_ZIP_URL,
        headers={"User-Agent": "Mozilla/5.0 bank-customer-marketing-analysis/1.0"},
    )
    print("正在从 UCI 官方数据集页面下载 Bank Marketing 数据……")
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read()

    csv_bytes = None
    names_bytes = None
    with zipfile.ZipFile(io.BytesIO(content)) as outer:
        outer_names = outer.namelist()
        direct_csv = find_member(outer_names, "bank-full.csv")
        if direct_csv:
            csv_bytes = outer.read(direct_csv)
        else:
            inner_zip_name = find_member(outer_names, "bank.zip")
            if not inner_zip_name:
                raise RuntimeError(f"下载包中没有找到 bank.zip 或 bank-full.csv：{outer_names}")
            with zipfile.ZipFile(io.BytesIO(outer.read(inner_zip_name))) as inner:
                inner_names = inner.namelist()
                csv_name = find_member(inner_names, "bank-full.csv")
                if not csv_name:
                    raise RuntimeError("bank.zip 中没有找到 bank-full.csv")
                csv_bytes = inner.read(csv_name)
                names_name = find_member(inner_names, "bank-names.txt")
                if names_name:
                    names_bytes = inner.read(names_name)
        # On some archives the data description can be at the outer level.
        if names_bytes is None:
            description_name = find_member(outer_names, "bank-names.txt")
            if description_name:
                names_bytes = outer.read(description_name)

    if not csv_bytes:
        raise RuntimeError("没有成功提取 bank-full.csv")
    destination.write_bytes(csv_bytes)
    if names_bytes:
        (RAW_DIR / "bank-names.txt").write_bytes(names_bytes)

    print(f"已保存原始数据：{destination}")
    print(f"文件大小：{destination.stat().st_size:,} bytes")
    print("数据以分号分隔，后续脚本会按 sep=';' 读取。")
    print("注意：首次使用需要网络连接 UCI 官网；也可手动下载并放到 data/raw/bank-full.csv。")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(
            f"数据下载失败：{exc}\n请检查网络，或访问 https://archive.ics.uci.edu/dataset/222/bank+marketing 手动下载。"
        ) from exc
