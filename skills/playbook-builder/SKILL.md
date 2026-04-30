---
name: playbook-builder
description: >
  Create structured test playbooks for validating features in any environment —
  local, staging, or production. Use whenever documenting how to test an existing
  feature, stabilizing legacy behavior for automated agent validation, converting
  a dead-reckoning spike or test-design contract into an executable playbook, or
  when the user says "cria um playbook", "documenta como testar", "quero um
  roteiro de teste", "how do I validate X", or "turn this into a playbook".
  Always invoke this skill before writing any playbook file — never write playbook
  markdown directly without following this protocol.
---

# Playbook Builder

Creates executable test playbooks stored in `~/.knowledge/playbooks/`.
A playbook is a procedural document that specifies how to validate a feature —
setup, steps, and acceptance criteria — executable by an agent, a human, or both.

This skill covers **creation only**. Execution is handled by the `workflow` skill
during validation sessions.

---

## Storage layout

```
~/.knowledge/
  playbooks/
    PB-001-auth-token-refresh.md
    PB-002-db-test-setup.md          ← reusable child
    PB-003-paginated-response.md     ← reusable child
```

ID format: `PB-NNN` (zero-padded, sequential). Separate from `FACT-NNN`.

Next ID:
```bash
ls ~/.knowledge/playbooks/ 2>/dev/null | grep -oP 'PB-\d+' | sort -t- -k2 -n | tail -1
```

Increment by 1. If no files exist, start at `PB-001`.

---

## Step format (summary)

Steps in `## Steps` follow one of four patterns:

| Pattern | Who executes |
|---|---|
| Step with fenced bash block | Agent (default) |
| Step prefixed `[guided]` | Human |
| Step with no block, no prefix | Agent narrates, waits for confirmation |
| Wiki link on its own line | Expand and execute referenced playbook inline |

`mode: guided` in frontmatter inverts the default: human executes all steps unless
a step is prefixed `[auto]`. Use for production environments with no agent access.

Prefer commands. If a step can be a bash block, make it one.

---

## Creation protocols

Choose based on what already exists:

| Starting point | Protocol |
|---|---|
| `dead-reckoning` spike with validated affirmations | A — From spike |
| `test-design` contract (Given/When/Then) | B — From contract |
| Existing feature, no prior investigation | C — Direct elicitation |

---

### Protocol A — From spike

1. Read the spike document. Locate `## Affirmations`.
2. Map to playbook sections:

   | Spike element | Playbook section |
   |---|---|
   | Pre-conditions implied by affirmations | `## Setup` |
   | Action under test (the `When`) | `## Steps` |
   | Observable outcome (the `Then`) | `## Validation` |
   | `[SCOPE-n]` records | `## Known edge cases` or scope exclusion |
   | `[DYNAMIC-n]` records | `[guided]` steps — agent cannot resolve statically |

3. Identify reusable sub-routines (setup sequences that recur across features).
   Extract them as child playbooks before writing the parent.
4. Ask the human for concrete commands for any step not resolvable from the spike.
5. Present a draft. Confirm scope, step commands, and mode before writing the file.

---

### Protocol B — From contract

1. Read the `test-design` contract artifact.
2. Map to playbook sections:

   | Contract element | Playbook section |
   |---|---|
   | `Given` | `## Setup` (preconditions) |
   | `When` | `## Steps` (one step per `When`) |
   | `Then` | `## Validation` (checkbox per `Then`) |
   | "Explicitly out of scope" | `## Scope` exclusions |

3. When the contract has multiple `Given` scenarios for the same `When` action,
   each scenario becomes a separate playbook — not a conditional branch inside
   `## Steps`. One playbook = one scenario.
4. For each step: determine if a concrete command exists or needs elicitation.
5. Ask the human only for what cannot be derived from the contract.
6. Write the playbook (or set of playbooks if multiple scenarios).

---

### Protocol C — Direct elicitation

Run this conversation in order. Do not advance to the next round without answers.

**Round 1 — Scope and mode**
> "What feature or behavior does this playbook validate? One sentence."
> "Will the agent execute steps automatically, or will a human? (default: agent)"

**Round 2 — Preconditions**
> "What must be true before the first step can run?
> (e.g., specific database state, running services, environment variables)"

**Round 3 — Steps**
> "Walk me through how to validate this feature, in order.
> For each step: what's the action, and how do you confirm it worked?"

For each step the human describes, try to derive a concrete command before asking.
If no command is obvious, ask: "Is there a command I can run for this, or does a
human need to do it?"

**Round 4 — Validation and regressions**
> "What observable outcomes confirm the feature is working correctly?"
> "What does breakage look like, and where would you look first?"

**Round 5 — Edge cases**
> "Is there behavior that's intentional but might look wrong to someone running
> this for the first time?"

Present a draft after Round 5. Ask: "Does this capture the feature correctly?
Anything missing or outside scope?" Iterate until confirmed.

---

## Hierarchy rules

- A child playbook must be self-contained — executable without knowing its parent.
- The parent references children via wiki links in `## Steps` (not frontmatter only).
  Frontmatter `refs.children` lists all children for indexing and stale detection.
- Circular references are forbidden.
- Maximum depth: 2 levels (parent → child). If a child needs a child, the
  decomposition is wrong — redesign the scope boundaries.

---

## Writing the file

Read `references/playbook-template.md` before creating the playbook file.
It contains the canonical frontmatter schema and section structure.

After writing:
```bash
qmd update && qmd embed
```

Add the playbook ID to:
- The originating card's `playbooks: [PB-NNN]` field (if applicable)
- The parent's frontmatter `refs.children` (if this is a child playbook)

---

## Stale detection

Mark a playbook `stale` when editing any file whose path falls under the
playbook's `scope` value. Do this at edit time during a workflow session —
not at session end.

When a session ends with a stale playbook in the card's `playbooks:` field:
> "PB-001 ficou stale nesta sessão. Revisar antes do PR."

A stale playbook must be re-executed or updated before the card goes to review.
Propose which steps are likely affected based on what changed in the session.
