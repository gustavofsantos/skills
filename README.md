# Skills

A personal Claude Code plugin containing the skills, commands, and agents Gustavo uses when pairing with AI as an engineer.

Skills are Markdown instruction files that Claude loads on demand. They encode repeatable protocols — code review, TDD cycles, knowledge management, daily workflow — so the same approach is applied consistently across sessions.

## Installation

### Claude Code marketplace (recommended)

Add the marketplace and install the plugin with the native Claude Code plugin system:

```bash
claude plugin marketplace add gustavofsantos/skills
claude plugin install skills@gustavofsantos
```

Works in Claude Code CLI and Claude Desktop. Keep in sync with:

```bash
claude plugin marketplace update gustavofsantos
```

Skills are namespaced as `/gustavofsantos:<skill-name>` (e.g. `/gustavofsantos:workflow`).

### npx skills (alternative)

Install globally using the `npx skills` package:

```bash
npx skills add gustavofsantos/skills -g
```

To install only specific skills:

```bash
npx skills add gustavofsantos/skills -g -s workflow deep-review knowledge
```

To install from a local clone of this repo:

```bash
npx skills add ./ -g
```

**Managing installed skills:**

```bash
npx skills list -g          # list what's installed
npx skills update -g        # pull latest versions
npx skills remove -g        # uninstall
```

## Skills

### Orchestration

| Skill | Description |
|---|---|
| [workflow](skills/workflow/SKILL.md) | Protocol for managing daily engineering work — the orchestrator that coordinates all other skills across planning, execution, and review phases. |

### Thinking & Design

| Skill | Description |
|---|---|
| [thinking-partner](skills/thinking-partner/SKILL.md) | Socratic thinking partner for exploring problems deeply before delegating to an executor. |
| [thinking-lenses](skills/thinking-lenses/SKILL.md) | Structured analytical lenses for reaching specific kinds of depth during a thinking session. |
| [design](skills/design/SKILL.md) | Interactive design analysis — `boundary` mode for module/service boundaries and coupling, `abstraction` mode for interfaces / protocols / traits across Go, Clojure, Java, Kotlin, TypeScript, and Python. |
| [design-constraints](skills/design-constraints/SKILL.md) | Constraint blocks to paste into an issue's `## Context` — `evolutionary` mode for tracer-bullet greenfield work, `refactor` mode for behavior-preserving incremental change. |

### TDD Cycle

| Skill | Description |
|---|---|
| [tdd-design](skills/tdd-design/SKILL.md) | Full TDD workflow: collaborative behavioral-contract conversation followed immediately by the red-green-refactor cycle. |

### Review & Validation

| Skill | Description |
|---|---|
| [deep-review](skills/deep-review/SKILL.md) | Two-phase code review — Phase 1 scope and safety (test confidence, scope discipline, risk signal), Phase 2 architectural depth applied only to the core changed logic. |
| [playbook-builder](skills/playbook-builder/SKILL.md) | Creates structured test playbooks for validating features in any environment — local, staging, or production. |

### Knowledge Management

| Skill | Description |
|---|---|
| [dream](skills/dream/SKILL.md) | Consolidates session logs into the engineering vault — extracts corrections, decisions, and fact candidates and writes them directly as facts and issue updates. |
| [knowledge](skills/knowledge/SKILL.md) | Manages the long-term knowledge library — atomic facts, spike narratives, and business domain terms stored in ~/engineering/. |
| [dead-reckoning](skills/dead-reckoning/SKILL.md) | Structured code investigation that dispatches a read-only subagent to trace behavior and answer architectural questions, returning behavioral claims and high-signal files to load. |
| [survey](skills/survey/SKILL.md) | Surveys an unfamiliar repository by dispatching a read-only subagent across Identity, Config, and Integration zones, returning findings and fact candidates. |
| [auto-spike](skills/auto-spike/SKILL.md) | Autonomously extends open investigation threads across the spike library — selects up to 4 spikes with unresolved SCOPE/DYNAMIC records, traverses the relevant code, and writes child spikes. |

