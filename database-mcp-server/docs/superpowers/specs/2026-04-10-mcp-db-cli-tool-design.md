# MCP 数据库 CLI 工具设计

**日期**: 2026-04-10
**项目**: database-mcp-server CLI 工具

## 目标

为 database-mcp-server 创建一个命令行界面（CLI）工具，让用户可以通过终端命令直接调用各个数据库工具，支持交互式选择数据库连接。

## 背景

database-mcp-server 当前是一个基于 FastMCP 的 MCP 服务器，通过 stdio 模式与 Claude Code 集成。为了提供更灵活的使用方式，需要添加一个 CLI 包装器，允许用户直接从终端调用各种数据库操作。

## 命令结构

### 全局选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--config PATH` | 配置文件路径 | `./databases.json` |
| `--connect_id ID` | 指定连接 ID | 交互式选择 |
| `--json` | JSON 格式输出 | 表格格式 |
| `--csv` | CSV 格式输出 | 表格格式 |

### 命令组

#### 1. ddl 子命令

```
mcp-db ddl get <table> [--schema SCHEMA]
mcp-db ddl tables [--schema SCHEMA]
mcp-db ddl view <view> [--schema SCHEMA]
```

#### 2. query 子命令

```
mcp-db query exec <sql> [--max-rows N]
mcp-db query tables
```

#### 3. metadata 子命令

```
mcp-db metadata columns <table> [--schema SCHEMA]
mcp-db metadata views [--schema SCHEMA]
mcp-db metadata indexes <table> [--schema SCHEMA]
mcp-db metadata constraints <table> [--schema SCHEMA]
mcp-db metadata foreign-keys <table> [--schema SCHEMA]
mcp-db metadata procedures [--schema SCHEMA]
mcp-db metadata functions [--schema SCHEMA]
```

#### 4. data 子命令

```
mcp-db data insert <table> <data> [--schema SCHEMA]
mcp-db data update <table> <data> <where> [--schema SCHEMA]
mcp-db data delete <table> <where> [--schema SCHEMA]
```

#### 5. transaction 子命令

```
mcp-db transaction begin
mcp-db transaction commit
mcp-db transaction rollback
```

## 交互流程设计

### 连接选择逻辑

```
1. 解析命令行参数，获取 --connect_id（如果提供）
2. 如果未提供，读取配置文件
3. 如果配置文件中只有一个连接，直接使用
4. 如果有多个连接，显示交互式选择菜单：
   
   请选择数据库连接:
     1) production_mysql    MySQL - 192.168.1.10:3306
     2) staging_oracle      Oracle - 192.168.1.20:1521
     3) analytics_starrocks StarRocks - 192.168.1.30:9030
   
   请选择 (1-3) 或输入名称: 
```

### 输入验证

- SQL 语句：直接传递
- JSON 数据：使用单引号包裹整个 JSON 字符串
  ```
  mcp-db data insert users '{"name": "张三", "age": 30}'
  ```

## 输出格式

### 表格形式（默认）

```
+------+-------+-------+
| id   | name  | age   |
+------+-------+-------+
| 1    | 张三  | 30    |
| 2    | 李四  | 25    |
+------+-------+-------+
```

### JSON 形式（--json）

```json
[
  {"id": "1", "name": "张三", "age": "30"},
  {"id": "2", "name": "李四", "age": "25"}
]
```

### CSV 形式（--csv）

```csv
id,name,age
1,张三,30
2,李四,25
```

## 代码结构

```
src/
├── server.py           # MCP 服务器入口 (现有)
├── cli.py              # CLI 入口点
├── cli/
│   ├── __init__.py
│   ├── context.py      # 连接上下文管理
│   ├── ddl.py          # ddl 子命令
│   ├── query.py        # query 子命令
│   ├── metadata.py     # metadata 子命令
│   ├── data.py         # data 子命令
│   ├── transaction.py  # transaction 子命令
│   └── formatter.py    # 输出格式化
├── config.py           # 配置加载 (复用)
├── database/           # 数据库层 (复用)
└── tools/              # 工具层 (复用)
```

## 技术选型

- **CLI 框架**: Click
- **依赖**: click, 现有项目依赖不变

## pyproject.toml 入口点

```toml
[project.scripts]
mcp-db = "src.cli:cli"
mcp-db-server = "src.server:main"  # 现有
```

## 错误处理

- 连接失败：显示友好错误信息，包含可能的原因
- SQL 执行错误：显示数据库返回的错误信息
- JSON 解析错误：提示正确的 JSON 格式
- 无权限操作：提示需要相应权限

## 兼容性

- 保留现有 MCP 服务器功能
- CLI 工具复用所有数据库层代码
- 配置文件格式不变