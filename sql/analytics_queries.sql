-- Monthly claim volume and paid-to-claimed ratio (a portfolio loss proxy).
SELECT
    d.year_number,
    d.month_number,
    COUNT(*) AS claim_count,
    SUM(f.claim_amount) AS claimed_amount,
    SUM(f.paid_amount) AS paid_amount,
    ROUND(SUM(f.paid_amount) / NULLIF(SUM(f.claim_amount), 0), 4) AS paid_claim_ratio
FROM insurance_dw.fact_claim f
JOIN insurance_dw.dim_date d ON d.date_key = f.event_date_key
GROUP BY d.year_number, d.month_number
ORDER BY d.year_number, d.month_number;

-- Vehicles with repeat claims, useful as an investigation input (not a fraud verdict).
SELECT
    v.vehicle_id,
    COUNT(*) AS claim_count,
    SUM(f.claim_amount) AS total_claimed
FROM insurance_dw.fact_claim f
JOIN insurance_dw.dim_vehicle v ON v.vehicle_key = f.vehicle_key
GROUP BY v.vehicle_id
HAVING COUNT(*) > 1
ORDER BY claim_count DESC, total_claimed DESC;

-- Processing delay between accident and ingestion event.
SELECT
    f.claim_type,
    ROUND(AVG(ed.full_date - ad.full_date), 2) AS avg_reporting_delay_days
FROM insurance_dw.fact_claim f
JOIN insurance_dw.dim_date ed ON ed.date_key = f.event_date_key
JOIN insurance_dw.dim_date ad ON ad.date_key = f.accident_date_key
GROUP BY f.claim_type
ORDER BY avg_reporting_delay_days DESC;
