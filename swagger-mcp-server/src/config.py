"""Configuration management for Swagger MCP Server."""
import json
import os
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".swagger-mcp-server"
CONFIG_FILE = CONFIG_DIR / "backends.json"


def ensure_config_dir():
    """Ensure config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load backends configuration."""
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        return {"backends": {}, "active_backend": None}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"backends": {}, "active_backend": None}


def save_config(config: dict):
    """Save backends configuration."""
    ensure_config_dir()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_backends() -> dict:
    """Get all backends."""
    config = load_config()
    return config.get("backends", {})


def get_active_backend() -> str | None:
    """Get active backend ID."""
    config = load_config()
    return config.get("active_backend")


def set_active_backend(backend_id: str):
    """Set active backend."""
    config = load_config()
    if backend_id in config.get("backends", {}):
        config["active_backend"] = backend_id
        save_config(config)


def add_backend(backend_id: str, backend_data: dict):
    """Add or update a backend."""
    config = load_config()
    if "backends" not in config:
        config["backends"] = {}
    config["backends"][backend_id] = backend_data

    # Set as active if first backend
    if config.get("active_backend") is None:
        config["active_backend"] = backend_id

    save_config(config)


def remove_backend(backend_id: str):
    """Remove a backend."""
    config = load_config()
    if backend_id in config.get("backends", {}):
        del config["backends"][backend_id]

        # Clear active if removed
        if config.get("active_backend") == backend_id:
            config["active_backend"] = None
            # Set first available as active
            if config["backends"]:
                config["active_backend"] = next(iter(config["backends"]))

        save_config(config)


def get_backend(backend_id: str) -> dict | None:
    """Get backend by ID."""
    backends = get_backends()
    return backends.get(backend_id)


def get_current_backend() -> tuple[str, dict] | tuple[None, None]:
    """Get current active backend (id, data)."""
    active_id = get_active_backend()
    if active_id:
        backend = get_backend(active_id)
        if backend:
            return active_id, backend
    return None, None