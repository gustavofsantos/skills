---
name: test-design
description: >
  Collaborative specification protocol to define the behavioral contract of a unit before
  any code is written. Use this skill when the user wants to think through what to test
  before implementing anything. Trigger on phrases like "let's figure out what to test",
  "before we write anything", "what should we cover for X", "help me think through the
  tests for Y", or when the user describes a feature and hasn't mentioned implementation
  yet. Also trigger when the user asks Claude to implement something non-trivial and no
  test plan exists — propose running this protocol first before jumping to tdd-design.
  The output is a behavioral contract artifact that feeds tdd-design.
---

# Test Design Protocol

## Purpose

Produce a written behavioral contract — a list of agreed test cases in simplified
Gherkin — before any test or production code is written.

This is a **conversation**, not a code generation task. No code is produced during
this protocol. The output is structured natural language that will drive tdd-design.

---

## Case format

All cases, during the conversation and in the final artifact, use this structure:

    Given <world state before the action>
    When  <the single action under test>
    Then  <observable outcome in domain terms>

Use `And` only when a Given genuinely requires a second condition. Keep Then
in domain language — no method names, no implementation vocabulary, no assertion
syntax.

---

## Your role during this protocol

- Propose cases in Given/When/Then and await confirmation
- Challenge cases that describe *how* something works internally, not *what* it does
- Ask questions when the unit's responsibility boundary is unclear
- Surface edge cases the user may not have considered
- Explicitly declare what is out of scope
- Do not suggest implementation details, class internals, or assertion code
- Do not advance past Phase 2 until the user confirms the case list is complete

---

## Phase 1: Orient

Ask the minimum necessary to understand the unit under test. Lead with one question
and let the conversation develop. Do not re-ask what the user has already told you.

Establish:
- What is the unit? (function, method, class, module)
- What is its single responsibility in one sentence?
- Does it already exist (adding behavior) or is it new (greenfield)?
- What are its direct collaborators, if any?

---

## Phase 2: Build the case list

Work through behavioral cases collaboratively. Propose cases already in
Given/When/Then form. The user confirms, reframes, or rejects each one.

### Sequencing

Go in this order:
1. Degenerate cases (empty, zero, null, missing)
2. Main happy path behaviors
3. Boundary conditions
4. Collaborator failure or unavailability
5. State-dependent variations

Propose a small group of cases at a time — not the entire list at once.

### How to propose

> "I'd start with:
>
>     Given the cart has no items
>     When  checkout is called
>     Then  an empty cart error is raised
>
> Does that belong here?"

Wait for confirmation before moving on.

### Challenges to make

Challenge a proposed case (yours or the user's) if:
- The Then describes internal behavior, not an observable outcome
- It duplicates an already-confirmed case under a different framing
- The When involves a collaborator's action, not this unit's action
- The behavior is speculative — not yet required

### Edge cases to surface proactively

- What happens with empty, null, or zero input?
- What happens when a collaborator fails or is unavailable?
- What happens when valid input arrives in an unexpected order?
- Is there a case where the same input produces different outcomes depending on state?
- What happens at the boundary of a numeric or size constraint?

### Running list

Maintain the confirmed cases as a running checklist during the conversation so the
user can see the contract taking shape.

---

## Phase 3: Close and produce the artifact

When the case list feels complete, ask:
> "Is there anything missing, or anything here you'd remove before we lock this?"

Once confirmed, produce the artifact:

---

**Unit:** `<identifier>` — <one-sentence responsibility>

**Test location:** `<file path>` > `<describe block>`

**Behavioral contract:**

    Given <context>
    When  <action>
    Then  <outcome>

    Given <context>
    When  <action>
    Then  <outcome>

**Explicitly out of scope:**
- <thing 1>
- <thing 2>

**Open questions / assumptions:**
- <anything unresolved that tdd-design should know>

---

After producing the artifact, say:
> "Contract is ready. Start tdd-design with the first case."

---

## What this protocol does not do

- Does not write test code
- Does not write production code
- Does not suggest assertion structure or mocking strategy
- Does not advance past Phase 2 until the user confirms the case list is complete
