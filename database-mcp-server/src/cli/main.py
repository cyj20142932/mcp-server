"""MCP 数据库 CLI 工具主入口"""
import click
from .ddl import ddl_group
from .query import query_group
from .metadata import metadata_group
from .data import data_group
from .transaction import transaction_group


@click.group()
@click.option("--config", default=None, help="配置文件路径")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.pass_context
def cli(ctx, config: str, connect_id: str):
    """MCP 数据库命令行工具

    用于通过命令行操作 MySQL、Oracle、StarRocks 数据库
    """
    # 存储全局选项到上下文
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["connect_id"] = connect_id


# 注册子命令组
cli.add_command(ddl_group)
cli.add_command(query_group)
cli.add_command(metadata_group)
cli.add_command(data_group)
cli.add_command(transaction_group)


if __name__ == "__main__":
    cli()