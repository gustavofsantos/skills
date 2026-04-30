#!/usr/bin/env python3
"""
work-issue-archive — move a done issue to the archive directory.
Also moves all associated session files to ~/engineering/sessions/archive/.

Usage:
    work-issue-archive --issue 001
    work-issue-archive --issue 001 --force   # skip status check
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ENG_DIR = Path.home() / "engineering"
ISSUES_DIR = ENG_DIR / "issues"
ARCHIVE_DIR = ISSUES_DIR / "archive"
SESSIONS_DIR = ENG_DIR / "sessions"
SESSIONS_ARCHIVE_DIR = SESSIONS_DIR / "archive"


def parse_frontmatter(path: Path) -> dict:
    content = path.read_text()
    if not content.startswith("---"):
        return {}

    end = content.find("---", 3)
    if end == -1:
        return {}

    fm_block = content[3:end].strip()
    fields = {}

    for line in fm_block.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        if key == "sessions":
            if value.startswith("["):
                inner = re.sub(r"^\[|\]$", "", value)
                fields["sessions"] = [s.strip() for s in inner.split(",") if s.strip()]
            else:
                fields["sessions"] = []
        elif key in ("tags", "spikes", "facts"):
            inner = re.sub(r"^\[|\]$", "", value)
            fields[key] = [t.strip() for t in inner.split(",") if t.strip()]
        else:
            fields[key] = value.strip('"').strip("'")

    return fields


def collect_multiline_sessions(path: Path) -> list[str]:
    content = path.read_text()
    lines = content.splitlines()
    sessions = []
    in_sessions = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("sessions:"):
            in_sessions = True
            inline = stripped[len("sessions:"):].strip()
            if inline.startswith("[") and inline != "[]":
                inner = re.sub(r"^\[|\]$", "", inline)
                return [s.strip() for s in inner.split(",") if s.strip()]
            continue
        if in_sessions:
            if stripped.startswith("- "):
                sessions.append(stripped[2:].strip())
            elif stripped and not stripped.startswith("#"):
                break
    return sessions


def find_issue_path(issue_id: str) -> Path | None:
    if not ISSUES_DIR.exists():
        return None
    for path in ISSUES_DIR.glob("*.md"):
        if path.stem == issue_id or path.stem.startswith(f"{issue_id}-"):
            return path
    return None


def archive_issue(issue_id: str, force: bool) -> dict:
    issue_path = find_issue_path(issue_id)
    if not issue_path:
        print(f"error: issue '{issue_id}' not found in {ISSUES_DIR}", file=sys.stderr)
        sys.exit(1)

    fm = parse_frontmatter(issue_path)
    status = fm.get("status", "")

    if not force and status != "done":
        print(f"error: issue status is '{status}', expected 'done'.", file=sys.stderr)
        print("set the issue status to 'done' first, or use --force to override.", file=sys.stderr)
        sys.exit(1)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    session_paths = collect_multiline_sessions(issue_path)

    archived_sessions = []
    skipped_sessions = []

    for session_ref in session_paths:
        session_path = Path(session_ref).expanduser()
        if not session_path.exists():
            skipped_sessions.append(str(session_path))
            continue
        dest = SESSIONS_ARCHIVE_DIR / session_path.name
        shutil.move(str(session_path), str(dest))
        archived_sessions.append(str(dest))

    dest_issue = ARCHIVE_DIR / issue_path.name
    shutil.move(str(issue_path), str(dest_issue))

    return {
        "id": issue_id,
        "status": "archived",
        "issue": str(dest_issue),
        "sessions_archived": archived_sessions,
        "sessions_skipped": skipped_sessions,
    }


def main():
    parser = argparse.ArgumentParser(description="Archive a done work issue")
    parser.add_argument("--issue", required=True, help="Issue ID (e.g. 001)")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Archive even if status is not 'done'",
    )
    parser.add_argument(
        "--format",
        dest="fmt",
        default="json",
        choices=["json", "text"],
        help="Output format (default: json)",
    )
    args = parser.parse_args()

    result = archive_issue(args.issue, args.force)

    if args.fmt == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['id']}  archived")
        print(f"issue:     {result['issue']}")
        if result["sessions_archived"]:
            print("sessions archived:")
            for s in result["sessions_archived"]:
                print(f"  {s}")
        if result["sessions_skipped"]:
            print("sessions not found (skipped):")
            for s in result["sessions_skipped"]:
                print(f"  {s}")


if __name__ == "__main__":
    main()
