-- The older bank-full version does not provide a full calendar date; month comparisons are descriptive.
SELECT
    month,
    COUNT(*) AS marketing_records,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) AS subscribed_records,
    ROUND(100.0 * AVG(target), 2) AS conversion_rate_pct
FROM bank_marketing
GROUP BY month
ORDER BY CASE lower(month)
    WHEN 'jan' THEN 1 WHEN 'feb' THEN 2 WHEN 'mar' THEN 3 WHEN 'apr' THEN 4
    WHEN 'may' THEN 5 WHEN 'jun' THEN 6 WHEN 'jul' THEN 7 WHEN 'aug' THEN 8
    WHEN 'sep' THEN 9 WHEN 'oct' THEN 10 WHEN 'nov' THEN 11 WHEN 'dec' THEN 12
    ELSE 99 END;
