---
description: >
  Interactive design analysis with two modes — `boundary` (module boundaries, coupling,
  bounded contexts) and `abstraction` (interfaces, protocols, traits, contracts).
when_to_use: >
  Use when discussing system structure or designing a type boundary. Mode is
  picked from the request, not by phrase-matching luck.
  • boundary — "how should A talk to B", "should this module depend on that one",
    "I'm changing X and it's breaking Y", "where does this belong", "this is too
    tangled", "como esses módulos conversam", "onde isso pertence", coupling/cohesion
    discussions, service contracts, component interactions.
  • abstraction — "design an interface", "create an abstraction", "define a contract",
    "what should this interface look like", "model this as a protocol/trait",
    "review this interface", "is this a good abstraction", any time introducing
    a new type boundary between components.
  Pick the mode that matches; if both fit, do `boundary` first then `abstraction`.
---

# Design

Read [references/design-principles.md](references/design-principles.md) for coupling/cohesion
signals, the 8 abstraction principles, the design checklist, and the anti-pattern gallery.
Read [references/idioms.md](references/idioms.md) when producing or reviewing code.

Two modes:

| Mode | Question it answers | Output |
|---|---|---|
| `boundary` | Where should this live, and how should it talk to the rest? | Boundary diagnosis + minimal contract proposal |
| `abstraction` | What should this interface look like? | Interface definition + rationale + checklist results |

---

## Mode: boundary

Two principles: high cohesion (things that change together belong together), loose coupling
(things that change for different reasons should not know each other's internals).

Before adding any dependency between two modules, ask:

1. Does A really need to know about B, or does a *result* B can provide suffice?
2. What is the minimal contract between them?
3. Who owns the contract definition?
4. If B changes internally, should A be affected?

If the answer to (4) is "no", make sure the contract prevents that coupling.

Present the diagnosis and proposed contract. Wait for the human to confirm before proceeding
to `abstraction` mode.

---

## Mode: abstraction

Two sub-modes — identify from context:
- "design", "create", "model", "define" → DESIGN
- "review", "is this good", "critique" → REVIEW
- ambiguous → ask.

**DESIGN:**
1. Establish consumer context — who is the consumer, what's the minimum behavior they need to swap, do we have two implementations in mind?
2. Draft the minimal interface — start with one method, name by behavior, place in consumer's namespace.
3. Run the design checklist from [references/design-principles.md](references/design-principles.md).
4. Output: interface definition + one-paragraph rationale + flagged trade-offs.

**REVIEW:**
1. Run the design checklist — note passes and failures.
2. Identify the dominant anti-pattern if any.
3. Output: checklist results + named anti-pattern + concrete refactoring suggestion with code.

Present output after each sub-step. Wait for the human before proceeding.
