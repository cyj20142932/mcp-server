# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 **MCP (Model Context Protocol) 服务器集合**，包含多个独立的 MCP 服务器实现。

## 开发行为准则

### 第一条
动手之前先动脑。在写任何代码前，先描述实现思路并等待确认。遇到模糊需求必须追问，不许自作主张。

### 第二条
三个文件是红线。如果一个任务需要改动超过三个文件，必须先拆解成更小的子任务。

### 第三条
写完代码要自检。列出可能出问题的地方，并建议相应的测试用例。

### 第四条
修 bug 先写测试。遇到 bug 时，第一步是写一个能复现问题的测试，然后修到测试通过为止。

### 第五条
每次纠错都要留痕。

## 项目结构

```
mcp-server/
├── database-mcp-server/     # 数据库 MCP 服务器（stdio 模式）
├── database-mcp-server-http/# 数据库 MCP 服务器（支持 HTTP 传输）
└── swagger-mcp-server/      # Swagger/OpenAPI MCP 服务器
```

## 常用命令

### 进入子项目开发

```bash
# 数据库 MCP 服务器
cd database-mcp-server
pip install -e .

# HTTP 版数据库 MCP 服务器
cd database-mcp-server-http
pip install -e .

# Swagger MCP 服务器
cd swagger-mcp-server
pip install -e .
```

### 运行 MCP 服务器

各子项目均支持以下运行方式：

```bash
# stdio 模式（默认）
python -m src.server

# 或使用已安装的入口点
mcp-db-server
swagger-mcp-server
```

## 架构说明

- **database-mcp-server**: 基于 FastMCP，为 MySQL、Oracle、StarRocks 提供数据库工具
- **database-mcp-server-http**: 支持 Streamable HTTP 传输协议的数据库 MCP 服务器
- **swagger-mcp-server**: 解析 Swagger/OpenAPI 规范，帮助探索和测试后端 API

各子项目均有独立的 CLAUDE.md 文件，包含详细的架构和使用说明。

## 交流语言

本项目所有交流均使用中文，包括代码注释和文档。