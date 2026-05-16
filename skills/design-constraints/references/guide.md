# Design Constraints — Reference Guide

---

## Evolutionary: what "vertical slice" means

A slice touches every major layer of the feature: UI (or API) → domain logic → persistence (or external call).

It does not mean:
- Building the data layer first, then the logic, then the UI
- Writing all the models before any behavior exists
- Scaffolding infrastructure "to support future work"

The first slice is deliberately incomplete. Its only job is to prove the path.

## Evolutionary: violation signals

- Agent proposes building a module with no behavior yet
- Abstractions appear before two concrete cases exist
- Plan has more than one layer being built before any layer is exercised
- "We'll need this later" appears as justification for any code

When you see these, redirect: thinnest slice first.

---

## Refactor: the flocking rules

When facing duplication or unclear abstractions:

1. Find the things that are most alike.
2. Find the smallest difference between them.
3. Make the simplest change to eliminate that difference.

Repeat until the pattern is obvious enough to name and extract cleanly. The right abstraction is discovered, not designed.

## Refactor: common safe moves

| Move | Safe when |
|---|---|
| Rename variable/function | Tests still pass |
| Extract variable | Behavior identical, name is more expressive |
| Extract function | New function does exactly what the old code did |
| Inline function | Called once or name adds no clarity |
| Move function | Cohesion improves, no circular dependencies introduced |
| Replace magic value with named constant | All uses updated |

## Refactor: violation signals

- Multiple structural changes in a single task
- Behavior change mixed with a structural change
- Abstraction extracted before two concrete cases exist
- Tests skipped "because the refactor is obviously safe"

When you see these, stop. Make the change smaller.

## Refactor: no tests

1. Write a characterization test — captures current behavior, whatever it is.
2. Use it as the safety net.
3. Then refactor.

Never refactor untested code without a safety net.
