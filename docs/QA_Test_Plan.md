# QA Test Plan: Weekly Deployment Update Workflow

**Version**: 2.3
**Date**: 2026-01-18
**Tester**: ______________________
**Test Date**: ______________________

---

## Overview

This document provides step-by-step instructions for testing the Weekly Deployment Update workflow. Please complete all test cases and record results in the provided tables.

---

## Prerequisites

- [ ] Python 3.x installed
- [ ] Access to repository at `/Users/matt/Git/n8n-evaluation`
- [ ] (Optional) n8n installed for workflow import testing
- [ ] Review `ASSUMPTIONS.md` for implementation decisions

## Environment Setup

```bash
cd /Users/matt/Git/n8n-evaluation
source flowbot/bin/activate  # Activate virtual environment
python3 check_env.py         # Verify setup (all checks should pass)
```

Note: The script uses only Python standard library - no external packages required.

---

## Part 1: Test Script Execution

### Step 1.1: Run the Test Script

```bash
cd /Users/matt/Git/n8n-evaluation
python3 test_workflow.py
```

**Expected Output:**
- Console shows "Test completed successfully!"
- Files created in `outputs/` and `mockdata/`

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| Script runs without errors | No exceptions | | |
| Total tickets generated | ~25-30 | | |
| Files created in `outputs/` | Confluence `.md`, index `.md`, slide `.txt`, verification summary `.md`, run index `.csv` | | |
| Files created in `mockdata/` | 2 files | | |

**Console Output Summary (fill in actual values):**

**Note**: Ranges below are illustrative based on current mock data. If mock data is modified, these ranges may shift. The key validation is that tickets are categorized (no ticket is lost) and each bucket contains reasonable items for its category.

| Bucket | Expected Range | Actual Count | Pass/Fail |
|--------|----------------|--------------|-----------|
| FE Deployed | 1-5 | | |
| BE Deployed | 1-4 | | |
| FE Upcoming | 3-6 | | |
| BE Upcoming | 3-5 | | |
| Focus Items | 4-8 | | |
| Risks/Blocks | 2-4 | | |
| Uncategorized | 4-10 | | |

**Validation rule**: Sum of all buckets should equal Total tickets generated (no tickets lost).

---

## Part 2: Confluence Output Verification

### Step 2.1: Open the Confluence Output

```bash
ls outputs/confluence/2026-January/week-03.md
cat outputs/confluence/2026-January/week-03.md
```

Or open in any text editor.

### Step 2.2: Verify Structure

Check that the following sections exist in order:

| # | Section | Present? (Y/N) | Notes |
|---|---------|----------------|-------|
| 1 | Title with week ID (e.g., "2026-W03") | | |
| 2 | Report Period dates | | |
| 3 | Generated timestamp | | |
| 4 | "Deployed Last Week" header | | |
| 5 | Frontend subsection | | |
| 6 | Backend subsection | | |
| 7 | "Expected Next 14 Days" header | | |
| 8 | Frontend subsection with dates | | |
| 9 | Backend subsection with dates | | |
| 10 | "Team Focus Items" header | | |
| 11 | "Risks & Blockers" header | | |

### Step 2.5: Verify Monthly Index

Open the index file for the current month:

```bash
cat outputs/confluence/2026-January/index.md
```

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| Index has month header | `# 2026-January Tech Updates` | | |
| Week entry present | `- 2026-W03 (...)` | | |

### Step 2.3: Verify Ticket Format

Check that tickets follow this format:
```
- [TICKET-KEY](url): Summary text
```

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| Ticket keys are hyperlinked | `[FE-xxx](https://jira...)` | | |
| Summary text follows colon | Yes | | |
| Upcoming items show target date | `*(Target: YYYY-MM-DD)*` | | |

### Step 2.4: Verify Date Windows (Internal Consistency)

**Note**: We validate that dates are internally consistent with each other, using the **Generated timestamp in the output** as the reference point. We do NOT compare against external calendars or test execution time. See `ASSUMPTIONS.md` for rationale.

**Reference point**: Use the "Generated" timestamp shown in the output (e.g., "Generated: 2026-01-18 11:13:48 UTC"). All checks below are relative to this date.

