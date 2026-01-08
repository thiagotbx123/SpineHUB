"""
SpineHUB Linear Automation Module

Provides issue templates and automated ticket generation for Linear.
Ported from LINEAR_AUTO TypeScript implementation.

Features:
- Parametrized issue templates
- Batch ticket creation with dry-run mode
- Project matrix filtering
- Template variable substitution
"""

from .templates import (
    IssueTemplate,
    MatrixRow,
    DEFAULT_TEMPLATES,
    create_template,
    list_templates,
    get_template,
)

from .generator import (
    TicketRequest,
    TicketResult,
    TicketGenerator,
    create_generator,
)

__all__ = [
    # Templates
    "IssueTemplate",
    "MatrixRow",
    "DEFAULT_TEMPLATES",
    "create_template",
    "list_templates",
    "get_template",
    # Generator
    "TicketRequest",
    "TicketResult",
    "TicketGenerator",
    "create_generator",
]
