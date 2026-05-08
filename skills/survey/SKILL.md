---
description: >
  Surveys an unfamiliar repository to build atomic facts correlated with the existing
  knowledge base, plus a spike document capturing what was covered and what remains open.
when_to_use: >
  Use when encountering a new or unfamiliar project and needing to orient before any
  targeted investigation. Triggers on "survey this repo", "o que esse projeto faz",
  "bootstrap knowledge for", "orient me on", "o que é esse projeto", "nunca vi esse
  projeto", "me dá um overview de", or when starting work in a codebase with no
  existing facts. Run before dead-reckoning, not instead of it.
argument-hint: [focus]
arguments: [focus]
effort: high
allowed-tools: Read Write Edit Bash(rg:*) Bash(fd:*) Bash(cat:*) Bash(git:*) Bash(qmd:*)
---

# Survey

Oriented discovery of an unfamiliar repository. Produces atomic facts correlated with
the existing knowledge base and a spike document capturing what was covered, what was
skipped, and where to go next.

This skill is not dead-reckoning. It has no central question. It surveys terrain.

---

## Storage layout

Follows the standard layout from the `knowledge` skill:

```
~/engineering/
  facts/     ← new facts written during survey
  spikes/    ← survey spike — created at session start, updated throughout
  issues/    ← reconciliation issues created when contradictions are found
```

Fact format: see `skills/knowledge/references/formats.md`.

---

## Session start

Before reading any repository file:

1. Record the repo root and derive the project slug:
   ```bash
   REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
   PROJECT_SLUG=$(basename "$REPO_ROOT" | tr '[:upper:]' '[:space:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
   ```

