# Code Review and Modernization Plan
**Purpose**: Transform codebase into a best-practice training repository for engineers and PMs learning n8n workflows

**Target Audience**: Junior/Mid engineers and Product Managers new to n8n
**Timeline**: 3-4 weeks
**Current State**: Functional but needs modernization for training/educational use

---

## Executive Summary

The current codebase is functional and includes good test coverage (Phase 1), but lacks modern Python practices, proper code organization, and educational scaffolding needed for a training repository. This plan outlines a comprehensive modernization approach focusing on:

1. **Code Quality**: Add type hints, improve error handling, reduce complexity
2. **Structure**: Refactor monolithic files into modules
3. **Documentation**: Add inline examples, tutorials, and learning paths
4. **Best Practices**: Demonstrate modern Python patterns and n8n best practices
5. **Usability**: Create clear entry points and progressive complexity

---

## Current State Analysis

### Strengths ✅
- Comprehensive test coverage (41 unit tests)
- Good documentation files (README, ASSUMPTIONS, QA_Test_Plan)
- Working workflow simulation
- Clear node structure mapping

### Issues to Address ❌

#### 1. **Code Organization**
- **Issue**: Single 1,831-line file (test_workflow.py)
- **Impact**: Hard to navigate, understand, and maintain
- **Priority**: HIGH

#### 2. **Type Safety**
- **Issue**: No type hints anywhere
- **Impact**: Harder to understand function contracts, no IDE support
- **Priority**: HIGH

#### 3. **Global State**
- **Issue**: Global `today` variable (line 14)
- **Impact**: Makes testing harder, violates best practices
- **Priority**: MEDIUM

#### 4. **Error Handling**
- **Issue**: Minimal error handling, bare `except` clauses
- **Impact**: Silent failures, poor debugging experience
- **Priority**: HIGH

#### 5. **Magic Values**
- **Issue**: Hardcoded strings, numbers throughout
- **Impact**: Hard to maintain, unclear meaning
- **Priority**: MEDIUM

#### 6. **Code Duplication**
- **Issue**: Repetitive formatting code, similar patterns
- **Impact**: Harder to maintain, inconsistencies
- **Priority**: MEDIUM

#### 7. **Documentation Gaps**
- **Issue**: Limited inline comments, no code examples
- **Impact**: Hard for newcomers to learn
- **Priority**: HIGH (for training repo)

#### 8. **Modern Python Features**
- **Issue**: Not using dataclasses, enums, pathlib, etc.
- **Impact**: Missed teaching opportunities
- **Priority**: MEDIUM

---

## Detailed Code Review Issues

### Issue #1: Monolithic File Structure

**Current**: All code in test_workflow.py (1,831 lines)

**Problems**:
- Hard to navigate
- Tight coupling
- Cannot easily reuse components
- Violates Single Responsibility Principle

**Recommendation**: Split into modular structure

```
src/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── ticket.py          # Ticket dataclass
│   ├── buckets.py         # Bucket dataclass
│   └── windows.py         # DateWindows dataclass
├── core/
│   ├── __init__.py
│   ├── date_utils.py      # Date calculations
│   ├── classifier.py      # Ticket classification
│   └── categorizer.py     # Filtering & categorization
├── formatters/
│   ├── __init__.py
│   ├── base.py            # Base formatter interface
│   ├── confluence.py      # Markdown formatter
│   └── slides.py          # Slide formatter
├── n8n/
│   ├── __init__.py
│   └── workflow_gen.py    # Workflow JSON generation
├── mock/
│   ├── __init__.py
│   └── jira_data.py       # Mock data generator
└── config.py              # Configuration constants

examples/
├── __init__.py
├── 01_basic_classification.py
├── 02_date_windows.py
├── 03_formatters.py
└── 04_full_workflow.py

scripts/
├── run_workflow.py        # Main entry point
├── generate_mock_data.py
└── validate_outputs.py
```

**Benefits**:
- Clear separation of concerns
- Easier to find and understand code
- Reusable components
- Better for teaching modular design

---

### Issue #2: Missing Type Hints

**Current**: No type hints

