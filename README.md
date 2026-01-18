# Weekly Deployment Update - n8n Workflow

An automated workflow for generating stakeholder-facing weekly deployment reports from Jira data, outputting to Confluence (Markdown) and Google Slides (text format).

## Overview

This project implements a 13-node n8n workflow that:
- Pulls ticket data from Jira (mocked for this evaluation)
- Categorizes tickets into 7 buckets (FE/BE deployed, FE/BE upcoming, focus items, risks, uncategorized)
- Generates formatted reports for Confluence and Google Slides
- Supports scheduled execution (Monday 9am UTC) or manual runs

## Repository Structure

```
n8n-evaluation/
├── flowbot/                           # Python virtual environment (not in git)
├── workflows/
│   └── weekly_deployment_update.json  # n8n workflow (import this)
├── docs/
│   ├── technical-documentation.md     # Detailed technical write-up
│   └── QA_Test_Plan.md                # Step-by-step QA testing guide
├── mockdata/
│   ├── mock_jira_tickets.json         # Sample mock ticket data
│   └── categorized_data.json          # Categorized output data
├── outputs/
│   ├── confluence/
│   │   └── YYYY-Month/
│   │       ├── week-WW.md                 # Confluence Markdown output
│   │       └── index.md                   # Monthly index (rollover log)
│   ├── slides/
│   │   └── YYYY-WWW.txt                   # Slide text output
│   ├── run_index.csv                      # Run index (week + paths)
│   └── verification_summary_YYYY-WWW.md   # Quick verification summary
├── test_workflow.py                   # Standalone test script
├── check_env.py                       # Environment verification script
├── requirements.txt                   # Python dependencies
├── PLAN.md                            # Implementation plan
├── ASSUMPTIONS.md                     # Implementation decisions & rationale
└── README.md                          # This file
```

## Quick Start

### Prerequisites

- n8n (self-hosted or cloud)
- Python 3.x (for test script only)

### Setup Virtual Environment (Recommended)

```bash
cd /path/to/n8n-evaluation
python3 -m venv flowbot
source flowbot/bin/activate  # On Windows: flowbot\Scripts\activate
python3 check_env.py         # Verify setup
```

### Running in n8n

1. Open n8n and create a new workflow
2. Import the workflow JSON:
   - Click the menu (⋮) → Import from File
   - Select `workflows/weekly_deployment_update.json`
3. Click "Execute Workflow" to run manually
4. Check outputs in `outputs/`:
   - `outputs/confluence/YYYY-Month/week-WW.md`
   - `outputs/slides/YYYY-WWW.txt`

### Running the Test Script

The test script simulates the entire workflow locally without n8n:

```bash
cd /path/to/n8n-evaluation
python3 test_workflow.py
```

Outputs are written to `outputs/` and `mockdata/` directories. Re-running the workflow overwrites the same week’s files to simulate upsert behavior; the test script also writes `outputs/run_index.csv` and a `verification_summary_*.md` for quick checks.

## Workflow Nodes

| # | Node | Purpose |
|---|------|---------|
| 1 | Schedule Trigger | Monday 9am UTC (manual run supported) |
| 2 | Read/Write Files from Disk | Reads mock Jira JSON from `~/.n8n-files` |
| 3 | Extract from File | Converts JSON to items |
| 4 | Date Windows | Calculates "last week" and "next 14 days" |
| 5 | Filter & Categorize | Assigns tickets to 7 buckets |
| 6 | Week Identifier | Generates ISO week (e.g., "2026-W03") |
| 7 | Confluence Formatter | Generates Markdown |
| 8 | Slide Formatter | Generates two-column text |
| 9 | IF First Monday | Monthly rollover check (placeholder) |
| 10 | Convert Confluence to File | Converts Markdown to a file |
| 11 | Convert Slide to File | Converts slide text to a file |
| 12 | Write Confluence File | Saves Markdown file |
| 13 | Write Slide File | Saves text file |

## Report Categories

The workflow categorizes tickets into 7 buckets:

1. **FE - Deployed Last Week**: Frontend items deployed in previous Mon-Sun
2. **BE - Deployed Last Week**: Backend items deployed in previous Mon-Sun
3. **FE - Expected Next 14 Days**: Frontend items planned for next 2 weeks
4. **BE - Expected Next 14 Days**: Backend items planned for next 2 weeks
5. **Team Focus Items**: In Progress/To Do items grouped by epic
6. **Risks/Blocks**: Items with status="Blocked" or blocked_reason
7. **Uncategorized**: Items not matching FE/BE classification

## Classification Logic

Tickets are classified as Frontend or Backend using:

1. **Primary**: `component` field = "Frontend" or "Backend"
2. **Fallback**: Ticket key prefix "FE-" or "BE-"
3. **Default**: Neither matches → "Uncategorized"

## Edge Cases Handled

- Missing `target_deploy_date` → Show "TBD" for Ready for Deploy items
- Missing `component` → Fall back to key prefix
- Missing `deployed_date` → Use `updated` field
- Empty categories → Display "[None]"
- Missing `epic` for focus items → Group under "Other Focus Items"
- No risks/blocks → Display "No known risks/blocks this week."

## Sample Outputs

### Confluence (Markdown)
```markdown
# Weekly Deployment Update - 2026-W03

## Deployed Last Week
### Frontend
- [FE-102](url): Add dark mode toggle
- [FE-104](url): Update form validation messages

### Backend
- [BE-202](url): Add rate limiting to API endpoints
```

### Slide (Text)
```
+-----------------------------+-----------------------------+
|     DEPLOYED LAST WEEK      |    EXPECTED NEXT 14 DAYS    |
+-----------------------------+-----------------------------+

LEFT COLUMN (Deployed):
FRONTEND:
* FE-102: Add dark mode toggle
* FE-104: Update form validation messages
```

## Documentation

See [docs/technical-documentation.md](docs/technical-documentation.md) for:
- Detailed reporting window definitions
- Complete classification logic
- Data schemas
- Production considerations
- Testing checklist

See [docs/QA_Test_Plan.md](docs/QA_Test_Plan.md) for:
- Step-by-step testing instructions
- Expected results for each test case
- Edge case verification
- QA sign-off template

See [ASSUMPTIONS.md](ASSUMPTIONS.md) for:
- Implementation decisions where requirements were ambiguous
- Rationale for each decision
- Alternatives considered

## Production Deployment (Not Implemented)

This evaluation uses mock data. For production, replace:

1. **Node 2** → Jira API HTTP Request with JQL query
2. **Node 9** → Confluence API to create/update pages
3. **Node 10** → Google Slides API for slide generation

See technical documentation for detailed production considerations.

## License

Internal evaluation project.
