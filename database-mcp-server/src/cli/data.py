"""Data 子命令 - 插入、更新、删除数据"""
import json
import click
from .context import get_connection
from .formatter import format_results


@click.group(name="data")
def data_group():
    """数据操作命令"""
    pass


@data_group.command(name="insert")
@click.argument("table")
@click.argument("data")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def insert_data_cmd(table: str, data: str, schema: str, connect_id: str, config: str):
    """插入数据

    TABLE: 表名

    DATA: JSON 格式的数据，如 '{"name": "张三", "age": 30}'
         或数组格式，如 '[{"name": "张三"}, {"name": "李四"}]'
    """
    from src.tools import manipulation as manip_tools

    cid, _ = get_connection(connect_id, config)

    # 解析 JSON 数据
    try:
        parsed_data = json.loads(data)
        # 确保是列表格式
        if isinstance(parsed_data, dict):
            parsed_data = [parsed_data]
        elif not isinstance(parsed_data, list):
            raise ValueError("数据必须是对象或对象数组")
    except json.JSONDecodeError as e:
        raise click.ClickException(f"JSON 解析失败: {e}")

    result = manip_tools.insert_data(cid, table, parsed_data, schema)

    # 解析结果并格式化输出
    try:
        result_obj = json.loads(result)
        if result_obj.get("success"):
            click.echo(f"✓ 插入成功，影响行数: {result_obj.get('affected_rows', 0)}")
        else:
            raise click.ClickException(f"插入失败: {result_obj.get('error')}")
    except Exception as e:
        raise click.ClickException(f"执行失败: {e}")


@data_group.command(name="update")
@click.argument("table")
@click.argument("data")
@click.argument("where")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def update_data_cmd(table: str, data: str, where: str, schema: str, connect_id: str, config: str):
    """更新数据

    TABLE: 表名

    DATA: JSON 格式的更新数据，如 '{"name": "张三", "age": 31}'

    WHERE: JSON 格式的 WHERE 条件，如 '{"id": 1}'
    """
    from src.tools import manipulation as manip_tools

    cid, _ = get_connection(connect_id, config)

    # 解析更新数据
    try:
        parsed_data = json.loads(data)
        if not isinstance(parsed_data, dict):
            raise ValueError("数据必须是对象格式")
    except json.JSONDecodeError as e:
        raise click.ClickException(f"JSON 解析失败 (data): {e}")

    # 解析 WHERE 条件
    try:
        parsed_where = json.loads(where)
        if not isinstance(parsed_where, dict):
            raise ValueError("WHERE 条件必须是对象格式")
    except json.JSONDecodeError as e:
        raise click.ClickException(f"JSON 解析失败 (where): {e}")

    result = manip_tools.update_data(cid, table, parsed_data, parsed_where, schema)

    # 解析结果并格式化输出
    try:
        result_obj = json.loads(result)
        if result_obj.get("success"):
            click.echo(f"✓ 更新成功，影响行数: {result_obj.get('affected_rows', 0)}")
        else:
            raise click.ClickException(f"更新失败: {result_obj.get('error')}")
    except Exception as e:
        raise click.ClickException(f"执行失败: {e}")


@data_group.command(name="delete")
@click.argument("table")
@click.argument("where")
@click.option("--schema", default=None, help="schema 名称")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def delete_data_cmd(table: str, where: str, schema: str, connect_id: str, config: str):
    """删除数据

    TABLE: 表名

    WHERE: JSON 格式的 WHERE 条件，如 '{"id": 1}'
    """
    from src.tools import manipulation as manip_tools

    cid, _ = get_connection(connect_id, config)

    # 解析 WHERE 条件
    try:
        parsed_where = json.loads(where)
        if not isinstance(parsed_where, dict):
            raise ValueError("WHERE 条件必须是对象格式")
    except json.JSONDecodeError as e:
        raise click.ClickException(f"JSON 解析失败: {e}")

    result = manip_tools.delete_data(cid, table, parsed_where, schema)

    # 解析结果并格式化输出
    try:
        result_obj = json.loads(result)
        if result_obj.get("success"):
            click.echo(f"✓ 删除成功，影响行数: {result_obj.get('affected_rows', 0)}")
        else:
            raise click.ClickException(f"删除失败: {result_obj.get('error')}")
    except Exception as e:
        raise click.ClickException(f"执行失败: {e}")