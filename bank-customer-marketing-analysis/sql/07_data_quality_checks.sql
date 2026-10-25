-- High-level checks in the analytical table.
SELECT
    COUNT(*) AS row_count,
    COUNT(DISTINCT age) AS distinct_age_values,
    SUM(CASE WHEN y NOT IN ('yes', 'no') OR y IS NULL THEN 1 ELSE 0 END) AS invalid_target_records,
    SUM(CASE WHEN age IS NULL OR balance IS NULL OR campaign IS NULL THEN 1 ELSE 0 END) AS missing_core_numeric_records,
    SUM(CASE WHEN lower(job) = 'unknown' THEN 1 ELSE 0 END) AS unknown_job_records,
    SUM(CASE WHEN lower(education) = 'unknown' THEN 1 ELSE 0 END) AS unknown_education_records,
    SUM(CASE WHEN pdays < 0 THEN 1 ELSE 0 END) AS no_previous_contact_records
FROM bank_marketing;
