"""Config file utilities for Swagger MCP Server."""
import json
import yaml
from pathlib import Path
from typing import Any
from ..backend.manager import manager
from .. import config


def load_backends_from_file(file_path: str) -> str:
    """Load backends from a configuration file.

    Supports JSON and YAML formats.

    Example JSON:
    {
      "backends": [
        {
          "id": "my-api",
          "name": "My API",
          "base_url": "https://api.example.com",
          "spec_source": "https://api.example.com/openapi.json",
          "spec_type": "url",
          "auth_type": "bearer",
          "auth_config": {
            "token": "your-token"
          },
          "environments": {
            "dev": {"base_url": "https://dev.api.example.com"},
            "prod": {"base_url": "https://api.example.com"}
          }
        }
      ],
      "active_backend": "my-api"
    }

    Example YAML:
    backends:
      - id: my-api
        name: My API
        base_url: https://api.example.com
        spec_source: https://api.example.com/openapi.json
        spec_type: url
        auth_type: bearer
        auth_config:
          token: your-token
        environments:
          dev:
            base_url: https://dev.api.example.com
          prod:
            base_url: https://api.example.com

    active_backend: my-api
    """
    path = Path(file_path)

    if not path.exists():
        return f"Config file not found: {file_path}"

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Try JSON first, then YAML
        try:
            file_config = json.loads(content)
        except json.JSONDecodeError:
            file_config = yaml.safe_load(content)

        if not file_config:
            return "Config file is empty"

        backends_list = file_config.get("backends", [])
        if not backends_list:
            return "No backends found in config file"

        added_count = 0
        for backend in backends_list:
            backend_id = backend.get("id", "").strip()
            name = backend.get("name", "").strip()

            if not backend_id or not name:
                continue

            # Extract auth config
            auth_type = backend.get("auth_type", "none")
            auth_config = backend.get("auth_config", {})

            # Extract environments
            environments = backend.get("environments", {})
            active_env = backend.get("active_environment", "default")

            # Build backend data
            backend_data = {
                "name": name,
                "title": backend.get("title", name),
                "version": backend.get("version", "1.0.0"),
                "base_url": backend.get("base_url", ""),
                "spec_source": backend.get("spec_source"),
                "spec_type": backend.get("spec_type", "url"),
                "auth_type": auth_type,
                "auth_config": auth_config or {},
                "environments": environments or {"default": {"base_url": backend.get("base_url", "")}},
                "active_environment": active_env,
            }

            config.add_backend(backend_id, backend_data)
            added_count += 1

        # Set active backend
        active_id = file_config.get("active_backend")
        if active_id and active_id in config.get_backends():
            config.set_active_backend(active_id)

        return f"Loaded {added_count} backend(s) from {file_path}"

    except Exception as e:
        return f"Failed to load config: {str(e)}"


def export_backends_to_file(file_path: str, format: str = "json") -> str:
    """Export current backends to a configuration file.

    Args:
        file_path: Path to save the config file
        format: "json" or "yaml"
    """
    backends = config.get_backends()
    active_backend = config.get_active_backend()

    if not backends:
        return "No backends to export"

    # Build export data
    backends_list = []
    for backend_id, backend in backends.items():
        backends_list.append({
            "id": backend_id,
            "name": backend.get("name", ""),
            "title": backend.get("title", ""),
            "version": backend.get("version", ""),
            "base_url": backend.get("base_url", ""),
            "spec_source": backend.get("spec_source"),
            "spec_type": backend.get("spec_type", "url"),
            "auth_type": backend.get("auth_type", "none"),
            "auth_config": _mask_auth_config(backend.get("auth_config", {})),
            "environments": backend.get("environments", {}),
            "active_environment": backend.get("active_environment", "default"),
        })

    export_data = {
        "backends": backends_list,
        "active_backend": active_backend,
    }

    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if format == "yaml":
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(export_data, f, allow_unicode=True, default_flow_style=False)
        else:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

        return f"Exported {len(backends)} backend(s) to {file_path}"

    except Exception as e:
        return f"Failed to export config: {str(e)}"


def _mask_auth_config(auth_config: dict) -> dict:
    """Mask sensitive auth config values."""
    masked = auth_config.copy()

    # Mask token
    if "token" in masked and masked["token"]:
        masked["token"] = "***"

    # Mask password
    if "password" in masked and masked["password"]:
        masked["password"] = "***"

    # Mask API key
    if "key" in masked and masked["key"]:
        masked["key"] = "***"

    return masked


def get_config_template(format: str = "json") -> str:
    """Get configuration file template."""
    if format == "yaml":
        return '''backends:
  - id: my-api
    name: My API
    base_url: https://api.example.com
    spec_source: https://api.example.com/openapi.json
    spec_type: url
    auth_type: bearer
    auth_config:
      token: your-token-here
    environments:
      dev:
        base_url: https://dev.api.example.com
      prod:
        base_url: https://api.example.com

active_backend: my-api
'''
    else:
        return json.dumps({
            "backends": [
                {
                    "id": "my-api",
                    "name": "My API",
                    "base_url": "https://api.example.com",
                    "spec_source": "https://api.example.com/openapi.json",
                    "spec_type": "url",
                    "auth_type": "bearer",
                    "auth_config": {
                        "token": "your-token-here"
                    },
                    "environments": {
                        "dev": {"base_url": "https://dev.api.example.com"},
                        "prod": {"base_url": "https://api.example.com"}
                    }
                }
            ],
            "active_backend": "my-api"
        }, ensure_ascii=False, indent=2)