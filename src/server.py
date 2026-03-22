"""MCP Database Server."""
import sys
import os
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP

mcp = FastMCP("mcp-db-server")


@mcp.tool()
def get_ddl(connect_id: str, table_name: str, schema_name: str = None) -> str:
    """Get DDL for a specific table."""
    from src.tools import ddl
    return ddl.get_ddl(connect_id, table_name, schema_name)


@mcp.tool()
def get_tables(connect_id: str, schema_name: str = None) -> str:
    """Get list of tables in a database."""
    from src.tools import ddl
    tables = ddl.get_tables(connect_id, schema_name)
    return "\n".join(tables)


@mcp.tool()
def execute_query(connect_id: str, sql: str, max_rows: int = 1000) -> str:
    """Execute SQL query and return results."""
    from src.tools import query
    results = query.execute_query(connect_id, sql, max_rows)
    if not results:
        return "No results"

    # Format as table
    headers = list(results[0].keys())
    rows = [[str(row.get(h, "")) for h in headers] for row in results]

    # Build output
    col_widths = [max(len(h), max(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    separator = "-+-".join("-" * w for w in col_widths)

    lines = [header_line, separator]
    for row in rows:
        lines.append(" | ".join(cell.ljust(w) for cell, w in zip(row, col_widths)))

    return "\n".join(lines)


# ========== 数据探索工具 ==========

@mcp.tool()
def get_columns(connect_id: str, table_name: str, schema_name: str = None) -> str:
    """Get column information for a table (name, type, nullable, default, comment)."""
    from src.tools import metadata
    return metadata.get_columns(connect_id, table_name, schema_name)


@mcp.tool()
def get_views(connect_id: str, schema_name: str = None) -> str:
    """Get list of views in a database."""
    from src.tools import metadata
    return metadata.get_views(connect_id, schema_name)


@mcp.tool()
def get_view_ddl(connect_id: str, view_name: str, schema_name: str = None) -> str:
    """Get DDL definition for a view."""
    from src.tools import metadata
    return metadata.get_view_ddl(connect_id, view_name, schema_name)


@mcp.tool()
def get_indexes(connect_id: str, table_name: str, schema_name: str = None) -> str:
    """Get index information for a table."""
    from src.tools import metadata
    return metadata.get_indexes(connect_id, table_name, schema_name)


@mcp.tool()
def get_constraints(connect_id: str, table_name: str, schema_name: str = None) -> str:
    """Get constraint information for a table."""
    from src.tools import metadata
    return metadata.get_constraints(connect_id, table_name, schema_name)


@mcp.tool()
def get_foreign_keys(connect_id: str, table_name: str, schema_name: str = None) -> str:
    """Get foreign key relationships for a table."""
    from src.tools import metadata
    return metadata.get_foreign_keys(connect_id, table_name, schema_name)


@mcp.tool()
def get_procedures(connect_id: str, schema_name: str = None) -> str:
    """Get list of stored procedures. (MySQL, Oracle only)"""
    from src.tools import metadata
    return metadata.get_procedures(connect_id, schema_name)


@mcp.tool()
def get_procedure_ddl(connect_id: str, procedure_name: str, schema_name: str = None) -> str:
    """Get DDL definition for a stored procedure. (MySQL, Oracle only)"""
    from src.tools import metadata
    return metadata.get_procedure_ddl(connect_id, procedure_name, schema_name)


@mcp.tool()
def get_functions(connect_id: str, schema_name: str = None) -> str:
    """Get list of functions. (MySQL, Oracle only)"""
    from src.tools import metadata
    return metadata.get_functions(connect_id, schema_name)


# ========== 数据操作工具 ==========

@mcp.tool()
def insert_data(connect_id: str, table_name: str, data: str, schema_name: str = None) -> str:
    """Insert single or batch data into a table. Data should be JSON array of objects."""
    from src.tools import manipulation
    try:
        data_list = json.loads(data)
        if isinstance(data_list, dict):
            data_list = [data_list]
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "Invalid JSON data"}, ensure_ascii=False, indent=2)
    return manipulation.insert_data(connect_id, table_name, data_list, schema_name)


@mcp.tool()
def update_data(connect_id: str, table_name: str, data: str, where: str, schema_name: str = None) -> str:
    """Update data in a table with WHERE conditions. Data and where should be JSON objects."""
    from src.tools import manipulation
    try:
        data_dict = json.loads(data)
        where_dict = json.loads(where)
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "Invalid JSON format"}, ensure_ascii=False, indent=2)
    return manipulation.update_data(connect_id, table_name, data_dict, where_dict, schema_name)


@mcp.tool()
def delete_data(connect_id: str, table_name: str, where: str, schema_name: str = None) -> str:
    """Delete data from a table with WHERE conditions. Where should be a JSON object."""
    from src.tools import manipulation
    try:
        where_dict = json.loads(where)
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "Invalid JSON format"}, ensure_ascii=False, indent=2)
    return manipulation.delete_data(connect_id, table_name, where_dict, schema_name)


@mcp.tool()
def begin_transaction(connect_id: str) -> str:
    """Begin a transaction session. After this, use transaction_insert/update/delete."""
    from src.tools import manipulation
    return manipulation.begin_transaction(connect_id)


@mcp.tool()
def commit_transaction(connect_id: str) -> str:
    """Commit current transaction."""
    from src.tools import manipulation
    return manipulation.commit_transaction(connect_id)


@mcp.tool()
def rollback_transaction(connect_id: str) -> str:
    """Rollback current transaction."""
    from src.tools import manipulation
    return manipulation.rollback_transaction(connect_id)


def main():
    """Main entry point."""
    mcp.run()


if __name__ == "__main__":
    main()