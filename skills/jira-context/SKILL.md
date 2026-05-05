---
description: >
  Fetches Jira ticket context via acli — parent, children, and comments — the moment a
  ticket ID or URL appears in the conversation.
when_to_use: >
  Run immediately when user mentions any ticket ID (e.g., PROJ-1234) or Jira URL. One ticket →
  run the script (auto-fetches parent + all children in parallel). Multiple tickets → run each
  in parallel. Do NOT ask — just run.
argument-hint: <TICKET-ID-OR-URL> [more...]
arguments: [tickets]
context: fork
agent: Explore
allowed-tools: Bash(python3:*) Bash(acli:*)
---

# Jira Context Skill

## When to Run (DO NOT ASK — JUST RUN)

| Scenario | Action |
|----------|--------|
| User mentions ticket ID like "PROJ-1234" | **RUN** the script with the ID |
| User pastes a Jira URL | **RUN** the script — URL parsing is built-in |
| User mentions multiple tickets | **RUN** multiple parallel calls |

## Command

```bash
python3 $CLAUDE_PLUGIN_ROOT/skills/jira-context/scripts/jira-ticket-context.py PROJ-1234
python3 $CLAUDE_PLUGIN_ROOT/skills/jira-context/scripts/jira-ticket-context.py https://your-org.atlassian.net/browse/PROJ-1234
```

## What the script does automatically

1. **Parses URLs** — extracts ticket ID from any Jira URL
2. **Fetches parent** — shows one-line parent summary (epic/story) if the ticket has one
3. **Fetches all children in parallel** — subtasks rendered with full details (description + comments)
4. **Full ADF parsing** — headings, bullet/ordered lists, code blocks, tables, blockquotes, mentions, panels
5. **Filters killed tickets** — killed/cancelled/discarded tickets are silently skipped

## Output structure

```
**Parent (Epic):** [PROJ-100] Epic title · Status: In Progress

# PROJ-200 · Main ticket summary
**Type:** Story · **Status:** Done · **Assignee:** Jane Smith

## Description
[full description with proper markdown formatting]

## Comments (N)
**Author** · 2026-04-15
[comment body]

---

## Children (N active)

### PROJ-201 · Child ticket summary
**Type:** Subtask · **Status:** Done · **Assignee:** ...
...
```

## If It Fails

| Error | Fix |
|-------|-----|
| "acli not found" | Install acli, then run: `acli jira auth` |
| "not authenticated" | Run: `acli jira auth` and log in |
| "Failed to fetch" | Check ticket ID is correct and Jira is accessible |
