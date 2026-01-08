"""
SpineHUB Collector Base Classes

Defines the base interfaces and data structures for all collectors.
Ported from TSA_CORTEX TypeScript implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import hashlib


class SourceSystem(str, Enum):
    """Supported source systems for data collection."""
    CLAUDE = "claude"
    SLACK = "slack"
    LINEAR = "linear"
    DRIVE = "drive"
    LOCAL = "local"


class EventType(str, Enum):
    """Types of activity events."""
    MESSAGE = "message"
    FILE_CREATED = "file_created"
    FILE_MODIFIED = "file_modified"
    ISSUE_CREATED = "issue_created"
    ISSUE_UPDATED = "issue_updated"
    COMMENT = "comment"
    PROMPT = "prompt"
    SESSION = "session"
    MENTION = "mention"


class OwnershipType(str, Enum):
    """Classification of event ownership."""
    MY_WORK = "my_work"          # Created/authored by user
    MENTIONED = "mentioned"       # User was mentioned
    CONTEXT = "context"           # Relevant context (not owned)
    KEYWORD_MATCH = "keyword"     # Matched search keywords


@dataclass
class SourcePointer:
    """
    Reference to the original source of an event.

    Enables full traceability back to source data.
    """
    pointer_id: str
    type: str                     # "slack_permalink", "drive_url", "file_path", etc.
    url: Optional[str] = None     # Web URL if available
    path: Optional[str] = None    # Local path if file
    display_text: str = ""        # Human-readable description

    def to_dict(self) -> dict:
        return {
            "pointer_id": self.pointer_id,
            "type": self.type,
            "url": self.url,
            "path": self.path,
            "display_text": self.display_text,
        }


@dataclass
class ActivityEvent:
    """
    Normalized activity event from any source.

    All collectors produce ActivityEvent objects for unified processing.
    """
    event_id: str                           # Deterministic hash
    source_system: SourceSystem
    event_type: EventType
    event_timestamp: datetime
    title: str
    body_text: str = ""
    actor_name: Optional[str] = None        # Who performed the action
    ownership: OwnershipType = OwnershipType.CONTEXT
    confidence: str = "medium"              # high, medium, low
    source_pointers: list[SourcePointer] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    pii_redacted: bool = False

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "source_system": self.source_system.value,
            "event_type": self.event_type.value,
            "event_timestamp": self.event_timestamp.isoformat(),
            "title": self.title,
            "body_text": self.body_text,
            "actor_name": self.actor_name,
            "ownership": self.ownership.value,
            "confidence": self.confidence,
            "source_pointers": [p.to_dict() for p in self.source_pointers],
            "metadata": self.metadata,
            "pii_redacted": self.pii_redacted,
        }


@dataclass
class CollectorResult:
    """
    Result from running a collector.

    Contains all collected events plus metadata about the collection run.
    """
    source: str
    events: list[ActivityEvent] = field(default_factory=list)
    raw_data: list[Any] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def record_count(self) -> int:
        return len(self.events)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "record_count": self.record_count,
            "success": self.success,
            "events": [e.to_dict() for e in self.events],
            "errors": self.errors,
            "warnings": self.warnings,
        }


class BaseCollector(ABC):
    """
    Abstract base class for all data collectors.

    Subclasses must implement:
    - source: Property returning the SourceSystem
    - is_configured(): Check if collector has required credentials
    - collect(): Async method to perform collection
    """

    def __init__(
        self,
        config: dict,
        date_range: tuple[datetime, datetime],
        user_id: Optional[str] = None,
    ):
        """
        Initialize collector.

        Args:
            config: Configuration dictionary (credentials, settings)
            date_range: Tuple of (start_date, end_date)
            user_id: Optional user ID for filtering
        """
        self.config = config
        self.start_date, self.end_date = date_range
        self.user_id = user_id

    @property
    @abstractmethod
    def source(self) -> str:
        """Return the source system identifier."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if collector has required configuration."""
        pass

    @abstractmethod
    async def collect(self) -> CollectorResult:
        """
        Perform data collection.

        Returns:
            CollectorResult with collected events
        """
        pass

    def create_empty_result(self) -> CollectorResult:
        """Create an empty result for this collector."""
        return CollectorResult(source=self.source)

    def generate_event_id(self, *parts: str) -> str:
        """
        Generate a deterministic event ID from parts.

        Using deterministic IDs allows safe re-runs without duplicates.
        """
        raw = ":".join(str(p) for p in parts)
        return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:16]

    def generate_pointer_id(self, type_: str, url_or_path: str) -> str:
        """Generate a deterministic pointer ID."""
        raw = f"{type_}:{url_or_path}"
        return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:12]

    def is_within_date_range(self, timestamp: datetime) -> bool:
        """Check if timestamp is within the configured date range."""
        return self.start_date <= timestamp <= self.end_date

    def log_info(self, message: str) -> None:
        """Log an info message."""
        print(f"[{self.source.upper()}] {message}")

    def log_warn(self, message: str) -> None:
        """Log a warning message."""
        print(f"[{self.source.upper()}] WARNING: {message}")

    def log_error(self, message: str) -> None:
        """Log an error message."""
        print(f"[{self.source.upper()}] ERROR: {message}")

    def truncate_text(self, text: str, max_length: int = 500) -> str:
        """Truncate text to max length, preserving word boundaries."""
        if len(text) <= max_length:
            return text
        truncated = text[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > max_length * 0.8:
            truncated = truncated[:last_space]
        return truncated + "..."
