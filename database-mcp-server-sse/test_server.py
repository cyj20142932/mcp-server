#!/usr/bin/env python
"""Test script for MCP Server."""
import os
import sys

# Set environment
os.environ['MCP_DB_CONFIG'] = r'C:\Users\Administrator\Desktop\mcp_python\databases.json'

# Add src to path
sys.path.insert(0, r'C:\Users\Administrator\Desktop\mcp_python')

# Test imports
print("Testing imports...")
from src.server import mcp
print(f"MCP Server created: {mcp.name}")

# List tools
print(f"Tools registered: {mcp.tool}")

print("\nAll tests passed!")