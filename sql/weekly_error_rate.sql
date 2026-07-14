-- weekly_error_rate.sql
-- KPI 2: Error Rate Over Time
-- Counts tickets (errors/incidents) per ISO week as a trend line.
-- Each row = one week with its ticket count, useful for spotting slow degradation.

SELECT
    strftime('%Y-W%W', created_at)  AS week,
    MIN(DATE(created_at))           AS week_start,
    COUNT(*)                        AS ticket_count
FROM tickets
GROUP BY strftime('%Y-W%W', created_at)
ORDER BY week;
