# Thinking Partner — File Templates

---

## Progression file

Path: `~/engineering/thinking/{topic}/progress.md`

```markdown
# {Topic or problem name}

**Started:** {date}
**Last updated:** {date}
**Status:** in progress | ready to flush

## Assumptions

- [grounded] {assumption with evidence}
- [inferred] {assumption that seems likely}
- [inherited] {assumption that came with the domain, never examined}

## Progression

[1] {established}
[2] {established}
[3] {current or most recent}
    → open: {unresolved}
    → set aside: {deprioritized — reason}

## Revised steps

{Steps that were revised, with original reasoning and what changed}

## Open threads

{Things surfaced during the session that weren't followed — worth returning to}
```

Write after each step is established. Do not wait for the end of the session.

---

## Flush file

Path: `~/engineering/thinking/{topic}/flush.md`

```markdown
# {Problem or feature name}

**Thinking file:** ~/engineering/thinking/{topic}/progress.md
**Flushed:** {date}

## Context
{Repo path if relevant. Last known commit if known.}

## What was understood
{Shared understanding reached — specific conclusions with the reasoning, not just the outcome.}

## What was decided
{Specific decisions. Each with a brief why.}

## Off-limits
{What was explicitly ruled out and why.}

## Dragons
{Known risks, fragile assumptions, things likely to break, people or systems to coordinate with.}

## Open questions
{What remains unresolved. The agent should surface these, not resolve them independently.}

## First move
{One concrete starting point. Not a plan — the next step.}
```

After flushing, update `progress.md` status to `flushed` and note the flush file location.
