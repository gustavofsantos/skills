#!/usr/bin/env python3
"""
Fetches Jira ticket context via acli. Outputs optimized markdown for Claude.

Features:
  - Accepts ticket IDs (FPF-1234) or Jira URLs
  - Auto-fetches parent ticket (summary level)
  - Auto-fetches all children in parallel with full details
  - Full ADF (Atlassian Document Format) parser: headings, lists, code, quotes, mentions
  - Filters killed tickets

Usage: python3 jira-ticket-context.py TICKET-ID-OR-URL [...]
"""

import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed


# ---------------------------------------------------------------------------
# Input normalisation
# ---------------------------------------------------------------------------

def extract_ticket_id(arg):
    """Accept raw ID (FPF-1234) or any Jira URL containing /browse/KEY."""
    m = re.search(r'/browse/([A-Z][A-Z0-9]+-\d+)', arg)
    if m:
        return m.group(1)
    m = re.match(r'^[A-Z][A-Z0-9]+-\d+$', arg.strip())
    if m:
        return arg.strip()
    return None


# ---------------------------------------------------------------------------
# acli wrapper
# ---------------------------------------------------------------------------

FIELDS_FULL = "key,issuetype,summary,status,assignee,description,comment,parent,subtasks,priority,labels"
FIELDS_BRIEF = "key,issuetype,summary,status"


