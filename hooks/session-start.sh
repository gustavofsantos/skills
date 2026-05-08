#!/usr/bin/env bash
# Surfaces engineering vault state to Claude at session start.
#
# Output is injected as raw context. Stays silent when nothing is
# in flight — empty stdout means no context injected.
#
# Safety:
#   - Never fails the session (always exit 0)
#   - Tolerates missing ~/engineering/, missing fd/rg/git
#   - No network calls, no slow operations

set -u

# Read hook payload from stdin; extract session_id if jq is available
_payload=$(cat 2>/dev/null || true)
session_id=""
if [ -n "$_payload" ] && command -v jq >/dev/null 2>&1; then
    session_id=$(printf '%s' "$_payload" | jq -r '.session_id // empty' 2>/dev/null || true)
fi

VAULT="${HOME}/engineering"
ISSUES_DIR="${VAULT}/issues"

# Find all in-flight issues (presence in issues/ = active; archive/ = done)
issue_files=""
inbox_count=0
if [ -d "$ISSUES_DIR" ]; then
    if command -v fd >/dev/null 2>&1; then
        issue_files=$(fd -t f -e md . "$ISSUES_DIR" 2>/dev/null | grep -v '/archive/' | sort || true)
    elif command -v find >/dev/null 2>&1; then
        issue_files=$(find "$ISSUES_DIR" -maxdepth 1 -name '*.md' 2>/dev/null | sort || true)
    fi

    if command -v rg >/dev/null 2>&1; then
        inbox_count=$(rg -l '^status: inbox$' "$ISSUES_DIR" -g '*.md' 2>/dev/null | wc -l | tr -d ' ' || echo 0)
    fi
fi

# Nothing to surface
if [ -z "$issue_files" ] && [ "${inbox_count:-0}" -eq 0 ] && [ -z "${session_id:-}" ]; then
    exit 0
fi

printf "## Engineering vault — current state\n\n"

if [ -n "$issue_files" ]; then
    issue_count=$(echo "$issue_files" | grep -c '.' 2>/dev/null || echo 0)

    if [ "$issue_count" -eq 1 ]; then
        f="$issue_files"
        title=$(grep -E '^title:' "$f" 2>/dev/null | head -1 | sed -e 's/^title: *//' -e 's/^"//' -e 's/"$//')
        id=$(grep -E '^id:' "$f" 2>/dev/null | head -1 | sed -e 's/^id: *//' -e 's/^"//' -e 's/"$//')
        pending=$(grep -c '^- \[ \]' "$f" 2>/dev/null || echo 0)
        done_count=$(grep -c '^- \[x\]' "$f" 2>/dev/null || echo 0)
        printf "**Current issue:** %s — %s\n" "${id:-?}" "${title:-(untitled)}"
        printf "  File: \`%s\`\n" "$f"
        printf "  Tasks: %s done, %s pending\n\n" "$done_count" "$pending"
    else
        printf "**Current issues (%s):**\n\n" "$issue_count"
        echo "$issue_files" | while IFS= read -r f; do
            [ -z "$f" ] && continue
            title=$(grep -E '^title:' "$f" 2>/dev/null | head -1 | sed -e 's/^title: *//' -e 's/^"//' -e 's/"$//')
            id=$(grep -E '^id:' "$f" 2>/dev/null | head -1 | sed -e 's/^id: *//' -e 's/^"//' -e 's/"$//')
            pending=$(grep -c '^- \[ \]' "$f" 2>/dev/null || echo 0)
            printf "  - %s — %s (%s pending)\n" "${id:-?}" "${title:-(untitled)}" "$pending"
        done
        printf "\n"
    fi

    printf "**Recall:** invoke the \`workflow\` skill to resume. Read the issue file before any execution.\n"
fi

if [ "${inbox_count:-0}" -gt 0 ]; then
    [ -n "$issue_files" ] && printf "\n"
    printf "**Inbox:** %s issue(s) waiting to be planned.\n" "$inbox_count"
fi

if [ -n "${session_id:-}" ]; then
    printf "\n---\n**Session ID:** \`%s\`\n" "$session_id"
fi

exit 0