### Planning & Tracking

| Skill | Description |
|---|---|
| [user-story-builder](skills/user-story-builder/SKILL.md) | Turns a raw problem or idea into a well-structured user story with acceptance criteria. |
| [user-story-planner](skills/user-story-planner/SKILL.md) | Breaks a ready user story into scoped development tasks with clear done criteria for agent execution. |

### Integrations

| Skill | Description |
|---|---|
| [jira-context](skills/jira-context/SKILL.md) | Fetches Jira ticket context via acli — parent, children, and comments — the moment a ticket ID or URL appears in the conversation. |

## Subagents

Read-only, batch-style skills are split into a thin trigger surface (the
`SKILL.md`) and a heavy protocol that runs in an isolated context (the
subagent in `agents/<name>.md`). The skill dispatches to the subagent via the
`Agent` tool, the subagent does the work, and only its final structured
report enters the main session.

| Subagent | Triggered by skill | Why |
|---|---|---|
| `deep-review` | [deep-review](skills/deep-review/SKILL.md) | Loads ~400 lines of analytical references + the full diff. Runs on `opus`. Concurrent reviews possible. |
| `dead-reckoning` | [dead-reckoning](skills/dead-reckoning/SKILL.md) | Reads code and knowledge base across many files without filling the main session context. Returns claims + high-signal files. |
| `survey` | [survey](skills/survey/SKILL.md) | Discovers an unfamiliar repo across three zones without filling the main session context. Two surveys can run concurrently on orthogonal focus areas. |
| `auto-spike` | [auto-spike](skills/auto-spike/SKILL.md) | Selects open spike threads, traverses the relevant code, writes child spikes, and updates parent SCOPE/DYNAMIC records. Runs headless on a schedule via `bin/auto-spike-run`. |

Subagents need the `Agent` tool — Claude Code is the canonical runtime for
the dispatch shims. Hosts without `Agent` will see a SKILL.md that reads
like a stub; for those environments, read the matching `agents/<name>.md`
file directly to run the protocol inline.

## Hooks

The plugin ships one hook script (`hooks/parse_session.py`) configured in `hooks/hooks.json`:

| Hook | Script | What it does |
|---|---|---|
| `UserPromptSubmit` (Claude Code) · `beforeSubmitPrompt` (Cursor) | `hooks/keyword_probe.py` | Extracts keywords from the user prompt, queries `~/engineering/` via `qmd`, and injects matching fact/spike/term file paths as `additionalContext` so Claude self-steers toward relevant memory before responding. Auto-detects the host runtime and emits the correct response format for each. |
| `PostToolUse` | `hooks/parse_session.py` | Reads new JSONL entries since last cursor, runs MapReduce to pair tool events, appends structured log to `~/engineering/sessions/`. |
| `Stop`        | `hooks/parse_session.py --finalize` | Final flush of session log; marks session complete in frontmatter. |

Hooks run in **Claude Code only**. Cursor and Claude Desktop installations
ignore them — the skill bodies still carry the same trigger phrases as a
fallback.

## Development setup

After cloning, install the git hooks:

```bash
bash .scripts/setup-hooks.sh
```

This installs a pre-commit hook that automatically bumps the patch version in `.claude-plugin/plugin.json` whenever you commit without manually changing the version.

## Adding a skill

1. Create `skills/<name>/SKILL.md` with YAML frontmatter (`description`, `when_to_use`) and the instruction body.
2. Add Python scripts to `skills/<name>/scripts/` only for genuine external integrations. Vault reads and writes use Read/Write/Edit directly.
3. Add reference docs to `skills/<name>/references/` as needed.
4. Re-run `npx skills add ./ -g` to pick up the new skill locally.
5. Add a row to the appropriate table in this README.
