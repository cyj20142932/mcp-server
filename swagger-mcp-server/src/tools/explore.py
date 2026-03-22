"""API exploration tools."""
import json
from ..backend.manager import manager
from ..parser.openapi import OpenAPIParser
from .. import config


def _get_parser() -> tuple[OpenAPIParser | None, str]:
    """Get parser for current backend."""
    backend_id, backend = manager.get_active_backend()
    if not backend:
        return None, "No active backend. Use add_backend first."

    spec = manager.get_spec(backend_id)
    if not spec:
        return None, f"No OpenAPI spec loaded for backend '{backend_id}'. Use add_backend with spec_source."

    return OpenAPIParser(spec), ""


def load_spec(backend_id: str = "") -> str:
    """Load/refresh OpenAPI spec for a backend."""
    if backend_id:
        backend = config.get_backend(backend_id)
        if not backend:
            return f"Backend '{backend_id}' not found"
    else:
        backend_id, backend = manager.get_active_backend()
        if not backend:
            return "No active backend."

    spec = manager.get_spec(backend_id)
    if not spec:
        return f"Failed to load spec for backend '{backend_id}'"

    info = spec.get("info", {})
    return f"Spec loaded: {info.get('title', 'Unknown')} v{info.get('version', '')}"


def list_endpoints(group_by: str = "path") -> str:
    """List all API endpoints."""
    parser, error = _get_parser()
    if error:
        return error

    endpoints = parser.list_endpoints()

    if not endpoints:
        return "No endpoints found in spec."

    if group_by == "tag":
        # Group by tags
        by_tag = {}
        for ep in endpoints:
            tags = ep.get("tags", ["untagged"])
            for tag in tags:
                if tag not in by_tag:
                    by_tag[tag] = []
                by_tag[tag].append(ep)

        lines = ["## API Endpoints (grouped by tag)", ""]
        for tag, eps in by_tag.items():
            lines.append(f"### {tag}")
            for ep in eps:
                lines.append(f"- `{ep['method']}` {ep['path']}")
                if ep.get("summary"):
                    lines.append(f"  - {ep['summary']}")
            lines.append("")

    else:
        # Group by path
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


def get_endpoint_details(path: str, method: str) -> str:
    """Get detailed information about an endpoint."""
    parser, error = _get_parser()
    if error:
        return error

    # Normalize path
    path = path.rstrip("/")

    details = parser.get_endpoint_details(path, method)
    if not details:
        return f"Endpoint {method} {path} not found in spec."

    lines = [f"## {details['method']} {details['path']}", ""]

    if details.get("summary"):
        lines.append(f"**Summary:** {details['summary']}")
        lines.append("")

    if details.get("description"):
        lines.append(details["description"])
        lines.append("")

    if details.get("operation_id"):
        lines.append(f"**Operation ID:** `{details['operation_id']}`")
        lines.append("")

    if details.get("deprecated"):
        lines.append("⚠️ **Deprecated**")
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
                if schema.get("enum"):
                    lines.append(f"  - Enum: {schema['enum']}")
            lines.append("")

    # Request Body
    body = details.get("request_body")
    if body:
        lines.append("### Request Body")
        lines.append("")
        if body.get("description"):
            lines.append(body["description"])
        if body.get("required"):
            lines.append("**Required**")
        schema = body.get("schema", {})
        if schema:
            lines.append("```json")
            lines.append(json.dumps(schema, indent=2, ensure_ascii=False))
            lines.append("```")
        if body.get("example"):
            lines.append("**Example:**")
            lines.append("```json")
            lines.append(json.dumps(body["example"], indent=2, ensure_ascii=False))
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
            schema = response.get("schema", {})
            if schema:
                lines.append("```json")
                lines.append(json.dumps(schema, indent=2, ensure_ascii=False))
                lines.append("```")
            if response.get("example"):
                lines.append("**Example:**")
                lines.append("```json")
                lines.append(json.dumps(response["example"], indent=2, ensure_ascii=False))
                lines.append("```")
            lines.append("")

    return "\n".join(lines)


def get_schemas() -> str:
    """List all Schema definitions."""
    parser, error = _get_parser()
    if error:
        return error

    schemas = parser.get_schemas()

    if not schemas:
        return "No schema definitions found in spec."

    lines = ["## Schema Definitions", ""]
    for name, schema in schemas.items():
        lines.append(f"### {name}")
        required = schema.get("required", [])
        if required:
            lines.append(f"Required: {', '.join(required)}")
        lines.append("```json")
        lines.append(json.dumps(schema, indent=2, ensure_ascii=False))
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def get_schema(schema_name: str) -> str:
    """Get a specific Schema definition."""
    parser, error = _get_parser()
    if error:
        return error

    schema = parser.get_schema(schema_name)
    if not schema:
        return f"Schema '{schema_name}' not found."

    lines = [f"## Schema: {schema_name}", ""]
    required = schema.get("required", [])
    if required:
        lines.append(f"**Required:** {', '.join(required)}")
        lines.append("")

    lines.append("```json")
    lines.append(json.dumps(schema, indent=2, ensure_ascii=False))
    lines.append("```")

    return "\n".join(lines)


def get_api_info() -> str:
    """Get API information."""
    parser, error = _get_parser()
    if error:
        return error

    info = parser.get_info()

    lines = ["## API Information", ""]
    lines.append(f"**Title:** {info.get('title', 'Unknown')}")
    lines.append(f"**Version:** {info.get('version', '')}")
    if info.get("description"):
        lines.append("")
        lines.append(info["description"])
    if info.get("contact"):
        contact = info["contact"]
        if contact.get("name"):
            lines.append(f"**Contact:** {contact['name']}")
        if contact.get("email"):
            lines.append(f"**Email:** {contact['email']}")
        if contact.get("url"):
            lines.append(f"**URL:** {contact['url']}")

    return "\n".join(lines)