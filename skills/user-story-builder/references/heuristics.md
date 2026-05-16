# User Story Heuristics — Reference

---

## Story quality

**Good when:**
- "So that" expresses real value, not an obvious technical consequence
- Any developer reading it knows what done looks like without asking
- Can be developed and delivered in one session or short iteration
- Acceptance criteria are testable manually or with automated tests

**Needs split when:**
- "I want" contains "and" or "or"
- More than 5 acceptance criteria
- The user hesitates to say it fits in one iteration
- There's an implicit dependency on another unwritten story

**"So that" is weak when:**
- It's a technical consequence ("so that the code is cleaner")
- It repeats "I want" in other words
- Removing it wouldn't change anything

---

## Task quality

**Good when:**
- Execution order is obvious
- Each task can be reviewed in isolation
- No task depends on a decision that hasn't been made
- Executing all tasks in order satisfies all acceptance criteria

**Rework signals:**
- A task assumes something not declared in any other task
- Two tasks touch the same files without explicit coordination
- The last task is "integrate everything" — the previous ones weren't atomic
