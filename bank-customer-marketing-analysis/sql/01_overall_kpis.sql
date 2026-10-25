-- Overall performance. Each row is a marketing record, not necessarily a unique customer.
SELECT
    COUNT(*) AS marketing_records,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) AS subscribed_records,
    SUM(CASE WHEN y = 'no' THEN 1 ELSE 0 END) AS not_subscribed_records,
    ROUND(100.0 * SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS conversion_rate_pct,
    ROUND(AVG(age), 2) AS average_age,
    ROUND(AVG(balance), 2) AS average_balance,
    ROUND(AVG(campaign), 2) AS average_contacts_in_current_campaign
FROM bank_marketing;
