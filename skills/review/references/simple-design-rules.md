# Kent Beck — Simple Design Rules

These four rules are applied in strict priority order. No gain from a lower rule justifies degrading a higher one.

## Rule 1 — Passes All Tests (Correctness)

Functional integrity is non-negotiable and precedes all aesthetic concerns.

**What to check:**
- Does the proposed refactoring preserve the original behavior under all known paths?
- Are error cases and boundary conditions still handled?
- Does the change risk altering return values or side effects?

**Directive:** Reject any refactoring that mutates semantics, even if the result is structurally cleaner. A well-organized bug is still a bug.

---

## Rule 2 — Reveals Intention (Clarity)

Code is communication. It is a letter to the next developer — often yourself in six months.

**What to check:**
- Do names of variables, methods, and classes describe *what* they represent in domain terms, not *how* they work mechanically?
- Can a reader understand the purpose of a block without reading its internals?
- Are abstractions named after concepts, not after implementation details?

**Directive:** Fix naming and structural clarity before addressing duplication or minimalism. A confusing but DRY codebase is worse than a slightly repetitive but legible one.

---

## Rule 3 — No Duplication (DRY)

Duplicated logic means a single domain concept lives in multiple places. When one changes, the others rot silently.

**What to check:**
- Is the same decision, calculation, or transformation expressed more than once?
- Do multiple callers reconstruct the same derived value independently?

**Directive:** Extract and centralize duplicated concepts — but only when doing so does not damage Rule 2. If unification requires a complex abstraction that obscures intent, tolerate the repetition. Accidental structural similarity is not the same as conceptual duplication.

---

## Rule 4 — Fewest Elements (Minimalism)

Once the first three rules are satisfied, eliminate everything that doesn't earn its place.

**What to check:**
- Are there classes or modules with insufficient responsibility that don't justify their existence? (Lazy Class)
- Are there abstractions written for hypothetical future scenarios that haven't materialized? (Speculative Generality)
- Are there interfaces with a single implementation, created "just in case"?

**Directive:** Delete or inline elements that add no present value. Design for what is known now. The cost of premature abstraction is paid continuously, in cognitive overhead, every time the code is read.

---

## Conflict Resolution — Rule 0

When rules conflict in edge cases: **empathy with future readers wins over any strict metric.** The goal is a codebase that a competent developer can understand and modify with confidence.
