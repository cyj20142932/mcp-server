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