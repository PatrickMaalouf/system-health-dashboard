-- open_vs_resolved.sql
-- KPI 5: Open vs. Resolved Tickets (Backlog Trend)
-- Weekly comparison of newly opened tickets against resolved tickets.
-- A growing gap (opened > resolved) signals the team is falling behind.

SELECT
    strftime('%Y-W%W', created_at)  AS week,
    MIN(DATE(created_at))           AS week_start,
    COUNT(*)                        AS opened,
    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) AS resolved,
    SUM(CASE WHEN status = 'open'     THEN 1 ELSE 0 END) AS still_open,
    COUNT(*) - SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) AS net_backlog_change
FROM tickets
GROUP BY strftime('%Y-W%W', created_at)
ORDER BY week;
