"""MCP Server for Swagger/OpenAPI - Swagger/OpenAPI 解析与测试工具"""
import sys
import os
from pathlib import Path
import json

# 添加父目录到路径以便导入模块
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import yaml
from fastmcp import FastMCP

mcp = FastMCP("swagger-mcp-server")


def _load_spec():
    """从配置中加载 OpenAPI 规范文件。"""
    from src import config

    spec_file = config.get_spec_file()
    if not spec_file:
        return None, "未配置。请先运行 configure_swagger。"

    spec_data = None

    # 检查是否为 URL
    if spec_file.startswith("http://") or spec_file.startswith("https://"):
        try:
            response = requests.get(spec_file, timeout=30)
            response.raise_for_status()
            content = response.text

            try:
                spec_data = response.json()
            except json.JSONDecodeError:
                spec_data = yaml.safe_load(content)
        except Exception as e:
            return None, f"获取规范文件失败: {e}"
    else:
        # 文件路径
        spec_path = Path(spec_file)
        if not spec_path.exists():
            return None, f"规范文件不存在: {spec_file}"

        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                spec_data = json.loads(content)
            except json.JSONDecodeError:
                spec_data = yaml.safe_load(content)
        except Exception as e:
            return None, f"加载规范文件失败: {e}"

    return spec_data, None


@mcp.tool()
def configure_swagger(spec_source: str, base_url: str) -> str:
    """配置 OpenAPI 规范文件/URL 和基础 URL。

    参数:
        spec_source: OpenAPI/Swagger JSON 文件路径或获取规范的 URL
        base_url: API 的基础 URL (例如 https://api.example.com)
    """
    from src import config
    return config.configure(spec_source, base_url)


@mcp.tool()
def list_endpoints() -> str:
    """列出 OpenAPI 规范中的所有 API 端点。"""
    from src.parser.openapi import OpenAPIParser

    spec, error = _load_spec()
    if error:
        return error

    parser = OpenAPIParser(spec)
    endpoints = parser.list_endpoints()

    if not endpoints:
        return "未找到端点。"

    by_path = {}
    for ep in endpoints:
        path = ep["path"]
        if path not in by_path:
            by_path[path] = []
        by_path[path].append(ep)

    lines = ["## API 端点", ""]
    for path, eps in sorted(by_path.items()):
        lines.append(f"### {path}")
        for ep in eps:
            lines.append(f"- **{ep['method']}**")
            if ep.get("summary"):
                lines.append(f"  - {ep['summary']}")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def get_endpoint(path: str, method: str = "GET") -> str:
    """获取 API 端点的详细信息。

    参数:
        path: API 路径 (例如 "/users/{id}")
        method: HTTP 方法 (GET, POST, PUT, DELETE, PATCH)
    """
    from src.parser.openapi import OpenAPIParser

    spec, error = _load_spec()
    if error:
        return error

    parser = OpenAPIParser(spec)
    details = parser.get_endpoint_details(path.rstrip("/"), method.lower())

    if not details:
        return f"未找到端点 {method} {path}。"

    lines = [f"## {details['method']} {details['path']}", ""]

    if details.get("summary"):
        lines.append(f"**摘要:** {details['summary']}")
        lines.append("")

    if details.get("description"):
        lines.append(details["description"])
        lines.append("")

    # 参数
    params = details.get("parameters", [])
    if params:
        lines.append("### 参数")
        lines.append("")
        for param in params:
            required = " (必填)" if param.get("required") else ""
            lines.append(f"- **{param['name']}** ({param['in']}){required}")
            if param.get("description"):
                lines.append(f"  - {param['description']}")
            schema = param.get("schema", {})
            if schema:
                type_ = schema.get("type", "any")
                lines.append(f"  - 类型: `{type_}`")
            lines.append("")

    # 请求体
    body = details.get("request_body")
    if body:
        lines.append("### 请求体")
        lines.append("")
        if body.get("description"):
            lines.append(body["description"])
        schema = body.get("schema", {})
        if schema:
            lines.append("```json")
            lines.append(json.dumps(schema, indent=2, ensure_ascii=False))
            lines.append("```")
        lines.append("")

    # 响应
    responses = details.get("responses", {})
    if responses:
        lines.append("### 响应")
        lines.append("")
        for status, response in responses.items():
            lines.append(f"#### {status}")
            lines.append(response.get("description", ""))
            lines.append("")

    return "\n".join(lines)


@mcp.tool()
def list_schemas() -> str:
    """列出所有 Schema 定义。"""
    from src.parser.openapi import OpenAPIParser

    spec, error = _load_spec()
    if error:
        return error

    parser = OpenAPIParser(spec)
    schemas = parser.get_schemas()

    if not schemas:
        return "未找到 Schema。"

    lines = ["## Schema 定义", ""]
    for name, schema in schemas.items():
        lines.append(f"### {name}")
        lines.append("```json")
        lines.append(json.dumps(schema, indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def get_schema(schema_name: str) -> str:
    """获取指定的 Schema 定义。

    参数:
        schema_name: Schema 名称 (例如 "User", "Order")
    """
    from src.parser.openapi import OpenAPIParser

    spec, error = _load_spec()
    if error:
        return error

    parser = OpenAPIParser(spec)
    schema = parser.get_schema(schema_name)

    if not schema:
        return f"未找到 Schema '{schema_name}'。"

    lines = [f"## Schema: {schema_name}", ""]
    lines.append("```json")
    lines.append(json.dumps(schema, indent=2, ensure_ascii=False))
    lines.append("```")

    return "\n".join(lines)


@mcp.tool()
def call_api(
    path: str,
    method: str = "GET",
    params: str = "{}",
    body: str = "",
) -> str:
    """调用 API 端点。

    参数:
        path: API 路径 (例如 "/users/123")
        method: HTTP 方法
        params: 查询参数 JSON 字符串 (例如 '{"limit": 10}')
        body: 请求体 JSON 字符串
    """
    from src import config
    import time

    base_url = config.get_base_url()
    if not base_url:
        return "未配置。请先运行 configure_swagger。"

    # 解析参数
    try:
        query_params = json.loads(params) if params else {}
    except json.JSONDecodeError:
        return f"参数 JSON 格式无效: {params}"

    # 构建 URL
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    # 准备请求体
    request_body = None
    if body:
        try:
            request_body = json.loads(body)
        except json.JSONDecodeError:
            return f"请求体 JSON 格式无效: {body}"

    # 发送请求
    start_time = time.time()
    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            params=query_params,
            json=request_body,
            timeout=30,
        )
    except Exception as e:
        return f"请求失败: {str(e)}"

    elapsed = time.time() - start_time

    # 格式化响应
    lines = [
        "## API 响应",
        "",
        f"**状态:** {response.status_code} {response.reason}",
        f"**耗时:** {elapsed*1000:.2f}ms",
        "",
    ]

    # 响应体
    try:
        response_json = response.json()
        lines.append("### 响应体")
        lines.append("```json")
        lines.append(json.dumps(response_json, indent=2, ensure_ascii=False))
        lines.append("```")
    except json.JSONDecodeError:
        lines.append("### 响应体")
        lines.append("```")
        lines.append(response.text[:2000])
        lines.append("```")

    return "\n".join(lines)


def main():
    """主入口点。"""
    mcp.run()


if __name__ == "__main__":
    main()