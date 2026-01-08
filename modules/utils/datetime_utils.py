"""
DateTime Utilities with Timezone Support

Ported from TSA_CORTEX TypeScript implementation.
Provides timezone-aware date handling for all SpineHUB collectors.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Union

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo


@dataclass
class DateRange:
    """Date range with timezone information."""
    start: datetime
    end: datetime
    timezone: str


def get_default_date_range(timezone: str = "America/Sao_Paulo", days: int = 7) -> DateRange:
    """
    Get default date range (last N days).

    Args:
        timezone: IANA timezone string
        days: Number of days to look back

    Returns:
        DateRange with start, end, and timezone
    """
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    start = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)

    return DateRange(start=start, end=end, timezone=timezone)


def parse_date_range(
    start_str: Optional[str] = None,
    end_str: Optional[str] = None,
    timezone: str = "America/Sao_Paulo",
    default_days: int = 7
) -> DateRange:
    """
    Parse date range from strings.

    Args:
        start_str: Start date (YYYY-MM-DD format) or None for default
        end_str: End date (YYYY-MM-DD format) or None for today
        timezone: IANA timezone string
        default_days: Days to look back if start not specified

    Returns:
        DateRange with parsed dates
    """
    tz = ZoneInfo(timezone)
    now = datetime.now(tz)

    if end_str:
        end = datetime.strptime(end_str, "%Y-%m-%d").replace(tzinfo=tz)
        end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    if start_str:
        start = datetime.strptime(start_str, "%Y-%m-%d").replace(tzinfo=tz)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start = (end - timedelta(days=default_days)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    return DateRange(start=start, end=end, timezone=timezone)


def is_within_date_range(date_input: Union[str, datetime], range: DateRange) -> bool:
    """
    Check if a date is within a date range.

    Args:
        date_input: ISO date string or datetime object
        range: DateRange to check against

    Returns:
        True if date is within range
    """
    if isinstance(date_input, str):
        # Parse ISO format
        date = datetime.fromisoformat(date_input.replace("Z", "+00:00"))
    else:
        date = date_input

    # Ensure timezone aware
    if date.tzinfo is None:
        tz = ZoneInfo(range.timezone)
        date = date.replace(tzinfo=tz)

    return range.start <= date <= range.end


def format_local_time(date: Union[str, datetime], timezone: str = "America/Sao_Paulo") -> str:
    """
    Format date to local time with timezone offset.

    Args:
        date: Date to format
        timezone: Target timezone

    Returns:
        ISO format string with timezone offset
    """
    if isinstance(date, str):
        dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
    else:
        dt = date

    tz = ZoneInfo(timezone)
    local = dt.astimezone(tz)
    return local.isoformat()


def format_utc(date: Union[str, datetime]) -> str:
    """
    Format date as UTC ISO string.

    Args:
        date: Date to format

    Returns:
        UTC ISO format string
    """
    if isinstance(date, str):
        dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
    else:
        dt = date

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z")


def format_display(date: Union[str, datetime], timezone: str = "America/Sao_Paulo") -> str:
    """
    Format date for display (YYYY-MM-DD HH:MM).

    Args:
        date: Date to format
        timezone: Target timezone

    Returns:
        Human-readable date string
    """
    if isinstance(date, str):
        dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
    else:
        dt = date

    tz = ZoneInfo(timezone)
    local = dt.astimezone(tz)
    return local.strftime("%Y-%m-%d %H:%M")


def to_unix_timestamp(date: datetime) -> int:
    """Convert datetime to Unix timestamp (seconds)."""
    return int(date.timestamp())


def from_unix_timestamp(ts: int) -> datetime:
    """Convert Unix timestamp to datetime (UTC)."""
    return datetime.fromtimestamp(ts, tz=ZoneInfo("UTC"))


def slack_ts_to_date(ts: str) -> datetime:
    """
    Convert Slack timestamp to datetime.

    Slack timestamps are Unix timestamps with microseconds (e.g., "1234567890.123456")

    Args:
        ts: Slack timestamp string

    Returns:
        datetime object (UTC)
    """
    unix_ts = float(ts)
    return datetime.fromtimestamp(unix_ts, tz=ZoneInfo("UTC"))


def date_to_slack_ts(date: datetime) -> str:
    """
    Convert datetime to Slack timestamp format.

    Args:
        date: datetime to convert

    Returns:
        Slack timestamp string with 6 decimal places
    """
    return f"{date.timestamp():.6f}"


def now_brasil() -> datetime:
    """Get current time in Brazil timezone."""
    return datetime.now(ZoneInfo("America/Sao_Paulo"))


def utc_to_brasil(utc_dt: Union[str, datetime]) -> datetime:
    """Convert UTC datetime to Brazil timezone."""
    if isinstance(utc_dt, str):
        dt = datetime.fromisoformat(utc_dt.replace("Z", "+00:00"))
    else:
        dt = utc_dt

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.astimezone(ZoneInfo("America/Sao_Paulo"))
