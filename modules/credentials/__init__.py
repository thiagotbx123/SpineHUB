"""
SpineHUB Credentials Manager

Centralized credential management for all projects and services.

Features:
- Validate credentials across services
- Copy credentials to other projects
- Track credential status and expiration
- MCP configuration management

Usage:
    from modules.credentials import CredentialsManager

    cm = CredentialsManager()
    status = cm.validate_all()
    cm.copy_to_project("TSA_CORTEX")
"""

from .manager import CredentialsManager
from .validators import (
    validate_slack,
    validate_linear,
    validate_google,
    validate_github,
)

__all__ = [
    "CredentialsManager",
    "validate_slack",
    "validate_linear",
    "validate_google",
    "validate_github",
]
