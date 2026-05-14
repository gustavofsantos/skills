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
QMD_TIMEOUT     = 10      # seconds — must stay well under Claude Code hook deadline
MIN_SCORE       = "0.50"
MAX_RESULTS     = "5"
MAX_KEYWORDS    = 20

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
    # Match URLs as single tokens, then regular words
    pattern = r"(?:https?://\S+|ftps?://\S+|\b[a-zA-ZÀ-ÿ]{3,}\b)"
    matches = re.findall(pattern, text)
    seen, result = set(), []
    for m in matches:
        if m not in STOPWORDS and m not in seen:
            seen.add(m)
            result.append(m)
    return result[:MAX_KEYWORDS]


# ─── Knowledge query ──────────────────────────────────────────────────────────

def query_knowledge(query: str) -> list[str]:
    """Return file paths that score above MIN_SCORE for the query."""
    try:
        r = subprocess.run(
            ["qmd", "query", query, "-c", "engineering",
             "--min-score", MIN_SCORE, "-n", MAX_RESULTS, "--no-rerank", "--json"],
            capture_output=True, text=True, timeout=QMD_TIMEOUT,
        )
    except FileNotFoundError:
        return []   # qmd not installed
    except subprocess.TimeoutExpired:
        return []

    if r.returncode != 0:
        return []

    return _parse_json_results(r.stdout)


_QMD_URI_PREFIX = "qmd://engineering/"


def _parse_json_results(output: str) -> list[str]:
    """Parse qmd --json output into absolute file paths, filtering archive entries."""
    try:
        results = json.loads(output)
    except json.JSONDecodeError:
        return []

    if not isinstance(results, list):
        return []

    paths = []
    for item in results:
        uri = item.get("file", "")
        if not uri.startswith(_QMD_URI_PREFIX):
            continue
        abs_path = str(ENGINEERING_DIR / uri[len(_QMD_URI_PREFIX):])
        if "/archive/" in abs_path:
            continue
        if Path(abs_path).exists():
            paths.append(abs_path)

    return paths


# ─── Agent adapters ───────────────────────────────────────────────────────────

def _extract_prompt(payload: dict) -> str:
    """Return the user's prompt text from the hook payload."""
    for key in ("prompt", "user_prompt", "message", "query"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _emit_claude(context: str) -> None:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                             "additionalContext": context}}))


def _emit_cursor(context: str) -> None:
    # Cursor permission-gating hooks must include 'permission: allow'.
    print(json.dumps({"permission": "allow", "additionalContext": context}))


def _allow_cursor() -> None:
    """Emit the bare Cursor permission grant used on every no-op exit path."""
    print(json.dumps({"permission": "allow"}))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=["claude", "cursor"], default="claude",
                        help="Agent runtime whose hook payload format to expect")
    args = parser.parse_args()

    try:
        payload = json.load(sys.stdin)
    except Exception:
        if args.agent == "cursor":
            _allow_cursor()
        sys.exit(0)

    prompt = _extract_prompt(payload)

    if not prompt or not ENGINEERING_DIR.exists():
        if args.agent == "cursor":
            _allow_cursor()
        sys.exit(0)

    keywords = extract_keywords(prompt)
    if not keywords:
        if args.agent == "cursor":
            _allow_cursor()
        sys.exit(0)

    paths = query_knowledge(" ".join(keywords))
    if not paths:
        if args.agent == "cursor":
            _allow_cursor()
        sys.exit(0)

    bullets   = "\n".join(f"  - {p}" for p in paths)
    key_label = ", ".join(keywords[:5])
    context = (
        f"[Memory probe — keywords: {key_label}]\n"
        f"These knowledge files scored above threshold for this prompt:\n"
        f"{bullets}\n"
        f"Read them if they bear on the request before responding."
    )

    if args.agent == "cursor":
        _emit_cursor(context)
    else:
        _emit_claude(context)


if __name__ == "__main__":
    main()
