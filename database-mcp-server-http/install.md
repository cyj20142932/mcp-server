# 全局（用户级）配置 ‌：
适用于所有项目，存储在用户主目录下。
‌macOS/Linux‌：~/.claude.json
‌Windows‌：C:\Users\用户名\.claude.json
# ‌项目级配置 ‌：
仅对当前项目生效，存储在项目根目录下。
路径 ‌：项目根目录中的 .mcp.json 文件


```
"mcpServers": {
    "database-mcp-server": {
    "command": "python",
    "args": [
        "C:\\Users\\Administrator\\Desktop\\mcp-server\\database-mcp-server\\src\\server.py"
    ],
"env": {
    "MCP_DB_CONFIG": "C:\\Users\\Administrator\\Desktop\\mcp-server\\database-mcp-server\\databases.json"
      }
    }
}

```
