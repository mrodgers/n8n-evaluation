# n8n Weekly Deployment Update - Implementation Plan

## Project Goal
Build an automated weekly deployment reporting workflow in n8n that generates stakeholder-facing reports from Jira data (mock) and outputs to Confluence (Markdown) and Google Slides (text format).

**Timebox**: 4 hours
**Strategy**: Speed + Completeness over perfection

---

## Core Requirements

### Reporting Windows
- [ ] **Deployed Last Week**: Previous Monday 00:00 to Sunday 23:59 (Pacific Time)
  - If today is Monday: Use week that just ended (7-13 days ago)
  - If today is Tue-Sun: Use most recent completed Mon-Sun week
  - Use `deployed_date` field, fallback to `updated` if missing

- [ ] **Expected Next 14 Days**: Today 00:00 through 14 days forward 23:59:59 (Pacific Time)
  - Use `target_deploy_date` field
  - Fallback: status IN ["Ready for Deploy", "In QA"] AND `fix_version` exists
  - If missing date but status="Ready for Deploy": Include with "TBD"

### Ticket Categories (7 Buckets)
- [ ] FE - Deployed Last Week
- [ ] BE - Deployed Last Week
- [ ] FE - Expected Next 14 Days
- [ ] BE - Expected Next 14 Days
- [ ] Team Focus Items (In Progress/To Do with epic, not in deployed/upcoming)
- [ ] Risks/Blocks (Status="Blocked" OR has `blocked_reason`)
- [ ] Uncategorized (items that don't fit FE/BE classification)

### FE vs BE Classification Logic
Priority order:
1. **Primary**: `component` field = "Frontend" → FE, "Backend" → BE
2. **Fallback**: Ticket key prefix = "FE-*" → Frontend, "BE-*" → Backend
3. **Default**: Neither matches → "Uncategorized"

### Edge Cases to Handle
- [ ] Missing `target_deploy_date`: Show "TBD" if status="Ready for Deploy"
- [ ] Missing `component` field: Use ticket key prefix fallback
- [ ] Missing `deployed_date`: Use `updated` field as fallback
- [ ] Empty category: Display "[None]"
- [ ] Missing `epic` field for focus items: Group under "Other Focus Items"
- [ ] No risks/blocks: Display "No known risks/blocks this week."

---

## n8n Workflow Architecture (10 Nodes)

- [ ] **Node 1**: Schedule Trigger (Monday 9am PST, manual re-run supported)
- [ ] **Node 2**: Python Code - Generate mock Jira data (25-30 tickets)
- [ ] **Node 3**: Python Code - Calculate date windows (last week, next 14 days)
- [ ] **Node 4**: Python Code - Filter & categorize into 7 buckets (FE/BE split)
- [ ] **Node 5**: Python Code - Generate ISO week identifier (e.g., "2026-W03")
- [ ] **Node 6**: Python Code - Format Confluence content (Markdown)
- [ ] **Node 7**: Python Code - Format Slide content (two-column text)
- [ ] **Node 8**: IF Node - Check if first Monday of month (for rollover logic)
- [ ] **Node 9**: Write to File - Save Confluence output: `/tmp/confluence_YYYY-WWW.md`
- [ ] **Node 10**: Write to File - Save Slide output: `/tmp/slide_YYYY-WWW.txt`

---

## Hour-by-Hour Implementation Tracker

### Hour 1: Mock Data + Core Filtering (0-60 min)

**0-15 min: Setup**
- [ ] Install/launch n8n on MacOS
- [ ] Create new workflow "Weekly Deployment Update"
- [ ] Add Schedule Trigger node (set to Monday 9am)
- [ ] Test manual execution

**15-45 min: Core Logic Nodes**
- [ ] Node 2: Python Code - Mock Jira data generator
  - [ ] Create 25-30 realistic tickets with all required fields
  - [ ] Include mix of FE/BE, deployed/upcoming, focus items, risks
  - [ ] Include edge cases: missing dates, missing components, etc.
- [ ] Node 3: Python Code - Date window calculator
  - [ ] Calculate "last week" window (previous Mon-Sun)
  - [ ] Calculate "next 14 days" window
  - [ ] Handle Pacific Time timezone
- [ ] Node 4: Python Code - Filter & categorize
  - [ ] Implement FE/BE classification logic
  - [ ] Filter into 7 buckets
  - [ ] Handle all edge cases
- [ ] Test execution, verify data flows

**45-60 min: Documentation**
- [ ] Add sticky notes to each node explaining business logic
- [ ] Document assumptions and limitations

### Hour 2: Output Formatting (60-120 min)

**0-30 min: Confluence Formatter**
- [ ] Node 6: Python Code - Generate Markdown
  - [ ] Match Appendix A structure (see original doc)
  - [ ] Handle FE/BE sections
  - [ ] Handle [None] cases
  - [ ] Add timestamp and week identifier
  - [ ] Format ticket links (even if mock)

**30-50 min: Slide Formatter**
- [ ] Node 7: Python Code - Generate two-column text
  - [ ] Match Appendix B layout (see original doc)
  - [ ] Left column: Deployed items
  - [ ] Right column: Upcoming items
  - [ ] Add focus items and risks at bottom

**50-60 min: File Output**
- [ ] Node 5: Generate ISO week identifier
- [ ] Node 9: Write to File (Confluence Markdown)
- [ ] Node 10: Write to File (Slide text)
- [ ] Test end-to-end execution
- [ ] Verify output files are created correctly

### Hour 3: Documentation Sprint (120-180 min)

**0-30 min: Technical Write-up**
- [ ] Create 1-page technical document explaining:
  - [ ] Reporting window definitions
  - [ ] FE/BE classification method
  - [ ] Edge cases handled
  - [ ] Assumptions (mock data, no API integration)
  - [ ] Workflow architecture

**30-45 min: Git Repository Setup**
- [ ] Create folder structure:
  - [ ] `/workflows/` - n8n workflow JSON export
  - [ ] `/docs/` - technical documentation
  - [ ] `/mockdata/` - sample mock data
  - [ ] `/outputs/` - example Confluence and Slide outputs
- [ ] Export n8n workflow as JSON
- [ ] Create comprehensive README.md with:
  - [ ] Project overview
  - [ ] Setup instructions
  - [ ] Execution instructions
  - [ ] Requirements

**45-60 min: Output Proof**
- [ ] Execute workflow and capture outputs
- [ ] Save example Confluence Markdown to `/outputs/`
- [ ] Save example Slide text to `/outputs/`
- [ ] Screenshot or document the n8n workflow canvas

### Hour 4: Polish & Final Review (180-240 min)

**0-20 min: Workflow Visual Cleanup**
- [ ] Organize nodes in clean left-to-right flow
- [ ] Ensure sticky notes are clear and well-positioned
- [ ] Add workflow description/documentation
- [ ] Test workflow execution one more time

**20-40 min: Edge Case Testing**
- [ ] Manually verify [None] handling for empty categories
- [ ] Verify date calculations (especially Monday logic)
- [ ] Check FE/BE/Uncategorized splits are correct
- [ ] Test with different "current date" scenarios
- [ ] Verify all 7 buckets are populated correctly

**40-55 min: Final Documentation Review**
- [ ] Proofread technical write-up
- [ ] Ensure README has clear setup instructions
- [ ] Verify all deliverables are present
- [ ] Update CLAUDE.md with build/run commands
- [ ] Check all edge cases are documented

**55-60 min: Buffer & Submission Prep**
- [ ] Final git commit with clear message
- [ ] Verify repo structure is clean
- [ ] Ensure all outputs are in correct locations
- [ ] Final manual test run

---

## Final Deliverables Checklist

- [ ] n8n workflow export JSON (runnable) in `/workflows/`
- [ ] Technical write-up in `/docs/`
- [ ] README.md with setup & execution instructions
- [ ] Mock Confluence output (Markdown) in `/outputs/`
- [ ] Mock Slide output (text) in `/outputs/`
- [ ] Example mock data in `/mockdata/`
- [ ] Clean Git repository structure
- [ ] Updated CLAUDE.md with project-specific guidance

---

## Deferred for Production (Document Only)

These are NOT implemented in the 4-hour timebox, but should be documented:

- [ ] Document Jira API integration approach (Node 2 replacement)
- [ ] Document Confluence API upsert logic (Node 9 replacement)
- [ ] Document Google Slides API integration (Node 10 replacement)
- [ ] Document monthly rollover logic (Node 8 expansion)
- [ ] Document authentication requirements (API tokens/OAuth)

---

## Success Criteria

✓ **Complete**: All 7 buckets implemented with correct filtering
✓ **Working**: End-to-end execution produces valid outputs
✓ **Documented**: Clear explanation of business logic and assumptions
✓ **Organized**: Professional Git repo structure with all deliverables
✓ **Edge Cases**: All edge cases handled and documented
✓ **On Time**: Completed within 4-hour timebox

---

## Notes & Assumptions

- Mock data only - no live API integration
- Single timezone - Pacific Time (PST/PDT)
- File outputs simulate API upsert behavior
- 25-30 mock tickets to demonstrate all scenarios
- Pre-built Python code for speed
- Focus on completeness over perfection