```python
# Current
def classify_ticket(ticket):
    """Classify ticket as FE, BE, or Uncategorized."""
    component = ticket.get("component")
    key = ticket.get("key", "")
    # ...
```

**Recommended**:

```python
from typing import Dict, Any, Literal

TicketClassification = Literal["FE", "BE", "Uncategorized"]

def classify_ticket(ticket: Dict[str, Any]) -> TicketClassification:
    """Classify ticket as FE, BE, or Uncategorized.

    Args:
        ticket: Dictionary containing ticket data with 'component' and 'key'

    Returns:
        Classification as "FE", "BE", or "Uncategorized"

    Examples:
        >>> classify_ticket({"key": "FE-123", "component": "Frontend"})
        'FE'
        >>> classify_ticket({"key": "BE-456", "component": None})
        'Uncategorized'
    """
    component: str | None = ticket.get("component")
    key: str = ticket.get("key", "")
    # ...
```

**Benefits**:
- IDE autocomplete
- Type checking with mypy
- Self-documenting code
- Catches bugs at development time
- Great teaching tool for type systems

---

### Issue #3: Global State

**Current**:
```python
# Line 14 - Global mutable state
today = datetime.now(timezone.utc)

def calculate_date_windows():
    current_weekday = today.weekday()  # Uses global
    # ...
```

**Problems**:
- Makes testing harder (we had to mock it)
- Not obvious where the value comes from
- Violates dependency injection principle
- Time-dependent code is fragile

**Recommended**:

```python
# Option 1: Dependency injection
def calculate_date_windows(reference_date: datetime | None = None) -> DateWindows:
    """Calculate reporting windows.

    Args:
        reference_date: Date to calculate windows from. Defaults to current UTC time.

    Returns:
        DateWindows object with last_week and next_14_days ranges
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)

    current_weekday = reference_date.weekday()
    # ...

# Option 2: Use a Clock abstraction
class Clock:
    """Abstraction for time to enable testing."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

class MockClock(Clock):
    """Test clock with fixed time."""

    def __init__(self, fixed_time: datetime):
        self._time = fixed_time

    def now(self) -> datetime:
        return self._time
```

**Benefits**:
- Testable without mocking
- Explicit dependencies
- Teaches dependency injection
- More flexible

---

### Issue #4: Weak Error Handling

**Current**:
```python
def parse_date(date_str):
    """Parse date string to datetime."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:  # ⚠️ Bare except
        return None
```

**Problems**:
- Bare `except` catches everything (KeyboardInterrupt, SystemExit)
- Silent failures
- No logging
- Hard to debug

**Recommended**:

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def parse_date(date_str: str | None) -> Optional[datetime]:
    """Parse date string to datetime.

    Args:
        date_str: Date in YYYY-MM-DD format or None

    Returns:
        Parsed datetime object or None if invalid

    Examples:
        >>> parse_date("2026-01-19")
        datetime.datetime(2026, 1, 19, 0, 0)
        >>> parse_date("invalid")
        None
        >>> parse_date(None)
        None
    """
    if not date_str:
        return None

    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError as e:
        logger.debug(f"Failed to parse date '{date_str}': {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing date '{date_str}': {e}")
        return None
```

**Benefits**:
- Explicit exception types
- Logging for debugging
- Teaches proper error handling
- Production-ready pattern

---

### Issue #5: Magic Values

**Current**: Scattered throughout
```python
# Line 359-362
if component == "Frontend":  # ⚠️ Magic string
    return "FE"
elif component == "Backend":  # ⚠️ Magic string
    return "BE"

# Line 424
if status in ["Ready for Deploy", "In QA"]:  # ⚠️ Magic strings
```

**Recommended**:

```python
from enum import Enum
from typing import Final

# config.py or constants.py
class Component(str, Enum):
    """Jira ticket component types."""
    FRONTEND = "Frontend"
    BACKEND = "Backend"

class TicketStatus(str, Enum):
    """Jira ticket status values."""
    DONE = "Done"
    BLOCKED = "Blocked"
    READY_FOR_DEPLOY = "Ready for Deploy"
    IN_QA = "In QA"
    IN_PROGRESS = "In Progress"
    TO_DO = "To Do"

