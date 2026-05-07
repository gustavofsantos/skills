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
| [bounded-contexts](skills/bounded-contexts/SKILL.md) | Applies bounded context and loose coupling principles when designing or reviewing module boundaries, service contracts, and component interactions. |
| [interface-design](skills/interface-design/SKILL.md) | Applies Go-derived interface design principles to design or review abstractions in any language — Go, Clojure, Java, Kotlin, TypeScript, and Python. |
| [evolutionary-design](skills/evolutionary-design/SKILL.md) | Produces design constraints for building new features or systems incrementally, avoiding big-bang design via a tracer-bullet approach. |

### TDD Cycle

| Skill | Description |
|---|---|
| [test-design](skills/test-design/SKILL.md) | Collaborative specification protocol to define the behavioral contract of a unit before any code is written. |
| [tdd-design](skills/tdd-design/SKILL.md) | Drives implementation using Test-Driven Development as a design tool, enforcing the red-green-refactor cycle and using test friction as a design signal. |
| [shameless-green](skills/shameless-green/SKILL.md) | Redirects to the simplest, most obvious code that makes a failing test pass during the GREEN phase of TDD — make it work first, make it clean after. |
| [incremental-refactor](skills/incremental-refactor/SKILL.md) | Produces constraints for safe, incremental refactoring — behavior-preserving steps, one transformation at a time, no scope expansion. |

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
| [qmd](skills/qmd/SKILL.md) | Semantic and keyword search over local markdown collections using the qmd CLI or MCP server. |
| [survey](skills/survey/SKILL.md) | Surveys an unfamiliar repository to build atomic facts correlated with the existing knowledge base, plus a spike document capturing what was covered and what remains open. |
| [provenance](skills/provenance/SKILL.md) | Retrieves the full intent context behind a commit — issue objective, task, linked facts, semantic git note, and session document — given a commit hash. |

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
