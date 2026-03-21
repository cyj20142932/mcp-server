#!/usr/bin/env python3
"""Install MCP Database Server to Claude Code."""
import json
import os
import shutil
import sys
from pathlib import Path


def get_settings_path() -> Path:
    """Get Claude Code settings.json path."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        settings_dir = base / "Claude" / "settings"
    else:
        settings_dir = Path.home() / ".config" / "Claude" / "settings"

    settings_file = settings_dir / "settings.json"
    if not settings_file.exists():
        # Try alternative locations
        settings_file = settings_dir / "settings.local.json"

    return settings_file


def load_settings(settings_path: Path) -> dict:
    """Load existing settings."""
    if settings_path.exists():
        with open(settings_path) as f:
            return json.load(f)
    return {}


def save_settings(settings_path: Path, data: dict):
    """Save settings."""
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(data, f, indent=2)


def add_mcp_config(settings: dict, server_path: Path) -> dict:
    """Add MCP server configuration."""
    mcp_servers = settings.get("mcpServers", {})

    mcp_servers["mcp-db-server"] = {
        "command": "python",
        "args": [str(server_path / "src" / "server.py")],
        "env": {
            "MCP_DB_CONFIG": str(server_path / "databases.json")
        }
    }

    settings["mcpServers"] = mcp_servers
    return settings


def main():
    # Get script directory
    script_dir = Path(__file__).parent.resolve()

    # Check config file
    config_file = script_dir / "databases.json"
    if not config_file.exists():
        # Copy template
        template = script_dir / "databases.json.template"
        if template.exists():
            shutil.copy(template, config_file)
            print(f"Created config file: {config_file}")
            print("Please edit it with your database connections before running.")
        else:
            print("ERROR: No config file found!")
            sys.exit(1)

    # Install dependencies
    print("Installing dependencies...")
    os.system(f"{sys.executable} -m pip install -r {script_dir / 'requirements.txt'}")

    # Update settings
    settings_path = get_settings_path()
    print(f"Updating settings: {settings_path}")

    settings = load_settings(settings_path)
    settings = add_mcp_config(settings, script_dir)
    save_settings(settings_path, settings)

    print("\nInstallation complete!")
    print(f"Config file: {config_file}")
    print("Restart Claude Code to load the MCP server.")


if __name__ == "__main__":
    main()