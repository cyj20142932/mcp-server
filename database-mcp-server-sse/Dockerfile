# Dockerfile for MCP Database Server

FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    MCP_DB_CONFIG=/app/config/databases.json

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY src/ ./src/
COPY config/ ./config/ 2>/dev/null || true
COPY databases.json.template .

# 创建配置目录并复制默认配置
RUN mkdir -p /app/config && \
    if [ -f databases.json.template ]; then \
        cp databases.json.template /app/config/databases.json; \
    fi

# 暴露端口
EXPOSE 8080

# 启动命令
# 默认启动 Streamable HTTP 模式
CMD ["python", "-m", "src.server", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8080"]