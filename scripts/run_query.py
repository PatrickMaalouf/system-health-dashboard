"""
run_query.py
~~~~~~~~~~~~
Run a .sql file against data/health.db and print the results.

Usage:
    python scripts/run_query.py sql/uptime_percentage.sql
    python scripts/run_query.py sql/weekly_error_rate.sql
    python scripts/run_query.py sql/tickets_by_category.sql
    python scripts/run_query.py sql/avg_resolution_time.sql
    python scripts/run_query.py sql/open_vs_resolved.sql
"""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "health.db"


def main():
    parser = argparse.ArgumentParser(description="Run a SQL file against health.db")
    parser.add_argument("sql_file", help="Path to the .sql file to execute")
    args = parser.parse_args()

    sql_path = Path(args.sql_file)
    if not sql_path.exists():
        print(f"✗ File not found: {sql_path}")
        raise SystemExit(1)

    if not DB_PATH.exists():
        print(f"✗ Database not found: {DB_PATH}")
        print("  Run  python scripts/load_to_sqlite.py  first.")
        raise SystemExit(1)

    sql = sql_path.read_text(encoding="utf-8")
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(sql, conn)
        print(f"── {sql_path.name} ({'─' * (50 - len(sql_path.name))})")
        print(df.to_string(index=False))
        print(f"\n({len(df)} row{'s' if len(df) != 1 else ''})")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
