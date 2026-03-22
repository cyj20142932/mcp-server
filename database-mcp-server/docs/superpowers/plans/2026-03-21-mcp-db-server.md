# MCP数据库服务器实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 开发一个MCP Server供Claude Code使用，支持MySQL、Oracle、StarRocks数据库的DDL获取和SQL查询

**Architecture:** 使用FastMCP框架构建MCP Server，通过配置文件管理多数据库连接，支持connect_id区分不同实例

**Tech Stack:** Python 3.8+, fastmcp, mysql-connector-python, oracledb, pyarrow

---

## 文件结构

```
mcp-db-server/
├── install.py                    # 一键安装脚本
├── databases.json.template       # 配置文件模板
├── requirements.txt              # Python依赖
├── pyproject.toml               # 项目配置
└── src/
    ├── __init__.py
    ├── server.py                # MCP Server入口
    ├── config.py                # 配置加载模块
    ├── database/
    │   ├── __init__.py
    │   ├── base.py              # 数据库基类
    │   ├── mysql.py             # MySQL实现
    │   ├── oracle.py            # Oracle实现
    │   └── starrocks.py         # StarRocks实现
    └── tools/
        ├── __init__.py
        ├── ddl.py               # DDL工具
        └── query.py             # 查询工具
```

---

### Task 1: 项目基础结构

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml`

- [ ] **Step 1: 创建requirements.txt**

```txt
fastmcp>=2.0.0
mysql-connector-python>=8.0.0
oracledb>=2.0.0
pyarrow>=14.0.0
```

- [ ] **Step 2: 创建pyproject.toml**

```toml
[project]
name = "mcp-db-server"
version = "1.0.0"
description = "MCP Server for MySQL, Oracle, StarRocks"
requires-python = ">=3.8"
dependencies = [
    "fastmcp>=2.0.0",
    "mysql-connector-python>=8.0.0",
    "oracledb>=2.0.0",
    "pyarrow>=14.0.0",
]

[project.scripts]
mcp-db-server = "src.server:main"
```

- [ ] **Step 3: Commit**

```bash
git add requirements.txt pyproject.toml
git commit -m "chore: add project dependencies"
```

---

### Task 2: 配置模块

**Files:**
- Create: `src/config.py`
- Create: `databases.json.template`

- [ ] **Step 1: 创建配置加载模块**

```python
"""Configuration loader for database connections."""
import json
import os
from pathlib import Path
from typing import Dict, Any

class DatabaseConfig:
    """Database connection configuration."""

    def __init__(self, config: Dict[str, Any]):
        self.type = config.get("type")
        self.host = config.get("host")
        self.port = config.get("port")
        self.user = config.get("user")
        self.password = config.get("password")
        self.database = config.get("database")
        self.service_name = config.get("service_name")

    def validate(self) -> bool:
        """Validate required fields."""
        required = ["type", "host", "port", "user"]
        return all(getattr(self, field) for field in required)


class ConfigLoader:
    """Load and manage database configurations."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.environ.get(
                "MCP_DB_CONFIG",
                str(Path.home() / "mcp-db-server" / "databases.json")
            )
        self.config_path = Path(config_path)
        self._databases: Dict[str, DatabaseConfig] = {}

    def load(self) -> Dict[str, DatabaseConfig]:
        """Load configurations from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path) as f:
            data = json.load(f)

        self._databases = {
            k: DatabaseConfig(v)
            for k, v in data.get("databases", {}).items()
        }
        return self._databases

    def get(self, connect_id: str) -> DatabaseConfig:
        """Get config by connect_id."""
        if not self._databases:
            self.load()
        return self._databases.get(connect_id)

    def list_ids(self) -> list:
        """List all available connect_ids."""
        if not self._databases:
            self.load()
        return list(self._databases.keys())


# Global instance
_config: ConfigLoader = None

def get_config(config_path: str = None) -> ConfigLoader:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = ConfigLoader(config_path)
    return _config
