"""Constants and enumerations for the Weekly Deployment Update workflow.

This module defines all constants, magic strings, and enumerations used throughout
the application to ensure type safety and maintainability.
"""

from enum import Enum
from typing import Final


class Component(str, Enum):
    """Jira ticket component types.

    These values match the actual Jira component field values.
    """

    FRONTEND = "Frontend"
    BACKEND = "Backend"


class TicketStatus(str, Enum):
    """Jira ticket status values.

    These represent the standard Jira workflow statuses.
    """

    DONE = "Done"
    BLOCKED = "Blocked"
    READY_FOR_DEPLOY = "Ready for Deploy"
    IN_QA = "In QA"
    IN_PROGRESS = "In Progress"
    TO_DO = "To Do"


class Classification(str, Enum):
    """Ticket classification for reporting.

    Used to categorize tickets into Frontend, Backend, or Uncategorized groups.
    """

    FE = "FE"
    BE = "BE"
    UNCATEGORIZED = "Uncategorized"


class BucketName(str, Enum):
    """Report bucket names.

    The 7 buckets used for categorizing tickets in reports.
    """

    FE_DEPLOYED = "fe_deployed"
    BE_DEPLOYED = "be_deployed"
    FE_UPCOMING = "fe_upcoming"
    BE_UPCOMING = "be_upcoming"
    FOCUS_ITEMS = "focus_items"
    RISKS_BLOCKS = "risks_blocks"
    UNCATEGORIZED = "uncategorized"


# Date and time constants
TIMEZONE: Final[str] = "UTC"
DATE_FORMAT: Final[str] = "%Y-%m-%d"
ISO_WEEK_FORMAT: Final[str] = "%Y-W%W"
TIMESTAMP_FORMAT: Final[str] = "%Y-%m-%dT%H-%M-%SZ"

# Categorization constants
UPCOMING_DAYS_WINDOW: Final[int] = 14
"""Number of days in the 'upcoming' window (next 14 days)."""

# File path constants
DEFAULT_OUTPUT_DIR: Final[str] = "outputs"
DEFAULT_MOCKDATA_DIR: Final[str] = "mockdata"
CONFLUENCE_SUBDIR: Final[str] = "confluence"
SLIDES_SUBDIR: Final[str] = "slides"

# Filename patterns
CONFLUENCE_FILENAME_PATTERN: Final[str] = "week-{week}.md"
SLIDES_FILENAME_PATTERN: Final[str] = "{year}-{week}.txt"
MOCK_TICKETS_FILENAME: Final[str] = "mock_jira_tickets.json"
CATEGORIZED_DATA_FILENAME: Final[str] = "categorized_data.json"

# Ticket field names (for consistency)
FIELD_KEY: Final[str] = "key"
FIELD_SUMMARY: Final[str] = "summary"
FIELD_STATUS: Final[str] = "status"
FIELD_COMPONENT: Final[str] = "component"
FIELD_DEPLOYED_DATE: Final[str] = "deployed_date"
FIELD_UPDATED: Final[str] = "updated"
FIELD_EPIC: Final[str] = "epic"
FIELD_FIX_VERSION: Final[str] = "fix_version"
FIELD_TARGET_DEPLOY_DATE: Final[str] = "target_deploy_date"
FIELD_BLOCKED_REASON: Final[str] = "blocked_reason"

# Default values
DEFAULT_EPIC_NAME: Final[str] = "Other Focus Items"
"""Epic name used when a focus item has no epic specified."""

EMPTY_BUCKET_PLACEHOLDER: Final[str] = "[None]"
"""Text displayed when a bucket has no items."""

TBD_DATE_PLACEHOLDER: Final[str] = "TBD"
"""Text displayed when a target deploy date is missing."""

# Key prefixes for classification fallback
FE_KEY_PREFIX: Final[str] = "FE-"
BE_KEY_PREFIX: Final[str] = "BE-"

# Mock data configuration
DEFAULT_MOCK_TICKET_COUNT: Final[int] = 28
"""Default number of mock tickets to generate."""
