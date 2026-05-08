---
description: >
  Manages the long-term knowledge library — atomic facts, spike narratives, and business
  domain terms stored in ~/engineering/.
when_to_use: >
  Use when a validated discovery should be preserved beyond a single session, when promoting a
  dead-reckoning theorem to a permanent fact, when querying for prior knowledge, or when
  maintaining the qmd index. Triggers on "save this as a fact", "do we know anything about X",
  "promote this theorem", "what do we know about Y", or when the workflow skill's session start
  protocol runs knowledge retrieval.
argument-hint: [topic]
allowed-tools: Read Write Edit Bash(rg:*) Bash(fd:*) Bash(qmd:*) Bash(cat:*)
---

# Knowledge

The knowledge library is the long-term memory of the system. It survives issue completion,
session endings, and context window pressure. It is queried automatically at session start
and written to whenever a validated fact is discovered.

This skill targets Claude Code (bash, fd, rg, qmd available). It is not designed
for environments without those tools.

---

## Storage layout

```
~/engineering/
  facts/
    FACT-001-auth-token-refresh-window.md
    FACT-002-billing-cycle-immutability.md
  spikes/
    001-auth-investigation.md
    002-payment-flow-traversal.md
  terms/
    financeiro/
      TERM-001-ciclo-de-faturamento.md
    fretboard/
      TERM-002-nota-musical.md
  .counters/
    facts    ← sequential ID counter
    spikes   ← sequential ID counter
    terms    ← sequential ID counter
```

Facts are global — not scoped to a system or repo.
Spikes are narratives produced by `dead-reckoning`. They reference facts but do not contain them.
Terms are scoped by business domain, not by project or codebase.

---

## Fact format

For the canonical fact format (YAML frontmatter + section structure), read [references/formats.md](references/formats.md).

**Confidence levels:**
- `asserted` — stated by the human as external truth. Not yet verified in code.
- `validated` — confirmed through traversal or testing. Anchored to evidence.

Never invent a fact. Never assert confidence higher than the evidence supports.

---

## Spike format

Spikes live in `~/engineering/spikes/`. They are produced by `dead-reckoning`.
Their format is defined in the `dead-reckoning` skill.

A spike references facts by wiki link. It never contains the fact content.

```markdown
This confirms that auth token refresh happens before expiry validation.
-> [[FACT-007-auth-token-refresh-window]]

The billing cycle is immutable once created — updates are not possible,
only replacements.
-> [[FACT-012-billing-cycle-immutability]], [[FACT-013-billing-replacement-flow]]
```

---

## Terms

Terms are normative definitions of business domain concepts. They answer the question
"what does this concept mean in this domain?" rather than "what does the code do?"

**Facts vs. terms:**
- A **fact** is empirical — a behavioral claim anchored to evidence in code (file:line, commit hash, test name). It describes what the system does.
- A **term** is normative — it defines what a concept means in the business domain. It does not require a code anchor.

**When to create a term:**
- A domain concept appears recurrently across sessions and issues
- There is risk of confusion between the business name and the code name
- A concept needs an authoritative definition that can be referenced, not re-explained

**Terms can exist without references.** Not every business concept has a fact yet.
A term without a `## Referências` entry is valid — it defines the concept for future use.

### Term format

For the canonical term format (YAML frontmatter + section structure), read [references/formats.md](references/formats.md).

### Creating a term

1. `domain_dir = ~/engineering/terms/<domain>` — create with `mkdir -p` if absent.
2. Read `~/engineering/.counters/terms` (treat as `0` if absent). Increment and write back.
3. Slugify the term name (lowercase, hyphens, max 5 words).
4. Write `$domain_dir/TERM-<NNN>-<slug>.md` using the format from [references/formats.md](references/formats.md) — substitute fields.
5. Fill `## Definição` and `## Não é`, then index:
   ```bash
   qmd update && qmd embed
   ```
6. Reference by wiki link: `[[TERM-NNN-slug]]`.

---

## Querying facts

```bash
# Semantic search
qmd query "auth token expiry behavior" -n 5

# Keyword + semantic combined
qmd query $'lex: auth token\nvec: token refresh before expiry check' -n 5

# Exact keyword / ID lookup
qmd search "FACT-007" --full

# Read a specific fact by ID
fd '^FACT-007.*\.md$' ~/engineering/facts -d 1
```

---

## Creating a fact

1. Check for duplicates:
   ```bash
   qmd query "<proposed fact statement>" -n 5
   ```
   If a related fact exists, extend it rather than creating a duplicate.

2. Allocate an ID and scaffold the file:
   ```bash
   NEXT=$(cat ~/engineering/.counters/facts 2>/dev/null || echo 0)
   NEXT=$((NEXT + 1))
   echo $NEXT > ~/engineering/.counters/facts
   ID="FACT-$(printf '%03d' $NEXT)"
   SLUG="<short-slug>"
   FILE=~/engineering/facts/${ID}-${SLUG}.md
   ```

3. Write `$FILE` using the Write tool with the canonical format from [references/formats.md](references/formats.md) — substitute `{id}`, `{title}`, `{today}`. Fill body sections.

4. Index:
   ```bash
   qmd update && qmd embed
   ```

5. Add the wiki link to the originating issue's `### Facts` section.

---

## Updating a fact

Locate the file:
```bash
FILE=$(fd '^FACT-007.*\.md$' ~/engineering/facts -d 1)
```
Use Read to load it, then Edit to update frontmatter or body. After any write:
```bash
qmd update && qmd embed
```

---

## Promoting a theorem from dead-reckoning

When `dead-reckoning` produces a confirmed theorem:

1. The theorem has: a statement, an anchor (commit hash or file:line), and human confirmation.
2. Scaffold the fact with `confidence: "validated"`, fill `refs` and `confirmed` date,
   then `qmd update && qmd embed`.
3. In the spike document, replace the full theorem text with `→ [[FACT-NNN-slug]]`.

---

## Invalidating a fact

```bash
FILE=$(fd '^FACT-007.*\.md$' ~/engineering/facts -d 1)
```
Use Read to load the file, Edit to set `confidence: invalidated` in frontmatter and
append an `## Invalidated` section, then:
```bash
qmd update && qmd embed
```

Do not delete invalidated facts. The history of what was believed is useful.
Identify any facts that `## Depends on` the invalidated one and review them.

---

## Session start protocol (automatic)

```bash
qmd query "<issue title> <issue objective>" -n 8
```

Load results above score 0.5. Ignore the rest.

---

## qmd collection setup (one-time)

```bash
qmd collection add ~/engineering --name engineering
qmd context add qmd://engineering "Engineering memory — issues, sessions, facts, and spike narratives"
qmd embed
```

Run once when setting up a new machine.

---

## Rules

- One fact per atomic claim. If a fact needs two paragraphs, it contains two claims — split it.
- Facts are global. Never scope them to a system when the claim is universal.
- Never copy fact content into an issue or spike. Reference by wiki link only.
- A fact exists to be found. If it cannot be found by query, it does not exist.
  Always run `qmd update && qmd embed` after writing.
- Confidence is a property of the evidence, not of how certain you feel.
  Asserted = human said so. Validated = code confirms it.
- Terms are scoped by business domain, not by codebase. A term in `financeiro/` applies
  to the financial domain regardless of which project implements it.
- The `## No código` section in a term is only written when the business name and the
  code name diverge. When they match, omit the section entirely — do not write it empty.
