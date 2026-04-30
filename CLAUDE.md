# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code plugin containing Gustavo's personal set of skills, commands, and agents for AI-assisted engineering. Skills are installed as symlinks into `~/.claude/skills/` and `~/.agents/skills/`, and copied into `~/.cursor/skills/` (symlinks are broken in Cursor for global skills).

Plugin metadata lives in `.claude-plugin/plugin.json`.

## Installing skills

```bash
bash .scripts/install.sh
```

This symlinks each `skills/<name>/` directory into `~/.claude/skills/<name>` and `~/.agents/skills/<name>`, and hard-copies into `~/.cursor/skills/<name>`.

## Repository layout

```
skills/          ← one subdirectory per skill
  <name>/
    SKILL.md     ← skill definition (frontmatter + instructions)
    scripts/     ← optional Python scripts invoked by the skill
    references/  ← optional reference documents the skill reads
    examples/    ← optional worked examples
agents/          ← custom agents (currently empty placeholder)
commands/        ← custom slash commands (currently empty placeholder)
.claude-plugin/
  plugin.json    ← plugin name, version, author metadata
.scripts/
  install.sh     ← installs all skills to ~/.claude/skills et al.
```

## Skill format

Every skill is defined by `SKILL.md` with YAML frontmatter:

```markdown
---
name: <skill-name>
description: >
  One-paragraph description used by the AI harness to decide when to
  invoke this skill. Trigger phrases belong here.
---

# Skill Title

Instructions for the AI...
```

The `description` field is the trigger surface — it controls when Claude activates the skill automatically. Keep it precise: include canonical trigger phrases and the exclusion cases.

## Skill conventions

- **Scripts** are Python 3, invoked via `python3 ~/.claude/skills/<name>/scripts/<script>.py`. Scripts accept `--format json` (default) or `--format text` unless the script has a different interface.
- **References** are markdown files the skill explicitly `Read`s at runtime — they are not auto-loaded. The skill SKILL.md must name which references to load and when.
- Skills are designed to be invoked from Claude Code (bash tool available) or Claude Desktop (no bash tool). Skills that use bash must detect the environment and fall back gracefully for Desktop.
- The `workflow` skill is the orchestrator — it coordinates all other skills. New issues, session starts, and context recovery all route through it first.

## Engineering workspace (not in this repo)

Skills operate against `~/engineering/` — a separate directory that is the user's live workspace:

```
~/engineering/
  issues/          ← active work items (see workflow skill)
    archive/
  facts/           ← atomic knowledge facts (see knowledge skill)
  spikes/          ← investigation narratives (see dead-reckoning skill)
  terms/<domain>/  ← business domain term definitions (see knowledge skill)
  .counters/       ← sequential ID files: facts, spikes, terms
```

The `qmd` CLI indexes this directory for semantic search. After writing any fact, spike, or term: `qmd update && qmd embed`.

## Adding a new skill

1. Create `skills/<name>/SKILL.md` with frontmatter (`name`, `description`) and the instruction body.
2. Add any Python scripts to `skills/<name>/scripts/`.
3. Add any reference docs to `skills/<name>/references/`.
4. Run `bash .scripts/install.sh` to install.
5. Add a row to the appropriate table in `README.md` — name, link, and one-sentence description.

## README consistency (required)

`README.md` is the canonical index of all skills. Keep it in sync whenever skills change:

- **New skill** — add a row to the correct group in the Skills table.
- **Renamed skill** — update the row name and the link path.
- **Deleted skill** — remove the row.
- **Changed purpose** — update the description in the row to match the new `description` frontmatter.
- **Moved to a different group** — move the row to the correct table.

The README description for a skill should match the first sentence of its `description` frontmatter — same scope, same trigger framing. If they diverge, the README is wrong.
