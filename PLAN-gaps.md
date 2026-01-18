# Gap Implementation Plan

## Overview

Three gaps to fill:
1. Confluence API integration
2. Google Slides API integration
3. Upsert logic (built into 1 & 2)

---

## Gap 1: Confluence API Integration

### What's Needed

| Item | Details |
|------|---------|
| Credentials | Atlassian API token + email |
| Base URL | `https://{domain}.atlassian.net/wiki/rest/api` |
| Space Key | e.g., `TECH2026` |
| Auth | Basic Auth (email:api_token as base64) |

### n8n Nodes to Add

```
Format Confluence → HTTP Request (Get Page) → IF (Page Exists?)
                                                    ↓ Yes: HTTP Request (Update Page)
                                                    ↓ No:  HTTP Request (Create Page)
```

### API Calls

**1. Find page by title:**
```
GET /rest/api/content?title={title}&spaceKey={space}&expand=version
```

**2. Create page:**
```
POST /rest/api/content
Body: { type: "page", title: "...", space: { key: "..." }, body: { storage: { value: "...", representation: "wiki" } } }
```

**3. Update page:**
```
PUT /rest/api/content/{pageId}
Body: { version: { number: currentVersion + 1 }, title: "...", body: { storage: { value: "...", representation: "wiki" } } }
```

### Monthly Rollover Logic

```javascript
// In Code node before Confluence API call
const now = new Date();
const isFirstMonday = now.getDate() <= 7 && now.getDay() === 1;
const monthName = now.toLocaleString('en-US', { month: 'long' });
const year = now.getFullYear();

const monthlyPageTitle = `${year} - ${monthName} Tech Updates`;
const weeklyTitle = `Week of ${weekStart} Tech Update`;

// If first Monday: create new monthly page, then add weekly section
// Else: find monthly page, append/update weekly section
```

---

## Gap 2: Google Slides API Integration

### What's Needed

| Item | Details |
|------|---------|
| Credentials | Google OAuth2 (or Service Account) |
| Scope | `https://www.googleapis.com/auth/presentations` |
| Presentation ID | ID of the deck to update |

### n8n Nodes to Add

```
Format Slide → HTTP Request (Get Slides) → Code (Find Week Slide)
                                                    ↓ Exists: HTTP Request (Update Slide)
                                                    ↓ Not:    HTTP Request (Create Slide)
```

### API Calls

**1. Get presentation:**
```
GET https://slides.googleapis.com/v1/presentations/{presentationId}
```

**2. Create slide:**
```
POST https://slides.googleapis.com/v1/presentations/{presentationId}:batchUpdate
Body: { requests: [{ createSlide: { slideLayoutReference: { predefinedLayout: "BLANK" } } }] }
```

**3. Update slide content:**
```
POST https://slides.googleapis.com/v1/presentations/{presentationId}:batchUpdate
Body: { requests: [{ deleteText: {...}, insertText: {...} }] }
```

### Week Identification

- Store week ID in slide speaker notes or a text box
- Search slides for matching week ID
- Update if found, create if not

---

## Gap 3: Upsert Logic

Built into Gaps 1 & 2. Key principle:

```
1. Generate week_identifier (e.g., "2026-W03")
2. Search for existing content with that identifier
3. If found → Update
4. If not found → Create
```

---

## Implementation Options

### Option A: Mock Mode (Current)
- Keep file-based output
- Document that API integration is "ready to wire up"
- Pros: No credentials needed, demonstrates logic
- Cons: Not end-to-end

### Option B: Add API Nodes (Requires Credentials)
- Add HTTP Request nodes to workflow
- Configure credentials in n8n
- Pros: Fully functional
- Cons: Need real Confluence/Google accounts

### Option C: Hybrid
- Add API nodes with placeholder credentials
- Include setup instructions
- User configures their own credentials
- Pros: Workflow is complete, user just adds creds

---

## Recommended Approach: Mock API Behavior

Since we don't have Confluence/Slides API access, we'll **mock the behavior** with file-based output that demonstrates the upsert logic.

### Mock Implementation

**Confluence Mock:**
- Output to `outputs/confluence/` directory
- Monthly page = folder (e.g., `2026-January/`)
- Weekly section = file (e.g., `week-03.md`)
- Re-run overwrites same file (simulates upsert)

**Slide Mock:**
- Output to `outputs/slides/` directory
- One file per week (e.g., `2026-W03.txt`)
- Re-run overwrites same file (simulates upsert)

### Key Changes

1. **Remove timestamps from filenames** - use week ID only
2. **Organize by month** for Confluence (simulates monthly pages)
3. **Overwrite on re-run** (demonstrates upsert behavior)
4. **Add "API simulation" comments** in output files

---

## Implementation Plan

| Step | Task |
|------|------|
| 1 | Update output paths to use `outputs/confluence/{month}/` and `outputs/slides/` |
| 2 | Change filenames to use week ID only (no timestamp) for upsert simulation |
| 3 | Add monthly rollover logic for Confluence folder structure |
| 4 | Update workflow JSON to match |
| 5 | Document mock behavior vs real API behavior |
