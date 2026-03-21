"""Database module."""
from .base import DatabaseBase
from .mysql import MySQLDatabase
from .oracle import OracleDatabase
from .starrocks import StarRocksDatabase

DATABASE_CLASSES = {
    "mysql": MySQLDatabase,
    "oracle": OracleDatabase,
    "starrocks": StarRocksDatabase,
}


def create_database(config) -> DatabaseBase:
    """Create database instance based on config type."""
    db_type = config.type.lower()
    if db_type not in DATABASE_CLASSES:
        raise ValueError(f"Unsupported database type: {db_type}")
    return DATABASE_CLASSES[db_type](config)