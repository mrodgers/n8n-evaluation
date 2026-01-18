#!/usr/bin/env python3
"""
Standalone test script for Weekly Deployment Update workflow.
Simulates all n8n nodes and generates outputs for verification.
"""

import json
from datetime import datetime, timedelta, timezone
import os
import shutil

# Use UTC for all date calculations (extensible to custom timezones later)
today = datetime.now(timezone.utc)

def days_ago(n):
    return (today - timedelta(days=n)).strftime('%Y-%m-%d')

def days_from_now(n):
    return (today + timedelta(days=n)).strftime('%Y-%m-%d')

# ============================================================
# Node 2: Mock Jira Data Generator
# ============================================================
def generate_mock_jira_data():
    """Generate 28 mock tickets covering all scenarios."""
    tickets = [
        # === DEPLOYED LAST WEEK - Frontend ===
        {
            "key": "FE-101",
            "summary": "Implement new dashboard layout",
            "status": "Done",
            "component": "Frontend",
            "deployed_date": days_ago(5),
            "updated": days_ago(5),
            "epic": "Dashboard Redesign",
            "fix_version": "2026.1"
        },
        {
            "key": "FE-102",
            "summary": "Add dark mode toggle",
            "status": "Done",
            "component": "Frontend",
            "deployed_date": days_ago(6),
            "updated": days_ago(6),
            "epic": "UX Improvements",
            "fix_version": "2026.1"
        },
        {
            "key": "FE-103",
            "summary": "Fix responsive navigation menu",
            "status": "Done",
            "component": "Frontend",
            "deployed_date": days_ago(4),
            "updated": days_ago(4),
            "epic": "Mobile Support",
            "fix_version": "2026.1"
        },
        # Edge case: missing deployed_date, use updated as fallback
        {
            "key": "FE-104",
            "summary": "Update form validation messages",
            "status": "Done",
            "component": "Frontend",
            "deployed_date": None,
            "updated": days_ago(7),
            "epic": "UX Improvements",
            "fix_version": "2026.1"
        },

        # === DEPLOYED LAST WEEK - Backend ===
        {
            "key": "BE-201",
            "summary": "Optimize database queries for reports",
            "status": "Done",
            "component": "Backend",
            "deployed_date": days_ago(5),
            "updated": days_ago(5),
            "epic": "Performance",
            "fix_version": "2026.1"
        },
        {
            "key": "BE-202",
            "summary": "Add rate limiting to API endpoints",
            "status": "Done",
            "component": "Backend",
            "deployed_date": days_ago(6),
            "updated": days_ago(6),
            "epic": "Security",
            "fix_version": "2026.1"
        },
        {
            "key": "BE-203",
            "summary": "Implement webhook retry logic",
            "status": "Done",
            "component": "Backend",
            "deployed_date": days_ago(3),
            "updated": days_ago(3),
            "epic": "Integrations",
            "fix_version": "2026.1"
        },

        # === EXPECTED NEXT 14 DAYS - Frontend ===
        {
            "key": "FE-105",
            "summary": "Build user settings page",
            "status": "Ready for Deploy",
            "component": "Frontend",
            "target_deploy_date": days_from_now(3),
            "updated": days_ago(1),
            "epic": "User Management",
            "fix_version": "2026.2"
        },
        {
            "key": "FE-106",
            "summary": "Add export to PDF feature",
            "status": "In QA",
            "component": "Frontend",
            "target_deploy_date": days_from_now(7),
            "updated": days_ago(2),
            "epic": "Reports",
            "fix_version": "2026.2"
        },
        # Edge case: Ready for Deploy but missing target_deploy_date -> TBD
        {
            "key": "FE-107",
            "summary": "Implement notification center",
            "status": "Ready for Deploy",
            "component": "Frontend",
            "target_deploy_date": None,
            "updated": days_ago(1),
            "epic": "Notifications",
            "fix_version": "2026.2"
        },
        {
            "key": "FE-108",
            "summary": "Add keyboard shortcuts help modal",
            "status": "In QA",
            "component": "Frontend",
            "target_deploy_date": days_from_now(10),
            "updated": days_ago(3),
            "epic": "UX Improvements",
            "fix_version": "2026.2"
        },

        # === EXPECTED NEXT 14 DAYS - Backend ===
        {
            "key": "BE-204",
            "summary": "Add batch processing endpoint",
            "status": "Ready for Deploy",
            "component": "Backend",
            "target_deploy_date": days_from_now(2),
            "updated": days_ago(1),
            "epic": "API Enhancements",
            "fix_version": "2026.2"
        },
        {
            "key": "BE-205",
            "summary": "Implement audit logging",
            "status": "In QA",
            "component": "Backend",
            "target_deploy_date": days_from_now(5),
            "updated": days_ago(2),
            "epic": "Security",
            "fix_version": "2026.2"
        },
        {
            "key": "BE-206",
            "summary": "Add GraphQL support",
            "status": "Ready for Deploy",
            "component": "Backend",
            "target_deploy_date": days_from_now(12),
            "updated": days_ago(4),
            "epic": "API Enhancements",
            "fix_version": "2026.2"
        },

        # === TEAM FOCUS ITEMS (In Progress/To Do with epic) ===
        {
            "key": "FE-109",
            "summary": "Redesign checkout flow",
            "status": "In Progress",
            "component": "Frontend",
            "updated": days_ago(1),
            "epic": "Checkout Revamp",
            "fix_version": "2026.3"
        },
        {
            "key": "BE-207",
            "summary": "Migrate to new payment processor",
            "status": "In Progress",
            "component": "Backend",
            "updated": days_ago(2),
            "epic": "Checkout Revamp",
            "fix_version": "2026.3"
        },
        {
            "key": "FE-110",
            "summary": "Build A/B testing framework",
            "status": "To Do",
            "component": "Frontend",
            "updated": days_ago(5),
            "epic": "Analytics",
            "fix_version": "2026.3"
        },
        {
            "key": "BE-208",
            "summary": "Implement feature flags service",
            "status": "In Progress",
            "component": "Backend",
            "updated": days_ago(3),
            "epic": "Analytics",
            "fix_version": "2026.3"
        },
        # Edge case: focus item without epic -> "Other Focus Items"
        {
            "key": "BE-209",
            "summary": "Update deprecated dependencies",
            "status": "In Progress",
            "component": "Backend",
            "updated": days_ago(1),
            "epic": None,
            "fix_version": "2026.2"
        },

        # === RISKS/BLOCKS ===
        {
            "key": "FE-111",
            "summary": "Third-party widget integration failing",
            "status": "Blocked",
            "component": "Frontend",
            "updated": days_ago(2),
            "epic": "Integrations",
            "blocked_reason": "Waiting for vendor API fix",
            "fix_version": "2026.2"
        },
        {
            "key": "BE-210",
            "summary": "Database migration script",
            "status": "In Progress",
            "component": "Backend",
            "updated": days_ago(1),
            "epic": "Infrastructure",
            "blocked_reason": "Requires DBA approval for production",
            "fix_version": "2026.2"
        },
        {
            "key": "BE-211",
            "summary": "SSL certificate renewal",
            "status": "Blocked",
            "component": "Backend",
            "updated": days_ago(3),
            "epic": "Security",
            "blocked_reason": "Pending security team review",
            "fix_version": "2026.2"
        },

        # === UNCATEGORIZED (missing component, use key prefix) ===
        # Edge case: No component field, but has FE- prefix
        {
            "key": "FE-112",
            "summary": "Update privacy policy page",
            "status": "Done",
            "component": None,
            "deployed_date": days_ago(4),
            "updated": days_ago(4),
            "epic": "Legal",
            "fix_version": "2026.1"
        },
        # Edge case: No component field and non-standard key prefix
        {
            "key": "OPS-301",
            "summary": "Update CI/CD pipeline",
            "status": "Done",
            "component": None,
            "deployed_date": days_ago(5),
            "updated": days_ago(5),
            "epic": "Infrastructure",
            "fix_version": "2026.1"
        },
        {
            "key": "OPS-302",
            "summary": "Configure monitoring alerts",
            "status": "Ready for Deploy",
            "component": None,
            "target_deploy_date": days_from_now(4),
            "updated": days_ago(2),
            "epic": "Infrastructure",
            "fix_version": "2026.2"
        },
        {
            "key": "DATA-401",
            "summary": "Build analytics dashboard",
            "status": "In Progress",
            "component": None,
            "updated": days_ago(1),
            "epic": "Analytics",
            "fix_version": "2026.3"
        },
        # Additional tickets
        {
            "key": "FE-113",
            "summary": "Implement lazy loading for images",
            "status": "In QA",
            "component": "Frontend",
            "target_deploy_date": days_from_now(6),
            "updated": days_ago(1),
            "epic": "Performance",
            "fix_version": "2026.2"
        },
        {
            "key": "BE-212",
            "summary": "Add caching layer for API responses",
            "status": "In QA",
            "component": "Backend",
            "target_deploy_date": days_from_now(8),
            "updated": days_ago(2),
            "epic": "Performance",
            "fix_version": "2026.2"
        }
    ]
    return tickets

