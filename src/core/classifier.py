"""Ticket classification logic.

This module handles the classification of Jira tickets into Frontend (FE),
Backend (BE), or Uncategorized categories based on component field and key prefix.
"""

from typing import Any

from src.constants import BE_KEY_PREFIX, FE_KEY_PREFIX, Classification, Component


def classify_ticket(ticket: dict[str, Any]) -> str:
    """Classify ticket as FE, BE, or Uncategorized.

    Classification follows a priority order:
    1. Component field (if present): "Frontend" → FE, "Backend" → BE
    2. Key prefix fallback: "FE-" → FE, "BE-" → BE
    3. Default: Uncategorized

    Args:
        ticket: Dictionary containing ticket data with 'component' and 'key' fields

    Returns:
        Classification as "FE", "BE", or "Uncategorized"

    Examples:
        >>> # Component takes priority
        >>> classify_ticket({"key": "BE-123", "component": "Frontend"})
        'FE'

        >>> # Fallback to key prefix
        >>> classify_ticket({"key": "FE-456", "component": None})
        'FE'

        >>> # Uncategorized when neither match
        >>> classify_ticket({"key": "OPS-789", "component": None})
        'Uncategorized'

        >>> # Missing key
        >>> classify_ticket({"component": None})
        'Uncategorized'

    Notes:
        - Component field has higher priority than key prefix
        - This is a business rule decision (see ASSUMPTIONS.md)
        - Key prefix matching is case-sensitive ("FE-" not "fe-")

    See Also:
        - src.constants.Component: Valid component values
        - src.constants.Classification: Return type enum
    """
    component: str | None = ticket.get("component")
    key: str = ticket.get("key", "")

    # Priority 1: Check component field
    if component == Component.FRONTEND.value:
        return Classification.FE.value
    if component == Component.BACKEND.value:
        return Classification.BE.value

    # Priority 2: Fallback to key prefix
    if key.startswith(FE_KEY_PREFIX):
        return Classification.FE.value
    if key.startswith(BE_KEY_PREFIX):
        return Classification.BE.value

    # Priority 3: Default to uncategorized
    return Classification.UNCATEGORIZED.value
