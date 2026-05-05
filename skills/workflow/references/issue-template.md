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

## Tasks

- [ ] Task 1

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
