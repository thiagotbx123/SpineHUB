"""
Privacy Utilities for PII Redaction

Ported from TSA_CORTEX TypeScript implementation.
Provides GDPR-compliant PII detection and redaction.
Supports US and Brazilian document formats.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional


# Common PII patterns
PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"(\+?[0-9]{1,3}[-.\s]?)?\(?[0-9]{2,3}\)?[-.\s]?[0-9]{3,5}[-.\s]?[0-9]{4}"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    # Brazilian documents
    "cpf": re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),
    "cnpj": re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"),
    # IP addresses
    "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
}


@dataclass
class RedactionConfig:
    """Configuration for PII redaction."""
    redact_emails: bool = True
    redact_phone_numbers: bool = True
    redact_ssn: bool = True
    redact_credit_cards: bool = True
    redact_cpf_cnpj: bool = True
    redact_ip_addresses: bool = False
    custom_patterns: List[str] = field(default_factory=list)


@dataclass
class RedactionResult:
    """Result of PII redaction operation."""
    text: str
    redacted_count: int
    types: List[str]


def redact_pii(
    text: str,
    config: Optional[RedactionConfig] = None
) -> RedactionResult:
    """
    Redact PII from text based on configuration.

    Args:
        text: Text to redact PII from
        config: RedactionConfig or None for defaults

    Returns:
        RedactionResult with redacted text and statistics
    """
    if config is None:
        config = RedactionConfig()

    result = text
    types: List[str] = []
    redacted_count = 0

    # Email addresses
    if config.redact_emails:
        matches = PATTERNS["email"].findall(result)
        if matches:
            redacted_count += len(matches)
            types.append("email")
            result = PATTERNS["email"].sub("[EMAIL_REDACTED]", result)

    # Phone numbers
    if config.redact_phone_numbers:
        matches = PATTERNS["phone"].findall(result)
        if matches:
            redacted_count += len(matches)
            types.append("phone")
            result = PATTERNS["phone"].sub("[PHONE_REDACTED]", result)

    # SSN (always redact - highly sensitive)
    if config.redact_ssn:
        matches = PATTERNS["ssn"].findall(result)
        if matches:
            redacted_count += len(matches)
            types.append("ssn")
            result = PATTERNS["ssn"].sub("[SSN_REDACTED]", result)

    # Credit cards (always redact - highly sensitive)
    if config.redact_credit_cards:
        matches = PATTERNS["credit_card"].findall(result)
        if matches:
            redacted_count += len(matches)
            types.append("credit_card")
            result = PATTERNS["credit_card"].sub("[CC_REDACTED]", result)

    # Brazilian CPF
    if config.redact_cpf_cnpj:
        matches = PATTERNS["cpf"].findall(result)
        if matches:
            redacted_count += len(matches)
            types.append("cpf")
            result = PATTERNS["cpf"].sub("[CPF_REDACTED]", result)

        # Brazilian CNPJ
        matches = PATTERNS["cnpj"].findall(result)
        if matches:
            redacted_count += len(matches)
            types.append("cnpj")
            result = PATTERNS["cnpj"].sub("[CNPJ_REDACTED]", result)

    # IP addresses
    if config.redact_ip_addresses:
        matches = PATTERNS["ip_address"].findall(result)
        if matches:
            redacted_count += len(matches)
            types.append("ip_address")
            result = PATTERNS["ip_address"].sub("[IP_REDACTED]", result)

    # Custom patterns
    for pattern_str in config.custom_patterns:
        try:
            pattern = re.compile(pattern_str)
            matches = pattern.findall(result)
            if matches:
                redacted_count += len(matches)
                types.append("custom")
                result = pattern.sub("[REDACTED]", result)
        except re.error:
            # Invalid regex, skip
            pass

    return RedactionResult(
        text=result,
        redacted_count=redacted_count,
        types=list(set(types))
    )


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to maximum length, preserving word boundaries.

    Args:
        text: Text to truncate
        max_length: Maximum length (default 500)

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]

    # Try to preserve word boundary
    last_space = truncated.rfind(" ")
    if last_space > max_length * 0.8:
        truncated = truncated[:last_space]

    return truncated + "..."


def sanitize_for_log(text: str, max_length: int = 200) -> str:
    """
    Sanitize text for safe logging.

    Removes newlines, collapses whitespace, and truncates.

    Args:
        text: Text to sanitize
        max_length: Maximum length for log output

    Returns:
        Sanitized text suitable for logging
    """
    result = text.replace("\n", " ").replace("\r", " ")
    result = re.sub(r"\s+", " ", result)
    return result.strip()[:max_length]


def mask_email(email: str) -> str:
    """
    Mask email address for display (e.g., j***@domain.com).

    Args:
        email: Email address to mask

    Returns:
        Masked email
    """
    if "@" not in email:
        return "[INVALID_EMAIL]"

    local, domain = email.rsplit("@", 1)
    if len(local) <= 1:
        masked_local = local[0] + "***"
    else:
        masked_local = local[0] + "***"

    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Mask phone number for display (e.g., ***-***-1234).

    Args:
        phone: Phone number to mask

    Returns:
        Masked phone showing only last 4 digits
    """
    # Extract only digits
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 4:
        return "[INVALID_PHONE]"

    return f"***-***-{digits[-4:]}"
