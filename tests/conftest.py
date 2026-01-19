"""Shared pytest fixtures for test suite."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

# Add parent directory to path to import test_workflow
sys.path.insert(0, str(Path(__file__).parent.parent))

import test_workflow


@pytest.fixture
def sample_ticket_fe_deployed():
    """Frontend ticket deployed last week."""
    return {
        "key": "FE-101",
        "summary": "Implement new dashboard layout",
        "status": "Done",
        "component": "Frontend",
        "deployed_date": test_workflow.days_ago(5),
        "updated": test_workflow.days_ago(5),
        "epic": "Dashboard Redesign",
        "fix_version": "2026.1"
    }


@pytest.fixture
def sample_ticket_be_upcoming():
    """Backend ticket upcoming in next 14 days."""
    return {
        "key": "BE-204",
        "summary": "Add batch processing endpoint",
        "status": "Ready for Deploy",
        "component": "Backend",
        "target_deploy_date": test_workflow.days_from_now(2),
        "updated": test_workflow.days_ago(1),
        "epic": "API Enhancements",
        "fix_version": "2026.2"
    }


@pytest.fixture
def sample_ticket_blocked():
    """Blocked ticket (risk)."""
    return {
        "key": "BE-999",
        "summary": "Critical API issue",
        "status": "Blocked",
        "component": "Backend",
        "blocked_reason": "Waiting on third-party API",
        "updated": test_workflow.days_ago(3),
        "epic": "Integrations",
        "fix_version": "2026.1"
    }


@pytest.fixture
def sample_ticket_focus():
    """Focus item (In Progress)."""
    return {
        "key": "FE-109",
        "summary": "Redesign checkout flow",
        "status": "In Progress",
        "component": "Frontend",
        "updated": test_workflow.days_ago(1),
        "epic": "Checkout Revamp",
        "fix_version": "2026.3"
    }


@pytest.fixture
def sample_windows():
    """Sample date windows for testing."""
    return {
        "last_week_start": "2026-01-12",
        "last_week_end": "2026-01-18",
        "next_14_start": "2026-01-19",
        "next_14_end": "2026-02-02",
        "current_date": "2026-01-19",
        "timezone": "UTC"
    }


@pytest.fixture
def mock_today_monday():
    """Mock today as a Monday."""
    return datetime(2026, 1, 19, 12, 0, 0, tzinfo=timezone.utc)  # Monday


@pytest.fixture
def mock_today_tuesday():
    """Mock today as a Tuesday."""
    return datetime(2026, 1, 20, 12, 0, 0, tzinfo=timezone.utc)  # Tuesday


@pytest.fixture
def mock_today_sunday():
    """Mock today as a Sunday."""
    return datetime(2026, 1, 25, 12, 0, 0, tzinfo=timezone.utc)  # Sunday


@pytest.fixture
def mock_today_year_boundary():
    """Mock today at year boundary (Jan 1)."""
    return datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)  # Thursday
