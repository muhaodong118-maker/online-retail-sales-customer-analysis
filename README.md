# Online Retail Sales & Customer Analytics

> A portfolio project for Data Analyst Internship applications. The project uses SQL and Python to analyze retail transactions, sales trends, product performance, and customer purchase behavior.

## 1. Business Questions

1. How did revenue and order volume change over time?
2. Which products generated the most revenue and sales volume?
3. Which countries contributed most to sales?
4. Which customers are most valuable based on recency, frequency, and monetary value (RFM)?
5. What practical actions could the business consider based on the analysis?

## 2. Dataset

- Source: [UCI Machine Learning Repository — Online Retail](https://archive.ics.uci.edu/dataset/352/online-retail)
- Original period: 2010-12-01 to 2011-12-09
- Original rows: 541,909
- Fields include invoice number, stock code, product description, quantity, invoice date, unit price, customer ID, and country.
- License: CC BY 4.0. Please credit the UCI source when sharing this project.

Download `Online Retail.xlsx` from the UCI page and place it in the `data/` directory. Do not commit the raw file to GitHub.

## 3. Tools

- Python: pandas, NumPy, Matplotlib
- SQL: SQLite
- Data source: UCI Online Retail

## 4. Analysis Workflow

1. Inspect data types, missing values, duplicates, cancellations, and non-positive quantities/prices.
2. Define a transparent sales-analysis dataset and document filters.
3. Use SQL for monthly trends, product/country ranking, and customer RFM metrics.
4. Use Python to create summary tables and visualizations.
5. Translate the results into business observations and recommendations.

## 5. How to Run

```bash
pip install -r requirements.txt
python src/analyze.py
```

The script expects `data/Online Retail.xlsx` (or `data/online_retail.xlsx`). It generates summary tables, visualizations, and a SQLite database under `outputs/`.

Run all SQL queries and export query results: `python src/run_sql_queries.py`. The queries are also available in `sql/queries.sql` and can be reviewed in a SQLite viewer against the generated `sales` table.

## 6. Results

> TODO: Replace this section after running the analysis. Do not publish placeholder metrics.

- Revenue trend: TODO
- Top products: TODO
- Leading markets: TODO
- Customer behavior / RFM observations: TODO
- Business recommendations: TODO

## 7. Data Cleaning Decisions

The script creates a primary sales-analysis table by removing exact duplicate rows, invoice numbers beginning with `C` (cancellations), rows with non-positive quantities, and rows with non-positive unit prices. This filter is for the primary positive-sales analysis, not a complete accounting treatment of returns. Customer-level analysis excludes records without a customer ID; sales summaries can still include transactions without customer IDs.

Review the data-quality summary produced by the script before interpreting results. These are analytical choices and should be explained in the final report.

## 8. Limitations

- The dataset is historical and covers one retailer, so findings should not be generalized to all e-commerce businesses.
- Missing customer IDs limit customer-level analysis.
- Revenue is calculated as `Quantity * UnitPrice`; the dataset does not provide product cost, so revenue should not be described as profit.
- The dataset contains cancellations/returns; the main sales analysis applies the documented positive-sales filter.

## 9. Attribution

Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33. Licensed under CC BY 4.0.
