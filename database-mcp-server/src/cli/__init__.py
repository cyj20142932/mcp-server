"""CLI 模块 - MCP 数据库命令行工具"""
from .main import cli

# 为入口点 "src.cli:main" 提供 main 别名
main = cli

from .context import get_connection, select_connection
from .formatter import format_results, format_table

__all__ = ["cli", "main", "get_connection", "select_connection", "format_results", "format_table"]