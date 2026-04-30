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
  terms/                ← managed by the knowledge skill
    financeiro/
    fretboard/
  thinking/             ← managed by the thinking-partner skill
  .counters/
    issues
    facts
    spikes
    terms
```

---

## Scripts

All scripts live at `~/.claude/skills/workflow/scripts/` and are invoked with `python3`.

| Script | Purpose |
|---|---|
| `work-issue-create.py` | Scaffold a new issue |
| `work-issue-list.py` | List issues, filter by status or tag |
| `work-issue-archive.py` | Move a done issue to archive |
| `work-term-create.py` | Scaffold a new term (knowledge/terms) |

```bash
SCRIPTS=~/.claude/skills/workflow/scripts

python3 $SCRIPTS/work-issue-create.py --title "Fix auth bug" --status inbox
python3 $SCRIPTS/work-issue-list.py --status active --format text
python3 $SCRIPTS/work-issue-archive.py --issue 001
python3 $SCRIPTS/work-term-create.py --term "Ciclo de faturamento" --domain financeiro
```

All scripts accept `--format json` (default) or `--format text`.

---

## Issue schema

```yaml
---
id: "001"
title: "Fix auth bug"
status: inbox | not-now | active | done
branch: feat/fix-auth          # optional — used for worktree context
tags: [feature, api]
facts:
  - "[[FACT-007-auth-token-refresh-window]]"
spikes:
  - "[[001-auth-investigation]]"
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

Questions that must be answered before or during execution.
If non-empty when work begins, consider dead-reckoning before writing tasks.

- [ ] ?

## Tasks

- [ ] Task 1
- [ ] Task 2
```

**Valid statuses:** `inbox` `not-now` `active` `done`

**On task completion:** agent marks the task `[x]` and updates `updated:` in frontmatter.

**On issue completion:** when all tasks are `[x]`, agent signals:
> "All tasks complete. Ready for review."

The agent never sets status to `done` unilaterally. That is the human's action after review.

**`facts`** — wiki links to facts in `~/engineering/facts/` relevant to this issue.
**`spikes`** — wiki links to spike narratives in `~/engineering/spikes/`.
**`branch`** — optional. When present, used to locate worktree context and filter knowledge retrieval.

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
qmd query "<issue title> <issue objective>" --min-score 0.5 -n 8 --files
```

Load returned facts and spike excerpts into working context.
If nothing scores above threshold, proceed without — do not ask the human.

If something surfaces that the human hasn't mentioned:
> "Before we start — [[FACT-012-auth-token-refresh]] covers token refresh behavior here.
> Worth keeping in mind."

If a loaded fact contradicts something in the issue's Context: surface it immediately
before any execution begins.

Then run a second query targeting terms for the relevant domain. Infer the domain from
the issue's tags, context, or the active card's subject matter:

```bash
qmd query "<domain> <key concepts from objective>" --min-score 0.5 -n 5 --files
```

Filter results to `~/engineering/terms/`. If a term surfaces that the human hasn't
mentioned and is directly relevant to the objective, surface it the same way as facts:

> "Before we start — [[TERM-003-ciclo-de-faturamento]] defines what a billing cycle
> means in this domain. Worth keeping in mind."

---

## Phase 1 — Planning an issue

Entry points: Jira ticket, Sentry issue, verbal description, scratch idea.

1. Create the issue:
   ```bash
   python3 ~/.claude/skills/workflow/scripts/work-issue-create.py \
     --title "<title>" [--status inbox] [--tags feature,api] [--branch feat/slug]
   ```
2. Fill `## Objective` — one sentence, defines done.
3. Fill `## Scope` — in and off-limits. Both fields required before the issue goes active.
4. Fill `## Context` with background, links, and constraints.
5. Run knowledge retrieval. Surface relevant facts.
6. Fill `## Open questions` with anything unresolved.

**If open questions exist before tasks are written:**
→ invoke `dead-reckoning`. Link resulting spike in `spikes:`. Promote confirmed
  facts to `~/engineering/facts/` and list in `facts:`. Clear resolved questions.

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
1. Mark `[x]` in `## Tasks`.
2. Update `updated:` in frontmatter.

**When a discovery warrants permanent storage:**
→ invoke `knowledge` skill. Add wiki link to issue's `facts:` field.

**When work surfaces something outside issue scope:**
→ create a new issue in `inbox`. Do not expand scope silently.
→ if it is an open question that blocks current work, add it to `## Open questions`
  and surface it to the human before continuing.

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
1. Set issue status to `done`.
2. Archive:
   ```bash
   python3 ~/.claude/skills/workflow/scripts/work-issue-archive.py --issue 001
   ```
   Moves issue to `archive/`. Spikes and facts remain — they outlive the issue.

---

## Rules

- Never read `archive/` directories. Stale context.
- `## Scope` with explicit off-limits is required before an issue goes `active`.
- `## Open questions` must be reviewed at session start. Non-empty = risk. Name it.
- The agent marks tasks `[x]` as they complete — never in bulk at session end.
- The agent never rewrites `## Objective`, `## Scope`, or `## Context`. Those belong to the human.
- Scope violations are not silent. New work goes to a new issue in `inbox`.
- Facts and spikes are pointers only. Never copy content into the issue.
- The agent never sets status to `done`. That is the human's action.
