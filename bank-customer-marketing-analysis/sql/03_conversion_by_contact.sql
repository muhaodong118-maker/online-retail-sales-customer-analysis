-- Channel performance includes both sample volume and conversion rate.
SELECT
    contact AS contact_channel,
    COUNT(*) AS marketing_records,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) AS subscribed_records,
    ROUND(100.0 * AVG(target), 2) AS conversion_rate_pct
FROM bank_marketing
GROUP BY contact
ORDER BY conversion_rate_pct DESC;
