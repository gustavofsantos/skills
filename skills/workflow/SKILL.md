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

## Skill chain

| Moment | Skill |
|---|---|
| Raw idea needs shaping | `user-story-builder` |
| Issue needs tasks broken down | `user-story-planner` |
| Objective is unclear or complex | `thinking-partner` |
| Thinking session needs depth | `thinking-lenses` (offered by thinking-partner) |
| Open questions remain before execution | `dead-reckoning` (dispatches subagent) |
| Unfamiliar codebase, no facts yet | `survey` (dispatches subagent; run before `dead-reckoning`) |
| New abstraction, API surface, or module boundary | `design` (modes: `boundary`, `abstraction`) |
| Implementation with new behavior | `tdd` |
| Refactor without behavior change | `design-constraints` (mode: `refactor`) |
| New feature, unsure where to start | `design-constraints` (mode: `evolutionary`) |
| Review before PR | `deep-review` (dispatches subagent) |
| Need to validate a feature in an environment | `playbook-builder` |
| Discover a fact worth keeping | `knowledge` |
| Jira ticket ID or URL appears | `jira-context` (run immediately, do not ask) |

---

## Triviality gate

Not every request is an issue. Skip orchestration when **all** hold:
- Bounded to one file (or a small, obviously related set)
- Reversible in a single commit (no migrations, schema changes, or public-API breaks)
- No new behaviour — typo fix, rename, mechanical refactor with tests green
- User did not explicitly ask for an issue

Execute directly. When in doubt: "This looks small enough to do directly — sound right?"

---

## Project-level recipes win

Check `CLAUDE.md` before dispatching to any skill:
```bash
fd -t f -d 2 'CLAUDE\.md' . 2>/dev/null | head -3
```
Priority: project recipe → plugin skill → generic judgement.

---

## Issue format

See [references/issue-template.md](references/issue-template.md) for the canonical template.

---

## Issue lifecycle

**Creating:**
1. Read `~/engineering/.counters/issues` (treat as `0` if absent). Increment and write back (zero-pad to 3 digits).
2. Slugify the title (lowercase, hyphens, max 5 words).
3. Write `~/engineering/issues/<NNN>-<slug>.md` using the template.
4. Confirm: "Created issue <NNN>: <title>."

**Task completion:** mark `[x]`, append short commit hash: `- [x] Task description abc1234`. Update `updated:` in frontmatter.

**Issue completion:** "All tasks complete. Ready for review." Never archive unilaterally — that is the human's action.

---

## Phase 1 — Planning

Entry points: Jira ticket, Sentry issue, verbal description, scratch idea.

1. Create the issue file.
2. Fill `## Objective` (one sentence, defines done) and `## Scope` (in and off-limits). Both required before tasks are written.
3. Fill `## Context` with background, links, constraints.
4. Search relevant facts: `qmd query "<issue title> <issue objective>" --min-score 0.5 -n 8 2>/dev/null || true`. Surface anything relevant that the human hasn't mentioned; skip silently if nothing scores above threshold.
5. Fill `## Open questions` with anything unresolved. If non-empty → invoke `dead-reckoning` before writing tasks.

**Invoking skills:**
- Scope needs shaping → `user-story-builder`
- Ready to break down → `user-story-planner`
- First task for implementation work is always: `- [ ] Spec + implement: behavioral contract → TDD (tdd)`

Issue stays lean: objective + scope + context + questions + tasks + pointers. Narrative belongs in spikes. Facts belong in the knowledge library.

After creating the issue, present it and wait for the human to confirm before proceeding.

---

## Phase 2 — Executing

### Session start

List active issues if none specified:
```bash
fd -t f -e md . ~/engineering/issues 2>/dev/null | grep -v '/archive/' | sort
```
One file → use it. Multiple → list and ask. Zero → ask.

1. Search relevant facts: `qmd query "<issue title> <issue objective>" --min-score 0.5 -n 8 2>/dev/null || true`. Surface anything that contradicts the issue or that the human hasn't mentioned; skip silently if nothing scores above threshold.
2. Read the issue — objective, scope, context, open questions, tasks.
3. If `## Open questions` is non-empty: "There are open questions. Want to run dead-reckoning, or proceed and treat them as known risks?" Wait for the decision.
4. State what you understand and what you're about to do. Wait for confirmation before starting.

### During execution

After each completed task: mark `[x]`, append commit hash, update `updated:`. Then surface the result to the human and wait.

Out-of-scope discovery → open a new issue, do not expand scope silently. If it blocks current work, add to `## Open questions` and surface it immediately.

Fact worth keeping → invoke `knowledge`. Add the link under `### Facts` in the issue.

When all tasks are `[x]` → invoke `deep-review` on the branch diff.

---

## Phase 3 — Review

Invoke `deep-review`. After review passes, the human archives the issue by moving it to `~/engineering/issues/archive/`. Spikes and facts are not moved — they outlive the issue.
