"""
SpineHUB Quality Validator (Benchmark)

Validates worklog quality against defined rules.
Based on RAC-14 standard from TSA_CORTEX.
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    """Result of a validation check."""
    rule_id: str
    rule_name: str
    passed: bool
    message: str
    severity: str  # "error", "warning", "info"
    line: Optional[int] = None


class QualityValidator:
    """
    Validates worklog and document quality.

    Rules are based on the RAC-14 standard:
    - Language must be 100% English
    - Third person narrative (not "I did", but "Thiago did")
    - No direct Slack quotes
    - All artifacts must have URLs
    - Each theme must have an outcome
    """

    # Quality rules configuration
    RULES = {
        "LANG_001": {
            "name": "English Only",
            "description": "Content must be 100% in English",
            "severity": "error",
            "patterns": [
                # Portuguese indicators
                r"\b(voce|você|trabalhou|fez|disse|reuniao|reunião)\b",
                r"\b(porque|então|também|já|não|está)\b",
                r"\b(projeto|arquivo|documento|semana)\b",
            ],
        },
        "PERS_001": {
            "name": "Third Person",
            "description": "Use third person narrative",
            "severity": "error",
            "patterns": [
                r"\b[Ii] (did|worked|created|updated|fixed|met)\b",
                r"\b[Ii]'m\b",
                r"\b[Mm]y work\b",
                r"\b[Ww]e (did|worked|created)\b",
            ],
        },
        "SLACK_001": {
            "name": "No Slack Quotes",
            "description": "Do not quote Slack messages directly",
            "severity": "error",
            "patterns": [
                r'"[^"]{20,}"',  # Long quotes
                r"said:\s*['\"]",
                r"wrote:\s*['\"]",
                r"messaged:\s*['\"]",
            ],
        },
        "STRUCT_001": {
            "name": "Has Summary",
            "description": "Worklog must have a Summary section",
            "severity": "warning",
            "check": "has_section",
            "section": "Summary",
        },
        "STRUCT_002": {
            "name": "Has Artifacts",
            "description": "Each theme should have Artifacts section",
            "severity": "warning",
            "check": "has_section",
            "section": "Artifacts",
        },
        "STRUCT_003": {
            "name": "Has Outcome",
            "description": "Each theme should have Outcome section",
            "severity": "warning",
            "check": "has_section",
            "section": "Outcome",
        },
        "LINK_001": {
            "name": "Artifacts Have URLs",
            "description": "Artifacts should have clickable links",
            "severity": "warning",
            "check": "has_urls_in_artifacts",
        },
        "META_001": {
            "name": "Has Metadata Table",
            "description": "Worklog should have metadata table",
            "severity": "info",
            "patterns": [
                r"\|\s*Field\s*\|\s*Value\s*\|",
                r"\|\s*Period\s*\|",
            ],
        },
    }

    def __init__(self):
        self.results: list[ValidationResult] = []

    def validate(self, content: str) -> list[ValidationResult]:
        """
        Validate content against all quality rules.

        Args:
            content: The text content to validate

        Returns:
            List of ValidationResult objects
        """
        self.results = []

        for rule_id, rule in self.RULES.items():
            if "patterns" in rule:
                self._check_patterns(rule_id, rule, content)
            elif rule.get("check") == "has_section":
                self._check_section(rule_id, rule, content)
            elif rule.get("check") == "has_urls_in_artifacts":
                self._check_artifact_urls(rule_id, rule, content)

        return self.results

    def _check_patterns(self, rule_id: str, rule: dict, content: str) -> None:
        """Check for pattern matches (violations)."""
        for pattern in rule["patterns"]:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                # Find line number for first match
                first_match = matches[0]
                line_num = content[: first_match.start()].count("\n") + 1

                self.results.append(
                    ValidationResult(
                        rule_id=rule_id,
                        rule_name=rule["name"],
                        passed=False,
                        message=f"Found {len(matches)} violation(s): '{matches[0].group()}'",
                        severity=rule["severity"],
                        line=line_num,
                    )
                )
                return  # Only report first pattern match per rule

        # No violations found
        self.results.append(
            ValidationResult(
                rule_id=rule_id,
                rule_name=rule["name"],
                passed=True,
                message="No violations found",
                severity=rule["severity"],
            )
        )

    def _check_section(self, rule_id: str, rule: dict, content: str) -> None:
        """Check if required section exists."""
        section = rule["section"]
        patterns = [
            rf"^##?\s*{section}",  # ## Summary or # Summary
            rf"\*\*{section}\*\*",  # **Summary**
            rf"^{section}:",  # Summary:
        ]

        found = any(
            re.search(p, content, re.MULTILINE | re.IGNORECASE) for p in patterns
        )

        self.results.append(
            ValidationResult(
                rule_id=rule_id,
                rule_name=rule["name"],
                passed=found,
                message=f"Section '{section}' {'found' if found else 'not found'}",
                severity=rule["severity"],
            )
        )

    def _check_artifact_urls(self, rule_id: str, rule: dict, content: str) -> None:
        """Check if artifacts section has URLs."""
        # Find Artifacts sections
        artifact_section = re.search(
            r"\*\*Artifacts?\*\*:?\s*(.*?)(?=\n\n|\n\*\*|\Z)",
            content,
            re.DOTALL | re.IGNORECASE,
        )

        if not artifact_section:
            self.results.append(
                ValidationResult(
                    rule_id=rule_id,
                    rule_name=rule["name"],
                    passed=True,
                    message="No Artifacts section found (skipped)",
                    severity="info",
                )
            )
            return

        section_content = artifact_section.group(1)

        # Check for URLs or markdown links
        has_urls = bool(
            re.search(r"https?://|www\.|]\(http", section_content, re.IGNORECASE)
        )

        self.results.append(
            ValidationResult(
                rule_id=rule_id,
                rule_name=rule["name"],
                passed=has_urls,
                message="Artifacts have URLs" if has_urls else "Artifacts missing URLs",
                severity=rule["severity"],
            )
        )

    def get_summary(self) -> dict:
        """Get validation summary."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        errors = sum(
            1 for r in self.results if not r.passed and r.severity == "error"
        )
        warnings = sum(
            1 for r in self.results if not r.passed and r.severity == "warning"
        )

        return {
            "total_rules": total,
            "passed": passed,
            "failed": total - passed,
            "errors": errors,
            "warnings": warnings,
            "score": round(passed / total * 100, 1) if total > 0 else 0,
            "status": "PASS" if errors == 0 else "FAIL",
        }

    def format_report(self) -> str:
        """Format validation results as a report."""
        summary = self.get_summary()

        lines = [
            "=" * 60,
            "QUALITY VALIDATION REPORT",
            "=" * 60,
            "",
            f"Status: {summary['status']}",
            f"Score: {summary['score']}%",
            f"Passed: {summary['passed']}/{summary['total_rules']}",
            f"Errors: {summary['errors']}",
            f"Warnings: {summary['warnings']}",
            "",
            "-" * 60,
            "DETAILS",
            "-" * 60,
        ]

        for result in self.results:
            icon = "[PASS]" if result.passed else "[FAIL]"
            line_info = f" (line {result.line})" if result.line else ""
            lines.append(
                f"{icon} [{result.severity.upper()}] {result.rule_name}{line_info}"
            )
            lines.append(f"       {result.message}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)


def validate_worklog(content: str) -> tuple[bool, str]:
    """
    Convenience function to validate worklog content.

    Returns:
        Tuple of (passed: bool, report: str)
    """
    validator = QualityValidator()
    validator.validate(content)
    summary = validator.get_summary()
    report = validator.format_report()
    return summary["status"] == "PASS", report
