#!/usr/bin/env python3
"""
SpineHUB Global Activation Script

Allows SpineHUB to be called from any project directory.
Creates a global command that can support other projects.

Usage:
    python activate.py install    # Install globally
    python activate.py uninstall  # Remove global installation
    python activate.py status     # Check installation status
"""

import os
import sys
from pathlib import Path


SPINEHUB_ROOT = Path(__file__).parent.parent.parent.resolve()


def get_shell_config() -> tuple[Path, str]:
    """Detect shell and return config file path and type."""
    shell = os.environ.get("SHELL", "").lower()
    home = Path.home()

    if "zsh" in shell:
        return home / ".zshrc", "zsh"
    elif "bash" in shell:
        # Check for various bash config files
        for config in [".bashrc", ".bash_profile", ".profile"]:
            path = home / config
            if path.exists():
                return path, "bash"
        return home / ".bashrc", "bash"
    elif sys.platform == "win32":
        # Windows - use PowerShell profile
        ps_profile = home / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
        return ps_profile, "powershell"
    else:
        return home / ".profile", "sh"


def get_activation_lines(shell_type: str) -> list[str]:
    """Generate activation lines for shell config."""
    spinehub_path = str(SPINEHUB_ROOT)

    if shell_type == "powershell":
        return [
            "",
            "# SpineHUB Global Activation",
            f'$env:SPINEHUB_ROOT = "{spinehub_path}"',
            f'function spinehub {{ python "{spinehub_path}\\spinehub.py" @args }}',
            "",
        ]
    else:
        return [
            "",
            "# SpineHUB Global Activation",
            f'export SPINEHUB_ROOT="{spinehub_path}"',
            f'alias spinehub="python \\"{spinehub_path}/spinehub.py\\""',
            "",
        ]


def install_global():
    """Install SpineHUB globally."""
    config_path, shell_type = get_shell_config()

    print(f"Installing SpineHUB globally...")
    print(f"  Shell: {shell_type}")
    print(f"  Config: {config_path}")
    print(f"  SpineHUB: {SPINEHUB_ROOT}")
    print()

    # Check if already installed
    marker = "# SpineHUB Global Activation"
    if config_path.exists():
        content = config_path.read_text()
        if marker in content:
            print("[!!] SpineHUB already installed globally")
            print("     Run 'activate.py uninstall' first to reinstall")
            return False

    # Generate activation lines
    lines = get_activation_lines(shell_type)

    # Create parent directory if needed (for PowerShell)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Append to config
    with open(config_path, "a", encoding="utf-8") as f:
        f.writelines(line + "\n" for line in lines)

    print("[OK] SpineHUB installed globally!")
    print()
    print("To activate, run one of:")
    if shell_type == "powershell":
        print(f'  . "{config_path}"')
    else:
        print(f"  source {config_path}")
    print("  OR restart your terminal")
    print()
    print("Then you can use 'spinehub' from any directory:")
    print("  spinehub status")
    print("  spinehub learn")
    print("  spinehub git status")

    return True


def uninstall_global():
    """Remove SpineHUB global installation."""
    config_path, shell_type = get_shell_config()

    if not config_path.exists():
        print("[--] Config file not found, nothing to uninstall")
        return False

    content = config_path.read_text()
    marker = "# SpineHUB Global Activation"

    if marker not in content:
        print("[--] SpineHUB not installed globally")
        return False

    # Remove SpineHUB lines
    lines = content.split("\n")
    new_lines = []
    skip_until_blank = False

    for line in lines:
        if marker in line:
            skip_until_blank = True
            continue
        if skip_until_blank:
            if line.strip() == "":
                skip_until_blank = False
            continue
        new_lines.append(line)

    # Write back
    config_path.write_text("\n".join(new_lines))

    print("[OK] SpineHUB uninstalled from global config")
    print("     Restart your terminal for changes to take effect")

    return True


def check_status():
    """Check SpineHUB global installation status."""
    config_path, shell_type = get_shell_config()

    print("SpineHUB Global Activation Status")
    print("=" * 40)
    print(f"  Shell Type: {shell_type}")
    print(f"  Config File: {config_path}")
    print(f"  SpineHUB Root: {SPINEHUB_ROOT}")
    print()

    # Check if installed
    if config_path.exists():
        content = config_path.read_text()
        if "# SpineHUB Global Activation" in content:
            print("  Status: INSTALLED")
            print()
            print("  You can use 'spinehub' from any directory")
        else:
            print("  Status: NOT INSTALLED")
            print()
            print("  Run 'python activate.py install' to install")
    else:
        print("  Status: NOT INSTALLED (config file doesn't exist)")
        print()
        print("  Run 'python activate.py install' to install")

    # Check if SPINEHUB_ROOT env var is set
    env_root = os.environ.get("SPINEHUB_ROOT")
    if env_root:
        print()
        print(f"  SPINEHUB_ROOT env: {env_root}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if command == "install":
        install_global()
    elif command == "uninstall":
        uninstall_global()
    elif command == "status":
        check_status()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
