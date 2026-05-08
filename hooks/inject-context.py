#!/usr/bin/env python3
"""
UserPromptSubmit hook — looks up the active issue for this session and injects
a resume-context pointer. Stays silent when no issue is linked to this session.
Never blocks (always exit 0).
"""
import json
import sys
from pathlib import Path


ISSUES_DIR = Path.home() / "engineering" / "issues"


def _extract_frontmatter(text: str) -> str | None:
    """Return raw YAML between the first pair of --- lines, or None."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None
    return "\n".join(lines[1:end])


def _fm_get(frontmatter: str, key: str) -> str:
    """Extract a scalar value for `key:` from raw YAML text. Returns stripped string or ''."""
    for line in frontmatter.splitlines():
        if line.startswith(f"{key}:"):
            value = line[len(key) + 1:].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            return value
    return ""


def find_issue_for_session(session_id: str) -> dict | None:
    if not ISSUES_DIR.is_dir():
        return None

    for issue_path in sorted(ISSUES_DIR.glob("*.md")):
        try:
            text = issue_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        fm = _extract_frontmatter(text)
        if fm is None:
            continue

        if _fm_get(fm, "session") != session_id:
            continue

        return {
            "path": str(issue_path),
            "id": _fm_get(fm, "id") or "?",
            "title": _fm_get(fm, "title") or "(untitled)",
            "pending_tasks": text.count("\n- [ ] "),
        }

    return None


def build_context(issue: dict) -> str:
    pending_str = (
        f"{issue['pending_tasks']} pending task(s)"
        if issue["pending_tasks"] > 0
        else "all tasks complete"
    )
    return (
        f"**Active issue for this session:** {issue['id']} — {issue['title']}\n"
        f"File: `{issue['path']}`\n"
        f"Status: {pending_str}\n\n"
        f"Read the issue file before any execution. "
        f"Use the `workflow` skill to resume."
    )


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    session_id = payload.get("session_id", "")
    if not session_id:
        sys.exit(0)

    issue = find_issue_for_session(session_id)
    if issue is None:
        sys.exit(0)

    print(json.dumps({"decision": "allow", "additionalContext": build_context(issue)}))


if __name__ == "__main__":
    main()
