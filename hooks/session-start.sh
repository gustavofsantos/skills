#!/usr/bin/env bash
# Surfaces engineering vault state to Claude at session start.
#
# Output is injected as raw context. Stays silent when nothing is
# in flight — empty stdout means no context injected.
#
# Safety:
#   - Never fails the session (always exit 0)
#   - Tolerates missing ~/engineering/, missing rg, missing git
#   - No network calls, no slow operations

set -u

VAULT="${HOME}/engineering"
ISSUES_DIR="${VAULT}/issues"

# If there's no vault, stay silent. This is normal on a fresh machine.
[ -d "$ISSUES_DIR" ] || exit 0

# Find active issue (single source of truth: status: active in frontmatter)
active_file=""
inbox_count=0
if command -v rg >/dev/null 2>&1; then
    active_file=$(rg -l '^status: active$' "$ISSUES_DIR" -g '*.md' --max-count=1 2>/dev/null | head -1 || true)
    inbox_count=$(rg -l '^status: inbox$' "$ISSUES_DIR" -g '*.md' 2>/dev/null | wc -l | tr -d ' ' || echo 0)
else
    # Fallback to grep
    active_file=$(grep -l '^status: active$' "$ISSUES_DIR"/*.md 2>/dev/null | head -1 || true)
    inbox_count=$(grep -l '^status: inbox$' "$ISSUES_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ' || echo 0)
fi

# Nothing to surface
if [ -z "$active_file" ] && [ "${inbox_count:-0}" -eq 0 ]; then
    exit 0
fi

# Header — only printed when we have something to say
printf "## Engineering vault — current state\n\n"

if [ -n "$active_file" ]; then
    title=$(grep -E '^title:' "$active_file" 2>/dev/null | head -1 | sed -e 's/^title: *//' -e 's/^"//' -e 's/"$//')
    id=$(grep -E '^id:' "$active_file" 2>/dev/null | head -1 | sed -e 's/^id: *//' -e 's/^"//' -e 's/"$//')
    pending=$(grep -c '^- \[ \]' "$active_file" 2>/dev/null || echo 0)
    done_count=$(grep -c '^- \[x\]' "$active_file" 2>/dev/null || echo 0)

    printf "**Active issue:** %s — %s\n" "${id:-?}" "${title:-(untitled)}"
    printf "  File: \`%s\`\n" "$active_file"
    printf "  Tasks: %s done, %s pending\n\n" "$done_count" "$pending"

    # Try to surface the last session for this issue, if a sessions branch exists.
    if command -v git >/dev/null 2>&1 && [ -n "${id:-}" ]; then
        # Only attempt if we are inside a git repo
        if git rev-parse --git-dir >/dev/null 2>&1; then
            sessions_branch=$(git config user.name 2>/dev/null \
                | tr '[:upper:]' '[:lower:]' \
                | tr -cs 'a-z0-9' '-' \
                | sed -e 's/-*$//' -e 's/$/\/sessions/')
            if [ -n "$sessions_branch" ] && git rev-parse --verify "$sessions_branch" >/dev/null 2>&1; then
                last_slug=$(git ls-tree -r --name-only "$sessions_branch" 2>/dev/null \
                    | grep "^${id}-" \
                    | sed 's|/SESSION.md$||' \
                    | sort -u \
                    | tail -1 || true)
                if [ -n "${last_slug:-}" ]; then
                    printf "  Last session: \`%s\` (on branch \`%s\`)\n\n" "$last_slug" "$sessions_branch"
                fi
            fi
        fi
    fi

    printf "**Recall:** invoke the \`workflow\` skill to resume. Read the issue file before any execution.\n"
fi

if [ "${inbox_count:-0}" -gt 0 ]; then
    if [ -n "$active_file" ]; then
        printf "\n"
    fi
    printf "**Inbox:** %s issue(s) waiting to be planned.\n" "$inbox_count"
fi

exit 0
