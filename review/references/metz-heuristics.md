# Sandi Metz — Structural Heuristics & Flocking Rules

## Structural Limits

These are not laws — they are signals. When a limit is exceeded, ask *why* before prescribing a fix.

| Rule | Limit | What chronic violation signals |
|---|---|---|
| Lines per class | ≤ 100 | God Class — knows too much, does too much |
| Lines per method | ≤ 5 | Missing named concept — the block deserves a name |
| Parameters per method | ≤ 4 | Data Clump — a hidden object waiting to be born |
| Objects instantiated per controller action | 1 | Layer coupling — orchestration layer reaching into domain |

**Tolerated exceptions:**
- Algorithms that are mathematically irreducible
- Framework-mandated signatures (e.g., Rails view helpers)
- Cases where fragmentation would harm cohesion of reading

**Hard prohibition:** Never mask high parameter count by passing generic hashes/dicts/maps. This hides the true interface and breaks static analysis. The fix is a typed object, not a bag of options.

---

## Flocking Rules (Horizontal Refactoring)

Use this algorithm when facing complex conditionals, duplicated branches, or unclear abstractions. It produces safe, incremental steps toward polymorphism without leaping to patterns prematurely.

**The three steps:**
1. Find the things that are most alike in the problem area.
2. Find the smallest difference between them.
3. Make the simplest change that eliminates that difference (parameterize it, extract it).

Repeat until the pattern becomes visible on its own.

**Key insight:** You are replacing difference with sameness, step by step. The destination (Strategy, Null Object, etc.) is discovered — not imposed.

---

## From Conditionals to Polymorphism

When a method contains a conditional that dispatches behavior based on a type or category:

1. Identify all branches.
2. Apply Flocking Rules to find the common shape.
3. Extract each branch into a separate object that responds to the same message.
4. Replace the conditional with polymorphic dispatch.

This transition satisfies Liskov Substitution: each new object is substitutable for the others, and new variants can be added without modifying existing code (Open-Closed).
