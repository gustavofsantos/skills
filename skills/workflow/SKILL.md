---
name: workflow
description: >
  Protocol for managing daily engineering work. The orchestrator skill — coordinates
  all other skills across the three phases of work: planning, execution, and review.
  Use whenever the user mentions an issue, starts a task, wants to know what's in progress,
  needs context recovery, or says things like "new issue", "start a session", "what are
  we working on", "recall", "continue", "create an issue for X", or "let's work on X".
  This skill is the entry point. It decides which other skills to invoke.
---

# Workflow

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
  spikes/               ← managed by the knowledge skill
  terms/                ← managed by the thinking-partner skill
```

---

## Issue format

```markdown
---
id: "001"
title: "Fix auth bug"
status: inbox | not-now | active | done
branch: feat/fix-auth
tags: [feature, api]
created: 2026-04-27
updated: 2026-04-27
---

## Objective

One sentence. What "done" looks like when this issue closes.

## Scope

**In:** what is explicitly included.
**Off-limits:** what will not be touched and why.

## Context

Relevant background. Links to Jira, Sentry, docs, prior decisions.
If design constraints apply (evolutionary-design, incremental-refactor),
state them here as named constraints — not as prose.

## Open questions

- [ ] ?

## Tasks

- [ ] Task 1
- [ ] Task 2 abc1234

---

### Facts
- [[FACT-007-auth-token-refresh-window]]

### Spikes
- [[001-auth-investigation]]
```

**Valid statuses:** `inbox` `not-now` `active` `done`

**`branch`** — optional. When present, used to locate worktree context.
**`### Facts`** — wiki links to facts in `~/engineering/facts/` relevant to this issue.
**`### Spikes`** — wiki links to spike narratives in `~/engineering/spikes/`.

---

## Issue management

**Creating an issue:** determine the next ID by listing `~/engineering/issues/` and
incrementing the highest existing number. Create the file directly.

**Archiving an issue:** move the file to `~/engineering/issues/archive/`. Spikes and
facts are not moved — they outlive the issue.

**On task completion:** mark the task `[x]`, append the short commit hash inline, and
update `updated:` in frontmatter.

**On issue completion:** when all tasks are `[x]`, signal:
> "All tasks complete. Ready for review."

The agent never sets status to `done` unilaterally. That is the human's action after review.

---

## Skill integration

| Moment | Skill |
|---|---|
| Raw idea needs shaping | `user-story-builder` |
| Issue needs tasks broken down | `user-story-planner` |
| Objective is unclear or complex | `thinking-partner` |
| Open questions remain before execution | `dead-reckoning` |
| Implementation with new behavior | `test-design` → `tdd-design` |
| Design choice feels coupled or tangled | `thinking-lenses` (Braided) |
| Bug keeps recurring or fix feels like a patch | `thinking-lenses` (Iceberg) |
| Review before PR | `review` |
| Code smell or duplication found | `incremental-refactor` constraints (in issue Context) |
| New feature, unsure where to start | `evolutionary-design` constraints (in issue Context) |

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

User informs the issue to work on. If not provided, ask before proceeding — do not guess.

1. Run knowledge retrieval.
2. Read the issue — objective, scope, context, open questions, tasks.
3. If `## Open questions` has unresolved items:
   > "There are open questions on this issue. Recommend resolving them before execution.
   > Want to run dead-reckoning, or proceed and treat them as known risks?"
   Wait for the human's decision.
4. State what you understand and what you're about to do. Wait for confirmation
   if anything is ambiguous.

### During execution

**After each completed task:**
1. Mark `[x]` in `## Tasks` and append the short commit hash: `- [x] Task description abc1234`
2. Attach a git note to that commit:
   ```bash
   git notes add -m "Task: <task title>
   Issue: <issue id>-<slug>
   Why: <one sentence from issue Objective or Context>
   Facts: <wiki links if any>
   Files: <files changed>" $(git log -1 --format="%H")
   ```
3. Update `updated:` in the issue frontmatter.

**When a discovery warrants permanent storage:**
→ invoke `knowledge` skill. Add the wiki link under `### Facts` in the issue.

**When work surfaces something outside issue scope:**
→ create a new issue in `inbox`. Do not expand scope silently.
→ if it blocks current work, add it to `## Open questions` and surface it to the human.

**When all tasks are `[x]`:**
> "All tasks complete. Ready for review."

### Context recovery

When resuming after any interruption:

1. User informs the issue.
2. Run knowledge retrieval.
3. Read the issue — tasks tell you exactly where execution stopped.
4. State the reconstruction: "We were doing X. The remaining tasks are Y and Z."
5. Wait for confirmation before proceeding.

---

## Phase 3 — Reviewing an issue

When all tasks are complete, invoke `review` skill.

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
