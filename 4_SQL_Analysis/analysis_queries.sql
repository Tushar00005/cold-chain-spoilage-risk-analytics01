-- ============================================================================
-- Cold Chain Integrity & Spoilage Risk Analytics
-- STEP 4: MYSQL BUSINESS ANALYSIS
-- ============================================================================
-- Run against the `cold_chain_analytics` database after schema.sql and
-- load_data.py have been executed. Organized by business question.
-- Uses: SELECT, WHERE, GROUP BY, HAVING, ORDER BY, CASE, JOIN, aggregate
-- functions, subqueries, CTEs, and window functions.
-- ============================================================================

USE cold_chain_analytics;

-- ----------------------------------------------------------------------------
-- Q1. Overall shipment volume and status breakdown
-- ----------------------------------------------------------------------------
SELECT
    COUNT(*)                                                   AS total_shipments,
    SUM(CASE WHEN shipment_status = 'Delivered' THEN 1 ELSE 0 END)   AS delivered_shipments,
    SUM(CASE WHEN shipment_status = 'In Transit' THEN 1 ELSE 0 END)  AS in_transit_shipments,
    SUM(CASE WHEN shipment_status = 'Cancelled' THEN 1 ELSE 0 END)   AS cancelled_shipments,
    ROUND(100 * SUM(CASE WHEN shipment_status = 'Delivered' THEN 1 ELSE 0 END) / COUNT(*), 2)
                                                                AS delivered_pct
FROM shipments;

-- ----------------------------------------------------------------------------
-- Q2. On-time vs delayed deliveries (delivered shipments only)
-- ----------------------------------------------------------------------------
SELECT
    SUM(CASE WHEN delay_flag = 0 THEN 1 ELSE 0 END)                AS on_time_shipments,
    SUM(CASE WHEN delay_flag = 1 THEN 1 ELSE 0 END)                AS delayed_shipments,
    ROUND(100 * SUM(CASE WHEN delay_flag = 1 THEN 1 ELSE 0 END)
        / SUM(CASE WHEN delay_flag IS NOT NULL THEN 1 ELSE 0 END), 2) AS delayed_pct,
    ROUND(AVG(CASE WHEN delay_flag = 1 THEN delay_duration_hours END), 2) AS avg_delay_hours_when_delayed
FROM shipments
WHERE shipment_status = 'Delivered';

-- ----------------------------------------------------------------------------
-- Q3. Temperature compliance: violations and average deviation
-- ----------------------------------------------------------------------------
SELECT
    COUNT(*)                                                          AS total_shipments,
    SUM(temperature_excursion_flag)                                   AS shipments_with_violation,
    ROUND(100 * SUM(temperature_excursion_flag) / COUNT(*), 2)        AS violation_pct,
    ROUND(100 * (COUNT(*) - SUM(temperature_excursion_flag)) / COUNT(*), 2) AS temperature_compliance_pct,
    ROUND(AVG(deviation_c), 2)                                        AS avg_deviation_c
FROM shipments;

-- ----------------------------------------------------------------------------
-- Q4. Spoilage risk distribution and total estimated financial loss
-- ----------------------------------------------------------------------------
SELECT
    spoilage_risk_category,
    COUNT(*)                                       AS shipment_count,
    ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_shipments,
    SUM(estimated_spoilage_qty)                    AS total_spoiled_units,
    ROUND(SUM(estimated_financial_loss), 2)        AS total_estimated_loss
FROM shipments
GROUP BY spoilage_risk_category
ORDER BY FIELD(spoilage_risk_category, 'Critical Risk', 'High Risk', 'Medium Risk', 'Low Risk');

-- ----------------------------------------------------------------------------
-- Q5. Spoilage rate and financial loss by product category
-- ----------------------------------------------------------------------------
SELECT
    p.product_category,
    COUNT(*)                                                              AS total_shipments,
    SUM(CASE WHEN s.spoilage_risk_category IN ('High Risk','Critical Risk') THEN 1 ELSE 0 END)
                                                                           AS high_or_critical_shipments,
    ROUND(100 * SUM(CASE WHEN s.spoilage_risk_category IN ('High Risk','Critical Risk') THEN 1 ELSE 0 END)
        / COUNT(*), 2)                                                    AS spoilage_rate_pct,
    ROUND(SUM(s.estimated_financial_loss), 2)                             AS total_estimated_loss
