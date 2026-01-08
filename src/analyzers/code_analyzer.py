"""
Unified Code Analyzer

Orchestrates multiple code analysis tools and provides
a unified interface for code quality checking.
"""

import json
import subprocess
import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from .analyzer_base import AnalyzerBase, AnalyzerResult, Issue, Severity


class RuffAnalyzer(AnalyzerBase):
    """
    Ruff - Fast Python linter and formatter.

    Checks for:
    - Style violations (E, W codes)
    - Import issues (I codes)
    - Pyflakes errors (F codes)
    - And many more
    """

    name = "ruff"
    description = "Fast Python linter (10-100x faster than flake8)"

    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                ["ruff", "--version"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def run(self, paths: Optional[list[str]] = None) -> AnalyzerResult:
        if not self.is_available():
            return AnalyzerResult(
                tool=self.name,
                success=False,
                error="Ruff is not installed. Run: pip install ruff",
            )

        target = paths if paths else [str(self.project_path)]

        try:
            result = subprocess.run(
                ["ruff", "check", "--output-format=json"] + target,
                capture_output=True,
                text=True,
                cwd=str(self.project_path),
            )

            issues = self.parse_output(result.stdout)

            return AnalyzerResult(
                tool=self.name,
                success=True,
                issues=issues,
                raw_output=result.stdout,
                summary={
                    "total_issues": len(issues),
                    "fixable": sum(1 for i in issues if i.fix_available),
                },
            )
        except Exception as e:
            return AnalyzerResult(
                tool=self.name,
                success=False,
                error=str(e),
            )

    def parse_output(self, output: str) -> list[Issue]:
        if not output.strip():
            return []

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return []

        issues = []
        for item in data:
            # Determine severity based on code
            code = item.get("code", "")
            if code.startswith("E"):
                severity = Severity.ERROR
            elif code.startswith("W"):
                severity = Severity.WARNING
            else:
                severity = Severity.INFO

            issues.append(
                Issue(
                    file=item.get("filename", ""),
                    line=item.get("location", {}).get("row", 0),
                    column=item.get("location", {}).get("column", 0),
                    code=code,
                    message=item.get("message", ""),
                    severity=severity,
                    tool=self.name,
                    fix_available=item.get("fix") is not None,
                    fix_description=item.get("fix", {}).get("message") if item.get("fix") else None,
                )
            )

        return issues


class BanditAnalyzer(AnalyzerBase):
    """
    Bandit - Security-focused Python linter.

    Detects:
    - SQL injection (B608)
    - Command injection (B602, B603)
    - Hardcoded passwords (B105, B106)
    - Unsafe deserialization (B301, B302)
    """

    name = "bandit"
    description = "Python security scanner"

    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                ["bandit", "--version"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def run(self, paths: Optional[list[str]] = None) -> AnalyzerResult:
        if not self.is_available():
            return AnalyzerResult(
                tool=self.name,
                success=False,
                error="Bandit is not installed. Run: pip install bandit",
            )

        target = paths if paths else [str(self.project_path)]

        try:
            result = subprocess.run(
                ["bandit", "-r", "-f", "json"] + target,
                capture_output=True,
                text=True,
                cwd=str(self.project_path),
            )

            issues = self.parse_output(result.stdout)

            return AnalyzerResult(
                tool=self.name,
                success=True,
                issues=issues,
                raw_output=result.stdout,
                summary={
                    "total_issues": len(issues),
                    "high_severity": sum(
                        1 for i in issues if i.severity == Severity.SECURITY
                    ),
                },
            )
        except Exception as e:
            return AnalyzerResult(
                tool=self.name,
                success=False,
                error=str(e),
            )

    def parse_output(self, output: str) -> list[Issue]:
        if not output.strip():
            return []

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return []

        issues = []
        for item in data.get("results", []):
            # Map Bandit severity to our severity
            bandit_severity = item.get("issue_severity", "").upper()
            if bandit_severity == "HIGH":
                severity = Severity.SECURITY
            elif bandit_severity == "MEDIUM":
                severity = Severity.WARNING
            else:
                severity = Severity.INFO

            issues.append(
                Issue(
                    file=item.get("filename", ""),
                    line=item.get("line_number", 0),
                    column=0,
                    code=item.get("test_id", ""),
                    message=f"{item.get('issue_text', '')} (Confidence: {item.get('issue_confidence', '')})",
                    severity=severity,
                    tool=self.name,
                )
            )

        return issues


class VultureAnalyzer(AnalyzerBase):
    """
    Vulture - Dead code detector.

    Finds:
    - Unused functions
    - Unused classes
    - Unused variables
    - Unused imports
    """

    name = "vulture"
    description = "Dead code detector"

    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                ["vulture", "--version"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def run(self, paths: Optional[list[str]] = None) -> AnalyzerResult:
        if not self.is_available():
            return AnalyzerResult(
                tool=self.name,
                success=False,
                error="Vulture is not installed. Run: pip install vulture",
            )

        target = paths if paths else [str(self.project_path)]

        try:
            result = subprocess.run(
                ["vulture", "--min-confidence", "80"] + target,
                capture_output=True,
                text=True,
                cwd=str(self.project_path),
            )

            issues = self.parse_output(result.stdout)

            return AnalyzerResult(
                tool=self.name,
                success=True,
                issues=issues,
                raw_output=result.stdout,
                summary={
                    "total_unused": len(issues),
                },
            )
        except Exception as e:
            return AnalyzerResult(
                tool=self.name,
                success=False,
                error=str(e),
            )

    def parse_output(self, output: str) -> list[Issue]:
        issues = []
        # Vulture output format: file.py:line: message (confidence%)
        pattern = r"(.+):(\d+): (.+) \((\d+)% confidence\)"

        for line in output.strip().split("\n"):
            if not line.strip():
                continue

            match = re.match(pattern, line)
            if match:
                issues.append(
                    Issue(
                        file=match.group(1),
                        line=int(match.group(2)),
                        column=0,
                        code="DEAD",
                        message=f"{match.group(3)} ({match.group(4)}% confidence)",
                        severity=Severity.WARNING,
                        tool=self.name,
                    )
                )

        return issues


class RadonAnalyzer(AnalyzerBase):
    """
    Radon - Complexity analyzer.

    Calculates:
    - Cyclomatic complexity (A-F scale)
    - Maintainability index
    - Raw metrics (LOC, comments, etc.)
    """

    name = "radon"
    description = "Cyclomatic complexity analyzer"

    # Complexity thresholds
    COMPLEXITY_GRADES = {
        "A": "Simple (1-5)",
        "B": "Low (6-10)",
        "C": "Moderate (11-20)",
        "D": "High (21-30)",
        "E": "Very High (31-40)",
        "F": "Complex (41+)",
    }

    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                ["radon", "--version"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def run(self, paths: Optional[list[str]] = None) -> AnalyzerResult:
        if not self.is_available():
            return AnalyzerResult(
                tool=self.name,
                success=False,
                error="Radon is not installed. Run: pip install radon",
            )

        target = paths if paths else [str(self.project_path)]

        try:
            # Run radon cc (cyclomatic complexity) with JSON output
            result = subprocess.run(
                ["radon", "cc", "-j", "-a"] + target,
                capture_output=True,
                text=True,
                cwd=str(self.project_path),
            )

            issues = self.parse_output(result.stdout)

            return AnalyzerResult(
                tool=self.name,
                success=True,
                issues=issues,
                raw_output=result.stdout,
                summary={
                    "total_functions": len(issues),
                    "complex_functions": sum(
                        1 for i in issues if i.code in ("D", "E", "F")
                    ),
                },
            )
        except Exception as e:
            return AnalyzerResult(
                tool=self.name,
                success=False,
                error=str(e),
            )

    def parse_output(self, output: str) -> list[Issue]:
        if not output.strip():
            return []

        try:
            data = json.loads(output)
        except json.JSONDecodeError:
            return []

        issues = []
        for filename, functions in data.items():
            if filename == "error":
                continue

            for func in functions:
                rank = func.get("rank", "A")

                # Only report C or worse
                if rank not in ("C", "D", "E", "F"):
                    continue

                # Map rank to severity
                if rank in ("E", "F"):
                    severity = Severity.ERROR
                elif rank == "D":
                    severity = Severity.WARNING
                else:
                    severity = Severity.INFO

                issues.append(
                    Issue(
                        file=filename,
                        line=func.get("lineno", 0),
                        column=0,
                        code=rank,
                        message=f"{func.get('type', '')} '{func.get('name', '')}' has complexity {func.get('complexity', 0)} (Grade {rank}: {self.COMPLEXITY_GRADES.get(rank, '')})",
                        severity=severity,
                        tool=self.name,
                    )
                )

        return issues


@dataclass
class FullAnalysisResult:
    """Result from running all analyzers."""
    results: dict[str, AnalyzerResult]
    total_issues: int
    has_errors: bool
    has_security_issues: bool

    def format_report(self) -> str:
        """Format a complete analysis report."""
        lines = [
            "=" * 70,
            "SPINEHUB CODE ANALYSIS REPORT",
            "=" * 70,
            "",
            f"Total Issues: {self.total_issues}",
            f"Has Errors: {'YES' if self.has_errors else 'NO'}",
            f"Security Issues: {'YES' if self.has_security_issues else 'NO'}",
            "",
        ]

        for tool_name, result in self.results.items():
            lines.append("-" * 70)
            lines.append(f"{tool_name.upper()}")
            lines.append("-" * 70)

            if not result.success:
                lines.append(f"  ERROR: {result.error}")
                continue

            lines.append(f"  Issues: {result.issue_count}")

            if result.issues:
                lines.append("  Top Issues:")
                for issue in result.issues[:5]:
                    lines.append(
                        f"    [{issue.severity.value}] {issue.file}:{issue.line} - {issue.message[:60]}"
                    )
                if len(result.issues) > 5:
                    lines.append(f"    ... and {len(result.issues) - 5} more")

            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)


class CodeAnalyzer:
    """
    Unified code analyzer that orchestrates all analysis tools.

    Usage:
        analyzer = CodeAnalyzer("/path/to/project")
        result = analyzer.run_all()
        print(result.format_report())
    """

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.analyzers = {
            "ruff": RuffAnalyzer(project_path),
            "bandit": BanditAnalyzer(project_path),
            "vulture": VultureAnalyzer(project_path),
            "radon": RadonAnalyzer(project_path),
        }

    def check_tools(self) -> dict[str, bool]:
        """Check which tools are available."""
        return {name: analyzer.is_available() for name, analyzer in self.analyzers.items()}

    def run_all(self, paths: Optional[list[str]] = None) -> FullAnalysisResult:
        """Run all available analyzers."""
        results = {}

        for name, analyzer in self.analyzers.items():
            results[name] = analyzer.run(paths)

        total_issues = sum(r.issue_count for r in results.values())
        has_errors = any(r.has_errors for r in results.values())
        has_security = any(r.has_security_issues for r in results.values())

        return FullAnalysisResult(
            results=results,
            total_issues=total_issues,
            has_errors=has_errors,
            has_security_issues=has_security,
        )

    def run_single(
        self, tool: str, paths: Optional[list[str]] = None
    ) -> AnalyzerResult:
        """Run a single analyzer."""
        if tool not in self.analyzers:
            return AnalyzerResult(
                tool=tool,
                success=False,
                error=f"Unknown tool: {tool}. Available: {list(self.analyzers.keys())}",
            )

        return self.analyzers[tool].run(paths)
