"""OpenAPI spec parser."""
from typing import Any


class OpenAPIParser:
    """Parse and extract information from OpenAPI specifications."""

    def __init__(self, spec: dict):
        self.spec = spec

    def get_info(self) -> dict:
        """Get API info."""
        return self.spec.get("info", {})

    def get_base_url(self) -> str | None:
        """Get base URL from spec."""
        # Try servers first
        servers = self.spec.get("servers", [])
        if servers and isinstance(servers, list):
            url = servers[0].get("url")
            if url:
                return url
        # Fall back to host/path
        return self.spec.get("host")

    def list_endpoints(self) -> list[dict]:
        """List all API endpoints."""
        endpoints = []
        paths = self.spec.get("paths", {})

        for path, path_item in paths.items():
            methods = ["get", "post", "put", "delete", "patch", "options", "head"]
            for method in methods:
                operation = path_item.get(method)
                if operation:
                    endpoints.append({
                        "path": path,
                        "method": method.upper(),
                        "summary": operation.get("summary", ""),
                        "description": operation.get("description", ""),
                        "operation_id": operation.get("operationId", ""),
                        "tags": operation.get("tags", []),
                    })

        return endpoints

    def get_endpoint_details(self, path: str, method: str) -> dict | None:
        """Get detailed info for a specific endpoint."""
        path = path.rstrip("/")
        paths = self.spec.get("paths", {})
        path_item = paths.get(path)

        if not path_item:
            # Try with trailing slash
            path_item = paths.get(path + "/")

        if not path_item:
            return None

        method = method.lower()
        operation = path_item.get(method)

        if not operation:
            return None

        # Build detailed info
        details = {
            "path": path,
            "method": method.upper(),
            "summary": operation.get("summary", ""),
            "description": operation.get("description", ""),
            "operation_id": operation.get("operationId", ""),
            "tags": operation.get("tags", []),
            "deprecated": operation.get("deprecated", False),
            "parameters": self._parse_parameters(operation.get("parameters", [])),
            "request_body": self._parse_request_body(operation.get("requestBody")),
            "responses": self._parse_responses(operation.get("responses", {})),
        }

        return details

    def _parse_parameters(self, parameters: list) -> list[dict]:
        """Parse parameters."""
        result = []
        for param in parameters:
            result.append({
                "name": param.get("name"),
                "in": param.get("in"),
                "description": param.get("description", ""),
                "required": param.get("required", False),
                "schema": param.get("schema", {}),
                "example": param.get("example"),
            })
        return result

    def _parse_request_body(self, request_body) -> dict | None:
        """Parse request body."""
        if not request_body:
            return None

        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})

        return {
            "description": request_body.get("description", ""),
            "required": request_body.get("required", False),
            "schema": schema,
            "example": json_content.get("example"),
        }

    def _parse_responses(self, responses: dict) -> dict:
        """Parse responses."""
        result = {}
        for status_code, response in responses.items():
            content = response.get("content", {})
            json_content = content.get("application/json", {})

            result[status_code] = {
                "description": response.get("description", ""),
                "schema": json_content.get("schema", {}),
                "example": json_content.get("example"),
            }
        return result

    def get_schemas(self) -> dict:
        """Get all schema definitions."""
        components = self.spec.get("components", {})
        return components.get("schemas", {})

    def get_schema(self, schema_name: str) -> dict | None:
        """Get specific schema by name."""
        schemas = self.get_schemas()
        return schemas.get(schema_name)

    def resolve_schema(self, schema: dict) -> dict:
        """Resolve $ref in schema to actual definition."""
        if "$ref" not in schema:
            return schema

        ref = schema["$ref"]
        if not ref.startswith("#/components/schemas/"):
            return schema

        schema_name = ref.replace("#/components/schemas/", "")
        return self.get_schema(schema_name) or schema