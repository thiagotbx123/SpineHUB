#!/usr/bin/env python3
"""
SpineHUB CLI - Project Enhancement Toolkit

The main command-line interface for SpineHUB operations.

Usage:
    spinehub init [path] [--name NAME]     Install SpineHUB in a project
    spinehub sync [--project NAME]          Sync commands to all projects
    spinehub git <command>                  Git operations
    spinehub status                         Show current project status
    spinehub learn [--days N] [--sources]   Learn from project activity
    spinehub credentials [status|copy|mcp]  Manage credentials and MCPs
    spinehub activate [install|status]      Install SpineHUB globally
    spinehub list                           List registered projects
    spinehub help                           Show this help
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# SpineHUB root directory
SPINEHUB_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(SPINEHUB_ROOT))


def cmd_init(args):
    """Initialize SpineHUB in a project."""
    from core.scripts.install import install_spinehub

    target = Path(args.path).resolve() if args.path else Path.cwd()
    install_spinehub(
        target,
        project_name=args.name,
        description=args.description or "",
        tech_stack=args.stack or "",
    )


def cmd_sync(args):
    """Sync commands to registered projects."""
    from core.scripts.sync import sync_all

    sync_all(dry_run=args.dry_run, project_filter=args.project)


def cmd_git(args):
    """Git operations."""
    from modules.github.git_manager import GitManager

    try:
        gm = GitManager()
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    git_command = args.git_command

    if git_command == "status":
        print(gm.format_status_report())

    elif git_command == "commit":
        if args.auto:
            result = gm.auto_commit(prefix=args.prefix or "update")
        elif args.message:
            gm.add_all()
            result = gm.commit(args.message)
        else:
            print("Error: Provide --message or use --auto")
            return 1

        if result["success"]:
            print(f"[OK] Commit {result['hash']}: {result['message']}")
        else:
            print(f"[ERROR] {result['error']}")

    elif git_command == "consolidar":
        result = gm.consolidar_commit(summary=args.summary)
        if result["success"]:
            print(f"[OK] Consolidation commit: {result['hash']}")
            print(f"     Message: {result['message']}")
        else:
            print(f"[ERROR] {result['error']}")

    elif git_command == "push":
        result = gm.push(force=args.force, set_upstream=args.upstream)
        if result["success"]:
            print("[OK] Pushed successfully")
        else:
            print(f"[ERROR] {result['output']}")

    elif git_command == "pull":
        result = gm.pull(rebase=args.rebase)
        print(result["output"])

    else:
        print(f"Unknown git command: {git_command}")
        return 1

    return 0


def cmd_status(args):
    """Show current project status."""
    cwd = Path.cwd()

    # Check if in a SpineHUB project
    claude_dir = cwd / ".claude"
    memory_file = claude_dir / "memory.md"

    print("\n" + "=" * 60)
    print("  SpineHUB Status")
    print("=" * 60 + "\n")

    # Project detection
    if claude_dir.exists():
        project_name = cwd.name
        print(f"Project: {project_name}")
        print(f"Path: {cwd}")
        print("SpineHUB: Installed")
    else:
        print(f"Path: {cwd}")
        print("SpineHUB: NOT INSTALLED")
        print("\nRun 'spinehub init' to install SpineHUB here")
        return

    # Memory status
    if memory_file.exists():
        stat = memory_file.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime)
        days_ago = (datetime.now() - mtime).days
        print(f"Memory: Updated {days_ago} days ago ({mtime.strftime('%Y-%m-%d')})")
    else:
        print("Memory: Not found")

    # Sessions count
    sessions_dir = cwd / "sessions"
    if sessions_dir.exists():
        session_count = len(list(sessions_dir.glob("*.md")))
        print(f"Sessions: {session_count} recorded")

    # Knowledge base count
    kb_dir = cwd / "knowledge-base"
    if kb_dir.exists():
        kb_count = len(list(kb_dir.glob("*.md")))
        print(f"Knowledge Base: {kb_count} documents")

    # Git status
    git_dir = cwd / ".git"
    if git_dir.exists():
        try:
            from modules.github.git_manager import GitManager
            gm = GitManager(str(cwd))
            status = gm.get_status()
            print("\nGit:")
            print(f"  Branch: {status['branch']}")
            print(f"  Status: {'clean' if status['clean'] else 'dirty'}")
            if status['ahead'] or status['behind']:
                print(f"  Sync: {status['ahead']} ahead, {status['behind']} behind")
        except Exception:
            print("\nGit: Configured (details unavailable)")

    print("\n" + "=" * 60 + "\n")


def cmd_learn(args):
    """Learn from project activity and feed knowledge graph."""
    from modules.collectors import run_all_collectors, create_collector
    from modules.collectors.base import OwnershipType

    # Determine date range
    days = args.days or 7
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    if args.start:
        start_date = datetime.strptime(args.start, "%Y-%m-%d")
    if args.end:
        end_date = datetime.strptime(args.end, "%Y-%m-%d")

    date_range = (start_date, end_date)

    # Load configuration from .env or environment
    config = {}
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                key, _, value = line.partition("=")
                config[key.strip()] = value.strip()

    # Add environment variables
    for key in ["SLACK_USER_TOKEN", "SLACK_BOT_TOKEN", "SLACK_USER_ID", "LOCAL_SCAN_PATHS"]:
        if key in os.environ:
            config[key] = os.environ[key]

    # Get user ID
    user_id = config.get("USER_ID") or os.getenv("USER") or "User"

    print("\n" + "=" * 60)
    print("           SpineHUB LEARNING")
    print("=" * 60 + "\n")

    print(f"Project: {Path.cwd().name}")
    print(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Days: {days}")
    print()

    # Dry run mode
    if args.dry_run:
        print("[DRY RUN] Would collect from the following sources:\n")
        sources_to_check = args.sources.split(",") if args.sources else ["claude", "slack", "local"]
        for source in sources_to_check:
            collector = create_collector(source, config, date_range, user_id)
            if collector:
                status = "[OK]" if collector.is_configured() else "[--]"
                print(f"  {status} {source}: {'Configured' if collector.is_configured() else 'Not configured'}")
        print()
        return 0

    # Filter sources if specified
    sources_filter = args.sources.split(",") if args.sources else None

    # Run collectors
    async def run():
        if sources_filter:
            # Run only specified collectors
            results = {}
            for source in sources_filter:
                collector = create_collector(source, config, date_range, user_id)
                if collector and collector.is_configured():
                    print(f"\nCollecting from {source}...")
                    result = await collector.collect()
                    results[source] = result
                else:
                    print(f"\n[--] {source}: Not configured")
            return results
        else:
            return await run_all_collectors(config, date_range, user_id)

    results = asyncio.run(run())

    # Display results
    print("\n" + "-" * 60)
    print("SOURCES COLLECTED:")
    print("-" * 60)

    total_events = 0
    all_events = []

    for source, result in results.items():
        status = "[OK]" if result.success else "[!!]"
        count = result.record_count
        total_events += count
        all_events.extend(result.events)

        # Calculate noise filtered (if available from warnings)
        noise_info = ""
        for warn in result.warnings:
            if "Noise reduction" in warn:
                noise_info = f" ({warn.split(':')[1].strip()})"
                break

        print(f"  {status} {source.title()}: {count} events{noise_info}")

        if result.errors:
            for err in result.errors:
                print(f"      ERROR: {err}")

    # Summary statistics
    print("\n" + "-" * 60)
    print("KNOWLEDGE SUMMARY:")
    print("-" * 60)

    my_work = sum(1 for e in all_events if e.ownership == OwnershipType.MY_WORK)
    mentioned = sum(1 for e in all_events if e.ownership == OwnershipType.MENTIONED)
    context = sum(1 for e in all_events if e.ownership == OwnershipType.CONTEXT)

    print(f"  Total Events: {total_events}")
    print(f"  - My Work: {my_work}")
    print(f"  - Mentioned: {mentioned}")
    print(f"  - Context: {context}")

    # Save to SpineHUB data (if src/spinehub exists)
    spinehub_data = SPINEHUB_ROOT / "data" / "spinehub.json"
    if spinehub_data.parent.exists() or args.save:
        spinehub_data.parent.mkdir(exist_ok=True)

        # Load existing data
        existing = {}
        if spinehub_data.exists():
            existing = json.loads(spinehub_data.read_text())

        # Merge new events
        existing_ids = set(existing.get("event_ids", []))
        new_events = [e for e in all_events if e.event_id not in existing_ids]

        if new_events:
            # Append to events list
            events_list = existing.get("events", [])
            for event in new_events:
                events_list.append(event.to_dict())
                existing_ids.add(event.event_id)

            existing["events"] = events_list
            existing["event_ids"] = list(existing_ids)
            existing["last_updated"] = datetime.now().isoformat()
            existing["total_count"] = len(events_list)

            # Save
            spinehub_data.write_text(json.dumps(existing, indent=2, default=str))
            print(f"\n  [OK] Saved {len(new_events)} new events to {spinehub_data}")
        else:
            print("\n  [--] No new events to save")

    print("\n" + "=" * 60 + "\n")
    return 0


def cmd_credentials(args):
    """Manage credentials and MCPs."""
    from modules.credentials import CredentialsManager

    cm = CredentialsManager()
    action = args.action or "status"

    if action == "status":
        cm.print_status_report()

    elif action == "copy":
        if not args.target:
            print("Error: --target required for copy")
            print("Usage: spinehub credentials copy --target /path/to/project")
            return 1

        target = Path(args.target).resolve()
        if not target.exists():
            print(f"Error: Target path not found: {target}")
            return 1

        services = args.services.split(",") if args.services else None
        result = cm.copy_to_project(target, services)

        print(f"\n[OK] Credentials copied to {result['target']}")
        print(f"     Services: {', '.join(result['services'])}")
        print(f"     Copied: {result['copied']} credentials")
        print(f"     Total in .env: {result['total']} credentials\n")

    elif action == "mcp":
        mcp = cm.get_mcp_status()
        print("\n" + "=" * 60)
        print("         MCP Servers Configuration")
        print("=" * 60 + "\n")
        print(f"Config: {mcp.get('config_path', 'Not found')}")
        print(f"Servers: {mcp.get('server_count', 0)}")
        print()
        for server in mcp.get("servers", []):
            print(f"  [OK] {server}")
        print("\n" + "=" * 60 + "\n")

    elif action == "export":
        services = args.services.split(",") if args.services else None
        export = cm.export_for_project(services)
        print(export)

    elif action == "validate":
        from modules.credentials.validators import (
            validate_slack,
            validate_linear,
            validate_github,
        )

        print("\n" + "=" * 60)
        print("         Credential Validation")
        print("=" * 60 + "\n")

        # Slack
        print("[SLACK]")
        valid, msg = validate_slack(
            bot_token=cm.get("SLACK_BOT_TOKEN"),
            user_token=cm.get("SLACK_USER_TOKEN"),
        )
        icon = "[OK]" if valid else "[!!]"
        print(f"  {icon} {msg}\n")

        # Linear
        print("[LINEAR]")
        valid, msg = validate_linear(cm.get("LINEAR_API_KEY"))
        icon = "[OK]" if valid else "[!!]"
        print(f"  {icon} {msg}\n")

        # GitHub
        print("[GITHUB]")
        valid, msg = validate_github(cm.get("GITHUB_TOKEN"))
        icon = "[OK]" if valid else "[!!]"
        print(f"  {icon} {msg}\n")

        print("=" * 60 + "\n")

    else:
        print(f"Unknown action: {action}")
        print("Available: status, copy, mcp, export, validate")
        return 1

    return 0


def cmd_activate(args):
    """Manage global SpineHUB activation."""
    from core.scripts.activate import install_global, uninstall_global, check_status

    action = args.action or "status"

    if action == "install":
        install_global()
    elif action == "uninstall":
        uninstall_global()
    elif action == "status":
        check_status()
    else:
        print(f"Unknown action: {action}")
        print("Available: install, uninstall, status")
        return 1

    return 0


def cmd_validate(args):
    """Validate credentials."""
    if args.what == "credentials":
        from credentials.validate import main as validate_main
        validate_main()
    else:
        print(f"Unknown validation target: {args.what}")


def cmd_list(args):
    """List registered projects."""
    registry_file = SPINEHUB_ROOT / "projects" / "registry.json"

    if not registry_file.exists():
        print("No projects registered yet.")
        print("Use 'spinehub init' to add projects.")
        return

    registry = json.loads(registry_file.read_text(encoding="utf-8"))
    projects = registry.get("projects", [])

    print("\n" + "=" * 60)
    print(f"  Registered Projects ({len(projects)})")
    print("=" * 60 + "\n")

    for p in projects:
        path = Path(p["path"])
        exists = path.exists()
        status = "[OK]" if exists else "[MISSING]"

        print(f"  {status} {p['name']}")
        print(f"       Path: {p['path']}")
        print(f"       Installed: {p.get('installed', 'N/A')[:10]}")
        print()

    print("=" * 60 + "\n")


def cmd_help(args):
    """Show help."""
    print(__doc__)


def main():
    parser = argparse.ArgumentParser(
        description="SpineHUB - Project Enhancement Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # init command
    init_parser = subparsers.add_parser("init", help="Install SpineHUB in a project")
    init_parser.add_argument("path", nargs="?", help="Target path (default: current)")
    init_parser.add_argument("--name", "-n", help="Project name")
    init_parser.add_argument("--description", "-d", help="Project description")
    init_parser.add_argument("--stack", "-s", help="Tech stack")

    # sync command
    sync_parser = subparsers.add_parser("sync", help="Sync commands to projects")
    sync_parser.add_argument("--project", "-p", help="Sync only this project")
    sync_parser.add_argument("--dry-run", "-n", action="store_true", help="Dry run")

    # git command
    git_parser = subparsers.add_parser("git", help="Git operations")
    git_parser.add_argument("git_command", choices=["status", "commit", "consolidar", "push", "pull"])
    git_parser.add_argument("--message", "-m", help="Commit message")
    git_parser.add_argument("--auto", "-a", action="store_true", help="Auto-generate message")
    git_parser.add_argument("--prefix", help="Message prefix for auto")
    git_parser.add_argument("--summary", "-s", help="Summary for consolidar")
    git_parser.add_argument("--force", "-f", action="store_true", help="Force push")
    git_parser.add_argument("--upstream", "-u", action="store_true", help="Set upstream")
    git_parser.add_argument("--rebase", "-r", action="store_true", help="Pull with rebase")

    # status command
    subparsers.add_parser("status", help="Show project status")

    # learn command
    learn_parser = subparsers.add_parser("learn", help="Learn from project activity")
    learn_parser.add_argument("--days", "-d", type=int, default=7, help="Days to collect (default: 7)")
    learn_parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    learn_parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    learn_parser.add_argument("--sources", "-s", help="Comma-separated sources (claude,slack,local)")
    learn_parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be collected")
    learn_parser.add_argument("--save", action="store_true", help="Force save to data/spinehub.json")

    # credentials command
    creds_parser = subparsers.add_parser("credentials", help="Manage credentials and MCPs")
    creds_parser.add_argument("action", nargs="?", choices=["status", "copy", "mcp", "export", "validate"], default="status")
    creds_parser.add_argument("--target", "-t", help="Target project path for copy")
    creds_parser.add_argument("--services", "-s", help="Comma-separated services (slack,linear,github)")

    # activate command
    activate_parser = subparsers.add_parser("activate", help="Install SpineHUB globally")
    activate_parser.add_argument("action", nargs="?", choices=["install", "uninstall", "status"], default="status")

    # validate command (deprecated - use credentials validate)
    validate_parser = subparsers.add_parser("validate", help="Validate configuration")
    validate_parser.add_argument("what", choices=["credentials"], help="What to validate")

    # list command
    subparsers.add_parser("list", help="List registered projects")

    # help command
    subparsers.add_parser("help", help="Show help")

    # Parse args
    args = parser.parse_args()

    if not args.command or args.command == "help":
        cmd_help(args)
        return 0

    # Dispatch to command handler
    commands = {
        "init": cmd_init,
        "sync": cmd_sync,
        "git": cmd_git,
        "status": cmd_status,
        "learn": cmd_learn,
        "credentials": cmd_credentials,
        "activate": cmd_activate,
        "validate": cmd_validate,
        "list": cmd_list,
    }

    handler = commands.get(args.command)
    if handler:
        return handler(args) or 0
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
