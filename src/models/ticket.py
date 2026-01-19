"""Data models for Jira tickets.

This module defines the JiraTicket dataclass and related utilities for working
with ticket data throughout the workflow.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class JiraTicket:
    """Represents a Jira ticket.

    This is the core data model for tickets processed by the workflow.
    All ticket data flows through this structure.

    Attributes:
        key: Unique ticket identifier (e.g., "FE-101", "BE-201")
        summary: Brief description of the ticket
        status: Current status (Done, In Progress, Blocked, etc.)
        component: Optional component classification (Frontend, Backend)
        deployed_date: ISO date string when the ticket was deployed (YYYY-MM-DD)
        updated: ISO date string of last update (YYYY-MM-DD)
        epic: Name of the epic this ticket belongs to
        fix_version: Target fix version (e.g., "2026.1")
        target_deploy_date: Planned deployment date (YYYY-MM-DD)
        blocked_reason: Reason for blockage if status is Blocked

    Examples:
        >>> ticket = JiraTicket(
        ...     key="FE-101",
        ...     summary="Implement dark mode",
        ...     status="Done",
        ...     component="Frontend",
        ...     deployed_date="2026-01-15"
        ... )
        >>> ticket.key
        'FE-101'

        >>> # Create from dictionary (e.g., from JSON)
        >>> data = {"key": "BE-201", "summary": "Add API endpoint", "status": "In Progress"}
        >>> ticket = JiraTicket.from_dict(data)
        >>> ticket.summary
        'Add API endpoint'
    """

    key: str
    summary: str
    status: str
    component: Optional[str] = None
    deployed_date: Optional[str] = None
    updated: Optional[str] = None
    epic: Optional[str] = None
    fix_version: Optional[str] = None
    target_deploy_date: Optional[str] = None
    blocked_reason: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert ticket to dictionary format.

        Returns:
            Dictionary with all ticket fields. None values are preserved.

        Examples:
            >>> ticket = JiraTicket(key="FE-101", summary="Test", status="Done")
            >>> data = ticket.to_dict()
            >>> data["key"]
            'FE-101'
            >>> "component" in data
            True
        """
        return {
            "key": self.key,
            "summary": self.summary,
            "status": self.status,
            "component": self.component,
            "deployed_date": self.deployed_date,
            "updated": self.updated,
            "epic": self.epic,
            "fix_version": self.fix_version,
            "target_deploy_date": self.target_deploy_date,
            "blocked_reason": self.blocked_reason,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JiraTicket":
        """Create ticket from dictionary.

        Args:
            data: Dictionary containing ticket fields

        Returns:
            JiraTicket instance with data from the dictionary

        Notes:
            - Only known fields are extracted (unknown fields are ignored)
            - Missing optional fields default to None
            - Required fields (key, summary, status) must be present

        Examples:
            >>> data = {
            ...     "key": "FE-101",
            ...     "summary": "Test ticket",
            ...     "status": "Done",
            ...     "unknown_field": "ignored"
            ... }
            >>> ticket = JiraTicket.from_dict(data)
            >>> ticket.key
            'FE-101'
        """
        # Extract only known fields
        valid_fields = {
            k: v for k, v in data.items() if k in cls.__dataclass_fields__
        }
        return cls(**valid_fields)

    def is_blocked(self) -> bool:
        """Check if ticket is blocked.

        A ticket is considered blocked if it has status "Blocked" or
        has a blocked_reason specified.

        Returns:
            True if ticket is blocked, False otherwise

        Examples:
            >>> ticket = JiraTicket(key="FE-1", summary="Test", status="Blocked")
            >>> ticket.is_blocked()
            True

            >>> ticket2 = JiraTicket(
            ...     key="FE-2",
            ...     summary="Test",
            ...     status="Done",
            ...     blocked_reason="Waiting on API"
            ... )
            >>> ticket2.is_blocked()
            True
        """
        from src.constants import TicketStatus

        return self.status == TicketStatus.BLOCKED.value or bool(self.blocked_reason)

    def get_deploy_date(self) -> Optional[str]:
        """Get the deployment date with fallback to updated.

        Returns deployed_date if available, otherwise falls back to updated.
        This matches the behavior expected in the categorization logic.

        Returns:
            Deployment date string or None if neither is available

        Examples:
            >>> ticket = JiraTicket(
            ...     key="FE-1",
            ...     summary="Test",
            ...     status="Done",
            ...     deployed_date="2026-01-15",
            ...     updated="2026-01-14"
            ... )
            >>> ticket.get_deploy_date()
            '2026-01-15'

            >>> ticket2 = JiraTicket(
            ...     key="FE-2",
            ...     summary="Test",
            ...     status="Done",
            ...     updated="2026-01-14"
            ... )
            >>> ticket2.get_deploy_date()
            '2026-01-14'
        """
        return self.deployed_date or self.updated

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return (
            f"JiraTicket(key='{self.key}', summary='{self.summary}', "
            f"status='{self.status}', component={self.component})"
        )
