"""Base database interface."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class DatabaseBase(ABC):
    """Abstract base class for database operations."""

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def connect(self):
        """Establish database connection."""
        pass

    @abstractmethod
    def close(self):
        """Close database connection."""
        pass

    @abstractmethod
    def get_ddl(self, table_name: str, schema_name: str = None) -> str:
        """Get DDL for a table."""
        pass

    @abstractmethod
    def get_tables(self, schema_name: str = None) -> List[str]:
        """Get list of tables."""
        pass

    @abstractmethod
    def execute_query(self, sql: str, max_rows: int = 1000) -> List[Dict[str, Any]]:
        """Execute SQL query and return results."""
        pass

    # ========== 数据探索方法 ==========

    @abstractmethod
    def get_columns(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """Get column information for a table."""
        pass

    @abstractmethod
    def get_views(self, schema_name: str = None) -> List[str]:
        """Get list of views."""
        pass

    @abstractmethod
    def get_view_ddl(self, view_name: str, schema_name: str = None) -> str:
        """Get DDL for a view."""
        pass

    @abstractmethod
    def get_indexes(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """Get index information for a table."""
        pass

    @abstractmethod
    def get_constraints(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """Get constraint information for a table."""
        pass

    @abstractmethod
    def get_foreign_keys(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """Get foreign key information for a table."""
        pass

    def get_procedures(self, schema_name: str = None) -> List[str]:
        """Get list of stored procedures. Override in subclasses."""
        return []

    def get_procedure_ddl(self, procedure_name: str, schema_name: str = None) -> str:
        """Get DDL for a stored procedure. Override in subclasses."""
        return ""

    def get_functions(self, schema_name: str = None) -> List[str]:
        """Get list of functions. Override in subclasses."""
        return []

    # ========== 数据操作方法 ==========

    @abstractmethod
    def insert_data(self, table_name: str, data: List[Dict[str, Any]], schema_name: str = None) -> int:
        """Insert data into a table. Returns affected row count."""
        pass

    @abstractmethod
    def update_data(self, table_name: str, data: Dict[str, Any], where: Dict[str, Any], schema_name: str = None) -> int:
        """Update data in a table. Returns affected row count."""
        pass

    @abstractmethod
    def delete_data(self, table_name: str, where: Dict[str, Any], schema_name: str = None) -> int:
        """Delete data from a table. Returns affected row count."""
        pass

    @abstractmethod
    def commit(self):
        """Commit current transaction."""
        pass

    @abstractmethod
    def rollback(self):
        """Rollback current transaction."""
        pass