---
name: interface-design
description: >
  Apply Go-derived interface design principles to design or review abstractions in any language.
  Use this skill whenever the agent is about to define an interface, protocol, trait, abstract class,
  or any abstraction boundary — or when reviewing one that already exists. Triggers on phrases like
  "design an interface", "create an abstraction", "define a contract", "what should this interface
  look like", "model this as a protocol/trait", "review this interface", "is this a good abstraction",
  or any time the agent introduces a new type boundary between components. Covers Go, Clojure, Java,
  Kotlin, TypeScript, and Python.
---

# Interface Design Skill

This skill encodes the Go community's mental model for well-designed abstractions and translates it
idiomatically to each supported language. It operates in two modes:

- **DESIGN mode** — agent proposes an interface from scratch given a problem context
- **REVIEW mode** — agent critiques an existing interface definition

Identify the mode from context. If the user says "design", "create", "model", "define" → DESIGN.
If they say "review", "is this good", "critique", "what do you think of" → REVIEW.
If ambiguous, ask.

---

## The Core Mental Model

> An interface should emerge from the **consumer's need to swap implementations**, not from the
> implementor's desire to declare a contract.

This inversion is the root of everything. It implies:

- The interface lives with the **consumer**, not the producer
- It describes **behavior** (what something does), not identity (what something is)
- It is discovered **after** you have at least one real use case, not before
- Its surface area should be the **minimum** needed to satisfy that use case

---

## The Eight Principles

### 1. Define at the point of use (consumer side)
The consumer owns the interface. The implementor knows nothing about it. This inverts the
Java/OOP instinct of declaring interfaces at the producer.

### 2. Keep the surface minimal
One or two methods is the ideal. If you need more, compose smaller interfaces. Every extra
method is a burden on every future implementor.

### 3. Name by behavior, not by role
Name single-method interfaces after what they do (`Reader`, `Notifier`, `Validator`), not what
they are (`UserService`, `Manager`, `Handler`). Role names suggest god interfaces.

### 4. No premature abstraction
Don't create an interface before you have two concrete implementations or a clear substitution
need (e.g., test doubles). One implementation = no interface needed yet.

### 5. Model behavior, not data
Interfaces describe what something does. Getters and setters in an interface are a smell —
you're modeling a struct, not a behavior contract.

### 6. Compose, don't inherit
Build larger contracts by composing smaller ones. Avoid tall interface hierarchies.

### 7. Avoid `any` / `Object` / untyped escape hatches
Using the top type (`any`, `Object`, `interface{}`) kills type safety. Use generics or
discriminated unions when you need polymorphism over types.

### 8. Concrete return types, abstract parameter types
Accept interfaces (broad), return concrete types (specific). Callers of your function should
get the full API, not a restricted view.

---

## Language-Specific Idioms

Read `references/idioms.md` for detailed per-language translation of each principle with
code examples. Always consult it when producing or reviewing code — the principles are universal
but the expression is idiomatic.

Languages covered: **Go, Clojure, Java, Kotlin, TypeScript, Python**

---

## DESIGN Mode — Protocol

When asked to design an interface:

### Step 1 — Establish consumer context
Ask (or infer from context):
- Who is the consumer of this abstraction?
- What is the minimum behavior they need to swap?
- Do we have at least two concrete implementations in mind, or a test double need?

If there is only one known implementation and no test need, flag this:
> "You may not need an interface yet. Consider using the concrete type and extracting the
> interface when a second implementation or substitution need arises."

### Step 2 — Draft the minimal interface
- Start with one method. Add a second only if the consumer genuinely needs both in the same call site.
- Name by behavior.
- Place it conceptually in the consumer's package/namespace.

### Step 3 — Apply the checklist (see below)

### Step 4 — Produce output
Output format:
1. The interface definition in the target language
2. A one-paragraph rationale explaining the design decisions
3. Any flagged trade-offs or deferred decisions

---

## REVIEW Mode — Protocol

When asked to review an existing interface:

### Step 1 — Run the checklist against the definition
Go through every item. Note passes and failures.

### Step 2 — Identify the dominant smell (if any)
See the Anti-Pattern Gallery below. Name it explicitly.

### Step 3 — Produce output
Output format:
1. Checklist results (pass/warn/fail per item)
2. Named anti-pattern if one applies
3. Concrete refactoring suggestion with code

---

## Design Checklist

Run this before finalizing any interface in either mode.

| # | Check | Signal to look for |
|---|-------|--------------------|
| 1 | **Consumer-side?** | Is the interface defined where it's used, not where it's implemented? |
| 2 | **Minimal surface?** | ≤ 2 methods, or composed from smaller interfaces |
| 3 | **Behavioral name?** | Name describes an action/capability, not a role or domain noun |
| 4 | **Justified existence?** | ≥ 2 implementations exist or test substitution is explicit goal |
| 5 | **No data leakage?** | No getters/setters modeling struct shape |
| 6 | **No escape hatches?** | No `any`, `Object`, untyped generics without constraint |
| 7 | **Concrete returns?** | Functions returning this interface — is the abstraction intentional? |
| 8 | **Composable?** | Could this be split into two independent interfaces with no loss? |

---

## Anti-Pattern Gallery

### God Interface
Too many methods. Every implementor is forced to provide behavior they don't own.
> Smell: 5+ methods, mix of unrelated concerns.
> Fix: split by responsibility, compose at call site.

### Premature Interface
One implementation, no substitution need.
> Smell: `UserRepositoryInterface` with a single `PostgresUserRepository`.
> Fix: delete the interface, use the concrete type, revisit when a second impl appears.

### Producer-Side Declaration
Interface declared next to its only implementation, forcing consumers to import the producer package.
> Smell: `impl/` package exports both `Service` struct and `ServiceInterface`.
> Fix: move interface definition to consumer package.

### Data Interface
Interface models an entity's shape, not its behavior.
> Smell: `getName()`, `setName()`, `getEmail()` in an interface.
> Fix: pass a struct/record/data class directly. Interfaces are for behavior.

### Typed Void (any/Object escape)
Interface accepts or returns the top type, losing all type safety.
> Smell: `process(input: any): any`.
> Fix: introduce a type parameter with a constraint, or use a discriminated union.

### Leaky Hierarchy
Interface extends/embeds another interface that leaks implementation concerns upward.
> Smell: `AdminService extends UserService extends BaseService`.
> Fix: flatten, compose horizontally, or use delegation.

---

## Reference Files

- `references/idioms.md` — Per-language idiomatic code examples for all 8 principles
