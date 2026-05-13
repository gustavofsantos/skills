---
description: >
  Consolidates session logs into the engineering vault — extracts corrections,
  decisions, and fact candidates from recent sessions and writes them as facts
  and issue updates directly to ~/engineering/.
when_to_use: >
  Use when you want to consolidate recent sessions into the knowledge vault.
  Triggers on "run dream", "consolidate sessions", "update vault", "dream",
  "process sessions", or when the scheduled job is not frequent enough and
  you want an immediate consolidation pass.
effort: high
allowed-tools: Read Write Edit Bash(fd:*) Bash(rg:*) Bash(git:*) Bash(qmd:*) Bash(date:*) Bash(cat:*)
---

# Dream — dispatch shim

Dispatches consolidation to the **`dream` subagent** (`agents/dream.md`).
The subagent reads all unprocessed session logs, mines signal across them,
and writes directly to the vault. Running in a subagent keeps the file
reads and writes out of the main session context.

## Dispatch

```
Agent(
  subagent_type: "dream",
  description: "Consolidate session logs into engineering vault",
  prompt: "Run the full 4-stage dream protocol.
           Vault root: ~/engineering/
           Session logs: ~/engineering/sessions/
           Write directly. Commit when done.
           Return the summary report."
)
```

## After the report arrives

Surface the report to the human. No follow-up action required — the
subagent has already written and committed.

If the report lists conflicts (corrected beliefs that touch validated facts),
surface those specifically:
> "These validated facts may need review: [list]"

The human decides whether to investigate further or leave them as-is.
