"""
SpineHUB Collectors - Multi-source data collection

Collectors gather data from various sources and feed it into the SpineHUB knowledge graph.

Available collectors:
- ClaudeCollector: Reads Claude Code history and sessions
- SlackCollector: Collects messages from Slack channels
- LocalCollector: Scans local files and directories
- LinearCollector: Fetches issues from Linear
- DriveCollector: Indexes Google Drive files

Usage:
    from modules.collectors import create_collector, run_all_collectors

    # Single collector
    collector = create_collector("claude", config, date_range)
    result = await collector.collect()

    # All collectors
    results = await run_all_collectors(config, date_range)
"""

from .base import BaseCollector, CollectorResult, SourceSystem
from .claude import ClaudeCollector
from .slack import SlackCollector
from .local import LocalCollector
from .linear import LinearCollector
from .drive import DriveCollector

__all__ = [
    "BaseCollector",
    "CollectorResult",
    "SourceSystem",
    "ClaudeCollector",
    "SlackCollector",
    "LocalCollector",
    "LinearCollector",
    "DriveCollector",
    "create_collector",
    "get_all_collectors",
    "run_all_collectors",
]


def create_collector(
    source: str,
    config: dict,
    date_range: tuple,
    user_id: str = None,
) -> BaseCollector | None:
    """
    Factory function to create a collector by source type.

    Args:
        source: Source system name (claude, slack, local, linear, drive)
        config: Configuration dictionary
        date_range: Tuple of (start_date, end_date) as datetime objects
        user_id: Optional user ID for filtering

    Returns:
        Collector instance or None if source not supported
    """
    collectors = {
        "claude": ClaudeCollector,
        "slack": SlackCollector,
        "local": LocalCollector,
        "linear": LinearCollector,
        "drive": DriveCollector,
    }

    collector_class = collectors.get(source.lower())
    if collector_class:
        return collector_class(config, date_range, user_id)
    return None


def get_all_collectors(
    config: dict,
    date_range: tuple,
    user_id: str = None,
) -> list[BaseCollector]:
    """
    Get all configured and available collectors.

    Args:
        config: Configuration dictionary
        date_range: Tuple of (start_date, end_date)
        user_id: Optional user ID

    Returns:
        List of configured collector instances
    """
    sources = ["claude", "slack", "local", "linear", "drive"]  # Active collectors
    collectors = []

    for source in sources:
        collector = create_collector(source, config, date_range, user_id)
        if collector and collector.is_configured():
            collectors.append(collector)

    return collectors


async def run_all_collectors(
    config: dict,
    date_range: tuple,
    user_id: str = None,
) -> dict[str, CollectorResult]:
    """
    Run all available collectors and return results.

    Args:
        config: Configuration dictionary
        date_range: Tuple of (start_date, end_date)
        user_id: Optional user ID

    Returns:
        Dictionary mapping source name to CollectorResult
    """
    results = {}
    collectors = get_all_collectors(config, date_range, user_id)

    print(f"Running {len(collectors)} collector(s)...")

    for collector in collectors:
        print(f"\nCollecting from {collector.source}...")
        try:
            result = await collector.collect()
            results[collector.source] = result

            if result.errors:
                print(f"  Errors: {', '.join(result.errors)}")
            if result.warnings:
                print(f"  Warnings: {', '.join(result.warnings)}")
            print(f"  Collected {result.record_count} events")
        except Exception as e:
            print(f"  FAILED: {e}")
            results[collector.source] = CollectorResult(
                source=collector.source,
                events=[],
                errors=[str(e)],
            )

    return results