class Classification(str, Enum):
    """Ticket classification for reporting."""
    FE = "FE"
    BE = "BE"
    UNCATEGORIZED = "Uncategorized"

# Usage
def classify_ticket(ticket: Dict[str, Any]) -> Classification:
    """Classify ticket as FE, BE, or Uncategorized."""
    component = ticket.get("component")

    if component == Component.FRONTEND.value:
        return Classification.FE
    elif component == Component.BACKEND.value:
        return Classification.BE

    # Fallback to key prefix
    key = ticket.get("key", "")
    if key.startswith("FE-"):
        return Classification.FE
    elif key.startswith("BE-"):
        return Classification.BE

    return Classification.UNCATEGORIZED
```

**Benefits**:
- Single source of truth
- IDE autocomplete
- Type safety
- Easy to update
- Self-documenting

---

### Issue #6: Complex Functions

**Current**: `generate_mock_jira_data()` is 300+ lines of ticket dictionaries

**Problems**:
- Hard to read
- Hard to maintain
- Duplicate structure
- Not reusable

**Recommended**:

```python
# models/ticket.py
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class JiraTicket:
    """Represents a Jira ticket.

    Attributes:
        key: Unique ticket identifier (e.g., "FE-101")
        summary: Brief description of the ticket
        status: Current status (Done, In Progress, etc.)
        component: Frontend, Backend, or None
        deployed_date: When the ticket was deployed
        updated: Last update timestamp
        epic: Epic name or None
        fix_version: Target fix version or None
        target_deploy_date: Planned deployment date or None
        blocked_reason: Reason if blocked, None otherwise
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization."""
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
    def from_dict(cls, data: Dict[str, Any]) -> 'JiraTicket':
        """Create ticket from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

# mock/ticket_builder.py
class TicketBuilder:
    """Builder pattern for creating test tickets."""

    def __init__(self):
        self._ticket = {}

    def with_key(self, key: str) -> 'TicketBuilder':
        self._ticket["key"] = key
        return self

    def frontend(self) -> 'TicketBuilder':
        self._ticket["component"] = "Frontend"
        return self

    def backend(self) -> 'TicketBuilder':
        self._ticket["component"] = "Backend"
        return self

    def done(self) -> 'TicketBuilder':
        self._ticket["status"] = "Done"
        return self

    def deployed_days_ago(self, days: int) -> 'TicketBuilder':
        self._ticket["deployed_date"] = days_ago(days)
        self._ticket["updated"] = days_ago(days)
        return self

    def build(self) -> JiraTicket:
        return JiraTicket.from_dict(self._ticket)

# Usage - much cleaner!
def generate_frontend_deployed_tickets() -> List[JiraTicket]:
    """Generate Frontend tickets deployed last week."""
    return [
        TicketBuilder()
            .with_key("FE-101")
            .frontend()
            .done()
            .deployed_days_ago(5)
            .build(),

        TicketBuilder()
            .with_key("FE-102")
            .frontend()
            .done()
            .deployed_days_ago(6)
            .build(),
    ]
```

**Benefits**:
- Type-safe data structures
- Reusable builder pattern
- Much more readable
- Easy to extend
- Great teaching example

---

### Issue #7: Documentation Gaps

**Current**: Minimal inline documentation

**Recommended**: Add comprehensive docstrings and examples

```python
def filter_and_categorize(
    tickets: List[JiraTicket],
    windows: DateWindows
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
        tickets: List of Jira tickets to categorize
        windows: Date windows defining "last week" and "next 14 days"

    Returns:
        CategorizationResult with tickets sorted into 7 buckets

    Examples:
        >>> # Setup
        >>> windows = DateWindows(
        ...     last_week_start="2026-01-12",
        ...     last_week_end="2026-01-18"
        ... )
        >>>
        >>> # Deployed ticket
        >>> tickets = [
        ...     JiraTicket(
        ...         key="FE-101",
        ...         status="Done",
        ...         component="Frontend",
        ...         deployed_date="2026-01-15"
        ...     )
        ... ]
        >>> result = filter_and_categorize(tickets, windows)
        >>> len(result.fe_deployed)
        1
        >>>
        >>> # Blocked ticket takes priority
        >>> blocked = [
        ...     JiraTicket(
        ...         key="BE-999",
        ...         status="Blocked",
        ...         component="Backend",
        ...         deployed_date="2026-01-15"  # Would be "deployed"
        ...     )
        ... ]
        >>> result = filter_and_categorize(blocked, windows)
        >>> len(result.risks_blocks)
        1
        >>> len(result.be_deployed)  # Not in deployed!
        0

    Notes:
        - Tickets only appear in ONE bucket (first match wins)
        - Blocked status/blocked_reason takes highest priority
        - Missing deployed_date falls back to updated field
        - Missing epic for focus items → "Other Focus Items"

    See Also:
        - classify_ticket(): Determines FE vs BE vs Uncategorized
        - DateWindows: Date range definitions
        - examples/02_categorization.py: Full examples
    """
    # Implementation...
