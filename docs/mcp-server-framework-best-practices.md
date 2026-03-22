# MCP 服务器开发最佳实践

本文档总结基于 `database-mcp-server` (Stdio 协议) 和 `database-mcp-server-http` (HTTP 协议) 两个项目的经验，提供开发 MCP 服务器的两种传输协议的框架模板。

## 目录

- [协议概述](#协议概述)
- [Stdio 协议框架](#stdio-协议框架)
- [Streamable HTTP 协议框架](#streamable-http-协议框架)
- [项目结构最佳实践](#项目结构最佳实践)
- [工具定义规范](#工具定义规范)
- [配置管理](#配置管理)

---

## 协议概述

MCP (Model Context Protocol) 支持两种传输协议：

| 协议 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **Stdio** | 本地进程、CLI 工具 | 简单、无需网络配置、延迟低 | 不支持远程访问 |
| **Streamable HTTP** | 远程服务、微服务架构 | 支持远程调用、可扩展 | 需要网络配置、复杂度稍高 |

---

## Stdio 协议框架

### 核心代码结构

```python
"""MCP Server - {服务名称}"""
import sys
from pathlib import Path

# 添加路径以便导入模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP

# 创建 MCP 服务器实例
mcp = FastMCP("{服务名称}")

# ========== 工具定义 ==========

@mcp.tool()
def tool_name(param1: str, param2: int = 100) -> str:
    """工具描述。"""
    # 工具实现逻辑
    return "结果"


# ========== 入口点 ==========

def main():
    """主入口点。"""
    mcp.run()


if __name__ == "__main__":
    main()
```

### pyproject.toml 配置

```toml
[project]
name = "{项目名称}"
version = "1.0.0"
description = "{服务描述}"
requires-python = ">=3.8"
dependencies = [
    "fastmcp>=2.0.0",
    # 其他依赖...
]

[project.scripts]
{命令名} = "src.server:main"
```

### 运行方式

```bash
# 直接运行
python -m src.server

# 或使用安装的命令
{命令名}
```

---

## Streamable HTTP 协议框架

### 核心代码结构

```python
"""MCP Server - {服务名称} (支持 Streamable HTTP)"""
import sys
import argparse
from pathlib import Path

# 添加路径以便导入模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP

# 创建 MCP 服务器实例
mcp = FastMCP("{服务名称}")

# ========== 工具定义 ==========

@mcp.tool()
def tool_name(param1: str, param2: int = 100) -> str:
    """工具描述。"""
    # 工具实现逻辑
    return "结果"


# ========== 入口点 ==========

def main():
    """主入口点，支持 stdio 和 streamable-http 两种模式。"""
    parser = argparse.ArgumentParser(description="{服务名称} (Streamable HTTP 支持)")
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="传输协议: stdio 或 streamable-http (默认: stdio)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Streamable HTTP 模式下的端口号 (默认: 8080)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Streamable HTTP 模式下的主机地址 (默认: 0.0.0.0)"
    )
    args = parser.parse_args()

    if args.transport == "streamable-http":
        print(f"启动 Streamable HTTP 服务器: {args.host}:{args.port}", file=sys.stderr)
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
```

### pyproject.toml 配置

```toml
[project]
name = "{项目名称}"
version = "1.0.0"
description = "{服务描述} (支持 Streamable HTTP)"
requires-python = ">=3.8"
dependencies = [
    "fastmcp>=2.0.0",
    # 其他依赖...
]

[project.scripts]
{命令名} = "src.server:main"
{命令名}-http = "src.server:main"
```

### 运行方式

```bash
# Stdio 模式（默认）
python -m src.server

# Streamable HTTP 模式
python -m src.server --transport streamable-http

# 指定端口
python -m src.server --transport streamable-http --port 9000

# 指定主机和端口
python -m src.server --transport streamable-http --host 127.0.0.1 --port 8080
```

---

## 项目结构最佳实践

推荐的项目目录结构：

```
{项目名称}/
├── pyproject.toml           # 项目配置和依赖
├── requirements.txt         # 依赖列表（可选）
├── README.md                # 项目说明
├── CLAUDE.md                # Claude Code 指导
├── databases.json           # 配置文件模板
├── databases.json.template  # 配置模板
├── test_server.py           # 测试脚本
├── src/
│   ├── __init__.py
│   ├── server.py            # MCP 服务器入口
│   ├── config.py            # 配置加载器
│   ├── database/            # 数据库抽象层
│   │   ├── __init__.py
│   │   ├── base.py          # 抽象基类
│   │   ├── mysql.py         # MySQL 实现
│   │   ├── oracle.py        # Oracle 实现
│   │   └── starrocks.py     # StarRocks 实现
│   └── tools/               # 工具实现
│       ├── __init__.py
│       ├── ddl.py           # DDL 工具
│       ├── query.py         # 查询工具
│       ├── metadata.py      # 元数据工具
│       └── manipulation.py  # 数据操作工具
└── docs/                    # 文档目录
```

---

## 工具定义规范

### 基本格式

```python
@mcp.tool()
def tool_name(param1: str, param2: int = 100, param3: str = None) -> str:
    """
    工具描述。

    Args:
        param1: 参数1描述
        param2: 参数2描述（默认: 100）
        param3: 参数3描述（可选）

    Returns:
        返回结果描述
    """
    # 实现逻辑
    return "结果"
```

### 参数类型提示

- 使用 Python 类型提示（`str`, `int`, `float`, `bool`, `list`, `dict`）
- 可选参数提供默认值
- 复杂数据结构使用 `str` + JSON 格式

### 返回值

- 优先返回字符串格式
- 复杂数据可返回 JSON 字符串
- 错误信息返回错误描述

---

## 配置管理

### 配置文件格式 (databases.json)

```json
{
    "connections": [
        {
            "id": "my_mysql",
            "type": "mysql",
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "password",
            "database": "test_db"
        }
    ]
}
```

### 配置加载器模式

```python
# config.py
import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class DatabaseConfig:
    id: str
    type: str
    host: str
    port: int
    user: str
    password: str
    database: Optional[str] = None
    service_name: Optional[str] = None

class ConfigLoader:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.environ.get("MCP_DB_CONFIG", "databases.json")
        self.config_path = Path(config_path)

    def load(self) -> List[DatabaseConfig]:
        """加载配置文件。"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [DatabaseConfig(**conn) for conn in data.get("connections", [])]

    def get_connection(self, connect_id: str) -> DatabaseConfig:
        """根据 ID 获取连接配置。"""
        for conn in self.load():
            if conn.id == connect_id:
                return conn
        raise ValueError(f"未找到连接: {connect_id}")
```

### 使用配置

```python
from src.config import ConfigLoader

config = ConfigLoader()
db_config = config.get_connection(connect_id)
```

---

## 快速开始模板

### 创建新的 Stdio 服务器

1. 复制 `database-mcp-server` 项目结构
2. 修改 `pyproject.toml` 中的项目名称和依赖
3. 在 `src/server.py` 中添加你的工具
4. 安装并运行：
   ```bash
   pip install -e .
   python -m src.server
   ```

### 创建新的 HTTP 服务器

1. 复制 `database-mcp-server-http` 项目结构
2. 修改 `pyproject.toml` 中的项目名称和依赖
3. 在 `src/server.py` 中添加你的工具
4. 安装并运行：
   ```bash
   pip install -e .
   python -m src.server --transport streamable-http --port 8080
   ```

---

## 依赖说明

核心依赖：

- `fastmcp>=2.0.0` - FastMCP 框架

根据需要添加：

- `mysql-connector-python` - MySQL 连接
- `oracledb` - Oracle 连接
- `psycopg2` - PostgreSQL 连接
- `pyarrow` - 数据格式处理
- `requests` - HTTP 客户端（用于 HTTP 协议调试）

---

## 常见问题

### Q: 如何选择协议？

- 本地使用优先选择 **Stdio**
- 需要远程部署或微服务架构选择 **Streamable HTTP**

### Q: 如何同时支持两种协议？

参考 `database-mcp-server-http` 的实现，使用命令行参数切换协议。

### Q: 如何添加新的数据库支持？

1. 在 `database/base.py` 中继承 `DatabaseBase` 抽象类
2. 在 `database/__init__.py` 的工厂函数中添加新的类型判断
3. 实现具体的数据库操作方法