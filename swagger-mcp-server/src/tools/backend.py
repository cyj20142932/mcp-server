"""Backend management tools."""
import json
from ..backend.manager import manager


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
    """Add a new API backend."""
    # Generate ID if not provided
    if not backend_id:
        backend_id = name.lower().replace(" ", "-")

    # Build auth config
    auth_config = {}
    if auth_type == "bearer" and auth_token:
        auth_config["token"] = auth_token
    elif auth_type == "apikey" and auth_api_key:
        auth_config = {
            "key": auth_api_key,
            "key_name": auth_api_key_name,
            "in": auth_api_key_location,
        }
    elif auth_type == "basic" and auth_username:
        auth_config = {
            "username": auth_username,
            "password": auth_password,
        }

    spec = spec_source if spec_source else None

    return manager.add_backend(
        backend_id=backend_id,
        name=name,
        base_url=base_url,
        spec_source=spec,
        spec_type=spec_type,
        auth_type=auth_type,
        auth_config=auth_config,
    )


def remove_backend(backend_id: str) -> str:
    """Remove an API backend."""
    return manager.remove_backend(backend_id)


def list_backends() -> str:
    """List all configured backends."""
    backends = manager.list_backends()
    active_id, _ = manager.get_active_backend()

    if not backends:
        return "No backends configured. Use add_backend to add one."

    lines = ["## Configured Backends", ""]
    for bid, backend in backends.items():
        active_marker = " *(active)*" if bid == active_id else ""
        env = backend.get("active_environment", "default")
        base_url = backend.get("base_url", "")
        lines.append(f"- **{bid}**: {backend.get('name', 'Unknown')}{active_marker}")
        lines.append(f"  - Base URL: {base_url}")
        lines.append(f"  - Environment: {env}")
        lines.append(f"  - Auth: {backend.get('auth_type', 'none')}")
        lines.append("")

    return "\n".join(lines)


def set_active_backend(backend_id: str) -> str:
    """Set the active backend."""
    return manager.set_active(backend_id)


def add_environment(backend_id: str, env_name: str, base_url: str) -> str:
    """Add environment to backend."""
    return manager.add_environment(backend_id, env_name, base_url)


def set_environment(backend_id: str, env_name: str) -> str:
    """Set active environment for backend."""
    return manager.set_environment(backend_id, env_name)


def get_current_backend_info() -> str:
    """Get info about current backend."""
    backend_id, backend = manager.get_active_backend()

    if not backend:
        return "No active backend. Use add_backend to add one."

    lines = [f"## Active Backend: {backend_id}", ""]
    lines.append(f"**Name:** {backend.get('name', 'Unknown')}")
    lines.append(f"**Title:** {backend.get('title', '')}")
    lines.append(f"**Version:** {backend.get('version', '')}")
    lines.append(f"**Base URL:** {backend.get('base_url', '')}")
    lines.append(f"**Environment:** {backend.get('active_environment', 'default')}")
    lines.append(f"**Auth Type:** {backend.get('auth_type', 'none')}")

    if backend.get("spec_source"):
        lines.append(f"**Spec Source:** {backend.get('spec_source')}")

    # List environments
    envs = backend.get("environments", {})
    if len(envs) > 1:
        lines.append("")
        lines.append("**Environments:**")
        for env_name, env_data in envs.items():
            active = " *(active)*" if env_name == backend.get("active_environment") else ""
            lines.append(f"- {env_name}: {env_data.get('base_url', '')}{active}")

    return "\n".join(lines)


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
    """Update authentication for backend."""
    from .. import config

    backend = config.get_backend(backend_id)
    if not backend:
        return f"Backend '{backend_id}' not found"

    auth_config = {}
    if auth_type == "bearer" and auth_token:
        auth_config["token"] = auth_token
    elif auth_type == "apikey" and auth_api_key:
        auth_config = {
            "key": auth_api_key,
            "key_name": auth_api_key_name,
            "in": auth_api_key_location,
        }
    elif auth_type == "basic" and auth_username:
        auth_config = {
            "username": auth_username,
            "password": auth_password,
        }

    backend["auth_type"] = auth_type
    backend["auth_config"] = auth_config
    config.add_backend(backend_id, backend)

    return f"Authentication updated for backend '{backend_id}'"