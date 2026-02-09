#!/usr/bin/env python3
"""
Archive ERCOT data from InfluxDB to SQLite.

Runs daily to archive data before InfluxDB Cloud 30-day retention expires.
Archives data from day -25 (5-day buffer before expiration).
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


def archive_rtm_api(client: InfluxDBClient3, archive: SQLiteArchive,
                    start_time: datetime, end_time: datetime) -> int:
    """Archive RTM LMP API data for a time range"""
    query = f'''
    SELECT time, settlement_point, lmp, energy_component, congestion_component, loss_component
    FROM "rtm_lmp_api"
    WHERE time >= '{start_time.isoformat()}' AND time < '{end_time.isoformat()}'
    '''

    try:
        result = client.query(query)
        df = result.to_pandas()

        if df.empty:
            print(f"  rtm_lmp_api: No data in range")
            return 0

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
        print(f"  rtm_lmp_api: Archived {count:,} records")
        return count

    except Exception as e:
        print(f"  rtm_lmp_api: Error - {e}")
        return 0


def archive_rtm_cdr(client: InfluxDBClient3, archive: SQLiteArchive,
                    start_time: datetime, end_time: datetime) -> int:
    """Archive RTM LMP CDR (realtime) data for a time range"""
    query = f'''
    SELECT time, settlement_point, lmp
    FROM "rtm_lmp_realtime"
    WHERE time >= '{start_time.isoformat()}' AND time < '{end_time.isoformat()}'
    '''

    try:
        result = client.query(query)
        df = result.to_pandas()

        if df.empty:
            print(f"  rtm_lmp_realtime: No data in range")
            return 0

        records = []
        for _, row in df.iterrows():
            records.append({
                "time": row['time'],
                "settlement_point": row.get('settlement_point', ''),
                "lmp": row.get('lmp', 0),
            })

        count = archive.write_rtm_lmp_cdr(records)
        print(f"  rtm_lmp_realtime: Archived {count:,} records")
        return count

    except Exception as e:
        print(f"  rtm_lmp_realtime: Error - {e}")
        return 0


def archive_dam(client: InfluxDBClient3, archive: SQLiteArchive,
                start_time: datetime, end_time: datetime) -> int:
    """Archive DAM LMP data for a time range"""
    query = f'''
    SELECT time, settlement_point, settlement_point_type, lmp
    FROM "dam_lmp"
    WHERE time >= '{start_time.isoformat()}' AND time < '{end_time.isoformat()}'
    '''

    try:
        result = client.query(query)
        df = result.to_pandas()

        if df.empty:
            print(f"  dam_lmp: No data in range")
            return 0

        records = []
        for _, row in df.iterrows():
            records.append({
                "time": row['time'],
                "settlement_point": row.get('settlement_point', ''),
                "settlement_point_type": row.get('settlement_point_type', ''),
                "lmp": row.get('lmp', 0),
            })

        count = archive.write_dam_lmp(records)
        print(f"  dam_lmp: Archived {count:,} records")
        return count

    except Exception as e:
        print(f"  dam_lmp: Error - {e}")
        return 0


def main():
    parser = ArgumentParser(description="Archive ERCOT data from InfluxDB to SQLite")
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Specific date to archive (YYYY-MM-DD). Default: today - 25 days",
    )
    parser.add_argument(
        "--days-ago",
        type=int,
        default=25,
        help="Days before today to archive. Default: 25 (5-day buffer before 30-day expiry)",
    )
    args = parser.parse_args()

    # Determine archive date
    if args.date:
        archive_date = datetime.fromisoformat(args.date).replace(tzinfo=timezone.utc)
    else:
        archive_date = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=args.days_ago)

    start_time = archive_date
    end_time = archive_date + timedelta(days=1)

    print("=" * 60)
    print("Archive ERCOT Data to SQLite")
    print("=" * 60)
    print(f"Archive date: {archive_date.date()}")
    print(f"Time range: {start_time.isoformat()} to {end_time.isoformat()}")
    print()

    # Initialize clients
    print("Initializing clients...")
    client = get_influxdb_client()
    archive = SQLiteArchive()
    print(f"SQLite DB: {archive.db_path}")
    print()

    # Archive each measurement
    print("Archiving data...")
    total = 0

    total += archive_rtm_api(client, archive, start_time, end_time)
    total += archive_rtm_cdr(client, archive, start_time, end_time)
    total += archive_dam(client, archive, start_time, end_time)

    # Close connections
    client.close()
    archive.close()

    print()
    print("=" * 60)
    print(f"Completed! Total records archived: {total:,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
