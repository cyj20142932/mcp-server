"""API testing tools."""
import json
import time
from ..backend.manager import manager
from ..parser.openapi import OpenAPIParser
from ..utils.http import HttpClient, build_url


def call_api(
    path: str,
    method: str = "GET",
    params: str = "{}",
    headers: str = "{}",
    body: str = "",
    backend_id: str = "",
) -> str:
    """Call an API endpoint."""
    # Get backend
    if backend_id:
        backend = manager.list_backends().get(backend_id)
        if not backend:
            return f"Backend '{backend_id}' not found"
    else:
        backend_id, backend = manager.get_active_backend()
        if not backend:
            return "No active backend. Use add_backend first."

    # Get base URL from environment
    env_name = backend.get("active_environment", "default")
    env_config = backend.get("environments", {}).get(env_name, {})
    base_url = env_config.get("base_url", backend.get("base_url", ""))

    if not base_url:
        return "No base URL configured for backend."

    # Parse parameters
    try:
        query_params = json.loads(params) if params else {}
    except json.JSONDecodeError:
        return f"Invalid JSON in params: {params}"

    try:
        extra_headers = json.loads(headers) if headers else {}
    except json.JSONDecodeError:
        return f"Invalid JSON in headers: {headers}"

    # Build URL
    url = build_url(base_url, path)

    # Create HTTP client with auth
    client = HttpClient(
        auth_type=backend.get("auth_type", "none"),
        auth_config=backend.get("auth_config", {}),
    )

    # Prepare request body
    request_body = None
    if body:
        try:
            request_body = json.loads(body)
        except json.JSONDecodeError:
            return f"Invalid JSON in body: {body}"

    # Make request
    start_time = time.time()

    try:
        response = client.request(
            method=method.upper(),
            url=url,
            params=query_params,
            json=request_body,
            headers=extra_headers,
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

    # Response headers
    if response.headers:
        lines.append("### Headers")
        for key, value in response.headers.items():
            lines.append(f"- {key}: {value}")
        lines.append("")

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


def test_endpoint(path: str, method: str = "GET") -> str:
    """Test an endpoint with auto-filled parameters from spec."""
    backend_id, backend = manager.get_active_backend()
    if not backend:
        return "No active backend."

    # Get spec
    spec = manager.get_spec(backend_id)
    if not spec:
        return "No OpenAPI spec loaded."

    parser = OpenAPIParser(spec)
    details = parser.get_endpoint_details(path.rstrip("/"), method.lower())

    if not details:
        return f"Endpoint {method} {path} not found in spec."

    # Build parameters from spec
    params = {}
    for param in details.get("parameters", []):
        name = param["name"]
        location = param.get("in", "query")
        schema = param.get("schema", {})

        # Use example if available
        if param.get("example") is not None:
            params[name] = param["example"]
        elif schema.get("example") is not None:
            params[name] = schema["example"]
        elif schema.get("default") is not None:
            params[name] = schema["default"]
        elif schema.get("type") == "integer":
            params[name] = 0
        elif schema.get("type") == "boolean":
            params[name] = False
        elif schema.get("type") == "array":
            params[name] = []
        elif schema.get("type") == "object":
            params[name] = {}

    # Get request body example
    body = ""
    request_body = details.get("request_body")
    if request_body and request_body.get("example"):
        body = json.dumps(request_body["example"], indent=2)

    # Call the API
    return call_api(path, method, json.dumps(params), "{}", body, backend_id)


def generate_request(path: str, method: str = "GET") -> str:
    """Generate request parameters from spec (without calling)."""
    backend_id, backend = manager.get_active_backend()
    if not backend:
        return "No active backend."

    spec = manager.get_spec(backend_id)
    if not spec:
        return "No OpenAPI spec loaded."

    parser = OpenAPIParser(spec)
    details = parser.get_endpoint_details(path.rstrip("/"), method.lower())

    if not details:
        return f"Endpoint {method} {path} not found in spec."

    lines = [
        f"## Request: {method} {path}",
        "",
        "### Parameters",
        "",
    ]

    for param in details.get("parameters", []):
        name = param["name"]
        location = param.get("in", "query")
        required = " (required)" if param.get("required") else ""
        lines.append(f"**{name}** ({location}){required}")

        if param.get("description"):
            lines.append(f"  - {param['description']}")

        schema = param.get("schema", {})
        if schema:
            type_ = schema.get("type", "any")
            lines.append(f"  - Type: `{type_}`")

            if schema.get("enum"):
                lines.append(f"  - Enum: {schema['enum']}")

            if param.get("example") is not None:
                lines.append(f"  - Example: `{param['example']}`")
            elif schema.get("example") is not None:
                lines.append(f"  - Example: `{schema['example']}`")
            elif schema.get("default") is not None:
                lines.append(f"  - Default: `{schema['default']}`")

        lines.append("")

    # Request body
    body = details.get("request_body")
    if body:
        lines.append("### Request Body")
        lines.append("")
        if body.get("required"):
            lines.append("**Required**")
            lines.append("")

        if body.get("example"):
            lines.append("```json")
            lines.append(json.dumps(body["example"], indent=2, ensure_ascii=False))
            lines.append("```")
        elif body.get("schema"):
            lines.append("```json")
            lines.append(json.dumps(body["schema"], indent=2, ensure_ascii=False))
            lines.append("```")

    return "\n".join(lines)