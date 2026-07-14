# KPI Definitions

Key Performance Indicators tracked by the System Health Dashboard.

---

## 1. Uptime %

The percentage of time the system was available over a given period.

**Justification:** This is the single number a non-technical exec cares about most — the "is it working?" headline metric. It translates directly into SLA compliance and customer trust.

---

## 2. Error Rate Over Time

Errors per day/week plotted as a trend line.

**Justification:** Catches slow degradation before it becomes a full outage. A flat count of errors hides trends; a rising slope is an early warning that something is quietly breaking.

---

## 3. Ticket Volume by Category

Number of support/incident tickets broken down by category (e.g., login, payments, performance, infrastructure).

**Justification:** Shows where problems cluster, which tells leadership where to invest engineering time. Without categorisation, all issues look equal and prioritisation becomes guesswork.

---

## 4. Average Resolution Time

Mean time from ticket creation to closure.

**Justification:** A proxy for support health and process efficiency. If resolution time is creeping up, it may signal understaffing, unclear runbooks, or growing technical debt — all of which need attention before they snowball.

---

## 5. Open vs. Resolved Tickets (Backlog Trend)

Running comparison of newly opened tickets against resolved tickets over time.

**Justification:** A growing backlog means the team is falling behind demand — an early warning sign that capacity or process needs adjustment. Conversely, a shrinking backlog confirms that recent improvements are working.
