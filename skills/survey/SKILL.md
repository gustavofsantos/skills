---
description: >
  Surveys an unfamiliar repository by dispatching a read-only subagent that
  discovers identity, configuration, and integration zones, returning a
  structured report with findings, fact candidates, and high-signal files.
when_to_use: >
  Use when encountering a new or unfamiliar project and needing to orient before
  targeted investigation. Triggers on "survey this repo", "o que esse projeto faz",
  "bootstrap knowledge for", "orient me on", "o que é esse projeto", "nunca vi esse
  projeto", "me dá um overview de", or when starting work in a codebase with no
  existing facts. Run before dead-reckoning, not instead of it.
argument-hint: [focus]
arguments: [focus]
effort: high
allowed-tools: Read Bash(rg:*) Bash(fd:*)
---

# Survey — dispatch shim

Dispatches the discovery to the **`survey` subagent** (see `agents/survey.md`).
The subagent reads the repository across three zones (Identity, Config,
Integration), correlates findings with the existing knowledge base, and returns
a structured report with findings and high-signal files. Running it in a
subagent keeps the zone reads and qmd queries out of the main session context.

Two survey subagents can be dispatched concurrently for orthogonal focus areas
(e.g., one on config/infra, one on integration/entrypoints).

## Dispatch

```
Agent(
  subagent_type: "survey",
  description: "Survey: <project name or focus>",
  prompt: "Repo root: <current working directory or git root>.
           Focus: <$ARGUMENTS if provided, otherwise 'general'>.
           Return the structured survey report."
)
```

## After the report arrives

1. **Surface the report** to the human.

2. **Read high-signal files.** The report's `## High-signal files` section lists
   files worth loading in full. Read each one now.

3. **Fact candidates.** For each entry in `## Fact candidates`, ask the human:
   > "Want to promote these N findings as facts?"
   If yes, invoke the `knowledge` skill for each one.

4. **Contradictions.** If the report has `## Contradictions with knowledge base`,
   surface them explicitly before proceeding. These need resolution before the
   facts can be trusted.

5. **Next step.** The report's `## Entry points for dead-reckoning` names the
   highest-signal questions for follow-up investigation. Suggest the top one as
   the next `dead-reckoning` dispatch.
