---
description: >
  Drives implementation using Test-Driven Development as a design tool, enforcing the
  red-green-refactor cycle and using test friction as a design signal.
when_to_use: >
  Use whenever the user is about to write new production code, implement a function, add a
  behavior, or fix a bug with a reproducible case. Triggers on "implement X", "add behavior Y",
  "write the function that...", "make this work", or when the user jumps straight to
  implementation code. Also trigger if the user writes code without a failing test first.
  When a behavioral contract from test-design is present, consume it — do not re-derive.
allowed-tools: Read Edit Bash(rg:*) Bash(fd:*)
---

# TDD as Design Tool

## Core idea

Write the test first. Not as a formality — as a **design act**.

If a test is hard to write, the design is wrong. Test friction is not an inconvenience;
it is information. Use it.

---

## Starting from a behavioral contract

If a contract from test-design is present, it is the source of truth for what to test.
Do not re-derive cases, do not add cases, do not skip cases.

At the start of each RED phase, take the next unimplemented case from the contract:

    Given <context>
    When  <action>
    Then  <outcome>

Translate it directly into a failing test. The Given maps to setup. The When maps to
the action under test. The Then maps to the assertion. Do not interpret beyond what
the case says.

When a case is implemented and green, move to the next one in contract order.

If no contract is present, apply the sequencing rules in the RED section below.

---

## The cycle

```
RED → GREEN → REFACTOR
```

Each step has a strict contract:

### RED: Write a failing test

**With a behavioral contract:** take the next case. Encode it. Confirm it fails for
the right reason before proceeding.

**Without a behavioral contract:** decide what to test next by asking:
*What is the simplest behavior I need to add next?*

In both cases:
- Write **one** test at a time
- The test must fail for the right reason (not compile errors, not setup failures)
- Do not write more than one failing test at a time

### GREEN: Make it pass — nothing more

- Write the minimum code to pass the test
- Do not add behavior that isn't tested
- Do not clean up yet — that comes in refactor
- Hardcoding the return value is valid if it makes the test pass

### REFACTOR: Improve structure, keep tests green

- Run tests after every change
- If a test breaks, undo the last change
- Do not add behavior during refactor

---

## What to test (message taxonomy)

Every test falls into one of three categories. Apply the right assertion type:

| Message type | Direction | Assert |
|---|---|---|
| Incoming (public interface) | Received by subject | State returned |
| Outgoing command (has side effects) | Sent by subject | That it was sent (mock/spy) |
| Outgoing query (no side effects) | Sent by subject | Nothing — don't test it |

**Incoming messages:** assert the return value. This is the only place that value
should be tested.

**Outgoing commands** (writes to DB, triggers events, calls observers): use a
mock/spy to verify the message was sent with the right arguments. Do not assert
on the internal state of the collaborator.

**Outgoing queries:** the receiver already tests those. Testing them from the sender
duplicates assertions and creates coupling.

**Never test private methods.** A bug in a private method will always surface
through a failing public interface test. Testing privates couples tests to
implementation and misleads readers.

---

## Point of view: sight along the edges

Tests behave as external consumers of the object under test — they know only what
messages come in and go out. They do not reach inside.

If you need to inspect internal state to verify behavior, that is a missing public
interface or a missing abstraction.

---

## TDD as design signal

| Symptom during TDD | Design problem |
|---|---|
| Hard to instantiate the subject | Too many dependencies |
| Test needs to know internal state | Missing abstraction or missing public interface |
| Need to mock many things | High coupling |
| Test setup is longer than the assertion | Wrong responsibility boundary |
| Can't test without side effects | Logic mixed with I/O |
| Test duplicates the implementation logic | Testing the wrong level of abstraction |
| Test double goes stale (passes but app is broken) | Double not validated against real interface |

When you hit friction, **stop and redesign** before continuing.

---

## Test doubles: use with discipline

When you create a double for a role, also verify that every real implementer of that
role responds to the same interface. A double that stubs a method that no longer
exists will silently pass while the application is broken.

---

## DRY is wrong in tests

Tests are concretions, not abstractions. Do not add conditionals or loops to test
code to reduce duplication. If you mirror production logic in tests, the tests become
coupled to implementation and break on every refactor.

Write it down twice. Duplication in tests is cheaper than the wrong abstraction.

---

## Test data signals intent

- Use prime numbers (47, 43, 97) to signal that the specific value is arbitrary
- Use ridiculously large values to signal scale-independence
- Use named constants when the value has domain meaning and must not change

---

## Sequencing behaviors (no contract)

When no behavioral contract exists, list behaviors before starting and go in this
order:

1. Degenerate case (empty input, zero, null, single item)
2. Main happy path
3. Boundary conditions
4. Collaborator failure
5. State-dependent variations

---

## What to avoid

- Writing tests after the code
- Writing multiple failing tests at once
- Skipping the refactor step
- Testing private methods
- Adding logic to test code to DRY it up
- Using mocks without validating them against real interfaces
- Testing outgoing query messages
- Deviating from the behavioral contract order without flagging it to the user
