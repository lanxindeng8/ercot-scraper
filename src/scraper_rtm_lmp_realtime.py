#!/usr/bin/env python3
"""
Real-Time Market LMP Scraper (CDR Version)

Fetches RTM LMP data from ERCOT's CDR (Current Day Reports) HTML pages.
This provides near real-time data (within 5 minutes) vs the ~6 hour delay
from the Public API.
"""

import os
import sys
from datetime import datetime, timezone, timedelta

from cdr_scraper import create_cdr_scraper
from influxdb_writer import create_writer_from_env

# Central Time offset (CST = UTC-6, CDT = UTC-5)
# For simplicity, using CST. In production, use pytz for proper DST handling.
CST_OFFSET = timedelta(hours=-6)


def cst_to_utc(cst_datetime: datetime) -> datetime:
    """Convert CST datetime to UTC"""
    # Assume the datetime is in CST (UTC-6)
    # Add 6 hours to get UTC
    return cst_datetime + timedelta(hours=6)


def main():
    """Main scraper function for real-time RTM LMP data"""
    print(f"Starting RTM LMP real-time scraper at {datetime.utcnow().isoformat()}")

    try:
        # Initialize clients
        print("Initializing CDR scraper...")
        cdr = create_cdr_scraper()

        print("Initializing InfluxDB writer...")
        influxdb = create_writer_from_env()

        # Fetch data from CDR
        print("Fetching RTM LMP data from CDR...")
        cst_timestamp, records = cdr.fetch_rtm_lmp()

        if not cst_timestamp:
            print("Error: Could not parse timestamp from CDR page")
            return 1

        if not records:
            print("Error: No records found in CDR page")
            return 1

        # Convert CST timestamp to UTC for storage
        utc_timestamp = cst_to_utc(cst_timestamp)
        print(f"CST timestamp: {cst_timestamp}")
        print(f"UTC timestamp: {utc_timestamp}")

        # Check if this data is newer than what we have in rtm_lmp_realtime
        last_timestamp = influxdb.get_last_timestamp("rtm_lmp_realtime")
        if last_timestamp:
            # Make last_timestamp timezone-aware if it isn't
            if last_timestamp.tzinfo is None:
                last_timestamp = last_timestamp.replace(tzinfo=timezone.utc)

            utc_ts_aware = utc_timestamp.replace(tzinfo=timezone.utc)

            if utc_ts_aware <= last_timestamp:
                print(f"Data already up to date. Last: {last_timestamp}, CDR: {utc_ts_aware}")
                print("No new data to write.")
                cdr.close()
                influxdb.close()
                return 0

        # Transform records for InfluxDB writer
        # The writer expects records with SCEDTimestamp field
        influx_records = []
        for record in records:
            influx_records.append({
                "SCEDTimestamp": utc_timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                "SettlementPoint": record["settlementPoint"],
                "LMP": record["lmp"],
            })

        # Write to rtm_lmp_realtime measurement (CDR data)
        points_written = influxdb.write_rtm_lmp_realtime(influx_records)
        print(f"Wrote {points_written} points to rtm_lmp_realtime")

        # Close connections
        cdr.close()
        influxdb.close()

        print(f"Completed! Real-time data timestamp: {cst_timestamp} CST ({utc_timestamp} UTC)")
        return 0

    except Exception as e:
        print(f"Error in RTM LMP real-time scraper: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
