#!/usr/bin/env python3
"""
Backfill RTM LMP data from ERCOT API to rtm_lmp_api measurement.
Fetches historical data and writes clean API data.

Note: ERCOT API has ~6 hour delay, so recent data may not be available.
"""

import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv()

from ercot_client import create_client_from_env
from influxdb_writer import create_writer_from_env


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Backfill RTM LMP data from ERCOT API")
    parser.add_argument(
        "--start-date",
        type=str,
        default="2026-01-22",
        help="Start date (YYYY-MM-DD). Default: 2026-01-22",
    )
    args = parser.parse_args()

    start_date = datetime.fromisoformat(args.start_date)

    print("=" * 60)
    print("Backfill RTM LMP from ERCOT API")
    print("=" * 60)
    print(f"Start date: {start_date.date()}")
    print(f"Target: rtm_lmp_api")
    print()
    print("Note: API has ~6h delay. Fetching all available data from start date.")
    print()

    # Initialize clients
    print("Initializing ERCOT client...")
    ercot = create_client_from_env()

    print("Initializing InfluxDB writer...")
    influxdb = create_writer_from_env()

    # Fetch all data from start_date
    # API only supports SCEDTimestampFrom (no "to" filter)
    # Pages are yielded by the generator, so memory is managed
    total_written = 0
    page_num = 0
    start_time = time.time()

    print(f"\nFetching RTM LMP data from {start_date.date()}...")

    try:
        for page_data in ercot.fetch_lmp_by_settlement_point(start_date):
            page_num += 1
            if page_data:
                # Write to rtm_lmp_api
                points_written = influxdb.write_rtm_lmp_data(page_data, measurement="rtm_lmp_api")
                total_written += points_written

                elapsed = time.time() - start_time
                rate = total_written / elapsed if elapsed > 0 else 0
                print(f"Page {page_num}: {points_written} written | Total: {total_written:,} | Rate: {rate:.0f}/s")

    except Exception as e:
        print(f"Error during fetch: {e}")
        import traceback
        traceback.print_exc()

    influxdb.close()

    elapsed = time.time() - start_time
    print()
    print("=" * 60)
    print(f"Completed! Total records written: {total_written:,}")
    print(f"Time elapsed: {elapsed/60:.1f} minutes")
    print("=" * 60)


if __name__ == "__main__":
    main()