```

**Benefits**:
- Comprehensive learning resource
- Inline examples
- Clear algorithms
- Links to related code
- Production-quality docs

---

### Issue #8: No Configuration Management

**Current**: Values scattered throughout code

**Recommended**: Centralized configuration

```python
# config.py
from dataclasses import dataclass
from pathlib import Path
from typing import Final

@dataclass(frozen=True)
class Paths:
    """File paths for the workflow."""
    PROJECT_ROOT: Path = Path(__file__).parent
    OUTPUTS: Path = PROJECT_ROOT / "outputs"
    MOCKDATA: Path = PROJECT_ROOT / "mockdata"
    WORKFLOWS: Path = PROJECT_ROOT / "workflows"

    # Output subdirectories
    CONFLUENCE: Path = OUTPUTS / "confluence"
    SLIDES: Path = OUTPUTS / "slides"

    def ensure_directories(self) -> None:
        """Create all necessary directories."""
        for path in [self.OUTPUTS, self.MOCKDATA, self.CONFLUENCE, self.SLIDES]:
            path.mkdir(parents=True, exist_ok=True)

@dataclass(frozen=True)
class WorkflowConfig:
    """Configuration for the workflow."""

    # Date settings
    TIMEZONE: str = "UTC"
    DATE_FORMAT: str = "%Y-%m-%d"
    WEEK_ID_FORMAT: str = "%Y-W%W"

    # File formats
    CONFLUENCE_FILENAME_PATTERN: str = "week-{week}.md"
    SLIDES_FILENAME_PATTERN: str = "{year}-{week}.txt"

    # Categorization
    UPCOMING_DAYS: int = 14

    # Mock data
    MOCK_TICKET_COUNT: int = 28

# Usage
config = WorkflowConfig()
paths = Paths()
```

**Benefits**:
- Single source of truth
- Easy to modify
- Environment-specific configs
- Type-safe configuration
- Teaching best practices

---

### Issue #9: Testing Structure

**Current**: Tests separate from source

**Recommended**: Better integration

```
src/
├── core/
│   ├── classifier.py
│   └── classifier_test.py      # ⭐ Co-located tests
├── formatters/
│   ├── confluence.py
│   └── confluence_test.py

