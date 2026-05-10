# Issue Template

```markdown
---
id: "{id}"
title: "{title}"
created: {today}
updated: {today}
sessions: []
---

## Objective
One sentence. What done looks like.

## Scenarios
- S1. Given ... When ... Then ...
- S2. ...

## Off-limits
What will not be touched and why.

## Context
Background, links, constraints, prior decisions.
Paste any relevant design-constraints block here.

## Tasks
- [ ] S1, S2 — label
- [ ] S3 — label

## Open questions
- [ ] ?

---
### Facts
### Spikes
```

## Field notes

**Scenarios** — co-authored with the issue skill. Each `Sn` maps to one or more tasks.
Rejected proposals during co-authoring become Off-limits entries.

**Tasks** — derived from scenario groupings, not written independently. Each task
references its scenarios so the TDD skill knows what to implement.

**An issue is active** when it exists in `~/engineering/issues/` (not `archive/`).
Archive when all tasks are complete — that is the human's action, not the agent's.
