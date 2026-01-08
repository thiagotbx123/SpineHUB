#!/usr/bin/env python3
"""
SpineHUB CLI

Command-line interface for SpineHUB operations.

Usage:
    python -m src.cli analyze [--path PATH] [--tool TOOL]
    python -m src.cli stats [--path PATH]
    python -m src.cli validate <file>
    python -m src.cli collect [--source SOURCE] [--days DAYS]
    python -m src.cli linear <action> [--template TEMPLATE] [--dry-run]
    python -m src.cli channels [--prefix PREFIX]
    python -m src.cli health [--output FILE]
    python -m src.cli release [--version VERSION] [--major|--minor] [--dry-run]
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


def cmd_analyze(args):
    """Run code analysis."""
    from .analyzers import CodeAnalyzer

    project_path = args.path or "."
    analyzer = CodeAnalyzer(project_path)

    # Check available tools
    tools = analyzer.check_tools()
    print("Available tools:")
    for name, available in tools.items():
        status = "[OK]" if available else "[NOT INSTALLED]"
        print(f"  {status} {name}")
    print()

    if args.tool:
        # Run single tool
        result = analyzer.run_single(args.tool)
        print(result.format_summary())
        if result.issues:
            print("\nIssues:")
            for issue in result.issues[:20]:
                print(f"  {issue.file}:{issue.line} [{issue.code}] {issue.message}")
    else:
        # Run all tools
        result = analyzer.run_all()
        print(result.format_report())

    return 0 if not result.has_errors else 1


def cmd_stats(args):
    """Show SpineHUB statistics."""
    from .spinehub import SpineHub

    data_path = args.path or "data/spinehub.json"
    hub = SpineHub(data_path)
    stats = hub.get_stats()

    print("=" * 50)
    print("SPINEHUB STATISTICS")
    print("=" * 50)
    print(f"Entities: {stats['entities']}")
    print(f"Relations: {stats['relations']}")
    print(f"Artifacts: {stats['artifacts']}")
    print(f"Patterns: {stats['patterns']}")
    print()
    print(f"Last Updated: {stats['metadata'].get('last_updated', 'N/A')}")
    print("=" * 50)

    return 0


def cmd_validate(args):
    """Validate a worklog file."""
    from .spinehub import validate_worklog

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1

    content = file_path.read_text(encoding="utf-8")
    passed, report = validate_worklog(content)

    print(report)

    return 0 if passed else 1


def cmd_collect(args):
    """Run data collectors."""
    # Add modules directory to path
    modules_path = Path(__file__).parent.parent / "modules"
    sys.path.insert(0, str(modules_path.parent))

    from modules.collectors import create_collector, run_all_collectors
    from modules.utils import get_default_date_range

    days = args.days or 7
    date_range = get_default_date_range(days=days)

    config = {
        "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
        "SLACK_USER_TOKEN": os.getenv("SLACK_USER_TOKEN"),
        "LINEAR_API_KEY": os.getenv("LINEAR_API_KEY"),
        "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID"),
        "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET"),
        "GOOGLE_REFRESH_TOKEN": os.getenv("GOOGLE_REFRESH_TOKEN"),
    }

    print("=" * 50)
    print("SPINEHUB DATA COLLECTION")
    print("=" * 50)
    print(f"Date Range: {date_range.start.date()} to {date_range.end.date()}")
    print()

    async def run():
        if args.source:
            # Single collector
            collector = create_collector(
                args.source,
                config,
                (date_range.start, date_range.end)
            )
            if not collector:
                print(f"Error: Unknown source '{args.source}'")
                print("Available: claude, slack, local, linear, drive")
                return 1

            if not collector.is_configured():
                print(f"Error: {args.source} collector not configured")
                print("Check environment variables for credentials")
                return 1

            print(f"Running {args.source} collector...")
            result = await collector.collect()

            print(f"\nResults for {args.source}:")
            print(f"  Events: {result.record_count}")
            if result.errors:
                print(f"  Errors: {', '.join(result.errors)}")
            if result.warnings:
                print(f"  Warnings: {', '.join(result.warnings)}")
        else:
            # All collectors
            results = await run_all_collectors(
                config,
                (date_range.start, date_range.end)
            )

            print("\n" + "=" * 50)
            print("COLLECTION SUMMARY")
            print("=" * 50)
            total = 0
            for source, result in results.items():
                print(f"{source}: {result.record_count} events")
                total += result.record_count
            print(f"\nTotal: {total} events")

        return 0

    return asyncio.run(run())


def cmd_linear(args):
    """Linear automation commands."""
    modules_path = Path(__file__).parent.parent / "modules"
    sys.path.insert(0, str(modules_path.parent))

    from modules.linear import (
        create_generator,
        list_templates,
    )

    if args.action == "templates":
        # List available templates
        print("=" * 50)
        print("AVAILABLE ISSUE TEMPLATES")
        print("=" * 50)
        for template in list_templates():
            print(f"\n[{template.id}] {template.name}")
            print(f"  {template.description}")
            print(f"  Labels: {', '.join(template.labels)}")
            print(f"  Priority: {template.priority}")
        return 0

    elif args.action == "generate":
        # Generate tickets from template
        if not args.matrix:
            print("Error: --matrix required for generate action")
            return 1

        matrix_path = Path(args.matrix)
        if not matrix_path.exists():
            print(f"Error: Matrix file not found: {matrix_path}")
            return 1

        import json
        from modules.linear.templates import MatrixRow

        with open(matrix_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        matrix = [MatrixRow(**row) for row in raw_data]

        team_key = args.team or os.getenv("DEFAULT_TEAM_KEY", "RAC")
        generator = create_generator(team_key)

        template_id = args.template or "weekly_update"
        dry_run = not args.execute

        async def run():
            if not await generator.initialize():
                print("Error: Failed to initialize generator")
                return 1

            results = await generator.process_matrix(
                matrix,
                template_id=template_id,
                dry_run=dry_run,
            )

            print("\n" + "=" * 50)
            print("GENERATION RESULTS")
            print("=" * 50)
            success = sum(1 for r in results if r.success)
            failed = sum(1 for r in results if not r.success)
            print(f"Success: {success}")
            print(f"Failed: {failed}")

            if not dry_run:
                print("\nCreated tickets:")
                for r in results:
                    if r.success and r.issue_url:
                        print(f"  {r.issue_id}: {r.issue_url}")

            return 0

        return asyncio.run(run())

    else:
        print(f"Unknown action: {args.action}")
        print("Available actions: templates, generate")
        return 1


def cmd_channels(args):
    """Map Slack channels and members."""
    modules_path = Path(__file__).parent.parent / "modules"
    sys.path.insert(0, str(modules_path.parent))

    from modules.utils import SlackChannelMapper

    token = os.getenv("SLACK_USER_TOKEN") or os.getenv("SLACK_BOT_TOKEN")
    if not token:
        print("Error: SLACK_USER_TOKEN or SLACK_BOT_TOKEN required")
        return 1

    prefixes = args.prefix.split(",") if args.prefix else ["ext-", "external-"]

    mapper = SlackChannelMapper(token=token, channel_prefixes=prefixes)

    print("=" * 50)
    print("SLACK CHANNEL MAPPING")
    print("=" * 50)
    print(f"Prefixes: {', '.join(prefixes)}")
    print()

    # List channels
    channels = mapper.list_channels()
    print(f"Found {len(channels)} channels\n")

    if args.map:
        # Full mapping with members
        mappings = mapper.map_all_channels()

        print("\n" + "=" * 50)
        print("CHANNEL MAPPINGS")
        print("=" * 50)
        for m in mappings:
            print(f"\n{m.channel}:")
            print(f"  TSA: {', '.join(m.tsa_members) or 'none'}")
            print(f"  ENG: {', '.join(m.eng_members) or 'none'}")
            print(f"  GTM: {', '.join(m.gtm_members) or 'none'}")
            print(f"  External: {', '.join(m.external_members) or 'none'}")

        if args.output:
            mapper.export_to_json(mappings, args.output)
    else:
        # Just list channels
        for ch in channels:
            private = "[PRIVATE]" if ch.is_private else ""
            print(f"  {ch.name} ({ch.num_members} members) {private}")

    return 0


def cmd_health(args):
    """Run comprehensive health check on SpineHUB."""
    import subprocess
    import json

    spinehub_path = Path(__file__).parent.parent

    print("=" * 60)
    print("          SPINEHUB HEALTH CHECK")
    print("=" * 60)
    print(f"Path: {spinehub_path}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = {
        "timestamp": datetime.now().isoformat(),
        "path": str(spinehub_path),
        "checks": {},
        "overall_status": "HEALTHY",
    }
    issues_found = 0

    # 1. CODE ANALYSIS
    print("\n[1/4] CODE ANALYSIS")
    print("-" * 40)

    from .analyzers import CodeAnalyzer
    analyzer = CodeAnalyzer(str(spinehub_path))
    tools = analyzer.check_tools()

    for tool_name, available in tools.items():
        if available:
            print(f"  Running {tool_name}...", end=" ")
            try:
                result = analyzer.run_single(tool_name)
                error_count = len([i for i in result.issues if i.severity.name == "ERROR"])
                warning_count = len([i for i in result.issues if i.severity.name == "WARNING"])
                security_count = len([i for i in result.issues if i.severity.name == "SECURITY"])

                if security_count > 0:
                    print(f"SECURITY ISSUES: {security_count}")
                    issues_found += security_count
                elif error_count > 0:
                    print(f"ERRORS: {error_count}")
                    issues_found += error_count
                elif warning_count > 0:
                    print(f"WARNINGS: {warning_count}")
                else:
                    print("OK")

                results["checks"][tool_name] = {
                    "errors": error_count,
                    "warnings": warning_count,
                    "security": security_count,
                }
            except Exception as e:
                print(f"FAILED: {e}")
                results["checks"][tool_name] = {"error": str(e)}
        else:
            print(f"  {tool_name}: NOT INSTALLED (skipped)")

    # 2. KNOWLEDGE GRAPH STATUS
    print("\n[2/4] KNOWLEDGE GRAPH STATUS")
    print("-" * 40)

    data_path = spinehub_path / "data" / "spinehub.json"
    if data_path.exists():
        try:
            from .spinehub import SpineHub
            hub = SpineHub(str(data_path))
            stats = hub.get_stats()
            print(f"  Entities:  {stats['entities']}")
            print(f"  Relations: {stats['relations']}")
            print(f"  Artifacts: {stats['artifacts']}")
            print(f"  Patterns:  {stats['patterns']}")
            print(f"  Last Updated: {stats['metadata'].get('last_updated', 'N/A')}")
            results["checks"]["knowledge_graph"] = stats
        except Exception as e:
            print(f"  ERROR: {e}")
            results["checks"]["knowledge_graph"] = {"error": str(e)}
            issues_found += 1
    else:
        print("  No data file found (data/spinehub.json)")
        results["checks"]["knowledge_graph"] = {"status": "no_data"}

    # 3. SESSIONS CHECK
    print("\n[3/4] SESSIONS STATUS")
    print("-" * 40)

    sessions_path = spinehub_path / "sessions"
    if sessions_path.exists():
        session_files = list(sessions_path.glob("*.md"))
        recent_sessions = []
        week_ago = datetime.now() - timedelta(days=7)

        for sf in session_files:
            try:
                # Parse date from filename (YYYY-MM-DD format)
                date_str = sf.stem[:10]
                session_date = datetime.strptime(date_str, "%Y-%m-%d")
                if session_date >= week_ago:
                    recent_sessions.append(sf.name)
            except ValueError:
                pass

        print(f"  Total sessions: {len(session_files)}")
        print(f"  Last 7 days:    {len(recent_sessions)}")
        if recent_sessions:
            print(f"  Most recent:    {sorted(recent_sessions)[-1]}")
        results["checks"]["sessions"] = {
            "total": len(session_files),
            "recent": len(recent_sessions),
        }
    else:
        print("  No sessions directory found")
        results["checks"]["sessions"] = {"status": "no_sessions_dir"}

    # 4. GIT STATUS
    print("\n[4/4] GIT STATUS")
    print("-" * 40)

    try:
        # Check if git repo
        git_check = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=spinehub_path,
            capture_output=True,
            text=True,
        )
        if git_check.returncode == 0:
            # Get branch
            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=spinehub_path,
                capture_output=True,
                text=True,
            ).stdout.strip()
            print(f"  Branch: {branch}")

            # Check for uncommitted changes
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=spinehub_path,
                capture_output=True,
                text=True,
            ).stdout.strip()

            if status:
                changes = len(status.split("\n"))
                print(f"  Uncommitted changes: {changes} files")
            else:
                print("  Working tree: CLEAN")

            # Get last commit
            last_commit = subprocess.run(
                ["git", "log", "-1", "--format=%h %s (%cr)"],
                cwd=spinehub_path,
                capture_output=True,
                text=True,
            ).stdout.strip()
            print(f"  Last commit: {last_commit}")

            # Get latest tag
            latest_tag = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=spinehub_path,
                capture_output=True,
                text=True,
            )
            if latest_tag.returncode == 0:
                print(f"  Latest tag: {latest_tag.stdout.strip()}")
            else:
                print("  Latest tag: none")

            results["checks"]["git"] = {
                "branch": branch,
                "clean": not bool(status),
                "uncommitted": len(status.split("\n")) if status else 0,
            }
        else:
            print("  Not a git repository")
            results["checks"]["git"] = {"status": "not_a_repo"}
    except FileNotFoundError:
        print("  Git not installed")
        results["checks"]["git"] = {"status": "git_not_found"}

    # SUMMARY
    print("\n" + "=" * 60)
    print("                    SUMMARY")
    print("=" * 60)

    if issues_found > 0:
        results["overall_status"] = "ISSUES_FOUND"
        print(f"  Status: ISSUES FOUND ({issues_found} issues)")
    else:
        print("  Status: HEALTHY")

    print("=" * 60)

    # Save report if requested
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nReport saved to: {output_path}")

    return 0 if issues_found == 0 else 1


def cmd_release(args):
    """Create a GitHub release."""
    import subprocess
    import re

    spinehub_path = Path(__file__).parent.parent

    print("=" * 60)
    print("          SPINEHUB RELEASE")
    print("=" * 60)

    # Check if gh CLI is available
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Error: GitHub CLI (gh) not installed or not authenticated")
        print("Install: https://cli.github.com/")
        return 1

    # Get current version from latest tag or default
    latest_tag = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        cwd=spinehub_path,
        capture_output=True,
        text=True,
    )

    if latest_tag.returncode == 0:
        current_version = latest_tag.stdout.strip()
        print(f"Current version: {current_version}")
    else:
        current_version = "v0.0.0"
        print("No previous tags found")

    # Determine new version
    if args.version:
        new_version = args.version
        if not new_version.startswith("v"):
            new_version = f"v{new_version}"
    else:
        # Auto-increment patch version
        match = re.match(r"v(\d+)\.(\d+)\.(\d+)", current_version)
        if match:
            major, minor, patch = map(int, match.groups())
            if args.major:
                new_version = f"v{major + 1}.0.0"
            elif args.minor:
                new_version = f"v{major}.{minor + 1}.0"
            else:
                new_version = f"v{major}.{minor}.{patch + 1}"
        else:
            new_version = "v1.0.0"

    print(f"New version: {new_version}")

    # Check for uncommitted changes
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=spinehub_path,
        capture_output=True,
        text=True,
    ).stdout.strip()

    if status and not args.force:
        print("\nError: Uncommitted changes detected")
        print("Commit your changes first or use --force")
        return 1

    # Generate release notes
    print("\nGenerating release notes...")

    # Get commits since last tag
    if current_version != "v0.0.0":
        commits = subprocess.run(
            ["git", "log", f"{current_version}..HEAD", "--oneline"],
            cwd=spinehub_path,
            capture_output=True,
            text=True,
        ).stdout.strip()
    else:
        commits = subprocess.run(
            ["git", "log", "--oneline", "-20"],
            cwd=spinehub_path,
            capture_output=True,
            text=True,
        ).stdout.strip()

    release_notes = f"""## SpineHUB {new_version}