tests/
├── integration/
│   ├── test_full_workflow.py
│   └── test_n8n_simulation.py
├── fixtures/
│   ├── sample_tickets.json
│   └── expected_outputs.json
└── conftest.py
```

**Benefits**:
- Tests closer to code
- Clear unit vs integration split
- Easier to find tests
- Better organization

---

## Modernization Roadmap

### Phase 1: Foundation (Week 1) 🔨

**Goal**: Set up modern Python infrastructure

#### Tasks:
1. Add type hints to all functions
   - Install mypy: `pip install mypy`
   - Create `mypy.ini` config
   - Add types incrementally
   - Goal: 100% typed

2. Add linting/formatting
   - Install tools: `pip install ruff black isort`
   - Create `pyproject.toml` config
   - Set up pre-commit hooks
   - Format all existing code

3. Set up project structure
   - Create `src/` directory
   - Create `examples/` directory
   - Update imports

4. Add dataclasses for all data structures
   - JiraTicket
   - DateWindows
   - CategorizationResult
   - FormatterConfig

**Deliverables**:
- Fully typed codebase
- Formatted with black/ruff
- Type checking passes
- Core data models defined

---

### Phase 2: Refactoring (Week 2) 🔧

**Goal**: Break up monolithic file, improve code quality

#### Tasks:
1. Extract modules
   - `src/models/` - Data classes
   - `src/core/` - Business logic
   - `src/formatters/` - Output generators
   - `src/mock/` - Test data
   - `src/n8n/` - Workflow generation

2. Remove global state
   - Make `today` injectable
   - Use dependency injection pattern
   - Update all tests

3. Add configuration management
   - Create `config.py`
   - Extract all constants
   - Use enums for fixed values

4. Improve error handling
   - Add logging throughout
   - Replace bare excepts
   - Add custom exceptions
   - Document error cases

**Deliverables**:
- Modular codebase
- No global state
- Proper error handling
- All tests still passing

---

### Phase 3: Documentation (Week 3) 📚

**Goal**: Create comprehensive learning resources

#### Tasks:
1. Enhance docstrings
   - Add examples to all functions
   - Document algorithms
   - Add "See Also" sections
   - Include complexity notes

2. Create progressive examples
   - `01_basic_classification.py` - Simple ticket classification
   - `02_date_windows.py` - Date calculations
   - `03_filtering.py` - Categorization logic
   - `04_formatters.py` - Output generation
   - `05_full_workflow.py` - Complete workflow
   - `06_custom_n8n.py` - Building custom workflows

3. Add architecture documentation
   - `docs/ARCHITECTURE.md` - System overview
   - `docs/DATA_FLOW.md` - Data transformation pipeline
   - `docs/TESTING_GUIDE.md` - How to write tests
   - `docs/N8N_PATTERNS.md` - n8n best practices

4. Create tutorial walkthrough
   - `docs/TUTORIAL.md` - Step-by-step guide
   - Include diagrams
   - Link to examples
   - Add exercises

**Deliverables**:
- Comprehensive docstrings
- 6 progressive examples
- 4 architecture docs
- Complete tutorial

---

### Phase 4: Polish (Week 4) ✨

**Goal**: Production-ready training repository

#### Tasks:
1. Add advanced features
   - CLI with click/typer
   - Configuration via environment variables
   - Proper logging setup
   - Performance optimization

2. Enhance test suite
   - Add property-based tests
   - Add regression tests
   - Add integration tests
   - Achieve 80%+ coverage

3. Create learning assessment
   - Quiz questions
   - Coding exercises
   - Real-world scenarios
   - Solutions with explanations

4. Polish for training
   - Add troubleshooting guide
   - Create FAQ
   - Add glossary
   - Record video walkthrough (optional)

**Deliverables**:
- Production-ready CLI
- 80%+ test coverage
- Learning exercises
- Complete training package

---

## Specific Code Improvements

### 1. Add Logging

```python
# Before
def filter_and_categorize(tickets, windows):
    buckets = {...}
    for ticket in tickets:
        # Silent processing
        pass
    return buckets

# After
import logging
logger = logging.getLogger(__name__)

def filter_and_categorize(
    tickets: List[JiraTicket],
    windows: DateWindows
) -> CategorizationResult:
    """Categorize tickets into buckets."""
    logger.info(f"Categorizing {len(tickets)} tickets")

    buckets = CategorizationResult()
    processed = 0

    for ticket in tickets:
        bucket = _categorize_single_ticket(ticket, windows)
        buckets.add(ticket, bucket)
        processed += 1

        if processed % 100 == 0:
            logger.debug(f"Processed {processed}/{len(tickets)} tickets")

    logger.info(f"Categorization complete: {buckets.summary()}")
    return buckets
```

### 2. Add Validation

```python
from pydantic import BaseModel, Field, validator

class JiraTicketSchema(BaseModel):
    """Validated Jira ticket schema."""

    key: str = Field(..., regex=r"^[A-Z]+-\d+$")
    summary: str = Field(..., min_length=1, max_length=500)
    status: str
    component: Optional[str] = None
    deployed_date: Optional[str] = None
    updated: Optional[str] = None

    @validator('deployed_date', 'updated')
    def validate_date_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError(f"Date must be in YYYY-MM-DD format, got: {v}")

    class Config:
        extra = 'forbid'  # Reject unknown fields

