# Swagger MCP Server

MCP Server for Swagger/OpenAPI - Simple API exploration and testing for frontend developers.

## Features

- **Simple config** - Just specify OpenAPI spec file/URL and base URL
- **List endpoints** - View all available API endpoints
- **View endpoint details** - See parameters, request body, responses
- **List schemas** - View data models
- **Call API** - Test API endpoints directly

## Installation

```bash
pip install -e .
```

## Tools

- `configure_swagger` - Configure spec file/URL and base URL
- `list_endpoints` - List all API endpoints
- `get_endpoint` - Get endpoint details
- `list_schemas` - List all schema definitions
- `get_schema` - Get specific schema
- `call_api` - Call an API endpoint

## Claude Code Integration

Add to your Claude Code settings:

```json
{
  "mcpServers": {
    "swagger-mcp-server": {
      "command": "python",
      "args": ["C:\\path\\to\\swagger-mcp-server\\src\\server.py"]
    }
  }
}
```

## Usage

```python
# Configure with URL
configure_swagger(
    spec_source="https://api.example.com/openapi.json",
    base_url="https://api.example.com"
)

# Or use local file
configure_swagger(
    spec_source="C:\\path\\to\\openapi.json",
    base_url="https://api.example.com"
)

# List endpoints
list_endpoints()

# Get endpoint details
get_endpoint("/users/{id}", "GET")

# List schemas
list_schemas()

# Get schema
get_schema("User")

# Call API
call_api("/users/123", "GET")
call_api("/users", "POST", body='{"name": "test"}')
```

## Configuration

The config is stored at: `~/.swagger-mcp-server/config.json