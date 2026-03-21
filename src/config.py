"""Configuration loader for database connections."""
import json
import os
from pathlib import Path
from typing import Dict, Any


class DatabaseConfig:
    """Database connection configuration."""

    def __init__(self, config: Dict[str, Any]):
        self.type = config.get("type")
        self.host = config.get("host")
        self.port = config.get("port")
        self.user = config.get("user")
        self.password = config.get("password")
        self.database = config.get("database")
        self.service_name = config.get("service_name")

    def validate(self) -> bool:
        """Validate required fields."""
        required = ["type", "host", "port", "user"]
        return all(getattr(self, field) for field in required)


class ConfigLoader:
    """Load and manage database configurations."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.environ.get(
                "MCP_DB_CONFIG",
                str(Path.home() / "mcp-db-server" / "databases.json")
            )
        self.config_path = Path(config_path)
        self._databases: Dict[str, DatabaseConfig] = {}

    def load(self) -> Dict[str, DatabaseConfig]:
        """Load configurations from JSON file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path) as f:
            data = json.load(f)

        self._databases = {
            k: DatabaseConfig(v)
            for k, v in data.get("databases", {}).items()
        }
        return self._databases

    def get(self, connect_id: str) -> DatabaseConfig:
        """Get config by connect_id."""
        if not self._databases:
            self.load()
        return self._databases.get(connect_id)

    def list_ids(self) -> list:
        """List all available connect_ids."""
        if not self._databases:
            self.load()
        return list(self._databases.keys())


# Global instance
_config: ConfigLoader = None


def get_config(config_path: str = None) -> ConfigLoader:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = ConfigLoader(config_path)
    return _config