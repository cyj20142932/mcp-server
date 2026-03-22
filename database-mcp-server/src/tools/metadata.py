"""数据探索工具 - 元数据查询"""
import json
from typing import Optional, List, Dict, Any
from ..config import get_config
from ..database import create_database


def get_columns(connect_id: str, table_name: str, schema_name: Optional[str] = None) -> str:
    """
    获取表的列信息。

    Args:
        connect_id: 数据库连接标识符
        table_name: 表名
        schema_name: 可选的schema/数据库名

    Returns:
        JSON格式的列信息列表
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        columns = db.get_columns(table_name, schema_name)
        return json.dumps(columns, ensure_ascii=False, indent=2)
    finally:
        db.close()


def get_views(connect_id: str, schema_name: Optional[str] = None) -> str:
    """
    获取数据库中的视图列表。

    Args:
        connect_id: 数据库连接标识符
        schema_name: 可选的schema/数据库名

    Returns:
        JSON格式的视图名称列表
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        views = db.get_views(schema_name)
        return json.dumps(views, ensure_ascii=False, indent=2)
    finally:
        db.close()


def get_view_ddl(connect_id: str, view_name: str, schema_name: Optional[str] = None) -> str:
    """
    获取视图的DDL定义。

    Args:
        connect_id: 数据库连接标识符
        view_name: 视图名
        schema_name: 可选的schema/数据库名

    Returns:
        视图的DDL语句
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        ddl = db.get_view_ddl(view_name, schema_name)
        return ddl
    finally:
        db.close()


def get_indexes(connect_id: str, table_name: str, schema_name: Optional[str] = None) -> str:
    """
    获取表的索引信息。

    Args:
        connect_id: 数据库连接标识符
        table_name: 表名
        schema_name: 可选的schema/数据库名

    Returns:
        JSON格式的索引信息列表
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        indexes = db.get_indexes(table_name, schema_name)
        return json.dumps(indexes, ensure_ascii=False, indent=2)
    finally:
        db.close()


def get_constraints(connect_id: str, table_name: str, schema_name: Optional[str] = None) -> str:
    """
    获取表的约束信息。

    Args:
        connect_id: 数据库连接标识符
        table_name: 表名
        schema_name: 可选的schema/数据库名

    Returns:
        JSON格式的约束信息列表
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        constraints = db.get_constraints(table_name, schema_name)
        return json.dumps(constraints, ensure_ascii=False, indent=2)
    finally:
        db.close()


def get_foreign_keys(connect_id: str, table_name: str, schema_name: Optional[str] = None) -> str:
    """
    获取表的外键关系。

    Args:
        connect_id: 数据库连接标识符
        table_name: 表名
        schema_name: 可选的schema/数据库名

    Returns:
        JSON格式的外键信息列表
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        fks = db.get_foreign_keys(table_name, schema_name)
        return json.dumps(fks, ensure_ascii=False, indent=2)
    finally:
        db.close()


def get_procedures(connect_id: str, schema_name: Optional[str] = None) -> str:
    """
    获取存储过程列表。

    Args:
        connect_id: 数据库连接标识符
        schema_name: 可选的schema名

    Returns:
        JSON格式的存储过程名称列表
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        procedures = db.get_procedures(schema_name)
        return json.dumps(procedures, ensure_ascii=False, indent=2)
    finally:
        db.close()


def get_procedure_ddl(connect_id: str, procedure_name: str, schema_name: Optional[str] = None) -> str:
    """
    获取存储过程定义。

    Args:
        connect_id: 数据库连接标识符
        procedure_name: 存储过程名
        schema_name: 可选的schema名

    Returns:
        存储过程的DDL语句
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        ddl = db.get_procedure_ddl(procedure_name, schema_name)
        return ddl
    finally:
        db.close()


def get_functions(connect_id: str, schema_name: Optional[str] = None) -> str:
    """
    获取函数列表。

    Args:
        connect_id: 数据库连接标识符
        schema_name: 可选的schema名

    Returns:
        JSON格式的函数名称列表
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        functions = db.get_functions(schema_name)
        return json.dumps(functions, ensure_ascii=False, indent=2)
    finally:
        db.close()