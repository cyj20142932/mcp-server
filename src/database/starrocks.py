"""StarRocks database implementation."""
import mysql.connector
from typing import List, Dict, Any
from .base import DatabaseBase


class StarRocksDatabase(DatabaseBase):
    """StarRocks database operations."""

    def __init__(self, config):
        super().__init__(config)
        self._conn = None

    def connect(self):
        self._conn = mysql.connector.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database
        )

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def get_ddl(self, table_name: str, schema_name: str = None) -> str:
        if not self._conn or not self._conn.is_connected():
            self.connect()

        cursor = self._conn.cursor()
        cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
        result = cursor.fetchone()
        cursor.close()
        return result[1] if result else ""

    def get_tables(self, schema_name: str = None) -> List[str]:
        if not self._conn or not self._conn.is_connected():
            self.connect()

        db = self.config.database
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{db}'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def execute_query(self, sql: str, max_rows: int = 1000) -> List[Dict[str, Any]]:
        if not self._conn or not self._conn.is_connected():
            self.connect()

        cursor = self._conn.cursor(dictionary=True)
        cursor.execute(sql)
        results = cursor.fetchmany(max_rows)
        cursor.close()
        return results