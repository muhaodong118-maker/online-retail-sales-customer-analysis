-- Online Retail Sales & Customer Analytics
-- Run against outputs/retail_analysis.db, table: sales
-- Revenue is defined in the Python pipeline as Quantity * UnitPrice.

-- Q1. Monthly revenue, order count, and distinct identified customers
SELECT
    strftime('%Y-%m', InvoiceDate) AS month,
    ROUND(SUM(Revenue), 2) AS revenue,
    COUNT(DISTINCT InvoiceNo) AS order_count,
    COUNT(DISTINCT CustomerID) AS identified_customers
FROM sales
GROUP BY strftime('%Y-%m', InvoiceDate)
ORDER BY month;

-- Q2. Month-over-month revenue change using a window function
WITH monthly AS (
    SELECT
        strftime('%Y-%m', InvoiceDate) AS month,
        SUM(Revenue) AS revenue
    FROM sales
    GROUP BY strftime('%Y-%m', InvoiceDate)
)
SELECT
    month,
    ROUND(revenue, 2) AS revenue,
    ROUND(LAG(revenue) OVER (ORDER BY month), 2) AS previous_month_revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
        / NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
        2
    ) AS mom_growth_pct
FROM monthly
ORDER BY month;

-- Q3. Top 10 products by revenue
SELECT
    StockCode,
    Description,
    ROUND(SUM(Revenue), 2) AS revenue,
    SUM(Quantity) AS units_sold,
    COUNT(DISTINCT InvoiceNo) AS order_count
FROM sales
GROUP BY StockCode, Description
ORDER BY revenue DESC
LIMIT 10;

-- Q4. Country-level performance
SELECT
    Country,
    ROUND(SUM(Revenue), 2) AS revenue,
    COUNT(DISTINCT InvoiceNo) AS order_count,
    COUNT(DISTINCT CustomerID) AS identified_customers
FROM sales
GROUP BY Country
ORDER BY revenue DESC
LIMIT 10;

-- Q5. Customer RFM metrics
-- Snapshot date = one day after the latest sales date in the cleaned dataset.
WITH snapshot AS (
    SELECT date(MAX(InvoiceDate), '+1 day') AS snapshot_date
    FROM sales
),
customer_rfm AS (
    SELECT
        CustomerID,
        CAST(julianday((SELECT snapshot_date FROM snapshot)) - julianday(MAX(InvoiceDate)) AS INTEGER) AS Recency_Days,
        COUNT(DISTINCT InvoiceNo) AS Frequency_Orders,
        ROUND(SUM(Revenue), 2) AS Monetary_Revenue
    FROM sales
    WHERE CustomerID IS NOT NULL AND TRIM(CustomerID) <> ''
    GROUP BY CustomerID
)
SELECT *
FROM customer_rfm
ORDER BY Monetary_Revenue DESC
LIMIT 50;
