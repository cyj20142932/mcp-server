"""Backend manager for Swagger MCP Server."""
import requests
import yaml
import json
from pathlib import Path
from typing import Any
from .. import config


class BackendManager:
    """Manage API backends and their OpenAPI specifications."""

    def __init__(self):
        self._spec_cache: dict[str, dict] = {}

    def list_backends(self) -> dict:
        """List all configured backends."""
        return config.get_backends()

    def get_active_backend(self) -> tuple[str | None, dict | None]:
        """Get active backend."""
        return config.get_current_backend()

    def set_active(self, backend_id: str) -> str:
        """Set active backend."""
        backend = config.get_backend(backend_id)
        if not backend:
            return f"Backend '{backend_id}' not found"

        config.set_active_backend(backend_id)
        # Clear spec cache when switching backend
        self._spec_cache.clear()
        return f"Switched to backend '{backend_id}'"

    def add_backend(
        self,
        backend_id: str,
        name: str,
        base_url: str,
        spec_source: str | None = None,
        spec_type: str = "url",  # url or file
        auth_type: str = "none",
        auth_config: dict | None = None,
    ) -> str:
        """Add a new backend."""
        # Validate spec if provided
        if spec_source:
            spec_data = self._load_spec(spec_source, spec_type)
            if isinstance(spec_data, str):  # Error message
                return spec_data
            # Extract info from spec
            info = spec_data.get("info", {})
            title = info.get("title", name)
            version = info.get("version", "1.0.0")
        else:
            title = name
            version = "1.0.0"

        backend_data = {
            "name": name,
            "title": title,
            "version": version,
            "base_url": base_url,
            "spec_source": spec_source,
            "spec_type": spec_type,
            "auth_type": auth_type,
            "auth_config": auth_config or {},
            "environments": {
                "default": {"base_url": base_url, "active": True}
            },
            "active_environment": "default",
        }

        config.add_backend(backend_id, backend_data)
        return f"Backend '{name}' added successfully (ID: {backend_id})"

    def remove_backend(self, backend_id: str) -> str:
        """Remove a backend."""
        if backend_id in config.get_backends():
            config.remove_backend(backend_id)
            self._spec_cache.pop(backend_id, None)
            return f"Backend '{backend_id}' removed"
        return f"Backend '{backend_id}' not found"

    def add_environment(
        self, backend_id: str, env_name: str, base_url: str
    ) -> str:
        """Add environment to backend."""
        backend = config.get_backend(backend_id)
        if not backend:
            return f"Backend '{backend_id}' not found"

        backend.setdefault("environments", {})[env_name] = {
            "base_url": base_url,
            "active": False,
        }
        config.add_backend(backend_id, backend)
        return f"Environment '{env_name}' added to backend '{backend_id}'"

    def set_environment(self, backend_id: str, env_name: str) -> str:
        """Set active environment for backend."""
        backend = config.get_backend(backend_id)
        if not backend:
            return f"Backend '{backend_id}' not found"

        env = backend.get("environments", {}).get(env_name)
        if not env:
            return f"Environment '{env_name}' not found in backend '{backend_id}'"

        backend["active_environment"] = env_name
        config.add_backend(backend_id, backend)
        # Clear spec cache when switching environment
        self._spec_cache.pop(backend_id, None)
        return f"Environment '{env_name}' activated for backend '{backend_id}'"

    def get_spec(self, backend_id: str | None = None) -> dict | None:
        """Get OpenAPI spec for backend."""
        if backend_id is None:
            backend_id, backend = self.get_active_backend()
        else:
            backend = config.get_backend(backend_id)

        if not backend:
            return None

        # Check cache
        cache_key = f"{backend_id}:{backend.get('active_environment', 'default')}"
        if cache_key in self._spec_cache:
            return self._spec_cache[cache_key]

        spec_source = backend.get("spec_source")
        spec_type = backend.get("spec_type", "url")

        if not spec_source:
            return None

        spec_data = self._load_spec(spec_source, spec_type)
        if isinstance(spec_data, dict):
            self._spec_cache[cache_key] = spec_data
            return spec_data

        return None

    def _load_spec(self, source: str, spec_type: str) -> dict | str:
        """Load OpenAPI spec from source."""
        try:
            if spec_type == "url":
                response = requests.get(source, timeout=30)
                response.raise_for_status()
                content = response.text

                # Try JSON first, then YAML
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return yaml.safe_load(content)

            elif spec_type == "file":
                path = Path(source)
                if not path.exists():
                    return f"File not found: {source}"

                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Try JSON first, then YAML
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return yaml.safe_load(content)

            return "Unknown spec type"

        except requests.RequestException as e:
            return f"Failed to fetch spec: {e}"
        except Exception as e:
            return f"Failed to load spec: {e}"


# Global instance
manager = BackendManager()