# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**swagger-mcp-server** 是一个基于 MCP (Model Context Protocol) 的服务器，用于解析 Swagger/OpenAPI 规范文档，帮助前端开发人员在使用 Claude Code 编程时探索和测试后端 API。

## 常用命令

```bash
# 安装依赖
pip install -e .

# 运行 MCP 服务器（stdio 模式）
python -m src.server

# 或使用已安装的入口点
swagger-mcp-server

# 依赖 anyio 版本需 >=4.0.0（与 mcp 1.26.0 兼容）
pip install "anyio>=4.0.0" --upgrade
```

## 架构

```
src/
├── server.py        # FastMCP 服务器入口，定义 6 个 MCP 工具
├── config.py        # 配置管理，加载/保存 swagger-config.json
└── parser/
    └── openapi.py   # OpenAPI 规范解析器
```

**配置**：通过 `configure_swagger` 工具或手动编辑 `swagger-config.json` 配置，包含 `spec_file`（OpenAPI 文件路径或 URL）和 `base_url`（API 基础 URL）。

**工具列表**：
- `configure_swagger` - 配置 OpenAPI 规范文件和基础 URL
- `list_endpoints` - 列出所有 API 端点
- `get_endpoint` - 获取端点详情（参数、请求体、响应）
- `list_schemas` - 列出所有 Schema 定义
- `get_schema` - 获取指定 Schema
- `call_api` - 直接调用 API 端点

## 交流语言

本项目所有交流均使用中文，包括代码注释和文档。