# ============================================================
# Node 3: Date Window Calculator
# ============================================================
def calculate_date_windows():
    """Calculate reporting windows in UTC."""
    current_weekday = today.weekday()  # 0=Monday, 6=Sunday

    if current_weekday == 0:  # Monday
        last_week_end = today - timedelta(days=1)  # Yesterday (Sunday)
        last_week_start = last_week_end - timedelta(days=6)  # Previous Monday
    else:
        days_since_monday = current_weekday
        last_week_end = today - timedelta(days=days_since_monday)  # Last Sunday
        last_week_start = last_week_end - timedelta(days=6)  # Previous Monday

    next_14_start = today
    next_14_end = today + timedelta(days=14)

    return {
        "last_week_start": last_week_start.strftime('%Y-%m-%d'),
        "last_week_end": last_week_end.strftime('%Y-%m-%d'),
        "next_14_start": next_14_start.strftime('%Y-%m-%d'),
        "next_14_end": next_14_end.strftime('%Y-%m-%d'),
        "current_date": today.strftime('%Y-%m-%d'),
        "timezone": "UTC"
    }

# ============================================================
# Node 4: Filter & Categorize
# ============================================================
def classify_ticket(ticket):
    """Classify ticket as FE, BE, or Uncategorized."""
    component = ticket.get("component")
    key = ticket.get("key", "")

    if component == "Frontend":
        return "FE"
    elif component == "Backend":
        return "BE"

    if key.startswith("FE-"):
        return "FE"
    elif key.startswith("BE-"):
        return "BE"

    return "Uncategorized"

