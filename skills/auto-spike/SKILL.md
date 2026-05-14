---
description: >
  Autonomously extends open investigation threads across the spike library — selects
  up to 4 spikes with unresolved SCOPE/DYNAMIC records, traverses the relevant code,
  writes child spikes, and updates parent spike records.
when_to_use: >
  Use when you want to advance stale investigations without manual effort. Triggers
  on "run auto-spike", "extend open spikes", "advance spike threads", "auto-spike",
  or when the scheduled job is not frequent enough and you want an immediate pass.
  Do not use for a focused investigation of a specific question — use dead-reckoning
  for that.
effort: high
allowed-tools: Read Write Edit Bash(fd:*) Bash(rg:*) Bash(git:*) Bash(qmd:*) Bash(date:*)
---

# Auto-Spike — dispatch shim

Dispatches spike extension to the **`auto-spike` subagent** (`agents/auto-spike.md`).
The subagent selects open threads, traverses the relevant code, writes child spikes,
and updates parent spike records. Running in a subagent keeps the file reads and
traversals out of the main session context.

## Dispatch

```
Agent(
  subagent_type: "auto-spike",
  description: "Extend open spike threads",
  prompt: "Run the full auto-spike protocol.
           Vault root: ~/engineering/
           Spikes dir: ~/engineering/spikes/
           Select up to 4 spikes with open threads (SCOPE/DYNAMIC/Open questions).
           Traverse one thread per spike. Write child spikes with repo: field.
           Update parent spike SCOPE/DYNAMIC records. Promote fact candidates.
           Commit when done. Return the summary report."
)
```

## After the report arrives

Surface the report to the human. No follow-up action required — the
subagent has already written and committed.

If the report lists skipped spikes (no `repo:` field), surface those:
> "These spikes were skipped — add a `repo:` field to enable auto-extension: [list]"

If the report lists new child spikes, offer to load the high-signal files
from any child spike the human wants to review:
> "I can load the high-signal files from any of these spikes if you want to
>  review the findings now."
