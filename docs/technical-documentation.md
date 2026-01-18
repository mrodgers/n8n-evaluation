# Weekly Deployment Update - Technical Documentation

## Overview

This document describes the technical implementation of the Weekly Deployment Update automation workflow built in n8n. The workflow generates stakeholder-facing deployment reports from Jira data (mocked for this evaluation) and outputs to Confluence (Markdown) and Google Slides (text format).

## Reporting Windows

### Deployed Last Week

**Definition**: Previous Monday 00:00 to Sunday 23:59 (UTC)

**Logic**:
- If today is Monday: Use the week that just ended (7-13 days ago)
- If today is Tuesday-Sunday: Use the most recent completed Monday-Sunday week

**Data Source**:
- Primary: `deployed_date` field
- Fallback: `updated` field (if `deployed_date` is missing)

### Expected Next 14 Days

**Definition**: Today 00:00 through 14 days forward 23:59:59 (UTC)

**Data Source**:
- Primary: `target_deploy_date` field
- Fallback qualification: `status` IN ["Ready for Deploy", "In QA"] AND `fix_version` exists
- Missing date handling: If status is "Ready for Deploy" but no date, display as "TBD"

## Ticket Categories (7 Buckets)

| Bucket | Description | Criteria |
|--------|-------------|----------|
| FE - Deployed Last Week | Frontend items deployed in previous week | Component="Frontend" OR key prefix "FE-", status="Done", deployed in window |
| BE - Deployed Last Week | Backend items deployed in previous week | Component="Backend" OR key prefix "BE-", status="Done", deployed in window |
| FE - Expected Next 14 Days | Frontend items planned for next 2 weeks | Component="Frontend" OR key prefix "FE-", status="Ready for Deploy"/"In QA" |
| BE - Expected Next 14 Days | Backend items planned for next 2 weeks | Component="Backend" OR key prefix "BE-", status="Ready for Deploy"/"In QA" |
| Team Focus Items | Current work in progress | Status="In Progress" OR "To Do", grouped by epic |
| Risks/Blocks | Blocked items requiring attention | Status="Blocked" OR has `blocked_reason` field |
| Uncategorized | Items not matching FE/BE classification | No component and non-standard key prefix |

## FE vs BE Classification Logic

Classification follows a priority order:

1. **Primary (Component field)**:
   - `component` = "Frontend" → FE
   - `component` = "Backend" → BE

2. **Fallback (Key prefix)**:
   - Key starts with "FE-" → Frontend
   - Key starts with "BE-" → Backend

3. **Default**:
   - Neither matches → "Uncategorized"

## Edge Cases Handled

| Edge Case | Handling |
|-----------|----------|
| Missing `target_deploy_date` | Show "TBD" if status="Ready for Deploy" |
| Missing `component` field | Use ticket key prefix fallback |
| Missing `deployed_date` | Use `updated` field as fallback |
| Empty category | Display "[None]" |
| Missing `epic` for focus items | Group under "Other Focus Items" |
| No risks/blocks | Display "No known risks/blocks this week." |

## Workflow Architecture

The n8n workflow consists of 13 nodes arranged in a linear flow:

```
[Schedule Trigger] → [Read/Write Files] → [Extract from File]
      ↓
[Calculate Date Windows] → [Filter/Categorize] → [Week ID]
      ↓
[Format Confluence] → [Format Slide] → [IF First Monday]
      ↓
[Convert Confluence] → [Write Confluence File]
      ↓
[Convert Slide] → [Write Slide File]
```

### Node Descriptions

| Node | Type | Purpose |
|------|------|---------|
| 1. Schedule Trigger | Trigger | Runs Monday 9am UTC, supports manual execution |
| 2. Read/Write Files from Disk | File | Reads mock Jira JSON from `~/.n8n-files` |
| 3. Extract from File | File | Converts JSON file to items |
| 4. Calculate Date Windows | Code (JS) | Calculates "last week" and "next 14 days" windows |
| 5. Filter & Categorize | Code (JS) | Assigns tickets to 7 buckets with FE/BE split |
| 6. Week Identifier | Code (JS) | Generates ISO week ID (e.g., "2026-W03") |
| 7. Confluence Formatter | Code (JS) | Generates Markdown output |
| 8. Slide Formatter | Code (JS) | Generates two-column text output |
| 9. IF First Monday | IF | Placeholder for monthly rollover logic |
| 10. Convert Confluence to File | Convert | Produces a `.md` binary file |
| 11. Convert Slide to File | Convert | Produces a `.txt` binary file |
| 12. Write Confluence File | Write File | Saves to `outputs/confluence/{YYYY-Month}/week-{WW}.md` |
| 13. Write Slide File | Write File | Saves to `outputs/slides/{YYYY}-W{WW}.txt` |

