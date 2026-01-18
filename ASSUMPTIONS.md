# ASSUMPTIONS.md

This document records decisions made during implementation where requirements were ambiguous or multiple interpretations were possible.

---

## Date Window Validation

**Decision**: Validate date windows using internal consistency, not external calendar calculation.

**What this means**:
- QA verifies that the output dates are self-consistent (e.g., last_week_start is a Monday, last_week_end is a Sunday 6 days later)
- QA does NOT manually calculate expected dates from a calendar
- QA does NOT compare against wall-clock time or test execution time
- The "Generated" timestamp in the output IS the authoritative reference point for all date checks

**Reference point**: The workflow's "Generated" timestamp (e.g., "Generated: 2026-01-18 11:13:48 UTC") is the "now" for all validations. "Next 14 Days Start" should match this date. No external clock comparison needed.

**Why**: Simpler to test and explain. If internal consistency passes, the logic is working. Manual calendar calculation introduces human error and complexity. Comparing to external clocks introduces race conditions and timezone confusion.

**Future consideration**: Add calendar-based validation if edge cases are found in production.

---

## "Last Week" Definition

**Decision**: "Last week" means the most recent completed Monday-Sunday week.

**What this means**:
- If today is Monday: Last week = the 7 days ending yesterday (Sunday)
- If today is Tuesday-Sunday: Last week = the most recent Mon-Sun that has fully passed

**Why**: Stakeholders want to report on completed work. A partial week would include incomplete data.

**Alternative considered**: Rolling 7-day window. Rejected because it would mix weeks and confuse reporting.

---

## Timezone Handling

**Decision**: All date calculations use UTC (Coordinated Universal Time).

**What this means**:
- "Monday 00:00" means midnight UTC
- No daylight saving transitions to handle
- All timestamps in outputs show "UTC" suffix

**Why**: UTC is timezone-agnostic and avoids confusion in a centralized app. Using UTC as the baseline makes it easier to extend to custom timezones or multi-timezone support later.

**Future consideration**: Add configurable timezone parameter that converts from UTC to user's local timezone for display.

---

## FE/BE Classification Priority

**Decision**: Component field takes priority over ticket key prefix.

**What this means**:
- A ticket with `component: "Backend"` and key `FE-123` is classified as Backend
- Key prefix is only used when component field is missing/null

**Why**: Component field is the authoritative source in Jira. Key prefixes are a naming convention that may not always be followed.

---

## Missing Target Deploy Date

**Decision**: Show "TBD" for Ready for Deploy items without a target date.

**What this means**:
- Ticket appears in "Expected Next 14 Days" section
- Date shows as "TBD" instead of being omitted

**Why**: Stakeholders need visibility into items that are ready but not yet scheduled. Hiding them would be misleading.

**Alternative considered**: Omit from report. Rejected because it hides important information.

---

## Focus Items Without Epic

**Decision**: Group under "Other Focus Items" instead of omitting.

**What this means**:
- Items with status "In Progress" or "To Do" but no epic field are still shown
- They appear under a generic "Other Focus Items" heading

**Why**: All in-progress work should be visible regardless of epic assignment.

---

## QA Bucket Count Expectations

**Decision**: QA test plan uses illustrative ranges, not hard-coded exact counts.

**What this means**:
- Bucket counts in QA plan (e.g., "FE Deployed: 1-5") are guidelines based on current mock data
- If mock data is modified, these ranges may shift
- The key validation is: (1) no tickets are lost (sum of buckets = total), (2) each bucket contains appropriate items for its category

**Why**: Hard-coding exact counts creates false test failures whenever mock data changes. Ranges allow the test plan to remain valid across minor data updates while still catching major categorization bugs.

**Validation rule**: Sum of all bucket counts must equal total tickets generated.

---

## Mock Data Date Generation

**Decision**: Mock ticket dates are relative to runtime, not fixed dates.

**What this means**:
- `deployed_date` values use `days_ago(N)` - always N days before test run
- `target_deploy_date` values use `days_from_now(N)` - always N days after test run
- Running the test on different days produces different absolute dates

**Why**: Ensures the date filtering logic is always testable regardless of when the test runs.

**Tradeoff**: Makes it harder to have reproducible test outputs with identical dates.

---

## Empty Category Display

**Decision**: Show "[None]" for empty categories instead of hiding the section.

**What this means**:
- If no Frontend items were deployed, the report shows "### Frontend" followed by "[None]"
- The section header is always present

**Why**: Explicit "nothing here" is clearer than silent omission. Stakeholders know the category was considered.

---

## Blocked Items with In-Progress Status

**Decision**: Items with `blocked_reason` field go to Risks/Blocks even if status is not "Blocked".

**What this means**:
- A ticket with status "In Progress" but has `blocked_reason: "Waiting on API"` appears in Risks/Blocks
- The `blocked_reason` field overrides status for categorization

**Why**: The presence of a blocked_reason indicates a real blocker that stakeholders should see, regardless of whether someone updated the status field.

---

## Ticket Processing Priority

**Decision**: Tickets are processed in this order: Risks/Blocks → Deployed → Upcoming → Focus → Uncategorized.

**What this means**:
- A ticket can only appear in one bucket
- If a ticket matches multiple criteria, the first match wins
- Blocked items are always surfaced first (most important for stakeholders)

**Why**: Prevents duplicate reporting and ensures blocked items get visibility.

---

## Google Slides Output Format

**Decision**: Output plain text (`.txt`) instead of calling the Google Slides API.

**What this means**:
- Output is `outputs/slides/YYYY-WWW.txt`
- Content is ready to paste into a slide deck
- No Google API authentication required

**Why**: Text output demonstrates the reporting format without OAuth complexity.

**Tradeoff**: Manual paste step required vs direct API integration.

**Future consideration**: Add Google Slides API integration for direct slide creation/update.

---

## Week-Based Outputs

**Decision**: Use week identifiers (no timestamps) and overwrite outputs on re-run.

**What this means**:
- Confluence outputs are stored at `outputs/confluence/{YYYY-Month}/week-{WW}.md`
- Slide outputs are stored at `outputs/slides/{YYYY}-W{WW}.txt`
- Re-runs overwrite the same week’s files (upsert simulation)

**Why**: Mirrors the desired upsert behavior and keeps the output locations stable.

**Tradeoff**: No historical file archive by default; use git or a copy step if history is needed.

**Future consideration**: Add a versioned archive folder or API-based revision history.

---

## Adding New Assumptions

When making implementation decisions, add them here with:
1. **Decision**: What was decided
2. **What this means**: Concrete behavior
3. **Why**: Reasoning
4. **Alternative considered** (optional): What else was considered
5. **Future consideration** (optional): How this might evolve
