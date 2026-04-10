"""Metadata 子命令 - 获取数据库元数据信息"""
import click
import json
from .context import get_connection
from .formatter import format_table, format_list


@click.group(name="metadata")
def metadata_group():
    """元数据查询命令"""
    pass


@metadata_group.command(name="columns")
@click.argument("table")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
@click.option("--json", "as_json", is_flag=True, help="JSON 格式输出")
def get_columns(table: str, schema: str, connect_id: str, config: str, as_json: bool):
    """获取表的列信息"""
    from src.tools import metadata as metadata_tools

    cid, _ = get_connection(connect_id, config)
    result = metadata_tools.get_columns(cid, table, schema)

    if as_json:
        click.echo(result)
    else:
        # 解析 JSON 并格式化为表格
        data = json.loads(result)
        if not data:
            click.echo("无结果")
            return

        headers = list(data[0].keys())
        rows = [[str(row.get(h, "")) for h in headers] for row in data]
        click.echo(format_table(headers, rows))


@metadata_group.command(name="views")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def list_views(schema: str, connect_id: str, config: str):
    """获取视图列表"""
    from src.tools import metadata as metadata_tools

    cid, _ = get_connection(connect_id, config)
    views = metadata_tools.get_views(cid, schema)
    click.echo(format_list(views))


@metadata_group.command(name="indexes")
@click.argument("table")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
@click.option("--json", "as_json", is_flag=True, help="JSON 格式输出")
def get_indexes(table: str, schema: str, connect_id: str, config: str, as_json: bool):
    """获取表的索引信息"""
    from src.tools import metadata as metadata_tools

    cid, _ = get_connection(connect_id, config)
    result = metadata_tools.get_indexes(cid, table, schema)

    if as_json:
        click.echo(result)
    else:
        data = json.loads(result)
        if not data:
            click.echo("无结果")
            return

        headers = list(data[0].keys())
        rows = [[str(row.get(h, "")) for h in headers] for row in data]
        click.echo(format_table(headers, rows))


@metadata_group.command(name="constraints")
@click.argument("table")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
@click.option("--json", "as_json", is_flag=True, help="JSON 格式输出")
def get_constraints(table: str, schema: str, connect_id: str, config: str, as_json: bool):
    """获取表的约束信息"""
    from src.tools import metadata as metadata_tools

    cid, _ = get_connection(connect_id, config)
    result = metadata_tools.get_constraints(cid, table, schema)

    if as_json:
        click.echo(result)
    else:
        data = json.loads(result)
        if not data:
            click.echo("无结果")
            return

        headers = list(data[0].keys())
        rows = [[str(row.get(h, "")) for h in headers] for row in data]
        click.echo(format_table(headers, rows))


@metadata_group.command(name="foreign-keys")
@click.argument("table")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
@click.option("--json", "as_json", is_flag=True, help="JSON 格式输出")
def get_foreign_keys(table: str, schema: str, connect_id: str, config: str, as_json: bool):
    """获取表的外键信息"""
    from src.tools import metadata as metadata_tools

    cid, _ = get_connection(connect_id, config)
    result = metadata_tools.get_foreign_keys(cid, table, schema)

    if as_json:
        click.echo(result)
    else:
        data = json.loads(result)
        if not data:
            click.echo("无结果")
            return

        headers = list(data[0].keys())
        rows = [[str(row.get(h, "")) for h in headers] for row in data]
        click.echo(format_table(headers, rows))


@metadata_group.command(name="procedures")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def list_procedures(schema: str, connect_id: str, config: str):
    """获取存储过程列表"""
    from src.tools import metadata as metadata_tools

    cid, _ = get_connection(connect_id, config)
    procedures = metadata_tools.get_procedures(cid, schema)
    click.echo(format_list(procedures))


@metadata_group.command(name="functions")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def list_functions(schema: str, connect_id: str, config: str):
    """获取函数列表"""
    from src.tools import metadata as metadata_tools

    cid, _ = get_connection(connect_id, config)
    functions = metadata_tools.get_functions(cid, schema)
    click.echo(format_list(functions))