2. Check if a survey spike already exists for this project:
   ```bash
   fd "survey-${PROJECT_SLUG}\.md" ~/engineering/spikes -d 1
   ```
   **If a spike exists → go to [Resuming an interrupted survey](#resuming-an-interrupted-survey).**
   **If no spike exists → continue below.**

3. Run knowledge retrieval — load existing facts related to this project:
   ```bash
   qmd query "$PROJECT_SLUG ${ARGUMENTS:-}" --min-score 0.5 -n 10
   ```
   Load results silently. These are the anchors for correlation.
   If nothing scores above threshold, proceed — a blank slate is valid.

4. Determine zone order from `$ARGUMENTS`:

   | Focus signal | Zone order |
   |---|---|
   | flag, feature, config, env, infra, terraform, helm, vault, k8s, kube | Config → Identity → Integration |
   | api, service, integrat, client, external, webhook, event | Integration → Identity → Config |
   | (none or unrecognized) | Identity → Config → Integration |

5. **Create the spike file now** — before reading anything else. Allocate a spike ID
   (read `~/engineering/.counters/spikes`, increment, write back), then write the
   initial spike using the format below with all zone sections empty and
   `## Zone progress` showing all zones as `[ ]`.

   This file is the source of truth for the entire session. Every subsequent action
   is recorded here before it is taken.

   State the zone order to the human and confirm the spike path before proceeding.

---

## Resuming an interrupted survey

When a spike already exists for this project:

1. Read the spike file in full.
2. From `## Zone progress`, identify the current state:
   - Zones marked `[x]` — already complete. Do not re-read their files.
   - Zone marked `[ ] (in progress)` — partially done. Its `### Files read` list shows
     what was already processed. Continue from the next unread file.
   - `(pending)` findings in the log — fact was noted but not yet written. Complete
     those first before continuing discovery.
3. Load the facts listed in the spike's `## Facts produced` into working context.
4. Report to the human: "Resuming survey of `<project>`. Zone N is in progress.
   Completing pending findings first, then continuing."
5. Continue the discovery loop from where it stopped.

---

## Zone 1 — Identity

What the project declares itself to be.

**Discovery commands:**
```bash
fd -t f -i '(README|CLAUDE|AGENTS|CONTRIBUTING|CHANGELOG)' "$REPO_ROOT" -d 3
fd -t f '(package\.json|pyproject\.toml|Cargo\.toml|go\.mod|mix\.exs|build\.gradle|pom\.xml|\.gemspec|project\.clj|deps\.edn)$' "$REPO_ROOT" -d 2
```

**Depth limit:** Up to 10 files. Skip files > 100kb. For README and docs, read the
first 300 lines. For manifests (package.json, go.mod, etc.), read in full.

**What to extract:**
- What the project is responsible for (one sentence, in domain terms)
- What problem it solves and for whom
- Technology stack
- Declared boundaries, scope, or explicit non-goals
- Project maturity signals (version, changelog, license)

**Fact trigger:** Write a fact for each atomic structural claim that is stable,
non-obvious, and would not be inferable from the project name or stack alone.
Identity facts tend to be broad — one or two are usually enough from this zone.

**After this zone completes:** mark Zone 1 as `[x]` in `## Zone progress` and write
the initial `## Project summary` paragraph before starting the next zone.

---

## Zone 2 — Configuration

What the project configures and controls.

**Discovery commands:**
```bash
fd -t f '\.(yaml|yml|toml|hcl|tf|tfvars)$' "$REPO_ROOT" -d 5 \
  --exclude '*/node_modules/*' --exclude '*/.git/*' --exclude '*/vendor/*' \
  --exclude '*/target/*' --exclude '*/.clj-kondo/*'

fd -t f '(\.env\.example|\.env\.sample|config\.json|settings\.json)$' "$REPO_ROOT" -d 4

fd -t d '(config|conf|configuration|settings|flags|features)' "$REPO_ROOT" -d 4
```

If `$ARGUMENTS` contains a focus keyword (flag, feature, config, env): read matching
files first and in full before moving to others in this zone.

**Depth limit:** Up to 25 files. For config directories, read all files within them.
Skip files > 200kb. Skip lock files (*.lock, yarn.lock, package-lock.json) and
compiled/generated outputs.

**What to extract:**
- Feature flags: name, default value, what behavior it gates
- External services configured: name, purpose, environment-specific variants
- Configuration categories and their purpose (especially non-obvious ones)
- Environment-specific behavior (prod vs staging vs dev differences)
- Infrastructure resources defined (if IaC is present)
- Secrets or credentials referenced by name (not value)

**Fact trigger:** Write a fact for each:
- Feature flag found (name, default, what it controls) — one fact per flag or per
  logical group of flags if they are tightly related
- External integration configured
- Distinct configuration category with non-obvious purpose

**After this zone completes:** mark Zone 2 as `[x]` in `## Zone progress`.

---

## Zone 3 — Integration

What the project connects to and how it is deployed.

**Discovery commands:**
```bash
# CI/CD
fd -t f -i '(\.github|\.gitlab-ci|circleci|jenkinsfile|\.drone|\.travis)' "$REPO_ROOT" -d 4

# Entrypoints
fd -t f '(main|app|server|entrypoint|cmd|run|start)\.(go|py|js|ts|clj|rb|ex|exs|kt|java)$' "$REPO_ROOT" -d 5

# External URLs in config files
rg -l 'https?://[^"'"'"'\s<>]+' "$REPO_ROOT" \
  --include='*.yaml' --include='*.yml' --include='*.toml' --include='*.hcl' \
  --include='*.env.example' -l 2>/dev/null | head -10
```

**Depth limit:** Up to 15 files. Focus on CI definitions (read in full) and entrypoints
(first 150 lines). For files surfaced by the URL scan, read only the sections containing
the URLs.

**What to extract:**
- External services called by name and purpose
- Deployment targets and environments
- CI/CD pipeline stages, triggers, and gates
- Other internal services this project depends on or is depended on by
- Deployment frequency signals (scheduled jobs, manual gates)

**Fact trigger:** Write a fact for each distinct external integration or deployment
target that is non-obvious from the project's identity.

**After this zone completes:** mark Zone 3 as `[x]` in `## Zone progress`.

---

## Per-discovery loop

The spike is written before the fact. If the session dies between these two steps,
on resume the agent sees the `(pending)` entry and completes it before continuing.

For each significant finding:

1. **Write to spike first.** Append to the current zone's `### Findings` list:
   ```
   - (pending) <finding statement> — anchored at <file:line or filename>
   ```
   Save the spike file. Only then proceed.

2. Query the knowledge base:
   ```bash
   qmd query "<finding in plain language>" --min-score 0.5 -n 5
   ```

3. **Related fact found — consistent:** write the new fact with `## Depends on: [[FACT-NNN-slug]]`.
   Update the spike entry: replace `(pending)` with `→ [[FACT-NNN-slug]]`.

4. **Related fact found — contradicts it:** do not write a fact. Create a reconciliation
   issue instead (see below). Update the spike entry:
   replace `(pending)` with `→ issue: reconcile-<slug>`.

5. **No related fact:** write the fact normally.
   Update the spike entry: replace `(pending)` with `→ [[FACT-NNN-slug]]`.

6. Update `### Files read` in the current zone's `## Zone progress` entry with the
   file just processed.

Never batch. One finding → spike entry → qmd → fact/issue → spike updated.

**Fact confidence:**
- `asserted` — claim comes from documentation, README, or configuration values
- `validated` — confirmed by reading actual implementation code

Most survey facts will be `asserted`. Mark `validated` only when the evidence is unambiguous code.

---

## Creating facts during survey

Follow the protocol from the `knowledge` skill:

1. Check for duplicates first (done via the per-discovery qmd query above).
2. Allocate ID:
   ```bash
   NEXT=$(cat ~/engineering/.counters/facts 2>/dev/null || echo 0)
   NEXT=$((NEXT + 1))
   printf '%d' $NEXT > ~/engineering/.counters/facts
   ID="FACT-$(printf '%03d' $NEXT)"
   ```
3. Write `~/engineering/facts/${ID}-${SLUG}.md` using the format in
   `skills/knowledge/references/formats.md`.
4. Do not run `qmd update && qmd embed` after each fact — batch the index update
   at session end.

---

## Reconciliation issues

When the survey finds something that contradicts an existing fact:

1. Do not modify the existing fact.
2. Create a new issue following the `workflow` skill's issue template:
   - Title: `Reconcile: <short description of the conflict>`
   - Status: `inbox`
   - Objective: determine which claim is accurate and update the knowledge base accordingly
   - Context: what the survey found, what the existing fact says, where each is anchored
   - Scope off-limits: do not resolve speculatively — only after targeted investigation

---

## Survey spike format

Created at session start with all zones empty. Updated after every action — not at the end.
This is the source of truth. A session can always be resumed by reading this file.

```markdown
# Survey: <project name>

**Date:** YYYY-MM-DD
**Repo:** <absolute path>
**Focus:** <focus argument or "general">
**Zone order:** <e.g., Config → Identity → Integration>

## Project summary

Written after the first zone completes. Updated if later zones revise the picture.
Leave this section empty at file creation — fill it after Zone 1 (or whichever is first).

## Zone progress

- [ ] Zone 1 — Identity
  ### Files read
  ### Findings
- [ ] Zone 2 — Configuration
  ### Files read
  ### Findings
- [ ] Zone 3 — Integration
  ### Files read
  ### Findings

(Each zone is marked [x] when complete. Files read and findings are appended
incrementally as the survey proceeds. Findings use (pending) until resolved.)

## Facts produced

- [[FACT-NNN-slug]] — <one-line summary>

## Reconciliation issues opened

- [[NNN-reconcile-slug]] — <one line on the conflict>

## Coverage gaps

Files or areas that exist in the project but were not read, with the reason.
Append to this section whenever the depth limit is reached or a file is skipped.

## Entry points for future investigation

Specific files, directories, or questions that look high-signal but were not
deeply explored. Append as they are noticed — do not wait for the end.
Each entry point is a candidate central question for a dead-reckoning session.
```

**Concrete example of a zone in progress:**

```markdown
- [ ] Zone 2 — Configuration
  ### Files read
  - config/flags.yaml
  - config/services.yaml
  ### Findings
  - (pending) Feature flag `enable-new-checkout` defaults to false — config/flags.yaml:14
  - → [[FACT-042-enable-new-checkout-flag]] Feature flag `enable-new-checkout` gates the
    redesigned checkout flow, disabled by default
  - → [[FACT-043-stripe-integration]] Stripe configured as payment provider, key injected
    via STRIPE_SECRET_KEY env var
```

---

## Finalizing the survey

By the time all three zones are marked `[x]`, the spike is already mostly complete —
findings, facts, gaps, and entry points were written incrementally. Finalization is
just the closing steps:

1. Review `## Project summary` — update if later zones revised the picture.
2. Review `## Coverage gaps` and `## Entry points` — add anything missed.
3. Index all new facts:
   ```bash
   qmd update && qmd embed
   ```
4. Report to the human:
   - N facts produced (list `## Facts produced` from the spike)
   - N reconciliation issues opened (if any)
   - 3–5 key findings from the spike
   - One concrete suggested next step — the highest-signal entry point phrased
     as a dead-reckoning central question

---

## Rules

- The spike is created before any repository file is read. No exceptions.
- Every finding is written to the spike as `(pending)` before the qmd query runs.
  If the session dies between spike write and fact write, the `(pending)` entry
  is the recovery point.
- Every file read is appended to `### Files read` in the current zone before
  reading the next file.
- Never skip knowledge retrieval at session start.
- Never batch fact writes — one finding → one spike entry → one fact.
- Never modify existing facts — read-only on the current base.
- Never write speculative facts — only what was directly observed.
- When a zone produces no facts, mark it `[x]` with an explicit note in
  `### Findings` — it is information, not a failure.
- Depth limits are hard stops. Stop at a zone's limit even if more files remain.
  Record the unread files in `## Coverage gaps`.
- The survey ends when all three zones are `[x]`, not when everything is understood.
  Unknown unknowns that remain are the job of future dead-reckoning sessions.