# Usage
def load_tickets(data: List[Dict]) -> List[JiraTicket]:
    """Load and validate tickets from raw data."""
    validated = []
    errors = []

    for i, item in enumerate(data):
        try:
            schema = JiraTicketSchema(**item)
            validated.append(JiraTicket.from_dict(schema.dict()))
        except ValidationError as e:
            errors.append(f"Ticket {i}: {e}")

    if errors:
        logger.warning(f"Found {len(errors)} validation errors")
        for error in errors[:5]:  # Show first 5
            logger.warning(error)

    return validated
```

### 3. Add Performance Monitoring

```python
import time
from functools import wraps

def timed(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        logger.info(f"{func.__name__} took {duration:.3f}s")
        return result
    return wrapper

@timed
def filter_and_categorize(tickets, windows):
    """Categorize tickets (now with timing)."""
    # Implementation...
```

### 4. Add CLI Interface

```python
# scripts/cli.py
import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
def cli():
    """Weekly Deployment Update - n8n Workflow Simulation."""
    pass

@cli.command()
@click.option('--date', help='Reference date (YYYY-MM-DD)')
@click.option('--output-dir', type=click.Path(), default='outputs')
@click.option('--verbose', '-v', is_flag=True)
def run(date, output_dir, verbose):
    """Run the workflow simulation."""
    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    console.print("[bold green]Starting workflow...[/bold green]")

    # Run workflow
    result = execute_workflow(date=date, output_dir=output_dir)

    # Display results
    table = Table(title="Categorization Results")
    table.add_column("Bucket", style="cyan")
    table.add_column("Count", justify="right", style="magenta")

    for bucket, count in result.summary().items():
        table.add_row(bucket, str(count))

    console.print(table)
    console.print(f"\n✅ Outputs written to {output_dir}")

@cli.command()
def validate():
    """Validate environment and configuration."""
    console.print("[bold]Running validation...[/bold]")
    # Run checks...

if __name__ == '__main__':
    cli()
```

---

## Training-Specific Additions

### 1. Progressive Examples

**examples/01_basic_classification.py**:
```python
"""
Example 1: Basic Ticket Classification

This example demonstrates the core classification logic that determines
whether a ticket is Frontend, Backend, or Uncategorized.

Learning Objectives:
- Understand the component field priority
- Learn the key prefix fallback logic
- Handle edge cases (missing fields)

Concepts:
- Dictionary access with .get()
- if/elif/else logic
- String methods (startswith)
"""

from src.core.classifier import classify_ticket, Classification

# Example 1: Component field takes priority
print("Example 1: Component field")
ticket1 = {
    "key": "BE-123",  # Backend key...
    "component": "Frontend"  # ...but Frontend component
}
result1 = classify_ticket(ticket1)
print(f"Result: {result1}")  # Output: FE
print(f"Why: Component field ('Frontend') takes priority over key prefix\n")

# Example 2: Fallback to key prefix
print("Example 2: Key prefix fallback")
ticket2 = {
    "key": "FE-456",
    "component": None  # No component
}
result2 = classify_ticket(ticket2)
print(f"Result: {result2}")  # Output: FE
print(f"Why: Key starts with 'FE-', so classified as Frontend\n")

# Example 3: Uncategorized
print("Example 3: Uncategorized")
ticket3 = {
    "key": "OPS-789",
    "component": None
}
result3 = classify_ticket(ticket3)
print(f"Result: {result3}")  # Output: Uncategorized
print(f"Why: Neither component nor key prefix match FE/BE\n")

# Exercise: Try these yourself!
print("=" * 50)
print("EXERCISES:")
print("1. What happens with key='FRONTEND-123'?")
print("2. What if the key is missing entirely?")
print("3. How would you extend this to support 'Mobile'?")
```

### 2. Architecture Diagrams

**docs/ARCHITECTURE.md**:
```markdown
# Architecture Overview

## System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        n8n Workflow                          │
│  ┌────────┐   ┌─────────┐   ┌──────────┐   ┌──────────┐   │
│  │Schedule│──→│Mock Jira│──→│Date      │──→│Filter &  │   │
│  │Trigger │   │Data     │   │Windows   │   │Categorize│   │
│  └────────┘   └─────────┘   └──────────┘   └──────────┘   │
│                                                    │         │
│                                                    ↓         │
│                                            ┌──────────┐     │
│                                            │7 Buckets │     │
│                                            └──────────┘     │
│                                                    │         │
│                        ┌───────────────────────────┴──┐     │
│                        ↓                              ↓     │
│                  ┌──────────┐                  ┌──────────┐│
│                  │Confluence│                  │  Slides  ││
│                  │Formatter │                  │Formatter ││
│                  └──────────┘                  └──────────┘│
│                        │                              │     │
│                        ↓                              ↓     │
│                  ┌──────────┐                  ┌──────────┐│
│                  │Write MD  │                  │Write TXT ││
│                  │  File    │                  │  File    ││
│                  └──────────┘                  └──────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Input: Jira Tickets
    │
    ├─ Step 1: Calculate Date Windows
    │  ├─ last_week_start
    │  ├─ last_week_end
    │  ├─ next_14_start
    │  └─ next_14_end
    │
    ├─ Step 2: Classify Each Ticket
    │  ├─ Check component field
    │  ├─ Fallback to key prefix
    │  └─ Result: FE | BE | Uncategorized
    │
    ├─ Step 3: Categorize into Buckets (Priority Order)
    │  ├─ 1. Blocked/Risk? → risks_blocks
    │  ├─ 2. Done + last week? → fe_deployed / be_deployed
    │  ├─ 3. Ready/QA + upcoming? → fe_upcoming / be_upcoming
    │  ├─ 4. In Progress/To Do? → focus_items
    │  └─ 5. Default → uncategorized
    │
    └─ Step 4: Format Outputs
       ├─ Confluence (Markdown)
       └─ Slides (Text)

Output: Reports
```
```

### 3. Learning Path

**docs/LEARNING_PATH.md**:
```markdown
# Learning Path: n8n Workflow Development

This repository is designed to teach n8n workflow development through
a real-world example. Follow this path for optimal learning.

## Prerequisites
- Basic Python knowledge (variables, functions, dictionaries)
- Understanding of JSON
- Basic command line skills

## Level 1: Foundations (2-3 hours)

### Goals:
- Understand the problem being solved
- Learn basic data structures
- Understand ticket classification

### Activities:
1. Read README.md and ASSUMPTIONS.md
2. Run `python3 check_env.py`
3. Run `python3 test_workflow.py`
4. Review generated outputs
5. Complete `examples/01_basic_classification.py`

### Quiz:
- What are the 7 buckets?
- What happens when a ticket has both component="Frontend" and key="BE-123"?
- Why is the "Blocked" status checked first?

## Level 2: Core Logic (3-4 hours)

### Goals:
- Master date calculations
- Understand categorization priority
- Learn testing

### Activities:
1. Study `src/core/date_utils.py`
2. Complete `examples/02_date_windows.py`
3. Study `src/core/categorizer.py`
4. Complete `examples/03_filtering.py`
5. Run tests: `pytest tests/test_core_logic.py -v`
6. Write a custom test

### Quiz:
- How is "last week" calculated on a Tuesday?
- What is the fallback if `deployed_date` is missing?
- Why do we use ISO week numbers?

## Level 3: Formatters (2-3 hours)

### Goals:
- Understand output formatting
- Learn template patterns
- Handle edge cases

### Activities:
1. Study `src/formatters/confluence.py`
2. Study `src/formatters/slides.py`
3. Complete `examples/04_formatters.py`
4. Modify formatting to add new fields
5. Test edge cases (empty buckets, TBD dates)

## Level 4: n8n Integration (3-4 hours)

### Goals:
- Map Python code to n8n nodes
- Understand n8n workflow structure
- Build custom workflows

### Activities:
1. Study `src/n8n/workflow_gen.py`
2. Read `docs/N8N_PATTERNS.md`
3. Import `workflows/weekly_deployment_update.json` into n8n
4. Complete `examples/06_custom_n8n.py`
5. Build a simplified workflow

## Level 5: Production Ready (4-5 hours)

### Goals:
- Add production features
- Optimize performance
- Deploy to production

### Activities:
1. Add error handling
2. Add logging
3. Add monitoring
4. Write integration tests
5. Set up CI/CD (optional)

## Final Project

Build your own n8n workflow that:
1. Fetches data from an API
2. Processes/transforms the data
3. Generates a formatted report
4. Includes tests

Example ideas:
- GitHub PR summary
- Customer support ticket metrics
- Sales pipeline report
- System health dashboard
```

---

## Implementation Checklist

### Week 1: Foundation
- [ ] Add mypy configuration
- [ ] Add type hints to all functions
- [ ] Set up black/ruff formatting
- [ ] Create pyproject.toml
- [ ] Define core dataclasses
- [ ] Update all imports

### Week 2: Refactoring
- [ ] Create src/ directory structure
- [ ] Extract models module
- [ ] Extract core module
- [ ] Extract formatters module
- [ ] Remove global state
- [ ] Add configuration
- [ ] Improve error handling
- [ ] Update tests

### Week 3: Documentation
- [ ] Enhance all docstrings
- [ ] Create 6 progressive examples
- [ ] Write ARCHITECTURE.md
- [ ] Write DATA_FLOW.md
- [ ] Write TESTING_GUIDE.md
- [ ] Write N8N_PATTERNS.md
- [ ] Write TUTORIAL.md
- [ ] Add diagrams

### Week 4: Polish
- [ ] Add CLI with click
- [ ] Add logging setup
- [ ] Add validation with pydantic
- [ ] Increase test coverage to 80%+
- [ ] Create learning exercises
- [ ] Write LEARNING_PATH.md
- [ ] Add FAQ
- [ ] Create troubleshooting guide
- [ ] Final review and polish

---

## Success Metrics

### Code Quality
- [ ] 100% type hints (passes mypy --strict)
- [ ] 80%+ test coverage
- [ ] 0 linting errors (ruff)
- [ ] All functions < 50 lines
- [ ] All files < 300 lines
- [ ] Cyclomatic complexity < 10

### Documentation
- [ ] Every function has docstring
- [ ] Every function has example
- [ ] 6 progressive examples complete
- [ ] 5 architecture docs complete
- [ ] Tutorial complete with exercises

### Training Readiness
- [ ] New engineer can complete Level 1 in < 3 hours
- [ ] Example code runs without errors
- [ ] Clear learning path defined
- [ ] Quiz questions included
- [ ] Real-world exercises included

---

## Maintenance Plan

### Monthly
- [ ] Update dependencies
- [ ] Review and merge PRs
- [ ] Update examples if n8n changes
- [ ] Gather feedback from trainees

### Quarterly
- [ ] Review and update documentation
- [ ] Add new examples based on feedback
- [ ] Update best practices
- [ ] Record new training videos

### Annually
- [ ] Major version review
- [ ] Update for Python/n8n changes
- [ ] Refresh all examples
- [ ] Survey training effectiveness

---

## Resources Needed

### Tools
- mypy (type checking)
- ruff (linting)
- black (formatting)
- pytest (testing)
- pytest-cov (coverage)
- click/typer (CLI)
- rich (pretty CLI output)
- pydantic (validation)

### Documentation Tools
- mkdocs (documentation site)
- mermaid (diagrams)
- sphinx (API docs)

### Optional
- pre-commit (git hooks)
- tox (multi-environment testing)
- docker (containerization)

---

## Questions for Discussion

1. **Scope**: Do we want to include API integration examples (real Jira/Confluence)?
2. **Level**: What's the target experience level (junior, mid, senior)?
3. **Timeline**: Is 4 weeks realistic or do we need more time?
4. **Resources**: Who will maintain this after initial creation?
5. **Deployment**: Do we want to include production deployment guides?
6. **Video**: Should we record video walkthroughs?
7. **Integration**: Should this integrate with other training materials?

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Prioritize** specific improvements
3. **Assign** ownership for each phase
4. **Schedule** kickoff meeting
5. **Create** GitHub project board
6. **Begin** Phase 1 implementation

Would you like me to proceed with any specific phase of this plan?
