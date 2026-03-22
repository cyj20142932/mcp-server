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

    # ========== 数据探索方法 ==========

    def get_columns(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """Get column information for a table."""
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                DATA_TYPE || '(' || DATA_LENGTH || ')' as COLUMN_TYPE,
                NULLABLE,
                DATA_DEFAULT,
                COLUMN_ID
            FROM ALL_TAB_COLUMNS
            WHERE OWNER = :schema AND TABLE_NAME = :table_name
            ORDER BY COLUMN_ID
        """, {"schema": schema, "table_name": table_name})

        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()

        # 转换Oracle数据类型
        for r in results:
            r["IS_NULLABLE"] = "YES" if r.get("NULLABLE") == "Y" else "NO"
            r["COLUMN_KEY"] = ""
            r["EXTRA"] = ""
            r["COLUMN_COMMENT"] = ""
        return results

    def get_views(self, schema_name: str = None) -> List[str]:
        """Get list of views."""
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT VIEW_NAME FROM ALL_VIEWS
            WHERE OWNER = :schema
        """, {"schema": schema})
        views = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return views

    def get_view_ddl(self, view_name: str, schema_name: str = None) -> str:
        """Get DDL for a view."""
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT TEXT FROM ALL_VIEWS
            WHERE OWNER = :schema AND VIEW_NAME = :view_name
        """, {"schema": schema, "view_name": view_name})
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else ""

    def get_indexes(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """Get index information for a table."""
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT
                a.INDEX_NAME,
                a.UNIQUENESS,
                b.COLUMN_POSITION,
                b.COLUMN_NAME
            FROM ALL_INDEXES a
            LEFT JOIN ALL_IND_COLUMNS b ON a.INDEX_NAME = b.INDEX_NAME AND a.OWNER = b.INDEX_OWNER
            WHERE a.TABLE_OWNER = :schema AND a.TABLE_NAME = :table_name
            ORDER BY a.INDEX_NAME, b.COLUMN_POSITION
        """, {"schema": schema, "table_name": table_name})

        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()

        # 转换字段名
        for r in results:
            r["NON_UNIQUE"] = 0 if r.get("UNIQUENESS") == "UNIQUE" else 1
            r["SEQ_IN_INDEX"] = r.pop("COLUMN_POSITION", 1)
            r["CARDINALITY"] = ""
        return results

    def get_constraints(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """Get constraint information for a table."""
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT
                CONSTRAINT_NAME,
                CONSTRAINT_TYPE,
                TABLE_NAME,
                STATUS
            FROM ALL_CONSTRAINTS
            WHERE OWNER = :schema AND TABLE_NAME = :table_name
        """, {"schema": schema, "table_name": table_name})

        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results

    def get_foreign_keys(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """Get foreign key information for a table."""
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT
                a.CONSTRAINT_NAME,
                a.TABLE_NAME,
                b.COLUMN_NAME,
                c.TABLE_NAME AS REFERENCED_TABLE_NAME,
                d.COLUMN_NAME AS REFERENCED_COLUMN_NAME
            FROM ALL_CONSTRAINTS a
            JOIN ALL_CONS_COLUMNS b ON a.CONSTRAINT_NAME = b.CONSTRAINT_NAME AND a.OWNER = b.OWNER
            JOIN ALL_CONSTRAINTS c ON a.R_CONSTRAINT_NAME = c.CONSTRAINT_NAME AND a.R_OWNER = c.OWNER
            JOIN ALL_CONS_COLUMNS d ON c.CONSTRAINT_NAME = d.CONSTRAINT_NAME AND c.OWNER = d.OWNER AND b.POSITION = d.POSITION
            WHERE a.OWNER = :schema AND a.TABLE_NAME = :table_name AND a.CONSTRAINT_TYPE = 'R'
        """, {"schema": schema, "table_name": table_name})

        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results

    def get_procedures(self, schema_name: str = None) -> List[str]:
        """Get list of stored procedures."""
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT OBJECT_NAME FROM ALL_PROCEDURES
            WHERE OWNER = :schema AND OBJECT_TYPE = 'PROCEDURE'
        """, {"schema": schema})
        procedures = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return procedures

    def get_procedure_ddl(self, procedure_name: str, schema_name: str = None) -> str:
        """Get DDL for a stored procedure."""
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT TEXT FROM ALL_SOURCE
            WHERE OWNER = :schema AND NAME = :proc_name AND TYPE = 'PROCEDURE'
            ORDER BY LINE
        """, {"schema": schema, "proc_name": procedure_name.upper()})
        lines = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return "".join(lines)

    def get_functions(self, schema_name: str = None) -> List[str]:
        """Get list of functions."""
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT OBJECT_NAME FROM ALL_PROCEDURES
            WHERE OWNER = :schema AND OBJECT_TYPE = 'FUNCTION'
        """, {"schema": schema})
        functions = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return functions

    # ========== 数据操作方法 ==========

    def insert_data(self, table_name: str, data: List[Dict[str, Any]], schema_name: str = None) -> int:
        """Insert data into a table."""
        if not self._conn:
            self.connect()

        if not data:
            return 0

        cursor = self._conn.cursor()
        columns = list(data[0].keys())
        placeholders = ", ".join([":{}".format(i) for i in range(len(columns))])
        column_names = ", ".join(f'"{col}"' for col in columns)
        sql = f'INSERT INTO "{table_name}" ({column_names}) VALUES ({placeholders})'

        for row in data:
            values = {i: row.get(col) for i, col in enumerate(columns)}
            cursor.execute(sql, values)

        affected = cursor.rowcount
        cursor.close()
        return affected

    def update_data(self, table_name: str, data: Dict[str, Any], where: Dict[str, Any], schema_name: str = None) -> int:
        """Update data in a table."""
        if not self._conn:
            self.connect()

        if not data or not where:
            return 0

        set_clause = ", ".join(f'"{k}" = :set_{k}' for k in data.keys())
        where_clause = " AND ".join(f'"{k}" = :where_{k}' for k in where.keys())
        sql = f'UPDATE "{table_name}" SET {set_clause} WHERE {where_clause}'

        params = {f"set_{k}": v for k, v in data.items()}
        params.update({f"where_{k}": v for k, v in where.items()})

        cursor = self._conn.cursor()
        cursor.execute(sql, params)
        affected = cursor.rowcount
        cursor.close()
        return affected

    def delete_data(self, table_name: str, where: Dict[str, Any], schema_name: str = None) -> int:
        """Delete data from a table."""
        if not self._conn:
            self.connect()

        if not where:
            return 0

        where_clause = " AND ".join(f'"{k}" = :{k}' for k in where.keys())
        sql = f'DELETE FROM "{table_name}" WHERE {where_clause}'

        cursor = self._conn.cursor()
        cursor.execute(sql, where)
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