---
description: >
  Structured analysis partner for tracing behavior, investigating bugs, and answering
  architectural questions in complex or legacy codebases.
when_to_use: >
  Use when understanding existing behavior, tracing a call tree, investigating a bug, or
  answering a specific architectural question in a system that is hard to read (Clojure,
  verbose Java, Kotlin monorepos, or any poorly structured codebase). Triggers on "analisa
  esse código", "quero entender como funciona", "como isso está implementado", "me ajuda a
  traçar", "trace this call", "how is this built", "what does X do in production", or any
  request to investigate existing code before making a decision or raising a PR. Do not use
  for greenfield design or planning without a codebase — use thinking-partner for that.
argument-hint: [issue-id]
arguments: [issue_id]
effort: high
allowed-tools: Read Write Edit Bash(rg:*) Bash(fd:*) Bash(qmd:*) Bash(git:*) Bash(cat:*)
---

# Dead Reckoning — Legacy Analysis

## Storage layout

```
~/engineering/
  facts/
    FACT-NNN-slug.md      ← validated facts, global, permanent
  spikes/
    NNN-slug.md           ← this session's spike document
```

The spike document is the narrative output of this skill and the working document during
traversal. Facts are atoms promoted from the spike into the permanent library.

See the `knowledge` skill for fact format and promotion protocol.

## Spike as working document

The spike is both the working document during traversal and the final output.
Affirmations, scope records, and dynamic paths are written directly into the spike as
the traversal proceeds — candidates are marked `(candidate)` until the human confirms them.

When Plan Mode is active, it provides phase tracking. Without Plan Mode, the spike itself
is the only artifact — no separate tracking file is needed.

## Session start

1. Find the active issue:
   ```bash
   python3 $CLAUDE_PLUGIN_ROOT/skills/workflow/scripts/work-issue-list.py --status active --format text
   ```
   Read the issue file at `~/engineering/issues/<id>-<slug>.md`.

2. Probe whether Plan Mode is warranted. Before doing anything else, assess the scope
   of the investigation from the central question and any context already given:

   **Signals that warrant Plan Mode:**
   - Multiple independent entry points to traverse (more than one subsystem, service, or call tree)
   - The question spans more than one repository or deployment boundary
   - Open questions in the issue suggest the traversal will branch significantly
   - You expect the work to take more than one session

   **Signals that do not warrant Plan Mode:**
   - Single entry point, narrow question, one system
   - Likely answerable in one focused session
   - The human said something like "quick look" or "just check"

   If Plan Mode is warranted, say so explicitly and ask:
   > "This investigation looks broad — [one sentence on why]. Want to switch to Plan Mode
   > so we can map the traversal phases before starting?"

   Wait for the human's answer. If yes, enter Plan Mode now. If no, proceed linearly.

3. Run knowledge retrieval:
   ```bash
   qmd query "<investigation topic>" --min-score 0.5 -n 6
   ```
   Load relevant facts silently. If a fact is directly relevant to the central question,
   surface it to the human before traversal begins:
   > "[[FACT-007-auth-token-refresh-window]] covers auth token refresh in this system. Should I treat it as an axiom
   > for this session, or do you want to verify it fresh?"

**If no issue exists yet:**
```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/workflow/scripts/work-issue-create.py --title "<title>"
```

**If no system name is clear:** ask "What system is this?" before anything else.

## Phase 1 — Orient

**Identify the central question.** A topic is not a question. If the input is vague:

> "That's a topic, not a question. What would a good answer look like — something like
> 'Does X happen before Y?' or 'Who owns Z when W occurs?'"

A good central question has a factual or yes/no answer, narrow enough for one session.
Once confirmed, write it in `**Central question:**` at the top of the spike document.

**Declare entry points.** Before touching code:

> "I'll start at {entry point} because {reason}. Does that make sense?"

Wait for confirmation or redirection.

If in Plan Mode, update the plan to reflect Phase 1 complete and Phase 2 in progress.

## Phase 2 — Traverse

Core loop. Repeat until the central question is answered or a genuine edge is reached.

**Traverse one step.** Read code. Understand behavior, not syntax.

**Produce an affirmation** — a plain-language behavioral claim, not a code description:

```
[A{n}] {Behavioral claim at business or architecture level}
       ↳ Anchored at: {file:line or function name}
       ↳ Depends on: {[[FACT-NNN-slug]] or prior affirmation — omit if none}
```

**Pause and ask: "Does this hold?"** Wait for a real answer.

- Yes → append to `## Affirmations` in the spike, marked `(candidate)`.
- No → stop. Ask what's wrong. Correct and re-ask. Do not continue until resolved,
  or human explicitly says "set it aside and keep going."

**Record ignored scope** before moving past any branch:

```
[SCOPE-{n}] Did not traverse: {branch or function}
             Reason: {out of scope | separate spike | depth limit}
             Risk: {what we might be missing}
```

**Flag dynamic paths:**

```
[DYNAMIC-{n}] Dynamic branch at: {location}
               Cannot resolve statically. Human verification required.
```

