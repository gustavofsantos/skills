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
agents/             ← custom subagents (one .md file per subagent)
  deep-review.md    ← read-only code review subagent (high effort, opus model)
  dead-reckoning.md ← read-only code investigation subagent
  survey.md         ← read-only repository discovery subagent
  dream.md          ← memory consolidation subagent (writes facts and issue updates)
commands/           ← custom slash commands (currently empty placeholder)
hooks/              ← plugin-level Claude Code hooks (session capture)
  hooks.json        ← hook config (PostToolUse + Stop)
  parse_session.py  ← reads JSONL transcript entries and appends to session log
.claude-plugin/
  plugin.json       ← plugin name, version, author metadata
  marketplace.json  ← marketplace listing
.scripts/
  install.sh        ← installs all skills to ~/.claude/skills et al.
  setup-hooks.sh    ← copies dev hooks from .scripts/hooks/ into .git/hooks/
  hooks/
    pre-commit      ← auto-bumps plugin patch version on every commit
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
- **Search conventions:** use `fd` and `rg` for file listing and content search throughout skill bodies. They're faster on large trees and consistent across the user's machines. Issue lookup uses `fd -t f -e md . ~/engineering/issues | grep -v '/archive/'` — presence in the directory is the active signal, not a status field.
- **References** are markdown files the skill explicitly `Read`s at runtime — they are not auto-loaded. The skill SKILL.md must name which references to load and when.
- Skills target **Claude Code** as the canonical runtime (bash tool, fd, rg, qmd, Agent dispatch). Cursor / Claude Desktop installs work to the extent the host supports the same primitives. Earlier "Desktop fallback" branches that asked the AI to detect environment and produce manual-save markdown were retired — the cognitive cost of every skill body branching on runtime outweighed the marginal utility.
- The `workflow` skill is the orchestrator — it coordinates all other skills. New issues, session starts, and context recovery all route through it first.
- **tdd-design** is the single skill for specification + TDD implementation. It runs a behavioral-contract conversation (Phase 1) and immediately starts the red-green-refactor cycle (Phase 2). There is no separate test-design skill.
- The plugin ships one hook script (`hooks/parse_session.py`) configured in
  `hooks/hooks.json`. It fires on `PostToolUse` and `Stop`, reading new JSONL
  entries from the current session transcript via a cursor and appending
  structured log entries to `~/.claude/sessions/`. Session logs are the
  input to the periodic `dream` consolidation job.
- **Subagent dispatch pattern.** Read-only, batch-style skills (`deep-review`, `dead-reckoning`, `survey`) are slim dispatch shims — they call the Agent tool with the matching `subagent_type`, surface the subagent's report, and then Read the high-signal files listed in the report. The full protocol lives in `agents/<name>.md` as the subagent's system prompt; this keeps file reads and qmd queries out of the main session context. Subagents are strictly read-only — they do not write facts or spikes. When adding a new read-only skill, prefer this pattern: SKILL.md = trigger + dispatch, `agents/<name>.md` = lean protocol (~100 lines, no interactive loops).

## Engineering workspace (not in this repo)

Skills operate against `~/engineering/` — a separate directory that is the user's live workspace:

```
~/engineering/
  issues/          ← in-flight work items; presence = active, archive/ = done
    archive/
  facts/           ← atomic knowledge facts (see knowledge skill)
  spikes/          ← investigation narratives (produced by dead-reckoning subagent)
  terms/<domain>/  ← business domain term definitions (see knowledge skill)
  playbooks/       ← validation playbooks (see playbook-builder skill)
  thinking/        ← thinking-partner progress.md and flush.md, by topic
  .counters/       ← sequential ID files: issues, facts, spikes, terms
```

This is the **single root** for long-lived AI-assisted engineering state.
There is no parallel `~/.knowledge/` or `~/.config/shared-memory/` tree —
every artifact lives under one prefix so paths are predictable across skills.

The `qmd` CLI indexes this directory for semantic search. After writing any fact, spike, or term: `qmd update && qmd embed`.

**Issue lifecycle:** an issue is active when it exists in `issues/` (not `archive/`). No status field is used for routing. Archive when done.

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