FROM shipments s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_category
HAVING COUNT(*) >= 10
ORDER BY total_estimated_loss DESC;

-- ----------------------------------------------------------------------------
-- Q6. Supplier performance scorecard (delay rate, violation rate, loss)
-- ----------------------------------------------------------------------------
SELECT
    sup.supplier_id,
    sup.supplier_name,
    sup.supplier_country,
    COUNT(*)                                                        AS total_shipments,
    ROUND(100 * SUM(s.temperature_excursion_flag) / COUNT(*), 2)    AS temp_violation_rate_pct,
    ROUND(100 * SUM(CASE WHEN s.delay_flag = 1 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN s.delay_flag IS NOT NULL THEN 1 ELSE 0 END), 0), 2)
                                                                     AS delay_rate_pct,
    ROUND(SUM(s.estimated_financial_loss), 2)                       AS total_estimated_loss,
    RANK() OVER (ORDER BY SUM(s.estimated_financial_loss) DESC)     AS loss_rank
FROM shipments s
JOIN suppliers sup ON s.supplier_id = sup.supplier_id
GROUP BY sup.supplier_id, sup.supplier_name, sup.supplier_country
ORDER BY total_estimated_loss DESC;

-- ----------------------------------------------------------------------------
-- Q7. Highest-risk suppliers (HAVING filter: violation rate above fleet average)
-- ----------------------------------------------------------------------------
WITH supplier_stats AS (
    SELECT
        sup.supplier_id,
        sup.supplier_name,
        COUNT(*)                                                   AS total_shipments,
        ROUND(100 * SUM(s.temperature_excursion_flag) / COUNT(*), 2) AS violation_rate_pct
    FROM shipments s
    JOIN suppliers sup ON s.supplier_id = sup.supplier_id
    GROUP BY sup.supplier_id, sup.supplier_name
)
SELECT *
FROM supplier_stats
WHERE violation_rate_pct > (SELECT AVG(violation_rate_pct) FROM supplier_stats)
ORDER BY violation_rate_pct DESC;

-- ----------------------------------------------------------------------------
-- Q8. Route performance: distance, avg transit time, excursion rate
-- ----------------------------------------------------------------------------
SELECT
    r.route_id,
    r.origin,
    r.destination,
    r.transport_mode,
    COUNT(*)                                                     AS total_shipments,
    ROUND(AVG(s.transit_hours), 1)                               AS avg_transit_hours,
    ROUND(100 * SUM(s.temperature_excursion_flag) / COUNT(*), 2) AS excursion_rate_pct,
    ROUND(SUM(s.estimated_financial_loss), 2)                    AS total_estimated_loss
FROM shipments s
JOIN routes r ON s.route_id = r.route_id
GROUP BY r.route_id, r.origin, r.destination, r.transport_mode
HAVING COUNT(*) >= 5
ORDER BY excursion_rate_pct DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Q9. Top 10 highest-loss products
-- ----------------------------------------------------------------------------
SELECT
    p.product_id,
    p.product_name,
    p.product_category,
    COUNT(*)                                     AS total_shipments,
    SUM(s.estimated_spoilage_qty)                 AS total_spoiled_units,
    ROUND(SUM(s.estimated_financial_loss), 2)     AS total_estimated_loss
FROM shipments s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.product_category
ORDER BY total_estimated_loss DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- Q10. Monthly shipment trend: volume, violation rate, financial loss
-- ----------------------------------------------------------------------------
SELECT
    DATE_FORMAT(shipment_date, '%Y-%m')                          AS shipment_month,
    COUNT(*)                                                     AS total_shipments,
    ROUND(100 * SUM(temperature_excursion_flag) / COUNT(*), 2)   AS violation_rate_pct,
    ROUND(SUM(estimated_financial_loss), 2)                      AS total_estimated_loss
