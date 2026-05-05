# DHH — Expressiveness & Conceptual Compression

## Programmer Happiness

The goal is code that induces flow, not friction. Every unnecessary decision imposed on the reader is a tax on productivity and morale.

**What to check:**
- Does the code fight its framework or language idioms?
- Are there manual implementations of things the ecosystem provides declaratively?
- Does reading the code feel like reading prose or deciphering a machine?

---

## Convention over Configuration

Idiomatic code leverages the established conventions of its ecosystem. Code that reinvents routing, persistence, validation, or serialization by hand is paying a continuous maintenance tax with no corresponding benefit.

**Directive:** Penalize re-implementations of framework capabilities. Reward code that embraces the abstraction layer it lives in.

---

## Conceptual Compression

Good abstractions compress complexity. A developer should be able to use a well-designed abstraction as a black box, trusting it, without reading its internals.

**What to check:**
- Does this abstraction reduce the cognitive surface the caller must manage?
- Or does it merely shuffle complexity around, forcing the caller to understand implementation details to use it correctly?

**Directive:** An abstraction that expands the caller's required knowledge is not an abstraction — it is a leaky indirection. Delete it or redesign it.

---

## Comments as Design Smells

An inline comment explaining *what* the code does is evidence that the code failed to explain itself.

**Diagnostic:** If a block requires a comment, ask:
- Can this be extracted into a method whose name is the comment?
- If yes — do it. Delete the comment.

**Tolerated comments:**
- *Why* a non-obvious decision was made (architectural rationale, not mechanics)
- References to external constraints (legal, spec, third-party quirk)
- Public API documentation (docstrings)

**Prohibited comments:**
- Restating what the code does in plain English
- Marking sections with headers inside a method (signals the method needs splitting)
- "TODO: fix this later" without a ticket reference
