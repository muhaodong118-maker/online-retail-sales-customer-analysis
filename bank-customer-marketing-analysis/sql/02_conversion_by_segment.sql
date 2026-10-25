-- Compare customer attribute segments; treat these as associations, not causal effects.
SELECT 'job' AS dimension, job AS segment,
       COUNT(*) AS marketing_records,
       SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) AS subscribed_records,
       ROUND(100.0 * AVG(target), 2) AS conversion_rate_pct
FROM bank_marketing
GROUP BY job
UNION ALL
SELECT 'age_group' AS dimension, age_group AS segment,
       COUNT(*) AS marketing_records,
       SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) AS subscribed_records,
       ROUND(100.0 * AVG(target), 2) AS conversion_rate_pct
FROM bank_marketing
GROUP BY age_group
UNION ALL
SELECT 'balance_segment' AS dimension, balance_segment AS segment,
       COUNT(*) AS marketing_records,
       SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) AS subscribed_records,
       ROUND(100.0 * AVG(target), 2) AS conversion_rate_pct
FROM bank_marketing
GROUP BY balance_segment
ORDER BY dimension, conversion_rate_pct DESC;
