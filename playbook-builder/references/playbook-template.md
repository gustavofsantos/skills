# Playbook Template

Use this as the canonical structure when writing a playbook file.
Fill every field. Omit sections only when genuinely not applicable — note why.

<template>
---
id: PB-NNN
title: "Short description of what this validates"
scope: path/to/relevant/source    # used for stale detection — match source path prefix
status: current                   # current | stale | deprecated
mode: auto                        # auto (default, omit if auto) | guided
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: []                          # domain tags, e.g. [auth, token, billing]
refs:
  facts: []                       # e.g. ["[[FACT-007-auth-token-expiry]]"]
  cards: []                       # e.g. ["012"]
  children: []                    # e.g. ["[[PB-002-db-test-setup]]"]
---

## Scope

One paragraph: what this playbook covers.
One sentence: what it explicitly does not cover.

## Setup

Preconditions stated as observable facts, not instructions.
The executor (agent or human) is responsible for achieving them before step 1.

- Precondition 1
- Precondition 2

## Steps

1. Description of what this step does
   ```bash
   command
   ```

2. [guided] Step the human must execute
   > What to do and what to observe

3. [[PB-NNN-child-playbook|Display name]]

## Validation

All criteria must hold for the feature to pass:
- [ ] Observable outcome 1
- [ ] Observable outcome 2

## Regression signals

- Signal description → likely cause → file or function

## Known edge cases

- Case: why it is correct
</template>

---

## Field reference

**`scope`** — path prefix used to detect stale state. When an agent edits any file
whose path starts with this value, the playbook is marked `stale`. Use the most
specific path that still covers all relevant source files.

**`mode`**
- `auto` — agent executes all steps with a bash block; `[guided]` overrides per step
- `guided` — human executes all steps; `[auto]` overrides per step
- Omit the field entirely when `auto` (the default)

**`refs.children`** — all child playbooks referenced in `## Steps`. Required for
indexing and stale cascade. Must match the wiki link stems exactly.

---

## Step format reference

| Pattern | Who executes |
|---|---|
| Step with fenced bash block | Agent |
| Step prefixed `[guided]` | Human |
| Step with no block, no prefix | Agent narrates, waits for confirmation |
| Wiki link on its own line | Expand and execute referenced playbook |

`[auto]` prefix on a step overrides `mode: guided` for that step only.
`[guided]` prefix on a step overrides `mode: auto` for that step only.
