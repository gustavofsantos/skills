---
description: >
  Closes the current working session: synthesizes a SESSION.md via Haiku, writes it
  to the personal sessions branch, and links all session commits back via git notes.
allowed-tools: Bash(git:*) Bash(python3:*) Bash(claude:*) Bash(rg:*) Bash(fd:*) Read
---

# Session Close

Closes the current session by producing a self-contained SESSION.md on the personal
`<username>/sessions` orphan branch. All commits that belong to the session receive a
`Session:` field appended to their existing git note.

---

## Preflight

Verify this is a git repository:

```bash
git rev-parse --git-dir
```

If this fails, stop: "Not a git repository."

Locate the active issue:

```bash
ISSUE_FILE=$(rg -l '^status: active$' ~/engineering/issues -g '*.md' 2>/dev/null | head -1)
```

If `ISSUE_FILE` is empty, ask the user which issue is being closed before continuing.

---

## Step 1 — Collect session commits

```bash
ORIGIN_HEAD=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null \
  | sed 's|refs/remotes/origin/||')
BASE=$(git merge-base HEAD "origin/${ORIGIN_HEAD:-main}" 2>/dev/null \
  || git rev-list --max-parents=0 HEAD)
COMMITS=$(git log "${BASE}..HEAD" --format="%H")
SHORT_COMMITS=$(git log "${BASE}..HEAD" --format="%h" | tr '\n' ' ' | sed 's/ $//')
```

If `COMMITS` is empty, stop: "No commits found in this session."

Surface to the user: `Commits found: $SHORT_COMMITS`

---

## Step 2 — Collect git notes from session commits

```bash
NOTES=$(echo "$COMMITS" | while read h; do
  note=$(git notes show "$h" 2>/dev/null)
  [ -n "$note" ] || continue
  short=$(git rev-parse --short "$h")
  printf "### %s\n%s\n\n" "$short" "$note"
done)
```

---

## Step 3 — Read issue content and extract external resources

```bash
ISSUE_CONTENT=$(cat "$ISSUE_FILE")

EXTERNAL_URLS=$(rg 'https?://\S+' "$ISSUE_FILE" -o 2>/dev/null | sort -u)
TICKET_IDS=$(rg '\b[A-Z][A-Z0-9]+-\d+\b' "$ISSUE_FILE" -o 2>/dev/null | sort -u)
EXTERNAL=$(printf '%s\n%s' "$EXTERNAL_URLS" "$TICKET_IDS" | grep -v '^$')
```

---

## Step 4 — Build the session slug

```bash
ISSUE_ID=$(rg '^id:' "$ISSUE_FILE" | head -1 \
  | sed 's/id: *//;s/"//g' | tr -d '[:space:]')
ISSUE_TITLE=$(rg '^title:' "$ISSUE_FILE" | head -1 \
  | sed 's/title: *//;s/"//g' \
  | tr '[:upper:]' '[:lower:]' \
  | tr -cs 'a-z0-9' '-' \
  | sed 's/-\+/-/g;s/^-//;s/-$//' \
  | cut -c1-40)
HEAD_SHORT=$(git rev-parse --short HEAD)
SESSION_SLUG="${ISSUE_ID}-${ISSUE_TITLE}-${HEAD_SHORT}"
```

Surface to the user: `Session slug: $SESSION_SLUG`

---

## Step 5 — Synthesize SESSION.md via Haiku

```bash
SESSION_CONTENT=$(printf \
'SLUG: %s
TODAY: %s
COMMITS: %s

ISSUE FILE:
%s

GIT NOTES FROM SESSION COMMITS:
%s

EXTERNAL RESOURCES (URLs and ticket IDs found in issue):
%s' \
  "$SESSION_SLUG" \
  "$(date +%Y-%m-%d)" \
  "$SHORT_COMMITS" \
  "$ISSUE_CONTENT" \
  "${NOTES:-(none)}" \
  "${EXTERNAL:-(none)}" \
| claude -p \
'Generate a SESSION.md for this AI coding session.

Output ONLY the document — no preamble, no explanation, no code fences.

Format:

# Session: <SLUG>

**Date:** <TODAY>
**Issue:** <issue id> — <issue title>
**Commits:** <COMMITS>

## Objective
<one sentence from issue ## Objective>

## Key decisions
- <key decision inferred from git notes>
...

## Context used
<[[FACT-NNN-slug]] and [[NNN-spike-slug]] referenced in git notes, or "(none)">

## External resources
<URLs and ticket IDs grouped by type. Infer type from pattern:
  - *.atlassian.net or jira.* = Jira
  - sentry.io = Sentry
  - github.com/*/pull/* = GitHub PR
  - docs.google.com = Google Doc
  - Bare ticket IDs like PAY-1234 without a URL = list under Jira.
Omit this section entirely if EXTERNAL RESOURCES is "(none)".>

## Tasks
<copy task lines from issue ## Tasks, preserving [x] and [ ] markers and inline commit hashes>

## Outcome
<"completed", "partial — <one-line reason>", or "blocked — <one-line reason>">

Rules:
- Self-contained prose. No local file paths. No explanations outside the document.
- Context used: only emit entries that actually appear in the git notes. Do not invent.
- Key decisions: infer from the Why and Context fields of the git notes. Be specific.' \
  --model claude-haiku-4-5-20251001 \
  --max-turns 1)
```

If the output is empty or the command fails, stop and report the error.

---

## Step 6 — Write to the sessions branch

```bash
RESULT=$(printf '%s' "$SESSION_CONTENT" \
  | python3 "${CLAUDE_SKILL_DIR}/../../bin/write-session-branch" "$SESSION_SLUG")
```

`write-session-branch` reads SESSION.md content from stdin, writes it to the
`<username>/sessions` orphan branch using git plumbing (no working tree changes,
no HEAD movement), and prints `<branch>:<slug>/SESSION.md` on success.

If the script exits non-zero, stop and display the error output.

---

## Step 7 — Append Session: to git notes

For each session commit that already has a git note and does not yet have a `Session:` field:

```bash
echo "$COMMITS" | while read h; do
  existing=$(git notes show "$h" 2>/dev/null)
  [ -z "$existing" ] && continue
  echo "$existing" | grep -q "^Session:" && continue
  git notes add -f -m "${existing}
Session: ${SESSION_SLUG}" "$h"
done
```

---

## Output

```
Session closed — <RESULT>

Commits linked: <SHORT_COMMITS>
To publish:     git push origin <branch>
```

If any tasks in the issue are still `[ ]`, append:

```
Pending tasks (not completed this session):
- [ ] <task text>
```
