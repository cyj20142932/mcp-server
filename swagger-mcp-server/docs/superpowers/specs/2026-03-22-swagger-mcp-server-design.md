# Swagger MCP Server 设计文档

## 项目概述

- **项目名称**: swagger-mcp-server
- **项目类型**: MCP (Model Context Protocol) Server
- **核心功能**: 为前端开发提供 Swagger/OpenAPI 文档解析、API 探索和测试能力
- **目标用户**: 前端开发人员，使用 Claude Code 编程时便于理解后端 API

## 功能需求

### 1. 多后端管理
- 添加、删除、切换不同的 API 服务
- 每个后端包含：名称、base URL、认证信息、OpenAPI 文档来源

### 2. 加载 Swagger 文档
- 从 URL 加载远程 OpenAPI/Swagger 文档
- 从本地文件加载（支持 JSON/YAML）
- 解析并缓存文档内容

### 3. API 端点列表
- 按路径+方法分组展示所有端点
- 显示端点简要说明

### 4. API 详情查看
- 请求说明（summary/description）
- 请求参数：path、query、header、body
- 响应结构：状态码、响应体 schema

### 5. Schema/模型查看
- 展示定义的 data model
- 显示字段类型、描述、是否必填

### 6. API 测试
- 根据规范自动填充默认参数
- 支持自定义请求参数
- 显示响应状态码、响应体、响应时间

### 7. 认证支持
- Bearer Token
- API Key（query/header）
- Basic Auth

### 8. 多环境支持
- 每个后端支持多个环境（dev/test/prod）
- 快速切换环境

## 技术方案

### 技术栈
- Python 3.10+
- FastMCP 框架
- pyyaml（YAML 解析）
- requests（HTTP 请求）
- openapi-schema-validator（规范验证）

### 项目结构
```
swagger-mcp-server/
├── src/
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── server.py          # MCP 入口
│   ├── backend/           # 后端管理
│   │   ├── __init__.py
│   │   └── manager.py
│   ├── parser/            # Swagger 解析
│   │   ├── __init__.py
│   │   └── openapi.py
│   ├── tools/             # MCP 工具
│   │   ├── __init__.py
│   │   ├── backend.py     # 后端管理工具
│   │   ├── explore.py     # API 探索工具
│   │   └── test.py        # API 测试工具
│   └── utils/
│       ├── __init__.py
│       └── http.py        # HTTP 客户端
├── pyproject.toml
└── README.md
```

### 数据存储
- 使用 JSON 文件存储后端配置（~/.swagger-mcp-server/backends.json）

## 工具定义

### 后端管理
- `add_backend` - 添加后端服务
- `remove_backend` - 删除后端服务
- `list_backends` - 列出所有后端
- `set_active_backend` - 设置当前使用的后端

### API 探索
- `list_endpoints` - 列出所有 API 端点
- `get_endpoint_details` - 查看端点详情
- `get_schema` - 查看 Schema 定义

### API 测试
- `call_api` - 调用 API 端点

## 验收标准

1. 可以添加多个后端并切换
2. 可以从 URL 或文件加载 Swagger 文档
3. 可以列出所有 API 端点
4. 可以查看端点详情和参数说明
5. 可以查看 Schema 定义
6. 可以直接调用 API 并查看响应
7. 支持 Bearer Token、API Key、Basic Auth 认证