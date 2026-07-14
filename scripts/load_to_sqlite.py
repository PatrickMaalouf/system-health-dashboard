"""
load_to_sqlite.py
~~~~~~~~~~~~~~~~~
Reads the generated CSVs and loads them into a SQLite database.

Inputs:
    data/tickets.csv
    data/uptime_events.csv

Output:
    data/health.db  (tables: tickets, uptime_events)

Usage:
    python scripts/load_to_sqlite.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "health.db"

CSV_TABLES = {
    "tickets": DATA_DIR / "tickets.csv",
    "uptime_events": DATA_DIR / "uptime_events.csv",
}


def load_csv(path: Path) -> pd.DataFrame:
    """Read a CSV and return a DataFrame, or exit with a clear message."""
    if not path.exists():
        print(f"✗ File not found: {path}")
        print("  Run  python scripts/generate_data.py  first.")
        raise SystemExit(1)
    return pd.read_csv(path)


def load_to_sqlite() -> None:
    """Load every CSV into its corresponding SQLite table."""
    DATA_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    try:
        for table_name, csv_path in CSV_TABLES.items():
            df = load_csv(csv_path)

            # Drop and recreate the table each run so the DB always
            # reflects the latest generated data.
            df.to_sql(table_name, conn, if_exists="replace", index=False)

            print(f"✓ Loaded {len(df):,} rows → {table_name}")

        # Quick sanity check: print row counts straight from SQLite
        print(f"\n{'='*50}")
        print(f"Database: {DB_PATH}")
        cur = conn.cursor()
        for table_name in CSV_TABLES:
            count = cur.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"  {table_name}: {count:,} rows")

        # Show a sample query to confirm everything looks right
        print(f"\nSample tickets:")
        sample = pd.read_sql("SELECT * FROM tickets LIMIT 5", conn)
        print(sample.to_string(index=False))

        print(f"\nSample uptime_events:")
        sample = pd.read_sql("SELECT * FROM uptime_events LIMIT 5", conn)
        print(sample.to_string(index=False))

    finally:
        conn.close()


if __name__ == "__main__":
    load_to_sqlite()
