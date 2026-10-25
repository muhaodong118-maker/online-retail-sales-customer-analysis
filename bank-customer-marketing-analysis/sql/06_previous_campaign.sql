-- Prior campaign outcome and prior-contact flag.
SELECT
    poutcome AS previous_campaign_outcome,
    previous_contacted,
    COUNT(*) AS marketing_records,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) AS subscribed_records,
    ROUND(100.0 * AVG(target), 2) AS conversion_rate_pct
FROM bank_marketing
GROUP BY poutcome, previous_contacted
ORDER BY conversion_rate_pct DESC;
