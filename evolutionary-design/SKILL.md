---
name: evolutionary-design
description: >
  Provides design constraints for building new features or systems incrementally.
  Use this skill when the user is starting a new feature, module, or integration and
  wants to avoid big-bang design. In Claude Code sessions, this skill produces a
  constraint block to paste into the card's Context section — not an interactive
  protocol. Trigger on phrases like "where do I start", "how should I structure this",
  "let's build X", "I need to add Y", or any greenfield work.
---

# Evolutionary Design

## Core idea

Build the thinnest vertical slice that integrates all major layers and delivers
one piece of real behavior. Then grow it. Never design the full system upfront.

A tracer bullet is not a prototype. It is production code, deliberately incomplete,
that proves the path works end-to-end.

---

## How to use this skill in Claude Code

This skill does not run as an interactive protocol in Claude Code. Claude Code plans
and executes in single runs — an interactive red/green/refactor loop does not fit
that model.

Instead: **paste the constraint block below into the card's `## Context` section**
before starting the session. Claude Code reads it during planning and applies it
as constraints on how it structures the work.

---

## Constraint block

Copy this into the card's `## Context`:

```
## Design constraints — evolutionary design

- First deliverable: thinnest vertical slice through all layers.
  One real behavior, end-to-end. Nothing more.
- Do not build utilities, helpers, or infrastructure before behavior exists.
- Do not extract abstractions until two concrete cases exist.
- Hardcode values if they unblock the slice — generalize only when forced by
  a second case.
- Each subsequent task extends the existing path. It does not replace it.
- Skip edge cases, validation, and error handling in the first slice unless
  they block the slice from running at all.
```

---

## What "vertical slice" means

A slice touches every major layer of the feature:
UI (or API) → domain logic → persistence (or external call)

It does not mean:
- Building the data layer first, then the logic, then the UI
- Writing all the models before any behavior exists
- Scaffolding infrastructure "to support future work"

The first slice is deliberately incomplete. Its only job is to prove the path.

---

## Signals the constraint is being violated

- The agent proposes building a module with no behavior yet
- Abstractions appear before two concrete cases exist
- The plan has more than one layer being built before any layer is exercised
- "We'll need this later" appears as justification for any code

When you see these, redirect: thinnest slice first.

---

## Interactive use (pairing sessions, not Claude Code)

If working interactively rather than delegating to Claude Code:

1. Identify the vertical slice: what is the smallest interaction that touches all layers?
2. Build just that. Skip everything else.
3. Verify it runs end-to-end before expanding.
4. Add the next slice only after the first works.

Output when applying interactively:
1. **Slice definition** — one sentence describing the primitive whole
2. **Layer map** — which layers the slice touches
3. **First task** — first concrete file/function to write
4. **Expand plan** — next 2–3 slices in order
