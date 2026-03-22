# CLAUDE.md

本文档为 Claude Code (claude.ai/code) 在本项目中工作提供指导。

## 项目概述

**mcp-db-server-sse** 是一个支持 Streamable HTTP 传输协议的 Model Context Protocol (MCP) 服务器，为 MySQL、Oracle 和 StarRocks 提供数据库工具。

## 常用命令

### Windows 环境

```powershell
# 安装依赖
pip install -e .

# 运行 MCP 服务器（stdio 模式，默认）
python -m src.server

# 运行 MCP 服务器（Streamable HTTP 模式）
python -m src.server --transport streamable-http
# 指定端口
python -m src.server --transport streamable-http --port 9000
# 指定主机和端口
python -m src.server --transport streamable-http --host 127.0.0.1 --port 8080

# 运行测试
python test_server.py

# 设置自定义配置路径（Windows 语法）
set MCP_DB_CONFIG=C:\path\to\databases.json
```

### Linux/macOS 环境

```bash
# 安装依赖
pip install -e .

# 运行 MCP 服务器（stdio 模式，默认）
python -m src.server
# 或
mcp-db-server

# 运行 MCP 服务器（Streamable HTTP 模式）
python -m src.server --transport streamable-http
# 指定端口
python -m src.server --transport streamable-http --port 9000
# 指定主机和端口
python -m src.server --transport streamable-http --host 127.0.0.1 --port 8080

# 运行测试
python test_server.py

# 设置自定义配置路径（Linux/macOS 语法）
export MCP_DB_CONFIG=/path/to/databases.json
```

## 架构

```
src/
├── server.py        # FastMCP 服务器入口，定义所有 MCP 工具，支持 stdio/Streamable HTTP 两种传输模式
├── config.py        # ConfigLoader 加载 databases.json，管理连接配置
├── database/
│   ├── base.py      # 抽象 DatabaseBase 类
│   ├── mysql.py     # MySQLDatabase 实现
│   ├── oracle.py    # OracleDatabase 实现（使用 service_name）
│   └── starrocks.py # StarRocksDatabase 实现（MySQL 协议）
└── tools/
    ├── ddl.py       # get_ddl, get_tables 函数
    ├── query.py     # execute_query 函数
    ├── metadata.py  # 元数据查询工具
    └── manipulation.py # 数据操作工具
```

**数据库工厂模式**：`database/__init__.py` 导出 `create_database(config)`，根据 `config.type` 返回相应的 DatabaseBase 子类。

**配置**：数据库连接在 `databases.json` 中定义（可通过 `MCP_DB_CONFIG` 环境变量指定路径）。每个条目包含 `type`（mysql/oracle/starrocks）、`host`、`port`、`user`、`password`，以及 `database`（MySQL/StarRocks）或 `service_name`（Oracle）。

## 交流语言

本项目所有交流均使用中文，包括代码注释和文档。