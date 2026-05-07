---
description: >
  Retrieves the full intent context behind a commit — issue objective, task, linked
  facts, semantic git note, and session document — given a commit hash.
when_to_use: >
  Use when debugging a change and wanting to understand why it was made. Triggers on
  "por que isso foi mudado", "contexto desse commit", "provenance <hash>", "quem mudou
  isso e por quê", "o que motivou essa mudança", or after a git blame when investigating
  a specific commit hash. Do not use for code traversal without a hash — use
  dead-reckoning for that.
argument-hint: [commit-hash]
arguments: [commit_hash]
allowed-tools: Bash(git:*) Bash(rg:*) Bash(fd:*) Bash(cat:*)
---

# Provenance

Recovers the full intent behind a commit by traversing from the hash to the issue
that produced it, the task that corresponds to it, the facts that informed it, and
the session that generated it.

---

## Environment detection

Attempt to use the Bash tool. If unavailable, you are on Claude Desktop — follow the
Desktop path in each step.

---

## Step 1 — Resolve the hash

```bash
HASH="${ARGUMENTS:-HEAD}"
FULL_HASH=$(git rev-parse "$HASH" 2>/dev/null)
```

If `git rev-parse` fails, tell the user the hash is invalid and stop.

If `$ARGUMENTS` is empty, use `HEAD` and surface that to the user:
> "No hash provided — using HEAD (`$FULL_HASH`)."

---

## Step 2 — Find the issue

Search active issues first, then archive:

```bash
ISSUE_FILE=$(rg "$HASH" ~/engineering/issues/ -l 2>/dev/null | head -1)

if [ -z "$ISSUE_FILE" ]; then
  ISSUE_FILE=$(rg "$HASH" ~/engineering/issues/archive/ -l 2>/dev/null | head -1)
fi
```

---

## Step 3 — Read the issue

**If an issue file was found:**

Read the file. Extract and present:

- `id` and `title` from frontmatter
- `## Objective` — full text
- `## Scope` — full text
- The specific task line(s) containing `$HASH` — highlight this as the task that
  produced the commit
- `### Facts` — list of wiki links (used in Step 4)

**If no issue file was found:**

Inform the user:
> "No issue found referencing `$HASH`. The commit may predate the workflow system or
> the hash may have been committed outside a tracked session."

Proceed to Step 5 (git note) with whatever is available.

---

## Step 4 — Resolve linked facts

Parse the wiki links from `### Facts`:

```bash
FACT_SLUGS=$(rg '\[\[FACT-[^\]]+\]\]' "$ISSUE_FILE" -o | sed 's/\[\[//g; s/\]\]//g')
```

For each slug, locate and read the fact file:

```bash
for slug in $FACT_SLUGS; do
  fd "^${slug}\.md$" ~/engineering/facts/ -d 1
done
```

Read each found file. Present each fact's `## Statement` and `## Evidence` inline.
Do not present the full fact file verbatim — summarize if there are more than three facts.

**If `### Facts` is empty or absent:** skip this step silently.

---

## Step 5 — Read the semantic git note

```bash
GIT_NOTE=$(git notes show "$FULL_HASH" 2>/dev/null)
```

If output is non-empty, present the note as-is under a "Git note" heading.

If empty:
> "No git note attached to this commit. The commit may predate the workflow system."

---

## Step 6 — Retrieve the SESSION.md

Extract the session slug from the git note:

```bash
SESSION_SLUG=$(printf '%s' "$GIT_NOTE" | rg "^Session: (.+)" -r '$1')
```

If `SESSION_SLUG` is empty, note:
> "No Session: reference in this git note. Commit predates session tracking."
Skip to output.

Derive the sessions branch name and read the document:

```bash
SESSIONS_BRANCH=$(git config user.name \
  | tr '[:upper:]' '[:lower:]' \
  | tr -cs 'a-z0-9' '-' \
  | sed 's/-*$//;s/$/\/sessions/')

SESSION_DOC=$(git show "${SESSIONS_BRANCH}:${SESSION_SLUG}/SESSION.md" 2>/dev/null)
```

If `SESSION_DOC` is empty:
> "Session slug `$SESSION_SLUG` not found on `$SESSIONS_BRANCH`. Branch may not
> have been pushed to this machine."

---

## Output format

Present results in this order, omitting sections that yielded nothing:

```
## Provenance — <short hash>

**Issue:** <id> — <title>  [active | archived]
**Task:** - [x] <task line containing the hash>

### Objective
<objective text>

### Scope
<scope text>

### Facts considered
**FACT-NNN — <title>**
<statement>
<evidence anchor>

[...repeat per fact...]

### Git note
<note content>

### Session
**<session-slug>**
<Objective, Key decisions, Outcome from SESSION.md>
```

If nothing was found (no issue, no note, no session), say so plainly and suggest:
> "Run `git log --oneline -20` to confirm the hash is correct, or check if the commit
> was made outside a tracked session."

---

## Rules

- Never invent context. If a section is absent, say it is absent.
- Do not read `$HOME/engineering/issues/archive/` proactively — only fall back to it
  if the hash is not found in active issues.
- Do not present the full issue file verbatim. Extract only the sections above.
- Wiki link resolution is mandatory when `### Facts` is non-empty. Do not skip it.
- Session retrieval is mandatory when `Session:` is present in the git note. Do not
  skip it.
- If multiple issue files match the hash (should not happen), present the most recent
  one and flag the collision to the user.
