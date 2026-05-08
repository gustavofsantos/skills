# Issue Template

```markdown
---
id: "{id}"
title: "{title}"
status: inbox
branch:
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
If design constraints apply (evolutionary-design, incremental-refactor),
state them here as named constraints — not as prose.

## Open questions

- [ ] ?

## Behavioral contract

<!--
Optional. Filled by `test-design` when the issue describes new behaviour.
Omit the section entirely until cases exist — same convention as ### Facts.

Format:

**Unit:** `<identifier>` — <one-sentence responsibility>
**Test location:** `<file path>` > `<describe block>`

- C1. Given <context>, When <action>, Then <outcome>
- C2. Given <context>, When <action>, Then <outcome>

For multi-unit issues, use one subsection per unit:

### Unit: cart
- C1. ...
- C2. ...

### Unit: pricing
- C3. ...
-->

## Tasks

- [ ] Task 1
<!--
For TDD work, tasks reference cases by ID rather than restating them:

- [ ] C1, C2 — implement empty-cart error and happy path
- [ ] C3 — handle currency boundary
- [ ] C4–C6 — collaborator failure modes

For non-TDD work (refactor, infra, docs), tasks remain imperative.
-->

---

### Facts
- [[FACT-NNN-slug]]

### Spikes
- [[NNN-slug]]
```

**Valid statuses:** `inbox` `not-now` `active` `done`

**`branch`** — optional. When present, used to locate worktree context.
**`### Facts`** — wiki links to facts in `~/engineering/facts/` relevant to this issue.
**`### Spikes`** — wiki links to spike narratives in `~/engineering/spikes/`.

## Refinement progression

An issue progresses through stages of refinement, each adding precision:

| Stage | Sections populated |
|---|---|
| `inbox` | Objective, maybe Context |
| `shaped` | + Scope, + Open questions |
| `contracted` | + Behavioral contract (TDD work only) |
| `planned` | + Tasks (referencing cases for TDD work) |
| `executing` | tasks getting `[x]`, commit hashes appended |
| `done` | all tasks `[x]`, archived |

The same file holds every stage. Reading the file at any point shows
exactly how refined the issue is.
