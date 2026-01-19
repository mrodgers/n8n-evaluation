"""Ticket categorization logic.

This module handles the core categorization logic that sorts tickets into
the 7 reporting buckets based on status, dates, and classification.
"""

from typing import Any

from src.constants import (
    DEFAULT_EPIC_NAME,
    FIELD_EPIC,
    FIELD_FIX_VERSION,
    FIELD_KEY,
    FIELD_STATUS,
    FIELD_TARGET_DEPLOY_DATE,
    Classification,
    TicketStatus,
)
from src.core.classifier import classify_ticket
from src.core.date_utils import parse_date
from src.models.buckets import CategorizationResult, EpicGroup
from src.models.ticket import JiraTicket
from src.models.windows import DateWindows


def filter_and_categorize(
    tickets: list[dict[str, Any]], windows: DateWindows | dict[str, str]
) -> CategorizationResult:
    """Categorize tickets into reporting buckets based on status and dates.

    This is the core categorization logic that implements the 7-bucket system:
    1. FE Deployed Last Week
    2. BE Deployed Last Week
    3. FE Expected Next 14 Days
    4. BE Expected Next 14 Days
    5. Team Focus Items (grouped by epic)
    6. Risks/Blocks
    7. Uncategorized

    Priority Rules (higher priority wins):
    1. Blocked/Risk → risks_blocks bucket
    2. Done + deployed last week → fe_deployed or be_deployed
    3. Ready for Deploy/In QA + upcoming → fe_upcoming or be_upcoming
    4. In Progress/To Do → focus_items (grouped by epic)
    5. Everything else → uncategorized

    Args:
        tickets: List of ticket dictionaries to categorize
        windows: DateWindows object or dict with date range information

    Returns:
        CategorizationResult with tickets sorted into 7 buckets

    Examples:
        >>> from src.core.date_utils import calculate_date_windows
        >>> windows = calculate_date_windows()
        >>>
        >>> # Deployed ticket
        >>> tickets = [{
        ...     "key": "FE-101",
        ...     "status": "Done",
        ...     "component": "Frontend",
        ...     "deployed_date": "2026-01-15",
        ...     "summary": "Test"
        ... }]
        >>> result = filter_and_categorize(tickets, windows)
        >>> len(result.fe_deployed) > 0
        True
        >>>
        >>> # Blocked ticket takes priority
        >>> blocked = [{
        ...     "key": "BE-999",
        ...     "status": "Blocked",
        ...     "component": "Backend",
        ...     "deployed_date": "2026-01-15",
        ...     "summary": "Test"
        ... }]
        >>> result = filter_and_categorize(blocked, windows)
        >>> len(result.risks_blocks) > 0
        True
        >>> len(result.be_deployed)  # Not in deployed!
        0

    Notes:
        - Tickets only appear in ONE bucket (first match wins)
        - Blocked status/blocked_reason takes highest priority
        - Missing deployed_date falls back to updated field
        - Missing epic for focus items → "Other Focus Items"
        - Missing target_deploy_date with fix_version still included in upcoming

    See Also:
        - classify_ticket(): Determines FE vs BE vs Uncategorized
        - DateWindows: Date range definitions
        - CategorizationResult: Return type structure
    """
    # Convert DateWindows to dict if needed for backward compatibility
    windows_dict = windows.to_dict() if isinstance(windows, DateWindows) else windows

    # Parse window boundaries
    last_week_start = parse_date(windows_dict["last_week_start"])
    last_week_end = parse_date(windows_dict["last_week_end"])
    next_14_start = parse_date(windows_dict["next_14_start"])
    next_14_end = parse_date(windows_dict["next_14_end"])

    # Initialize result buckets
    result = CategorizationResult()

    # Track processed tickets to avoid duplicates
    processed: set[str] = set()

    # Dictionary for building focus items by epic
    focus_items_dict: dict[str, list[dict[str, Any]]] = {}

    for ticket_data in tickets:
        key: str = ticket_data.get(FIELD_KEY, "")
        status: str = ticket_data.get(FIELD_STATUS, "")
        classification: str = classify_ticket(ticket_data)

        # Priority 1: Check for risks/blocks first (highest priority)
        if status == TicketStatus.BLOCKED.value or ticket_data.get("blocked_reason"):
            ticket = JiraTicket.from_dict(ticket_data)
            result.risks_blocks.append(ticket)
            processed.add(key)
            continue

        # Priority 2: Check if deployed last week
        if status == TicketStatus.DONE.value:
            # Try deployed_date first, fall back to updated
            deploy_date = parse_date(ticket_data.get("deployed_date")) or parse_date(
                ticket_data.get("updated")
            )

            if (
                deploy_date
                and last_week_start
                and last_week_end
                and last_week_start <= deploy_date <= last_week_end
            ):
                ticket = JiraTicket.from_dict(ticket_data)

                if classification == Classification.FE.value:
                    result.fe_deployed.append(ticket)
                elif classification == Classification.BE.value:
                    result.be_deployed.append(ticket)
                else:
                    result.uncategorized.append(ticket)

                processed.add(key)
                continue

        # Priority 3: Check if expected next 14 days
        if status in [TicketStatus.READY_FOR_DEPLOY.value, TicketStatus.IN_QA.value]:
            target_date = parse_date(ticket_data.get(FIELD_TARGET_DEPLOY_DATE))
            in_window = (
                target_date
                and next_14_start
                and next_14_end
                and next_14_start <= target_date <= next_14_end
            )
            has_fallback = ticket_data.get(FIELD_FIX_VERSION) is not None

            # Include if in window OR has fix_version as fallback
            if in_window or has_fallback:
                ticket = JiraTicket.from_dict(ticket_data)

                if classification == Classification.FE.value:
                    result.fe_upcoming.append(ticket)
                elif classification == Classification.BE.value:
                    result.be_upcoming.append(ticket)
                else:
                    result.uncategorized.append(ticket)

                processed.add(key)
                continue

        # Priority 4: Check if focus item (In Progress or To Do)
        if status in [TicketStatus.IN_PROGRESS.value, TicketStatus.TO_DO.value]:
            epic: str = ticket_data.get(FIELD_EPIC) or DEFAULT_EPIC_NAME

            # Build epic groups (will convert to EpicGroup objects later)
            if epic not in focus_items_dict:
                focus_items_dict[epic] = []
            focus_items_dict[epic].append(ticket_data)

            processed.add(key)
            continue

        # Priority 5: Default to uncategorized
        if key not in processed:
            ticket = JiraTicket.from_dict(ticket_data)
            result.uncategorized.append(ticket)

    # Convert focus_items dictionary to list of EpicGroup objects
    for epic, ticket_data_list in focus_items_dict.items():
        tickets_in_epic = [JiraTicket.from_dict(t) for t in ticket_data_list]
        epic_group = EpicGroup(epic=epic, tickets=tickets_in_epic)
        result.focus_items.append(epic_group)

    return result
