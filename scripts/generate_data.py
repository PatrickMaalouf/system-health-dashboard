"""
generate_data.py
~~~~~~~~~~~~~~~~
Generates 3-6 months of realistic incident / support-ticket data
and writes it to:
  - data/tickets.csv        (incident tickets)
  - data/uptime_events.csv  (hourly uptime/downtime pings)

Usage:
    python scripts/generate_data.py            # defaults: 500 tickets, 6 months
    python scripts/generate_data.py -n 1000    # 1 000 tickets
    python scripts/generate_data.py -m 3       # 3-month window
"""

import argparse
import os
import random
from pathlib import Path

import pandas as pd
# pyrefly: ignore [missing-import]
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CATEGORIES = ["login", "payments", "performance", "API", "UI"]
SEVERITIES = ["low", "medium", "high", "critical"]
STATUSES = ["open", "resolved"]

# Weighted probabilities so the data looks realistic
CATEGORY_WEIGHTS = [0.25, 0.20, 0.20, 0.20, 0.15]  # login issues most common
SEVERITY_WEIGHTS = [0.35, 0.35, 0.20, 0.10]          # critical is rare
STATUS_WEIGHTS = [0.15, 0.85]                          # most tickets get resolved

# Median resolution hours by severity (used to shape the distribution)
RESOLUTION_HOURS = {
    "low": (1, 24),
    "medium": (4, 72),
    "high": (2, 48),
    "critical": (0.5, 12),
}


def _random_resolution_hours(severity: str) -> float:
    """Return a realistic resolution time in hours for the given severity."""
    lo, hi = RESOLUTION_HOURS[severity]
    # Use a triangular distribution so we get a natural-looking spread
    # with most values clustering toward the lower end.
    hours = random.triangular(lo, hi, lo + (hi - lo) * 0.3)
    return round(hours, 2)


def generate_tickets(n_tickets: int = 500, months: int = 6) -> pd.DataFrame:
    """Create *n_tickets* rows of synthetic incident data."""
    from datetime import timedelta

    end_date = pd.Timestamp.now()
    start_date = end_date - pd.DateOffset(months=months)

    rows = []
    for i in range(1, n_tickets + 1):
        category = random.choices(CATEGORIES, weights=CATEGORY_WEIGHTS, k=1)[0]
        severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS, k=1)[0]
        status = random.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]

        created_at = fake.date_time_between(
            start_date=start_date.to_pydatetime(),
            end_date=end_date.to_pydatetime(),
        )

        if status == "resolved":
            resolution_hours = _random_resolution_hours(severity)
            resolved_at = created_at + timedelta(hours=resolution_hours)
        else:
            resolution_hours = None
            resolved_at = None

        rows.append(
            {
                "ticket_id": f"TKT-{i:05d}",
                "created_at": created_at,
                "resolved_at": resolved_at,
                "category": category,
                "severity": severity,
                "status": status,
                "resolution_time_hours": resolution_hours,
            }
        )

    df = pd.DataFrame(rows)
    df = df.sort_values("created_at").reset_index(drop=True)
    return df


def generate_uptime_events(months: int = 6) -> pd.DataFrame:
    """Create one row per hour simulating uptime/downtime health-check pings.

    Realistic behaviour:
    - ~99 % of hours are "up".
    - Outages are clustered into multi-hour windows (1-6 hrs) so the data
      looks like real incidents rather than random blips.
    - "down" rows get a response_time_ms of 0; "up" rows get a value
      drawn from a log-normal distribution centred around 120 ms.
    """
    import math

    end_date = pd.Timestamp.now().floor("h")
    start_date = end_date - pd.DateOffset(months=months)
    timestamps = pd.date_range(start=start_date, end=end_date, freq="h")

    statuses = ["up"] * len(timestamps)

    # Sprinkle in outage windows
    # Target roughly 0.5-1.5 % downtime overall
    total_hours = len(timestamps)
    target_down_hours = int(total_hours * random.uniform(0.005, 0.015))
    down_hours_placed = 0

    while down_hours_placed < target_down_hours:
        # Pick a random starting hour and an outage length of 1-6 hours
        outage_len = random.randint(1, 6)
        start_idx = random.randint(0, total_hours - outage_len)
        for j in range(outage_len):
            if statuses[start_idx + j] == "up":
                statuses[start_idx + j] = "down"
                down_hours_placed += 1
            if down_hours_placed >= target_down_hours:
                break

    # Generate response times
    response_times = []
    for s in statuses:
        if s == "down":
            response_times.append(0)
        else:
            # Log-normal with median ~120 ms, occasional spikes up to ~800 ms
            ms = random.lognormvariate(math.log(120), 0.4)
            response_times.append(round(ms, 1))

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "status": statuses,
            "response_time_ms": response_times,
        }
    )
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic incident/ticket data."
    )
    parser.add_argument(
        "-n", "--num-tickets", type=int, default=500,
        help="Number of tickets to generate (default: 500)",
    )
    parser.add_argument(
        "-m", "--months", type=int, default=6,
        help="How many months of history to cover (default: 6)",
    )
    args = parser.parse_args()

    # Ensure the output directory exists
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    # --- tickets.csv ---
    df_tickets = generate_tickets(n_tickets=args.num_tickets, months=args.months)
    tickets_path = data_dir / "tickets.csv"
    df_tickets.to_csv(tickets_path, index=False)

    print(f"✓ Generated {len(df_tickets)} tickets spanning {args.months} months")
    print(f"  → {tickets_path}")
    print(f"\nSample rows:\n{df_tickets.head(10).to_string(index=False)}")
    print(f"\nCategory distribution:\n{df_tickets['category'].value_counts().to_string()}")
    print(f"\nSeverity distribution:\n{df_tickets['severity'].value_counts().to_string()}")
    print(f"\nStatus distribution:\n{df_tickets['status'].value_counts().to_string()}")

    # --- uptime_events.csv ---
    df_uptime = generate_uptime_events(months=args.months)
    uptime_path = data_dir / "uptime_events.csv"
    df_uptime.to_csv(uptime_path, index=False)

    up_count = (df_uptime["status"] == "up").sum()
    total = len(df_uptime)
    uptime_pct = up_count / total * 100

    print(f"\n{'='*50}")
    print(f"✓ Generated {total} hourly uptime pings spanning {args.months} months")
    print(f"  → {uptime_path}")
    print(f"  Uptime: {uptime_pct:.2f}% ({total - up_count} hours down)")
    print(f"\nSample rows:\n{df_uptime.head(10).to_string(index=False)}")


if __name__ == "__main__":
    main()
