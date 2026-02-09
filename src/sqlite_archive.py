"""
SQLite Archive Writer

Handles persistent storage of ERCOT LMP data in SQLite for historical analysis.
Data older than 30 days is archived here before InfluxDB Cloud retention expires.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent / "data" / "ercot_archive.db"


class SQLiteArchive:
    """Archive writer for persistent ERCOT data storage"""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize SQLite archive.

        Args:
            db_path: Path to SQLite database file. Default: data/ercot_archive.db
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema if not exists"""
        cursor = self.conn.cursor()

        # RTM LMP from API (finalized, ~6h delay)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rtm_lmp_api (
            time DATETIME NOT NULL,
            settlement_point TEXT NOT NULL,
            lmp REAL NOT NULL,
            energy_component REAL,
            congestion_component REAL,
            loss_component REAL,
            PRIMARY KEY (time, settlement_point)
        )
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_rtm_api_time ON rtm_lmp_api(time)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_rtm_api_sp ON rtm_lmp_api(settlement_point)
        """)

        # RTM LMP from CDR (real-time, for comparison)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rtm_lmp_cdr (
            time DATETIME NOT NULL,
            settlement_point TEXT NOT NULL,
            lmp REAL NOT NULL,
            PRIMARY KEY (time, settlement_point)
        )
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_rtm_cdr_time ON rtm_lmp_cdr(time)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_rtm_cdr_sp ON rtm_lmp_cdr(settlement_point)
        """)

        # DAM LMP (API only)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dam_lmp (
            time DATETIME NOT NULL,
            settlement_point TEXT NOT NULL,
            settlement_point_type TEXT,
            lmp REAL NOT NULL,
            PRIMARY KEY (time, settlement_point)
        )
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_dam_time ON dam_lmp(time)
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_dam_sp ON dam_lmp(settlement_point)
        """)

        self.conn.commit()

    def close(self):
        """Close database connection"""
        self.conn.close()

    def write_rtm_lmp_api(self, records: List[Dict[str, Any]]) -> int:
        """
        Write RTM LMP data from API to SQLite.

        Args:
            records: List of records with keys: time, settlement_point, lmp,
                     energy_component, congestion_component, loss_component

        Returns:
            Number of records written/updated
        """
        if not records:
            return 0

        cursor = self.conn.cursor()
        count = 0

        for record in records:
            try:
                time_val = record.get("time")
                if isinstance(time_val, str):
                    time_val = datetime.fromisoformat(time_val.replace("Z", "+00:00"))

                cursor.execute("""
                INSERT OR REPLACE INTO rtm_lmp_api
                (time, settlement_point, lmp, energy_component, congestion_component, loss_component)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    time_val.isoformat() if hasattr(time_val, 'isoformat') else str(time_val),
                    record.get("settlement_point", ""),
                    float(record.get("lmp", 0) or 0),
                    float(record.get("energy_component", 0) or 0),
                    float(record.get("congestion_component", 0) or 0),
                    float(record.get("loss_component", 0) or 0),
                ))
                count += 1
            except Exception as e:
                print(f"Error writing RTM API record: {e}")
                continue

        self.conn.commit()
        return count

    def write_rtm_lmp_cdr(self, records: List[Dict[str, Any]]) -> int:
        """
        Write RTM LMP data from CDR (real-time) to SQLite.

        Args:
            records: List of records with keys: time, settlement_point, lmp

        Returns:
            Number of records written/updated
        """
        if not records:
            return 0

        cursor = self.conn.cursor()
        count = 0

        for record in records:
            try:
                time_val = record.get("time")
                if isinstance(time_val, str):
                    time_val = datetime.fromisoformat(time_val.replace("Z", "+00:00"))

                cursor.execute("""
                INSERT OR REPLACE INTO rtm_lmp_cdr (time, settlement_point, lmp)
                VALUES (?, ?, ?)
                """, (
                    time_val.isoformat() if hasattr(time_val, 'isoformat') else str(time_val),
                    record.get("settlement_point", ""),
                    float(record.get("lmp", 0) or 0),
                ))
                count += 1
            except Exception as e:
                print(f"Error writing RTM CDR record: {e}")
                continue

        self.conn.commit()
        return count

    def write_dam_lmp(self, records: List[Dict[str, Any]]) -> int:
        """
        Write DAM LMP data to SQLite.

        Args:
            records: List of records with keys: time, settlement_point,
                     settlement_point_type, lmp

        Returns:
            Number of records written/updated
        """
        if not records:
            return 0

        cursor = self.conn.cursor()
        count = 0

        for record in records:
            try:
                time_val = record.get("time")
                if isinstance(time_val, str):
                    time_val = datetime.fromisoformat(time_val.replace("Z", "+00:00"))

                cursor.execute("""
                INSERT OR REPLACE INTO dam_lmp
                (time, settlement_point, settlement_point_type, lmp)
                VALUES (?, ?, ?, ?)
                """, (
                    time_val.isoformat() if hasattr(time_val, 'isoformat') else str(time_val),
                    record.get("settlement_point", ""),
                    record.get("settlement_point_type", ""),
                    float(record.get("lmp", 0) or 0),
                ))
                count += 1
            except Exception as e:
                print(f"Error writing DAM record: {e}")
                continue

        self.conn.commit()
        return count

    def get_record_count(self, table: str) -> int:
        """Get total record count for a table"""
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        return cursor.fetchone()[0]

    def get_time_range(self, table: str) -> tuple:
        """Get min and max time for a table"""
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT MIN(time), MAX(time) FROM "{table}"')
        row = cursor.fetchone()
        return row[0], row[1]

    def get_last_time(self, table: str) -> Optional[datetime]:
        """Get the latest timestamp in a table"""
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT MAX(time) FROM "{table}"')
        row = cursor.fetchone()
        if row[0]:
            return datetime.fromisoformat(row[0])
        return None
