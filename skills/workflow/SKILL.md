---
description: >
  Protocol for managing daily engineering work — the orchestrator that coordinates all other
  skills across planning, execution, and review phases.
when_to_use: >
  Use whenever the user mentions an issue, starts a task, wants to know what's in progress,
  needs context recovery, or says things like "new issue", "nova issue", "start a session",
  "começar a trabalhar", "vamos trabalhar em X", "let's work on X", "what are we working on",
  "what should I do next", "o que estamos fazendo", "recall", "continue", "continuar",
  "resume", "retomar", "create an issue for X", "criar uma issue para". This skill is the
  ENTRY POINT — it decides which other skills to invoke and chains them together.
argument-hint: [action] [issue-id]
arguments: [action, issue_id]
allowed-tools: Read Write Edit Bash(rg:*) Bash(fd:*) Bash(mv:*) Bash(cat:*) Bash(qmd:*) Bash(git:*)
---

# Workflow

> **Orchestrator skill.** Decides which other skills to invoke at each
> phase of an issue. Always read the [Skill chain](#skill-chain) section
> below before any execution — it is the routing map for the entire
> plugin.

## Skill chain

The orchestrator routes work to specialist skills. This table is the
single source of truth for which skill handles which moment:

| Moment | Skill |
|---|---|
| Raw idea needs shaping | `user-story-builder` |
| Issue needs tasks broken down | `user-story-planner` |
| Objective is unclear or complex | `thinking-partner` |
| Thinking session needs depth | `thinking-lenses` (offered by thinking-partner) |
| Open questions remain before execution | `dead-reckoning` |
| Unfamiliar codebase, no facts yet | `survey` (run before `dead-reckoning`) |
| New abstraction or API surface to design | `interface-design` |
| Module boundaries / coupling questions | `bounded-contexts` |
| Implementation with new behavior | `test-design` (writes contract into issue) → `tdd-design` |
| GREEN phase, overthinking the implementation | `shameless-green` |
| Refactor without behavior change | `incremental-refactor` constraints (in issue Context) |
| New feature, unsure where to start | `evolutionary-design` constraints (in issue Context) |
| Review before PR | `deep-review` (dispatches to subagent) |
| Need to validate a feature in an environment | `playbook-builder` |
| Discover a fact worth keeping | `knowledge` |
| Investigate why a commit was made | `provenance` (dispatches to subagent) |
| Jira ticket ID or URL appears | `jira-context` (run immediately, do not ask) |
| Wrapping up the working session | `session-close` |

The plugin also ships a SessionStart hook that surfaces the active
issue, inbox, and last session at session begin — the model receives
that context automatically and should consult it before asking the
human "what are we working on".

---

## Currently active issues

```bash
rg -l '^status: active$' ~/engineering/issues -g '*.md'
```

## Inbox issues

```bash
rg -l '^status: inbox$' ~/engineering/issues -g '*.md'
```

---

One abstraction. One source of truth.

**Issue** — unit of intent and execution state. Lives at `~/engineering/issues/<nnn>-<slug>.md`.

The issue carries everything needed to resume work across sessions without any additional
state file. Plan Mode handles transient session state. The issue handles everything else.

---

## Directory layout

```
~/engineering/
  issues/
    001-fix-auth-bug.md
    archive/            ← completed issues — never read these
  facts/                ← managed by the knowledge skill
  spikes/               ← managed by the knowledge skill (produced by dead-reckoning)
  terms/                ← managed by the knowledge skill (business domain definitions)
  playbooks/            ← managed by the playbook-builder skill
  thinking/             ← managed by the thinking-partner skill (progress + flush files)
  .counters/            ← sequential ID files: issues, facts, spikes, terms
```

The vault is the single root for all long-lived state. There is no parallel
`~/.knowledge/` or `~/.config/shared-memory/` tree — every artifact lives
under one prefix so paths are predictable across skills.

---

## Issue format

See [references/issue-template.md](references/issue-template.md) for the canonical template with field reference.

---

## Issue management

**Creating an issue:**

1. Read `~/engineering/.counters/issues` (treat as `0` if absent). Increment and write back (zero-pad to 3 digits).
2. Slugify the title (lowercase, hyphens, max 5 words).
3. Write `~/engineering/issues/<NNN>-<slug>.md` — use the template in `references/issue-template.md`.
4. Confirm: "Created issue <NNN>: <title>."

**Archiving an issue:** move the file to `~/engineering/issues/archive/`. Spikes and
facts are not moved — they outlive the issue.

**On task completion:** mark the task `[x]`, append the short commit hash inline, and
update `updated:` in frontmatter.

**On issue completion:** when all tasks are `[x]`, signal:
> "All tasks complete. Ready for review."

The agent never sets status to `done` unilaterally. That is the human's action after review.

---

## Knowledge retrieval — session start

Run at the start of every session, silently, before any other action:

```bash
qmd query "<issue title> <issue objective>" --min-score 0.5 -n 8
```

Load returned facts and spike excerpts into working context.
If nothing scores above threshold, proceed without — do not ask the human.

If something surfaces that the human hasn't mentioned:
> "Before we start — [[FACT-012-auth-token-refresh]] covers token refresh behavior here.
> Worth keeping in mind."

If a loaded fact contradicts something in the issue's Context: surface it immediately
before any execution begins.

Then run a second query targeting terms for the relevant domain:

```bash
qmd query "<domain> <key concepts from objective>" --min-score 0.5 -n 5
```

Filter results to `~/engineering/terms/`. Surface relevant terms the same way as facts.

---

## Phase 1 — Planning an issue

Entry points: Jira ticket, Sentry issue, verbal description, scratch idea.

1. Create the issue file at `~/engineering/issues/<nnn>-<slug>.md`.
2. Fill `## Objective` — one sentence, defines done.
3. Fill `## Scope` — in and off-limits. Both fields required before the issue goes active.
4. Fill `## Context` with background, links, and constraints.
5. Run knowledge retrieval. Surface relevant facts.
6. Fill `## Open questions` with anything unresolved.

**If open questions exist before tasks are written:**
→ invoke `dead-reckoning`. Add the resulting spike link under `### Spikes`. Promote
  confirmed facts and add links under `### Facts`. Clear resolved questions.

**If objective is clear enough to proceed:**
→ invoke `user-story-builder` if scope needs shaping.
→ invoke `user-story-planner` to break into tasks.
→ write tasks into `## Tasks`. Set status to `active`.

**Issue stays lean.** Objective + scope + context + questions + tasks + pointers.
Narrative belongs in spikes. Facts belong in the knowledge library.

---

## Phase 2 — Executing an issue

### Session start protocol

User informs the issue to work on. If not provided, ask before proceeding —
do not guess.

1. **Retrieve the last session for this issue.**

   Extract the issue ID from the issue file frontmatter and search the sessions branch:

   ```bash
   ISSUE_ID=$(rg '^id:' "$ISSUE_FILE" | head -1 | sed 's/id: *//;s/"//g' | tr -d '[:space:]')

   SESSIONS_BRANCH=$(git config user.name \
     | tr '[:upper:]' '[:lower:]' \
     | tr -cs 'a-z0-9' '-' \
     | sed 's/-*$//;s/$/\/sessions/')

   LAST_SESSION=$(git show "${SESSIONS_BRANCH}" 2>/dev/null \
     | git ls-tree "${SESSIONS_BRANCH}" 2>/dev/null \
     | rg "\t${ISSUE_ID}-" \
     | awk '{print $NF}' \
     | sort | tail -1)

   if [ -n "$LAST_SESSION" ]; then
     git show "${SESSIONS_BRANCH}:${LAST_SESSION}/SESSION.md" 2>/dev/null
   fi
   ```

   If a SESSION.md is found, surface it immediately:

   > "Last session on this issue: [outcome]. Key decisions: [...].
   > Pending tasks from that session: [any [ ] tasks listed]."

   If the sessions branch does not exist or no session matches the issue ID,
   proceed silently — this is expected for issues that have not been worked on yet.

2. **Run knowledge retrieval.**

   ```bash
   qmd query "<issue title> <issue objective>" --min-score 0.5 -n 8
   ```

   Load returned facts and spike excerpts into working context.
   If nothing scores above threshold, proceed without — do not ask the human.

   If something surfaces that the human hasn't mentioned:
   > "Before we start — [[FACT-012-auth-token-refresh]] covers token refresh behavior
   > here. Worth keeping in mind."

   If a loaded fact contradicts something in the issue's Context: surface it
   immediately before any execution begins.

   Then run a second query targeting terms for the relevant domain:

   ```bash
   qmd query "<domain> <key concepts from objective>" --min-score 0.5 -n 5
   ```

   Filter results to `~/engineering/terms/`. Surface relevant terms the same way
   as facts.

3. **Read the issue** — objective, scope, context, open questions, tasks.

4. **If `## Open questions` has unresolved items:**
   > "There are open questions on this issue. Recommend resolving them before
   > execution. Want to run dead-reckoning, or proceed and treat them as known risks?"
   Wait for the human's decision.

5. **State what you understand and what you're about to do.** Wait for confirmation
   if anything is ambiguous.

### During execution

**After each completed task:**

1. Mark `[x]` in `## Tasks` and append the short commit hash: `- [x] Task description abc1234`

2. Assemble the summarization input from what is already in working context:
   issue objective, completed task title, and prose of any facts loaded this session
   that were relevant to this task. Pipe to Haiku to produce a self-contained Context field:
```bash
   CONTEXT_SUMMARY=$(printf "Issue objective: <objective>\nTask: <task title>\nContext used:\n<prose of relevant loaded facts — omit if none>" \
     | claude -p \
       "Summarize in 2-3 sentences what was known and what informed this task. Self-contained — no file paths, no wiki links, no FACT-NNN references. Plain prose only." \
       --model claude-haiku-4-5-20251001 \
       --max-turns 1)
```

3. Attach a git note to that commit:
```bash
   git notes add -m "Task: <task title>
   Why: <one sentence from issue Objective>
   Context: $CONTEXT_SUMMARY
   Files: <files changed>" $(git log -1 --format="%H")
```
   Omit the `Context:` field entirely if no facts or session context informed this task.

4. Update `updated:` in the issue frontmatter.

**When a discovery warrants permanent storage:**
→ invoke `knowledge` skill. Add the wiki link under `### Facts` in the issue.

**When work surfaces something outside issue scope:**
→ create a new issue in `inbox`. Do not expand scope silently.
→ if it blocks current work, add it to `## Open questions` and surface it to the human.

**When all tasks are `[x]`:**
> "All tasks complete. Ready for review — invoking `deep-review` next."

Then invoke the `deep-review` skill on the branch diff. Phase 1 (scope and
safety) gates whether Phase 2 runs.

### Context recovery

When resuming after any interruption:

1. User informs the issue.
2. Run knowledge retrieval.
3. Read the issue — tasks tell you exactly where execution stopped.
4. State the reconstruction: "We were doing X. The remaining tasks are Y and Z."
5. Wait for confirmation before proceeding.

---

## Phase 3 — Reviewing an issue

When all tasks are complete, invoke `deep-review` skill.

After review passes:
1. Human sets status to `done`.
2. Move issue file to `~/engineering/issues/archive/`.
3. Spikes and facts are not moved — they outlive the issue.

---

## Rules

- Never read `archive/`. Stale context.
- `## Scope` with explicit off-limits is required before an issue goes `active`.
- `## Open questions` must be reviewed at session start. Non-empty = risk. Name it.
- The agent marks tasks `[x]` as they complete — never in bulk at session end.
- The agent never rewrites `## Objective`, `## Scope`, or `## Context`. Those belong to the human.
- Scope violations are not silent. New work goes to a new issue in `inbox`.
- Facts and spikes are pointers only. Never copy content into the issue.
- The agent never sets status to `done`. That is the human's action.
