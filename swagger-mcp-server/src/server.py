"""MCP Server for Swagger/OpenAPI - simple version."""
import json
import requests
import yaml
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("swagger-mcp-server")


def _load_spec():
    """Load OpenAPI spec from config."""
    from src import config

    spec_file = config.get_spec_file()
    if not spec_file:
        return None, "Not configured. Run configure_swagger first."

    spec_data = None

    # Check if it's a URL
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
            return None, f"Failed to fetch spec: {e}"
    else:
        # It's a file path
        spec_path = Path(spec_file)
        if not spec_path.exists():
            return None, f"Spec file not found: {spec_file}"

        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                spec_data = json.loads(content)
            except json.JSONDecodeError:
                spec_data = yaml.safe_load(content)
        except Exception as e:
            return None, f"Failed to load spec: {e}"

    return spec_data, None


@mcp.tool()
def configure_swagger(spec_source: str, base_url: str) -> str:
    """Configure OpenAPI spec file/URL and base URL.

    Args:
        spec_source: Path to OpenAPI/Swagger JSON file, or URL to fetch spec
        base_url: Base URL of the API (e.g., https://api.example.com)
    """
    from src import config
    return config.configure(spec_source, base_url)


@mcp.tool()
def list_endpoints() -> str:
    """List all API endpoints from the OpenAPI spec."""
    from src.parser.openapi import OpenAPIParser

    spec, error = _load_spec()
    if error:
        return error

    parser = OpenAPIParser(spec)
    endpoints = parser.list_endpoints()

    if not endpoints:
        return "No endpoints found."

    by_path = {}
    for ep in endpoints:
        path = ep["path"]
        if path not in by_path:
            by_path[path] = []
        by_path[path].append(ep)

    lines = ["## API Endpoints", ""]
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
    """Get detailed information about an API endpoint.

    Args:
        path: API path (e.g., "/users/{id}")
        method: HTTP method (GET, POST, PUT, DELETE, PATCH)
    """
    from src.parser.openapi import OpenAPIParser

    spec, error = _load_spec()
    if error:
        return error

    parser = OpenAPIParser(spec)
    details = parser.get_endpoint_details(path.rstrip("/"), method.lower())

    if not details:
        return f"Endpoint {method} {path} not found."

    lines = [f"## {details['method']} {details['path']}", ""]

    if details.get("summary"):
        lines.append(f"**Summary:** {details['summary']}")
        lines.append("")

    if details.get("description"):
        lines.append(details["description"])
        lines.append("")

    # Parameters
    params = details.get("parameters", [])
    if params:
        lines.append("### Parameters")
        lines.append("")
        for param in params:
            required = " (required)" if param.get("required") else ""
            lines.append(f"- **{param['name']}** ({param['in']}){required}")
            if param.get("description"):
                lines.append(f"  - {param['description']}")
            schema = param.get("schema", {})
            if schema:
                type_ = schema.get("type", "any")
                lines.append(f"  - Type: `{type_}`")
            lines.append("")

    # Request Body
    body = details.get("request_body")
    if body:
        lines.append("### Request Body")
        lines.append("")
        if body.get("description"):
            lines.append(body["description"])
        schema = body.get("schema", {})
        if schema:
            lines.append("```json")
            lines.append(json.dumps(schema, indent=2, ensure_ascii=False))
            lines.append("```")
        lines.append("")

    # Responses
    responses = details.get("responses", {})
    if responses:
        lines.append("### Responses")
        lines.append("")
        for status, response in responses.items():
            lines.append(f"#### {status}")
            lines.append(response.get("description", ""))
            lines.append("")

    return "\n".join(lines)


@mcp.tool()
def list_schemas() -> str:
    """List all Schema definitions."""
    from src.parser.openapi import OpenAPIParser

    spec, error = _load_spec()
    if error:
        return error

    parser = OpenAPIParser(spec)
    schemas = parser.get_schemas()

    if not schemas:
        return "No schemas found."

    lines = ["## Schema Definitions", ""]
    for name, schema in schemas.items():
        lines.append(f"### {name}")
        lines.append("```json")
        lines.append(json.dumps(schema, indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


@mcp.tool()
def get_schema(schema_name: str) -> str:
    """Get a specific Schema definition.

    Args:
        schema_name: Name of the schema (e.g., "User", "Order")
    """
    from src.parser.openapi import OpenAPIParser

    spec, error = _load_spec()
    if error:
        return error

    parser = OpenAPIParser(spec)
    schema = parser.get_schema(schema_name)

    if not schema:
        return f"Schema '{schema_name}' not found."

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
    """Call an API endpoint.

    Args:
        path: API path (e.g., "/users/123")
        method: HTTP method
        params: Query parameters as JSON string (e.g., '{"limit": 10}')
        body: Request body as JSON string
    """
    from src import config
    import time

    base_url = config.get_base_url()
    if not base_url:
        return "Not configured. Run configure_swagger first."

    # Parse parameters
    try:
        query_params = json.loads(params) if params else {}
    except json.JSONDecodeError:
        return f"Invalid JSON in params: {params}"

    # Build URL
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

    # Prepare body
    request_body = None
    if body:
        try:
            request_body = json.loads(body)
        except json.JSONDecodeError:
            return f"Invalid JSON in body: {body}"

    # Make request
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
        return f"Request failed: {str(e)}"

    elapsed = time.time() - start_time

    # Format response
    lines = [
        "## API Response",
        "",
        f"**Status:** {response.status_code} {response.reason}",
        f"**Time:** {elapsed*1000:.2f}ms",
        "",
    ]

    # Response body
    try:
        response_json = response.json()
        lines.append("### Body")
        lines.append("```json")
        lines.append(json.dumps(response_json, indent=2, ensure_ascii=False))
        lines.append("```")
    except json.JSONDecodeError:
        lines.append("### Body")
        lines.append("```")
        lines.append(response.text[:2000])
        lines.append("```")

    return "\n".join(lines)


def main():
    """Main entry point."""
    mcp.run()


if __name__ == "__main__":
    main()