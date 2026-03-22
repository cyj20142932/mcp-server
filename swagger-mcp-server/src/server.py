"""MCP Server for Swagger/OpenAPI."""
from fastmcp import FastMCP

mcp = FastMCP("swagger-mcp-server")


# ========== 后端管理工具 ==========

@mcp.tool()
def add_backend(
    name: str,
    base_url: str,
    spec_source: str = "",
    spec_type: str = "url",
    auth_type: str = "none",
    auth_token: str = "",
    auth_api_key: str = "",
    auth_api_key_name: str = "X-API-Key",
    auth_api_key_location: str = "header",
    auth_username: str = "",
    auth_password: str = "",
    backend_id: str = "",
) -> str:
    """Add a new API backend with OpenAPI spec.

    Args:
        name: Backend name (e.g., "My API")
        base_url: Base URL of the API (e.g., "https://api.example.com")
        spec_source: URL or file path to OpenAPI spec (optional)
        spec_type: "url" or "file" - how to load the spec
        auth_type: Authentication type: none, bearer, apikey, basic
        auth_token: Token for bearer auth
        auth_api_key: API key value
        auth_api_key_name: API key header/query name
        auth_api_key_location: Where to send API key: header or query
        auth_username: Username for basic auth
        auth_password: Password for basic auth
        backend_id: Custom ID for the backend (optional)
    """
    from src.tools import backend as backend_tools

    return backend_tools.add_backend(
        name=name,
        base_url=base_url,
        spec_source=spec_source,
        spec_type=spec_type,
        auth_type=auth_type,
        auth_token=auth_token,
        auth_api_key=auth_api_key,
        auth_api_key_name=auth_api_key_name,
        auth_api_key_location=auth_api_key_location,
        auth_username=auth_username,
        auth_password=auth_password,
        backend_id=backend_id,
    )


@mcp.tool()
def remove_backend(backend_id: str) -> str:
    """Remove an API backend."""
    from src.tools import backend as backend_tools
    return backend_tools.remove_backend(backend_id)


@mcp.tool()
def list_backends() -> str:
    """List all configured backends."""
    from src.tools import backend as backend_tools
    return backend_tools.list_backends()


@mcp.tool()
def set_active_backend(backend_id: str) -> str:
    """Set the active backend."""
    from src.tools import backend as backend_tools
    return backend_tools.set_active_backend(backend_id)


@mcp.tool()
def get_current_backend() -> str:
    """Get info about current backend."""
    from src.tools import backend as backend_tools
    return backend_tools.get_current_backend_info()


@mcp.tool()
def add_environment(backend_id: str, env_name: str, base_url: str) -> str:
    """Add an environment to a backend (e.g., dev, test, prod).

    Args:
        backend_id: Backend ID
        env_name: Environment name (e.g., "dev", "test", "prod")
        base_url: Base URL for this environment
    """
    from src.tools import backend as backend_tools
    return backend_tools.add_environment(backend_id, env_name, base_url)


@mcp.tool()
def set_environment(backend_id: str, env_name: str) -> str:
    """Set active environment for a backend."""
    from src.tools import backend as backend_tools
    return backend_tools.set_environment(backend_id, env_name)


@mcp.tool()
def update_auth(
    backend_id: str,
    auth_type: str,
    auth_token: str = "",
    auth_api_key: str = "",
    auth_api_key_name: str = "X-API-Key",
    auth_api_key_location: str = "header",
    auth_username: str = "",
    auth_password: str = "",
) -> str:
    """Update authentication for a backend."""
    from src.tools import backend as backend_tools
    return backend_tools.update_auth(
        backend_id=backend_id,
        auth_type=auth_type,
        auth_token=auth_token,
        auth_api_key=auth_api_key,
        auth_api_key_name=auth_api_key_name,
        auth_api_key_location=auth_api_key_location,
        auth_username=auth_username,
        auth_password=auth_password,
    )


# ========== API 探索工具 ==========

@mcp.tool()
def load_spec(backend_id: str = "") -> str:
    """Load/refresh OpenAPI spec for a backend."""
    from src.tools import explore
    return explore.load_spec(backend_id)


@mcp.tool()
def list_endpoints(group_by: str = "path") -> str:
    """List all API endpoints.

    Args:
        group_by: "path" or "tag" - how to group endpoints
    """
    from src.tools import explore
    return explore.list_endpoints(group_by)


@mcp.tool()
def get_endpoint(path: str, method: str = "GET") -> str:
    """Get detailed information about an API endpoint.

    Args:
        path: API path (e.g., "/users/{id}")
        method: HTTP method (GET, POST, PUT, DELETE, PATCH)
    """
    from src.tools import explore
    return explore.get_endpoint_details(path, method)


@mcp.tool()
def list_schemas() -> str:
    """List all Schema definitions."""
    from src.tools import explore
    return explore.get_schemas()


@mcp.tool()
def get_schema(schema_name: str) -> str:
    """Get a specific Schema definition.

    Args:
        schema_name: Name of the schema (e.g., "User", "Order")
    """
    from src.tools import explore
    return explore.get_schema(schema_name)


@mcp.tool()
def get_api_info() -> str:
    """Get API information."""
    from src.tools import explore
    return explore.get_api_info()


# ========== API 测试工具 ==========

@mcp.tool()
def call_api(
    path: str,
    method: str = "GET",
    params: str = "{}",
    headers: str = "{}",
    body: str = "",
    backend_id: str = "",
) -> str:
    """Call an API endpoint.

    Args:
        path: API path (e.g., "/users/123")
        method: HTTP method
        params: Query parameters as JSON string (e.g., '{"limit": 10}')
        headers: Additional headers as JSON string
        body: Request body as JSON string
        backend_id: Backend ID (uses active if not specified)
    """
    from src.tools import test as test_tools
    return test_tools.call_api(path, method, params, headers, body, backend_id)


@mcp.tool()
def test_endpoint(path: str, method: str = "GET") -> str:
    """Test an endpoint using auto-filled parameters from spec.

    Uses example values from the OpenAPI spec to fill in parameters.
    """
    from src.tools import test as test_tools
    return test_tools.test_endpoint(path, method)


@mcp.tool()
def generate_request(path: str, method: str = "GET") -> str:
    """Generate request parameters from spec (without calling API).

    Shows what parameters are needed for an endpoint.
    """
    from src.tools import test as test_tools
    return test_tools.generate_request(path, method)


def main():
    """Main entry point."""
    mcp.run()


if __name__ == "__main__":
    main()