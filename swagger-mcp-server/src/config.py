"""Config for Swagger MCP Server - simple version."""
import json
import os
from pathlib import Path

CONFIG_FILE = Path.home() / ".swagger-mcp-server" / "config.json"


def load_config() -> dict:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return {"spec_file": "", "base_url": ""}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"spec_file": "", "base_url": ""}


def save_config(config: dict):
    """Save configuration to file."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_spec_file() -> str:
    """Get OpenAPI spec file path or URL."""
    return load_config().get("spec_file", "")


def get_base_url() -> str:
    """Get base URL."""
    return load_config().get("base_url", "")


def configure(spec_source: str, base_url: str) -> str:
    """Configure the MCP server with OpenAPI spec.

    Args:
        spec_source: Path to OpenAPI/Swagger JSON file, or URL to fetch spec from
        base_url: Base URL of the API (e.g., https://api.example.com)
    """
    import requests
    import yaml

    spec_data = None

    # Check if it's a URL
    if spec_source.startswith("http://") or spec_source.startswith("https://"):
        try:
            response = requests.get(spec_source, timeout=30)
            response.raise_for_status()
            content = response.text

            # Try JSON first, then YAML
            try:
                spec_data = response.json()
            except json.JSONDecodeError:
                spec_data = yaml.safe_load(content)
        except Exception as e:
            return f"Failed to fetch spec from URL: {e}"
    else:
        # It's a file path
        spec_path = Path(spec_source)
        if not spec_path.exists():
            return f"Spec file not found: {spec_source}"

        try:
            with open(spec_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Try JSON first, then YAML
            try:
                spec_data = json.loads(content)
            except json.JSONDecodeError:
                spec_data = yaml.safe_load(content)
        except Exception as e:
            return f"Failed to load spec file: {e}"

    if not spec_data:
        return "Failed to parse spec"

    # Check if it's an OpenAPI spec
    if "openapi" not in spec_data and "swagger" not in spec_data:
        return "Not a valid OpenAPI/Swagger spec file"

    # Determine if spec_source is a URL or file
    is_url = spec_source.startswith("http://") or spec_source.startswith("https://")

    config = {
        "spec_file": spec_source if is_url else str(Path(spec_source).absolute()),
        "base_url": base_url,
    }
    save_config(config)
    return f"Configured: {spec_source}, base_url: {base_url}"