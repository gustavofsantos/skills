# Knowledge Vault — Canonical Formats

## Fact

```markdown
---
id: FACT-NNN
title: "Short label — what this fact says"
confidence: asserted | validated
created: YYYY-MM-DD
confirmed: YYYY-MM-DD
tags: [tag1, tag2]
refs:
  spike:
  issue:
  commit:
---

## Statement

One paragraph. Plain language. Behavioral claim, not code description.
What is true, not how it is implemented.

## Evidence

What anchors this fact. File and line, commit hash, or test name.
Prefer commit hash over file:line — a changed hash signals staleness.

## Depends on

- [[FACT-NNN-slug]] (if this fact builds on another)

## Notes

Optional. Caveats, edge cases, conditions under which this might not hold.
```

**Confidence levels:**
- `asserted` — stated by the human as external truth. Not yet verified in code.
- `validated` — confirmed through traversal or testing. Anchored to evidence.

---

## Term

```markdown
---
id: TERM-NNN
term: "Nome do conceito"
domain: financeiro
aliases: [alias1, alias2]
---

## Definição

## No código

<!-- Só preencher se o nome no código divergir do nome de negócio. Omitir a seção caso contrário. -->

## Não é

---

## Referências

- [[FACT-NNN-slug]]
- [[TERM-NNN-slug]]
```

The `## No código` section is optional. Include it only when the code name diverges from the business name. Omit the section entirely when names align.

---

## Spike

Spike format is defined in the `dead-reckoning` skill. A spike lives in `~/engineering/spikes/` and
is produced by `dead-reckoning`. It references facts by wiki link — it never contains fact content.

The spike format uses these sections:
- `**Central question:**`, `**Date:**`, `**Issue:**`
- `## Answer` — response to the central question
- `## Traversal map`
- `## Flow diagrams` (optional Mermaid)
- `## Affirmations` — `[A1]`, `[A2]`, ... marked `(candidate)` until confirmed
- `## Ignored scope` — `[SCOPE-n]` records
- `## Dynamic paths` — `[DYNAMIC-n]` records
- `## Facts promoted this session`
- `## Open questions`