### Release Date
{datetime.now().strftime('%Y-%m-%d')}

### Changes
"""
    if commits:
        for line in commits.split("\n")[:20]:
            if line.strip():
                release_notes += f"- {line}\n"
    else:
        release_notes += "- Initial release\n"

    release_notes += """
### Installation
```bash
git clone https://github.com/your-org/SpineHUB.git
cd SpineHUB
pip install -r requirements.txt
```

### Health Check
```bash
python -m src.cli health
```
"""

    if args.dry_run:
        print("\n[DRY RUN] Would create release:")
        print(f"  Tag: {new_version}")
        print(f"  Title: SpineHUB {new_version}")
        print("\nRelease notes:")
        print("-" * 40)
        print(release_notes)
        return 0

    # Create tag
    print(f"\nCreating tag {new_version}...")
    subprocess.run(
        ["git", "tag", "-a", new_version, "-m", f"Release {new_version}"],
        cwd=spinehub_path,
        check=True,
    )

    # Push tag
    print("Pushing tag to remote...")
    subprocess.run(
        ["git", "push", "origin", new_version],
        cwd=spinehub_path,
        check=True,
    )

    # Create GitHub release
    print("Creating GitHub release...")
    result = subprocess.run(
        [
            "gh", "release", "create", new_version,
            "--title", f"SpineHUB {new_version}",
            "--notes", release_notes,
        ],
        cwd=spinehub_path,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("\nRelease created successfully!")
        print(f"URL: {result.stdout.strip()}")
        return 0
    else:
        print(f"\nError creating release: {result.stderr}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="SpineHUB - Knowledge Graph System with Code Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Run code analysis")
    analyze_parser.add_argument(
        "--path", "-p", help="Project path (default: current directory)"
    )
    analyze_parser.add_argument(
        "--tool", "-t", choices=["ruff", "bandit", "vulture", "radon"],
        help="Run specific tool only"
    )

    # stats command
    stats_parser = subparsers.add_parser("stats", help="Show SpineHUB statistics")
    stats_parser.add_argument(
        "--path", "-p", help="Path to spinehub.json"
    )

    # validate command
    validate_parser = subparsers.add_parser("validate", help="Validate worklog quality")
    validate_parser.add_argument("file", help="Worklog file to validate")

    # collect command
    collect_parser = subparsers.add_parser("collect", help="Run data collectors")
    collect_parser.add_argument(
        "--source", "-s",
        choices=["claude", "slack", "local", "linear", "drive"],
        help="Run specific collector (default: all)"
    )
    collect_parser.add_argument(
        "--days", "-d", type=int, default=7,
        help="Number of days to collect (default: 7)"
    )

    # linear command
    linear_parser = subparsers.add_parser("linear", help="Linear automation")
    linear_parser.add_argument(
        "action",
        choices=["templates", "generate"],
        help="Action: templates (list), generate (create tickets)"
    )
    linear_parser.add_argument(
        "--template", "-t",
        help="Template ID for generate action"
    )
    linear_parser.add_argument(
        "--matrix", "-m",
        help="Path to project matrix JSON file"
    )
    linear_parser.add_argument(
        "--team",
        help="Linear team key (default: RAC)"
    )
    linear_parser.add_argument(
        "--execute", "-x", action="store_true",
        help="Execute for real (default: dry-run)"
    )

    # channels command
    channels_parser = subparsers.add_parser("channels", help="Map Slack channels")
    channels_parser.add_argument(
        "--prefix", "-p",
        help="Channel prefixes (comma-separated, default: ext-,external-)"
    )
    channels_parser.add_argument(
        "--map", action="store_true",
        help="Full mapping with member classification"
    )
    channels_parser.add_argument(
        "--output", "-o",
        help="Output JSON file for mappings"
    )

    # health command
    health_parser = subparsers.add_parser("health", help="Run health check on SpineHUB")
    health_parser.add_argument(
        "--output", "-o",
        help="Save report to JSON file"
    )

    # release command
    release_parser = subparsers.add_parser("release", help="Create GitHub release")
    release_parser.add_argument(
        "--version", "-v",
        help="Version number (e.g., 1.0.0 or v1.0.0)"
    )
    release_parser.add_argument(
        "--major", action="store_true",
        help="Increment major version"
    )
    release_parser.add_argument(
        "--minor", action="store_true",
        help="Increment minor version"
    )
    release_parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview release without creating"
    )
    release_parser.add_argument(
        "--force", action="store_true",
        help="Create release even with uncommitted changes"
    )

    args = parser.parse_args()

    if args.command == "analyze":
        return cmd_analyze(args)
    elif args.command == "stats":
        return cmd_stats(args)
    elif args.command == "validate":
        return cmd_validate(args)
    elif args.command == "collect":
        return cmd_collect(args)
    elif args.command == "linear":
        return cmd_linear(args)
    elif args.command == "channels":
        return cmd_channels(args)
    elif args.command == "health":
        return cmd_health(args)
    elif args.command == "release":
        return cmd_release(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
