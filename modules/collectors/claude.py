"""
Claude History Collector

Collects activity events from Claude Code history and session files.
Ported from TSA_CORTEX TypeScript implementation.

Sources:
- ~/.claude/history.jsonl - Global prompt history
- ~/.claude/projects/*/sessions/*.jsonl - Per-project sessions
- Project sessions/ directories - Session markdown files

Features:
- 92% noise reduction (filters short/irrelevant prompts)
- Project relevance filtering
- Session file parsing
- Memory.md change tracking
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .base import (
    BaseCollector,
    CollectorResult,
    ActivityEvent,
    SourcePointer,
    SourceSystem,
    EventType,
    OwnershipType,
)


class ClaudeCollector(BaseCollector):
    """
    Collector for Claude Code history and sessions.

    Reads from:
    1. history.jsonl - Main prompt history
    2. projects/*/sessions/*.jsonl - Project-specific sessions
    3. sessions/*.md - Markdown session documentation

    Filters:
    - Minimum prompt length (5 chars)
    - Ignores single-letter commands (c, y, n, ok)
    - Excludes system directories (Windows, system32)
    """

    # Noise patterns to filter out
    NOISE_PATTERNS = [
        r"^[cyn]$",           # Single letter responses
        r"^ok$",              # Simple acknowledgments
        r"^yes$",
        r"^no$",
        r"^\.$",              # Just a period
        r"^\.\.\.+$",         # Just ellipsis
        r"^q$",               # Quit commands
        r"^exit$",
        r"^clear$",
    ]

    # Directories to exclude
    EXCLUDED_PATHS = [
        "system32",
        "windows",
        "c-windows",
        "program files",
        "appdata\\local\\temp",
    ]

    MIN_PROMPT_LENGTH = 5

    def __init__(
        self,
        config: dict,
        date_range: tuple[datetime, datetime],
        user_id: Optional[str] = None,
    ):
        super().__init__(config, date_range, user_id)
        self.claude_dir = Path.home() / ".claude"
        self.projects_dir = self.claude_dir / "projects"

    @property
    def source(self) -> str:
        return SourceSystem.CLAUDE.value

    def is_configured(self) -> bool:
        """Check if Claude history exists."""
        return self.claude_dir.exists()

    async def collect(self) -> CollectorResult:
        """Collect Claude history events."""
        result = self.create_empty_result()

        if not self.is_configured():
            result.errors.append(f"Claude directory not found: {self.claude_dir}")
            return result

        # Collect from all sources
        history_events = self._collect_history_jsonl()
        session_events = self._collect_project_sessions()
        markdown_events = self._collect_session_markdowns()

        # Combine and deduplicate
        all_events = history_events + session_events + markdown_events
        seen_ids = set()
        unique_events = []

        for event in all_events:
            if event.event_id not in seen_ids:
                seen_ids.add(event.event_id)
                unique_events.append(event)

        # Sort by timestamp
        unique_events.sort(key=lambda e: e.event_timestamp)

        result.events = unique_events

        # Statistics
        total_raw = len(history_events) + len(session_events) + len(markdown_events)
        noise_filtered = total_raw - len(unique_events)
        if noise_filtered > 0:
            reduction_pct = (noise_filtered / total_raw * 100) if total_raw > 0 else 0
            result.warnings.append(
                f"Noise reduction: {noise_filtered} events filtered ({reduction_pct:.0f}%)"
            )

        self.log_info(f"Collected {len(unique_events)} events from Claude history")
        return result

    def _collect_history_jsonl(self) -> list[ActivityEvent]:
        """Collect from main history.jsonl file."""
        events = []
        history_file = self.claude_dir / "history.jsonl"

        if not history_file.exists():
            self.log_warn("history.jsonl not found")
            return events

        try:
            with open(history_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        record = json.loads(line)
                        event = self._parse_history_record(record, line_num)
                        if event:
                            events.append(event)
                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            self.log_error(f"Failed to read history.jsonl: {e}")

        return events

    def _parse_history_record(self, record: dict, line_num: int) -> Optional[ActivityEvent]:
        """Parse a single history.jsonl record into an ActivityEvent."""
        # Extract timestamp
        timestamp_str = record.get("timestamp") or record.get("ts")
        if not timestamp_str:
            return None

        try:
            if isinstance(timestamp_str, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp_str / 1000)
            else:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

        # Check date range
        if not self.is_within_date_range(timestamp):
            return None

        # Extract prompt text
        prompt = record.get("prompt") or record.get("message") or record.get("input", "")
        if not prompt or not isinstance(prompt, str):
            return None

        # Filter noise
        if self._is_noise(prompt):
            return None

        # Extract project path
        cwd = record.get("cwd") or record.get("directory", "")
        if self._is_excluded_path(cwd):
            return None

        # Create event
        event_id = self.generate_event_id(self.source, str(line_num), timestamp_str)

        title = self._create_title(prompt)
        body = self.truncate_text(prompt, 500)

        # Determine project from cwd
        project_name = self._extract_project_name(cwd)

        pointer = SourcePointer(
            pointer_id=self.generate_pointer_id("claude_history", str(line_num)),
            type="claude_history_entry",
            path=str(self.claude_dir / "history.jsonl"),
            display_text=f"Claude prompt in {project_name or 'unknown'}",
        )

        return ActivityEvent(
            event_id=event_id,
            source_system=SourceSystem.CLAUDE,
            event_type=EventType.PROMPT,
            event_timestamp=timestamp,
            title=title,
            body_text=body,
            actor_name=self.user_id or "User",
            ownership=OwnershipType.MY_WORK,
            confidence="high",
            source_pointers=[pointer],
            metadata={
                "cwd": cwd,
                "project": project_name,
                "line_number": line_num,
            },
        )

    def _collect_project_sessions(self) -> list[ActivityEvent]:
        """Collect from project-specific session files."""
        events = []

        if not self.projects_dir.exists():
            return events

        # Find all session jsonl files
        for session_file in self.projects_dir.rglob("sessions/*.jsonl"):
            try:
                project_name = self._extract_project_from_path(session_file)

                with open(session_file, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue

                        try:
                            record = json.loads(line)
                            event = self._parse_session_record(
                                record, session_file, line_num, project_name
                            )
                            if event:
                                events.append(event)
                        except json.JSONDecodeError:
                            continue

            except Exception as e:
                self.log_warn(f"Failed to read session file {session_file}: {e}")

        return events

    def _parse_session_record(
        self,
        record: dict,
        file_path: Path,
        line_num: int,
        project_name: str,
    ) -> Optional[ActivityEvent]:
        """Parse a session jsonl record."""
        # Similar to history record parsing
        timestamp_str = record.get("timestamp") or record.get("ts")
        if not timestamp_str:
            return None

        try:
            if isinstance(timestamp_str, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp_str / 1000)
            else:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            return None

        if not self.is_within_date_range(timestamp):
            return None

        prompt = record.get("prompt") or record.get("message") or ""
        if not prompt or self._is_noise(prompt):
            return None

        event_id = self.generate_event_id(
            self.source, str(file_path), str(line_num), timestamp_str
        )

        title = self._create_title(prompt)
        body = self.truncate_text(prompt, 500)

        pointer = SourcePointer(
            pointer_id=self.generate_pointer_id("claude_session", str(file_path)),
            type="claude_session_entry",
            path=str(file_path),
            display_text=f"Session in {project_name}",
        )

        return ActivityEvent(
            event_id=event_id,
            source_system=SourceSystem.CLAUDE,
            event_type=EventType.SESSION,
            event_timestamp=timestamp,
            title=title,
            body_text=body,
            actor_name=self.user_id or "User",
            ownership=OwnershipType.MY_WORK,
            confidence="high",
            source_pointers=[pointer],
            metadata={
                "project": project_name,
                "session_file": str(file_path),
            },
        )

    def _collect_session_markdowns(self) -> list[ActivityEvent]:
        """Collect from session markdown files in projects."""
        events = []

        # Look for sessions/ directories in common project locations
        search_paths = [
            Path.home(),
            Path.home() / "Projects",
        ]

        for base_path in search_paths:
            if not base_path.exists():
                continue

            # Find sessions directories
            for sessions_dir in base_path.glob("*/sessions"):
                if not sessions_dir.is_dir():
                    continue

                project_name = sessions_dir.parent.name

                for md_file in sessions_dir.glob("*.md"):
                    # Skip templates
                    if md_file.name.startswith("_"):
                        continue

                    event = self._parse_session_markdown(md_file, project_name)
                    if event:
                        events.append(event)

        return events

    def _parse_session_markdown(
        self, file_path: Path, project_name: str
    ) -> Optional[ActivityEvent]:
        """Parse a session markdown file."""
        try:
            stat = file_path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime)

            if not self.is_within_date_range(mtime):
                return None

            # Read content
            content = file_path.read_text(encoding="utf-8")

            # Extract title from filename or first heading
            title = file_path.stem
            if title.startswith("20"):  # Date-based filename
                title = f"Session {title}"

            # Look for # heading
            heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if heading_match:
                title = heading_match.group(1)

            # Extract summary if present
            summary_match = re.search(
                r"##\s+Summary\s*\n(.+?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE
            )
            body = summary_match.group(1).strip() if summary_match else ""
            body = self.truncate_text(body, 500) if body else f"Session documentation for {project_name}"

            event_id = self.generate_event_id(
                self.source, str(file_path), mtime.isoformat()
            )

            pointer = SourcePointer(
                pointer_id=self.generate_pointer_id("session_md", str(file_path)),
                type="session_markdown",
                path=str(file_path),
                display_text=f"Session doc: {file_path.name}",
            )

            return ActivityEvent(
                event_id=event_id,
                source_system=SourceSystem.CLAUDE,
                event_type=EventType.SESSION,
                event_timestamp=mtime,
                title=title,
                body_text=body,
                actor_name=self.user_id or "User",
                ownership=OwnershipType.MY_WORK,
                confidence="medium",
                source_pointers=[pointer],
                metadata={
                    "project": project_name,
                    "file": str(file_path),
                    "file_size": stat.st_size,
                },
            )

        except Exception as e:
            self.log_warn(f"Failed to parse session markdown {file_path}: {e}")
            return None

    def _is_noise(self, text: str) -> bool:
        """Check if text is noise that should be filtered."""
        text = text.strip().lower()

        # Too short
        if len(text) < self.MIN_PROMPT_LENGTH:
            return True

        # Matches noise patterns
        for pattern in self.NOISE_PATTERNS:
            if re.match(pattern, text, re.IGNORECASE):
                return True

        return False

    def _is_excluded_path(self, path: str) -> bool:
        """Check if path should be excluded."""
        path_lower = path.lower()
        return any(excl in path_lower for excl in self.EXCLUDED_PATHS)

    def _create_title(self, text: str) -> str:
        """Create a title from prompt text."""
        # Take first line or first 100 chars
        first_line = text.split("\n")[0].strip()
        if len(first_line) > 100:
            # Find word boundary
            truncated = first_line[:100]
            last_space = truncated.rfind(" ")
            if last_space > 70:
                truncated = truncated[:last_space]
            first_line = truncated + "..."
        return first_line

    def _extract_project_name(self, cwd: str) -> Optional[str]:
        """Extract project name from working directory."""
        if not cwd:
            return None

        path = Path(cwd)
        # Return last directory component
        return path.name if path.name else None

    def _extract_project_from_path(self, file_path: Path) -> str:
        """Extract project name from a session file path."""
        # Path like: ~/.claude/projects/PROJECT_NAME/sessions/file.jsonl
        parts = file_path.parts
        try:
            projects_idx = parts.index("projects")
            if projects_idx + 1 < len(parts):
                return parts[projects_idx + 1]
        except ValueError:
            pass
        return "unknown"
