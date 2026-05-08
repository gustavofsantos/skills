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
allowed-tools: Read Write Edit Bash(rg:*) Bash(fd:*) Bash(mv:*) Bash(git:*) Bash(qmd:*)
---

# Workflow

> **Orchestrator skill.** Decides which other skills to invoke at each
> phase of an issue. Always read the [Skill chain](#skill-chain) section
> below before any execution — it is the routing map for the entire
> plugin.

## Skill chain

| Moment | Skill |
|---|---|
| Raw idea needs shaping | `user-story-builder` |
| Issue needs tasks broken down | `user-story-planner` |
| Objective is unclear or complex | `thinking-partner` |
| Thinking session needs depth | `thinking-lenses` (offered by thinking-partner) |
| Open questions remain before execution | `dead-reckoning` (dispatches subagent) |
| Unfamiliar codebase, no facts yet | `survey` (dispatches subagent; run before `dead-reckoning`) |
| New abstraction, API surface, or module boundary to design | `design` (modes: `boundary`, `abstraction`) |
| Implementation with new behavior | `tdd-design` (spec conversation → TDD cycle) |
| Refactor without behavior change | `design-constraints` (mode: `refactor`) |
| New feature, unsure where to start | `design-constraints` (mode: `evolutionary`) |
| Review before PR | `deep-review` (dispatches subagent) |
| Need to validate a feature in an environment | `playbook-builder` |
| Discover a fact worth keeping | `knowledge` |
| Jira ticket ID or URL appears | `jira-context` (run immediately, do not ask) |

---

## Current issues

```bash
fd -t f -e md . ~/engineering/issues 2>/dev/null | grep -v '/archive/' | sort
```

One file → use it. Multiple files → list them and ask the human which one
to work on. Zero files → ask.

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
  thinking/             ← managed by the thinking-partner skill
  .counters/            ← sequential ID files: issues, facts, spikes, terms
```

---

## Triviality gate

Not every request is an issue. Skip the orchestration chain when **all** hold:

- Bounded to one file (or a small, obviously related set)
- Reversible in a single commit (no migrations, no schema changes, no public-API breaks)
- No new behaviour — typo fix, rename, comment update, mechanical refactor with tests green
- User did not explicitly ask for an issue

In that case, **execute directly**. When in doubt:
> "This looks small enough to do directly — sound right, or do you want it tracked?"

---

## Project-level recipes win

Before dispatching to any plugin skill, scan the current project's `CLAUDE.md`:

```bash
fd -t f -d 2 'CLAUDE\.md' . 2>/dev/null | head -3
```

Priority:
1. Direct project recipe in `CLAUDE.md` — use as written
2. Plugin skill that fits — invoke as the chain table directs
3. Generic engineering judgement

---

## Issue format

See [references/issue-template.md](references/issue-template.md) for the canonical template.

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

**On issue completion:** when all tasks are `[x]`:
> "All tasks complete. Ready for review."

The agent never archives or marks issues done unilaterally. That is the human's action.

---

## Knowledge retrieval — session start

Run at the start of every session, silently, before any other action:

```bash
qmd query "<issue title> <issue objective>" --min-score 0.5 -n 8 2>/dev/null || true
```

Load returned facts and spike excerpts into working context.
If nothing scores above threshold, proceed without — do not ask the human.

If something surfaces that the human hasn't mentioned:
> "Before we start — [[FACT-012-auth-token-refresh]] covers token refresh behavior here.
> Worth keeping in mind."

If a loaded fact contradicts something in the issue's Context: surface it immediately.

---

## Phase 1 — Planning an issue

Entry points: Jira ticket, Sentry issue, verbal description, scratch idea.

1. Create the issue file at `~/engineering/issues/<nnn>-<slug>.md`.
2. Fill `## Objective` — one sentence, defines done.
3. Fill `## Scope` — in and off-limits. Both fields required before tasks are written.
4. Fill `## Context` with background, links, and constraints.
5. Run knowledge retrieval. Surface relevant facts.
6. Fill `## Open questions` with anything unresolved.

**If open questions exist before tasks are written:**
→ invoke `dead-reckoning`. Add the resulting spike link under `### Spikes`. Clear resolved questions.

**If objective is clear enough to proceed:**
→ invoke `user-story-builder` if scope needs shaping.
→ invoke `user-story-planner` to break into tasks.

**When generating tasks for implementation work,** the first task is always:
```
- [ ] Spec + implement: behavioral contract → TDD (tdd-design)
```
This ensures tdd-design runs before any production code is written.

→ Write tasks into `## Tasks`. The issue is now active (present in issues/, not archived).

**Issue stays lean.** Objective + scope + context + questions + tasks + pointers.
Narrative belongs in spikes. Facts belong in the knowledge library.

---

## Phase 2 — Executing an issue

### Session start protocol

User informs the issue to work on. If not provided, list issues and ask.

1. **Run knowledge retrieval.**

   ```bash
   qmd query "<issue title> <issue objective>" --min-score 0.5 -n 8 2>/dev/null || true
   ```

   Load returned facts and spike excerpts into working context.

   If something surfaces that the human hasn't mentioned:
   > "Before we start — [[FACT-012-auth-token-refresh]] covers token refresh behavior
   > here. Worth keeping in mind."

   If a loaded fact contradicts something in the issue's Context: surface it
   immediately before any execution begins.

2. **Stamp the session ID into the issue frontmatter.**

   The current session ID was injected at session start (look for **Session ID:** in
   the session context). Use Edit to append it to the `sessions:` frontmatter field —
   an inline YAML list, e.g. `sessions: ["abc123"]` or `sessions: ["abc123", "def456"]`.

   This links the issue to the session so the UserPromptSubmit hook injects resume
   context on every subsequent turn.

   If the session ID is already in the `sessions:` list, skip this step.

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

2. Attach a git note to the commit:
   ```bash
   git notes add -m "Task: <task title>
   Why: <one sentence from issue Objective>
   Files: <files changed>" $(git log -1 --format="%H")
   ```

3. Update `updated:` in the issue frontmatter.

**When a discovery warrants permanent storage:**
→ invoke `knowledge` skill. Add the wiki link under `### Facts` in the issue.

**When work surfaces something outside issue scope:**
→ create a new issue in `~/engineering/issues/`. Do not expand scope silently.
→ if it blocks current work, add it to `## Open questions` and surface it.

**When all tasks are `[x]`:**
> "All tasks complete. Ready for review — invoking `deep-review` next."

Then invoke the `deep-review` skill on the branch diff.

### Context recovery

When resuming after any interruption:

1. User informs the issue (or list issues to pick one).
2. Run knowledge retrieval.
3. Read the issue — tasks tell you exactly where execution stopped.
4. State the reconstruction: "We were doing X. Remaining tasks: Y and Z."
5. Wait for confirmation before proceeding.

---

## Phase 3 — Reviewing an issue

When all tasks are complete, invoke `deep-review` skill.

After review passes:
1. Human archives the issue: move file to `~/engineering/issues/archive/`.
2. Spikes and facts are not moved — they outlive the issue.

---

## Rules

- Never read `archive/`. Stale context.
- `## Scope` with explicit off-limits is required before tasks are written.
- `## Open questions` must be reviewed at session start. Non-empty = risk. Name it.
- The agent marks tasks `[x]` as they complete — never in bulk at session end.
- The agent never archives issues. That is the human's action.
- Scope violations are not silent. New work goes to a new issue.
- Facts and spikes are pointers only. Never copy content into the issue.
