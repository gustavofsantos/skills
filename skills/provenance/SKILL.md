---
description: >
  Retrieves the full intent context behind a commit — issue objective, task, linked
  facts, semantic git note, and session document — given a commit hash.
when_to_use: >
  Use when debugging a change and wanting to understand why it was made. Triggers on
  "por que isso foi mudado", "contexto desse commit", "provenance <hash>", "quem mudou
  isso e por quê", "o que motivou essa mudança", "git blame this", "who wrote this
  line", "who introduced this", "quem introduziu", "quem adicionou", "what was the
  reasoning", or after a git blame / git log when investigating a specific commit
  hash. Also when a 7-40 char hex hash appears next to investigative language
  (porquê, motivação, contexto, why, blame, motivation). Do not use for code
  traversal without a hash — use dead-reckoning for that.
argument-hint: [commit-hash]
arguments: [commit_hash]
allowed-tools: Bash(git:*) Bash(rg:*) Bash(fd:*) Bash(cat:*)
---

# Provenance — dispatch shim

This skill dispatches the read-only provenance traversal to the
**`provenance` subagent** (see `agents/provenance.md` in this plugin). The
subagent walks the chain commit → issue → task → facts → git note →
SESSION.md and returns a structured report. Running it in a subagent keeps
fact files and session documents out of the main context.

## When triggered

1. **Resolve the hash** from `$ARGUMENTS`. If none, the subagent will default
   to HEAD.

2. **Dispatch via the Agent tool:**
   ```
   Agent(
     subagent_type: "provenance",
     description: "Provenance for <short-hash>",
     prompt: <see template below>
   )
   ```

   Prompt template:
   > "Recover the provenance for commit `<hash-or-HEAD>`.
   > [Optional: any context the human gave about why they're asking — e.g.
   > 'I'm investigating an auth regression' — pass through verbatim.]
   > Return only the structured provenance report."

3. **Surface the subagent's report** to the human verbatim.

4. **Chain pointers:**
   - If the report references facts or a session that the human wants to
     act on, the relevant skills (`knowledge`, `dead-reckoning`) handle the
     follow-up.
   - If the commit predates the workflow system (no issue, no note, no
     session), suggest `dead-reckoning` for a forward investigation if the
     human wants to reconstruct intent from the code.

## Why a subagent

- Pulls in fact files, git notes, and SESSION.md content that are only
  useful for this specific report — keeps them out of main context.
- Pure read-only — no side effects, safe to dispatch.
- Multiple commits can be investigated in parallel via concurrent calls.
