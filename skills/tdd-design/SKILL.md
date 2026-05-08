---
description: >
  Drives the full TDD workflow: first runs a collaborative behavioral-contract
  conversation to specify what to test, then immediately executes the
  red-green-refactor cycle using that contract.
when_to_use: >
  Use when starting any implementation task, when the user wants to think
  through what to test before writing code, or when about to write new
  production code. Triggers on "let's figure out what to test", "before we
  write anything", "what should we cover for X", "implement X", "add behavior Y",
  "write the function that...", "make this work", "vamos implementar", "implementar X",
  or when the user jumps straight to implementation without a test plan. Also when
  an issue has an implementation task with no behavioral contract yet. Do not use
  for pure refactoring with no behavior change — use design-constraints instead.
allowed-tools: Read Edit Bash(rg:*) Bash(fd:*)
---

# TDD Design

Two phases in sequence. The spec phase produces the contract; the TDD phase
consumes it. No handoff — it all happens in one skill invocation.

---

## Locate the issue

```bash
ISSUE_FILES=$(fd -t f -e md . ~/engineering/issues 2>/dev/null | grep -v '/archive/' | sort)
ISSUE_COUNT=$(echo "$ISSUE_FILES" | grep -c '.' 2>/dev/null || echo 0)
```

- **One file:** use it. Read it now.
- **Multiple files:** list them and ask which issue this work belongs to.
- **Zero files:** ask the user which issue to use, or create one first via `workflow`.

---

## Phase 1 — Behavioral contract

**Purpose:** produce a written list of test cases in simplified Gherkin before
any test or production code is written. The contract lives in the active
issue's `## Behavioral contract` section.

This is a conversation, not a code-generation task. No code is produced here.

### Check for an existing contract

Read the issue. If `## Behavioral contract` already exists and has cases, skip
Phase 1 entirely and proceed directly to Phase 2 with the existing contract.

### Orient

Ask the minimum needed to understand the unit under test. One question at a
time. Do not re-ask what is already in the issue's Objective or Context.

Establish:
- What is the unit? (function, method, class, module)
- Its single responsibility in one sentence
- Whether it already exists (adding behavior) or is new (greenfield)
- Direct collaborators, if any

### Build the case list

Work through behavioral cases collaboratively. Propose cases in Given/When/Then
form. The user confirms, reframes, or rejects each one.

**Sequencing:**
1. Degenerate cases (empty, zero, null, missing)
2. Main happy path
3. Boundary conditions
4. Collaborator failure
5. State-dependent variations

**Propose one group at a time:**
> "I'd start with:
>
>     Given the cart has no items
>     When  checkout is called
>     Then  an empty cart error is raised
>
> Does that belong here?"

Wait for confirmation before moving on. On confirmation, assign the next
stable ID: `C1`, `C2`, `C3`, …

**Case format:**

    Given <world state before the action>
    When  <the single action under test>
    Then  <observable outcome in domain terms>

Use `And` only when a Given genuinely requires a second condition. Keep Then
in domain language — no method names, no assertion syntax.

**Challenge a case if:**
- The Then describes internal behavior, not an observable outcome
- It duplicates a confirmed case under a different framing
- The When involves a collaborator's action, not this unit's action
- The behavior is speculative — not yet required

### Close and write into the issue

When the list feels complete, ask:
> "Anything missing, or anything you'd remove before we lock this?"

Once confirmed:

1. Edit the active issue file, inserting or replacing `## Behavioral contract`
   between `## Open questions` and `## Tasks`:

   ```markdown
   ## Behavioral contract

   **Unit:** `<identifier>` — <one-sentence responsibility>
   **Test location:** `<file path>` > `<describe block>`

   - C1. Given <context>, When <action>, Then <outcome>
   - C2. ...
   ```

   For multi-unit issues, use subsections: `### Unit: cart`, `### Unit: pricing`.

2. Fold "out of scope" items into the issue's `## Scope` → **Off-limits:** field.

3. Fold "open questions / assumptions" into `## Open questions`.

4. Update `updated:` in the issue frontmatter.

Say:
> "Contract written (cases C1–CN). Starting TDD with C1 now."

Then immediately begin Phase 2.

---

## Phase 2 — TDD cycle

**Core idea:** write the test first. Not as a formality — as a design act.
Test friction is not an inconvenience; it is information.

```
RED → GREEN → REFACTOR
```

### Starting from the contract

Take the next unimplemented case from `## Behavioral contract`:

    Given <context>
    When  <action>
    Then  <outcome>

Translate directly into a failing test. Given → setup, When → action under
test, Then → assertion. Do not interpret beyond what the case says.

When a case is implemented and green, mark its task `[x]` in the issue's
`## Tasks` section. If no corresponding task exists, append one referencing
the implemented case.

If no contract exists (ad-hoc work), list behaviors before starting and
apply the sequencing from Phase 1.

### RED — write a failing test

- Write **one** test at a time
- The test must fail for the right reason (not compile errors, not setup failures)
- Do not write more than one failing test at a time

### GREEN — make it pass, nothing more

- Write the minimum code to pass the test
- Do not add behavior that isn't tested
- Hardcoding the return value is valid if it makes the test pass
- Do not clean up yet — refactor step comes next

### REFACTOR — improve structure, keep tests green

- Run tests after every change
- If a test breaks, undo the last change
- Do not add behavior during refactor

---

## What to test (message taxonomy)

| Message type | Direction | Assert |
|---|---|---|
| Incoming (public interface) | Received by subject | State returned |
| Outgoing command (side effects) | Sent by subject | That it was sent (mock/spy) |
| Outgoing query (no side effects) | Sent by subject | Nothing |

**Never test private methods.** A bug in a private method surfaces through a
failing public interface test. Testing privates couples tests to implementation.

**Tests are concretions.** No conditionals or loops in test code to reduce
duplication. Write it down twice before abstracting.

---

## TDD as design signal

| Symptom | Design problem |
|---|---|
| Hard to instantiate the subject | Too many dependencies |
| Test needs internal state | Missing abstraction or public interface |
| Many mocks needed | High coupling |
| Setup longer than assertion | Wrong responsibility boundary |
| Can't test without side effects | Logic mixed with I/O |

When you hit friction, stop and redesign before continuing.

---

## Test data signals intent

- Prime numbers (47, 43, 97) → arbitrary value
- Ridiculously large values → scale-independence
- Named constants → domain meaning that must not change
