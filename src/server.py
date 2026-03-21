"""MCP Database Server."""
import sys
import os
from pathlib import Path

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


def main():
    """Main entry point."""
    mcp.run()


if __name__ == "__main__":
    main()