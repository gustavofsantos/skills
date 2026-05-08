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

# Deep Review — dispatch shim

This skill dispatches the heavy review work to the **`deep-review` subagent**
(see `agents/deep-review.md` in this plugin). The subagent runs in an
isolated context, reads the diff and the analytical reference files
(simple-design-rules, metz-heuristics, dhh-expressiveness, code-smells,
oop-criteria / fp-criteria), and returns a structured review report.

The dispatch is necessary because Phase 2 references alone are ~400 lines
plus the diff itself — running inline pollutes the main session with content
that's only useful for the review itself.

## When triggered

1. **Identify the target** from `$ARGUMENTS` or recent conversation:
   - branch range (e.g., `main..HEAD`, `origin/main...feature/x`)
   - single file path
   - inline pattern provided by the user
   If the target is genuinely ambiguous, ask one short question first.

2. **Dispatch via the Agent tool:**
   ```
   Agent(
     subagent_type: "deep-review",
     description: "Deep review of <target>",
     prompt: <see template below>
   )
   ```

   Prompt template:
   > "Run the two-phase deep review protocol on the following target:
   > **<target>**.
   >
   > Plugin root (for reading reference files): `${CLAUDE_PLUGIN_ROOT}`
   > (or run `fd 'simple-design-rules.md'` from the repo to locate the
   > reference files if the env var isn't set).
   >
   > [Any extra context the human gave, e.g. 'focus on the auth flow' or
   > 'I'm worried about edge case X' — pass through verbatim.]
   >
   > Return only the structured review report."

3. **Surface the subagent's report** to the human verbatim.

4. **Act on the chain pointer** in the report's summary:
   - **Green / Yellow** → tell the human the issue is ready to ship; the human
     (not the agent) sets `status: done` and archives the issue.
   - **Red, fixable in scope** → propose `incremental-refactor` for a
     constrained fix pass.
   - **Red, structural problems beyond scope** → propose creating a new
     inbox issue via `workflow`.

## Why a subagent

- Phase 2 loads 5 reference files (~400 lines) — kept out of main context.
- Diff scanning + per-file reads stay isolated in the subagent.
- Multiple files / branches can be reviewed in parallel via concurrent
  Agent calls.
- Subagent runs on `opus` for the high-effort analysis while main can stay
  on a faster model.