**Reference existing facts explicitly.** When relying on a loaded fact:

> "I'm relying on [[FACT-007-auth-token-refresh-window]] — '{fact statement}'. Is that still accurate?"

If invalidated: follow the invalidation protocol in the `knowledge` skill immediately.
Treat dependent affirmations as suspect until re-verified.

**Name divergence hook.** When traversal encounters a concept whose name in code
diverges from the expected business name (e.g., the code uses `BillingPeriod` but
the domain calls it "Ciclo de faturamento"):

1. Query for an existing term:
   ```bash
   qmd query "<business concept name>" --min-score 0.5 -n 3 --files
   ```
   Filter results to `~/engineering/terms/`.

2. **If a term exists** (`[[TERM-NNN-slug]]`): reference it in the affirmation and,
   if the term's `## No código` section is empty, fill it in:
   ```
   [A{n}] {Behavioral claim}
          ↳ Anchored at: {file:line}
          ↳ Term: [[TERM-NNN-slug]] — note: code uses '{CodeName}'
   ```

3. **If no term exists**: pause and signal to the human before continuing:
   > "The code uses '{CodeName}' for what I'd expect to be called '{BusinessName}'.
   > No term exists for this concept yet. Want to create one before we continue,
   > or proceed and flag it as a candidate term?"
   Wait for the human's decision. Do not continue traversal past the divergence
   without resolution.

**Lens triggers.** During traversal, two situations warrant offering a lens:

- An affirmation reveals something recurring — the same pattern appearing in multiple
  places, or a fix that feels like a patch on a deeper issue:
  > "This looks structural — the same problem appearing in three different places.
  > Want to run the Iceberg lens before we continue?"

- An architectural decision is encountered — a design choice about coupling, boundaries,
  or how two parts of the system interact:
  > "This is a design decision worth examining. Want to run 'What Is Braided Here?'
  > on how these two concerns are coupled?"

Do not run lenses automatically. Offer them. Wait for the human to decide.

**When traversal reveals mappable structure**, produce a Mermaid diagram in the spike
as a visual layer alongside the prose. The diagram distills structure already described
in affirmations — it does not replace them.

Good candidates:
- Call sequence between components → `sequenceDiagram`
- State transitions in a domain object → `stateDiagram-v2`
- Data flow or component boundaries → `flowchart`

Place the diagram in `## Flow diagrams` in the spike, referencing the affirmation IDs
it distills (`[A1]–[A4]`). Only produce a diagram when the structure is clear enough
to be accurate — a misleading diagram is worse than no diagram.

**Update the spike document** after every validated affirmation, scope/dynamic record,
and fact confirmation or invalidation. Write directly into the relevant sections — never
leave state only in memory.

**Signal edges clearly:**

- *Scope edge* — chose not to go further: note in `### Scope records`, continue.
- *Knowledge edge* — cannot go further: say so explicitly, wait for human.

Never conflate these.

## Phase 3 — Promote to facts

For each `(candidate)` affirmation in `## Affirmations` of the spike:

> "Candidate: '{statement}' — anchored at {commit hash or file:line}.
> Promote to a permanent fact?"

If confirmed, invoke the `knowledge` skill promotion protocol.
Unconfirmed candidates stay in the spike as narrative — not promoted.

Mark promoted affirmations in the spike with `→ [[FACT-NNN-slug]]` replacing the candidate text.

## Phase 4 — Finalize spike

1. Write the **Answer** section in the spike document — response to the central
   question, referencing affirmation IDs and fact wiki links.
2. Write the **Open Questions** section — genuine unknowns reached but not resolved.
   (Not "we didn't look" — that's Ignored Scope.)
3. Add a wiki link to the spike in the originating issue's `spikes:` field.
4. Report to human: question answered or not, open questions, facts promoted.
5. If in Plan Mode: mark all phases done. If this was the entire issue, signal:
   "Investigation complete. Ready for planning."

## Spike document format

<spike>
# {Investigation title}

**Central question:** {One sentence.}
**Date:** YYYY-MM-DD
**Issue:** {issue id if applicable}

## Answer

{Response to the central question. References [A-n] and [[FACT-NNN-slug]].}

## Traversal map

{Entry points and path taken.}

## Flow diagrams

{Optional. Mermaid diagrams of structures revealed during traversal — call sequences,
state machines, data flows. Each diagram notes which affirmations it distills.
Omit this section if no mappable structure was found.}

## Affirmations

[A1] ...
[A2] ...

## Ignored scope

[SCOPE-1] ...

## Dynamic paths

[DYNAMIC-1] ...

## Facts promoted this session

- [[FACT-NNN-slug]] — {one-line summary}

## Open questions

{Genuine unknowns not resolved.}
</spike>

## What this skill does not do

- Does not begin traversal without a confirmed central question.
- Does not continue past a rejected affirmation without resolution.
- Does not invent facts — only the human confirms external truths.
- Does not promote unconfirmed candidates to the knowledge library.
- Does not run thinking lenses automatically — offers them at the right moment.
- Does not create files in the worktree — all state lives in the spike document.
