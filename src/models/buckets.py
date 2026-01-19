"""Data models for categorization results.

This module defines the CategorizationResult dataclass for storing tickets
grouped into the 7 reporting buckets.
"""

from dataclasses import dataclass, field
from typing import Any

from src.models.ticket import JiraTicket


@dataclass
class EpicGroup:
    """Group of tickets within an epic for focus items.

    Attributes:
        epic: Name of the epic
        tickets: List of tickets in this epic
    """

    epic: str
    tickets: list[JiraTicket] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {"epic": self.epic, "tickets": [t.to_dict() for t in self.tickets]}


@dataclass
class CategorizationResult:
    """Result of categorizing tickets into reporting buckets.

    This represents the 7-bucket system used for weekly deployment reports:
    1. FE Deployed Last Week
    2. BE Deployed Last Week
    3. FE Expected Next 14 Days
    4. BE Expected Next 14 Days
    5. Team Focus Items (grouped by epic)
    6. Risks/Blocks
    7. Uncategorized

    Attributes:
        fe_deployed: Frontend tickets deployed last week
        be_deployed: Backend tickets deployed last week
        fe_upcoming: Frontend tickets expected in next 14 days
        be_upcoming: Backend tickets expected in next 14 days
        focus_items: In Progress/To Do tickets grouped by epic
        risks_blocks: Blocked tickets or those with blocked_reason
        uncategorized: Tickets not matching any FE/BE classification

    Examples:
        >>> result = CategorizationResult()
        >>> result.fe_deployed.append(
        ...     JiraTicket(key="FE-101", summary="Test", status="Done")
        ... )
        >>> len(result.fe_deployed)
        1

        >>> # Check if any buckets have items
        >>> result.has_deployed_tickets()
        True

        >>> # Get summary counts
        >>> summary = result.summary()
        >>> summary["fe_deployed"]
        1
    """

    fe_deployed: list[JiraTicket] = field(default_factory=list)
    be_deployed: list[JiraTicket] = field(default_factory=list)
    fe_upcoming: list[JiraTicket] = field(default_factory=list)
    be_upcoming: list[JiraTicket] = field(default_factory=list)
    focus_items: list[EpicGroup] = field(default_factory=list)
    risks_blocks: list[JiraTicket] = field(default_factory=list)
    uncategorized: list[JiraTicket] = field(default_factory=list)

    def has_deployed_tickets(self) -> bool:
        """Check if any tickets were deployed last week.

        Returns:
            True if fe_deployed or be_deployed have tickets
        """
        return len(self.fe_deployed) > 0 or len(self.be_deployed) > 0

    def has_upcoming_tickets(self) -> bool:
        """Check if any tickets are expected in next 14 days.

        Returns:
            True if fe_upcoming or be_upcoming have tickets
        """
        return len(self.fe_upcoming) > 0 or len(self.be_upcoming) > 0

    def has_focus_items(self) -> bool:
        """Check if there are any focus items.

        Returns:
            True if focus_items has any epic groups
        """
        return len(self.focus_items) > 0

    def has_risks(self) -> bool:
        """Check if there are any risks or blocked tickets.

        Returns:
            True if risks_blocks has tickets
        """
        return len(self.risks_blocks) > 0

    def total_tickets(self) -> int:
        """Get total number of tickets across all buckets.

        Returns:
            Total count of tickets
        """
        focus_count = sum(len(group.tickets) for group in self.focus_items)
        return (
            len(self.fe_deployed)
            + len(self.be_deployed)
            + len(self.fe_upcoming)
            + len(self.be_upcoming)
            + focus_count
            + len(self.risks_blocks)
            + len(self.uncategorized)
        )

    def summary(self) -> dict[str, int]:
        """Get summary of ticket counts per bucket.

        Returns:
            Dictionary mapping bucket name to ticket count

        Examples:
            >>> result = CategorizationResult()
            >>> result.fe_deployed.append(
            ...     JiraTicket(key="FE-1", summary="Test", status="Done")
            ... )
            >>> result.be_deployed.append(
            ...     JiraTicket(key="BE-1", summary="Test", status="Done")
            ... )
            >>> summary = result.summary()
            >>> summary["fe_deployed"]
            1
            >>> summary["be_deployed"]
            1
            >>> summary["total"]
            2
        """
        focus_count = sum(len(group.tickets) for group in self.focus_items)
        return {
            "fe_deployed": len(self.fe_deployed),
            "be_deployed": len(self.be_deployed),
            "fe_upcoming": len(self.fe_upcoming),
            "be_upcoming": len(self.be_upcoming),
            "focus_items": focus_count,
            "risks_blocks": len(self.risks_blocks),
            "uncategorized": len(self.uncategorized),
            "total": self.total_tickets(),
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format matching original structure.

        Returns:
            Dictionary with all buckets in original format

        Examples:
            >>> result = CategorizationResult()
            >>> data = result.to_dict()
            >>> "fe_deployed" in data
            True
            >>> isinstance(data["fe_deployed"], list)
            True
        """
        return {
            "fe_deployed": [t.to_dict() for t in self.fe_deployed],
            "be_deployed": [t.to_dict() for t in self.be_deployed],
            "fe_upcoming": [t.to_dict() for t in self.fe_upcoming],
            "be_upcoming": [t.to_dict() for t in self.be_upcoming],
            "focus_items": [g.to_dict() for g in self.focus_items],
            "risks_blocks": [t.to_dict() for t in self.risks_blocks],
            "uncategorized": [t.to_dict() for t in self.uncategorized],
        }

    def __repr__(self) -> str:
        """Return concise string representation with counts."""
        summary = self.summary()
        return (
            f"CategorizationResult("
            f"FE_deployed={summary['fe_deployed']}, "
            f"BE_deployed={summary['be_deployed']}, "
            f"FE_upcoming={summary['fe_upcoming']}, "
            f"BE_upcoming={summary['be_upcoming']}, "
            f"focus={summary['focus_items']}, "
            f"risks={summary['risks_blocks']}, "
            f"uncategorized={summary['uncategorized']}, "
            f"total={summary['total']})"
        )
