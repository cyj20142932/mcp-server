"""连接上下文管理 - 处理数据库连接选择"""
import click
from pathlib import Path
from typing import Optional
from src.config import ConfigLoader, get_config


class ConnectionContext:
    """数据库连接上下文"""

    def __init__(self, config_path: str = None):
        self.loader = get_config(config_path)
        self.current_connect_id: Optional[str] = None

    def get_connect_id(self, connect_id: Optional[str] = None) -> str:
        """获取连接 ID，如果未指定则交互式选择"""
        if connect_id:
            return connect_id

        if not self.current_connect_id:
            self.current_connect_id = select_connection(self.loader)

        return self.current_connect_id

    def reset(self):
        """重置当前连接"""
        self.current_connect_id = None


# 全局上下文实例
_context: Optional[ConnectionContext] = None


def get_context(config_path: str = None) -> ConnectionContext:
    """获取全局连接上下文"""
    global _context
    if _context is None:
        _context = ConnectionContext(config_path)
    return _context


def select_connection(loader: ConfigLoader) -> str:
    """交互式选择数据库连接"""
    connect_ids = loader.list_ids()

    if not connect_ids:
        raise click.ClickException("配置文件中没有数据库连接")

    if len(connect_ids) == 1:
        click.echo(f"使用唯一连接: {connect_ids[0]}")
        return connect_ids[0]

    # 显示选择菜单
    click.echo("请选择数据库连接:")
    click.echo("")

    configs = loader.load()
    for i, connect_id in enumerate(connect_ids, 1):
        cfg = configs[connect_id]
        type_str = cfg.type.upper()
        host_port = f"{cfg.host}:{cfg.port}"
        click.echo(f"  {i}) {connect_id:<20} {type_str:<10} {host_port}")

    click.echo("")
    while True:
        choice = click.prompt("请选择 (1-%d) 或输入名称" % len(connect_ids),
                              type=str, default="1")

        # 尝试数字选择
        if choice.isdigit() and 1 <= int(choice) <= len(connect_ids):
            return connect_ids[int(choice) - 1]

        # 尝试名称匹配
        if choice in connect_ids:
            return choice

        click.echo(f"无效选择: {choice}，请重试")


def get_connection(connect_id: Optional[str] = None, config_path: str = None) -> tuple:
    """获取数据库连接和配置
    返回: (connect_id, db_instance)
    """
    ctx = get_context(config_path)
    cid = ctx.get_connect_id(connect_id)

    from src.database import create_database
    cfg = ctx.loader.get(cid)
    db = create_database(cfg)

    return cid, db