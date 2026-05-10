---
description: >
  Co-authors a new issue with BDD scenarios from a problem description,
  then writes the issue file.
when_to_use: >
  Use when the user has a new problem, feature, or task to track. Triggers on
  "new issue", "nova issue", "create issue for", "criar issue para", "let's work
  on X", "vamos trabalhar em X", or any raw problem description that needs to be
  shaped before execution.
allowed-tools: Read Write Edit Bash(fd:*) Bash(cat:*)
---

# Issue

Turns a problem description into a tracked issue with co-authored BDD scenarios.

## Step 1 — Allocate ID

```bash
NEXT=$(cat ~/engineering/.counters/issues 2>/dev/null || echo 0)
NEXT=$((NEXT + 1))
echo $NEXT > ~/engineering/.counters/issues
ID=$(printf '%03d' $NEXT)
```

## Step 2 — Get the objective

If not stated in the request: "What's the objective — one sentence describing what done looks like?"

## Step 3 — Co-author scenarios

Propose scenarios one at a time. Start with the happy path, then edge cases, then
error and limitation cases.

For each proposal:
- State it in Given/When/Then form
- Wait for confirmation, reframe, or rejection before the next
- Rejected or out-of-scope proposals become **Off-limits** entries

When the list feels complete: "Anything missing, or anything to remove?"

Assign stable IDs: S1, S2, S3, …

## Step 4 — Write the issue

Slugify the title (lowercase, hyphens, max 5 words).
Write `~/engineering/issues/<ID>-<slug>.md` using `references/template.md`.
Derive tasks from scenario groupings — tasks are just labels for batches of scenarios.

Confirm: "Created issue <ID>: <title> — N scenarios."
