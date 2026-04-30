#!/usr/bin/env python3
"""
work-issue-list — list work issues

Usage:
    work-issue-list [--status active] [--tag feature] [--format json|text]
"""

import argparse
import json
import re
import sys
from pathlib import Path

ENG_DIR = Path.home() / "engineering"
ISSUES_DIR = ENG_DIR / "issues"
ARCHIVE_DIR = ISSUES_DIR / "archive"
VALID_STATUSES = {"inbox", "not-now", "active", "done"}


def parse_frontmatter(path: Path) -> dict | None:
    try:
        content = path.read_text()
    except OSError:
        return None

    if not content.startswith("---"):
        return None

    end = content.find("---", 3)
    if end == -1:
        return None

    fm_block = content[3:end].strip()
    fields = {}

    for line in fm_block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if key in ("tags", "sessions", "spikes", "facts"):
            if value.startswith("["):
                inner = re.sub(r"^\[|\]$", "", value)
                fields[key] = [t.strip() for t in inner.split(",") if t.strip()]
            else:
                fields[key] = []
        else:
            fields[key] = value.strip('"').strip("'")

    fields["path"] = str(path)
    return fields


def load_issues(status_filter: str | None, tag_filter: str | None) -> list[dict]:
    if not ISSUES_DIR.exists():
        return []

    issues = []
    for path in sorted(ISSUES_DIR.glob("*.md")):
        issue = parse_frontmatter(path)
        if not issue:
            continue
        if status_filter and issue.get("status") != status_filter:
            continue
        if tag_filter and tag_filter not in issue.get("tags", []):
            continue
        issues.append(issue)

    return issues


def render_text(issues: list[dict]) -> str:
    if not issues:
        return "No issues found."

    lines = []
    for issue in issues:
        issue_id = issue.get("id", "?")
        status = issue.get("status", "?")
        title = issue.get("title", "?")
        lines.append(f"{issue_id:<12}  {status:<10}  {title}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="List work issues")
    parser.add_argument("--status", help="Filter by status")
    parser.add_argument("--tag", help="Filter by tag")
    parser.add_argument(
        "--format",
        dest="fmt",
        default="json",
        choices=["json", "text"],
        help="Output format (default: json)",
    )
    args = parser.parse_args()

    if args.status and args.status not in VALID_STATUSES:
        print(f"error: invalid status '{args.status}'. valid: {', '.join(sorted(VALID_STATUSES))}", file=sys.stderr)
        sys.exit(1)

    issues = load_issues(args.status, args.tag)

    if args.fmt == "json":
        print(json.dumps(issues, indent=2))
    else:
        print(render_text(issues))


if __name__ == "__main__":
    main()
