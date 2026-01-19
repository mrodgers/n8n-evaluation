"""
Phase 1 Unit Tests: Core Logic

Tests for:
- Date calculation and window logic
- Ticket classification
- Filtering priority rules
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import test_workflow


# ============================================================
# Date Calculation Tests
# ============================================================

class TestCalculateDateWindows:
    """Test date window calculation logic."""

    def test_calculate_date_windows_monday(self, mock_today_monday):
        """When run on Monday, last_week_end should be yesterday (Sunday)."""
        with patch('test_workflow.today', mock_today_monday):
            windows = test_workflow.calculate_date_windows()

            # Monday 2026-01-19, so last week is Mon 1/12 - Sun 1/18
            assert windows["last_week_start"] == "2026-01-12"
            assert windows["last_week_end"] == "2026-01-18"
            assert windows["next_14_start"] == "2026-01-19"
            assert windows["next_14_end"] == "2026-02-02"
            assert windows["current_date"] == "2026-01-19"
            assert windows["timezone"] == "UTC"

    def test_calculate_date_windows_tuesday(self, mock_today_tuesday):
        """When run on Tuesday, last_week_end is most recent Monday."""
        with patch('test_workflow.today', mock_today_tuesday):
            windows = test_workflow.calculate_date_windows()

            # Tuesday 2026-01-20, last_week_end = 20 - 1 day = Monday 1/19
            # Note: Comment in code says "Last Sunday" but logic gives Monday
            assert windows["last_week_start"] == "2026-01-13"
            assert windows["last_week_end"] == "2026-01-19"
            assert windows["next_14_start"] == "2026-01-20"

    def test_calculate_date_windows_sunday(self, mock_today_sunday):
        """When run on Sunday, last_week_end is most recent Monday."""
        with patch('test_workflow.today', mock_today_sunday):
            windows = test_workflow.calculate_date_windows()

            # Sunday 2026-01-25 (weekday=6), last_week_end = 25 - 6 = Monday 1/19
            assert windows["last_week_start"] == "2026-01-13"
            assert windows["last_week_end"] == "2026-01-19"

    def test_calculate_date_windows_year_boundary(self, mock_today_year_boundary):
        """Test date calculation at year boundary."""
        with patch('test_workflow.today', mock_today_year_boundary):
            windows = test_workflow.calculate_date_windows()

            # Thursday 2026-01-01 (weekday=3), last_week_end = 1 - 3 = Monday 12/29
            assert windows["last_week_start"] == "2025-12-23"
            assert windows["last_week_end"] == "2025-12-29"
            assert windows["current_date"] == "2026-01-01"

    def test_next_14_days_calculation(self):
        """Verify next 14 days window is exactly 14 days from today."""
        windows = test_workflow.calculate_date_windows()

        next_14_start = datetime.strptime(windows["next_14_start"], '%Y-%m-%d')
        next_14_end = datetime.strptime(windows["next_14_end"], '%Y-%m-%d')

        # Should be exactly 14 days apart
        diff = (next_14_end - next_14_start).days
        assert diff == 14

    def test_last_week_is_7_days(self):
        """Verify last week window is exactly 7 days."""
        windows = test_workflow.calculate_date_windows()

        last_week_start = datetime.strptime(windows["last_week_start"], '%Y-%m-%d')
        last_week_end = datetime.strptime(windows["last_week_end"], '%Y-%m-%d')

        # Should be exactly 7 days (Monday to Sunday inclusive)
        diff = (last_week_end - last_week_start).days
        assert diff == 6  # 6 days difference = 7 days inclusive


class TestGenerateWeekId:
    """Test ISO week ID generation."""

    def test_generate_week_id_format(self):
        """Week ID should be in format YYYY-WNN."""
        week_id = test_workflow.generate_week_id()

        assert isinstance(week_id, str)
        assert len(week_id) >= 8  # "2026-W01"
        assert "-W" in week_id

        # Check format with regex-like validation
        parts = week_id.split("-W")
        assert len(parts) == 2
        assert parts[0].isdigit()  # Year
        assert parts[1].isdigit()  # Week number

    def test_generate_week_id_monday(self, mock_today_monday):
        """Week ID for Monday 2026-01-19 should be 2026-W04."""
        with patch('test_workflow.today', mock_today_monday):
            week_id = test_workflow.generate_week_id()
            # 2026-01-19 is ISO week 4
            assert week_id == "2026-W04"

    def test_generate_week_id_year_boundary(self, mock_today_year_boundary):
        """Week ID at year boundary should handle ISO week correctly."""
        with patch('test_workflow.today', mock_today_year_boundary):
            week_id = test_workflow.generate_week_id()
            # 2026-01-01 is Thursday, should be week 1 of 2026
            assert week_id == "2026-W01"


# ============================================================
# Ticket Classification Tests
# ============================================================

class TestClassifyTicket:
    """Test ticket classification logic."""

    def test_classify_ticket_component_frontend(self):
        """Component 'Frontend' should classify as FE."""
        ticket = {"key": "ANY-123", "component": "Frontend"}
        assert test_workflow.classify_ticket(ticket) == "FE"

    def test_classify_ticket_component_backend(self):
        """Component 'Backend' should classify as BE."""
        ticket = {"key": "ANY-123", "component": "Backend"}
        assert test_workflow.classify_ticket(ticket) == "BE"

    def test_classify_ticket_component_priority_over_key(self):
        """Component field should override key prefix."""
        ticket = {"key": "FE-123", "component": "Backend"}
        assert test_workflow.classify_ticket(ticket) == "BE"

        ticket2 = {"key": "BE-456", "component": "Frontend"}
        assert test_workflow.classify_ticket(ticket2) == "FE"

    def test_classify_ticket_key_fallback_fe(self):
        """Key prefix 'FE-' should be used when component is None."""
        ticket = {"key": "FE-123", "component": None}
        assert test_workflow.classify_ticket(ticket) == "FE"

    def test_classify_ticket_key_fallback_be(self):
        """Key prefix 'BE-' should be used when component is None."""
        ticket = {"key": "BE-456", "component": None}
        assert test_workflow.classify_ticket(ticket) == "BE"

    def test_classify_ticket_no_component_field(self):
        """Missing component field should fall back to key."""
        ticket = {"key": "FE-789"}
        assert test_workflow.classify_ticket(ticket) == "FE"

    def test_classify_ticket_uncategorized(self):
        """Non-standard keys without component should return Uncategorized."""
        ticket = {"key": "OPS-123", "component": None}
        assert test_workflow.classify_ticket(ticket) == "Uncategorized"

        ticket2 = {"key": "DATA-456"}
        assert test_workflow.classify_ticket(ticket2) == "Uncategorized"

    def test_classify_ticket_missing_key(self):
        """Missing key should return Uncategorized."""
        ticket = {"component": None}
        assert test_workflow.classify_ticket(ticket) == "Uncategorized"

    def test_classify_ticket_empty_key(self):
        """Empty key should return Uncategorized."""
        ticket = {"key": "", "component": None}
        assert test_workflow.classify_ticket(ticket) == "Uncategorized"


# ============================================================
# Date Parsing Tests
# ============================================================

class TestParseDate:
    """Test date parsing logic."""

    def test_parse_date_valid(self):
        """Valid date string should parse correctly."""
        result = test_workflow.parse_date("2026-01-19")
        assert result is not None
        assert isinstance(result, datetime)
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 19

    def test_parse_date_invalid_format(self):
        """Invalid date format should return None."""
        assert test_workflow.parse_date("01/19/2026") is None
        assert test_workflow.parse_date("invalid") is None
        assert test_workflow.parse_date("not-a-date") is None
        assert test_workflow.parse_date("2026-13-45") is None  # Invalid month/day

    def test_parse_date_none(self):
        """None input should return None."""
        assert test_workflow.parse_date(None) is None

    def test_parse_date_empty_string(self):
        """Empty string should return None."""
        assert test_workflow.parse_date("") is None

    def test_parse_date_whitespace(self):
        """Whitespace should return None."""
        assert test_workflow.parse_date("   ") is None


# ============================================================
# Filtering and Categorization Tests
# ============================================================

class TestFilterAndCategorize:
    """Test filtering and categorization logic."""

    def test_blocked_takes_priority_over_deployed(self, sample_windows):
        """Blocked tickets should go to risks_blocks even if Done."""
        tickets = [
            {
                "key": "BE-1",
                "status": "Done",
                "component": "Backend",
                "blocked_reason": "API issue",
                "deployed_date": "2026-01-15",  # Would be deployed last week
                "updated": "2026-01-15"
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["risks_blocks"]) == 1
        assert len(buckets["be_deployed"]) == 0
        assert buckets["risks_blocks"][0]["key"] == "BE-1"

    def test_blocked_status_takes_priority(self, sample_windows):
        """Status 'Blocked' should prioritize to risks_blocks."""
        tickets = [
            {
                "key": "FE-2",
                "status": "Blocked",
                "component": "Frontend",
                "updated": "2026-01-19"
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["risks_blocks"]) == 1
        assert buckets["risks_blocks"][0]["key"] == "FE-2"

    def test_deployed_last_week_fe(self, sample_windows):
        """Frontend tickets deployed last week should go to fe_deployed."""
        tickets = [
            {
                "key": "FE-101",
                "status": "Done",
                "component": "Frontend",
                "deployed_date": "2026-01-15",  # Within last week window
                "updated": "2026-01-15"
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["fe_deployed"]) == 1
        assert buckets["fe_deployed"][0]["key"] == "FE-101"

    def test_deployed_last_week_be(self, sample_windows):
        """Backend tickets deployed last week should go to be_deployed."""
        tickets = [
            {
                "key": "BE-201",
                "status": "Done",
                "component": "Backend",
                "deployed_date": "2026-01-15",
                "updated": "2026-01-15"
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["be_deployed"]) == 1
        assert buckets["be_deployed"][0]["key"] == "BE-201"

    def test_deployed_uses_updated_fallback(self, sample_windows):
        """Should use 'updated' field when 'deployed_date' is None."""
        tickets = [
            {
                "key": "FE-104",
                "status": "Done",
                "component": "Frontend",
                "deployed_date": None,
                "updated": "2026-01-16"  # Within last week
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["fe_deployed"]) == 1
        assert buckets["fe_deployed"][0]["key"] == "FE-104"

    def test_deployed_outside_window_not_included(self, sample_windows):
        """Done tickets outside last week window should go to uncategorized."""
        tickets = [
            {
                "key": "FE-999",
                "status": "Done",
                "component": "Frontend",
                "deployed_date": "2026-01-01",  # Too old
                "updated": "2026-01-01"
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["fe_deployed"]) == 0
        # Note: This ticket doesn't match any other criteria, so goes to uncategorized
        assert len(buckets["uncategorized"]) == 1

    def test_upcoming_fe_ready_for_deploy(self, sample_windows):
        """FE tickets Ready for Deploy in next 14 days go to fe_upcoming."""
        tickets = [
            {
                "key": "FE-105",
                "status": "Ready for Deploy",
                "component": "Frontend",
                "target_deploy_date": "2026-01-22",  # Within next 14 days
                "fix_version": "2026.2"
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["fe_upcoming"]) == 1
        assert buckets["fe_upcoming"][0]["key"] == "FE-105"

    def test_upcoming_be_in_qa(self, sample_windows):
        """BE tickets In QA with target date go to be_upcoming."""
        tickets = [
            {
                "key": "BE-205",
                "status": "In QA",
                "component": "Backend",
                "target_deploy_date": "2026-01-24",  # Within next 14 days
                "fix_version": "2026.2"
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["be_upcoming"]) == 1
        assert buckets["be_upcoming"][0]["key"] == "BE-205"

    def test_upcoming_with_fix_version_fallback(self, sample_windows):
        """Upcoming tickets without target_deploy_date but with fix_version should be included."""
        tickets = [
            {
                "key": "FE-107",
                "status": "Ready for Deploy",
                "component": "Frontend",
                "target_deploy_date": None,
                "fix_version": "2026.2"  # Fallback to fix_version
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["fe_upcoming"]) == 1
        assert buckets["fe_upcoming"][0]["key"] == "FE-107"

    def test_upcoming_outside_window_not_included(self, sample_windows):
        """Tickets with target date outside next 14 days should go to uncategorized."""
        tickets = [
            {
                "key": "FE-999",
                "status": "Ready for Deploy",
                "component": "Frontend",
                "target_deploy_date": "2026-03-01",  # Too far in future
                "fix_version": None  # No fallback
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["fe_upcoming"]) == 0
        assert len(buckets["uncategorized"]) == 1

    def test_focus_items_in_progress(self, sample_windows):
        """In Progress tickets should go to focus_items."""
        tickets = [
            {
                "key": "FE-109",
                "status": "In Progress",
                "component": "Frontend",
                "epic": "Checkout Revamp"
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["focus_items"]) == 1
        assert buckets["focus_items"][0]["epic"] == "Checkout Revamp"
        assert len(buckets["focus_items"][0]["tickets"]) == 1
        assert buckets["focus_items"][0]["tickets"][0]["key"] == "FE-109"

    def test_focus_items_to_do(self, sample_windows):
        """To Do tickets should go to focus_items."""
        tickets = [
            {
                "key": "FE-110",
                "status": "To Do",
                "component": "Frontend",
                "epic": "A/B Testing"
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["focus_items"]) == 1
        assert buckets["focus_items"][0]["epic"] == "A/B Testing"

    def test_focus_items_grouped_by_epic(self, sample_windows):
        """Focus items should be grouped by epic."""
        tickets = [
            {
                "key": "FE-109",
                "status": "In Progress",
                "component": "Frontend",
                "epic": "Checkout Revamp"
            },
            {
                "key": "BE-207",
                "status": "In Progress",
                "component": "Backend",
                "epic": "Checkout Revamp"
            },
            {
                "key": "FE-110",
                "status": "To Do",
                "component": "Frontend",
                "epic": "A/B Testing"
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["focus_items"]) == 2  # Two epics

        # Find the Checkout Revamp epic
        checkout_epic = [e for e in buckets["focus_items"] if e["epic"] == "Checkout Revamp"][0]
        assert len(checkout_epic["tickets"]) == 2

    def test_focus_items_no_epic_goes_to_other(self, sample_windows):
        """Focus items without epic should go to 'Other Focus Items'."""
        tickets = [
            {
                "key": "FE-111",
                "status": "In Progress",
                "component": "Frontend",
                "epic": None
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["focus_items"]) == 1
        assert buckets["focus_items"][0]["epic"] == "Other Focus Items"

    def test_no_duplicate_categorization(self, sample_windows):
        """Tickets should only appear in one bucket."""
        tickets = [
            {
                "key": "FE-1",
                "status": "Blocked",
                "component": "Frontend",
                "blocked_reason": "Issue",
                "deployed_date": "2026-01-15"  # Could match deployed
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        # Should only be in risks_blocks
        assert len(buckets["risks_blocks"]) == 1
        assert len(buckets["fe_deployed"]) == 0

    def test_empty_ticket_list(self, sample_windows):
        """Empty ticket list should return empty buckets."""
        buckets = test_workflow.filter_and_categorize([], sample_windows)

        assert len(buckets["fe_deployed"]) == 0
        assert len(buckets["be_deployed"]) == 0
        assert len(buckets["fe_upcoming"]) == 0
        assert len(buckets["be_upcoming"]) == 0
        assert len(buckets["focus_items"]) == 0
        assert len(buckets["risks_blocks"]) == 0
        assert len(buckets["uncategorized"]) == 0

    def test_uncategorized_classification(self, sample_windows):
        """Tickets with uncategorized classification should go to uncategorized bucket."""
        tickets = [
            {
                "key": "OPS-1",
                "status": "Done",
                "component": None,  # Will classify as Uncategorized
                "deployed_date": "2026-01-15"
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, sample_windows)

        assert len(buckets["uncategorized"]) == 1
        assert buckets["uncategorized"][0]["key"] == "OPS-1"


# ============================================================
# Integration: Full Flow Tests
# ============================================================

class TestIntegrationCoreFlow:
    """Test core flow integration."""

    def test_full_categorization_flow(self):
        """Test complete flow with multiple tickets."""
        windows = test_workflow.calculate_date_windows()

        tickets = [
            # Deployed last week
            {
                "key": "FE-1",
                "status": "Done",
                "component": "Frontend",
                "deployed_date": test_workflow.days_ago(5),
                "updated": test_workflow.days_ago(5)
            },
            # Upcoming
            {
                "key": "BE-2",
                "status": "Ready for Deploy",
                "component": "Backend",
                "target_deploy_date": test_workflow.days_from_now(3),
                "fix_version": "2026.2"
            },
            # Focus item
            {
                "key": "FE-3",
                "status": "In Progress",
                "component": "Frontend",
                "epic": "Epic 1"
            },
            # Blocked
            {
                "key": "BE-4",
                "status": "Blocked",
                "component": "Backend"
            }
        ]

        buckets = test_workflow.filter_and_categorize(tickets, windows)

        # Verify each ticket went to correct bucket
        assert len(buckets["fe_deployed"]) == 1
        assert len(buckets["be_upcoming"]) == 1
        assert len(buckets["focus_items"]) == 1
        assert len(buckets["risks_blocks"]) == 1

        # Verify no duplicates
        total_tickets = (
            len(buckets["fe_deployed"]) +
            len(buckets["be_deployed"]) +
            len(buckets["fe_upcoming"]) +
            len(buckets["be_upcoming"]) +
            sum(len(epic["tickets"]) for epic in buckets["focus_items"]) +
            len(buckets["risks_blocks"]) +
            len(buckets["uncategorized"])
        )
        assert total_tickets == 4