| Check | How to Verify | Pass/Fail |
|-------|---------------|-----------|
| Report Period Start is a Monday | Look up day of week for date shown | |
| Report Period End is a Sunday | Look up day of week for date shown | |
| Start and End are 6 days apart | End date minus Start date = 6 | |
| Next 14 Days Start = Generated date | Compare dates (ignore time) | |
| Next 14 Days End = Generated date + 14 | End minus Start = 14 days | |

**Why no external time check?** The workflow's Generated timestamp IS the authoritative "now". If you run the test at 11:00 and the output says "Generated: 11:00:05", that's correct. We don't validate against wall-clock time.

---

## Part 3: Slide Output Verification

### Step 3.1: Open the Slide Output

```bash
ls outputs/slides/2026-W03.txt
cat outputs/slides/2026-W03.txt
```

### Step 3.2: Verify Structure

| # | Element | Present? (Y/N) | Notes |
|---|---------|----------------|-------|
| 1 | Title with week ID | | |
| 2 | "SLIDE 1: OVERVIEW" section | | |
| 3 | Two-column header (DEPLOYED / EXPECTED) | | |
| 4 | LEFT COLUMN with Frontend/Backend | | |
| 5 | RIGHT COLUMN with Frontend/Backend | | |
| 6 | "SLIDE 2: FOCUS & RISKS" section | | |
| 7 | TEAM FOCUS ITEMS section | | |
| 8 | RISKS & BLOCKERS section | | |
| 9 | Generated timestamp at bottom | | |

### Step 3.3: Verify Ticket Format

| Check | Expected Format | Actual | Pass/Fail |
|-------|-----------------|--------|-----------|
| Deployed items | `* KEY: Summary` | | |
| Upcoming items | `* KEY: Summary [DATE]` | | |
| Blocked items | `! KEY: Summary` then `-> reason` | | |

---

## Part 4: Edge Case Verification

### Step 4.1: TBD Date Handling

Look for ticket **FE-107** in the Confluence output.

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| FE-107 appears in "Expected Next 14 Days" | Yes | | |
| FE-107 shows "(Target: TBD)" | Yes | | |

### Step 4.2: Missing Component Fallback

Look for ticket **FE-112** (has `component: null` but key starts with "FE-").

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| FE-112 classified as Frontend | Yes (appears in FE section or Other Items) | | |

### Step 4.3: Uncategorized Items

Look for tickets with non-standard prefixes: **OPS-301**, **OPS-302**, **DATA-401**

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| OPS-301 in "Other Items" section | Yes | | |
| OPS-302 in "Other Items" section | Yes | | |
| DATA-401 in Focus Items (has epic) | Yes | | |

### Step 4.4: Missing Epic Handling

Look for ticket **BE-209** in Focus Items section.

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| BE-209 grouped under "Other Focus Items" | Yes | | |

### Step 4.5: Risks/Blockers with Reasons

Check the Risks & Blockers section for these tickets:

| Ticket | Expected Reason | Reason Present? | Pass/Fail |
|--------|-----------------|-----------------|-----------|
| FE-111 | "Waiting for vendor API fix" | | |
| BE-210 | "Requires DBA approval for production" | | |
| BE-211 | "Pending security team review" | | |

---

## Part 5: Mock Data Verification

### Step 5.1: Check Mock Data File

```bash
cat mockdata/mock_jira_tickets.json | python3 -m json.tool | head -50
```

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| Valid JSON format | Parses without error | | |
| Array of tickets | Yes | | |
| Each ticket has "key" field | Yes | | |
| Each ticket has "summary" field | Yes | | |
| Each ticket has "status" field | Yes | | |

### Step 5.2: Check Categorized Data File

```bash
cat mockdata/categorized_data.json | python3 -m json.tool | head -30
```

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| Valid JSON format | Parses without error | | |
| Contains "buckets" object | Yes | | |
| Contains "windows" object | Yes | | |
| Contains "week_id" string | Yes | | |

---

## Part 6: n8n Workflow Import (Optional)

If n8n is available:

### Step 6.1: Import Workflow

1. Open n8n
2. Create new workflow
3. Menu (⋮) → Import from File
4. Select `workflows/weekly_deployment_update.json`

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| Import succeeds without errors | Yes | | |
| All 13 nodes visible | Yes | | |
| Nodes are connected | Yes | | |

