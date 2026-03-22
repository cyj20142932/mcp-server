"""DDL retrieval tools."""
from typing import Optional, List
from ..config import get_config
from ..database import create_database


def get_ddl(connect_id: str, table_name: str, schema_name: Optional[str] = None) -> str:
    """
    Get DDL for a specific table.

    Args:
        connect_id: Database connection identifier
        table_name: Name of the table
        schema_name: Optional schema/database name

    Returns:
        DDL statement as string
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        return db.get_ddl(table_name, schema_name)
    finally:
        db.close()


def get_tables(connect_id: str, schema_name: Optional[str] = None) -> List[str]:
    """
    Get list of tables in a database.

    Args:
        connect_id: Database connection identifier
        schema_name: Optional schema/database name

    Returns:
        List of table names
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        return db.get_tables(schema_name)
    finally:
        db.close()