-- uptime_percentage.sql
-- KPI 1: Uptime %
-- The percentage of hours the system was "up" over the full dataset.
-- Returns a single row with total hours, up hours, down hours, and uptime %.

SELECT
    COUNT(*)                                        AS total_hours,
    SUM(CASE WHEN status = 'up'   THEN 1 ELSE 0 END) AS up_hours,
    SUM(CASE WHEN status = 'down' THEN 1 ELSE 0 END) AS down_hours,
    ROUND(
        SUM(CASE WHEN status = 'up' THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        4
    ) AS uptime_pct
FROM uptime_events;
