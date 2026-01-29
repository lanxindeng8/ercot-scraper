#!/usr/bin/env python3
"""
Real-Time Market LMP Scraper

Fetches RTM LMP (Real-Time Market Locational Marginal Price) data from ERCOT
and writes to InfluxDB.
"""

import os
import sys
from datetime import datetime, timedelta

from ercot_client import create_client_from_env
from influxdb_writer import create_writer_from_env


def main():
    """Main scraper function for RTM LMP data"""
    print(f"Starting RTM LMP scraper at {datetime.utcnow().isoformat()}")

    try:
        # Initialize clients
        print("Initializing ERCOT client...")
        ercot = create_client_from_env()

        print("Initializing InfluxDB writer...")
        influxdb = create_writer_from_env()

        # Get start date (last timestamp or default lookback)
        print("Determining start date...")
        last_timestamp = influxdb.get_last_timestamp("rtm_lmp")

        if last_timestamp:
            # Start from last timestamp
            start_date = last_timestamp
            print(f"Found last timestamp: {start_date.isoformat()}")
        else:
            # Default: start from 7 days ago
            start_date = datetime.utcnow() - timedelta(days=7)
            print(f"No existing data, starting from: {start_date.isoformat()}")

        # Fetch and write data
        print("Fetching RTM LMP data from ERCOT...")
        total_records = 0

        for page_data in ercot.fetch_lmp_by_settlement_point(start_date):
            print(f"Received {len(page_data)} records")

            # Write to InfluxDB
            points_written = influxdb.write_rtm_lmp_data(page_data)
            total_records += points_written

        print(f"Completed! Total records processed: {total_records}")

        # Close connections
        influxdb.close()

        return 0

    except Exception as e:
        print(f"Error in RTM LMP scraper: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
