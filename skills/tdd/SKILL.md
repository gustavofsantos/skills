---
description: >
  Implements issue scenarios test-first, one at a time, using the red-green-refactor cycle.
when_to_use: >
  Use when an issue has ## Scenarios and implementation is about to begin. Triggers on
  "implement", "vamos implementar", "start coding", "começar a implementar", "let's build
  this", or when moving from planning to execution on a tracked issue.
allowed-tools: Read Write Edit Bash(rg:*) Bash(fd:*) Bash(git:*)
---

# TDD

Read the active issue. Find the first task with unchecked scenarios. Implement them
test-first in order.

## Cycle

For each scenario Sn:

**RED** — Write a failing test that directly expresses the Given/When/Then.
Given → setup. When → action. Then → assertion. No more than what the scenario says.

**GREEN** — Write the minimum code to pass. Hardcoding is valid if it makes the test
pass. Do not add untested behavior.

**REFACTOR** — Improve structure. Run tests after every change. If a test breaks, undo
and try smaller.

Mark the task `[x]` with the short commit hash when all its scenarios are green.

Move to the next task.

## Test friction is design signal

| Friction | Problem |
|---|---|
| Hard to instantiate the subject | Too many dependencies |
| Many mocks needed | High coupling |
| Setup longer than assertion | Wrong responsibility boundary |
| Can't assert without side effects | Logic mixed with I/O |

When friction appears, stop and redesign before continuing.

## Rules

- One failing test at a time.
- Never test private methods — they surface through public interface failures.
- No conditionals or loops in test code to reduce duplication.
