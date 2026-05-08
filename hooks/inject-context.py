#!/usr/bin/env python3
"""
UserPromptSubmit hook — pattern-detects skill triggers in the user's prompt
and injects skill suggestions as additionalContext.

Stays silent (exit 0, empty output) when no patterns match. Never blocks.
The injected text is prepended to the model's context for that turn,
nudging recall of the relevant skill without overriding the user.
"""
import json
import re
import sys
from typing import List


# Identifiers that look like Jira tickets but aren't
JIRA_EXCLUDED_PREFIXES = {
    "UTF", "ISO", "ASCII", "HTTP", "HTTPS", "SHA", "MD", "AES", "RSA",
    "TLS", "SSL", "API", "URL", "URI", "JSON", "XML", "HTML", "CSS",
    "PR", "CI", "CD", "RFC", "ECMA", "ANSI", "IEEE", "OAUTH", "JWT",
    "CVE", "GHSA",
}


def detect(text: str) -> List[str]:
    """Return a list of skill suggestions to inject. Empty = stay silent."""
    suggestions: List[str] = []

    # ── Jira ticket IDs ──────────────────────────────────────────────────
    # PROJ-1234, ABC-99, etc. Excludes well-known non-Jira prefixes.
    jira_re = re.compile(r"\b([A-Z][A-Z0-9]{1,9})-(\d+)\b")
    jira_hits = sorted({
        m.group(0)
        for m in jira_re.finditer(text)
        if m.group(1) not in JIRA_EXCLUDED_PREFIXES
    })
    if jira_hits:
        suggestions.append(
            f"**Jira ticket(s) detected:** {', '.join(jira_hits)}. "
            f"Run the `jira-context` skill **immediately** and in parallel for each ticket — "
            f"do not ask for confirmation."
        )

    # ── Commit-hash provenance investigation ─────────────────────────────
    # 7–40 hex chars with intent signals nearby (not on the same line as code blocks)
    hash_re = re.compile(r"\b([0-9a-f]{7,40})\b")
    intent_re = re.compile(
        r"\b(why|por\s*qu[eê]|porqu[eê]|provenance|blame|"
        r"who\s+(wrote|changed|made|added|introduced)|"
        r"quem\s+(escreveu|mudou|fez|adicionou|introduziu)|"
        r"context\s+(of|behind|for)|contexto\s+(do|desse|deste)|"
        r"motivou|motivation|motiva[çc][ãa]o)\b",
        re.IGNORECASE,
    )
    if hash_re.search(text) and intent_re.search(text):
        suggestions.append(
            "**Commit-intent investigation pattern detected.** "
            "Trigger the `provenance` skill — it dispatches to the `provenance` "
            "subagent (read-only chain: issue → task → facts → git note → "
            "SESSION.md). Pass the commit hash as the argument."
        )

    # ── Workflow entry points ────────────────────────────────────────────
    workflow_re = re.compile(
        r"(?:\b|^)("
        r"new\s+issue|nova\s+issue|"
        r"start\s+(?:a\s+)?session|come[çc]ar\s+(?:a\s+)?(?:trabalhar|sess[ãa]o)|"
        r"let'?s\s+work\s+on|vamos\s+(?:trabalhar|começar|comecar)\s+(?:em|n[oa])|"
        r"continue\s+(?:on|with|the)|continuar\s+(?:n[oa]|com)|"
        r"context\s+recovery|recuperar\s+contexto|"
        r"what\s+are\s+we\s+working\s+on|"
        r"resume\s+(?:work|session|the\s+issue)|retomar\s+(?:trabalho|sess[ãa]o)|"
        r"create\s+an?\s+issue\s+for|criar\s+uma?\s+issue\s+para"
        r")(?:\b|$)",
        re.IGNORECASE,
    )
    if workflow_re.search(text):
        suggestions.append(
            "**Workflow entry point detected.** Use the `workflow` skill — it is "
            "the orchestrator and decides which other skills to invoke "
            "(test-design / tdd-design / dead-reckoning / deep-review / etc.)."
        )

    # ── Code review request on a branch / PR ─────────────────────────────
    review_re = re.compile(
        r"\b(review|revis[ãa]r|revise|fa[çc]a\s+(?:um\s+)?code\s*review|"
        r"code\s*review|c\.r\.|cr\b)\b",
        re.IGNORECASE,
    )
    review_target_re = re.compile(
        r"\b(branch|pr|pull\s+request|main\.\.|origin/|HEAD\.\.|"
        r"diff|changes|altera[çc][õo]es|este\s+pr|esse\s+pr|"
        r"before\s+(?:i\s+)?(?:push|merge|ship|pr)|"
        r"antes\s+(?:do|de)\s+(?:push|merge|pr))\b",
        re.IGNORECASE,
    )
    if review_re.search(text) and review_target_re.search(text):
        suggestions.append(
            "**Code review intent detected.** Trigger the `deep-review` skill — "
            "it dispatches to the `deep-review` subagent (Phase 1 scope/safety "
            "+ Phase 2 depth on the core change). The subagent runs on Opus in "
            "an isolated context."
        )

    # ── Survey / orient on unfamiliar codebase ───────────────────────────
    survey_re = re.compile(
        r"\b(survey\s+(?:this\s+)?(?:repo|project)|"
        r"orient\s+me|me\s+orient[ae]|"
        r"never\s+seen\s+(?:this|that)|nunca\s+vi\s+(?:esse|este)|"
        r"o\s+que\s+(?:esse|este)\s+projeto\s+faz|"
        r"what\s+does\s+this\s+(?:repo|project)\s+do|"
        r"give\s+me\s+an\s+overview|me\s+d[áa]\s+um\s+overview|"
        r"bootstrap\s+knowledge)\b",
        re.IGNORECASE,
    )
    if survey_re.search(text):
        suggestions.append(
            "**Codebase orientation request detected.** Use the `survey` skill "
            "to build atomic facts before any targeted investigation. "
            "(Run `dead-reckoning` only after the survey, or for a specific question.)"
        )

    # ── Session close ────────────────────────────────────────────────────
    close_re = re.compile(
        r"\b(close\s+(?:the\s+)?session|end\s+(?:the\s+)?session|"
        r"wrap\s+up\s+(?:this|the)\s+session|finalize\s+session|"
        r"fechar\s+(?:a\s+)?sess[ãa]o|encerrar\s+(?:a\s+)?sess[ãa]o|"
        r"finalizar\s+(?:a\s+)?sess[ãa]o)\b",
        re.IGNORECASE,
    )
    if close_re.search(text):
        suggestions.append(
            "**Session close intent detected.** Use the `session-close` skill "
            "to synthesize SESSION.md, write to the personal sessions branch, "
            "and link commits via git notes."
        )

    return suggestions


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        # Malformed input — stay invisible
        sys.exit(0)

    # The Claude Code hook contract uses several keys depending on version.
    # Try them all, fall back to empty.
    user_input = (
        payload.get("userInput")
        or payload.get("user_input")
        or payload.get("prompt")
        or payload.get("message")
        or ""
    )
    if not isinstance(user_input, str) or not user_input.strip():
        sys.exit(0)

    suggestions = detect(user_input)
    if not suggestions:
        sys.exit(0)

    context_lines = ["**Skill triggers detected by plugin hook — consider invoking:**", ""]
    context_lines.extend(f"- {s}" for s in suggestions)
    context_lines.append("")
    context_lines.append(
        "These are heuristic suggestions, not commands. Use them when the user's "
        "intent matches; otherwise proceed normally."
    )

    response = {
        "decision": "allow",
        "additionalContext": "\n".join(context_lines),
    }
    print(json.dumps(response))


if __name__ == "__main__":
    main()
