---
description: >
  One-time onboarding — bootstraps the engineering vault, surveys the current project,
  promotes findings to facts, and orients the user on what to do next.
when_to_use: >
  Use when setting up the plugin for the first time or when a teammate is getting started.
  Triggers on "setup", "getting started", "bootstrap vault", "initialize vault",
  "setup vault", "onboard", "quero começar", or at the start of a first session with no
  existing ~/engineering/ vault.
allowed-tools: Read Write Edit Bash(rg:*) Bash(fd:*) Bash(mkdir:*) Bash(git:*) Bash(qmd:*) Bash(date:*)
---

# Setup

One-time onboarding. Safe to re-run — idempotent at every step.

---

## Phase 1 — Vault check

```bash
ls ~/engineering/ 2>/dev/null
```

If the vault exists and has content, confirm before continuing:
> "A vault already exists at ~/engineering/. Re-running will add new facts from a fresh survey but won't overwrite existing ones. Continue?"

---

## Phase 2 — Scaffold

Create the directory tree and initialize counter files (only if absent):

```bash
mkdir -p ~/engineering/{facts,spikes,issues/archive,terms,playbooks,thinking,.counters}
for f in issues facts spikes terms; do
  [ -f ~/engineering/.counters/$f ] || echo "0" > ~/engineering/.counters/$f
done
```

Set up the qmd collection:

```bash
qmd collection add ~/engineering --name engineering 2>/dev/null || true
qmd context add qmd://engineering "Engineering memory — issues, facts, spikes" 2>/dev/null || true
qmd embed 2>/dev/null || true
```

Confirm: "Vault ready at ~/engineering/."

---

## Phase 3 — Survey

Invoke the `survey` skill on the current repository. Wait for the full report before proceeding.

From the report, extract candidate facts — grounded claims about the project:
- Technology stack (language, frameworks, key dependencies)
- Architecture patterns (monolith/services, persistence, API style)
- Key conventions (testing framework, module structure, build tool)
- Integration points (external services, databases, queues)

---

## Phase 4 — Fact promotion

For each candidate fact, classify it:

**High confidence** — directly observable without inference (explicit in package.json, go.mod, README, config files, or clear directory structure). Write automatically as `confidence: asserted`.

**Unclear** — inferred from patterns, uncertain scope, or potentially outdated. Present to the user before writing:
> "I inferred [X] from [signal]. Is that accurate?"
Write only on confirmation.

To write each fact:
1. Read `~/engineering/.counters/facts`, increment, write back (zero-pad to 3 digits)
2. Write `~/engineering/facts/FACT-NNN-<slug>.md` using the format in the knowledge skill's `references/formats.md`
3. Set `confidence: asserted`; omit `validated_at`

After all facts are written: `qmd update && qmd embed`

---

## Phase 5 — Orientation

Present a short orientation grounded in what was just found — not generic docs.

```
Here's what I learned about [project name]:
[2–3 sentences from survey findings]

[N] facts written to ~/engineering/facts/.

What to do next:
- Investigate a specific question about the codebase → /dead-reckoning
- Start working on a feature or bug → /workflow
- Think through a problem before coding → /thinking-partner
- Set up git hooks in this project → /project-setup
```
