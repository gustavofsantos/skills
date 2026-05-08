---
description: >
  Structured code investigation — dispatches a read-only subagent to trace
  behavior, answer architectural questions, and return a structured report
  with behavioral claims and high-signal files to load.
when_to_use: >
  Use when understanding existing behavior, tracing a call tree, investigating
  a bug, or answering a specific architectural question. Triggers on "analisa
  esse código", "quero entender como funciona", "como isso está implementado",
  "me ajuda a traçar", "trace this call", "how is this built", "what does X do",
  or any request to investigate existing code before making a decision. Do not
  use for greenfield design — use thinking-partner for that.
argument-hint: [question] [entry-point]
arguments: [question, entry_point]
effort: high
allowed-tools: Read Bash(rg:*) Bash(fd:*)
---

# Dead Reckoning — dispatch shim

Dispatches the investigation to the **`dead-reckoning` subagent**
(see `agents/dead-reckoning.md`). The subagent traverses the codebase,
correlates with the knowledge base, and returns a structured report with
behavioral claims and high-signal files. Running it in a subagent keeps
the file reads and qmd queries out of the main session context.

## Dispatch

Build the prompt from `$ARGUMENTS` and any context the human gave:

```
Agent(
  subagent_type: "dead-reckoning",
  description: "Investigate: <central question>",
  prompt: "Central question: <question from $ARGUMENTS or inferred from context>.
           Entry points: <specific files, functions, or symbols if provided>.
           Context: <any relevant facts, issue objective, or prior knowledge from
           this session — pass through verbatim>.
           Return the structured report."
)
```

## After the report arrives

1. **Surface the report** to the human.

2. **Read high-signal files.** The report's `## High-signal files` section lists
   files worth loading in full. Read each one:
   ```
   Read(path)  — for each file in the list
   ```

3. **Fact candidates.** If the report has a `## Fact candidates` section and the
   human wants to promote findings, invoke the `knowledge` skill for each candidate.

4. **Scope pointer.** If the report's `## Ignored scope` contains branches the
   human wants to investigate next, this skill can be dispatched again with a
   narrower entry point.
