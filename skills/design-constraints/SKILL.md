---
description: >
  Produces named constraint blocks to paste into an issue's `## Context` section.
  Two modes — `evolutionary` (greenfield, tracer-bullet) and `refactor`
  (behavior-preserving incremental change).
when_to_use: >
  Use when planning an issue and the work needs guardrails the agent will follow
  during execution. Triggers on:
  • evolutionary — "where do I start", "how should I structure this", "let's build X",
    "I need to add Y", "novo módulo", "vou começar X", or any greenfield work.
  • refactor — "refactor this", "clean this up", "there's duplication here",
    "this feels wrong", "extract this", "refatorar", "limpar este código", or
    when code has structural problems identified during review.
  Output is a constraint block named after the mode, copied into the issue's
  `## Context`. The agent reads the issue at session start and applies them.
---

# Design Constraints

Read [references/guide.md](references/guide.md) for slice definition, violation signals,
flocking rules, safe moves, and characterization test guidance.

Two modes. Each emits a constraint block to paste into the issue's `## Context`.

| Mode | When | Block name |
|---|---|---|
| `evolutionary` | New feature, module, or integration. Path through layers is unproven. | `## Design constraints — evolutionary design` |
| `refactor` | Code is being restructured without changing behavior. Tests are the safety net. | `## Design constraints — incremental refactoring` |

---

## Mode: evolutionary

Build the thinnest vertical slice that integrates all major layers and delivers one piece
of real behavior. Then grow it. Never design the full system upfront.

A tracer bullet is not a prototype — it is production code, deliberately incomplete,
that proves the path works end-to-end.

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

## Mode: refactor

Refactoring is changing structure without changing behavior. The safety net is the test
suite. If tests aren't green before you start, fix that first.

```
## Design constraints — incremental refactoring

- Tests must be green before the first change. If they aren't, stop and report.
- One logical change at a time. Run tests after each change.
- If tests go red: undo the last change immediately. Understand why. Try smaller.
- Do not mix refactoring with behavior changes in the same task.
- Do not extract an abstraction until the duplication is obvious.
  Apply the flocking rules: find the most alike things, find the smallest difference,
  make the simplest change to remove that difference. Repeat.
- Do not refactor code that has no tests. Write a characterization test first.
- No speculative abstractions — only extract what two or more concrete cases demand.
```
