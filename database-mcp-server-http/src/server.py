"""MCP Database Server - 数据库 MCP 服务器 (支持 Streamable HTTP)"""
import sys
import os
import argparse
from pathlib import Path
import json

# 添加父目录到路径以便导入模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP

mcp = FastMCP("mcp-db-server-sse")


@mcp.tool()
def get_ddl(connect_id: str, table_name: str, schema_name: str = None) -> str:
    """获取指定表的 DDL 定义。"""
    from src.tools import ddl
    return ddl.get_ddl(connect_id, table_name, schema_name)


@mcp.tool()
def get_tables(connect_id: str, schema_name: str = None) -> str:
    """获取数据库中的所有表。"""
    from src.tools import ddl
    tables = ddl.get_tables(connect_id, schema_name)
    return "\n".join(tables)


@mcp.tool()
def execute_query(connect_id: str, sql: str, max_rows: int = 1000) -> str:
    """执行 SQL 查询并返回结果。"""
    from src.tools import query
    results = query.execute_query(connect_id, sql, max_rows)
    if not results:
        return "无结果"

    # 格式化为表格
    headers = list(results[0].keys())
    rows = [[str(row.get(h, "")) for h in headers] for row in results]

    # 构建输出
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
    """获取表的列信息（名称、类型、是否可空、默认值、注释）。"""
    from src.tools import metadata
    return metadata.get_columns(connect_id, table_name, schema_name)


@mcp.tool()
def get_views(connect_id: str, schema_name: str = None) -> str:
    """获取数据库中的视图列表。"""
    from src.tools import metadata
    return metadata.get_views(connect_id, schema_name)


@mcp.tool()
def get_view_ddl(connect_id: str, view_name: str, schema_name: str = None) -> str:
    """获取视图的 DDL 定义。"""
    from src.tools import metadata
    return metadata.get_view_ddl(connect_id, view_name, schema_name)


@mcp.tool()
def get_indexes(connect_id: str, table_name: str, schema_name: str = None) -> str:
    """获取表的索引信息。"""
    from src.tools import metadata
    return metadata.get_indexes(connect_id, table_name, schema_name)


@mcp.tool()
def get_constraints(connect_id: str, table_name: str, schema_name: str = None) -> str:
    """获取表的约束信息。"""
    from src.tools import metadata
    return metadata.get_constraints(connect_id, table_name, schema_name)


@mcp.tool()
def get_foreign_keys(connect_id: str, table_name: str, schema_name: str = None) -> str:
    """获取表的外键关系。"""
    from src.tools import metadata
    return metadata.get_foreign_keys(connect_id, table_name, schema_name)


@mcp.tool()
def get_procedures(connect_id: str, schema_name: str = None) -> str:
    """获取存储过程列表。（仅支持 MySQL、Oracle）"""
    from src.tools import metadata
    return metadata.get_procedures(connect_id, schema_name)


@mcp.tool()
def get_procedure_ddl(connect_id: str, procedure_name: str, schema_name: str = None) -> str:
    """获取存储过程的 DDL 定义。（仅支持 MySQL、Oracle）"""
    from src.tools import metadata
    return metadata.get_procedure_ddl(connect_id, procedure_name, schema_name)


@mcp.tool()
def get_functions(connect_id: str, schema_name: str = None) -> str:
    """获取函数列表。（仅支持 MySQL、Oracle）"""
    from src.tools import metadata
    return metadata.get_functions(connect_id, schema_name)


# ========== 数据操作工具 ==========

@mcp.tool()
def insert_data(connect_id: str, table_name: str, data: str, schema_name: str = None) -> str:
    """向表中插入单条或批量数据。data 应为 JSON 对象数组。"""
    from src.tools import manipulation
    try:
        data_list = json.loads(data)
        if isinstance(data_list, dict):
            data_list = [data_list]
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "无效的 JSON 数据"}, ensure_ascii=False, indent=2)
    return manipulation.insert_data(connect_id, table_name, data_list, schema_name)


@mcp.tool()
def update_data(connect_id: str, table_name: str, data: str, where: str, schema_name: str = None) -> str:
    """使用 WHERE 条件更新表中的数据。data 和 where 应为 JSON 对象。"""
    from src.tools import manipulation
    try:
        data_dict = json.loads(data)
        where_dict = json.loads(where)
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "无效的 JSON 格式"}, ensure_ascii=False, indent=2)
    return manipulation.update_data(connect_id, table_name, data_dict, where_dict, schema_name)


@mcp.tool()
def delete_data(connect_id: str, table_name: str, where: str, schema_name: str = None) -> str:
    """使用 WHERE 条件删除表中的数据。where 应为 JSON 对象。"""
    from src.tools import manipulation
    try:
        where_dict = json.loads(where)
    except json.JSONDecodeError:
        return json.dumps({"success": False, "error": "无效的 JSON 格式"}, ensure_ascii=False, indent=2)
    return manipulation.delete_data(connect_id, table_name, where_dict, schema_name)


@mcp.tool()
def begin_transaction(connect_id: str) -> str:
    """开始事务会话。之后使用 transaction_insert/update/delete。"""
    from src.tools import manipulation
    return manipulation.begin_transaction(connect_id)


@mcp.tool()
def commit_transaction(connect_id: str) -> str:
    """提交当前事务。"""
    from src.tools import manipulation
    return manipulation.commit_transaction(connect_id)


@mcp.tool()
def rollback_transaction(connect_id: str) -> str:
    """回滚当前事务。"""
    from src.tools import manipulation
    return manipulation.rollback_transaction(connect_id)


def main():
    """主入口点。"""
    parser = argparse.ArgumentParser(description="MCP Database Server (Streamable HTTP 支持)")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="传输协议: stdio 或 streamable-http (默认: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Streamable HTTP 模式下的端口号 (默认: 8080)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Streamable HTTP 模式下的主机地址 (默认: 0.0.0.0)"
    )
    args = parser.parse_args()

    if args.transport == "streamable-http":
        print(f"启动 Streamable HTTP 服务器: {args.host}:{args.port}", file=sys.stderr)
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()