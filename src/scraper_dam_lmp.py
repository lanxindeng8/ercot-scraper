#!/usr/bin/env python3
"""
Day-Ahead Market LMP Scraper

Fetches DAM LMP (Day-Ahead Market Locational Marginal Price) data from ERCOT
and writes to InfluxDB.

Usage:
    python scraper_dam_lmp.py                     # Normal operation (from last timestamp)
    python scraper_dam_lmp.py --start-date 2026-01-01  # Backfill from specific date
"""

import argparse
import os
import sys
from datetime import datetime, timedelta

from ercot_client import create_client_from_env
from influxdb_writer import create_writer_from_env


def main():
    """Main scraper function for DAM LMP data"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="DAM LMP Scraper")
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date for backfill (YYYY-MM-DD format). Overrides auto-detection.",
    )
    args = parser.parse_args()

    print(f"Starting DAM LMP scraper at {datetime.utcnow().isoformat()}")

    try:
        # Initialize clients
        print("Initializing ERCOT client...")
        ercot = create_client_from_env()

        print("Initializing InfluxDB writer...")
        influxdb = create_writer_from_env()

        # Get start date
        print("Determining start date...")

        if args.start_date:
            # Use command-line specified start date
            start_date = datetime.fromisoformat(args.start_date)
            print(f"Using specified start date: {start_date.isoformat()}")
        else:
            # Auto-detect from last timestamp
            last_timestamp = influxdb.get_last_timestamp("dam_lmp")

            if last_timestamp:
                # Start from last timestamp
                start_date = last_timestamp
                print(f"Found last timestamp: {start_date.isoformat()}")
            else:
                # Default: start from 7 days ago
                start_date = datetime.utcnow() - timedelta(days=7)
                print(f"No existing data, starting from: {start_date.isoformat()}")

        # Fetch and write data
        print("Fetching DAM LMP data from ERCOT...")
        total_records = 0

        for page_data in ercot.fetch_spp_day_ahead_hourly(start_date):
            print(f"Received {len(page_data)} records")

            # Write to InfluxDB
            points_written = influxdb.write_dam_lmp_data(page_data)
            total_records += points_written

        print(f"Completed! Total records processed: {total_records}")

        # Close connections
        influxdb.close()

        return 0

    except Exception as e:
        print(f"Error in DAM LMP scraper: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
