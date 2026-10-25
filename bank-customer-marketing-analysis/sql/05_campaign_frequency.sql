-- Contact frequency during the current campaign. A high frequency may also signal previous non-response.
SELECT
    campaign_group,
    COUNT(*) AS marketing_records,
    SUM(CASE WHEN y = 'yes' THEN 1 ELSE 0 END) AS subscribed_records,
    ROUND(100.0 * AVG(target), 2) AS conversion_rate_pct,
    ROUND(AVG(campaign), 2) AS average_raw_contact_count
FROM bank_marketing
GROUP BY campaign_group
ORDER BY CASE campaign_group
    WHEN '1 contact' THEN 1 WHEN '2 contacts' THEN 2 WHEN '3 contacts' THEN 3
    WHEN '4-5 contacts' THEN 4 WHEN '6+ contacts' THEN 5 ELSE 99 END;
