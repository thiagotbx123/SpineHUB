"""
Credentials Manager - Core module for credential management.

Handles:
- Loading credentials from .env files
- Validating credentials with APIs
- Copying credentials to projects
- MCP configuration
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class CredentialStatus:
    """Status of a single credential."""
    service: str
    key_name: str
    is_set: bool
    is_valid: Optional[bool] = None
    error: Optional[str] = None
    last_checked: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "service": self.service,
            "key_name": self.key_name,
            "is_set": self.is_set,
            "is_valid": self.is_valid,
            "error": self.error,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
        }


class CredentialsManager:
    """
    Centralized credential manager for SpineHUB.

    Manages credentials across all services and projects.
    """

    # SpineHUB root directory
    SPINEHUB_ROOT = Path(__file__).parent.parent.parent

    # Expected credentials by service
    CREDENTIAL_SCHEMA = {
        "slack": {
            "keys": ["SLACK_BOT_TOKEN", "SLACK_USER_TOKEN", "SLACK_USER_ID"],
            "optional": ["SLACK_MCP_XOXC_TOKEN", "SLACK_MCP_XOXD_TOKEN"],
        },
        "linear": {
            "keys": ["LINEAR_API_KEY"],
            "optional": ["LINEAR_DEFAULT_TEAM"],
        },
        "google": {
            "keys": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN"],
            "optional": [],
        },
        "github": {
            "keys": ["GITHUB_TOKEN"],
            "optional": [],
        },
        "anthropic": {
            "keys": ["ANTHROPIC_API_KEY"],
            "optional": [],
        },
        "gem": {
            "keys": ["GEM_API_KEY"],
            "optional": [],
        },
        "quickbooks": {
            "keys": ["QUICKBOOKS_CLIENT_ID", "QUICKBOOKS_CLIENT_SECRET"],
            "optional": ["QUICKBOOKS_REFRESH_TOKEN", "QUICKBOOKS_REALM_ID"],
        },
    }

    # MCP config location
    MCP_CONFIG_PATH = Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"

    def __init__(self, env_file: Optional[Path] = None):
        """
        Initialize credentials manager.

        Args:
            env_file: Path to .env file. Defaults to SpineHUB/.env.master
        """
        self.env_file = env_file or (self.SPINEHUB_ROOT / ".env.master")
        self.credentials = {}
        self._load_credentials()

    def _load_credentials(self) -> None:
        """Load credentials from .env file and environment."""
        # Load from .env file
        if self.env_file.exists():
            for line in self.env_file.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    if value:  # Only store non-empty values
                        self.credentials[key] = value

        # Override with environment variables
        for schema in self.CREDENTIAL_SCHEMA.values():
            for key in schema["keys"] + schema.get("optional", []):
                if key in os.environ:
                    self.credentials[key] = os.environ[key]

    def get(self, key: str, default: str = "") -> str:
        """Get a credential value."""
        return self.credentials.get(key, default)

    def is_set(self, key: str) -> bool:
        """Check if a credential is set and non-empty."""
        return bool(self.credentials.get(key))

    def get_status(self, service: str) -> list[CredentialStatus]:
        """Get status of all credentials for a service."""
        if service not in self.CREDENTIAL_SCHEMA:
            return []

        schema = self.CREDENTIAL_SCHEMA[service]
        statuses = []

        for key in schema["keys"]:
            statuses.append(CredentialStatus(
                service=service,
                key_name=key,
                is_set=self.is_set(key),
            ))

        for key in schema.get("optional", []):
            statuses.append(CredentialStatus(
                service=service,
                key_name=f"{key} (optional)",
                is_set=self.is_set(key),
            ))

        return statuses

    def get_all_status(self) -> dict[str, list[CredentialStatus]]:
        """Get status of all credentials."""
        return {
            service: self.get_status(service)
            for service in self.CREDENTIAL_SCHEMA
        }

    def validate_all(self, skip_api_calls: bool = True) -> dict[str, list[CredentialStatus]]:
        """
        Validate all credentials.

        Args:
            skip_api_calls: If True, only check if credentials are set.
                           If False, also make API calls to verify.
        """
        statuses = self.get_all_status()

        if not skip_api_calls:
            # TODO: Implement actual API validation
            pass

        return statuses

    def copy_to_project(self, project_path: Path, services: list[str] = None) -> dict:
        """
        Copy credentials to another project's .env file.

        Args:
            project_path: Path to target project
            services: List of services to copy. None = all

        Returns:
            Dictionary with results
        """
        target_env = project_path / ".env"
        services = services or list(self.CREDENTIAL_SCHEMA.keys())

        # Load existing target .env if exists
        existing = {}
        if target_env.exists():
            for line in target_env.read_text().splitlines():
                if "=" in line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    existing[key.strip()] = value.strip()

        # Prepare credentials to copy
        to_copy = {}
        for service in services:
            if service not in self.CREDENTIAL_SCHEMA:
                continue
            schema = self.CREDENTIAL_SCHEMA[service]
            for key in schema["keys"] + schema.get("optional", []):
                if self.is_set(key):
                    to_copy[key] = self.credentials[key]

        # Merge (new values override existing)
        merged = {**existing, **to_copy}

        # Write back
        lines = []
        for key, value in sorted(merged.items()):
            lines.append(f"{key}={value}")

        target_env.write_text("\n".join(lines) + "\n")

        return {
            "target": str(target_env),
            "copied": len(to_copy),
            "total": len(merged),
            "services": services,
        }

    def get_mcp_status(self) -> dict:
        """Get status of MCP servers."""
        if not self.MCP_CONFIG_PATH.exists():
            return {"error": "MCP config not found", "servers": []}

        config = json.loads(self.MCP_CONFIG_PATH.read_text())
        servers = config.get("mcpServers", {})

        return {
            "config_path": str(self.MCP_CONFIG_PATH),
            "server_count": len(servers),
            "servers": list(servers.keys()),
        }

    def print_status_report(self) -> None:
        """Print a formatted status report."""
        print("\n" + "=" * 60)
        print("         SpineHUB Credentials Status")
        print("=" * 60 + "\n")

        # Credentials status
        all_status = self.get_all_status()

        for service, statuses in all_status.items():
            print(f"[{service.upper()}]")
            for s in statuses:
                icon = "[OK]" if s.is_set else "[--]"
                print(f"  {icon} {s.key_name}")
            print()

        # MCP status
        mcp = self.get_mcp_status()
        print(f"[MCP SERVERS] ({mcp.get('server_count', 0)} configured)")
        for server in mcp.get("servers", []):
            print(f"  [OK] {server}")

        print("\n" + "=" * 60 + "\n")

    def export_for_project(self, services: list[str] = None) -> str:
        """
        Export credentials as .env format string.

        Args:
            services: List of services to export. None = all
        """
        services = services or list(self.CREDENTIAL_SCHEMA.keys())
        lines = []

        for service in services:
            if service not in self.CREDENTIAL_SCHEMA:
                continue

            lines.append(f"# {service.upper()}")
            schema = self.CREDENTIAL_SCHEMA[service]

            for key in schema["keys"]:
                value = self.get(key, "")
                lines.append(f"{key}={value}")

            for key in schema.get("optional", []):
                value = self.get(key, "")
                if value:
                    lines.append(f"{key}={value}")

            lines.append("")

        return "\n".join(lines)
