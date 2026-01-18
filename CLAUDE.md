# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains an n8n workflow for generating automated weekly deployment reports. The workflow processes Jira ticket data (mocked) and outputs to Confluence (Markdown) and Google Slides (text format).

## Commands

### Environment Setup
```bash
source flowbot/bin/activate  # Activate virtual environment
python3 check_env.py         # Verify setup
```

### Run Test Script
```bash
python3 test_workflow.py
```
Generates weekly output files in `outputs/` (e.g., `outputs/confluence/YYYY-Month/week-WW.md`, `outputs/slides/YYYY-WWW.txt`) and mock data in `mockdata/`.

### Import Workflow to n8n
1. Open n8n
2. Import `workflows/weekly_deployment_update.json`
3. Execute manually or wait for scheduled trigger (Monday 9am UTC)

## Project Structure

```
n8n-evaluation/
├── flowbot/             # Python virtual environment (not in git)
├── workflows/           # n8n workflow JSON exports
├── docs/                # Technical documentation & QA test plan
├── mockdata/            # Generated mock Jira data and categorized output
├── outputs/             # Generated Confluence and Slide outputs
├── test_workflow.py     # Standalone test script (simulates all n8n nodes)
├── check_env.py         # Environment verification script
├── requirements.txt     # Python dependencies (python-pptx optional)
├── ASSUMPTIONS.md       # Implementation decisions & rationale
└── .gitignore           # Git ignore rules
```

## Key Files

| File | Purpose |
|------|---------|
| `workflows/weekly_deployment_update.json` | Main n8n workflow (import this) |
| `test_workflow.py` | Python script that simulates the entire workflow |
| `check_env.py` | Verifies environment is set up correctly |
| `docs/technical-documentation.md` | Detailed technical specification |
| `docs/QA_Test_Plan.md` | Step-by-step QA testing guide |
| `ASSUMPTIONS.md` | Implementation decisions & rationale |

## Architecture

The workflow has 13 nodes:
1. Schedule Trigger (Monday 9am UTC)
2. Read/Write Files from Disk
3. Extract from File
4. Date Window Calculator
5. Filter & Categorize (7 buckets)
6. Week ID Generator (ISO format)
7. Confluence Formatter (Markdown)
8. Slide Formatter (two-column text)
9. IF First Monday (monthly rollover placeholder)
10. Convert Confluence to File
11. Convert Slide to File
12. Write Confluence File
13. Write Slide File (single slide text output)

## Ticket Classification

- **FE/BE split**: Uses `component` field first, falls back to key prefix (FE-/BE-)
- **7 buckets**: FE deployed, BE deployed, FE upcoming, BE upcoming, focus items, risks/blocks, uncategorized

## Edge Cases

- Missing dates use fallback fields or show "TBD"
- Missing components use key prefix
- Empty categories show "[None]"
- Focus items without epic grouped under "Other Focus Items"

## Testing

1. Run `python3 check_env.py` to verify environment
2. Run `python3 test_workflow.py` to generate outputs
3. Follow `docs/QA_Test_Plan.md` for comprehensive testing
