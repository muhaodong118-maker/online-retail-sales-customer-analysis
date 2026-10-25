# GitHub 上传清单

## 建议上传

提交项目代码、SQL、README、字段字典、分析计划和测试文件。不要提交 `.venv/`、本地 SQLite 数据库、原始 CSV、清洗 CSV 或临时文件。

## 首次提交前检查

1. 确认根目录有 `README.md`、`requirements.txt`、`run_pipeline.py` 和 `app.py`。
2. 确认 `sql/` 中所有查询可读，`scripts/` 中的脚本有明确输入输出。
3. 本地执行 `python -m unittest discover -s tests -v`。
4. 下载数据后运行 `python run_pipeline.py`，检查 `outputs/tables/`、`outputs/charts/`、`outputs/sql_results/`。
5. 运行 `streamlit run app.py` 检查筛选器和图表。
6. 在 README 中引用 UCI 数据集和论文，说明数据范围及分析限制。

## 网页上传方式

进入 GitHub → New repository，仓库名填 `bank-customer-marketing-analysis`，可见性按求职需要选择 Public。创建后使用 Add file → Upload files 上传项目目录中的文件夹/文件，或本地 Git 初始化后推送。GitHub 网页上传时可分批上传；不要上传 raw/processed 下的数据 CSV。
