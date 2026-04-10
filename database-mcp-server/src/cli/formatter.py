"""输出格式化模块"""
import json
import csv
import io
from typing import List, Dict, Any, Optional


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """格式化为 ASCII 表格"""
    if not headers:
        return ""

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # 表头
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    separator = "-+-".join("-" * w for w in col_widths)

    # 数据行
    lines = [header_line, separator]
    for row in rows:
        lines.append(" | ".join(cell.ljust(w) for cell, w in zip(row, col_widths)))

    return "\n".join(lines)


def format_results(results: List[Dict[str, Any]], format: str = "table") -> str:
    """格式化查询结果

    Args:
        results: 查询结果列表
        format: 输出格式 ("table", "json", "csv")
    """
    if not results:
        return "无结果"

    headers = list(results[0].keys())
    rows = [[str(row.get(h, "")) for h in headers] for row in results]

    if format == "json":
        return json.dumps(results, ensure_ascii=False, indent=2)

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        return output.getvalue()

    # 默认表格格式
    return format_table(headers, rows)


def format_ddl(ddl: str) -> str:
    """格式化 DDL 输出"""
    return ddl


def format_list(items: List[str]) -> str:
    """格式化列表输出"""
    if not items:
        return "无结果"
    return "\n".join(items)


def format_message(message: str, success: bool = True) -> str:
    """格式化消息输出"""
    prefix = "✓" if success else "✗"
    return f"{prefix} {message}"