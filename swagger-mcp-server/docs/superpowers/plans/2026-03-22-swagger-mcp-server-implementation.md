# Swagger MCP Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create an MCP server for Swagger/OpenAPI that helps frontend developers explore and test backend APIs

**Architecture:** Python-based MCP server using FastMCP framework. Supports multiple backends, environment switching, authentication, and OpenAPI spec parsing

**Tech Stack:** Python 3.10+, FastMCP, pyyaml, requests, openapi-schema-validator

---

## Files Created

- `pyproject.toml` - Project configuration
- `.gitignore` - Git ignore rules
- `README.md` - Documentation
- `src/__init__.py` - Package init
- `src/config.py` - Configuration management (backends.json)
- `src/server.py` - MCP server entry point
- `src/backend/__init__.py` - Backend module init
- `src/backend/manager.py` - Backend manager
- `src/parser/__init__.py` - Parser module init
- `src/parser/openapi.py` - OpenAPI spec parser
- `src/tools/__init__.py` - Tools module init
- `src/tools/backend.py` - Backend management tools
- `src/tools/explore.py` - API exploration tools
- `src/tools/test.py` - API testing tools
- `src/utils/__init__.py` - Utils module init
- `src/utils/http.py` - HTTP client with auth support
- `docs/superpowers/specs/2026-03-22-swagger-mcp-server-design.md` - Design spec

---

## Implemented Tools

### Backend Management
- [x] add_backend - Add new API backend
- [x] remove_backend - Remove backend
- [x] list_backends - List all backends
- [x] set_active_backend - Switch backend
- [x] get_current_backend - Get current info
- [x] add_environment - Add dev/test/prod env
- [x] set_environment - Switch environment
- [x] update_auth - Update authentication

### API Exploration
- [x] load_spec - Reload OpenAPI spec
- [x] list_endpoints - List all endpoints
- [x] get_endpoint - Get endpoint details
- [x] list_schemas - List schema definitions
- [x] get_schema - Get specific schema
- [x] get_api_info - Get API information

### API Testing
- [x] call_api - Call API endpoint
- [x] test_endpoint - Test with auto-filled params
- [x] generate_request - Generate request params

---

## Verification

Tested functionality:
- Server imports OK
- Backend management works
- Endpoint listing works
- API calls work

---

## Next Steps

1. Commit the implementation
2. Consider adding Swagger 2.0 support (currently only OpenAPI 3.x tested)
3. Add more error handling