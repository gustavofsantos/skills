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
  Pick the mode that matches; if both fit (designing both system structure
  AND the abstraction surface for it), do `boundary` first then `abstraction`.
---

# Design

Two modes. Pick the one that fits the request, or run them in sequence
when both apply.

| Mode | Question it answers | Output |
|---|---|---|
| `boundary` | Where should this thing live, and how should it talk to the rest? | A boundary diagnosis + minimal contract proposal |
| `abstraction` | What should this interface/protocol/trait look like? | An interface definition + rationale + checklist results |

---

## Mode: boundary

Two principles:

1. **High cohesion**: things that change together belong together.
2. **Loose coupling**: things that change for different reasons should not
   know about each other's internals.

A change that should be local but forces changes elsewhere is a coupling
problem. A function that does many unrelated things is a cohesion problem.

### Bounded context

A bounded context is a region of the codebase where:
- The vocabulary is consistent
- The rules are internally consistent
- Changes stay local

Outside that boundary, the same concept may mean something different.

**Identify a bounded context** by asking:
- If I change this, what else *must* change? (those things are in the same context)
- Does this concept mean the same thing here as it does over there?
  (if not, they may be separate contexts)
- Who owns this rule? (one owner per context)

### Designing the boundary

When two contexts need to interact, define a **contract** — not a shared
internal model.

Minimal contract = least information needed to fulfill the interaction.

```
Context A  →  [contract/interface]  →  Context B
             (minimal, stable, owned)
```

The contract should be:
- **Narrow** — expose only what is needed
- **Stable** — change as rarely as possible
- **Owned** — one side owns the definition

### Coupling signals

| Signal | Problem |
|---|---|
| Changing X requires changing Y | Structural coupling |
| A imports B's internal types | Data coupling |
| A knows about B's implementation details | Knowledge coupling |
| Two modules always change together | Boundary is in the wrong place |
| A test for A requires setting up B | Test-time coupling |

### Cohesion signals

| Signal | Problem |
|---|---|
| Function does A, B, and C for unrelated reasons | Low cohesion |
| Module has many small unrelated functions | Wrong grouping |
| Adding a feature requires touching many files | Scattered cohesion |
| Hard to name a module without "and" or "utils" | No clear responsibility |

### Diagnosis output

Before adding any dependency between two modules, ask:

1. Does A really need to know about B, or does it need a *result* B can provide?
2. What is the minimal contract between them?
3. Who owns the contract definition?
4. If B changes internally, should A be affected?

If the answer to (4) is "no", make sure the contract prevents that coupling.

If `boundary` reveals that a contract needs a precise abstraction, switch
to the `abstraction` mode below to design it.

---

## Mode: abstraction

Encodes the Go community's mental model for well-designed abstractions and
translates it idiomatically across languages.

Operates in DESIGN (propose an interface from scratch) or REVIEW (critique
an existing interface). Identify the sub-mode from context:
- "design", "create", "model", "define" → DESIGN
- "review", "is this good", "critique", "what do you think of" → REVIEW
- ambiguous → ask.

### The core mental model

> An interface should emerge from the **consumer's need to swap
> implementations**, not from the implementor's desire to declare a contract.

This inversion is the root of everything. It implies:

- The interface lives with the **consumer**, not the producer
- It describes **behavior** (what something does), not identity (what something is)
- It is discovered **after** you have at least one real use case, not before
- Its surface area should be the **minimum** needed to satisfy that use case

### The eight principles

1. **Define at the point of use (consumer side).** The consumer owns the
   interface. The implementor knows nothing about it. This inverts the
   Java/OOP instinct of declaring interfaces at the producer.

2. **Keep the surface minimal.** One or two methods is the ideal. If you
   need more, compose smaller interfaces. Every extra method is a burden
   on every future implementor.

3. **Name by behavior, not by role.** Name single-method interfaces after
   what they do (`Reader`, `Notifier`, `Validator`), not what they are
   (`UserService`, `Manager`, `Handler`). Role names suggest god interfaces.

4. **No premature abstraction.** Don't create an interface before you have
   two concrete implementations or a clear substitution need (e.g., test
   doubles). One implementation = no interface needed yet.

