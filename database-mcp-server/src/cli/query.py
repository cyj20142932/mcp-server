"""Query 子命令 - 执行 SQL 查询和列出表"""
import click
from .context import get_connection
from .formatter import format_results, format_list


@click.group(name="query")
def query_group():
    """Query 相关命令"""
    pass


@query_group.command(name="exec")
@click.argument("sql")
@click.option("--max-rows", default=1000, help="最大返回行数，默认 1000")
@click.option("--json", "output_json", is_flag=True, help="JSON 格式输出")
@click.option("--csv", "output_csv", is_flag=True, help="CSV 格式输出")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def exec_query(sql: str, max_rows: int, output_json: bool, output_csv: bool, connect_id: str, config: str):
    """执行 SQL 查询

    SQL: 要执行的 SQL 语句
    """
    from src.tools import query as query_tools

    cid, _ = get_connection(connect_id, config)
    results = query_tools.execute_query(cid, sql, max_rows)

    # 确定输出格式
    if output_json:
        fmt = "json"
    elif output_csv:
        fmt = "csv"
    else:
        fmt = "table"

    click.echo(format_results(results, fmt))


@query_group.command(name="tables")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def list_tables(schema: str, connect_id: str, config: str):
    """列出所有表"""
    from src.tools import ddl as ddl_tools

    cid, _ = get_connection(connect_id, config)
    tables = ddl_tools.get_tables(cid, schema)
    click.echo(format_list(tables))