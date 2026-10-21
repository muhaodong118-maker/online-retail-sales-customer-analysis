# Start Here — Tonight's 0-to-1 Checklist

## Step 1 — Download data
1. Open https://archive.ics.uci.edu/dataset/352/online-retail
2. Download `Online Retail.xlsx`.
3. Put the file in this project's `data/` folder. Keep the filename `Online Retail.xlsx`.

## Step 2 — Install requirements
Open a terminal in this folder and run:

```bash
pip install -r requirements.txt
```

## Step 3 — Run analysis

```bash
python src/analyze.py
```

## Step 4 — Inspect outputs
- `outputs/tables/data_quality_summary.csv`
- `outputs/tables/monthly_sales.csv`
- `outputs/tables/top_products.csv`
- `outputs/tables/top_countries.csv`
- `outputs/tables/customer_rfm.csv`
- `outputs/figures/monthly_revenue.png`
- `outputs/figures/top_products.png`
- `outputs/figures/top_countries.png`
- `outputs/retail_analysis.db`
- `outputs/tables/sql_q1_result.csv` through `sql_q5_result.csv`

## Step 5 — Run SQL
Run all SQL queries and export their results with:

```bash
python src/run_sql_queries.py
```

You can also open `outputs/retail_analysis.db` in a SQLite viewer and inspect `sql/queries.sql`.

## Step 6 — Finish the portfolio story
1. Copy the real values from the tables into README.
2. Record 2–3 findings that are supported by charts/tables.
3. Write one practical recommendation per finding.
4. Add your own contribution accurately; distinguish your work from any team work.
5. Add 2–3 chart screenshots to your Portfolio PPT.

Do not invent numbers or business findings. If a query or chart fails, fix the process before writing conclusions.
