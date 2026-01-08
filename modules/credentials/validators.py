"""
Credential Validators

Functions to validate credentials by making API calls.
Each validator returns a tuple of (is_valid, error_message).
"""

import os
from typing import Tuple, Optional


def validate_slack(bot_token: str = None, user_token: str = None) -> Tuple[bool, Optional[str]]:
    """
    Validate Slack tokens by calling auth.test endpoint.

    Args:
        bot_token: Slack bot token (xoxb-)
        user_token: Slack user token (xoxp-)

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        from slack_sdk import WebClient
        from slack_sdk.errors import SlackApiError
    except ImportError:
        return False, "slack_sdk not installed"

    token = bot_token or user_token
    if not token:
        return False, "No token provided"

    try:
        client = WebClient(token=token)
        response = client.auth_test()

        if response.get("ok"):
            user_id = response.get("user_id", "unknown")
            team = response.get("team", "unknown")
            return True, f"Valid - User: {user_id}, Team: {team}"
        else:
            return False, response.get("error", "Unknown error")

    except SlackApiError as e:
        return False, f"API Error: {e.response.get('error', str(e))}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_linear(api_key: str = None) -> Tuple[bool, Optional[str]]:
    """
    Validate Linear API key by calling viewer query.

    Args:
        api_key: Linear API key (lin_api_)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "No API key provided"

    try:
        import requests

        response = requests.post(
            "https://api.linear.app/graphql",
            headers={
                "Authorization": api_key,
                "Content-Type": "application/json",
            },
            json={"query": "{ viewer { id name email } }"},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            if "data" in data and "viewer" in data["data"]:
                viewer = data["data"]["viewer"]
                return True, f"Valid - User: {viewer.get('name', 'unknown')}"
            elif "errors" in data:
                return False, data["errors"][0].get("message", "Unknown error")

        return False, f"HTTP {response.status_code}"

    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_google(
    client_id: str = None,
    client_secret: str = None,
    refresh_token: str = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate Google OAuth credentials by refreshing the token.

    Args:
        client_id: Google OAuth client ID
        client_secret: Google OAuth client secret
        refresh_token: Google OAuth refresh token

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not all([client_id, client_secret, refresh_token]):
        return False, "Missing credentials"

    try:
        import requests

        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                return True, "Valid - Token refreshed successfully"
            return False, "No access token in response"

        data = response.json()
        return False, data.get("error_description", f"HTTP {response.status_code}")

    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_github(token: str = None) -> Tuple[bool, Optional[str]]:
    """
    Validate GitHub token by calling user endpoint.

    Args:
        token: GitHub personal access token

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not token:
        return False, "No token provided"

    try:
        import requests

        response = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            return True, f"Valid - User: {data.get('login', 'unknown')}"

        if response.status_code == 401:
            return False, "Invalid or expired token"

        return False, f"HTTP {response.status_code}"

    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_anthropic(api_key: str = None) -> Tuple[bool, Optional[str]]:
    """
    Validate Anthropic API key.

    Note: Anthropic doesn't have a simple validation endpoint,
    so we just check the format.

    Args:
        api_key: Anthropic API key (sk-ant-)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "No API key provided"

    if not api_key.startswith("sk-ant-"):
        return False, "Invalid key format (should start with sk-ant-)"

    # Key looks valid format-wise
    return True, "Valid format (not verified with API)"


def validate_gem(api_key: str = None) -> Tuple[bool, Optional[str]]:
    """
    Validate Gem API key.

    Args:
        api_key: Gem API key

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "No API key provided"

    try:
        import requests

        # Gem uses X-API-Key header
        response = requests.get(
            "https://api.gem.com/v0/candidates",
            headers={"X-API-Key": api_key},
            params={"page_size": 1},
            timeout=10,
        )

        if response.status_code == 200:
            return True, "Valid - API accessible"
        elif response.status_code == 401:
            return False, "Invalid API key"
        elif response.status_code == 403:
            return False, "Forbidden - check permissions"

        return False, f"HTTP {response.status_code}"

    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_quickbooks(
    client_id: str = None,
    client_secret: str = None,
    refresh_token: str = None,
    realm_id: str = None,
) -> Tuple[bool, Optional[str]]:
    """
    Validate QuickBooks OAuth credentials.

    Args:
        client_id: QuickBooks OAuth client ID
        client_secret: QuickBooks OAuth client secret
        refresh_token: QuickBooks OAuth refresh token
        realm_id: QuickBooks company/realm ID

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not all([client_id, client_secret, refresh_token]):
        return False, "Missing OAuth credentials"

    try:
        import requests
        import base64

        # Encode credentials
        auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

        response = requests.post(
            "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                return True, f"Valid - Realm: {realm_id or 'unknown'}"
            return False, "No access token in response"

        data = response.json()
        return False, data.get("error_description", f"HTTP {response.status_code}")

    except Exception as e:
        return False, f"Error: {str(e)}"