5. **Model behavior, not data.** Interfaces describe what something does.
   Getters and setters in an interface are a smell — you're modeling a
   struct, not a behavior contract.

6. **Compose, don't inherit.** Build larger contracts by composing smaller
   ones. Avoid tall interface hierarchies.

7. **Avoid `any` / `Object` / untyped escape hatches.** Using the top type
   kills type safety. Use generics or discriminated unions when you need
   polymorphism over types.

8. **Concrete return types, abstract parameter types.** Accept interfaces
   (broad), return concrete types (specific). Callers should get the full
   API, not a restricted view.

### Language-specific idioms

Read [references/idioms.md](references/idioms.md) for detailed per-language
translation of each principle with code examples. Always consult it when
producing or reviewing code — the principles are universal but the expression
is idiomatic.

Languages covered: **Go, Clojure, Java, Kotlin, TypeScript, Python**.

### DESIGN sub-mode

1. **Establish consumer context.** Ask (or infer):
   - Who is the consumer of this abstraction?
   - What is the minimum behavior they need to swap?
   - Do we have at least two concrete implementations in mind, or a test
     double need?

   If only one implementation exists and there's no test need, flag it:
   > "You may not need an interface yet. Consider using the concrete type
   > and extracting the interface when a second implementation or
   > substitution need arises."

2. **Draft the minimal interface.**
   - Start with one method. Add a second only if the consumer genuinely
     needs both at the same call site.
   - Name by behavior.
   - Place it conceptually in the consumer's package/namespace.

3. **Run the design checklist** (below).

4. **Produce output:**
   1. The interface definition in the target language
   2. A one-paragraph rationale explaining the design decisions
   3. Any flagged trade-offs or deferred decisions

### REVIEW sub-mode

1. **Run the design checklist** against the definition. Note passes and failures.
2. **Identify the dominant smell** if any (Anti-Pattern Gallery below).
3. **Produce output:**
   1. Checklist results (pass/warn/fail per item)
   2. Named anti-pattern if one applies
   3. Concrete refactoring suggestion with code

### Design checklist

Run before finalizing any interface in either sub-mode.

| # | Check | Signal to look for |
|---|-------|--------------------|
| 1 | Consumer-side? | Defined where it's used, not where it's implemented |
| 2 | Minimal surface? | ≤ 2 methods, or composed from smaller interfaces |
| 3 | Behavioral name? | Action/capability, not a role or domain noun |
| 4 | Justified existence? | ≥ 2 implementations or test substitution explicit |
| 5 | No data leakage? | No getters/setters modeling struct shape |
| 6 | No escape hatches? | No `any`, `Object`, untyped generics without constraint |
| 7 | Concrete returns? | Functions returning this — is the abstraction intentional? |
| 8 | Composable? | Could this split into two independent interfaces with no loss? |

### Anti-pattern gallery

**God Interface.** 5+ methods, mix of unrelated concerns. Every implementor
forced to provide behavior they don't own.
*Fix:* split by responsibility, compose at call site.

**Premature Interface.** One implementation, no substitution need.
Smell: `UserRepositoryInterface` with a single `PostgresUserRepository`.
*Fix:* delete the interface, use the concrete type, revisit when a second
impl appears.

**Producer-Side Declaration.** Interface declared next to its only
implementation, forcing consumers to import the producer package.
Smell: `impl/` package exports both `Service` struct and `ServiceInterface`.
*Fix:* move interface definition to consumer package.

**Data Interface.** Interface models an entity's shape, not its behavior.
Smell: `getName()`, `setName()`, `getEmail()` in an interface.
*Fix:* pass a struct/record/data class directly.

**Typed Void.** Interface accepts or returns the top type, losing all type
safety. Smell: `process(input: any): any`.
*Fix:* introduce a type parameter with a constraint, or use a discriminated
union.

**Leaky Hierarchy.** Interface extends/embeds another that leaks
implementation concerns upward. Smell: `AdminService extends UserService
extends BaseService`.
*Fix:* flatten, compose horizontally, or use delegation.
