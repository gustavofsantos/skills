---
description: >
  Manages the long-term knowledge library — atomic facts, spike narratives, and business
  domain terms stored in ~/engineering/.
when_to_use: >
  Use when a validated discovery should be preserved beyond a single session, when promoting
  a dead-reckoning finding to a permanent fact, or when querying for prior knowledge.
  Triggers on "save this as a fact", "do we know anything about X", "promote this finding",
  "what do we know about Y", "salva isso como fato", "o que sabemos sobre X".
argument-hint: [topic]
allowed-tools: Read Write Edit Bash(rg:*) Bash(fd:*) Bash(qmd:*) Bash(cat:*)
---

# Knowledge

The knowledge library is the long-term memory of the system. Queried before execution,
written whenever a validated fact is discovered.

## Storage layout

```
~/engineering/
  facts/      FACT-001-auth-token-refresh-window.md
  spikes/     001-auth-investigation.md
  terms/
    financeiro/   TERM-001-ciclo-de-faturamento.md
  .counters/  facts  spikes  terms
```

Facts are global — not scoped to a repo. Spikes are produced by `dead-reckoning`.
Terms are scoped by business domain.

For canonical file formats (frontmatter + sections), read `references/formats.md`.

**Confidence levels:**
- `asserted` — stated as external truth, not yet verified in code
- `validated` — confirmed through traversal or testing, anchored to evidence

---

## Querying

```bash
qmd query "auth token expiry behavior" -n 5
qmd search "FACT-007" --full
fd '^FACT-007.*\.md$' ~/engineering/facts -d 1
```

---

## Creating a fact

1. Check for duplicates first:
   ```bash
   qmd query "<proposed statement>" -n 5
   ```
   If a related fact exists, extend it rather than creating a duplicate.

2. Allocate ID and write the file:
   ```bash
   NEXT=$(cat ~/engineering/.counters/facts 2>/dev/null || echo 0)
   NEXT=$((NEXT + 1))
   echo $NEXT > ~/engineering/.counters/facts
   ID="FACT-$(printf '%03d' $NEXT)"
   FILE=~/engineering/facts/${ID}-<slug>.md
   ```
   Write `$FILE` using the format in `references/formats.md`.

3. Index:
   ```bash
   qmd update && qmd embed
   ```

4. Add the wiki link to the originating issue's `### Facts` section.

---

## Updating a fact

```bash
FILE=$(fd '^FACT-007.*\.md$' ~/engineering/facts -d 1)
```
Read, Edit, then `qmd update && qmd embed`.

---

## Promoting a finding from dead-reckoning

1. The finding has: a statement, an anchor (file:line or commit hash), human confirmation.
2. Create the fact with `confidence: validated`. Fill `refs` and `confirmed` date.
3. In the spike, replace the full finding text with `→ [[FACT-NNN-slug]]`.
4. `qmd update && qmd embed`.

---

## Invalidating a fact

Read the file, set `confidence: invalidated`, append an `## Invalidated` section, then
`qmd update && qmd embed`. Do not delete — the history of what was believed is useful.
Review any facts that `## Depends on` the invalidated one.

---

## Creating a term

```bash
mkdir -p ~/engineering/terms/<domain>
NEXT=$(cat ~/engineering/.counters/terms 2>/dev/null || echo 0)
NEXT=$((NEXT + 1))
echo $NEXT > ~/engineering/.counters/terms
FILE=~/engineering/terms/<domain>/TERM-$(printf '%03d' $NEXT)-<slug>.md
```
Write using the term format in `references/formats.md`. Then `qmd update && qmd embed`.

**Facts vs. terms:** a fact is empirical — behavioral claim anchored to code.
A term is normative — what a concept means in the business domain.
The `## No código` section is only written when the code name diverges from the business name.

---

## qmd collection setup (one-time)

```bash
qmd collection add ~/engineering --name engineering
qmd context add qmd://engineering "Engineering memory — issues, sessions, facts, spikes"
qmd embed
```

---

## Rules

- One fact per atomic claim. Two paragraphs = two facts — split it.
- Facts are global. Never scope a universal claim to a single system.
- Never copy fact content into an issue or spike. Reference by wiki link only.
- Always `qmd update && qmd embed` after writing. A fact that can't be found doesn't exist.
- Confidence reflects the evidence, not how certain you feel.
