---
description: >
  Collaborative specification protocol to define the behavioral contract of a unit before
  any code is written. Writes the contract directly into the active issue file.
when_to_use: >
  Use when the user wants to think through what to test before implementing. Triggers on
  "let's figure out what to test", "before we write anything", "what should we cover for X",
  "help me think through the tests for Y", or when a feature is described with no test plan.
  Also trigger when asked to implement something non-trivial with no test plan — propose this
  protocol first. The output is a behavioural contract section appended to the active issue
  file, which feeds tdd-design.
allowed-tools: Read Edit Bash(rg:*) Bash(fd:*)
---

# Test Design Protocol

## Purpose

Produce a written behavioral contract — a list of agreed test cases in
simplified Gherkin — before any test or production code is written. The
contract lives in the active issue's `## Behavioral contract` section, not in
a separate file. It refines the issue's Objective into precise behavioral
specs at unit granularity.

This is a **conversation**, not a code generation task. No code is produced
during this protocol. The output is structured natural language that drives
tdd-design.

---

## Case format

All cases, during the conversation and in the final artifact, use this structure:

    Given <world state before the action>
    When  <the single action under test>
    Then  <observable outcome in domain terms>

Use `And` only when a Given genuinely requires a second condition. Keep Then
in domain language — no method names, no implementation vocabulary, no
assertion syntax.

Each confirmed case gets a stable ID: `C1`, `C2`, `C3`, ... in confirmation
order. The IDs survive into Tasks (which reference them) and into git notes
(which reference the task → case → issue chain).

---

## Your role during this protocol

- Propose cases in Given/When/Then and await confirmation
- Challenge cases that describe *how* something works internally, not *what* it does
- Ask questions when the unit's responsibility boundary is unclear
- Surface edge cases the user may not have considered
- Explicitly declare what is out of scope (folds into the issue's `Scope.Off-limits`)
- Do not suggest implementation details, class internals, or assertion code
- Do not advance past Phase 2 until the user confirms the case list is complete

---

## Phase 0: Locate the active issue

Before anything else:

```bash
ISSUE_FILE=$(rg -l '^status: active$' ~/engineering/issues -g '*.md' 2>/dev/null | head -1)
```

If empty, ask the user which issue is being contracted before proceeding.
The contract belongs in an issue — without one, there's nowhere to write it.

Read the issue. The Objective and Scope frame what the contract refines.

---

## Phase 1: Orient

Ask the minimum necessary to understand the unit under test. Lead with one
question and let the conversation develop. Do not re-ask what is already in
the issue's Objective or Context.

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

Wait for confirmation before moving on. On confirmation, assign the next
case ID (`C1`, `C2`, ...).

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

Maintain the confirmed cases as a running checklist during the conversation
so the user can see the contract taking shape.

---

## Phase 3: Close and write into the issue

When the case list feels complete, ask:
> "Is there anything missing, or anything here you'd remove before we lock this?"

Once confirmed:

1. **Edit the active issue file**, inserting (or replacing) the
   `## Behavioral contract` section between `## Open questions` and `## Tasks`:

   ```markdown
   ## Behavioral contract

   **Unit:** `<identifier>` — <one-sentence responsibility>
   **Test location:** `<file path>` > `<describe block>`

   - C1. Given <context>, When <action>, Then <outcome>
   - C2. Given <context>, When <action>, Then <outcome>
   ...
   ```

   For multi-unit issues, use subsections (`### Unit: cart`, `### Unit: pricing`).

2. **Fold "out of scope" items** into the issue's existing `## Scope` →
   **Off-limits:** field. Do not duplicate them under the contract section.

3. **Fold "open questions / assumptions"** into the issue's `## Open questions`
   list. Do not duplicate them under the contract section.

4. **Update `updated:`** in the issue frontmatter.

5. **Hand off to tdd-design immediately.** Invoke the `tdd-design` skill in
   the same turn. Do not wait for the human to ask. Say:
   > "Contract written into the issue (`<issue-file>`, cases C1–CN).
   > Starting `tdd-design` with C1 now."

---

## What this protocol does not do

- Does not write test code
- Does not write production code
- Does not suggest assertion structure or mocking strategy
- Does not advance past Phase 2 until the user confirms the case list is complete
- Does not write to a separate `~/.knowledge/contracts/` file — that pattern was retired. The issue is the source of truth.
