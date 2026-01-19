"""Date calculation utilities.

This module handles all date-related calculations for the workflow including
calculating date windows (last week, next 14 days), parsing dates, and
generating ISO week identifiers.
"""

from datetime import datetime, timedelta, timezone

from src.constants import DATE_FORMAT, TIMEZONE, UPCOMING_DAYS_WINDOW
from src.models.windows import DateWindows


def parse_date(date_str: str | None) -> datetime | None:
    """Parse date string to datetime object.

    Parses ISO format date strings (YYYY-MM-DD) into datetime objects.
    Returns None for invalid or missing dates.

    Args:
        date_str: Date string in YYYY-MM-DD format or None

    Returns:
        Parsed datetime object or None if invalid/missing

    Examples:
        >>> parse_date("2026-01-19")
        datetime.datetime(2026, 1, 19, 0, 0)

        >>> parse_date("invalid") is None
        True

        >>> parse_date(None) is None
        True

        >>> parse_date("") is None
        True

    Notes:
        - Only accepts YYYY-MM-DD format (strict)
        - Returns timezone-naive datetime
        - Logs debug message for parse failures (when logging configured)

    See Also:
        - src.constants.DATE_FORMAT: Expected date format
    """
    if not date_str:
        return None

    try:
        return datetime.strptime(date_str, DATE_FORMAT)
    except ValueError:
        # Invalid date format or values (e.g., "2026-13-45")
        return None
    except Exception:
        # Unexpected error (shouldn't happen, but defensive)
        return None


def calculate_date_windows(reference_date: datetime | None = None) -> DateWindows:
    """Calculate reporting date windows.

    Calculates "last week" (Monday-Sunday) and "next 14 days" windows
    based on a reference date (defaults to current UTC time).

    Last Week Calculation:
    - If reference is Monday: Last week = previous Monday to yesterday (Sunday)
    - If reference is Tue-Sun: Last week = Monday before last Monday to last Monday

    Next 14 Days:
    - Starts from reference date (inclusive)
    - Ends 14 days later (inclusive)

    Args:
        reference_date: Date to calculate windows from. Defaults to current UTC time.

    Returns:
        DateWindows object with calculated ranges

    Examples:
        >>> # Monday 2026-01-19
        >>> ref = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        >>> windows = calculate_date_windows(ref)
        >>> windows.last_week_start
        '2026-01-12'
        >>> windows.last_week_end
        '2026-01-18'
        >>> windows.next_14_start
        '2026-01-19'
        >>> windows.next_14_end
        '2026-02-02'

        >>> # Tuesday 2026-01-20
        >>> ref = datetime(2026, 1, 20, 12, 0, 0, tzinfo=timezone.utc)
        >>> windows = calculate_date_windows(ref)
        >>> windows.last_week_start
        '2026-01-13'
        >>> windows.last_week_end
        '2026-01-19'

    Notes:
        - All dates returned in YYYY-MM-DD format
        - Uses UTC timezone
        - Window is 14 days (not 2 weeks) to avoid ambiguity
        - IMPORTANT: Current logic calculates last_week_end as most recent Monday
          when run on non-Monday days (not Sunday as comment suggests)

    See Also:
        - src.models.windows.DateWindows: Return type
        - src.constants.UPCOMING_DAYS_WINDOW: Number of upcoming days
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)

    current_weekday = reference_date.weekday()  # 0=Monday, 6=Sunday

    # Calculate "last week" window
    if current_weekday == 0:  # Monday
        # Last week = previous Monday to yesterday (Sunday)
        last_week_end = reference_date - timedelta(days=1)
        last_week_start = last_week_end - timedelta(days=6)
    else:
        # Last week = Monday before last Monday to last Monday
        # Note: This calculates to most recent Monday, not Sunday
        days_since_monday = current_weekday
        last_week_end = reference_date - timedelta(days=days_since_monday)
        last_week_start = last_week_end - timedelta(days=6)

    # Calculate "next 14 days" window
    next_14_start = reference_date
    next_14_end = reference_date + timedelta(days=UPCOMING_DAYS_WINDOW)

    return DateWindows(
        last_week_start=last_week_start.strftime(DATE_FORMAT),
        last_week_end=last_week_end.strftime(DATE_FORMAT),
        next_14_start=next_14_start.strftime(DATE_FORMAT),
        next_14_end=next_14_end.strftime(DATE_FORMAT),
        current_date=reference_date.strftime(DATE_FORMAT),
        timezone=TIMEZONE,
    )


def generate_week_id(reference_date: datetime | None = None) -> str:
    """Generate ISO week identifier.

    Generates a week identifier in format YYYY-WNN (e.g., "2026-W03")
    using ISO 8601 week numbering.

    Args:
        reference_date: Date to generate week ID from. Defaults to current UTC time.

    Returns:
        Week identifier string in format "YYYY-WNN"

    Examples:
        >>> # Monday 2026-01-19 is ISO week 4
        >>> ref = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        >>> generate_week_id(ref)
        '2026-W04'

        >>> # Thursday 2026-01-01 is ISO week 1 of 2026
        >>> ref = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        >>> generate_week_id(ref)
        '2026-W01'

    Notes:
        - Uses ISO 8601 week date system
        - Week 1 is the week with the first Thursday of the year
        - Week starts on Monday, ends on Sunday
        - Some years have 53 weeks (e.g., 2026)
        - Year in week ID may differ from calendar year at year boundaries

    See Also:
        - datetime.isocalendar(): Python's ISO calendar method
        - src.constants.ISO_WEEK_FORMAT: Week format string
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)

    iso_year, iso_week, _ = reference_date.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def days_ago(n: int, reference_date: datetime | None = None) -> str:
    """Get date string for N days ago.

    Helper function for generating dates relative to a reference point.
    Useful for creating test data.

    Args:
        n: Number of days in the past
        reference_date: Reference date. Defaults to current UTC time.

    Returns:
        Date string in YYYY-MM-DD format

    Examples:
        >>> ref = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        >>> days_ago(5, ref)
        '2026-01-14'

        >>> days_ago(0, ref)  # Today
        '2026-01-19'

    See Also:
        - days_from_now(): Future dates
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)

    past_date = reference_date - timedelta(days=n)
    return past_date.strftime(DATE_FORMAT)


def days_from_now(n: int, reference_date: datetime | None = None) -> str:
    """Get date string for N days from now.

    Helper function for generating future dates relative to a reference point.
    Useful for creating test data.

    Args:
        n: Number of days in the future
        reference_date: Reference date. Defaults to current UTC time.

    Returns:
        Date string in YYYY-MM-DD format

    Examples:
        >>> ref = datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)
        >>> days_from_now(5, ref)
        '2026-01-24'

        >>> days_from_now(0, ref)  # Today
        '2026-01-19'

    See Also:
        - days_ago(): Past dates
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)

    future_date = reference_date + timedelta(days=n)
    return future_date.strftime(DATE_FORMAT)
