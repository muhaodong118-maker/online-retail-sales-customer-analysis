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
## 6. Results & Key Findings

### 6.1 Sales Trend Analysis

- Total revenue: **£10,642,110.80**
- Total orders: **19,960**
- Identifiable customers: **4,338**
- Total units sold: **5,572,420**
- Average order value (AOV): **£533.17**

November 2011 was the highest-revenue complete month, reaching **£1,503,866.78**, up **30.6% month over month**. Order volume increased by 35.7%, while identifiable customers increased by 22.0%. AOV decreased by 3.8%.

**Business insight:** The revenue increase coincided with growth in order volume and identifiable customers rather than an increase in average order value. December 2011 only contains data through December 9 and should not be directly compared with full months.

### 6.2 Product Performance Analysis

After excluding the non-merchandise stock codes `DOT`, `POST`, and `M`, the top 10 products were recalculated by revenue.

- Top 10 product revenue: **£966,985.94**
- Share of total revenue: **9.09%**

Sales volume and revenue rankings differed across products. Some products sold in high quantities but generated relatively less revenue, while some high-revenue products were associated with a small number of orders.

**Business insight:** Product performance should be assessed using revenue, units sold, and order coverage together. Products with unusually high quantities but very few orders should be reviewed separately.

### 6.3 Customer Behavior Analysis

Among 4,338 identifiable customers:

- Repeat customers: **2,845 (65.58%)**
- One-time customers: **1,493 (34.42%)**
- Revenue from repeat customers: **£8,273,219.33**
- Repeat-customer share of identifiable-customer revenue: **93.09%**

The top 10 customers contributed **£1,537,659.21**, equivalent to approximately 14.45% of total revenue.

**Business insight:** Repeat customers represent the main revenue base among identifiable customers. Customer retention, targeted product recommendations, and carefully designed reactivation tests for high-value inactive customers are potential follow-up strategies.

### 6.4 Business Recommendations

1. Investigate the products and customer groups contributing most to peak-month revenue before making inventory and marketing decisions.
2. Compare revenue, quantity, and order coverage when evaluating product performance.
3. Distinguish frequent high-value customers from high-value one-time or inactive customers when designing customer-retention strategies.

### 6.5 Limitations

- The dataset represents one retailer during a historical period; the findings should not be generalized to all retailers.
- December 2011 is an incomplete month.
- Product costs are unavailable, so revenue cannot be interpreted as profit.
- Customer IDs are missing for some transactions. Customer-level metrics therefore use identifiable-customer records where applicable.
- Repeat-customer status is defined by the number of distinct invoices during the observation period and is not equivalent to monthly retention.
- Business recommendations are hypotheses for further testing, not evidence of measured marketing impact.

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
