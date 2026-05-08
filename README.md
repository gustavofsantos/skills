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
| [session-close](skills/session-close/SKILL.md) | Closes the current working session: synthesizes a SESSION.md via Haiku, writes it to the personal sessions branch, and links all session commits back via git notes. |

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
| [test-design](skills/test-design/SKILL.md) | Collaborative specification protocol that writes the behavioural contract directly into the active issue's `## Behavioral contract` section. Feeds tdd-design. |
| [tdd-design](skills/tdd-design/SKILL.md) | Drives implementation using Test-Driven Development as a design tool, enforcing the red-green-refactor cycle and using test friction as a design signal. Reads cases from the issue's contract section. |
| [shameless-green](skills/shameless-green/SKILL.md) | Redirects to the simplest, most obvious code that makes a failing test pass during the GREEN phase of TDD — make it work first, make it clean after. |

### Review & Validation

| Skill | Description |
|---|---|
| [deep-review](skills/deep-review/SKILL.md) | Two-phase code review — Phase 1 scope and safety (test confidence, scope discipline, risk signal), Phase 2 architectural depth applied only to the core changed logic. |
| [playbook-builder](skills/playbook-builder/SKILL.md) | Creates structured test playbooks for validating features in any environment — local, staging, or production. |

### Knowledge Management

| Skill | Description |
|---|---|
| [knowledge](skills/knowledge/SKILL.md) | Manages the long-term knowledge library — atomic facts, spike narratives, and business domain terms stored in ~/engineering/. |
| [dead-reckoning](skills/dead-reckoning/SKILL.md) | Structured analysis partner for tracing behavior, investigating bugs, and answering architectural questions in complex or legacy codebases. |
| [survey](skills/survey/SKILL.md) | Surveys an unfamiliar repository to build atomic facts correlated with the existing knowledge base, plus a spike document capturing what was covered and what remains open. |
| [provenance](skills/provenance/SKILL.md) | Retrieves the full intent context behind a commit — issue objective, task, linked facts, semantic git note, and session document — given a commit hash. |

`qmd` ships as a non-user-invocable reference (the search primitive used by the
skills above). It is loaded by `knowledge`, `dead-reckoning`, `survey`, and
`workflow` — not exposed as a separate command surface.

### Planning & Tracking

| Skill | Description |
|---|---|
| [user-story-builder](skills/user-story-builder/SKILL.md) | Turns a raw problem or idea into a well-structured user story with acceptance criteria. |
| [user-story-planner](skills/user-story-planner/SKILL.md) | Breaks a ready user story into scoped development tasks with clear done criteria for agent execution. |

### Integrations

| Skill | Description |
|---|---|
| [jira-context](skills/jira-context/SKILL.md) | Fetches Jira ticket context via acli — parent, children, and comments — the moment a ticket ID or URL appears in the conversation. |
| [project-setup](skills/project-setup/SKILL.md) | Installs or updates provenance git hooks in the current project's .git/hooks/. |

## Subagents

Read-only, batch-style skills are split into a thin trigger surface (the
`SKILL.md`) and a heavy protocol that runs in an isolated context (the
subagent in `agents/<name>.md`). The skill dispatches to the subagent via the
`Agent` tool, the subagent does the work, and only its final structured
report enters the main session.

| Subagent | Triggered by skill | Why |
|---|---|---|
| `deep-review` | [deep-review](skills/deep-review/SKILL.md) | Loads ~400 lines of analytical references + the full diff. Runs on `opus`. Concurrent reviews possible. |
| `provenance` | [provenance](skills/provenance/SKILL.md) | Pulls fact files, git notes, and SESSION.md content into a single read — keeps them out of main context. |

Subagents need the `Agent` tool — Claude Code is the canonical runtime for
the dispatch shims. Hosts without `Agent` will see a SKILL.md that reads
like a stub; for those environments, read the matching `agents/<name>.md`
file directly to run the protocol inline.

## Hooks

The plugin ships two Claude Code hooks (configured in `hooks/hooks.json`) that
make skill recall proactive instead of purely reactive:

| Hook | Script | What it does |
|---|---|---|
| `SessionStart` | `hooks/session-start.sh` | Surfaces the active issue, inbox count, and last session for that issue at session begin. Stays silent on fresh machines (no `~/engineering/`). |
| `UserPromptSubmit` | `hooks/inject-context.py` | Pattern-matches the user's input for Jira ticket IDs, commit-hash investigations, workflow entry points, code-review intent, codebase-orientation requests, and session-close intent. Injects skill suggestions as `additionalContext` when matched. Never blocks. |

Hooks run in **Claude Code only**. Cursor and Claude Desktop installations
ignore them — the skill bodies still carry the same trigger phrases as a
fallback.

To extend hook behaviour, add patterns to `detect()` in
`hooks/inject-context.py` or new commands to `hooks/hooks.json`.

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
