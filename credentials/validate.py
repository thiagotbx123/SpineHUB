"""
SpineHUB Credentials Validator

Validates that all configured credentials are working.
Usage: python validate.py
"""

import os
import subprocess
from pathlib import Path


def load_env(env_path: Path) -> dict:
    """Load environment variables from file."""
    env = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip()
    return env


def validate_github(token: str) -> dict:
    """Validate GitHub token."""
    if not token:
        return {"valid": False, "error": "Token not set"}

    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            env={**os.environ, "GITHUB_TOKEN": token},
        )

        if result.returncode == 0:
            return {"valid": True, "info": "GitHub CLI authenticated"}
        else:
            # Try API directly
            import urllib.request

            req = urllib.request.Request(
                "https://api.github.com/user",
                headers={"Authorization": f"token {token}"},
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status == 200:
                        import json
                        data = json.loads(resp.read())
                        return {"valid": True, "info": f"User: {data.get('login')}"}
            except Exception as e:
                return {"valid": False, "error": str(e)}

    except Exception as e:
        return {"valid": False, "error": str(e)}


def validate_slack(token: str) -> dict:
    """Validate Slack token."""
    if not token:
        return {"valid": False, "error": "Token not set"}

    try:
        import urllib.request

        req = urllib.request.Request(
            "https://slack.com/api/auth.test",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            import json
            data = json.loads(resp.read())
            if data.get("ok"):
                return {"valid": True, "info": f"Team: {data.get('team')}"}
            else:
                return {"valid": False, "error": data.get("error")}

    except Exception as e:
        return {"valid": False, "error": str(e)}


def validate_linear(token: str) -> dict:
    """Validate Linear API key."""
    if not token:
        return {"valid": False, "error": "Token not set"}

    try:
        import urllib.request
        import json

        query = '{"query": "{ viewer { id name } }"}'
        req = urllib.request.Request(
            "https://api.linear.app/graphql",
            data=query.encode("utf-8"),
            headers={
                "Authorization": token,
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            if "data" in data and data["data"].get("viewer"):
                viewer = data["data"]["viewer"]
                return {"valid": True, "info": f"User: {viewer.get('name')}"}
            else:
                return {"valid": False, "error": "Invalid response"}

    except Exception as e:
        return {"valid": False, "error": str(e)}


def validate_google(creds_path: str) -> dict:
    """Validate Google credentials file."""
    if not creds_path:
        return {"valid": False, "error": "Path not set"}

    path = Path(creds_path)
    if not path.exists():
        return {"valid": False, "error": f"File not found: {creds_path}"}

    try:
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "type" in data:
            return {"valid": True, "info": f"Type: {data.get('type')}"}
        else:
            return {"valid": False, "error": "Invalid credentials format"}

    except Exception as e:
        return {"valid": False, "error": str(e)}


def main():
    """Validate all credentials."""
    credentials_dir = Path(__file__).parent
    env_master = credentials_dir / ".env.master"

    print("\n" + "=" * 60)
    print("  SpineHUB Credentials Validation")
    print("=" * 60 + "\n")

    if not env_master.exists():
        print("[ERROR] .env.master not found")
        print("        Copy .env.template to .env.master and fill in your tokens")
        return 1

    env = load_env(env_master)

    validators = [
        ("GitHub", "GITHUB_TOKEN", validate_github),
        ("Slack Bot", "SLACK_BOT_TOKEN", validate_slack),
        ("Slack User", "SLACK_USER_TOKEN", validate_slack),
        ("Linear", "LINEAR_API_KEY", validate_linear),
        ("Google Drive", "GOOGLE_CREDENTIALS_PATH", validate_google),
    ]

    results = []

    for name, key, validator in validators:
        value = env.get(key, "")
        result = validator(value)
        results.append((name, result))

        status = "[OK]" if result["valid"] else "[--]" if not value else "[FAIL]"
        print(f"  {status} {name}")

        if result["valid"]:
            print(f"       {result.get('info', 'Valid')}")
        elif value:
            print(f"       Error: {result.get('error', 'Unknown')}")
        else:
            print("       Not configured")

    print("\n" + "=" * 60)

    valid_count = sum(1 for _, r in results if r["valid"])
    total_count = len(results)
    print(f"  Valid: {valid_count}/{total_count}")
    print("=" * 60 + "\n")

    return 0 if valid_count > 0 else 1


if __name__ == "__main__":
    exit(main())
