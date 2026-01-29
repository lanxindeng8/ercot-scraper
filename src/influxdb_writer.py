"""
InfluxDB Writer

Handles writing ERCOT data to InfluxDB Cloud Serverless (3.x).
Uses influxdb3-python for proper compatibility with InfluxDB 3.0.
"""

import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

from influxdb_client_3 import InfluxDBClient3, Point

# Rate limiting settings for InfluxDB Cloud free tier
BATCH_SIZE = 5000  # Write in smaller batches
BATCH_DELAY_SECONDS = 1  # Delay between batches
MAX_RETRIES = 3  # Max retries on rate limit
RETRY_DELAY_SECONDS = 60  # Wait time on 429 error


class InfluxDBWriter:
    """Writer for InfluxDB Cloud Serverless with rate limiting protection"""

    def __init__(
        self,
        url: str,
        token: str,
        org: str,
        database: str,
    ):
        """
        Initialize InfluxDB writer

        Args:
            url: InfluxDB URL (host)
            token: InfluxDB authentication token
            org: InfluxDB organization
            database: InfluxDB database (bucket) name
        """
        self.url = url
        self.token = token
        self.org = org
        self.database = database

        self.client = InfluxDBClient3(
            host=url.replace("https://", "").replace("http://", ""),
            token=token,
            org=org,
            database=database,
        )

    def close(self):
        """Close the InfluxDB client connection"""
        self.client.close()

    def write_lmp_data(self, records: List[Dict[str, Any]]) -> int:
        """
        Write LMP by Settlement Point data to InfluxDB

        Args:
            records: List of LMP records from ERCOT API

        Returns:
            Number of points written
        """
        if not records:
            print("No LMP records to write")
            return 0

        points = []

        for record in records:
            try:
                # Parse timestamp
                timestamp_str = record.get("SCEDTimestamp")
                if not timestamp_str:
                    continue

                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

                # Create point with tags as regular fields for InfluxDB 3.0
                # In InfluxDB 3.0, we use Point from influxdb_client_3
                point = (
                    Point("lmp_by_settlement_point")
                    .tag("settlement_point", record.get("SettlementPoint", ""))
                    .tag("settlement_point_type", record.get("SettlementPointType", ""))
                    .field("lmp", float(record.get("LMP", 0) or 0))
                    .field("energy_component", float(record.get("EnergyComponent", 0) or 0))
                    .field("congestion_component", float(record.get("CongestionComponent", 0) or 0))
                    .field("loss_component", float(record.get("LossComponent", 0) or 0))
                    .time(timestamp)
                )

                points.append(point)

            except Exception as e:
                print(f"Error creating point for LMP record: {e}")
                continue

        if points:
            return self._write_points_with_rate_limit(points, "LMP")

        return 0

    def _write_points_with_rate_limit(self, points: List[Point], data_type: str) -> int:
        """Write points in batches with rate limiting protection"""
        total_written = 0
        total_points = len(points)

        # Split into batches
        for i in range(0, total_points, BATCH_SIZE):
            batch = points[i:i + BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (total_points + BATCH_SIZE - 1) // BATCH_SIZE

            # Retry logic for rate limiting
            for retry in range(MAX_RETRIES):
                try:
                    self.client.write(record=batch)
                    total_written += len(batch)
                    print(f"Wrote batch {batch_num}/{total_batches}: {len(batch)} {data_type} points")
                    break
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "too many requests" in error_str.lower():
                        if retry < MAX_RETRIES - 1:
                            print(f"Rate limited, waiting {RETRY_DELAY_SECONDS}s before retry {retry + 2}/{MAX_RETRIES}...")
                            time.sleep(RETRY_DELAY_SECONDS)
                        else:
                            print(f"Max retries exceeded. Wrote {total_written}/{total_points} points.")
                            return total_written
                    else:
                        print(f"Error writing {data_type} points: {e}")
                        raise

            # Delay between batches to avoid rate limiting
            if i + BATCH_SIZE < total_points:
                time.sleep(BATCH_DELAY_SECONDS)

        print(f"Successfully wrote {total_written} {data_type} points to InfluxDB")
        return total_written

    def write_spp_day_ahead_data(self, records: List[Dict[str, Any]]) -> int:
        """
        Write Day-Ahead Settlement Point Prices to InfluxDB

        Args:
            records: List of SPP records from ERCOT API

        Returns:
            Number of points written
        """
        if not records:
            print("No SPP records to write")
            return 0

        points = []

        for record in records:
            try:
                # Parse delivery date and hour
                delivery_date = record.get("DeliveryDate")
                hour_ending = record.get("HourEnding")

                if not delivery_date or not hour_ending:
                    continue

                # Construct timestamp (delivery date + hour)
                # HourEnding format: "01:00", "02:00", etc.
                hour = int(hour_ending.split(":")[0])
                timestamp = datetime.fromisoformat(delivery_date)
                timestamp = timestamp.replace(hour=hour - 1)  # Hour ending 01:00 means hour 0

                # Create point
                point = (
                    Point("spp_day_ahead_hourly")
                    .tag("settlement_point", record.get("SettlementPoint", ""))
                    .tag("settlement_point_type", record.get("SettlementPointType", ""))
                    .field("settlement_point_price", float(record.get("SettlementPointPrice", 0) or 0))
                    .time(timestamp)
                )

                points.append(point)

            except Exception as e:
                print(f"Error creating point for SPP record: {e}")
                continue

        if points:
            return self._write_points_with_rate_limit(points, "SPP")

        return 0

    def get_last_timestamp(
        self, measurement: str, timestamp_field: str = "time"
    ) -> Optional[datetime]:
        """
        Get the last timestamp for a measurement using SQL

        Args:
            measurement: Measurement name (e.g., "lmp_by_settlement_point")
            timestamp_field: Timestamp field name

        Returns:
            Last timestamp or None if no data exists
        """
        query = f'''
        SELECT time FROM "{measurement}"
        ORDER BY time DESC
        LIMIT 1
        '''

        try:
            result = self.client.query(query)

            # Convert to pandas DataFrame and get the timestamp
            df = result.to_pandas()
            if not df.empty:
                last_time = df['time'].iloc[0]
                # Convert to datetime if needed
                if hasattr(last_time, 'to_pydatetime'):
                    return last_time.to_pydatetime()
                return last_time

            return None

        except Exception as e:
            print(f"Error querying last timestamp: {e}")
            return None


def create_writer_from_env() -> InfluxDBWriter:
    """
    Create InfluxDB writer from environment variables

    Required environment variables:
        - INFLUXDB_URL
        - INFLUXDB_TOKEN
        - INFLUXDB_ORG
        - INFLUXDB_BUCKET (or INFLUXDB_DATABASE)

    Returns:
        Configured InfluxDBWriter instance
    """
    return InfluxDBWriter(
        url=os.environ["INFLUXDB_URL"],
        token=os.environ["INFLUXDB_TOKEN"],
        org=os.environ["INFLUXDB_ORG"],
        database=os.environ.get("INFLUXDB_BUCKET") or os.environ.get("INFLUXDB_DATABASE", "ercot"),
    )
