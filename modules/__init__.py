"""
SpineHUB Modules Package

Provides collectors, utilities, and automation tools for SpineHUB.

Subpackages:
- collectors: Multi-source data collection (Slack, Linear, Drive, Claude, Local)
- utils: Common utilities (datetime, privacy, slack channels)
- linear: Linear automation (templates, ticket generator)
"""

# Export subpackages for easy access
from . import collectors
from . import utils
from . import linear

__all__ = [
    "collectors",
    "utils",
    "linear",
]
