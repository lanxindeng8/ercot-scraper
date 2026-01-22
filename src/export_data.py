#!/usr/bin/env python3
"""
InfluxDB Data Exporter

Exports data from InfluxDB to CSV for backup purposes.
"""

import os
import sys
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient


def export_measurement(
    client: InfluxDBClient,
    bucket: str,
    org: str,
    measurement: str,
    days: int = 7,
    output_file: str = None,
):
    """
    Export a measurement to CSV

    Args:
        client: InfluxDB client
        bucket: Bucket name
        org: Organization
        measurement: Measurement name
        days: Number of days to export
        output_file: Output file path (optional)
    """
    if not output_file:
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        output_file = f"{measurement}_{timestamp}.csv"

    print(f"Exporting {measurement} (last {days} days) to {output_file}...")

    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -{days}d)
      |> filter(fn: (r) => r._measurement == "{measurement}")
      |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
    '''

    query_api = client.query_api()

    try:
        # Query data
        result = query_api.query_csv(query, org=org)

        # Write to file
        with open(output_file, 'w') as f:
            f.write(result)

        print(f"Successfully exported to {output_file}")
        return output_file

    except Exception as e:
        print(f"Error exporting {measurement}: {e}")
        raise


def main():
    """Main export function"""
    print(f"Starting data export at {datetime.utcnow().isoformat()}")

    try:
        # Get configuration from environment
        url = os.environ["INFLUXDB_URL"]
        token = os.environ["INFLUXDB_TOKEN"]
        org = os.environ["INFLUXDB_ORG"]
        bucket = os.environ.get("INFLUXDB_BUCKET") or os.environ.get("INFLUXDB_DATABASE", "ercot")

        # Number of days to export (default 7)
        days = int(os.environ.get("EXPORT_DAYS", "7"))

        # Initialize client
        print("Connecting to InfluxDB...")
        client = InfluxDBClient(url=url, token=token, org=org)

        # Export measurements
        measurements = [
            "lmp_by_settlement_point",
            "spp_day_ahead_hourly",
        ]

        exported_files = []

        for measurement in measurements:
            try:
                output_file = export_measurement(
                    client, bucket, org, measurement, days
                )
                exported_files.append(output_file)
            except Exception as e:
                print(f"Failed to export {measurement}: {e}")

        # Close client
        client.close()

        print(f"\nExport completed! Exported {len(exported_files)} files:")
        for f in exported_files:
            print(f"  - {f}")

        return 0

    except Exception as e:
        print(f"Error in data export: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