def parse_date(date_str):
    """Parse date string to datetime."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:
        return None

def filter_and_categorize(tickets, windows):
    """Filter and categorize tickets into 7 buckets."""
    last_week_start = datetime.strptime(windows["last_week_start"], '%Y-%m-%d')
    last_week_end = datetime.strptime(windows["last_week_end"], '%Y-%m-%d')
    next_14_start = datetime.strptime(windows["next_14_start"], '%Y-%m-%d')
    next_14_end = datetime.strptime(windows["next_14_end"], '%Y-%m-%d')

    buckets = {
        "fe_deployed": [],
        "be_deployed": [],
        "fe_upcoming": [],
        "be_upcoming": [],
        "focus_items": {},
        "risks_blocks": [],
        "uncategorized": []
    }

    processed = set()

    for ticket in tickets:
        key = ticket.get("key")
        status = ticket.get("status", "")
        classification = classify_ticket(ticket)

        # Check for risks/blocks first
        if status == "Blocked" or ticket.get("blocked_reason"):
            buckets["risks_blocks"].append(ticket)
            processed.add(key)
            continue

        # Check if deployed last week
        if status == "Done":
            deploy_date = parse_date(ticket.get("deployed_date")) or parse_date(ticket.get("updated"))
            if deploy_date and last_week_start <= deploy_date <= last_week_end:
                if classification == "FE":
                    buckets["fe_deployed"].append(ticket)
                elif classification == "BE":
                    buckets["be_deployed"].append(ticket)
                else:
                    buckets["uncategorized"].append(ticket)
                processed.add(key)
                continue

        # Check if expected next 14 days
        if status in ["Ready for Deploy", "In QA"]:
            target_date = parse_date(ticket.get("target_deploy_date"))
            in_window = target_date and next_14_start <= target_date <= next_14_end
            has_fallback = ticket.get("fix_version") is not None

            if in_window or has_fallback:
                if classification == "FE":
                    buckets["fe_upcoming"].append(ticket)
                elif classification == "BE":
                    buckets["be_upcoming"].append(ticket)
                else:
                    buckets["uncategorized"].append(ticket)
                processed.add(key)
                continue

        # Check if focus item
        if status in ["In Progress", "To Do"]:
            epic = ticket.get("epic") or "Other Focus Items"
            if epic not in buckets["focus_items"]:
                buckets["focus_items"][epic] = []
            buckets["focus_items"][epic].append(ticket)
            processed.add(key)
            continue

        # Anything else goes to uncategorized
        if key not in processed:
            buckets["uncategorized"].append(ticket)

    # Convert focus_items to list format
    focus_items_list = []
    for epic, items in buckets["focus_items"].items():
        focus_items_list.append({"epic": epic, "tickets": items})

    return {
        "fe_deployed": buckets["fe_deployed"],
        "be_deployed": buckets["be_deployed"],
        "fe_upcoming": buckets["fe_upcoming"],
        "be_upcoming": buckets["be_upcoming"],
        "focus_items": focus_items_list,
        "risks_blocks": buckets["risks_blocks"],
        "uncategorized": buckets["uncategorized"]
    }

# ============================================================
# Node 5: Generate Week ID
# ============================================================
def generate_week_id():
    """Generate ISO week identifier."""
    iso_year, iso_week, _ = today.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"

# ============================================================
# Node 6: Confluence Formatter
# ============================================================
def format_confluence(buckets, windows, week_id, timestamp):
    """Generate Markdown for Confluence."""

    def format_ticket(ticket, include_date=False):
        key = ticket.get("key", "")
        summary = ticket.get("summary", "")
        url = f"https://jira.example.com/browse/{key}"
        line = f"- [{key}]({url}): {summary}"

        if include_date:
            date = ticket.get("target_deploy_date") or ticket.get("deployed_date")
            if date:
                line += f" *(Target: {date})*"
            elif ticket.get("status") == "Ready for Deploy":
                line += " *(Target: TBD)*"
        return line

    def format_bucket(tickets, title, include_date=False):
        if not tickets:
            return f"### {title}\n\n[None]\n"
        lines = [f"### {title}\n"]
        for ticket in tickets:
            lines.append(format_ticket(ticket, include_date))
        return "\n".join(lines) + "\n"

    md_lines = [
        f"# Weekly Deployment Update - {week_id}",
        "",
        f"**Report Period**: {windows.get('last_week_start', '')} to {windows.get('last_week_end', '')}",
        f"**Generated**: {timestamp}",
        "",
        "---",
        "",
        "## Deployed Last Week",
        ""
    ]

    md_lines.append(format_bucket(buckets.get("fe_deployed", []), "Frontend"))
    md_lines.append("")
    md_lines.append(format_bucket(buckets.get("be_deployed", []), "Backend"))
    md_lines.append("")

    md_lines.extend([
        "---",
        "",
        "## Expected Next 14 Days",
        f"**Window**: {windows.get('next_14_start', '')} to {windows.get('next_14_end', '')}",
        ""
    ])

    md_lines.append(format_bucket(buckets.get("fe_upcoming", []), "Frontend", include_date=True))
    md_lines.append("")
    md_lines.append(format_bucket(buckets.get("be_upcoming", []), "Backend", include_date=True))
    md_lines.append("")

    md_lines.extend([
        "---",
        "",
        "## Team Focus Items",
        ""
    ])

    focus_items = buckets.get("focus_items", [])
    if not focus_items:
        md_lines.append("[None]\n")
    else:
        for group in focus_items:
            epic = group.get("epic", "Other")
            tickets = group.get("tickets", [])
            md_lines.append(f"### {epic}\n")
            for ticket in tickets:
                md_lines.append(format_ticket(ticket))
            md_lines.append("")

    md_lines.extend([
        "---",
        "",
        "## Risks & Blockers",
        ""
    ])

    risks = buckets.get("risks_blocks", [])
    if not risks:
        md_lines.append("No known risks/blocks this week.\n")
    else:
        for ticket in risks:
            key = ticket.get("key", "")
            summary = ticket.get("summary", "")
            reason = ticket.get("blocked_reason", "No details provided")
            url = f"https://jira.example.com/browse/{key}"
            md_lines.append(f"- **[{key}]({url})**: {summary}")
            md_lines.append(f"  - *Reason*: {reason}")
        md_lines.append("")

    uncategorized = buckets.get("uncategorized", [])
    if uncategorized:
        md_lines.extend([
            "---",
            "",
            "## Other Items",
            ""
        ])
        for ticket in uncategorized:
            md_lines.append(format_ticket(ticket))
        md_lines.append("")

    return "\n".join(md_lines)

# ============================================================
# Node 7: Slide Formatter
# ============================================================
def format_slide(buckets, windows, week_id, timestamp):
    """Generate two-column text for slides (aligned with NEW_WORKING workflow)."""
    newline = "\n"

    def format_ticket_simple(ticket):
        key = ticket.get("key", "")
        summary = ticket.get("summary", "")
        return f"* {key}: {summary}"

    def format_ticket_with_date(ticket):
        key = ticket.get("key", "")
        summary = ticket.get("summary", "")
        date = ticket.get("target_deploy_date")
        if date:
            return f"* {key}: {summary} [{date}]"
        if ticket.get("status") == "Ready for Deploy":
            return f"* {key}: {summary} [TBD]"
        return f"* {key}: {summary}"

    slide_lines = [
        f"WEEKLY DEPLOYMENT UPDATE - {week_id}",
        "=" * 50,
        "",
        "=" * 50,
        "                    SLIDE 1: OVERVIEW",
        "=" * 50,
        "",
        "+-----------------------------+-----------------------------+",
        "|     DEPLOYED LAST WEEK      |    EXPECTED NEXT 14 DAYS    |",
        "+-----------------------------+-----------------------------+",
        "",
    ]

    slide_lines.append("LEFT COLUMN (Deployed):")
    slide_lines.append("-" * 30)
    fe_deployed = buckets.get("fe_deployed", [])
    be_deployed = buckets.get("be_deployed", [])

    if fe_deployed:
        slide_lines.append("FRONTEND:")
        for t in fe_deployed[:5]:
            slide_lines.append(format_ticket_simple(t))
        slide_lines.append("")
    if be_deployed:
        slide_lines.append("BACKEND:")
        for t in be_deployed[:5]:
            slide_lines.append(format_ticket_simple(t))
    if not fe_deployed and not be_deployed:
        slide_lines.append("[None]")

    slide_lines.append("")
    slide_lines.append("RIGHT COLUMN (Upcoming):")
    slide_lines.append("-" * 30)

    fe_upcoming = buckets.get("fe_upcoming", [])
    be_upcoming = buckets.get("be_upcoming", [])

    if fe_upcoming:
        slide_lines.append("FRONTEND:")
        for t in fe_upcoming[:5]:
            slide_lines.append(format_ticket_with_date(t))
        slide_lines.append("")
    if be_upcoming:
        slide_lines.append("BACKEND:")
        for t in be_upcoming[:5]:
            slide_lines.append(format_ticket_with_date(t))
    if not fe_upcoming and not be_upcoming:
        slide_lines.append("[None]")

    slide_lines.extend([
        "",
        "=" * 50,
        "            SLIDE 2: FOCUS & RISKS",
        "=" * 50,
        "",
        "TEAM FOCUS ITEMS:",
        "-" * 30,
    ])

    focus_items = buckets.get("focus_items", [])
    if not focus_items:
        slide_lines.append("[None]")
    else:
        for group in focus_items:
            epic = group.get("epic", "Other")
            slide_lines.append(f"{newline}> {epic}:")
            for ticket in group.get("tickets", [])[:3]:
                slide_lines.append(format_ticket_simple(ticket))

    slide_lines.extend([
        "",
        "RISKS & BLOCKERS:",
        "-" * 30,
    ])

    risks = buckets.get("risks_blocks", [])
    if not risks:
        slide_lines.append("No known risks/blocks this week.")
    else:
        for ticket in risks:
            key = ticket.get("key", "")
            summary = ticket.get("summary", "")
            reason = ticket.get("blocked_reason", "No details")
            slide_lines.append(f"! {key}: {summary}")
            slide_lines.append(f"  -> {reason}")

    slide_lines.extend([
        "",
        "=" * 50,
        f"Generated: {timestamp}",
        "=" * 50,
    ])

    return newline.join(slide_lines)

# ============================================================
# Node 7b: PowerPoint Generator (opens in Google Slides)
# ============================================================
def generate_powerpoint(buckets, windows, week_id, timestamp):
    """Generate PowerPoint file that can be opened in Google Slides."""
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN

    prs = Presentation()
    prs.slide_width = Inches(13.333)  # Widescreen 16:9
    prs.slide_height = Inches(7.5)

    # ===== SLIDE 1: Title Slide =====
    slide_layout = prs.slide_layouts[6]  # Blank layout
    slide1 = prs.slides.add_slide(slide_layout)

    # Title
    title_box = slide1.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12.333), Inches(1))
    title_frame = title_box.text_frame
    title_para = title_frame.paragraphs[0]
    title_para.text = f"Weekly Deployment Update"
    title_para.font.size = Pt(44)
    title_para.font.bold = True
    title_para.alignment = PP_ALIGN.CENTER

    # Subtitle (week ID)
    subtitle_box = slide1.shapes.add_textbox(Inches(0.5), Inches(3.5), Inches(12.333), Inches(0.5))
    subtitle_frame = subtitle_box.text_frame
    subtitle_para = subtitle_frame.paragraphs[0]
    subtitle_para.text = week_id
    subtitle_para.font.size = Pt(28)
    subtitle_para.alignment = PP_ALIGN.CENTER

    # Date info
    date_box = slide1.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(12.333), Inches(0.5))
    date_frame = date_box.text_frame
    date_para = date_frame.paragraphs[0]
    date_para.text = f"Generated: {timestamp}"
    date_para.font.size = Pt(14)
    date_para.alignment = PP_ALIGN.CENTER

    # ===== SLIDE 2: Overview (Deployed / Upcoming) =====
    slide2 = prs.slides.add_slide(slide_layout)

    # Header
    header_box = slide2.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.333), Inches(0.5))
    header_frame = header_box.text_frame
    header_para = header_frame.paragraphs[0]
    header_para.text = "Deployed Last Week | Expected Next 14 Days"
    header_para.font.size = Pt(24)
    header_para.font.bold = True
    header_para.alignment = PP_ALIGN.CENTER

    def add_ticket_list(slide, tickets, x, y, width, height, title, include_date=False):
        """Add a text box with ticket list."""
        box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(width), Inches(height))
        tf = box.text_frame
        tf.word_wrap = True

        # Title
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True

        if not tickets:
            p = tf.add_paragraph()
            p.text = "[None]"
            p.font.size = Pt(12)
        else:
            for ticket in tickets[:6]:  # Limit for readability
                p = tf.add_paragraph()
                key = ticket.get("key", "")
                summary = ticket.get("summary", "")
                if include_date:
                    date = ticket.get("target_deploy_date")
                    if date:
                        p.text = f"• {key}: {summary} [{date}]"
                    elif ticket.get("status") == "Ready for Deploy":
                        p.text = f"• {key}: {summary} [TBD]"
                    else:
                        p.text = f"• {key}: {summary}"
                else:
                    p.text = f"• {key}: {summary}"
                p.font.size = Pt(11)

    # Left column - Deployed
    add_ticket_list(slide2, buckets.get("fe_deployed", []), 0.5, 1, 6, 2.5, "Frontend (Deployed)")
    add_ticket_list(slide2, buckets.get("be_deployed", []), 0.5, 3.8, 6, 2.5, "Backend (Deployed)")

    # Right column - Upcoming
    add_ticket_list(slide2, buckets.get("fe_upcoming", []), 6.833, 1, 6, 2.5, "Frontend (Upcoming)", include_date=True)
    add_ticket_list(slide2, buckets.get("be_upcoming", []), 6.833, 3.8, 6, 2.5, "Backend (Upcoming)", include_date=True)

    # ===== SLIDE 3: Focus Items =====
    slide3 = prs.slides.add_slide(slide_layout)

    header_box = slide3.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.333), Inches(0.5))
    header_frame = header_box.text_frame
    header_para = header_frame.paragraphs[0]
    header_para.text = "Team Focus Items"
    header_para.font.size = Pt(24)
    header_para.font.bold = True

    focus_items = buckets.get("focus_items", [])
    y_pos = 1
    for group in focus_items[:4]:  # Limit groups
        epic = group.get("epic", "Other")
        tickets = group.get("tickets", [])

        box = slide3.shapes.add_textbox(Inches(0.5), Inches(y_pos), Inches(12.333), Inches(1.5))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = epic
        p.font.size = Pt(14)
        p.font.bold = True

        for ticket in tickets[:3]:
            p = tf.add_paragraph()
            p.text = f"• {ticket.get('key', '')}: {ticket.get('summary', '')}"
            p.font.size = Pt(11)

        y_pos += 1.5

    # ===== SLIDE 4: Risks & Blockers =====
    slide4 = prs.slides.add_slide(slide_layout)

    header_box = slide4.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.333), Inches(0.5))
    header_frame = header_box.text_frame
    header_para = header_frame.paragraphs[0]
    header_para.text = "Risks & Blockers"
    header_para.font.size = Pt(24)
    header_para.font.bold = True

    risks = buckets.get("risks_blocks", [])
    box = slide4.shapes.add_textbox(Inches(0.5), Inches(1), Inches(12.333), Inches(5.5))
    tf = box.text_frame
    tf.word_wrap = True

    if not risks:
        p = tf.paragraphs[0]
        p.text = "No known risks or blockers this week."
        p.font.size = Pt(14)
    else:
        first = True
        for ticket in risks:
            if first:
                p = tf.paragraphs[0]
                first = False
            else:
                p = tf.add_paragraph()

            key = ticket.get("key", "")
            summary = ticket.get("summary", "")
            reason = ticket.get("blocked_reason", "No details provided")

            p.text = f"⚠ {key}: {summary}"
            p.font.size = Pt(14)
            p.font.bold = True

            p = tf.add_paragraph()
            p.text = f"    → {reason}"
            p.font.size = Pt(12)

    return prs

# ============================================================
# Node 8: Workflow JSON Generator
# ============================================================
def generate_workflow_json():
    """Generate the complete n8n workflow JSON structure."""
    import uuid

    # Generate unique IDs for nodes
    def new_id():
        return str(uuid.uuid4())

    # JavaScript code for each Code node
    js_calculate_date_windows = '''const inputItems = $input.all();
let tickets = [];

if (inputItems.length === 1 && Array.isArray(inputItems[0].json?.data)) {
  tickets = inputItems[0].json.data;
} else if (inputItems.length === 1 && Array.isArray(inputItems[0].json)) {
  tickets = inputItems[0].json;
} else {
  tickets = inputItems.map((item) => item.json);
}

const now = new Date();
const today = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()));
const currentWeekday = (today.getUTCDay() + 6) % 7; // Monday=0

let lastWeekEnd;
let lastWeekStart;
if (currentWeekday === 0) {
  lastWeekEnd = new Date(today);
  lastWeekEnd.setUTCDate(today.getUTCDate() - 1);
  lastWeekStart = new Date(lastWeekEnd);
  lastWeekStart.setUTCDate(lastWeekEnd.getUTCDate() - 6);
} else {
  lastWeekEnd = new Date(today);
  lastWeekEnd.setUTCDate(today.getUTCDate() - currentWeekday);
  lastWeekStart = new Date(lastWeekEnd);
  lastWeekStart.setUTCDate(lastWeekEnd.getUTCDate() - 6);
}

const next14Start = new Date(today);
const next14End = new Date(today);
next14End.setUTCDate(today.getUTCDate() + 14);

const formatDate = (d) => d.toISOString().slice(0, 10);

return [
  {
    json: {
      tickets,
      date_windows: {
        last_week_start: formatDate(lastWeekStart),
        last_week_end: formatDate(lastWeekEnd),
        next_14_start: formatDate(next14Start),
        next_14_end: formatDate(next14End),
        current_date: formatDate(today),
        timezone: 'UTC',
      },
      generated_at: now.toISOString(),
    },
  },
];
'''

    js_filter_categorize = '''const input = $input.first().json;
const tickets = input.tickets || [];
const windows = input.date_windows || {};

const parseDate = (dateStr) => {
  if (!dateStr) return null;
  const d = new Date(`${dateStr}T00:00:00Z`);
  return Number.isNaN(d.getTime()) ? null : d;
};

const lastWeekStart = parseDate(windows.last_week_start);
const lastWeekEnd = parseDate(windows.last_week_end);
const next14Start = parseDate(windows.next_14_start);
const next14End = parseDate(windows.next_14_end);

const buckets = {
  fe_deployed: [],
  be_deployed: [],
  fe_upcoming: [],
  be_upcoming: [],
  focus_items: {},
  risks_blocks: [],
  uncategorized: [],
};

const classifyTicket = (ticket) => {
  const component = ticket.component;
  const key = ticket.key || '';

  if (component === 'Frontend') return 'FE';
  if (component === 'Backend') return 'BE';

  if (key.startsWith('FE-')) return 'FE';
  if (key.startsWith('BE-')) return 'BE';

  return 'Uncategorized';
};

const isInLastWeek = (ticket) => {
  const deployDate = parseDate(ticket.deployed_date) || parseDate(ticket.updated);
  if (!deployDate || !lastWeekStart || !lastWeekEnd) return false;
  return deployDate >= lastWeekStart && deployDate <= lastWeekEnd;
};

const isInNext14Days = (ticket) => {
  const targetDate = parseDate(ticket.target_deploy_date);
  const status = ticket.status || '';

  if (targetDate && next14Start && next14End) {
    if (targetDate >= next14Start && targetDate <= next14End) return true;
  }

  if ((status === 'Ready for Deploy' || status === 'In QA') && ticket.fix_version) {
    return true;
  }

  return false;
};

const isBlocked = (ticket) => ticket.status === 'Blocked' || ticket.blocked_reason;

const processed = new Set();

for (const ticket of tickets) {
  const key = ticket.key;
  const status = ticket.status || '';
  const classification = classifyTicket(ticket);

  if (isBlocked(ticket)) {
    buckets.risks_blocks.push(ticket);
    processed.add(key);
    continue;
  }

  if (status === 'Done' && isInLastWeek(ticket)) {
    if (classification === 'FE') buckets.fe_deployed.push(ticket);
    else if (classification === 'BE') buckets.be_deployed.push(ticket);
    else buckets.uncategorized.push(ticket);
    processed.add(key);
    continue;
  }

  if ((status === 'Ready for Deploy' || status === 'In QA') && isInNext14Days(ticket)) {
    if (classification === 'FE') buckets.fe_upcoming.push(ticket);
    else if (classification === 'BE') buckets.be_upcoming.push(ticket);
    else buckets.uncategorized.push(ticket);
    processed.add(key);
    continue;
  }

  if (status === 'In Progress' || status === 'To Do') {
    const epic = ticket.epic || 'Other Focus Items';
    if (!buckets.focus_items[epic]) buckets.focus_items[epic] = [];
    buckets.focus_items[epic].push(ticket);
    processed.add(key);
    continue;
  }

  if (!processed.has(key)) buckets.uncategorized.push(ticket);
}

const focusItemsList = Object.entries(buckets.focus_items).map(([epic, items]) => ({
  epic,
  tickets: items,
}));

return [
  {
    json: {
      buckets: {
        fe_deployed: buckets.fe_deployed,
        be_deployed: buckets.be_deployed,
        fe_upcoming: buckets.fe_upcoming,
        be_upcoming: buckets.be_upcoming,
        focus_items: focusItemsList,
        risks_blocks: buckets.risks_blocks,
        uncategorized: buckets.uncategorized,
      },
      date_windows: windows,
      summary: {
        total_tickets: tickets.length,
        fe_deployed_count: buckets.fe_deployed.length,
        be_deployed_count: buckets.be_deployed.length,
        fe_upcoming_count: buckets.fe_upcoming.length,
        be_upcoming_count: buckets.be_upcoming.length,
        focus_items_count: Object.values(buckets.focus_items).reduce((sum, items) => sum + items.length, 0),
        risks_blocks_count: buckets.risks_blocks.length,
        uncategorized_count: buckets.uncategorized.length,
      },
    },
  },
];
'''

    js_generate_week_id = '''const input = $input.first().json;
const now = new Date();

const getISOWeek = (date) => {
  const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
  return { year: d.getUTCFullYear(), week: weekNo };
};

const pad = (n) => String(n).padStart(2, '0');
const iso = getISOWeek(now);
const week_identifier = `${iso.year}-W${pad(iso.week)}`;

const generated_timestamp = `${now.getUTCFullYear()}-${pad(now.getUTCMonth() + 1)}-${pad(now.getUTCDate())} ${pad(now.getUTCHours())}:${pad(now.getUTCMinutes())}:${pad(now.getUTCSeconds())} UTC`;
const generated_timestamp_id = `${now.getUTCFullYear()}-${pad(now.getUTCMonth() + 1)}-${pad(now.getUTCDate())}T${pad(now.getUTCHours())}-${pad(now.getUTCMinutes())}-${pad(now.getUTCSeconds())}Z`;

return [
  {
    json: {
      buckets: input.buckets || {},
      date_windows: input.date_windows || {},
      summary: input.summary || {},
      week_identifier,
      generated_timestamp,
      generated_timestamp_id,
    },
  },
];
'''

    js_format_confluence = r'''const input = $input.first().json;
const buckets = input.buckets || {};
const windows = input.date_windows || {};
const weekId = input.week_identifier || '';
const timestamp = input.generated_timestamp || '';
const timestampId = input.generated_timestamp_id || '';
const NL = '\n';

const formatTicket = (ticket, includeDate = false) => {
  const key = ticket.key || '';
  const summary = ticket.summary || '';
  const url = `https://jira.example.com/browse/${key}`;
  let line = `- [${key}](${url}): ${summary}`;

  if (includeDate) {
    const date = ticket.target_deploy_date || ticket.deployed_date;
    if (date) line += ` *(Target: ${date})*`;
    else if (ticket.status === 'Ready for Deploy') line += ' *(Target: TBD)*';
  }

  return line;
};

const formatBucket = (tickets, title, includeDate = false) => {
  if (!tickets || tickets.length === 0) {
    return `### ${title}${NL}${NL}[None]${NL}`;
  }
  const lines = [`### ${title}${NL}`];
  for (const ticket of tickets) {
    lines.push(formatTicket(ticket, includeDate));
  }
  return `${lines.join(NL)}${NL}`;
};

const mdLines = [
  `# Weekly Deployment Update - ${weekId}`,
  '',
  `**Report Period**: ${windows.last_week_start || ''} to ${windows.last_week_end || ''}`,
  `**Generated**: ${timestamp}`,
  '',
  '---',
  '',
  '## Deployed Last Week',
  '',
];

mdLines.push(formatBucket(buckets.fe_deployed || [], 'Frontend'));
mdLines.push('');
mdLines.push(formatBucket(buckets.be_deployed || [], 'Backend'));
mdLines.push('');

mdLines.push('---');
mdLines.push('');
mdLines.push('## Expected Next 14 Days');
mdLines.push(`**Window**: ${windows.next_14_start || ''} to ${windows.next_14_end || ''}`);
mdLines.push('');

mdLines.push(formatBucket(buckets.fe_upcoming || [], 'Frontend', true));
mdLines.push('');
mdLines.push(formatBucket(buckets.be_upcoming || [], 'Backend', true));
mdLines.push('');

mdLines.push('---');
mdLines.push('');
mdLines.push('## Team Focus Items');
mdLines.push('');

const focusItems = buckets.focus_items || [];
if (!focusItems.length) {
  mdLines.push(`[None]${NL}`);
} else {
  for (const group of focusItems) {
    const epic = group.epic || 'Other';
    const tickets = group.tickets || [];
    mdLines.push(`### ${epic}${NL}`);
    for (const ticket of tickets) {
      mdLines.push(formatTicket(ticket));
    }
    mdLines.push('');
  }
}

mdLines.push('---');
mdLines.push('');
mdLines.push('## Risks & Blockers');
mdLines.push('');

const risks = buckets.risks_blocks || [];
if (!risks.length) {
  mdLines.push(`No known risks/blocks this week.${NL}`);
} else {
  for (const ticket of risks) {
    const key = ticket.key || '';
    const summary = ticket.summary || '';
    const reason = ticket.blocked_reason || 'No details provided';
    const url = `https://jira.example.com/browse/${key}`;
    mdLines.push(`- **[${key}](${url})**: ${summary}`);
    mdLines.push(`  - *Reason*: ${reason}`);
  }
  mdLines.push('');
}

const uncategorized = buckets.uncategorized || [];
if (uncategorized.length) {
  mdLines.push('---');
  mdLines.push('');
  mdLines.push('## Other Items');
  mdLines.push('');
  for (const ticket of uncategorized) {
    mdLines.push(formatTicket(ticket));
  }
  mdLines.push('');
}

const confluenceContent = mdLines.join(NL);

return [
  {
    json: {
      buckets,
      date_windows: windows,
      summary: input.summary || {},
      week_identifier: weekId,
      generated_timestamp: timestamp,
      generated_timestamp_id: timestampId,
      confluence_content: confluenceContent,
    },
  },
];
'''

    js_format_slide = r'''const input = $input.first().json;
const buckets = input.buckets || {};
const windows = input.date_windows || {};
const weekId = input.week_identifier || '';
const timestamp = input.generated_timestamp || '';
const NL = '\n';

const formatTicketSimple = (ticket) => {
  const key = ticket.key || '';
  const summary = ticket.summary || '';
  return `* ${key}: ${summary}`;
};

const formatTicketWithDate = (ticket) => {
  const key = ticket.key || '';
  const summary = ticket.summary || '';
  const date = ticket.target_deploy_date;
  if (date) return `* ${key}: ${summary} [${date}]`;
  if (ticket.status === 'Ready for Deploy') return `* ${key}: ${summary} [TBD]`;
  return `* ${key}: ${summary}`;
};

const slideLines = [
  `WEEKLY DEPLOYMENT UPDATE - ${weekId}`,
  '='.repeat(50),
  '',
  '='.repeat(50),
  '                    SLIDE 1: OVERVIEW',
  '='.repeat(50),
  '',
  '+-----------------------------+-----------------------------+',
  '|     DEPLOYED LAST WEEK      |    EXPECTED NEXT 14 DAYS    |',
  '+-----------------------------+-----------------------------+',
  '',
];

slideLines.push('LEFT COLUMN (Deployed):');
slideLines.push('-'.repeat(30));
const feDeployed = buckets.fe_deployed || [];
const beDeployed = buckets.be_deployed || [];

if (feDeployed.length) {
  slideLines.push('FRONTEND:');
  for (const t of feDeployed.slice(0, 5)) slideLines.push(formatTicketSimple(t));
  slideLines.push('');
}
if (beDeployed.length) {
  slideLines.push('BACKEND:');
  for (const t of beDeployed.slice(0, 5)) slideLines.push(formatTicketSimple(t));
}
if (!feDeployed.length && !beDeployed.length) slideLines.push('[None]');

slideLines.push('');
slideLines.push('RIGHT COLUMN (Upcoming):');
slideLines.push('-'.repeat(30));

const feUpcoming = buckets.fe_upcoming || [];
const beUpcoming = buckets.be_upcoming || [];

if (feUpcoming.length) {
  slideLines.push('FRONTEND:');
  for (const t of feUpcoming.slice(0, 5)) slideLines.push(formatTicketWithDate(t));
  slideLines.push('');
}
if (beUpcoming.length) {
  slideLines.push('BACKEND:');
  for (const t of beUpcoming.slice(0, 5)) slideLines.push(formatTicketWithDate(t));
}
if (!feUpcoming.length && !beUpcoming.length) slideLines.push('[None]');

slideLines.push('');
slideLines.push('='.repeat(50));
slideLines.push('            SLIDE 2: FOCUS & RISKS');
slideLines.push('='.repeat(50));
slideLines.push('');
slideLines.push('TEAM FOCUS ITEMS:');
slideLines.push('-'.repeat(30));

const focusItems = buckets.focus_items || [];
if (!focusItems.length) {
  slideLines.push('[None]');
} else {
  for (const group of focusItems) {
    const epic = group.epic || 'Other';
    slideLines.push(`${NL}> ${epic}:`);
    for (const ticket of (group.tickets || []).slice(0, 3)) {
      slideLines.push(formatTicketSimple(ticket));
    }
  }
}

slideLines.push('');
slideLines.push('RISKS & BLOCKERS:');
slideLines.push('-'.repeat(30));

const risks = buckets.risks_blocks || [];
if (!risks.length) {
  slideLines.push('No known risks/blocks this week.');
} else {
  for (const ticket of risks) {
    const key = ticket.key || '';
    const summary = ticket.summary || '';
    const reason = ticket.blocked_reason || 'No details';
    slideLines.push(`! ${key}: ${summary}`);
    slideLines.push(`  -> ${reason}`);
  }
}

slideLines.push('');
slideLines.push('='.repeat(50));
slideLines.push(`Generated: ${timestamp}`);
slideLines.push('='.repeat(50));

const slideContent = slideLines.join(NL);

return [
  {
    json: {
      buckets,
      date_windows: windows,
      summary: input.summary || {},
      week_identifier: weekId,
      generated_timestamp: timestamp,
      confluence_content: input.confluence_content || '',
      slide_content: slideContent,
    },
  },
];
'''

    # Node IDs
    id_schedule = new_id()
    id_read_file = new_id()
    id_extract = new_id()
    id_date_windows = new_id()
    id_filter = new_id()
    id_week_id = new_id()
    id_confluence = new_id()
    id_slide = new_id()
    id_if_monday = new_id()
    id_write_confluence = new_id()
    id_write_slide = new_id()

    # Build nodes array
    nodes = [
        {
            "parameters": {
                "rule": {
                    "interval": [
                        {
                            "field": "weeks",
                            "triggerAtDay": [1],
                            "triggerAtHour": 9
                        }
                    ]
                }
            },
            "id": id_schedule,
            "name": "Schedule Trigger",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [-240, 192],
            "notes": "Runs every Monday at 9am. Manual execution also supported for testing."
        },
        {
            "parameters": {
                "fileSelector": "/Users/matt/.n8n-files/mock_jira_tickets.json",
                "options": {}
            },
            "type": "n8n-nodes-base.readWriteFile",
            "typeVersion": 1.1,
            "position": [-16, 192],
            "id": id_read_file,
            "name": "Read/Write Files from Disk",
            "executeOnce": True,
            "alwaysOutputData": True
        },
        {
            "parameters": {
                "operation": "fromJson",
                "options": {}
            },
            "type": "n8n-nodes-base.extractFromFile",
            "typeVersion": 1.1,
            "position": [208, 192],
            "id": id_extract,
            "name": "Extract from File"
        },
        {
            "parameters": {
                "jsCode": js_calculate_date_windows
            },
            "id": id_date_windows,
            "name": "Calculate Date Windows",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [432, 192],
            "notes": "Calculates UTC windows:\n- Last Week: Previous Mon 00:00 to Sun 23:59:59\n- Next 14 Days: Today 00:00 to +14 days 23:59:59\n\nMonday logic: If today is Monday, use the week that just ended."
        },
        {
            "parameters": {
                "jsCode": js_filter_categorize
            },
            "id": id_filter,
            "name": "Filter & Categorize",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [656, 192],
            "notes": "Categorizes tickets into 7 buckets:\n1. FE Deployed Last Week\n2. BE Deployed Last Week\n3. FE Expected Next 14 Days\n4. BE Expected Next 14 Days\n5. Team Focus Items (by epic)\n6. Risks/Blocks\n7. Uncategorized\n\nClassification: component field > key prefix > Uncategorized"
        },
        {
            "parameters": {
                "jsCode": js_generate_week_id
            },
            "id": id_week_id,
            "name": "Generate Week ID",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [880, 192],
            "notes": "Generates ISO week identifier (e.g., 2026-W03) for file naming and report headers."
        },
        {
            "parameters": {
                "jsCode": js_format_confluence
            },
            "id": id_confluence,
            "name": "Format Confluence",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1104, 192],
            "notes": "Generates Markdown for Confluence:\n- Deployed Last Week (FE/BE)\n- Expected Next 14 Days (FE/BE)\n- Team Focus Items (by epic)\n- Risks & Blockers\n- Other Items (if any)\n\nHandles [None] for empty categories."
        },
        {
            "parameters": {
                "jsCode": js_format_slide
            },
            "id": id_slide,
            "name": "Format Slide",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1328, 192],
            "notes": "Generates two-column text layout for Google Slides:\n- Left: Deployed items\n- Right: Upcoming items\n- Bottom: Focus items and risks\n\nLimits items per section for readability."
        },
        {
            "parameters": {
                "conditions": {
                    "options": {
                        "caseSensitive": True,
                        "leftValue": "",
                        "typeValidation": "strict",
                        "version": 2
                    },
                    "conditions": [
                        {
                            "id": "first-monday-check",
                            "leftValue": "={{ $now.toFormat('d') <= 7 && $now.weekday === 1 }}",
                            "rightValue": True,
                            "operator": {
                                "type": "boolean",
                                "operation": "equals"
                            }
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "id": id_if_monday,
            "name": "Is First Monday?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2.2,
            "position": [1552, 192],
            "notes": "Checks if today is the first Monday of the month.\nUsed for monthly rollover logic (future enhancement).\nCurrently both branches continue to file output."
        },
        {
            "parameters": {
                "operation": "toText",
                "sourceProperty": "=",
                "binaryPropertyName": "{{ $json.confluence_content }}",
                "options": {}
            },
            "type": "n8n-nodes-base.convertToFile",
            "typeVersion": 1.1,
            "position": [1776, 96],
            "id": id_write_confluence,
            "name": "Write to Confluence"
        },
        {
            "parameters": {
                "operation": "toText",
                "sourceProperty": "=",
                "binaryPropertyName": "={{ $json.confluence_content }}",
                "options": {
                    "fileName": "=/tmp/slide_{{ $json.week_identifier }}_{{ $json.generated_timestamp }}.txt"
                }
            },
            "type": "n8n-nodes-base.convertToFile",
            "typeVersion": 1.1,
            "position": [1776, 288],
            "id": id_write_slide,
            "name": "Write to Slide"
        }
    ]

    # Build connections
    connections = {
        "Schedule Trigger": {
            "main": [[{"node": "Read/Write Files from Disk", "type": "main", "index": 0}]]
        },
        "Read/Write Files from Disk": {
            "main": [[{"node": "Extract from File", "type": "main", "index": 0}]]
        },
        "Extract from File": {
            "main": [[{"node": "Calculate Date Windows", "type": "main", "index": 0}]]
        },
        "Calculate Date Windows": {
            "main": [[{"node": "Filter & Categorize", "type": "main", "index": 0}]]
        },
        "Filter & Categorize": {
            "main": [[{"node": "Generate Week ID", "type": "main", "index": 0}]]
        },
        "Generate Week ID": {
            "main": [[{"node": "Format Confluence", "type": "main", "index": 0}]]
        },
        "Format Confluence": {
            "main": [[{"node": "Format Slide", "type": "main", "index": 0}]]
        },
        "Format Slide": {
            "main": [[{"node": "Is First Monday?", "type": "main", "index": 0}]]
        },
        "Is First Monday?": {
            "main": [
                [
                    {"node": "Write to Confluence", "type": "main", "index": 0},
                    {"node": "Write to Slide", "type": "main", "index": 0}
                ],
                [
                    {"node": "Write to Confluence", "type": "main", "index": 0},
                    {"node": "Write to Slide", "type": "main", "index": 0}
                ]
            ]
        }
    }

    # Build complete workflow
    workflow = {
        "name": "Weekly Deployment Update",
        "nodes": nodes,
        "pinData": {},
        "connections": connections,
        "active": False,
        "settings": {
            "executionOrder": "v1",
            "availableInMCP": False
        },
        "versionId": new_id(),
        "meta": {
            "instanceId": "9eff279eec139ff89f93a31975497043c66ae4c2145ee868d8adc56b024aa1a0"
        },
        "id": new_id().replace("-", "")[:21],
        "tags": []
    }

    return workflow


# ============================================================
# Main Execution
# ============================================================
def main():
    print("=" * 60)
    print("Weekly Deployment Update - Test Run")
    print("=" * 60)
    print()

    # Generate mock data
    print("Step 1: Generating mock Jira data...")
    tickets = generate_mock_jira_data()
    print(f"  Generated {len(tickets)} tickets")

    # Calculate date windows
    print("Step 2: Calculating date windows...")
    windows = calculate_date_windows()
    print(f"  Last week: {windows['last_week_start']} to {windows['last_week_end']}")
    print(f"  Next 14 days: {windows['next_14_start']} to {windows['next_14_end']}")

    # Filter and categorize
    print("Step 3: Filtering and categorizing...")
    buckets = filter_and_categorize(tickets, windows)
    print(f"  FE Deployed: {len(buckets['fe_deployed'])}")
    print(f"  BE Deployed: {len(buckets['be_deployed'])}")
    print(f"  FE Upcoming: {len(buckets['fe_upcoming'])}")
    print(f"  BE Upcoming: {len(buckets['be_upcoming'])}")
    print(f"  Focus Items: {sum(len(g['tickets']) for g in buckets['focus_items'])}")
    print(f"  Risks/Blocks: {len(buckets['risks_blocks'])}")
    print(f"  Uncategorized: {len(buckets['uncategorized'])}")

    # Generate week ID
    week_id = generate_week_id()
    generated_timestamp = today.strftime('%Y-%m-%d %H:%M:%S UTC')
    timestamp_id = today.strftime('%Y-%m-%dT%H-%M-%SZ')
    print(f"Step 4: Week identifier: {week_id}")

    # Generate outputs
    print("Step 5: Generating outputs...")
    confluence_content = format_confluence(buckets, windows, week_id, generated_timestamp)
    slide_content = format_slide(buckets, windows, week_id, generated_timestamp)

    # Write outputs
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = "/tmp"
    mockdata_dir = os.path.join(script_dir, "mockdata")

    os.makedirs(outputs_dir, exist_ok=True)
    os.makedirs(mockdata_dir, exist_ok=True)

    # Write Confluence output
    confluence_path = os.path.join(outputs_dir, f"confluence_{week_id}_{generated_timestamp}.md")
    with open(confluence_path, 'w') as f:
        f.write(confluence_content)
    print(f"  Wrote: {confluence_path}")

    # Write Slide output (text)
    slide_path = os.path.join(outputs_dir, f"slide_{week_id}_{generated_timestamp}.txt")
    with open(slide_path, 'w') as f:
        f.write(slide_content)
    print(f"  Wrote: {slide_path}")

    # PowerPoint output is not generated in the n8n workflow.

    # Write mock data
    mockdata_path = os.path.join(mockdata_dir, "mock_jira_tickets.json")
    with open(mockdata_path, 'w') as f:
        json.dump(tickets, f, indent=2)
    print(f"  Wrote: {mockdata_path}")

    # Write categorized data
    categorized_path = os.path.join(mockdata_dir, "categorized_data.json")
    with open(categorized_path, 'w') as f:
        json.dump({
            "buckets": buckets,
            "windows": windows,
            "week_id": week_id,
            "timestamp": generated_timestamp,
            "timestamp_id": timestamp_id
        }, f, indent=2)
    print(f"  Wrote: {categorized_path}")

    # Keep the n8n file sandbox copy updated for Read/Write Files from Disk.
    n8n_files_dir = os.path.expanduser("~/.n8n-files")
    os.makedirs(n8n_files_dir, exist_ok=True)
    n8n_mock_path = os.path.join(n8n_files_dir, "mock_jira_tickets.json")
    try:
        if not os.path.samefile(mockdata_path, n8n_mock_path):
            shutil.copyfile(mockdata_path, n8n_mock_path)
            print(f"  Wrote: {n8n_mock_path}")
        else:
            print(f"  Skipped: {n8n_mock_path} (already linked)")
    except FileNotFoundError:
        shutil.copyfile(mockdata_path, n8n_mock_path)
        print(f"  Wrote: {n8n_mock_path}")

    # Generate n8n workflow JSON
    print("Step 6: Generating n8n workflow JSON...")
    workflow_json = generate_workflow_json()
    workflow_path = os.path.join(script_dir, "workflows", "weekly_deployment_update.json")
    os.makedirs(os.path.dirname(workflow_path), exist_ok=True)
    with open(workflow_path, 'w') as f:
        json.dump(workflow_json, f, indent=2)
    print(f"  Wrote: {workflow_path}")

    print()
    print("=" * 60)
    print("Test completed successfully!")
    print("=" * 60)

    return buckets

if __name__ == "__main__":
    main()
