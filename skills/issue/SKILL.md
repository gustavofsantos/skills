---
description: Co-authors a new issue with BDD scenarios from a problem description,
  then writes the issue file.
when_to_use: Use when the user has a new problem, feature, or task to track. Triggers on
  "new issue", "nova issue", "create issue for", "criar issue para", "let's work
  on X", "vamos trabalhar em X", or any raw problem description that needs to be
  shaped before execution.
allowed-tools: Read Write Edit Bash(fd:*) Bash(git:*) Bash(grep:*) Bash(mkdir:*)
---

# Issue

Turns a problem description into a tracked issue with co-authored BDD scenarios.

## Step 1 — Resolve storage

```bash
_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
_CFG="${_ROOT}/.skills/config"
if [ -f "$_CFG" ]; then
  ISSUES_DIR=$(grep '^issues=' "$_CFG" | cut -d= -f2 | xargs)
  [[ "$ISSUES_DIR" != /* ]] && ISSUES_DIR="${_ROOT}/${ISSUES_DIR}"
else
  ISSUES_DIR="$HOME/engineering/issues"
fi
mkdir -p "$ISSUES_DIR"
```

## Step 2 — Allocate ID

```bash
NEXT=$(fd -t f -e md . "$ISSUES_DIR" -d 1 2>/dev/null \
  | sed 's|.*/||' | grep '^[0-9]' | sed 's/-.*//' | sort -n | tail -1)
ID=$(printf '%03d' $((${NEXT:-0} + 1)))
```

## Step 3 — Get the objective

If not stated in the request: "What's the objective — one sentence describing what done looks like?"

## Step 4 — Co-author scenarios

Propose scenarios one at a time. Start with the happy path, then edge cases, then
error and limitation cases.

For each proposal:
- State it in Given/When/Then form
- Wait for confirmation, reframe, or rejection before the next
- Rejected or out-of-scope proposals become **Off-limits** entries

When the list feels complete: "Anything missing, or anything to remove?"

Assign stable IDs: S1, S2, S3, …

## Step 5 — Write the issue

Slugify the title (lowercase, hyphens, max 5 words).
Write `$ISSUES_DIR/<ID>-<slug>.md` using `references/template.md`.
Derive tasks from scenario groupings.

Confirm: "Created issue <ID>: <title> — N scenarios → $ISSUES_DIR"
