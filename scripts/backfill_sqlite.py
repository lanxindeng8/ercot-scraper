#!/usr/bin/env python3
"""
Backfill SQLite archive from InfluxDB.

Run after InfluxDB has clean data to populate SQLite with historical records.
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from argparse import ArgumentParser

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv()

from influxdb_client_3 import InfluxDBClient3
from sqlite_archive import SQLiteArchive


def get_influxdb_client():
    """Create InfluxDB client from environment"""
    url = os.environ.get('INFLUXDB_URL')
    token = os.environ.get('INFLUXDB_TOKEN')
    org = os.environ.get('INFLUXDB_ORG')
    database = os.environ.get('INFLUXDB_BUCKET') or os.environ.get('INFLUXDB_DATABASE', 'ercot')

    return InfluxDBClient3(
        host=url.replace('https://', '').replace('http://', ''),
        token=token,
        org=org,
        database=database,
    )


def backfill_rtm_api(client: InfluxDBClient3, archive: SQLiteArchive,
                     start_date: datetime, end_date: datetime) -> int:
    """Backfill RTM LMP API data day by day"""
    print("\nBackfilling rtm_lmp_api...")
    total = 0
    current = start_date

    while current < end_date:
        next_day = current + timedelta(days=1)

        query = f'''
        SELECT time, settlement_point, lmp, energy_component, congestion_component, loss_component
        FROM "rtm_lmp_api"
        WHERE time >= '{current.isoformat()}' AND time < '{next_day.isoformat()}'
        '''

        try:
            result = client.query(query)
            df = result.to_pandas()

            if not df.empty:
                records = []
                for _, row in df.iterrows():
                    records.append({
                        "time": row['time'],
                        "settlement_point": row.get('settlement_point', ''),
                        "lmp": row.get('lmp', 0),
                        "energy_component": row.get('energy_component', 0),
                        "congestion_component": row.get('congestion_component', 0),
                        "loss_component": row.get('loss_component', 0),
                    })

                count = archive.write_rtm_lmp_api(records)
                total += count
                print(f"  {current.date()}: {count:,} records")

        except Exception as e:
            print(f"  {current.date()}: Error - {e}")

        current = next_day

    return total


def backfill_rtm_cdr(client: InfluxDBClient3, archive: SQLiteArchive,
                     start_date: datetime, end_date: datetime) -> int:
    """Backfill RTM LMP CDR (realtime) data day by day"""
    print("\nBackfilling rtm_lmp_realtime (CDR)...")
    total = 0
    current = start_date

    while current < end_date:
        next_day = current + timedelta(days=1)

        query = f'''
        SELECT time, settlement_point, lmp
        FROM "rtm_lmp_realtime"
        WHERE time >= '{current.isoformat()}' AND time < '{next_day.isoformat()}'
        '''

        try:
            result = client.query(query)
            df = result.to_pandas()

            if not df.empty:
                records = []
                for _, row in df.iterrows():
                    records.append({
                        "time": row['time'],
                        "settlement_point": row.get('settlement_point', ''),
                        "lmp": row.get('lmp', 0),
                    })

                count = archive.write_rtm_lmp_cdr(records)
                total += count
                print(f"  {current.date()}: {count:,} records")

        except Exception as e:
            if "Table or CTE with name" not in str(e):  # Ignore table not found
                print(f"  {current.date()}: Error - {e}")

        current = next_day

    return total


def backfill_dam(client: InfluxDBClient3, archive: SQLiteArchive,
                 start_date: datetime, end_date: datetime) -> int:
    """Backfill DAM LMP data day by day"""
    print("\nBackfilling dam_lmp...")
    total = 0
    current = start_date

    while current < end_date:
        next_day = current + timedelta(days=1)

        query = f'''
        SELECT time, settlement_point, settlement_point_type, lmp
        FROM "dam_lmp"
        WHERE time >= '{current.isoformat()}' AND time < '{next_day.isoformat()}'
        '''

        try:
            result = client.query(query)
            df = result.to_pandas()

            if not df.empty:
                records = []
                for _, row in df.iterrows():
                    records.append({
                        "time": row['time'],
                        "settlement_point": row.get('settlement_point', ''),
                        "settlement_point_type": row.get('settlement_point_type', ''),
                        "lmp": row.get('lmp', 0),
                    })

                count = archive.write_dam_lmp(records)
                total += count
                print(f"  {current.date()}: {count:,} records")

        except Exception as e:
            print(f"  {current.date()}: Error - {e}")

        current = next_day

    return total


def main():
    parser = ArgumentParser(description="Backfill SQLite archive from InfluxDB")
    parser.add_argument(
        "--start-date",
        type=str,
        default="2026-01-22",
        help="Start date (YYYY-MM-DD). Default: 2026-01-22",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="End date (YYYY-MM-DD). Default: today",
    )
    parser.add_argument(
        "--tables",
        type=str,
        default="all",
        help="Tables to backfill: all, rtm_api, rtm_cdr, dam",
    )
    args = parser.parse_args()

    start_date = datetime.fromisoformat(args.start_date).replace(tzinfo=timezone.utc)
    end_date = (
        datetime.fromisoformat(args.end_date).replace(tzinfo=timezone.utc)
        if args.end_date
        else datetime.now(timezone.utc)
    )

    print("=" * 60)
    print("Backfill SQLite Archive from InfluxDB")
    print("=" * 60)
    print(f"Start date: {start_date.date()}")
    print(f"End date: {end_date.date()}")
    print(f"Tables: {args.tables}")
    print()

    # Initialize clients
    print("Initializing clients...")
    client = get_influxdb_client()
    archive = SQLiteArchive()
    print(f"SQLite DB: {archive.db_path}")

    total = 0

    if args.tables in ("all", "rtm_api"):
        total += backfill_rtm_api(client, archive, start_date, end_date)

    if args.tables in ("all", "rtm_cdr"):
        total += backfill_rtm_cdr(client, archive, start_date, end_date)

    if args.tables in ("all", "dam"):
        total += backfill_dam(client, archive, start_date, end_date)

    # Show summary
    print()
    print("=" * 60)
    print("SQLite Archive Status:")
    for table in ["rtm_lmp_api", "rtm_lmp_cdr", "dam_lmp"]:
        try:
            count = archive.get_record_count(table)
            min_t, max_t = archive.get_time_range(table)
            print(f"  {table}: {count:,} records ({min_t} to {max_t})")
        except:
            print(f"  {table}: (empty)")
    print("=" * 60)
    print(f"Total new records: {total:,}")
    print("=" * 60)

    # Close connections
    client.close()
    archive.close()


if __name__ == "__main__":
    main()
