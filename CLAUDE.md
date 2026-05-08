# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code plugin containing Gustavo's personal set of skills, commands, and agents for AI-assisted engineering. Skills are installed as symlinks into `~/.claude/skills/` and `~/.agents/skills/`, and copied into `~/.cursor/skills/` (symlinks are broken in Cursor for global skills).

Plugin metadata lives in `.claude-plugin/plugin.json`.

## Remote environment setup

When working in a remote or ephemeral environment (e.g. a cloud agent, CI worktree, or fresh clone), run this before starting any work:

```bash
bash .scripts/setup-hooks.sh
```

This installs git hooks from `.scripts/hooks/` into `.git/hooks/`. Without it, the pre-commit hook that auto-bumps the plugin version will not run and commits may go out with a stale version number.

## Installing skills

```bash
npx skills add ./ -g
```

Uses the `npx skills` package to install globally. The package discovers skills via the `skills/` directory and the `.claude-plugin/plugin.json` manifest, then symlinks them into `~/.claude/skills/`, `~/.agents/skills/`, etc.

## Repository layout

```
skills/             ← one subdirectory per skill
  <name>/
    SKILL.md        ← skill definition (frontmatter + instructions)
    scripts/        ← optional Python scripts invoked by the skill
    references/     ← optional reference documents the skill reads
    examples/       ← optional worked examples
agents/             ← custom agents (currently empty placeholder)
commands/           ← custom slash commands (currently empty placeholder)
hooks/              ← plugin-level Claude Code hooks (proactive recall)
  hooks.json        ← hook config (SessionStart + UserPromptSubmit)
  session-start.sh  ← surfaces active issue / inbox / last session at start
  inject-context.py ← regex pattern detector that injects skill suggestions
.claude-plugin/
  plugin.json       ← plugin name, version, author metadata
  marketplace.json  ← marketplace listing
.scripts/
  install.sh        ← installs all skills to ~/.claude/skills et al.
  setup-hooks.sh    ← copies dev hooks from .scripts/hooks/ into .git/hooks/
  hooks/
    pre-commit      ← auto-bumps plugin patch version on every commit
bin/
  write-session-branch  ← git-plumbing writer for the personal sessions branch
```

## Skill format

Every skill is defined by `SKILL.md` with YAML frontmatter:

```markdown
---
description: >
  One sentence on what the skill does. No trigger phrases here.
when_to_use: >
  Trigger phrases (Portuguese + English) and example requests that activate this skill.
argument-hint: [arg1] [arg2]   # only when arguments are meaningful
arguments: [arg1, arg2]        # mirror argument-hint when used
allowed-tools: <space-separated>   # pre-approve tools to kill permission prompts
effort: high                   # only for reasoning-heavy skills
user-invocable: false          # only for reference-only skills not shown in /
---

# Skill Title

Instructions for the AI...
```

`description` answers "what does it do" in one sentence. `when_to_use` is the trigger surface — include canonical phrases and exclusion cases. Drop fields that don't apply. The `name:` field defaults to the directory name — do not include it.

## Skill conventions

- **Skills do not shell out to custom Python scripts** for reading or writing the engineering vault (`~/engineering/`). Use the native Read / Write / Edit / Bash tools directly. Scripts are reserved for genuine external integrations — e.g. `skills/jira-context/scripts/jira-ticket-context.py` for Jira/ADF parsing. When a script is needed, invoke it via `python3 ${CLAUDE_SKILL_DIR}/scripts/<script>.py` so the path resolves under plugin, personal, and Cursor installations alike.
- **`${CLAUDE_SKILL_DIR}`** resolves the skill's installation directory across all three distribution methods (plugin, personal symlinks, Cursor copies). Use it instead of `$CLAUDE_PLUGIN_ROOT/skills/<name>`.
- **Search conventions:** use `fd` and `rg` for file listing and content search throughout skill bodies. They're faster on large trees and consistent across the user's machines. Anchor `rg` patterns to line boundaries when matching YAML frontmatter fields (e.g. `rg -l '^status: active$'`).
- **References** are markdown files the skill explicitly `Read`s at runtime — they are not auto-loaded. The skill SKILL.md must name which references to load and when.
- Skills are designed to be invoked from Claude Code (bash tool available) or Claude Desktop (no bash tool). Skills that use bash must detect the environment and fall back gracefully for Desktop.
- The `workflow` skill is the orchestrator — it coordinates all other skills. New issues, session starts, and context recovery all route through it first.
- The plugin ships **hooks** in `hooks/` that fire on SessionStart (engineering vault state) and UserPromptSubmit (skill-trigger pattern detection). They are configured in `hooks/hooks.json` and only run in Claude Code. They make recall proactive — but the skill bodies still carry the canonical `when_to_use` triggers as a fallback for Cursor / Claude Desktop installations.

## Engineering workspace (not in this repo)

Skills operate against `~/engineering/` — a separate directory that is the user's live workspace:

```
~/engineering/
  issues/          ← active work items (see workflow skill)
    archive/
  facts/           ← atomic knowledge facts (see knowledge skill)
  spikes/          ← investigation narratives (see dead-reckoning skill)
  terms/<domain>/  ← business domain term definitions (see knowledge skill)
  .counters/       ← sequential ID files: issues, facts, spikes, terms
```

The `qmd` CLI indexes this directory for semantic search. After writing any fact, spike, or term: `qmd update && qmd embed`.

## Adding a new skill

1. Create `skills/<name>/SKILL.md` with frontmatter (`description`, `when_to_use`) and the instruction body.
2. Add Python scripts to `skills/<name>/scripts/` only for genuine external integrations. Vault reads and writes use Read/Write/Edit directly.
3. Add any reference docs to `skills/<name>/references/`.
4. Run `npx skills add ./ -g` to install locally.
5. Add a row to the appropriate table in `README.md` — name, link, and one-sentence description.

## README consistency (required)

`README.md` is the canonical index of all skills. Keep it in sync whenever skills change:

- **New skill** — add a row to the correct group in the Skills table.
- **Renamed skill** — update the row name and the link path.
- **Deleted skill** — remove the row.
- **Changed purpose** — update the description in the row to match the new `description` frontmatter.
- **Moved to a different group** — move the row to the correct table.

The README description for a skill should match the first sentence of its `description` frontmatter — same scope, same trigger framing. If they diverge, the README is wrong.
