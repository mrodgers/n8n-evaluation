# Weekly Deployment Update Automation — Implementation Write-up

## Reporting Window Definitions

**"Deployed Last Week"**: Previous Monday 00:00 UTC through Sunday 23:59 UTC
- If today is Monday, "last week" = the 7 days ending yesterday (Sunday)
- If today is Tuesday-Sunday, "last week" = the most recent completed Mon-Sun week

**"Expected Next 14 Days"**: Today 00:00 UTC through +14 calendar days 23:59 UTC
- Items included if `target_deploy_date` falls within this window
- Items with status "Ready for Deploy" or "In QA" with a `fix_version` are also included

## FE/BE Classification Method

Classification priority:
1. **Component field** — `Frontend` → FE, `Backend` → BE
2. **Key prefix fallback** — `FE-*` → FE, `BE-*` → BE
3. **Uncategorized** — Items that don't match above are still included (not dropped)

## Definition of "Deployed" and "Expected"

| Category | Criteria |
|----------|----------|
| **Deployed** | `status = "Done"` AND (`deployed_date` OR `updated`) within last week window |
| **Expected** | `status` in ["Ready for Deploy", "In QA"] AND (`target_deploy_date` in next 14 days OR has `fix_version`) |
| **Focus Items** | `status` in ["In Progress", "To Do"] — grouped by epic |
| **Risks/Blocks** | `status = "Blocked"` OR has `blocked_reason` field |

## Edge Cases Handled

- **Missing `deployed_date`**: Falls back to `updated` field
- **Missing `target_deploy_date`**: Shows "TBD" for Ready for Deploy items
- **Missing epic**: Grouped under "Other Focus Items"
- **Missing component**: Uses key prefix; if neither, goes to Uncategorized
- **Blocked with non-Blocked status**: `blocked_reason` field overrides status
- **Empty categories**: Display "[None]" rather than hiding section

## Assumptions (Mock Data)

- **28 mock tickets** covering all scenarios: deployed, upcoming, focus, blocked, uncategorized
- **Relative dates**: Mock data uses `days_ago(N)` / `days_from_now(N)` so tests work on any date
- **Jira URL format**: `https://jira.example.com/browse/{key}` (placeholder)
- **Timezone**: All calculations in UTC
- **File output**: Timestamped files (actual Confluence/Slides API would do upsert)

## Output Formats

- **Confluence**: Markdown matching Appendix A — title "Week of {date} Tech Update", status in each bullet, "Last updated" footer
- **Slide**: Text layout matching Appendix B — two-column (Released/Upcoming) + Focus box at bottom
