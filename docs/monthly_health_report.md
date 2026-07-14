# Monthly System Health Report — June 2026

**To:** Stakeholders  
**From:** Systems Engineering  
**Date:** July 14, 2026  
**Subject:** June 2026 System Health Summary

---

Hi team,

Overall the system performed well in June. Uptime held at **99.31%** (715 of 720 monitored hours), and total ticket volume dropped **19.5%** month-over-month — from 87 tickets in May down to **70 in June**. The weekly trend was encouraging: we went from 21 new tickets in the first week of the month (W22) down to just 5 by the final week (W26), which tells us the hardening work from Q1 is paying off. Critical tickets also resolved quickly, averaging **5.44 hours** to close — well inside our 8-hour SLA.

That said, two areas need attention. **Payments** accounted for only 13 of the month's 70 tickets but carried the **highest critical-severity concentration** at 3 criticals — nearly half of the month's total of 7. Average resolution time for payments-related issues sits at **22.99 hours** across the full dataset, the slowest of any category. Separately, **medium-severity tickets** continue to drag at **33.09 hours** average resolution (virtually unchanged from the 33.18-hour all-time average), which suggests our triage process is de-prioritizing them rather than right-sizing the effort. We also saw uptime dip from May's 99.87% to June's 99.31% — a small move in percentage terms, but it represents **5 hours of additional downtime** compared to the prior month.

Our **open backlog currently stands at 77 tickets**, with 10 of those originating in June alone. While the overall resolution rate is healthy (60 of 70 June tickets already closed), the cumulative backlog has been climbing steadily — every single week this year has added at least 1 net-new unresolved ticket, and weeks with spikes (e.g., W20 added 8 to the backlog in one go) are pulling us further behind.

**Recommended action:** Schedule a focused payments triage sprint this cycle. With 12 criticals all-time and the longest category-level resolution time (22.99 hrs), payments is our highest-risk surface. A dedicated review of the 3 open critical payments tickets — plus a root-cause pass on the recurring failure patterns — would reduce both backlog pressure and the outsized business risk that payments outages carry. Happy to walk through the dashboard data in more detail at the next ops review.

Best,  
Systems Engineering
