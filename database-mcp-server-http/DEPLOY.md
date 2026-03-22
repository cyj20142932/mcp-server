# Docker 部署指南

本文档介绍如何使用 Docker 部署 MCP Database Server。

## 快速开始

### 1. 构建镜像

```bash
docker build -t mcp-db-server .
```

### 2. 运行容器

```bash
# 基本用法（Streamable HTTP 模式）
docker run -d -p 8080:8080 --name mcp-db-server mcp-db-server

# 指定端口
docker run -d -p 9000:8080 --name mcp-db-server mcp-db-server \
  python -m src.server --transport streamable-http --port 8080

# 挂载自定义配置
docker run -d -p 8080:8080 \
  -v /path/to/databases.json:/app/config/databases.json:ro \
  --name mcp-db-server mcp-db-server
```

## 配置数据库连接

### 方式一：挂载配置文件

```bash
# 创建配置目录
mkdir -p ./config

# 编辑数据库配置
cp databases.json.template ./config/databases.json
vim ./config/databases.json

# 运行容器并挂载配置
docker run -d -p 8080:8080 \
  -v ./config/databases.json:/app/config/databases.json:ro \
  --name mcp-db-server mcp-db-server
```

### 方式二：使用环境变量覆盖配置路径

```bash
docker run -d -p 8080:8080 \
  -e MCP_DB_CONFIG=/app/config/databases.json \
  -v /path/to/databases.json:/app/config/databases.json:ro \
  --name mcp-db-server mcp-db-server
```

## Docker Compose 部署

### 1. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  mcp-db-server:
    build: .
    container_name: mcp-db-server
    ports:
      - "8080:8080"
    volumes:
      - ./config/databases.json:/app/config/databases.json:ro
    environment:
      - MCP_DB_CONFIG=/app/config/databases.json
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 2. 部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 使用 Claude Code 连接

在 Claude Code 的 `settings.json` 中配置：

```json
{
  "mcpServers": {
    "mcp-db-server": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

> **注意**：Streamable HTTP 模式的端点为 `/mcp`

## 网络配置

### 访问宿主机数据库

```bash
# 使用 host.docker.internal (Linux/macOS)
docker run -d -p 8080:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v ./config/databases.json:/app/config/databases.json:ro \
  mcp-db-server

# Windows 使用 host.docker.internal
docker run -d -p 8080:8080 \
  -v ./config/databases.json:/app/config/databases.json:ro \
  mcp-db-server
```

配置文件中的数据库地址应使用 `host.docker.internal` 或 `host-gateway`。

### 使用自定义网络

```yaml
version: '3.8'

services:
  mcp-db-server:
    build: .
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
```

## 生产环境建议

### 1. 安全配置

```bash
# 使用只读配置
docker run -d -p 8080:8080 \
  -v ./config/databases.json:/app/config/databases.json:ro \
  --read-only \
  --tmpfs /tmp \
  mcp-db-server
```

### 2. 资源限制

```yaml
services:
  mcp-db-server:
    build: .
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### 3. 日志管理

```yaml
services:
  mcp-db-server:
    build: .
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 故障排查

### 查看日志

```bash
docker logs mcp-db-server
```

### 进入容器调试

```bash
docker exec -it mcp-db-server /bin/bash
```

### 检查端口占用

```bash
netstat -tlnp | grep 8080
# 或
lsof -i :8080
```

### 常见问题

1. **数据库连接失败**：检查 `databases.json` 中的主机地址是否正确，容器内访问宿主机使用 `host.docker.internal`
2. **端口冲突**：修改 `-p` 参数使用其他端口
3. **权限问题**：确保配置文件路径正确且可读