# n8n Weekly Deployment Update — Implementation Plan

## Project Goal
Build an automated weekly deployment reporting workflow in n8n that generates stakeholder-facing reports from Jira data (mock) and outputs to Confluence (Markdown) and Google Slides (text format).

**Status**: v2.3 — Working in n8n with file-based output

---

## Current State (v2.3)

### Workflow Architecture (13 Nodes)

```
Schedule Trigger (Mon 9am UTC)
       ↓
Read Mock Jira Data (~/.n8n-files/mock_jira_tickets.json)
       ↓
Extract from File (JSON → items)
       ↓
Calculate Date Windows (Last Week Mon-Sun, Next 14 Days)
       ↓
Filter & Categorize (7 buckets)
       ↓
Generate Week ID (e.g., 2026-W03)
       ↓
Format Confluence (Markdown per Appendix A)
       ↓
Format Slide (Text per Appendix B)
       ↓
Is First Monday? (IF node - placeholder for monthly rollover)
       ↓
┌──────────────────────────────────────┐
│                                      │
Convert Confluence to File    Convert Slide to File
       ↓                              ↓
Write Confluence File         Write Slide File
```

### Output Paths (Upsert Simulation)

| Output | Path | Behavior |
|--------|------|----------|
| Confluence | `outputs/confluence/{YYYY-Month}/week-{WW}.md` | Overwrites on re-run |
| Slide | `outputs/slides/{YYYY}-W{WW}.txt` | Overwrites on re-run |

### Completed Requirements

| Requirement | Status |
|-------------|--------|
| FE/BE classification (component → key prefix → uncategorized) | ✅ Done |
| Date windows (UTC) - Last week Mon-Sun, Next 14 days | ✅ Done |
| Confluence format (Appendix A) | ✅ Done |
| Slide format - single slide (Appendix B) | ✅ Done |
| Empty categories show "[None]" | ✅ Done |
| Week identifier (ISO YYYY-W##) | ✅ Done |
| Schedule trigger (Monday 9am UTC) | ✅ Done |
| Upsert simulation (file overwrite) | ✅ Done |
| Monthly folder structure (Confluence output) | ✅ Done |
| Manual re-run supported | ✅ Done |

---

## Remaining Work

### 1. Monthly Folder Structure for Confluence

**Priority:** Low (optional enhancement)

**Status:** ✅ Implemented in n8n output path

**Path:** `outputs/confluence/{YYYY-Month}/week-{WW}.md`

**Why:** Simulates monthly page rollover (new Confluence page each month)

---

### 2. Documentation Updates

| Document | Status | Action Needed |
|----------|--------|---------------|
| `STATUS.md` | Outdated | Update to reflect v2.3 |
| `docs/technical-documentation.md` | Outdated | Update node count (13 nodes) |
| `docs/QA_Test_Plan.md` | Outdated | Update test steps for new paths |
| `ASSUMPTIONS.md` | Current | No changes |
| `CLAUDE.md` | Current | No changes |

---

### 3. Verify Format Compliance

**Confluence (Appendix A):**
- [x] Title: "Week of {date} Tech Update"
- [x] Section: Released Last Week (FE/BE)
- [x] Section: Upcoming Releases (FE/BE)
- [x] Section: Team Focus This Sprint
- [x] Section: Risks / Blocks
- [x] Status field in bullets
- [x] Jira links
- [x] Last updated timestamp

**Slide (Appendix B):**
- [x] Single slide (not multiple)
- [x] Two-column layout (Released | Upcoming)
- [x] Focus box at bottom
- [x] No Risks section (per Appendix B)

**Action:** Manual review of output files

---

## Not Implemented (Documented Only)

### API Integration (Requires Credentials)

**Confluence API:**
- Would replace file write with HTTP Request nodes
- GET `/rest/api/content?title=...` to find page
- PUT `/rest/api/content/{id}` to update
- POST `/rest/api/content` to create

**Google Slides API:**
- Would replace file write with HTTP Request nodes
- GET `presentations/{id}` to get slides
- POST `presentations/{id}:batchUpdate` to create/update

### PowerPoint Generation
- Not implemented in the current workflow
- Removed from the Python test script to keep outputs text-only

---

## Test Checklist

### Python Test Script
```bash
python3 test_workflow.py
```
- [ ] Generates mock data (28 tickets)
- [ ] Creates `outputs/confluence/2026-January/week-03.md`
- [ ] Creates `outputs/slides/2026-W03.txt`
- [ ] Creates `workflows/weekly_deployment_update.json`
- [ ] Updates `~/.n8n-files/mock_jira_tickets.json`

### n8n Workflow Test
1. Import `workflows/weekly_deployment_update.json`
2. Verify workflow name shows "Weekly Deployment Update v2.3"
3. Execute manually
4. Verify output files created in `outputs/`
5. Re-run and verify files overwritten (upsert behavior)

### Output Verification
- [ ] Confluence has "Week of {date} Tech Update" title
- [ ] Confluence has all 4 main sections
- [ ] Confluence shows "[None]" for empty categories
- [ ] Slide has two-column layout
- [ ] Slide has Focus section (no Risks)
- [ ] Both outputs use correct week identifier

---

## Quick Reference

### Run Tests
```bash
source flowbot/bin/activate  # if needed
python3 test_workflow.py
```

### Import to n8n
```
File: workflows/weekly_deployment_update.json
Name: Weekly Deployment Update v2.3
```

### Output Locations
```
outputs/
├── confluence/
│   └── week-03.md          # n8n output (flat)
│   └── 2026-January/
│       └── week-03.md      # Python output (monthly folders)
└── slides/
    └── 2026-W03.txt
```

### Mock Data
```
~/.n8n-files/mock_jira_tickets.json   # n8n reads from here
mockdata/mock_jira_tickets.json       # Python reference copy
```

---

## Version History

| Version | Changes |
|---------|---------|
| v2.3 | Convert + Write nodes for file output (working) |
| v2.2 | Attempted Code node with fs (blocked by n8n security) |
| v2.1 | Attempted readWriteFile (binary input required) |
| v2.0 | Initial upsert paths (timestamped output) |
| v1.x | Original implementation with timestamped files |
