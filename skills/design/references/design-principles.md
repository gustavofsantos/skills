# Design Principles — Reference

Read this when running boundary diagnosis or abstraction design/review.

---

## Boundary mode — signals

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

### Bounded context

A region where vocabulary is consistent, rules are internally consistent, and changes stay local.

**Identify one by asking:**
- If I change this, what else *must* change? (same context)
- Does this concept mean the same thing here as over there? (if not, separate contexts)
- Who owns this rule? (one owner per context)

**Designing the contract:**
```
Context A  →  [contract/interface]  →  Context B
             (narrow, stable, owned by one side)
```

---

## Abstraction mode — the eight principles

> An interface should emerge from the **consumer's need to swap implementations**, not from the implementor's desire to declare a contract.

1. **Define at the point of use (consumer side).** The consumer owns the interface.
2. **Keep the surface minimal.** One or two methods is the ideal. Every extra method burdens every future implementor.
3. **Name by behavior, not by role.** `Reader`, `Notifier`, `Validator` — not `UserService`, `Manager`, `Handler`.
4. **No premature abstraction.** Don't create an interface before you have two concrete implementations or a clear substitution need.
5. **Model behavior, not data.** Getters and setters in an interface are a smell.
6. **Compose, don't inherit.** Build larger contracts by composing smaller ones.
7. **Avoid `any` / `Object` / untyped escape hatches.** Use generics or discriminated unions.
8. **Concrete return types, abstract parameter types.** Accept interfaces (broad), return concrete types (specific).

---

## Abstraction mode — design checklist

Run before finalizing any interface.

| # | Check | Signal to look for |
|---|---|---|
| 1 | Consumer-side? | Defined where it's used, not where it's implemented |
| 2 | Minimal surface? | ≤ 2 methods, or composed from smaller interfaces |
| 3 | Behavioral name? | Action/capability, not a role or domain noun |
| 4 | Justified existence? | ≥ 2 implementations or test substitution explicit |
| 5 | No data leakage? | No getters/setters modeling struct shape |
| 6 | No escape hatches? | No `any`, `Object`, untyped generics without constraint |
| 7 | Concrete returns? | Functions returning this — is the abstraction intentional? |
| 8 | Composable? | Could this split into two independent interfaces with no loss? |

---

## Abstraction mode — anti-pattern gallery

**God Interface.** 5+ methods, mix of unrelated concerns.
*Fix:* split by responsibility, compose at call site.

**Premature Interface.** One implementation, no substitution need.
*Fix:* delete the interface, use the concrete type.

**Producer-Side Declaration.** Interface declared next to its only implementation.
*Fix:* move interface definition to consumer package.

**Data Interface.** Models an entity's shape, not its behavior. Smell: `getName()`, `setName()`.
*Fix:* pass a struct/record/data class directly.

**Typed Void.** Accepts or returns the top type. Smell: `process(input: any): any`.
*Fix:* type parameter with constraint, or discriminated union.

**Leaky Hierarchy.** Interface extends another that leaks implementation concerns upward.
*Fix:* flatten, compose horizontally, or use delegation.
