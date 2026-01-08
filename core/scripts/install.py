"""
SpineHUB Install Script

Installs SpineHUB structure in a target project directory.
Usage: python install.py [target_path] [--name PROJECT_NAME]
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


# SpineHUB root directory
SPINEHUB_ROOT = Path(__file__).parent.parent.parent
TEMPLATES_DIR = SPINEHUB_ROOT / "core" / "templates"
COMMANDS_DIR = SPINEHUB_ROOT / "core" / "commands"
CREDENTIALS_DIR = SPINEHUB_ROOT / "credentials"
REGISTRY_FILE = SPINEHUB_ROOT / "projects" / "registry.json"


def get_git_user():
    """Get git user name and email."""
    import subprocess

    try:
        name = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        email = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        return name, email
    except Exception:
        return "User", "user@example.com"


def render_template(template_path: Path, variables: dict) -> str:
    """Render a template file with variables."""
    content = template_path.read_text(encoding="utf-8")
    for key, value in variables.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    return content


def install_spinehub(target_path: Path, project_name: str = None, description: str = "", tech_stack: str = ""):
    """Install SpineHUB structure in target directory."""

    target_path = Path(target_path).resolve()

    if not target_path.exists():
        target_path.mkdir(parents=True)

    # Detect project name if not provided
    if not project_name:
        project_name = target_path.name

    # Get user info
    user_name, user_email = get_git_user()

    # Template variables
    today = datetime.now().strftime("%Y-%m-%d")
    variables = {
        "PROJECT_NAME": project_name,
        "PROJECT_DESCRIPTION": description or "A project managed with SpineHUB",
        "TECH_STACK": tech_stack or "Python",
        "INSTALL_DATE": today,
        "USER_NAME": user_name,
        "USER_EMAIL": user_email,
        "INITIAL_PHASE": "Setup",
        "MAIN_DIRS": "src/\ntests/",
        "PROJECT_RULES": "- Follow project coding standards\n- Write tests for new features",
        "DATE": today,
        "DESCRIPTION": "Initial Setup",
        "DURATION": "N/A",
        "SUMMARY": "SpineHUB structure installed",
    }

    print(f"\n{'='*60}")
    print("  SpineHUB Installation")
    print(f"{'='*60}\n")
    print(f"Target: {target_path}")
    print(f"Project: {project_name}")
    print(f"User: {user_name}")
    print()

    # Create directory structure
    dirs_to_create = [
        ".claude",
        ".claude/commands",
        "sessions",
        "knowledge-base",
    ]

    for dir_name in dirs_to_create:
        dir_path = target_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  [OK] Created {dir_name}/")

    # Copy and render templates
    templates = [
        ("CLAUDE.md.template", "CLAUDE.md"),
        ("memory.md.template", ".claude/memory.md"),
        ("settings.json.template", ".claude/settings.json"),
        ("session.md.template", "sessions/_template.md"),
    ]

    for template_name, dest_name in templates:
        template_path = TEMPLATES_DIR / template_name
        if template_path.exists():
            content = render_template(template_path, variables)
            dest_path = target_path / dest_name
            dest_path.write_text(content, encoding="utf-8")
            print(f"  [OK] Created {dest_name}")

    # Append to .gitignore
    gitignore_path = target_path / ".gitignore"
    gitignore_template = TEMPLATES_DIR / "gitignore.template"

    if gitignore_template.exists():
        gitignore_content = gitignore_template.read_text(encoding="utf-8")

        if gitignore_path.exists():
            existing = gitignore_path.read_text(encoding="utf-8")
            if "# SpineHUB" not in existing:
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    f.write("\n\n" + gitignore_content)
                print("  [OK] Updated .gitignore")
        else:
            gitignore_path.write_text(gitignore_content, encoding="utf-8")
            print("  [OK] Created .gitignore")

    # Copy commands
    for cmd_file in COMMANDS_DIR.glob("*.md"):
        dest_path = target_path / ".claude" / "commands" / cmd_file.name
        shutil.copy2(cmd_file, dest_path)
        print(f"  [OK] Installed command: {cmd_file.name}")

    # Create knowledge-base README
    kb_readme = target_path / "knowledge-base" / "README.md"
    kb_readme.write_text(f"""# Knowledge Base - {project_name}

This directory contains permanent documentation for the project.

## Contents

- API documentation
- Architecture decisions
- Troubleshooting guides
- Integration notes

---

*Managed by SpineHUB*
""", encoding="utf-8")
    print("  [OK] Created knowledge-base/README.md")

    # Link credentials if master exists
    master_env = CREDENTIALS_DIR / ".env.master"
    if master_env.exists():
        env_path = target_path / ".env"
        if not env_path.exists():
            # Copy instead of symlink for Windows compatibility
            shutil.copy2(master_env, env_path)
            print("  [OK] Copied credentials from master")

    # Register project
    register_project(target_path, project_name)

    # Initialize git if needed
    git_dir = target_path / ".git"
    if not git_dir.exists():
        import subprocess
        subprocess.run(["git", "init"], cwd=target_path, capture_output=True)
        print("  [OK] Initialized git repository")

    print(f"\n{'='*60}")
    print("  Installation Complete!")
    print(f"{'='*60}\n")
    print("Next steps:")
    print("  1. Review and customize CLAUDE.md")
    print("  2. Run /status to verify setup")
    print("  3. Start working and use /consolidar at the end")
    print()

    return True


def register_project(project_path: Path, project_name: str):
    """Register project in SpineHUB registry."""

    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)

    if REGISTRY_FILE.exists():
        registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    else:
        registry = {"projects": [], "version": "3.1"}

    # Check if already registered
    project_path_str = str(project_path)
    for p in registry["projects"]:
        if p["path"] == project_path_str:
            p["last_updated"] = datetime.now().isoformat()
            print("  [OK] Updated registry entry")
            REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
            return

    # Add new entry
    registry["projects"].append({
        "name": project_name,
        "path": project_path_str,
        "installed": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "spinehub_version": "3.1",
    })

    REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    print("  [OK] Registered in SpineHUB")


def main():
    parser = argparse.ArgumentParser(description="Install SpineHUB in a project")
    parser.add_argument("target", nargs="?", default=".", help="Target directory (default: current)")
    parser.add_argument("--name", "-n", help="Project name (default: directory name)")
    parser.add_argument("--description", "-d", help="Project description")
    parser.add_argument("--stack", "-s", help="Tech stack (e.g., Python, TypeScript)")

    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    install_spinehub(
        target_path,
        project_name=args.name,
        description=args.description or "",
        tech_stack=args.stack or "",
    )


if __name__ == "__main__":
    main()
