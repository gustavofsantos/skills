#!/usr/bin/env python3
"""
keyword_probe.py — UserPromptSubmit hook ("self-steering")

On every user prompt:
  1. Strip stopwords to extract signal keywords.
  2. Run `qmd query` against ~/engineering/ to find semantically similar
     facts, spikes, and terms.
  3. Emit `additionalContext` JSON listing matched files so Claude can
     read them proactively before forming a response.

Silent no-op when:
  - ~/engineering/ does not exist
  - qmd is not installed or times out
  - no file scores above MIN_SCORE
  - prompt has no extractable keywords

Output (stdout) — Claude Code UserPromptSubmit hook format:
  {"hookSpecificOutput": {"additionalContext": "<text>"}}
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ENGINEERING_DIR = Path.home() / "engineering"
QMD_TIMEOUT     = 6      # seconds — must stay well under Claude Code hook deadline
MIN_SCORE       = "0.50"
MAX_RESULTS     = "5"
MAX_KEYWORDS    = 10

# ─── Stopwords ────────────────────────────────────────────────────────────────

_EN = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "can", "it", "its", "this", "that",
    "these", "those", "i", "you", "he", "she", "we", "they", "me", "him",
    "her", "us", "them", "my", "your", "his", "our", "their", "what",
    "which", "who", "when", "where", "why", "how", "all", "any", "not",
    "just", "about", "up", "out", "if", "into", "through", "some", "only",
    "also", "then", "than", "so", "too", "very", "now", "here", "there",
    "no", "like", "want", "need", "make", "let", "get", "go", "use",
    "add", "new", "think", "know", "see", "look", "work", "run", "set",
    "can", "put", "take", "keep", "try", "ask", "help", "show", "tell",
    "give", "find", "move", "change", "check", "read", "write", "call",
}

_PT = {
    "o", "a", "os", "as", "um", "uma", "uns", "umas", "de", "do", "da",
    "dos", "das", "em", "no", "na", "nos", "nas", "e", "ou", "mas", "se",
    "que", "com", "por", "para", "ao", "aos", "é", "está", "são", "tem",
    "ter", "ser", "foi", "era", "isso", "esse", "essa", "este", "esta",
    "eu", "você", "ele", "ela", "nós", "eles", "elas", "meu", "seu",
    "todo", "toda", "todos", "todas", "mais", "muito", "bem", "já",
    "não", "sim", "como", "quando", "onde", "qual", "quais", "aqui",
    "lá", "então", "quero", "preciso", "fazer", "deixar", "ir", "ver",
    "usar", "adicionar", "novo", "nova", "acho", "sei", "vamos", "pode",
    "sobre", "entre", "após", "antes", "durante", "ainda", "agora",
}

STOPWORDS = _EN | _PT


# ─── Keyword extraction ───────────────────────────────────────────────────────

def extract_keywords(text: str) -> list[str]:
    words = re.findall(r"\b[a-zA-ZÀ-ÿ]{3,}\b", text.lower())
    seen, result = set(), []
    for w in words:
        if w not in STOPWORDS and w not in seen:
            seen.add(w)
            result.append(w)
    return result[:MAX_KEYWORDS]


# ─── Knowledge query ──────────────────────────────────────────────────────────

def query_knowledge(query: str) -> list[str]:
    """Return file paths that score above MIN_SCORE for the query."""
    try:
        r = subprocess.run(
            ["qmd", "query", query, "--min-score", MIN_SCORE, "-n", MAX_RESULTS],
            capture_output=True, text=True, timeout=QMD_TIMEOUT,
        )
    except FileNotFoundError:
        return []   # qmd not installed
    except subprocess.TimeoutExpired:
        return []

    if r.returncode != 0:
        return []

    return _parse_paths(r.stdout)


def _parse_paths(output: str) -> list[str]:
    """Extract file paths from qmd stdout, filtering archive entries."""
    paths, seen = [], set()
    home = str(Path.home())

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        # file:/// absolute URI
        if line.startswith("file:///"):
            candidate = line[7:]
        # bare absolute path ending in .md
        elif line.startswith("/") and ".md" in line:
            candidate = line.split()[0]  # drop trailing score annotation
        # ~/… path
        elif line.startswith("~/"):
            candidate = line.replace("~/", home + "/", 1).split()[0]
        else:
            # mixed line — try to pull out any path segment
            m = re.search(r'((?:/|~/)[^\s]+\.md)', line)
            if not m:
                continue
            candidate = m.group(1).replace("~/", home + "/", 1)

        # strip any trailing annotation like " (score: 0.82)"
        candidate = candidate.split(" (")[0].rstrip(",;")

        if "/archive/" in candidate:
            continue
        if candidate in seen:
            continue
        if Path(candidate).exists():
            seen.add(candidate)
            paths.append(candidate)

    return paths


# ─── Runtime detection ────────────────────────────────────────────────────────

# Cursor hook events that require a permission response on stdout.
_CURSOR_PERMISSION_EVENTS = {
    "beforeSubmitPrompt",
    "beforeShellExecution",
    "beforeMCPExecution",
    "beforeReadFile",
}


def _detect_runtime(payload: dict) -> str:
    """Return 'claude' or 'cursor' based on the hook payload shape."""
    event = payload.get("hook_event_name", "")
    # Claude Code uses 'UserPromptSubmit'; Cursor uses 'beforeSubmitPrompt'.
    if event == "UserPromptSubmit":
        return "claude"
    if event in _CURSOR_PERMISSION_EVENTS or "workspace_roots" in payload:
        return "cursor"
    # Fallback: if 'session_id' is present it's likely Claude Code.
    return "claude" if "session_id" in payload else "cursor"


def _extract_prompt(payload: dict) -> str:
    """Return the user's prompt text regardless of host-specific key name."""
    for key in ("prompt", "user_prompt", "message", "query"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _emit(context: str, runtime: str) -> None:
    """Print the host-appropriate JSON response."""
    if runtime == "cursor":
        # Cursor permission hooks must include 'permission: allow'.
        print(json.dumps({"permission": "allow", "additionalContext": context}))
    else:
        print(json.dumps({"hookSpecificOutput": {"additionalContext": context}}))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    runtime = _detect_runtime(payload)
    prompt  = _extract_prompt(payload)

    if not prompt:
        # For Cursor permission hooks we must always emit allow, even on no-op.
        if runtime == "cursor" and payload.get("hook_event_name") in _CURSOR_PERMISSION_EVENTS:
            print(json.dumps({"permission": "allow"}))
        sys.exit(0)

    if not ENGINEERING_DIR.exists():
        if runtime == "cursor" and payload.get("hook_event_name") in _CURSOR_PERMISSION_EVENTS:
            print(json.dumps({"permission": "allow"}))
        sys.exit(0)

    keywords = extract_keywords(prompt)
    if not keywords:
        if runtime == "cursor" and payload.get("hook_event_name") in _CURSOR_PERMISSION_EVENTS:
            print(json.dumps({"permission": "allow"}))
        sys.exit(0)

    paths = query_knowledge(" ".join(keywords))
    if not paths:
        if runtime == "cursor" and payload.get("hook_event_name") in _CURSOR_PERMISSION_EVENTS:
            print(json.dumps({"permission": "allow"}))
        sys.exit(0)

    bullets   = "\n".join(f"  - {p}" for p in paths)
    key_label = ", ".join(keywords[:5])
    context = (
        f"[Memory probe — keywords: {key_label}]\n"
        f"These knowledge files scored above threshold for this prompt:\n"
        f"{bullets}\n"
        f"Read them if they bear on the request before responding."
    )

    _emit(context, runtime)


if __name__ == "__main__":
    main()
