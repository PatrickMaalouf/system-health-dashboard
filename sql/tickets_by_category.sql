-- tickets_by_category.sql
-- KPI 3: Ticket Volume by Category
-- Shows where problems cluster so leadership knows where to invest
-- engineering time.

SELECT
    category,
    COUNT(*)                                                    AS total_tickets,
    SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END)     AS critical,
    SUM(CASE WHEN severity = 'high'     THEN 1 ELSE 0 END)     AS high,
    SUM(CASE WHEN severity = 'medium'   THEN 1 ELSE 0 END)     AS medium,
    SUM(CASE WHEN severity = 'low'      THEN 1 ELSE 0 END)     AS low,
    ROUND(AVG(resolution_time_hours), 2)                        AS avg_resolution_hrs
FROM tickets
GROUP BY category
ORDER BY total_tickets DESC;
