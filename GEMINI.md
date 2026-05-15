# GEMINI.md

This file provides guidance to Gemini CLI when working with code in this repository.

## What this repo is

A personal set of skills, commands, and agents for AI-assisted engineering. Skills are installed as symlinks into `~/.gemini/skills/` and `~/.gemini/agents/`.

Extension metadata lives in `gemini-extension.json`.

## Remote environment setup

When working in a remote or ephemeral environment, run this before starting any work:

```bash
bash .scripts/setup-hooks.sh
```

## Installing skills

```bash
bash .scripts/install.sh
```

## Repository layout

```
skills/             ← one subdirectory per skill
  <name>/
    SKILL.md        ← skill definition (frontmatter + instructions)
    scripts/        ← optional Python scripts invoked by the skill
    references/     ← optional reference documents the skill reads
    examples/       ← optional worked examples
agents/             ← custom subagents (one .md file per subagent)
  deep-review.md    ← read-only code review subagent
  dead-reckoning.md ← read-only code investigation subagent
  survey.md         ← read-only repository discovery subagent
  dream.md          ← memory consolidation subagent
hooks/              ← plugin-level hooks (currently Claude-only)
gemini-extension.json ← extension metadata
GEMINI.md           ← this file
```

## Skill format

Every skill is defined by `SKILL.md` with YAML frontmatter. Gemini CLI uses the same **Agent Skills** standard as Claude Code.

```markdown
---
description: >
  One sentence on what the skill does.
when_to_use: >
  Trigger phrases and example requests that activate this skill.
---

# Skill Title

Instructions for the AI...
```

## Tool Mapping (Claude vs Gemini)

When following instructions in `SKILL.md` files that might mention Claude Code tools, use the following Gemini CLI equivalents:

| Claude Code Tool | Gemini CLI Equivalent |
| :--- | :--- |
| `Read` | `read_file`, `read_many_files`, `list_directory` |
| `Write` | `write_file` |
| `Edit` | `replace` |
| `Bash` | `run_shell_command` |
| `fd` | `glob` |
| `rg` | `grep_search` |
| `Agent` | `invoke_agent` or specific tool name |

## Subagent dispatch pattern

Read-only, batch-style skills (`deep-review`, `dead-reckoning`, `survey`) are slim dispatch shims. In Gemini CLI, call them using the `invoke_agent` tool (or the specific tool name if available).

The full protocol lives in `agents/<name>.md`. Gemini CLI loads these from `.gemini/agents/`.

## Engineering workspace (not in this repo)

Skills operate against `~/engineering/` — the single root for long-lived AI-assisted engineering state.
The `qmd` CLI (if available) indexes this directory for semantic search.

**Issue lifecycle:** an issue is active when it exists in `issues/` (not `archive/`).
