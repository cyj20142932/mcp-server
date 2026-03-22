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

    # ========== 数据探索方法 ==========

    def get_columns(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """Get column information for a table."""
        if not self._conn or not self._conn.is_connected():
            self.connect()

        db = self.config.database
        cursor = self._conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                COLUMN_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                COLUMN_KEY,
                EXTRA,
                COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """, (db, table_name))
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_views(self, schema_name: str = None) -> List[str]:
        """Get list of views."""
        if not self._conn or not self._conn.is_connected():
            self.connect()

        db = self.config.database
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS
            WHERE TABLE_SCHEMA = %s
        """, (db,))
        views = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return views

    def get_view_ddl(self, view_name: str, schema_name: str = None) -> str:
        """Get DDL for a view."""
        if not self._conn or not self._conn.is_connected():
            self.connect()

        db = self.config.database
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT VIEW_DEFINITION FROM INFORMATION_SCHEMA.VIEWS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """, (db, view_name))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else ""

    def get_indexes(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """Get index information for a table."""
        if not self._conn or not self._conn.is_connected():
            self.connect()

        db = self.config.database
        cursor = self._conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                INDEX_NAME,
                NON_UNIQUE,
                SEQ_IN_INDEX,
                COLUMN_NAME,
                CARDINALITY
            FROM INFORMATION_SCHEMA.STATISTICS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY INDEX_NAME, SEQ_IN_INDEX
        """, (db, table_name))
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_constraints(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """Get constraint information for a table."""
        if not self._conn or not self._conn.is_connected():
            self.connect()

        db = self.config.database
        cursor = self._conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                CONSTRAINT_NAME,
                CONSTRAINT_TYPE,
                TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        """, (db, table_name))
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_foreign_keys(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """Get foreign key information for a table."""
        if not self._conn or not self._conn.is_connected():
            self.connect()

        db = self.config.database
        cursor = self._conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                CONSTRAINT_NAME,
                TABLE_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = %s
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """, (db, table_name))
        results = cursor.fetchall()
        cursor.close()
        return results

    def get_procedures(self, schema_name: str = None) -> List[str]:
        """Get list of stored procedures. StarRocks不支持存储过程。"""
        return []

    def get_procedure_ddl(self, procedure_name: str, schema_name: str = None) -> str:
        """Get DDL for a stored procedure. StarRocks不支持存储过程。"""
        return ""

    def get_functions(self, schema_name: str = None) -> List[str]:
        """Get list of functions. StarRocks不支持自定义函数。"""
        return []

    # ========== 数据操作方法 ==========

    def insert_data(self, table_name: str, data: List[Dict[str, Any]], schema_name: str = None) -> int:
        """Insert data into a table."""
        if not self._conn or not self._conn.is_connected():
            self.connect()

        if not data:
            return 0

        cursor = self._conn.cursor()
        columns = list(data[0].keys())
        placeholders = ", ".join(["%s"] * len(columns))
        column_names = ", ".join(f"`{col}`" for col in columns)
        sql = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({placeholders})"

        for row in data:
            values = tuple(row.get(col) for col in columns)
            cursor.execute(sql, values)

        affected = cursor.rowcount
        cursor.close()
        return affected

    def update_data(self, table_name: str, data: Dict[str, Any], where: Dict[str, Any], schema_name: str = None) -> int:
        """Update data in a table."""
        if not self._conn or not self._conn.is_connected():
            self.connect()

        if not data or not where:
            return 0

        set_clause = ", ".join(f"`{k}` = %s" for k in data.keys())
        where_clause = " AND ".join(f"`{k}` = %s" for k in where.keys())
        sql = f"UPDATE `{table_name}` SET {set_clause} WHERE {where_clause}"

        values = tuple(list(data.values()) + list(where.values()))
        cursor = self._conn.cursor()
        cursor.execute(sql, values)
        affected = cursor.rowcount
        cursor.close()
        return affected

    def delete_data(self, table_name: str, where: Dict[str, Any], schema_name: str = None) -> int:
        """Delete data from a table."""
        if not self._conn or not self._conn.is_connected():
            self.connect()

        if not where:
            return 0

        where_clause = " AND ".join(f"`{k}` = %s" for k in where.keys())
        sql = f"DELETE FROM `{table_name}` WHERE {where_clause}"

        cursor = self._conn.cursor()
        cursor.execute(sql, tuple(where.values()))
        affected = cursor.rowcount
        cursor.close()
        return affected

    def commit(self):
        """Commit current transaction."""
        if self._conn:
            self._conn.commit()

    def rollback(self):
        """Rollback current transaction."""
        if self._conn:
            self._conn.rollback()