# Swagger MCP Server

MCP Server for Swagger/OpenAPI - API exploration and testing for frontend developers.

## Features

- **Multi-backend support** - Manage multiple API services
- **OpenAPI spec parsing** - Load from URL or local file
- **API exploration** - List endpoints, view details, explore schemas
- **API testing** - Call endpoints directly with auto-filled parameters
- **Authentication** - Bearer Token, API Key, Basic Auth
- **Multi-environment** - dev/test/prod environment support

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Run the server
swagger-mcp-server
```

Or with Python:

```bash
python -m src.server
```

## Tools

### Backend Management

- `add_backend` - Add a new API backend
- `remove_backend` - Remove a backend
- `list_backends` - List all backends
- `set_active_backend` - Switch active backend
- `get_current_backend` - Get current backend info
- `add_environment` - Add environment (dev/test/prod)
- `set_environment` - Switch environment
- `update_auth` - Update authentication

### API Exploration

- `load_spec` - Reload OpenAPI spec
- `list_endpoints` - List all API endpoints
- `get_endpoint` - Get endpoint details
- `list_schemas` - List all schema definitions
- `get_schema` - Get specific schema
- `get_api_info` - Get API information

### API Testing

- `call_api` - Call an API endpoint
- `test_endpoint` - Test with auto-filled parameters
- `generate_request` - Generate request parameters

## Example

```python
# Add a backend
add_backend(
    name="My API",
    base_url="https://api.example.com",
    spec_source="https://api.example.com/openapi.json",
    spec_type="url",
    auth_type="bearer",
    auth_token="your-token-here"
)

# List endpoints
list_endpoints()

# Get endpoint details
get_endpoint("/users/{id}", "GET")

# Call API
call_api("/users/123", "GET")
```