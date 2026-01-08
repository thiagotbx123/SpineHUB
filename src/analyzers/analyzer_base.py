"""
Base classes for code analyzers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Severity(str, Enum):
    """Issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SECURITY = "security"


@dataclass
class Issue:
    """A single issue found by an analyzer."""
    file: str
    line: int
    column: int
    code: str
    message: str
    severity: Severity
    tool: str
    fix_available: bool = False
    fix_description: Optional[str] = None


@dataclass
class AnalyzerResult:
    """Result from running an analyzer."""
    tool: str
    success: bool
    issues: list[Issue] = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    raw_output: str = ""
    error: Optional[str] = None

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def has_security_issues(self) -> bool:
        return any(i.severity == Severity.SECURITY for i in self.issues)

    def format_summary(self) -> str:
        """Format a summary of the results."""
        lines = [
            f"Tool: {self.tool}",
            f"Status: {'SUCCESS' if self.success else 'FAILED'}",
            f"Issues Found: {self.issue_count}",
        ]

        if self.issues:
            by_severity = {}
            for issue in self.issues:
                sev = issue.severity.value
                by_severity[sev] = by_severity.get(sev, 0) + 1

            lines.append("By Severity:")
            for sev, count in sorted(by_severity.items()):
                lines.append(f"  {sev}: {count}")

        return "\n".join(lines)


class AnalyzerBase(ABC):
    """Base class for code analyzers."""

    name: str = "base"
    description: str = "Base analyzer"

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the tool is installed and available."""
        pass

    @abstractmethod
    def run(self, paths: Optional[list[str]] = None) -> AnalyzerResult:
        """Run the analyzer on the project or specific paths."""
        pass

    @abstractmethod
    def parse_output(self, output: str) -> list[Issue]:
        """Parse the tool's output into Issue objects."""
        pass

    def get_python_files(self, paths: Optional[list[str]] = None) -> list[Path]:
        """Get all Python files in the project or specified paths."""
        if paths:
            return [Path(p) for p in paths if p.endswith(".py")]

        return list(self.project_path.rglob("*.py"))