FROM shipments
GROUP BY DATE_FORMAT(shipment_date, '%Y-%m')
ORDER BY shipment_month;

-- ----------------------------------------------------------------------------
-- Q11. Relationship between delivery delay and spoilage risk
-- ----------------------------------------------------------------------------
SELECT
    CASE
        WHEN delay_flag = 0 THEN 'On Time'
        WHEN delay_duration_hours < 6  THEN 'Delayed < 6h'
        WHEN delay_duration_hours < 24 THEN 'Delayed 6-24h'
        WHEN delay_duration_hours >= 24 THEN 'Delayed 24h+'
        ELSE 'Cancelled/Unknown'
    END                                                          AS delay_bucket,
    COUNT(*)                                                     AS shipments,
    ROUND(100 * SUM(CASE WHEN spoilage_risk_category IN ('High Risk','Critical Risk') THEN 1 ELSE 0 END)
        / COUNT(*), 2)                                           AS high_critical_risk_pct,
    ROUND(AVG(estimated_financial_loss), 2)                      AS avg_loss_per_shipment
FROM shipments
WHERE delay_flag IS NOT NULL
GROUP BY delay_bucket
ORDER BY FIELD(delay_bucket, 'On Time', 'Delayed < 6h', 'Delayed 6-24h', 'Delayed 24h+');

-- ----------------------------------------------------------------------------
-- Q12. Shipment-level detail ranked by financial loss, with a running total
--      (window function example)
-- ----------------------------------------------------------------------------
SELECT
    shipment_id,
    product_id,
    spoilage_risk_category,
    estimated_financial_loss,
    SUM(estimated_financial_loss) OVER (ORDER BY estimated_financial_loss DESC) AS running_loss_total,
    ROW_NUMBER() OVER (ORDER BY estimated_financial_loss DESC)                  AS loss_rank
FROM shipments
WHERE estimated_financial_loss > 0
ORDER BY estimated_financial_loss DESC
LIMIT 25;

-- ----------------------------------------------------------------------------
-- Q13. Average transit time and temperature deviation by transport mode
-- ----------------------------------------------------------------------------
SELECT
    r.transport_mode,
    COUNT(*)                          AS total_shipments,
    ROUND(AVG(s.transit_hours), 1)    AS avg_transit_hours,
    ROUND(AVG(s.deviation_c), 2)      AS avg_temp_deviation_c
FROM shipments s
JOIN routes r ON s.route_id = r.route_id
GROUP BY r.transport_mode
ORDER BY avg_temp_deviation_c DESC;

-- ----------------------------------------------------------------------------
-- Q14. Suppliers whose average financial loss per shipment exceeds the
--      overall average (correlated subquery example)
-- ----------------------------------------------------------------------------
SELECT
    sup.supplier_name,
    ROUND(AVG(s.estimated_financial_loss), 2) AS avg_loss_per_shipment
FROM shipments s
JOIN suppliers sup ON s.supplier_id = sup.supplier_id
GROUP BY sup.supplier_name
HAVING AVG(s.estimated_financial_loss) > (
    SELECT AVG(estimated_financial_loss) FROM shipments
)
ORDER BY avg_loss_per_shipment DESC;

-- ----------------------------------------------------------------------------
-- Q15. Top-3 highest-loss products WITHIN each category (window function:
--      ROW_NUMBER partitioned by category)
-- ----------------------------------------------------------------------------
WITH product_loss AS (
    SELECT
        p.product_category,
        p.product_id,
        p.product_name,
        SUM(s.estimated_financial_loss) AS total_loss
    FROM shipments s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.product_category, p.product_id, p.product_name
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY product_category ORDER BY total_loss DESC) AS rank_in_category
    FROM product_loss
)
SELECT product_category, product_id, product_name, ROUND(total_loss, 2) AS total_loss, rank_in_category
FROM ranked
WHERE rank_in_category <= 3
ORDER BY product_category, rank_in_category;
