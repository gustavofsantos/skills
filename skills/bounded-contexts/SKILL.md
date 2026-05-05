---
description: >
  Applies bounded context and loose coupling principles when designing or reviewing module
  boundaries, service contracts, and component interactions.
when_to_use: >
  Use when deciding how two parts of the system should communicate, when adding a dependency
  between modules, when a change in one place is breaking things in another, or when discussing
  system structure. Triggers on "how should A talk to B", "should this module depend on that
  one", "I'm changing X and it's breaking Y", "where does this belong", "this is too tangled".
---

# Bounded Contexts / Loose Coupling

## Core idea

Two things:

1. **High cohesion**: things that change together belong together
2. **Loose coupling**: things that change for different reasons should not know about each other's internals

A change that should be local but forces changes elsewhere is a coupling problem.
A function that does many unrelated things is a cohesion problem.

---

## Bounded Context

A bounded context is a boundary within which a specific model applies and has meaning.
Outside that boundary, the same concept may mean something different.

**Practical definition**: a bounded context is a region of the codebase where:
- The vocabulary is consistent
- The rules are internally consistent
- Changes stay local

### How to identify a bounded context

Ask:
- If I change this, what else *must* change? (those things are in the same context)
- Does this concept mean the same thing here as it does over there? (if not, they may be separate contexts)
- Who owns this rule? (one owner per context)

---

## Designing the boundary

When two contexts need to interact, define a **contract** — not a shared internal model.

Minimal contract = least information needed to fulfill the interaction.

Bad: Context A imports and uses Context B's internal data structures  
Good: Context A calls Context B through a defined interface/function that returns only what A needs

```
Context A  →  [contract/interface]  →  Context B
             (minimal, stable)
```

The contract should be:
- **Narrow**: expose only what is needed
- **Stable**: change as rarely as possible
- **Owned**: one side owns the definition

---

## Coupling signals

Watch for these:

| Signal | Problem |
|---|---|
| Changing X requires changing Y | Structural coupling |
| A imports B's internal types | Data coupling |
| A knows about B's implementation details | Knowledge coupling |
| Two modules always change together | Boundary is in the wrong place |
| A test for A requires setting up B | Test-time coupling |

---

## Cohesion signals

Watch for these:

| Signal | Problem |
|---|---|
| Function does A, B, and C for unrelated reasons | Low cohesion |
| Module has many small unrelated functions | Wrong grouping |
| Adding a feature requires touching many files | Scattered cohesion |
| Hard to name a module without using "and" or "utils" | No clear responsibility |

---

## When to apply this skill

Before adding any dependency between two modules, ask:

1. Does A really need to know about B, or does it need a *result* that B can provide?
2. What is the minimal contract between them?
3. Who owns the contract definition?
4. If B changes internally, should A be affected?

If the answer to 4 is "no", make sure the contract prevents that coupling.

---

## Signals to watch for

Trigger this skill when:

- User is connecting two modules or services
- A change in one place is breaking something unrelated
- User asks "where does this belong" or "should X depend on Y"
- Code review reveals tangled dependencies
- User is designing a new module or service boundary
