# FP Evaluation Criteria

## Pure Functions

A function is pure if:
1. Same inputs always produce the same output (referential transparency)
2. No observable side effects (no I/O, no mutation of external state, no global reads)

**What to check:**
- Does the function read from global/external state?
- Does it mutate any structure passed to it?
- Does it produce effects (logging, I/O) without those being explicit in its signature?

**Directive:** Isolate all effects at the boundary. Pure core, impure shell.

---

## Immutability

**What to check:**
- Are data structures mutated in-place after creation?
- Are shared mutable references passed between functions?
- Are there reassignment patterns (`x = ...; x = x + ...`) that could be expressed as transforms?

**Directive:** Treat mutation as a last resort for performance-critical paths, not a default. Return new structures. Use persistent data structures where the language supports them.

---

## Declarative Pipelines over Imperative Loops

**Smells like this:**
```
result = []
for item in items:
    if item.active:
        result.append(transform(item))
```

**Target direction:**
```
result = [transform(item) for item in items if item.active]
# or
result = list(map(transform, filter(lambda i: i.active, items)))
```

**Principle:** Prefer `map`, `filter`, `reduce`, and their equivalents. Each operation names what it does. Manual loops name nothing — they only describe the mechanics.

---

## Higher-Order Functions & Composition

**What to check:**
- Are behaviors hardcoded inside loops instead of passed as parameters?
- Could repeated structural patterns be expressed as a single HOF?
- Are there opportunities for `partial` application or currying to reduce repetition?

**Target:** Parameterize behavior, not just data.

---

## Handling Absence and Errors

**Avoid:**
- Returning `null`/`None` as a signal value
- Using exceptions for control flow
- Nested `if x is not None` chains

**Prefer:**
- `Optional[T]` / `Maybe` for nullable results
- `Result[T, E]` / `Either` for operations that can fail
- Pattern matching to exhaustively handle all cases

---

## Lazy Evaluation

When processing potentially large or infinite sequences:
- Prefer generators/lazy sequences over materializing full collections
- Chain transformations without intermediate allocation
- Signal when eagerness is required (e.g., `list(...)` wrapping a generator)

---

## Pattern Matching

When dispatching on structure or type:
- Prefer exhaustive pattern matching over chains of `if/elif`
- Ensure all cases are handled — treat unmatched cases as a compile-time concern, not a runtime surprise
- Name the matched shapes, not the conditions
