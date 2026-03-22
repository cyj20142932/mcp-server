"""数据操作工具 - 插入、更新、删除和事务管理"""
import json
from typing import Optional, Dict, Any, List
from ..config import get_config
from ..database import create_database

# 连接会话存储 - 用于事务管理
# key: connect_id, value: database instance with active connection
_sessions: Dict[str, Any] = {}


def _get_session(connect_id: str):
    """获取或创建数据库会话（用于事务管理）"""
    if connect_id not in _sessions:
        config = get_config().get(connect_id)
        if not config:
            raise ValueError(f"Unknown connect_id: {connect_id}")
        db = create_database(config)
        db.connect()
        _sessions[connect_id] = db
    return _sessions[connect_id]


def _close_session(connect_id: str):
    """关闭并移除会话"""
    if connect_id in _sessions:
        db = _sessions.pop(connect_id)
        db.close()


def insert_data(connect_id: str, table_name: str, data: List[Dict[str, Any]], schema_name: Optional[str] = None) -> str:
    """
    插入单条或批量数据。

    Args:
        connect_id: 数据库连接标识符
        table_name: 表名
        data: 要插入的数据，格式为字典列表
        schema_name: 可选的schema/数据库名

    Returns:
        JSON格式的结果，包含影响的行数
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        affected = db.insert_data(table_name, data, schema_name)
        db.commit()
        return json.dumps({"success": True, "affected_rows": affected}, ensure_ascii=False, indent=2)
    except Exception as e:
        db.rollback()
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2)
    finally:
        db.close()


def update_data(connect_id: str, table_name: str, data: Dict[str, Any], where: Dict[str, Any], schema_name: Optional[str] = None) -> str:
    """
    更新数据（支持WHERE条件）。

    Args:
        connect_id: 数据库连接标识符
        table_name: 表名
        data: 要更新的字段和值，格式为字典
        where: WHERE条件，格式为字典
        schema_name: 可选的schema/数据库名

    Returns:
        JSON格式的结果，包含影响的行数
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        affected = db.update_data(table_name, data, where, schema_name)
        db.commit()
        return json.dumps({"success": True, "affected_rows": affected}, ensure_ascii=False, indent=2)
    except Exception as e:
        db.rollback()
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2)
    finally:
        db.close()


def delete_data(connect_id: str, table_name: str, where: Dict[str, Any], schema_name: Optional[str] = None) -> str:
    """
    删除数据（支持WHERE条件）。

    Args:
        connect_id: 数据库连接标识符
        table_name: 表名
        where: WHERE条件，格式为字典
        schema_name: 可选的schema/数据库名

    Returns:
        JSON格式的结果，包含影响的行数
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        affected = db.delete_data(table_name, where, schema_name)
        db.commit()
        return json.dumps({"success": True, "affected_rows": affected}, ensure_ascii=False, indent=2)
    except Exception as e:
        db.rollback()
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2)
    finally:
        db.close()


def begin_transaction(connect_id: str) -> str:
    """
    开始一个事务会话。之后的数据操作将在同一个连接中执行。

    Args:
        connect_id: 数据库连接标识符

    Returns:
        JSON格式的结果
    """
    try:
        db = _get_session(connect_id)
        return json.dumps({"success": True, "message": "Transaction started"}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2)


def commit_transaction(connect_id: str) -> str:
    """
    提交当前事务。

    Args:
        connect_id: 数据库连接标识符

    Returns:
        JSON格式的结果
    """
    try:
        db = _get_session(connect_id)
        db.commit()
        _close_session(connect_id)
        return json.dumps({"success": True, "message": "Transaction committed"}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2)


def rollback_transaction(connect_id: str) -> str:
    """
    回滚当前事务。

    Args:
        connect_id: 数据库连接标识符

    Returns:
        JSON格式的结果
    """
    try:
        db = _get_session(connect_id)
        db.rollback()
        _close_session(connect_id)
        return json.dumps({"success": True, "message": "Transaction rolled back"}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2)


def transaction_insert(connect_id: str, table_name: str, data: List[Dict[str, Any]], schema_name: Optional[str] = None) -> str:
    """
    在事务中插入数据（需要先调用begin_transaction）。

    Args:
        connect_id: 数据库连接标识符
        table_name: 表名
        data: 要插入的数据，格式为字典列表
        schema_name: 可选的schema/数据库名

    Returns:
        JSON格式的结果
    """
    try:
        db = _get_session(connect_id)
        affected = db.insert_data(table_name, data, schema_name)
        return json.dumps({"success": True, "affected_rows": affected}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2)


def transaction_update(connect_id: str, table_name: str, data: Dict[str, Any], where: Dict[str, Any], schema_name: Optional[str] = None) -> str:
    """
    在事务中更新数据（需要先调用begin_transaction）。

    Args:
        connect_id: 数据库连接标识符
        table_name: 表名
        data: 要更新的字段和值
        where: WHERE条件
        schema_name: 可选的schema/数据库名

    Returns:
        JSON格式的结果
    """
    try:
        db = _get_session(connect_id)
        affected = db.update_data(table_name, data, where, schema_name)
        return json.dumps({"success": True, "affected_rows": affected}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2)


def transaction_delete(connect_id: str, table_name: str, where: Dict[str, Any], schema_name: Optional[str] = None) -> str:
    """
    在事务中删除数据（需要先调用begin_transaction）。

    Args:
        connect_id: 数据库连接标识符
        table_name: 表名
        where: WHERE条件
        schema_name: 可选的schema/数据库名

    Returns:
        JSON格式的结果
    """
    try:
        db = _get_session(connect_id)
        affected = db.delete_data(table_name, where, schema_name)
        return json.dumps({"success": True, "affected_rows": affected}, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2)