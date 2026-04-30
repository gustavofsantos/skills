---
name: shameless-green
description: >
  Apply Shameless Green — write the simplest, most obvious code that makes tests pass,
  without worrying about elegance, abstraction, or duplication. Use this skill during the
  GREEN phase of TDD, when the user is trying to make a failing test pass, when writing
  the first implementation of anything, or when the user is overthinking the design before
  having working code. Trigger when the user says "how should I implement this cleanly",
  "what's the best abstraction here", or starts designing structure before having a passing
  test. Redirect them: make it work first, make it clean after.
---

# Shameless Green

## Core idea

Make the test pass. That's it.

Don't worry about:
- Elegant structure
- Avoiding duplication
- Future extensibility
- The "right" abstraction

Those concerns belong in the **refactor** step. Not here.

Shameless Green is the GREEN phase of TDD. Its only job is to turn the red test green
as quickly and clearly as possible.

---

## Rules

### 1. Prioritize clarity over cleverness

The Shameless Green solution should be immediately understandable by anyone.
If you have to explain it, it's too clever.

Prefer:
```
if condition
  return "this"
else
  return "that"
```

Over:
```
return lookup_table[condition] || compute_fallback(condition)
```

...if both make the test pass.

### 2. Duplication is allowed — even encouraged

Do not extract duplication prematurely. Two identical blocks of code are fine.
Three might be a signal. Extraction happens during refactor, when the pattern is clear.

> It is much cheaper to manage temporary duplication than to recover from
> a wrong abstraction.

### 3. Hardcoding is valid

If the test passes with a hardcoded value, that is a valid Shameless Green.
The next test will force you to generalize.

```clojure
(defn discount [amount] 0)  ; makes the first test pass
```

The second test will break this and force real logic. That's the point.

### 4. No speculative behavior

Do not implement anything that isn't required by a currently failing test.
If there's no test for it, don't build it.

---

## The sequence

```
Write test → [RED] → Write Shameless Green → [GREEN] → Refactor → [GREEN]
```

Shameless Green is always followed by refactoring. It is not the final state —
it is the **safe state from which you refactor**.

---

## When perfectionism is a problem

If you find yourself saying:
- "But this won't scale..."
- "This will need to change when..."
- "The clean version would be..."

...stop. Make the test pass first. Then refactor. You can only refactor safely from green.

Premature design is speculation. Shameless Green is fact.

---

## Signals to watch for

Trigger this skill when:

- User has a failing test and is asking how to implement it "properly"
- User is designing structure before having any passing tests
- User is resisting a simple solution because "it won't work long term"
- User asks "what's the best way to implement X" before X has a test
- The GREEN phase of TDD is stalling due to over-engineering