```

- [ ] **Step 2: 创建配置文件模板**

```json
{
  "databases": {
    "db_prod": {
      "type": "mysql",
      "host": "localhost",
      "port": 3306,
      "user": "root",
      "password": "your_password",
      "database": "production"
    },
    "db_test": {
      "type": "starrocks",
      "host": "localhost",
      "port": 9030,
      "user": "root",
      "password": "",
      "database": "test"
    }
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add src/config.py databases.json.template
git commit -m "feat: add config module"
```

---

### Task 3: 数据库抽象层

**Files:**
- Create: `src/database/__init__.py`
- Create: `src/database/base.py`
- Create: `src/database/mysql.py`
- Create: `src/database/oracle.py`
- Create: `src/database/starrocks.py`

- [ ] **Step 1: 创建数据库基类**

```python
"""Base database interface."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class DatabaseBase(ABC):
    """Abstract base class for database operations."""

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def connect(self):
        """Establish database connection."""
        pass

    @abstractmethod
    def close(self):
        """Close database connection."""
        pass

    @abstractmethod
    def get_ddl(self, table_name: str, schema_name: str = None) -> str:
        """Get DDL for a table."""
        pass

    @abstractmethod
    def get_tables(self, schema_name: str = None) -> List[str]:
        """Get list of tables."""
        pass

    @abstractmethod
    def execute_query(self, sql: str, max_rows: int = 1000) -> List[Dict[str, Any]]:
        """Execute SQL query and return results."""
        pass
```

- [ ] **Step 2: 创建MySQL实现**

```python
"""MySQL database implementation."""
import mysql.connector
from typing import List, Dict, Any
from .base import DatabaseBase

class MySQLDatabase(DatabaseBase):
    """MySQL database operations."""

    def __init__(self, config):
        super().__init__(config)
        self._conn = None

    def connect(self):
        self._conn = mysql.connector.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database
        )

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def get_ddl(self, table_name: str, schema_name: str = None) -> str:
        if not self._conn or not self._conn.is_connected():
            self.connect()

        cursor = self._conn.cursor()
        cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
        result = cursor.fetchone()
        cursor.close()
        return result[1] if result else ""

    def get_tables(self, schema_name: str = None) -> List[str]:
        if not self._conn or not self._conn.is_connected():
            self.connect()

        db = self.config.database
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{db}'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def execute_query(self, sql: str, max_rows: int = 1000) -> List[Dict[str, Any]]:
        if not self._conn or not self._conn.is_connected():
            self.connect()

        cursor = self._conn.cursor(dictionary=True)
        cursor.execute(sql)
        results = cursor.fetchmany(max_rows)
        cursor.close()
        return results
```

- [ ] **Step 3: 创建Oracle实现**

```python
"""Oracle database implementation."""
import oracledb
from typing import List, Dict, Any
from .base import DatabaseBase

class OracleDatabase(DatabaseBase):
    """Oracle database operations."""

    def __init__(self, config):
        super().__init__(config)
        self._conn = None

    def connect(self):
        dsn = oracledb.makedsn(
            self.config.host,
            self.config.port,
            service_name=self.config.service_name
        )
        self._conn = oracledb.connect(
            user=self.config.user,
            password=self.config.password,
            dsn=dsn
        )

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def get_ddl(self, table_name: str, schema_name: str = None) -> str:
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute(f"""
            SELECT DBMS_METADATA.GET_DDL('TABLE', '{table_name}', '{schema}')
            FROM DUAL
        """)
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else ""

    def get_tables(self, schema_name: str = None) -> List[str]:
        if not self._conn:
            self.connect()

        schema = schema_name or self.config.user.upper()
        cursor = self._conn.cursor()
        cursor.execute(f"""
            SELECT TABLE_NAME FROM ALL_TABLES
            WHERE OWNER = '{schema}'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def execute_query(self, sql: str, max_rows: int = 1000) -> List[Dict[str, Any]]:
        if not self._conn:
            self.connect()

        cursor = self._conn.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description] if cursor.description else []
        results = cursor.fetchmany(max_rows)
        cursor.close()
        return [dict(zip(columns, row)) for row in results]
```

- [ ] **Step 4: 创建StarRocks实现**

```python
"""StarRocks database implementation."""
import mysql.connector
from typing import List, Dict, Any
from .base import DatabaseBase

class StarRocksDatabase(DatabaseBase):
    """StarRocks database operations."""

    def __init__(self, config):
        super().__init__(config)
        self._conn = None

    def connect(self):
        self._conn = mysql.connector.connect(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database
        )

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def get_ddl(self, table_name: str, schema_name: str = None) -> str:
        if not self._conn or not self._conn.is_connected():
            self.connect()

        cursor = self._conn.cursor()
        cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
        result = cursor.fetchone()
        cursor.close()
        return result[1] if result else ""

    def get_tables(self, schema_name: str = None) -> List[str]:
        if not self._conn or not self._conn.is_connected():
            self.connect()

        db = self.config.database
        cursor = self._conn.cursor()
        cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{db}'")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def execute_query(self, sql: str, max_rows: int = 1000) -> List[Dict[str, Any]]:
        if not self._conn or not self._conn.is_connected():
            self.connect()

        cursor = self._conn.cursor(dictionary=True)
        cursor.execute(sql)
        results = cursor.fetchmany(max_rows)
        cursor.close()
        return results
```

- [ ] **Step 5: 创建数据库工厂**

```python
"""Database factory."""
from .base import DatabaseBase
from .mysql import MySQLDatabase
from .oracle import OracleDatabase
from .starrocks import StarRocksDatabase

DATABASE_CLASSES = {
    "mysql": MySQLDatabase,
    "oracle": OracleDatabase,
    "starrocks": StarRocksDatabase,
}

def create_database(config) -> DatabaseBase:
    """Create database instance based on config type."""
    db_type = config.type.lower()
    if db_type not in DATABASE_CLASSES:
        raise ValueError(f"Unsupported database type: {db_type}")
    return DATABASE_CLASSES[db_type](config)
```

- [ ] **Step 6: Commit**

```bash
git add src/database/
git commit -m "feat: add database abstraction layer"
```

---

### Task 4: MCP工具

**Files:**
- Create: `src/tools/ddl.py`
- Create: `src/tools/query.py`

- [ ] **Step 1: 创建DDL工具**

```python
"""DDL retrieval tools."""
from typing import Optional, List
from ..config import get_config
from ..database import create_database

def get_ddl(connect_id: str, table_name: str, schema_name: Optional[str] = None) -> str:
    """
    Get DDL for a specific table.

    Args:
        connect_id: Database connection identifier
        table_name: Name of the table
        schema_name: Optional schema/database name

    Returns:
        DDL statement as string
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        return db.get_ddl(table_name, schema_name)
    finally:
        db.close()

def get_tables(connect_id: str, schema_name: Optional[str] = None) -> List[str]:
    """
    Get list of tables in a database.

    Args:
        connect_id: Database connection identifier
        schema_name: Optional schema/database name

    Returns:
        List of table names
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        return db.get_tables(schema_name)
    finally:
        db.close()
```

- [ ] **Step 2: 创建查询工具**

```python
"""SQL query tools."""
from typing import Dict, Any, List
from ..config import get_config
from ..database import create_database

def execute_query(connect_id: str, sql: str, max_rows: int = 1000) -> List[Dict[str, Any]]:
    """
    Execute SQL query and return results.

    Args:
        connect_id: Database connection identifier
        sql: SQL query to execute
        max_rows: Maximum number of rows to return

    Returns:
        List of result rows as dictionaries
    """
    config = get_config().get(connect_id)
    if not config:
        raise ValueError(f"Unknown connect_id: {connect_id}")

    db = create_database(config)
    try:
        db.connect()
        return db.execute_query(sql, max_rows)
    finally:
        db.close()
```

- [ ] **Step 3: Commit**

```bash
git add src/tools/
git commit -m "feat: add MCP tools"
```

---

### Task 5: MCP Server主入口

**Files:**
- Create: `src/server.py`
- Create: `src/__init__.py`

- [ ] **Step 1: 创建MCP Server**

```python
"""MCP Database Server."""
from fastmcp import FastMCP
from .config import get_config
from .tools import ddl, query

mcp = FastMCP("mcp-db-server")

@mcp.tool()
def get_ddl(connect_id: str, table_name: str, schema_name: str = None) -> str:
    """Get DDL for a specific table."""
    return ddl.get_ddl(connect_id, table_name, schema_name)

@mcp.tool()
def get_tables(connect_id: str, schema_name: str = None) -> str:
    """Get list of tables in a database."""
    tables = ddl.get_tables(connect_id, schema_name)
    return "\n".join(tables)

@mcp.tool()
def execute_query(connect_id: str, sql: str, max_rows: int = 1000) -> str:
    """Execute SQL query and return results."""
    results = query.execute_query(connect_id, sql, max_rows)
    if not results:
        return "No results"

    # Format as table
    headers = list(results[0].keys())
    rows = [[str(row.get(h, "")) for h in headers] for row in results]

    # Build output
    col_widths = [max(len(h), max(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    separator = "-+-".join("-" * w for w in col_widths)

    lines = [header_line, separator]
    for row in rows:
        lines.append(" | ".join(cell.ljust(w) for cell, w in zip(row, col_widths)))

    return "\n".join(lines)

def main():
    """Main entry point."""
    # Load config
    config = get_config()
    config.load()

    # Run server
    mcp.run()

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add src/server.py src/__init__.py
git commit -m "feat: add MCP server"
```

---

### Task 6: 安装脚本

**Files:**
- Create: `install.py`

- [ ] **Step 1: 创建安装脚本**

```python
#!/usr/bin/env python3
"""Install MCP Database Server to Claude Code."""
import json
import os
import shutil
import sys
from pathlib import Path

def get_settings_path() -> Path:
    """Get Claude Code settings.json path."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        settings_dir = base / "Claude" / "settings"
    else:
        settings_dir = Path.home() / ".config" / "Claude" / "settings"

    settings_file = settings_dir / "settings.json"
    if not settings_file.exists():
        # Try alternative locations
        settings_file = settings_dir / "settings.local.json"

    return settings_file

def load_settings(settings_path: Path) -> dict:
    """Load existing settings."""
    if settings_path.exists():
        with open(settings_path) as f:
            return json.load(f)
    return {}

def save_settings(settings_path: Path, data: dict):
    """Save settings."""
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(data, f, indent=2)

def add_mcp_config(settings: dict, server_path: Path) -> dict:
    """Add MCP server configuration."""
    mcp_servers = settings.get("mcpServers", {})

    mcp_servers["mcp-db-server"] = {
        "command": "python",
        "args": [str(server_path / "src" / "server.py")],
        "env": {
            "MCP_DB_CONFIG": str(server_path / "databases.json")
        }
    }

    settings["mcpServers"] = mcp_servers
    return settings

def main():
    # Get script directory
    script_dir = Path(__file__).parent.resolve()

    # Check config file
    config_file = script_dir / "databases.json"
    if not config_file.exists():
        # Copy template
        template = script_dir / "databases.json.template"
        if template.exists():
            shutil.copy(template, config_file)
            print(f"Created config file: {config_file}")
            print("Please edit it with your database connections before running.")
        else:
            print("ERROR: No config file found!")
            sys.exit(1)

    # Install dependencies
    print("Installing dependencies...")
    os.system(f"{sys.executable} -m pip install -r {script_dir / 'requirements.txt'}")

    # Update settings
    settings_path = get_settings_path()
    print(f"Updating settings: {settings_path}")

    settings = load_settings(settings_path)
    settings = add_mcp_config(settings, script_dir)
    save_settings(settings_path, settings)

    print("\nInstallation complete!")
    print(f"Config file: {config_path}")
    print("Restart Claude Code to load the MCP server.")

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add install.py
git commit -m "feat: add install script"
```

---

## 执行方式

**Plan complete and saved to `docs/superpowers/plans/2026-03-21-mcp-db-server.md`. Two execution options:**

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?