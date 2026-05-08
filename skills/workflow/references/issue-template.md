# Issue Template

```markdown
---
id: "{id}"
title: "{title}"
branch:
session:
tags: []
created: {today}
updated: {today}
---

## Objective

One sentence. What "done" looks like when this issue closes.

## Scope

**In:** what is explicitly included.
**Off-limits:** what will not be touched and why.

## Context

Relevant background. Links to Jira, Sentry, docs, prior decisions.
If design constraints apply, paste the relevant `design-constraints` block here.

## Open questions

- [ ] ?

## Behavioral contract

<!--
Filled by `tdd-design` Phase 1 when the issue describes new behaviour.
Omit entirely until cases exist.

**Unit:** `<identifier>` — <one-sentence responsibility>
**Test location:** `<file path>` > `<describe block>`

- C1. Given <context>, When <action>, Then <outcome>
- C2. ...
-->

## Tasks

<!--
For TDD work, the first task is always the spec + implementation task:

- [ ] Spec + implement: behavioral contract → TDD (tdd-design)

Subsequent tasks (if the issue has multiple units or phases):

- [ ] C1, C2 — implement empty-cart error and happy path
- [ ] C3 — handle currency boundary

For non-TDD work (refactor, infra, docs), tasks remain imperative.
-->

- [ ] Task 1

---

### Facts
- [[FACT-NNN-slug]]

### Spikes
- [[NNN-slug]]
```

**`branch`** — optional. When present, used to locate worktree context.
**`### Facts`** — wiki links to facts in `~/engineering/facts/` relevant to this issue.
**`### Spikes`** — wiki links to spike narratives in `~/engineering/spikes/`.

An issue is **active** when it exists in `~/engineering/issues/` (not `archive/`).
Archive when all tasks are complete.

## Refinement progression

| Stage | Sections populated |
|---|---|
| Created | Objective, maybe Context |
| Shaped | + Scope, + Open questions |
| Contracted | + Behavioral contract (TDD work only) |
| Planned | + Tasks |
| Executing | Tasks getting `[x]`, commit hashes appended |
| Done | All tasks `[x]`, archived |
