"""
Local File Collector

Scans local directories for files modified within the date range.
Ported from TSA_CORTEX TypeScript implementation.

Features:
- Recursive directory scanning
- SHA256 hashing for deduplication
- Configurable denylist patterns
- Size filtering
- File type detection
"""

import hashlib
import os
from datetime import datetime
from fnmatch import fnmatch
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


class LocalCollector(BaseCollector):
    """
    Collector for local file system changes.

    Scans configured directories for files created or modified
    within the date range.

    Features:
    - Denylist patterns (node_modules, __pycache__, etc.)
    - File size limits (default 10MB)
    - Hash-based deduplication
    - File type classification
    """

    # Default directories to scan
    DEFAULT_PATHS = [
        "~/Downloads",
        "~/Documents",
    ]

    # Patterns to exclude
    DEFAULT_DENYLIST = [
        "**/__pycache__/**",
        "**/node_modules/**",
        "**/.git/**",
        "**/.venv/**",
        "**/venv/**",
        "**/.ruff_cache/**",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.exe",
        "**/*.dll",
        "**/*.so",
        "**/*.dylib",
        "**/Thumbs.db",
        "**/.DS_Store",
        "**/desktop.ini",
        "**/*.tmp",
        "**/*.bak",
        "**/*.swp",
        "**/*.lock",
        "**/package-lock.json",
        "**/yarn.lock",
    ]

    # Maximum file size (10 MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # File type mappings
    FILE_TYPES = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".md": "markdown",
        ".txt": "text",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".csv": "csv",
        ".xlsx": "excel",
        ".xls": "excel",
        ".docx": "word",
        ".doc": "word",
        ".pdf": "pdf",
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
        ".gif": "image",
        ".svg": "image",
        ".html": "html",
        ".css": "css",
        ".sql": "sql",
        ".sh": "shell",
        ".bat": "batch",
        ".ps1": "powershell",
    }

    def __init__(
        self,
        config: dict,
        date_range: tuple[datetime, datetime],
        user_id: Optional[str] = None,
    ):
        super().__init__(config, date_range, user_id)

        # Get scan paths from config or use defaults
        self.scan_paths = config.get("LOCAL_SCAN_PATHS", self.DEFAULT_PATHS)
        if isinstance(self.scan_paths, str):
            self.scan_paths = [p.strip() for p in self.scan_paths.split(",")]

        # Expand ~ to home directory
        self.scan_paths = [
            str(Path(p).expanduser()) for p in self.scan_paths
        ]

        # Denylist patterns
        self.denylist = config.get("LOCAL_DENYLIST", self.DEFAULT_DENYLIST)

        # Max file size
        self.max_size = config.get("LOCAL_MAX_FILE_SIZE", self.MAX_FILE_SIZE)

        # Track file hashes for deduplication
        self._seen_hashes = set()

    @property
    def source(self) -> str:
        return SourceSystem.LOCAL.value

    def is_configured(self) -> bool:
        """Check if at least one scan path exists."""
        return any(Path(p).exists() for p in self.scan_paths)

    async def collect(self) -> CollectorResult:
        """Scan local directories for modified files."""
        result = self.create_empty_result()

        if not self.is_configured():
            result.warnings.append("No configured scan paths exist")
            return result

        events = []
        files_scanned = 0
        files_filtered = 0

        for scan_path in self.scan_paths:
            path = Path(scan_path)
            if not path.exists():
                self.log_warn(f"Scan path not found: {scan_path}")
                continue

            self.log_info(f"Scanning {scan_path}...")

            try:
                for file_path in path.rglob("*"):
                    if not file_path.is_file():
                        continue

                    files_scanned += 1

                    # Check denylist
                    if self._is_denied(file_path):
                        files_filtered += 1
                        continue

                    # Check size
                    try:
                        stat = file_path.stat()
                        if stat.st_size > self.max_size:
                            files_filtered += 1
                            continue
                    except OSError:
                        continue

                    # Parse file
                    event = self._parse_file(file_path, stat)
                    if event:
                        events.append(event)

            except PermissionError:
                result.warnings.append(f"Permission denied: {scan_path}")
            except Exception as e:
                result.errors.append(f"Error scanning {scan_path}: {e}")

        result.events = events

        self.log_info(
            f"Scanned {files_scanned} files, filtered {files_filtered}, "
            f"collected {len(events)} events"
        )

        return result

    def _parse_file(self, file_path: Path, stat: os.stat_result) -> Optional[ActivityEvent]:
        """Parse a file into an ActivityEvent."""
        # Check modification time
        mtime = datetime.fromtimestamp(stat.st_mtime)
        ctime = datetime.fromtimestamp(stat.st_ctime)

        # Use the more recent of mtime and ctime
        timestamp = max(mtime, ctime)

        if not self.is_within_date_range(timestamp):
            return None

        # Determine if created or modified
        # If ctime and mtime are close, it's likely created
        is_created = abs((ctime - mtime).total_seconds()) < 60
        event_type = EventType.FILE_CREATED if is_created else EventType.FILE_MODIFIED

        # Calculate hash for deduplication
        try:
            file_hash = self._hash_file(file_path)
            if file_hash in self._seen_hashes:
                return None  # Duplicate
            self._seen_hashes.add(file_hash)
        except Exception:
            file_hash = None

        # Determine file type
        file_type = self._get_file_type(file_path)

        # Generate event ID
        event_id = self.generate_event_id(
            self.source, str(file_path), timestamp.isoformat()
        )

        # Create title
        title = f"{event_type.value.replace('_', ' ').title()}: {file_path.name}"

        # Extract project name from path
        project = self._extract_project(file_path)

        pointer = SourcePointer(
            pointer_id=self.generate_pointer_id("local_file", str(file_path)),
            type="local_file_path",
            path=str(file_path),
            display_text=f"Local file: {file_path.name}",
        )

        return ActivityEvent(
            event_id=event_id,
            source_system=SourceSystem.LOCAL,
            event_type=event_type,
            event_timestamp=timestamp,
            title=title,
            body_text=f"File: {file_path}\nSize: {self._format_size(stat.st_size)}\nType: {file_type}",
            actor_name=self.user_id or "User",
            ownership=OwnershipType.MY_WORK,
            confidence="high",
            source_pointers=[pointer],
            metadata={
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_type": file_type,
                "file_size": stat.st_size,
                "file_hash": file_hash,
                "project": project,
                "extension": file_path.suffix.lower(),
            },
        )

    def _is_denied(self, file_path: Path) -> bool:
        """Check if file matches any denylist pattern."""
        path_str = str(file_path)

        for pattern in self.denylist:
            # Handle ** patterns
            if "**" in pattern:
                # Convert to fnmatch pattern
                simple_pattern = pattern.replace("**/", "*/").replace("/**", "/*")
                if fnmatch(path_str, f"*{simple_pattern}"):
                    return True
                if fnmatch(path_str.lower(), f"*{simple_pattern.lower()}"):
                    return True
            else:
                if fnmatch(file_path.name, pattern):
                    return True
                if fnmatch(file_path.name.lower(), pattern.lower()):
                    return True

        return False

    def _hash_file(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file contents."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _get_file_type(self, file_path: Path) -> str:
        """Determine file type from extension."""
        ext = file_path.suffix.lower()
        return self.FILE_TYPES.get(ext, "other")

    def _extract_project(self, file_path: Path) -> Optional[str]:
        """Extract project name from file path."""
        # Look for common project indicators
        parts = file_path.parts

        for i, part in enumerate(parts):
            # Check if this looks like a project directory
            if part.lower() in ("projects", "repos", "workspace", "work"):
                if i + 1 < len(parts):
                    return parts[i + 1]

            # Check for typical project markers
            project_path = Path(*parts[:i + 1])
            if (project_path / ".git").exists():
                return part
            if (project_path / "package.json").exists():
                return part
            if (project_path / "pyproject.toml").exists():
                return part
            if (project_path / "CLAUDE.md").exists():
                return part

        return None

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable form."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
