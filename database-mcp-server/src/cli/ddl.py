"""DDL 子命令 - 获取表/视图的 DDL 定义"""
import click
from .context import get_connection
from .formatter import format_ddl, format_list


@click.group(name="ddl")
def ddl_group():
    """DDL 相关命令"""
    pass


@ddl_group.command(name="get")
@click.argument("table_name")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def get_ddl(table_name: str, schema: str, connect_id: str, config: str):
    """获取指定表的 DDL 定义"""
    from src.tools import ddl as ddl_tools

    cid, _ = get_connection(connect_id, config)
    result = ddl_tools.get_ddl(cid, table_name, schema)
    click.echo(format_ddl(result))


@ddl_group.command(name="tables")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def list_tables(schema: str, connect_id: str, config: str):
    """获取数据库中的所有表"""
    from src.tools import ddl as ddl_tools

    cid, _ = get_connection(connect_id, config)
    tables = ddl_tools.get_tables(cid, schema)
    click.echo(format_list(tables))


@ddl_group.command(name="view")
@click.argument("view_name")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def get_view(view_name: str, schema: str, connect_id: str, config: str):
    """获取视图的 DDL 定义"""
    from src.tools import metadata

    cid, _ = get_connection(connect_id, config)
    result = metadata.get_view_ddl(cid, view_name, schema)
    click.echo(format_ddl(result))