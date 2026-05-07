# Git Context Retrieval

Standard protocol for recovering intent from git notes and SESSION.md files before
starting investigative or review work. Invoked by `dead-reckoning`, `workflow`,
`provenance`, and `deep-review` when commit history is relevant to the task.

## When to invoke

- Investigating existing behavior in a specific path or subsystem
- Resuming work on an issue with prior session history
- Reviewing a branch before raising a PR
- Resolving the intent behind a specific commit hash

## Protocol

### Step A — Identify commits

**From a file path or set of paths:**
```bash
COMMITS=$(git log --format="%H" -20 -- <path> [<path2> ...])
```

**From the current branch (session scope):**
```bash
BASE=$(git merge-base HEAD \
  "origin/$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null \
  | sed 's|refs/remotes/origin/||')" 2>/dev/null \
  || git rev-list --max-parents=0 HEAD)
COMMITS=$(git log "${BASE}..HEAD" --format="%H")
```

**From a specific hash:** use that hash directly.

---

### Step B — Read git notes

```bash
NOTES=$(echo "$COMMITS" | while read h; do
  note=$(git notes show "$h" 2>/dev/null)
  [ -z "$note" ] && continue
  short=$(git rev-parse --short "$h")
  printf "### %s\n%s\n\n" "$short" "$note"
done)
```

If no notes exist for any commit, state this explicitly and proceed — the absence
of notes is itself information (commit predates the workflow system or was made
outside a tracked session).

---

### Step C — Resolve Session: references

Extract session slugs from the collected notes:

```bash
SESSION_SLUGS=$(printf '%s' "$NOTES" | rg "^Session: (.+)" -r '$1' | sort -u)
```

Derive the sessions branch name and retrieve each SESSION.md:

```bash
SESSIONS_BRANCH=$(git config user.name \
  | tr '[:upper:]' '[:lower:]' \
  | tr -cs 'a-z0-9' '-' \
  | sed 's/-*$//;s/$/\/sessions/')

SESSION_DOCS=$(echo "$SESSION_SLUGS" | while read slug; do
  [ -z "$slug" ] && continue
  doc=$(git show "${SESSIONS_BRANCH}:${slug}/SESSION.md" 2>/dev/null)
  [ -z "$doc" ] && continue
  printf "### %s\n%s\n\n" "$slug" "$doc"
done)
```

If the branch does not exist or a slug is not found, continue silently — the
git notes alone are still useful context.

---

### Step D — Surface findings

Present the recovered context before starting any traversal or analysis:

```
Git context — <N> commits, <M> session(s) found

Commits:
  <short-hash> — <Task field from note>
  <short-hash> — <Task field from note>
  ...

Sessions:
  <slug>: <Objective> | Outcome: <outcome>
  Key decisions: <bullet list from SESSION.md>
```

If the recovered context directly answers the question at hand, or significantly
reshapes the expected entry point, surface this before proceeding:

> "The last session on this path ([session-slug]) already investigated X and
> concluded Y. Should we treat that as a starting axiom, or verify it fresh?"

---

## What this protocol does not do

- Does not query `~/engineering/` — that is the `qmd` retrieval step, which runs
  separately and is complementary to this one.
- Does not replace code traversal — it informs where to start and what to expect.
- Does not surface everything — only what is directly relevant to the paths or
  commits under investigation.
