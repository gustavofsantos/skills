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

Two modes. Each emits a constraint block to paste into the issue's
`## Context` section. The agent reads the block during planning and execution.

This skill does not run as an interactive protocol — Claude Code plans and
executes in single runs. The constraints are framework-style guardrails, not
a conversation.

| Mode | When | Block name |
|---|---|---|
| `evolutionary` | New feature, module, or integration. Path through layers is unproven. | `## Design constraints — evolutionary design` |
| `refactor` | Code is being restructured without changing behavior. Tests are the safety net. | `## Design constraints — incremental refactoring` |

---

## Mode: evolutionary

Build the thinnest vertical slice that integrates all major layers and
delivers one piece of real behavior. Then grow it. Never design the full
system upfront.

A tracer bullet is not a prototype. It is production code, deliberately
incomplete, that proves the path works end-to-end.

### Constraint block

Copy this into the issue's `## Context`:

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

### What "vertical slice" means

A slice touches every major layer of the feature: UI (or API) → domain logic
→ persistence (or external call).

It does not mean:
- Building the data layer first, then the logic, then the UI
- Writing all the models before any behavior exists
- Scaffolding infrastructure "to support future work"

The first slice is deliberately incomplete. Its only job is to prove the path.

### Signals the constraint is being violated

- The agent proposes building a module with no behavior yet
- Abstractions appear before two concrete cases exist
- The plan has more than one layer being built before any layer is exercised
- "We'll need this later" appears as justification for any code

When you see these, redirect: thinnest slice first.

### Interactive use (pairing, not Claude Code)

If working interactively rather than delegating to Claude Code:

1. Identify the slice: smallest interaction that touches all layers?
2. Build just that. Skip everything else.
3. Verify it runs end-to-end before expanding.
4. Add the next slice only after the first works.

Output:
1. **Slice definition** — one sentence describing the primitive whole
2. **Layer map** — which layers the slice touches
3. **First task** — first concrete file/function to write
4. **Expand plan** — next 2–3 slices in order

---

## Mode: refactor

Refactoring is changing structure without changing behavior. The safety net
is the test suite. If tests aren't green before you start, fix that first.

### Constraint block

Copy this into the issue's `## Context`:

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

### The flocking rules

When facing duplication or unclear abstractions:

1. Find the things that are most alike.
2. Find the smallest difference between them.
3. Make the simplest change to eliminate that difference.

Repeat until the pattern is obvious enough to name and extract cleanly.
The right abstraction is discovered, not designed.

### Common safe moves (each is one step)

| Move | Safe when |
|---|---|
| Rename variable/function | Tests still pass |
| Extract variable | Behavior identical, name is more expressive |
| Extract function | New function does exactly what the old code did |
| Inline function | Called once or name adds no clarity |
| Move function | Cohesion improves, no circular dependencies introduced |
| Replace magic value with named constant | All uses updated |

### When there are no tests

1. Write a characterization test — captures current behavior, whatever it is.
2. Use it as the safety net.
3. Then refactor.

Never refactor untested code without a safety net.

### Signals the constraint is being violated

- Multiple structural changes in a single task
- Behavior change mixed with a structural change
- Abstraction extracted before two concrete cases exist
- Tests skipped "because the refactor is obviously safe"

When you see these, stop. Make the change smaller.

### Interactive use (pairing, not Claude Code)

One change, run tests, repeat. The cycle is the discipline. Never accumulate
untested changes. If uncertain whether a change is safe, make it smaller.
