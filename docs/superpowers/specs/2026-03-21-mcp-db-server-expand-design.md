# MCP 数据库服务器功能扩展设计

**Date:** 2026-03-21
**Status:** Draft
**Author:** Claude

## 目标

扩展 mcp-db-server，增加数据探索和数据操作功能。

## 架构

采用混合模式：
- 基础方法在各数据库类中实现
- 高级工具函数在 tools 模块中组合调用

```
src/
├── database/
│   ├── base.py     # 添加抽象方法
│   ├── mysql.py    # 实现 MySQL 特有逻辑
│   ├── oracle.py   # 实现 Oracle 特有逻辑
│   └── starrocks.py # 实现 StarRocks 特有逻辑
├── tools/
│   ├── ddl.py           # 现有
│   ├── query.py         # 现有
│   ├── metadata.py      # 新增：数据探索工具
│   └── manipulation.py  # 新增：数据操作工具
└── server.py            # 新增 MCP 工具
```

## 新增功能

### 数据探索工具（9个）

| 工具名 | 功能 | 数据库支持 |
|--------|------|------------|
| `get_columns` | 获取表的列信息（名称、类型、可空、默认值、注释） | MySQL, Oracle, StarRocks |
| `get_views` | 获取数据库中的视图列表 | MySQL, Oracle, StarRocks |
| `get_view_ddl` | 获取视图的 DDL 定义 | MySQL, Oracle, StarRocks |
| `get_indexes` | 获取表的索引信息 | MySQL, Oracle, StarRocks |
| `get_constraints` | 获取表的约束信息 | MySQL, Oracle, StarRocks |
| `get_foreign_keys` | 获取表的外键关系 | MySQL, Oracle, StarRocks |
| `get_procedures` | 获取存储过程列表 | MySQL, Oracle |
| `get_procedure_ddl` | 获取存储过程定义 | MySQL, Oracle |
| `get_functions` | 获取函数列表 | MySQL, Oracle |

### 数据操作工具（5个）

| 工具名 | 功能 | 数据库支持 |
|--------|------|------------|
| `insert_data` | 插入单条或批量数据 | MySQL, Oracle, StarRocks |
| `update_data` | 更新数据（支持 WHERE 条件） | MySQL, Oracle, StarRocks |
| `delete_data` | 删除数据（支持 WHERE 条件） | MySQL, Oracle, StarRocks |
| `commit_transaction` | 提交事务 | MySQL, Oracle, StarRocks |
| `rollback_transaction` | 回滚事务 | MySQL, Oracle, StarRocks |

## 数据库实现差异

### MySQL/StarRocks
- 使用 `INFORMATION_SCHEMA` 查询元数据
- 视图查询：`INFORMATION_SCHEMA.VIEWS`
- 索引查询：`INFORMATION_SCHEMA.STATISTICS`
- 约束查询：`INFORMATION_SCHEMA.TABLE_CONSTRAINTS`
- 外键查询：`INFORMATION_SCHEMA.KEY_COLUMN_USAGE`

### Oracle
- 使用 `ALL_*` 数据字典视图查询
- 视图查询：`ALL_VIEWS`
- 索引查询：`ALL_INDEXES`, `ALL_IND_COLUMNS`
- 约束查询：`ALL_CONSTRAINTS`
- 外键查询：`ALL_CONS_COLUMNS`
- 存储过程/函数：`ALL_PROCEDURES`, `ALL_SOURCE`

## 错误处理

- 数据库连接失败返回错误信息
- SQL 执行失败返回具体错误详情
- 不支持的数据库类型返回明确提示

## 测试策略

- 单元测试：各数据库类的抽象方法实现
- 集成测试：使用 mock 数据库验证工具函数
- 手动测试：连接真实数据库验证功能