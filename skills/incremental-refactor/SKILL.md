---
description: >
  Produces constraints for safe, incremental refactoring — behavior-preserving steps, one
  transformation at a time, no scope expansion.
when_to_use: >
  Use when cleaning up code, removing duplication, extracting a concept, or improving structure
  without changing behavior. Triggers on "refactor this", "clean this up", "there's duplication
  here", "this feels wrong", "extract this", or when code has structural problems identified
  during review.
---

# Incremental Refactoring

## Core idea

Refactoring is changing structure without changing behavior.
The safety net is the test suite. If tests aren't green before you start, fix that first.

---

## How to use this skill in Claude Code

In Claude Code sessions, paste the constraint block below into the card's `## Context`
before starting the session. Claude Code applies it during planning — not as an
interactive loop.

---

## Constraint block

Copy this into the card's `## Context`:

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

---

## The flocking rules

When facing duplication or unclear abstractions:

1. Find the things that are most alike.
2. Find the smallest difference between them.
3. Make the simplest change to eliminate that difference.

Repeat until the pattern is obvious enough to name and extract cleanly.
The right abstraction is discovered, not designed.

---

## Common safe moves (each is one step)

| Move | Safe when |
|---|---|
| Rename variable/function | Tests still pass |
| Extract variable | Behavior identical, name is more expressive |
| Extract function | New function does exactly what the old code did |
| Inline function | Called once or name adds no clarity |
| Move function | Cohesion improves, no circular dependencies introduced |
| Replace magic value with named constant | All uses updated |

---

## When there are no tests

1. Write a characterization test — captures current behavior, whatever it is.
2. Use it as the safety net.
3. Then refactor.

Never refactor untested code without a safety net.

---

## Signals the constraint is being violated

- Multiple structural changes in a single task
- Behavior change mixed with a structural change
- Abstraction extracted before two concrete cases exist
- Tests skipped "because the refactor is obviously safe"

When you see these, stop. Make the change smaller.

---

## Interactive use (pairing sessions, not Claude Code)

If working interactively: one change, run tests, repeat. The cycle is the discipline.
Never accumulate untested changes. If uncertain whether a change is safe, make it smaller.
