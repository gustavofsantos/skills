---
description: >
  Two-phase code review — Phase 1 scope and safety (test confidence, scope discipline, risk
  signal), Phase 2 architectural depth applied only to the core changed logic.
when_to_use: >
  Use when the user says "review branch", "review before PR", "review this file", "check my
  changes", "faça um code review", "analise este código", "revise este PR", or similar.
  Works on a branch diff, a single file, or a usage pattern.
argument-hint: [target]
effort: high
allowed-tools: Read Bash(rg:*) Bash(fd:*) Bash(git:*) Bash(cat:*)
---

# Review

Two phases. Phase 1 always runs. Phase 2 runs on the core logic only — not the whole
diff, not scaffolding, not test boilerplate.

The goal of Phase 1 is: is this safe to ship?
The goal of Phase 2 is: is the core logic well-designed?

---

## Entry points

If invoked with `$ARGUMENTS` (e.g. `/deep-review main..feature` or `/deep-review src/auth.clj`),
use the argument as the review target and skip the clarification step. Otherwise ask the user
what to review before proceeding.

**Branch diff** (most common):
```bash
BASE=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' \
  || git branch -l main master | head -1 | xargs)
git log $BASE..HEAD --oneline
git diff $BASE...HEAD --stat
git diff $BASE...HEAD
```

**Single file:** read the file directly.

**Usage pattern:** the human provides the code inline or describes the pattern.

In all cases, identify the **core change** before starting Phase 1.
The core change is the thing this review exists to evaluate — not the surrounding
infrastructure that makes it work.

State it explicitly before proceeding:
> "The core change here is {X}. Everything else is scaffolding.
> I'll review the full diff for safety, then apply depth analysis to {X}."

Wait for confirmation or correction before proceeding.

---

## Phase 1 — Scope and safety

### 1a — Test confidence

Read tests first. Tests are the documentation of what the change is supposed to do.

Ask:
1. Do the test names and assertions communicate the intent without reading production code?
2. Is coverage proportional to risk? High-risk paths — error handling, side effects,
   edge cases — should have explicit coverage.
3. Would a meaningful regression in production code cause these tests to fail?
   If not, the tests are not protecting anything.

Rate test confidence:

```
TEST CONFIDENCE
├── Rating: High | Medium | Low | None
├── What tests communicate: [what you understood from tests alone]
├── Gaps: [missing coverage, vague assertions, untested scenarios]
└── Verdict: enough confidence to proceed | tests need work first
```

If rating is **Low or None**: stop. Flag it. Let the human decide whether to continue.
A review without test confidence is a guess.

### 1b — Scope discipline

Does the diff contain only what the card or intent describes?

Flag separately any change that:
- Touches unrelated files or behavior
- Mixes refactoring with feature work
- Introduces new abstractions not required by the stated problem

Scope violations are not blocking by default — they are flagged for the human to decide.

### 1c — Safety signal

```
PHASE 1 — SCOPE AND SAFETY
├── Test confidence: High | Medium | Low | None
├── What tests communicate: [summary]
├── Test gaps: [list or "none"]
├── Scope discipline: on-target | contains unrelated changes — [list if any]
├── Safety signal: Green | Yellow | Red
└── Verdict: proceed to depth review | address first
```

**Signal guide:**
- Green — proceed. Tests give confidence, scope is clean.
- Yellow — proceed with noted gaps. Human decides.
- Red — do not ship. Tests are absent or scope is dangerously wide.

---

## Phase 2 — Depth review

Only the **core change** gets depth review. Not the test files, not the wiring,
not the migration scripts. The thing this change is fundamentally about.

Load the analytical pillars before proceeding. Read each reference file:

- `references/simple-design-rules.md` — Kent Beck, four rules in priority order
- `references/metz-heuristics.md` — Sandi Metz structural limits and flocking rules
- `references/dhh-expressiveness.md` — DHH conceptual compression and expressiveness
- `references/code-smells.md` — Kerievsky/Fowler smell catalog and refactoring paths
- `references/oop-criteria.md` or `references/fp-criteria.md` — based on detected paradigm

Infer the paradigm from the code. Load both criteria files if the paradigm is mixed.

### Depth analysis structure

**Section 1 — Paradigm and health signal**
One paragraph. Detected paradigm. Overall signal. Framing tone — empathetic, never punitive.
The code reflects the constraints of the moment it was written.

**Section 2 — Structural diagnosis**
Narrative prose, not bullet lists. Each finding:
- Names the smell or violation
- Points to the exact location in the code
- Names the pillar it violates and why that matters in practice
- Explains how it degrades clarity, cohesion, or substitutability

Use a table only when multiple violations share the same root cause.

**Section 3 — Refactoring plan**
Ordered steps. Each step:
- Names the transformation (e.g., "Extract Value Object for Money")
- Cites the pillar (e.g., "eliminates Primitive Obsession")
- Describes the mechanical action

Steps must be sequential and safe. No leaps. New pattern without showing the path = blocked.

**Section 4 — Refactored code**
The core change rewritten. No inline comments explaining what the code does.
No section markers. Names carry all meaning. Reading it should feel easy.

---

## Full output format

```
REVIEW: [branch/file/pattern]
CORE CHANGE: [one sentence]

─── PHASE 1 — SCOPE AND SAFETY ───────────────────────────────

Test confidence: [High/Medium/Low/None]
What tests communicate: [summary]
Test gaps: [list or "none"]
Scope discipline: [on-target / unrelated changes: list]
Safety signal: [Green/Yellow/Red]
Verdict: [proceed / address first]

─── PHASE 2 — DEPTH REVIEW ────────────────────────────────────

[Section 1 — Paradigm and health signal]

[Section 2 — Structural diagnosis]

[Section 3 — Refactoring plan]

[Section 4 — Refactored code]

─── SUMMARY ────────────────────────────────────────────────────

Overall: Green | Yellow | Red
Must fix before merge: [blocking issues or "none"]
Consider: [non-blocking improvements]
Looks good: [specific things done well]
```

---

## After review — chain back to workflow

When the review concludes:

- **Green / Yellow** → tell the human the issue is ready to ship and remind them
  that the human (not the agent) sets `status: done`. If the workflow skill is
  active for the issue, surface its archive step.
- **Red** → name what blocks shipping in one sentence. If the blockers can be
  addressed in scope, hand off to `incremental-refactor` for a constrained fix
  pass; otherwise create a new inbox issue (via `workflow`) for follow-up work.

If structural problems surface that match the catalog of `bounded-contexts` or
`interface-design`, name the skill and flag it as a candidate for a separate
issue — do not expand the current review.

---

## Rules

- Always state the core change before starting. Get confirmation.
- Lead with tests. No tests on meaningful logic = Red, always.
- Never invent findings. Only flag what is actually present.
- Depth review applies to the core change only — not the full diff.
- If the core change is simple and correct, say so. A short Phase 2 is not a lazy review.
- Do not suggest refactors outside the scope of the change. Flag them under:
  `OUT OF SCOPE — WORTH NOTING` if genuinely important (security, data integrity).
- Write in the same language the human is using.
- Empathy is not optional. The code reflects the constraints of the moment it was written.
