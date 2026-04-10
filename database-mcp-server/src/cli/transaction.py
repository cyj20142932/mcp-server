"""Transaction 子命令 - 事务管理"""
import click
from .context import get_connection
from .formatter import format_results


@click.group(name="transaction")
def transaction_group():
    """Transaction 相关命令"""
    pass


@transaction_group.command(name="begin")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def begin_transaction(connect_id: str, config: str):
    """开始一个事务"""
    from src.tools import manipulation as manip_tools

    cid, _ = get_connection(connect_id, config)
    result = manip_tools.begin_transaction(cid)
    click.echo(format_results(result, "json"))


@transaction_group.command(name="commit")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def commit_transaction(connect_id: str, config: str):
    """提交当前事务"""
    from src.tools import manipulation as manip_tools

    cid, _ = get_connection(connect_id, config)
    result = manip_tools.commit_transaction(cid)
    click.echo(format_results(result, "json"))


@transaction_group.command(name="rollback")
@click.option("--connect_id", default=None, help="数据库连接 ID")
@click.option("--config", default=None, help="配置文件路径")
def rollback_transaction(connect_id: str, config: str):
    """回滚当前事务"""
    from src.tools import manipulation as manip_tools

    cid, _ = get_connection(connect_id, config)
    result = manip_tools.rollback_transaction(cid)
    click.echo(format_results(result, "json"))