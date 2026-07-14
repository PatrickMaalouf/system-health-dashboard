-- avg_resolution_time.sql
-- KPI 4: Average Resolution Time
-- Mean hours from ticket creation to closure, broken down by severity.
-- Only includes resolved tickets (open tickets have no resolution time).

SELECT
    severity,
    COUNT(*)                                    AS resolved_tickets,
    ROUND(AVG(resolution_time_hours), 2)        AS avg_hours,
    ROUND(MIN(resolution_time_hours), 2)        AS min_hours,
    ROUND(MAX(resolution_time_hours), 2)        AS max_hours
FROM tickets
WHERE status = 'resolved'
GROUP BY severity
ORDER BY
    CASE severity
        WHEN 'critical' THEN 1
        WHEN 'high'     THEN 2
        WHEN 'medium'   THEN 3
        WHEN 'low'      THEN 4
    END;