def fetch_issue(key, fields=FIELDS_FULL):
    cmd = ["acli", "jira", "workitem", "view", key, "--json", "--fields", fields]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        err = e.stderr.strip() if e.stderr else ""
        if "401" in err or "unauthorized" in err.lower() or "not logged" in err.lower():
            print("Error: not authenticated. Run: acli jira auth", file=sys.stderr)
            sys.exit(1)
        print(f"Failed to fetch {key}: {err or 'unknown error'}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"Bad JSON from acli for {key}", file=sys.stderr)
        return None


def fetch_issues_parallel(keys, fields=FIELDS_FULL):
    """Fetch multiple tickets simultaneously. Returns {key: data}."""
    results = {}
    with ThreadPoolExecutor(max_workers=min(len(keys), 8)) as pool:
        futures = {pool.submit(fetch_issue, k, fields): k for k in keys}
        for future in as_completed(futures):
            key = futures[future]
            results[key] = future.result()
    return results


# ---------------------------------------------------------------------------
# ADF → plain text
# ---------------------------------------------------------------------------

def adf_to_text(node, depth=0):
    """Recursively convert an ADF node to readable markdown-ish text."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node

    if not isinstance(node, dict):
        return ""

    t = node.get("type", "")
    content = node.get("content", [])
    text = node.get("text", "")
    attrs = node.get("attrs", {})

    if t == "doc":
        return "\n".join(adf_to_text(c, depth) for c in content).strip()

    if t == "text":
        result = text
        for mark in node.get("marks", []):
            mt = mark.get("type", "")
            if mt == "strong":
                result = f"**{result}**"
            elif mt == "em":
                result = f"*{result}*"
            elif mt == "code":
                result = f"`{result}`"
            elif mt == "link":
                href = mark.get("attrs", {}).get("href", "")
                result = f"[{result}]({href})" if href else result
        return result

    if t == "paragraph":
        inner = "".join(adf_to_text(c, depth) for c in content)
        return inner if inner.strip() else ""

    if t == "heading":
        level = attrs.get("level", 2)
        inner = "".join(adf_to_text(c, depth) for c in content)
        return f"{'#' * level} {inner}"

    if t == "bulletList":
        items = []
        for item in content:
            item_text = _list_item_text(item, depth)
            items.append(f"{'  ' * depth}- {item_text}")
        return "\n".join(items)

    if t == "orderedList":
        items = []
        for i, item in enumerate(content, 1):
            item_text = _list_item_text(item, depth)
            items.append(f"{'  ' * depth}{i}. {item_text}")
        return "\n".join(items)

    if t == "listItem":
        parts = []
        for c in content:
            if c.get("type") in ("bulletList", "orderedList"):
                parts.append("\n" + adf_to_text(c, depth + 1))
            else:
                parts.append(adf_to_text(c, depth))
        return "".join(parts)

    if t == "codeBlock":
        lang = attrs.get("language", "")
        inner = "".join(adf_to_text(c, depth) for c in content)
        return f"```{lang}\n{inner}\n```"

    if t == "blockquote":
        inner = "\n".join(adf_to_text(c, depth) for c in content)
        return "\n".join(f"> {line}" for line in inner.splitlines())

    if t == "rule":
        return "---"

    if t == "hardBreak":
        return "\n"

    if t == "mention":
        return f"@{attrs.get('text', attrs.get('id', 'user'))}"

    if t == "inlineCard":
        url = attrs.get("url", "")
        return f"[{url}]({url})" if url else ""

    if t == "panel":
        panel_type = attrs.get("panelType", "info")
        inner = "\n".join(adf_to_text(c, depth) for c in content)
        return f"[{panel_type.upper()}]\n{inner}"

    if t == "table":
        return _table_to_text(content)

    if t == "tableRow":
        cells = [adf_to_text(c, depth) for c in content]
        return " | ".join(cells)

    if t in ("tableCell", "tableHeader"):
        return "".join(adf_to_text(c, depth) for c in content).replace("\n", " ")

    if t == "mediaGroup" or t == "mediaSingle":
        return "[attachment]"

    if t == "media":
        return "[media]"

    # Fallback: recurse into children
    parts = [adf_to_text(c, depth) for c in content]
    return " ".join(p for p in parts if p)


def _list_item_text(item, depth):
    parts = []
    for c in item.get("content", []):
        if c.get("type") in ("bulletList", "orderedList"):
            parts.append("\n" + adf_to_text(c, depth + 1))
        else:
            parts.append(adf_to_text(c, depth))
    return "".join(parts)


def _table_to_text(rows):
    lines = []
    for i, row in enumerate(rows):
        cells = []
        for cell in row.get("content", []):
            inner = "".join(adf_to_text(c) for c in cell.get("content", []))
            cells.append(inner.replace("\n", " ").strip())
        lines.append("| " + " | ".join(cells) + " |")
        if i == 0:
            lines.append("| " + " | ".join(["---"] * len(cells)) + " |")
    return "\n".join(lines)


def render_description(raw):
    if raw is None:
        return None
    if isinstance(raw, str):
        return raw.strip() or None
    return adf_to_text(raw).strip() or None


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

KILLED_STATUSES = {"killed", "cancelado", "cancelled", "descartado", "discarded"}


def is_killed(data):
    if data is None:
        return True
    status = data.get("fields", {}).get("status", {}).get("name", "")
    return status.lower() in KILLED_STATUSES


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def format_ticket(data, key, level=1):
    """Render a full ticket. level=1 for main, level=2 for children."""
    if data is None:
        print(f"{'#' * level} {key} · (fetch failed)\n")
        return

    fields = data.get("fields", {})
    actual_key = data.get("key", key)
    summary = fields.get("summary", "(no summary)")
    status = fields.get("status", {}).get("name", "—")
    issuetype = fields.get("issuetype", {}).get("name", "—")

    assignee_obj = fields.get("assignee")
    assignee = assignee_obj.get("displayName", "—") if assignee_obj else "Unassigned"

    print(f"{'#' * level} {actual_key} · {summary}")
    print()
    print(f"**Type:** {issuetype} · **Status:** {status} · **Assignee:** {assignee}")
    print()

    desc = render_description(fields.get("description"))
    if desc:
        print(f"{'#' * (level + 1)} Description")
        print()
        print(desc)
        print()

    comments = fields.get("comment", {}).get("comments", [])
    if comments:
        print(f"{'#' * (level + 1)} Comments ({len(comments)})")
        print()
        for c in comments:
            author = c.get("author", {}).get("displayName", "—")
            when = (c.get("created") or "")[:10]
            body = render_description(c.get("body")) or ""
            if body.strip():
                print(f"**{author}** · {when}")
                print()
                print(body)
                print()

    print("---")
    print()


def format_parent_summary(data, key):
    """One-line parent reference block."""
    if data is None:
        print(f"**Parent:** {key} (fetch failed)\n")
        return
    fields = data.get("fields", {})
    actual_key = data.get("key", key)
    summary = fields.get("summary", "(no summary)")
    status = fields.get("status", {}).get("name", "—")
    issuetype = fields.get("issuetype", {}).get("name", "—")
    print(f"**Parent ({issuetype}):** [{actual_key}] {summary} · Status: {status}")
    print()


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def process_ticket(key):
    """Fetch key + its parent + all children in parallel, then render."""
    main_data = fetch_issue(key, FIELDS_FULL)
    if main_data is None:
        print(f"# {key} · (not found or access denied)\n---\n")
        return

    if is_killed(main_data):
        return

    fields = main_data.get("fields", {})
    parent_info = fields.get("parent")
    subtasks = [s for s in fields.get("subtasks", []) if not is_killed(s)]
    child_keys = [s["key"] for s in subtasks if s.get("key")]

    # Parallel fetch: parent (brief) + all children (full)
    to_fetch = {}
    if parent_info:
        parent_key = parent_info.get("key")
        if parent_key:
            to_fetch[parent_key] = FIELDS_BRIEF
    for ck in child_keys:
        to_fetch[ck] = FIELDS_FULL

    fetched = {}
    if to_fetch:
        with ThreadPoolExecutor(max_workers=min(len(to_fetch), 10)) as pool:
            futures = {pool.submit(fetch_issue, k, f): k for k, f in to_fetch.items()}
            for future in as_completed(futures):
                k = futures[future]
                fetched[k] = future.result()

    # --- Render ---
    # Parent summary line (if exists)
    if parent_info:
        pk = parent_info.get("key")
        if pk:
            format_parent_summary(fetched.get(pk, parent_info), pk)

    # Main ticket
    format_ticket(main_data, key, level=1)

    # Children with full details
    if child_keys:
        live_children = [ck for ck in child_keys if not is_killed(fetched.get(ck))]
        killed_count = len(child_keys) - len(live_children)

        if live_children:
            print(f"## Children ({len(live_children)} active" +
                  (f", {killed_count} killed/skipped" if killed_count else "") + ")")
            print()
            for ck in live_children:
                format_ticket(fetched.get(ck), ck, level=3)


def main():
    if not shutil.which("acli"):
        print(
            "Error: acli not found.\n"
            "Install: https://developer.atlassian.com/cloud/acli/guides/install-acli/\n"
            "Then authenticate: acli jira auth",
            file=sys.stderr,
        )
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python3 jira-ticket-context.py TICKET-ID-OR-URL [...]", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  python3 jira-ticket-context.py PROJ-1234", file=sys.stderr)
        print("  python3 jira-ticket-context.py https://your-org.atlassian.net/browse/PROJ-1234", file=sys.stderr)
        sys.exit(1)

    keys = []
    for arg in sys.argv[1:]:
        ticket_id = extract_ticket_id(arg)
        if ticket_id:
            keys.append(ticket_id)
        else:
            print(f"Warning: could not parse ticket ID from '{arg}' — skipping", file=sys.stderr)

    for key in keys:
        process_ticket(key)


if __name__ == "__main__":
    main()
