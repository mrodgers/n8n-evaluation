"""Data models for date windows.

This module defines the DateWindows dataclass for tracking date ranges
used in ticket categorization.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class DateWindows:
    """Date ranges for ticket categorization.

    Defines the "last week" and "next 14 days" windows used to categorize
    tickets into deployed vs upcoming buckets.

    Attributes:
        last_week_start: Start of last week (Monday, YYYY-MM-DD)
        last_week_end: End of last week (Sunday, YYYY-MM-DD)
        next_14_start: Start of upcoming window (today, YYYY-MM-DD)
        next_14_end: End of upcoming window (today + 14 days, YYYY-MM-DD)
        current_date: Reference date for calculations (YYYY-MM-DD)
        timezone: Timezone used for calculations (default: "UTC")

    Examples:
        >>> windows = DateWindows(
        ...     last_week_start="2026-01-12",
        ...     last_week_end="2026-01-18",
        ...     next_14_start="2026-01-19",
        ...     next_14_end="2026-02-02",
        ...     current_date="2026-01-19",
        ...     timezone="UTC"
        ... )
        >>> windows.last_week_start
        '2026-01-12'

        >>> # Check if a date is in the last week
        >>> "2026-01-15" >= windows.last_week_start
        True
        >>> "2026-01-15" <= windows.last_week_end
        True
    """

    last_week_start: str
    last_week_end: str
    next_14_start: str
    next_14_end: str
    current_date: str
    timezone: str = "UTC"

    def is_in_last_week(self, date_str: str) -> bool:
        """Check if a date falls within last week's window.

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            True if date is within last week (inclusive), False otherwise

        Examples:
            >>> windows = DateWindows(
            ...     last_week_start="2026-01-12",
            ...     last_week_end="2026-01-18",
            ...     next_14_start="2026-01-19",
            ...     next_14_end="2026-02-02",
            ...     current_date="2026-01-19"
            ... )
            >>> windows.is_in_last_week("2026-01-15")
            True
            >>> windows.is_in_last_week("2026-01-11")
            False
            >>> windows.is_in_last_week("2026-01-19")
            False
        """
        return self.last_week_start <= date_str <= self.last_week_end

    def is_in_next_14_days(self, date_str: str) -> bool:
        """Check if a date falls within the next 14 days window.

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            True if date is within next 14 days (inclusive), False otherwise

        Examples:
            >>> windows = DateWindows(
            ...     last_week_start="2026-01-12",
            ...     last_week_end="2026-01-18",
            ...     next_14_start="2026-01-19",
            ...     next_14_end="2026-02-02",
            ...     current_date="2026-01-19"
            ... )
            >>> windows.is_in_next_14_days("2026-01-25")
            True
            >>> windows.is_in_next_14_days("2026-01-19")
            True
            >>> windows.is_in_next_14_days("2026-02-05")
            False
        """
        return self.next_14_start <= date_str <= self.next_14_end

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary format.

        Returns:
            Dictionary with all window fields

        Examples:
            >>> windows = DateWindows(
            ...     last_week_start="2026-01-12",
            ...     last_week_end="2026-01-18",
            ...     next_14_start="2026-01-19",
            ...     next_14_end="2026-02-02",
            ...     current_date="2026-01-19"
            ... )
            >>> data = windows.to_dict()
            >>> data["timezone"]
            'UTC'
        """
        return {
            "last_week_start": self.last_week_start,
            "last_week_end": self.last_week_end,
            "next_14_start": self.next_14_start,
            "next_14_end": self.next_14_end,
            "current_date": self.current_date,
            "timezone": self.timezone,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DateWindows":
        """Create DateWindows from dictionary.

        Args:
            data: Dictionary containing window fields

        Returns:
            DateWindows instance

        Examples:
            >>> data = {
            ...     "last_week_start": "2026-01-12",
            ...     "last_week_end": "2026-01-18",
            ...     "next_14_start": "2026-01-19",
            ...     "next_14_end": "2026-02-02",
            ...     "current_date": "2026-01-19",
            ...     "timezone": "UTC"
            ... }
            >>> windows = DateWindows.from_dict(data)
            >>> windows.timezone
            'UTC'
        """
        return cls(**data)

    def __repr__(self) -> str:
        """Return concise string representation."""
        return (
            f"DateWindows(last_week={self.last_week_start}..{self.last_week_end}, "
            f"next_14={self.next_14_start}..{self.next_14_end})"
        )
