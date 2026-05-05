# Claude Desktop — Fallback Procedures

When running on Claude Desktop the bash tool is unavailable. Follow these procedures.

## Detecting the environment

Attempt to use the bash tool. If unavailable, switch to Desktop mode for all operations.

## Querying facts (Desktop)

Use the `qmd` MCP server query tool with the issue title and objective as the query.
Load results above score 0.5. Ignore the rest. The server exposes the same collection
as the CLI.

## Creating a fact (Desktop)

Fact writes require filesystem access. Generate the complete fact markdown in chat using
the format in `formats.md`, state clearly that the user must save it to
`~/engineering/facts/FACT-NNN-<slug>.md` with the correct sequential ID, and then run
`qmd update && qmd embed` in a terminal to index it.

## Creating a term (Desktop)

Generate the full term markdown using the format in `formats.md`, instruct the user to
save it to `~/engineering/terms/<domain>/TERM-NNN-<slug>.md` with the correct sequential
ID, then run `qmd update && qmd embed` in a terminal.

## Updating a fact (Desktop)

Read via qmd MCP server. For writes, generate the updated markdown and instruct
the user to apply it, then run `qmd update && qmd embed`.

## Invalidating a fact (Desktop)

Generate the updated markdown with `confidence: invalidated` and an `## Invalidated`
section (date, reason, replaced-by link if applicable). Instruct the user to apply and
then run `qmd update && qmd embed`.

Do not delete invalidated facts. The history of what was believed is useful.
Identify any facts that `## Depends on` the invalidated one and review them.

## General rule

On Claude Desktop, never silently skip a write operation. Always surface the markdown
to the user and explain what they need to do.
