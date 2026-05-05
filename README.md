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
| [workflow](skills/workflow/SKILL.md) | Daily work management protocol. Entry point for all phases — planning, execution, and review. Manages issues in `~/engineering/issues/` and coordinates all other skills. |

### Thinking & Design

| Skill | Description |
|---|---|
| [thinking-partner](skills/thinking-partner/SKILL.md) | Socratic partner for exploring problems before acting. Drives the conversation with questions, tracks a progression document, and produces a flush file Claude Code can load at session start. |
| [thinking-lenses](skills/thinking-lenses/SKILL.md) | Structured analytical lenses to apply during a thinking session when the problem needs a specific kind of depth. Used by `thinking-partner` — not run standalone. |
| [bounded-contexts](skills/bounded-contexts/SKILL.md) | Applies bounded context and loose coupling principles when deciding how modules should communicate, where a dependency belongs, or why a change is breaking something far away. |
| [interface-design](skills/interface-design/SKILL.md) | Applies Go-derived interface design principles to any language when defining or reviewing an abstraction boundary (interface, protocol, trait, abstract class). |
| [evolutionary-design](skills/evolutionary-design/SKILL.md) | Produces a constraint block for the issue's Context section when starting a new feature or module, to avoid big-bang design. |

### TDD Cycle

| Skill | Description |
|---|---|
| [test-design](skills/test-design/SKILL.md) | Collaborative protocol to define the behavioral contract of a unit before any code is written. Run before `tdd-design`. |
| [tdd-design](skills/tdd-design/SKILL.md) | Enforces the red-green-refactor cycle and uses test friction as a design signal. Takes the contract from `test-design` as input. |
| [shameless-green](skills/shameless-green/SKILL.md) | Redirects the agent to write the simplest code that makes the test pass during the GREEN phase, before worrying about abstraction or elegance. |
| [incremental-refactor](skills/incremental-refactor/SKILL.md) | Produces refactoring constraints for the issue's Context section: behavior-preserving steps, no scope expansion, one transformation at a time. |

### Review & Validation

| Skill | Description |
|---|---|
| [deep-review](skills/deep-review/SKILL.md) | Two-phase code review. Phase 1: scope and safety (test confidence, scope discipline, risk signal). Phase 2: architectural depth on the core change only. |
| [playbook-builder](skills/playbook-builder/SKILL.md) | Creates structured test playbooks for validating features in local, staging, or production environments. |

### Knowledge Management

| Skill | Description |
|---|---|
| [knowledge](skills/knowledge/SKILL.md) | Manages the long-term knowledge library: atomic facts (`~/engineering/facts/`), spike narratives (`~/engineering/spikes/`), and business domain terms (`~/engineering/terms/`). |
| [dead-reckoning](skills/dead-reckoning/SKILL.md) | Structured codebase investigation for complex or legacy systems. Enforces a central question, builds a living fact base, and produces a spike document. |
| [qmd](skills/qmd/SKILL.md) | Semantic search over the knowledge library using the `qmd` CLI or MCP server. |

### Planning & Tracking

| Skill | Description |
|---|---|
| [user-story-builder](skills/user-story-builder/SKILL.md) | Turns a raw idea or problem description into a well-structured user story with acceptance criteria. |
| [user-story-planner](skills/user-story-planner/SKILL.md) | Breaks a ready user story into scoped development tasks with clear done criteria for agent execution. |

### Integrations

| Skill | Description |
|---|---|
| [jira-context](skills/jira-context/SKILL.md) | Fetches Jira ticket context (parent, children, comments) via `acli` the moment a ticket ID or URL is mentioned. |

## Development setup

After cloning, install the git hooks:

```bash
bash .scripts/setup-hooks.sh
```

This installs a pre-commit hook that automatically bumps the patch version in `.claude-plugin/plugin.json` whenever you commit without manually changing the version.

## Adding a skill

1. Create `skills/<name>/SKILL.md` with YAML frontmatter (`name`, `description`) and the instruction body.
2. Add Python scripts to `skills/<name>/scripts/` and reference docs to `skills/<name>/references/` as needed.
3. Re-run `npx skills add ./ -g` to pick up the new skill locally.
4. Add a row to the appropriate table in this README.