## Assumptions & Limitations

### Current Implementation (Mock Data)

- **Mock data only**: No live Jira API integration
- **Single timezone**: All calculations use UTC (extensible to custom timezones later)
- **File-based output**: Simulates API upsert by writing to files
- **28 mock tickets**: Demonstrates all scenarios including edge cases

### Production Considerations (Not Implemented)

These items are documented for future production deployment:

1. **Jira API Integration**: Replace mock data node with Jira HTTP Request
   - Authentication: API token or OAuth 2.0
   - JQL query for relevant tickets
   - Pagination handling for large result sets

2. **Confluence API Integration**: Replace file write with Confluence API
   - Create or update page (upsert logic)
   - Handle page versioning
   - Apply appropriate labels

3. **Google Slides API Integration**: Replace file write with Slides API
   - Template-based slide generation
   - Dynamic content insertion
   - Two-column layout formatting

4. **Monthly Rollover Logic**: Expand IF node for first Monday of month
   - Archive previous month's page
   - Create new month's page structure
   - Update navigation/index pages

5. **Error Handling**: Add error handling nodes
   - Retry logic for API failures
   - Notification on workflow failure
   - Logging for debugging

## Data Schema

### Input Ticket Schema (Mock Jira)

```json
{
  "key": "FE-101",
  "summary": "Implement new dashboard layout",
  "status": "Done",
  "component": "Frontend",
  "deployed_date": "2026-01-13",
  "updated": "2026-01-13",
  "target_deploy_date": null,
  "epic": "Dashboard Redesign",
  "fix_version": "2026.1",
  "blocked_reason": null
}
```

### Output Schema (Categorized)

```json
{
  "fe_deployed": [...],
  "be_deployed": [...],
  "fe_upcoming": [...],
  "be_upcoming": [...],
  "focus_items": [
    {
      "epic": "Epic Name",
      "tickets": [...]
    }
  ],
  "risks_blocks": [...],
  "uncategorized": [...]
}
```

## Testing

### Environment Setup

```bash
cd /path/to/n8n-evaluation
source flowbot/bin/activate  # Activate virtual environment
python3 check_env.py         # Verify environment is ready
```

The `check_env.py` script verifies:
- Python version (3.8+)
- Virtual environment is active
- All required project files exist
- Output directories exist
- Python imports work

### Test Script

The `test_workflow.py` script simulates the entire workflow locally:

```bash
python3 test_workflow.py
```

This generates:
- `outputs/confluence/{YYYY-Month}/week-{WW}.md` - Confluence Markdown (overwrites by week)
- `outputs/confluence/{YYYY-Month}/index.md` - Monthly index with week entries (rollover log)
- `outputs/slides/{YYYY}-W{WW}.txt` - Slide text format (overwrites by week)
- `outputs/verification_summary_{YYYY}-W{WW}.md` - Quick verification summary
- `outputs/run_index.csv` - Run history (week + output paths)
- `mockdata/mock_jira_tickets.json` - Raw mock tickets
- `mockdata/categorized_data.json` - Categorized output

### QA Test Plan

For comprehensive testing, see `docs/QA_Test_Plan.md` which provides:
- Step-by-step testing instructions
- Expected results for each test case
- Edge case verification checklist
- QA sign-off template

### Quick Verification Checklist

- [ ] All 7 buckets populated correctly
- [ ] Date windows calculated properly for current weekday
- [ ] FE/BE classification working (component + fallback)
- [ ] Edge cases: TBD dates, missing components, empty categories
- [ ] Risks/blocks include blocked_reason
- [ ] Focus items grouped by epic
