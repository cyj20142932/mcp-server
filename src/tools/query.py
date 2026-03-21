"""SQL query tools."""
from typing import Dict, Any, List
from ..config import get_config
from ..database import create_database


def execute_query(connect_id: str, sql: str, max_rows: int = 1000) -> List[Dict[str, Any]]:
    """
    Execute SQL query and return results.

    Args:
        connect_id: Database connection identifier
        sql: SQL query to execute
        max_rows: Maximum number of rows to return

    Returns:
        List of result rows as dictionaries
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        return db.execute_query(sql, max_rows)
    finally:
        db.close()