"""Oracle database implementation."""
import oracledb
from typing import List, Dict, Any
from .base import DatabaseBase


class OracleDatabase(DatabaseBase):
    """Oracle database operations."""

    def __init__(self, config):
        super().__init__(config)
        self._conn = None

    def connect(self):
        dsn = oracledb.makedsn(
            self.config.host,
            self.config.port,
            service_name=self.config.service_name
        )
        self._conn = oracledb.connect(
            user=self.config.user,
            password=self.config.password,
            dsn=dsn
        )

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def get_ddl(self, table_name: str, schema_name: str = None) -> str:
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute(f"""
            SELECT DBMS_METADATA.GET_DDL('TABLE', '{table_name}', '{schema}')
            FROM DUAL
        """)
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else ""

    def get_tables(self, schema_name: str = None) -> List[str]:
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute(f"""
            SELECT TABLE_NAME FROM ALL_TABLES
            WHERE OWNER = '{schema}'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def execute_query(self, sql: str, max_rows: int = 1000) -> List[Dict[str, Any]]:
        if not self._conn:
            self.connect()

        cursor = self._conn.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description] if cursor.description else []
        results = cursor.fetchmany(max_rows)
        cursor.close()
        return [dict(zip(columns, row)) for row in results]