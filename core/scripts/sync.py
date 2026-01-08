"""
SpineHUB Sync Script

Synchronizes commands and templates from SpineHUB core to all registered projects.
Usage: python sync.py [--project PROJECT_NAME] [--dry-run]
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


# SpineHUB root directory
SPINEHUB_ROOT = Path(__file__).parent.parent.parent
COMMANDS_DIR = SPINEHUB_ROOT / "core" / "commands"
REGISTRY_FILE = SPINEHUB_ROOT / "projects" / "registry.json"


def get_registered_projects() -> list:
    """Get list of registered projects."""
    if not REGISTRY_FILE.exists():
        return []

    registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    return registry.get("projects", [])


def sync_commands(project_path: Path, dry_run: bool = False) -> list:
    """Sync commands to a project."""
    changes = []

    commands_dest = project_path / ".claude" / "commands"

    if not commands_dest.exists():
        if not dry_run:
            commands_dest.mkdir(parents=True)
        changes.append("Created .claude/commands/")

    for cmd_file in COMMANDS_DIR.glob("*.md"):
        dest_file = commands_dest / cmd_file.name

        # Check if update needed
        needs_update = False
        if not dest_file.exists():
            needs_update = True
            reason = "new"
        else:
            # Compare modification times
            src_mtime = cmd_file.stat().st_mtime
            dest_mtime = dest_file.stat().st_mtime
            if src_mtime > dest_mtime:
                needs_update = True
                reason = "updated"

        if needs_update:
            if not dry_run:
                shutil.copy2(cmd_file, dest_file)
            changes.append(f"{'Would sync' if dry_run else 'Synced'} {cmd_file.name} ({reason})")

    return changes


def sync_project(project: dict, dry_run: bool = False) -> dict:
    """Sync a single project."""
    project_path = Path(project["path"])

    result = {
        "name": project["name"],
        "path": str(project_path),
        "exists": project_path.exists(),
        "changes": [],
        "errors": [],
    }

    if not project_path.exists():
        result["errors"].append(f"Project path does not exist: {project_path}")
        return result

    # Check if SpineHUB structure exists
    claude_dir = project_path / ".claude"
    if not claude_dir.exists():
        result["errors"].append("No .claude directory - run spinehub init first")
        return result

    # Sync commands
    try:
        changes = sync_commands(project_path, dry_run)
        result["changes"].extend(changes)
    except Exception as e:
        result["errors"].append(f"Failed to sync commands: {e}")

    # Update registry
    if not dry_run and result["changes"]:
        update_registry_timestamp(project["path"])

    return result


def update_registry_timestamp(project_path: str):
    """Update last_updated timestamp in registry."""
    if not REGISTRY_FILE.exists():
        return

    registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))

    for p in registry.get("projects", []):
        if p["path"] == project_path:
            p["last_updated"] = datetime.now().isoformat()
            break

    REGISTRY_FILE.write_text(json.dumps(registry, indent=2), encoding="utf-8")


def sync_all(dry_run: bool = False, project_filter: str = None):
    """Sync all registered projects."""

    projects = get_registered_projects()

    if not projects:
        print("No registered projects found.")
        print("Use 'spinehub init' to add projects.")
        return

    # Filter if specified
    if project_filter:
        projects = [p for p in projects if project_filter.lower() in p["name"].lower()]
        if not projects:
            print(f"No projects matching '{project_filter}'")
            return

    print(f"\n{'='*60}")
    print(f"  SpineHUB Sync {'(DRY RUN)' if dry_run else ''}")
    print(f"{'='*60}\n")
    print(f"Found {len(projects)} project(s) to sync\n")

    total_changes = 0
    total_errors = 0

    for project in projects:
        result = sync_project(project, dry_run)

        print(f"--- {result['name']} ---")
        print(f"    Path: {result['path']}")

        if result["errors"]:
            for error in result["errors"]:
                print(f"    [ERROR] {error}")
            total_errors += len(result["errors"])

        if result["changes"]:
            for change in result["changes"]:
                print(f"    [OK] {change}")
            total_changes += len(result["changes"])
        elif not result["errors"]:
            print("    [OK] Already up to date")

        print()

    print(f"{'='*60}")
    print(f"  Summary: {total_changes} changes, {total_errors} errors")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Sync SpineHUB commands to projects")
    parser.add_argument("--project", "-p", help="Sync only this project (name filter)")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be done")
    parser.add_argument("--list", "-l", action="store_true", help="List registered projects")

    args = parser.parse_args()

    if args.list:
        projects = get_registered_projects()
        print(f"\nRegistered Projects ({len(projects)}):\n")
        for p in projects:
            print(f"  - {p['name']}")
            print(f"    Path: {p['path']}")
            print(f"    Last updated: {p.get('last_updated', 'N/A')}")
            print()
        return

    sync_all(dry_run=args.dry_run, project_filter=args.project)


if __name__ == "__main__":
    main()