### Step 6.2: Execute Workflow

1. Click "Execute Workflow"
2. Wait for completion

| Check | Expected | Actual | Pass/Fail |
|-------|----------|--------|-----------|
| Workflow executes without errors | Yes | | |
| All nodes show green checkmarks | Yes | | |
| Output files created in `outputs/` | Yes | | |

---

## Part 7: Summary & Sign-off

### Test Summary

| Category | Total Tests | Passed | Failed | Blocked |
|----------|-------------|--------|--------|---------|
| Script Execution | | | | |
| Confluence Output | | | | |
| Slide Output | | | | |
| Edge Cases | | | | |
| Mock Data | | | | |
| n8n Import (if tested) | | | | |
| **TOTAL** | | | | |

### Issues Found

| # | Severity (High/Med/Low) | Description | Steps to Reproduce |
|---|-------------------------|-------------|-------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### Specific Feedback Requested

Please provide answers to these questions:

1. **Date Window Consistency**: Are the date windows internally consistent? (Start is Monday, End is Sunday, 6 days apart, Next 14 days spans 14 days from Generated date)

   Answer: _________________________________________________________________

2. **Output Readability**: Is the Confluence Markdown output clear and well-formatted? Any suggestions for improvement?

   Answer: _________________________________________________________________

3. **Slide Format Usability**: Is the slide text format easy to copy into a presentation? Would a different format work better?

   Answer: _________________________________________________________________

4. **Missing Scenarios**: Are there any edge cases or scenarios not covered by the mock data that should be tested?

   Answer: _________________________________________________________________

5. **Classification Accuracy**: Did any tickets appear in the wrong category? If so, which ones?

   Answer: _________________________________________________________________

### QA Tester Sign-off

- [ ] All critical tests passed
- [ ] All issues documented above
- [ ] Feedback questions answered

**Tester Signature**: ______________________
**Date**: ______________________

---

## QA Logging & Outcome Criteria

- **Findings file**: Capture each test run in `outputs/QA_Findings_<ISO-UTC-timestamp>.md` (e.g., `outputs/QA_Findings_2026-01-18T19-43-21Z.md`). Document the commands run, bucket counts, observations, issues, and any follow-up questions so the UTC timestamp is the single source of truth for the dev team.
- **Success metrics**:
  1. `test_workflow.py` completes successfully inside the `flowbot` virtual environment (no stack traces or error exit code).
  2. All bucket counts still sum to the total ticket count and fall within the illustrative ranges in Part 1.
  3. The generated artifacts (`outputs/confluence/{YYYY-Month}/week-{WW}.md`, `outputs/confluence/{YYYY-Month}/index.md`, `outputs/slides/{YYYY}-W{WW}.txt`, `outputs/verification_summary_{YYYY}-W{WW}.md`, `outputs/run_index.csv`, `mockdata/*.json`) exist, parse correctly, and include the sections/keys referenced throughout this plan.
- **Timestamp ID**: Record the week ID used for each generated output so QA can point devs to the correct files and diff them against prior runs.
- **Failures or deviations**: Log missing sections, formatting regressions, incorrect bucket placements, or JSON parsing issues in the findings file and describe how to reproduce them.
- **Handoff**: Point dev engs to the UTC-dated findings file first, then reference the raw outputs and mock data so they can trace from the summary to the actual artifacts.

## Appendix: Quick Commands Reference

```bash
# Run test
python3 test_workflow.py

# View Confluence output
ls outputs/confluence/2026-January/week-03.md
cat outputs/confluence/2026-January/week-03.md

# View monthly index
cat outputs/confluence/2026-January/index.md

# View Slide output (text)
ls outputs/slides/2026-W03.txt
cat outputs/slides/2026-W03.txt

# View verification summary
cat outputs/verification_summary_2026-W03.md

# View run index
cat outputs/run_index.csv

# View mock data (pretty print)
cat mockdata/mock_jira_tickets.json | python3 -m json.tool

# View categorized data
cat mockdata/categorized_data.json | python3 -m json.tool

# Count tickets in mock data
cat mockdata/mock_jira_tickets.json | python3 -c "import json,sys; print(len(json.load(sys.stdin)))"
```
