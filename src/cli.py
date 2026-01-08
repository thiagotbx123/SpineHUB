#!/usr/bin/env python3
"""
SpineHUB CLI

Command-line interface for SpineHUB operations.

Usage:
    python -m src.cli analyze [--path PATH] [--tool TOOL]
    python -m src.cli stats [--path PATH]
    python -m src.cli validate <file>
"""

import argparse
import sys
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

    args = parser.parse_args()

    if args.command == "analyze":
        return cmd_analyze(args)
    elif args.command == "stats":
        return cmd_stats(args)
    elif args.command == "validate":
        return cmd_validate(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
