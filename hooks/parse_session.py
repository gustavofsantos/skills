#!/usr/bin/env python3
"""
parse_session.py — Session log builder

Called by PostToolUse and Stop hooks via hooks.json.
Reads new JSONL entries since last cursor position, runs a MapReduce
pipeline to pair tool_use/tool_result entries, and appends structured
log entries to ~/engineering/sessions/<date>-<session-id>.md.

Usage (hooks.json):
  PostToolUse: python3 .../parse_session.py
  Stop:        python3 .../parse_session.py --finalize

NOTE: The JSONL format is inferred from Anthropic's Messages API shape
as used by Claude Code. Validate against a real session file at
~/.claude/projects/<hash>/conversations/ before deploying.
Run with --dump-raw <session-id> to inspect without writing anything.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict
import subprocess

ENGINEERING_DIR = Path.home() / "engineering"
SESSIONS_DIR    = ENGINEERING_DIR / "sessions"
DEBUG_LOG       = SESSIONS_DIR / ".parse-debug.log"


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--finalize",  action="store_true",
                        help="Mark session complete (called by Stop hook)")
    parser.add_argument("--dump-raw", metavar="SESSION_ID",
                        help="Print raw JSONL entries for a session and exit")
    args = parser.parse_args()

    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    if args.dump_raw:
        dump_raw(args.dump_raw)
        return

    payload = load_hook_payload()
    session_id = payload.get("session_id", "")
    if not session_id:
        sys.exit(0)

    project = payload.get("cwd", os.getcwd())
    jsonl_path = find_jsonl(session_id)
    if not jsonl_path:
        debug(f"JSONL not found for session {session_id}")
        sys.exit(0)

    state   = load_state(session_id)
    cursor  = state.get("cursor", 0)

    raw = read_from_cursor(jsonl_path, cursor)
    if not raw:
        if args.finalize:
            finalize(session_id, state)
        sys.exit(0)

    mapped  = map_entries(raw)
    reduced = reduce_records(mapped)

    if reduced:
        session_file = get_or_create_session_file(session_id, state, project)
        append_log(session_file, reduced)

    state["cursor"] = raw[-1][0] + 1
    if args.finalize:
        state["complete"] = True
    save_state(session_id, state)


# ---------------------------------------------------------------------------
# JSONL location
# ---------------------------------------------------------------------------

def find_jsonl(session_id: str) -> Path | None:
    """Search ~/.claude/ for the JSONL transcript of this session.

    Claude Code stores sessions at paths like:
      ~/.claude/projects/<hash>/conversations/<session-id>.jsonl
    The exact structure may vary — fd search covers all variants.
    """
    claude_dir = Path.home() / ".claude"
    if not claude_dir.exists():
        return None

    # Try fd first (faster); fall back to find
    for cmd in [
        ["fd", "-t", "f", session_id, str(claude_dir)],
        ["find", str(claude_dir), "-type", "f", "-name", f"*{session_id}*"],
    ]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            matches = [p for p in result.stdout.strip().split("\n")
                       if p.endswith(".jsonl") and session_id in p]
            if matches:
                return Path(matches[0])
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def load_state(session_id: str) -> dict:
    f = SESSIONS_DIR / f".state-{session_id}.json"
    if f.exists():
        try:
            return json.loads(f.read_text())
        except Exception:
            pass
    return {"cursor": 0, "session_file": None, "complete": False}


def save_state(session_id: str, state: dict) -> None:
    f = SESSIONS_DIR / f".state-{session_id}.json"
    f.write_text(json.dumps(state, indent=2))


def finalize(session_id: str, state: dict) -> None:
    state["complete"] = True
    save_state(session_id, state)
    if sf := state.get("session_file"):
        path = Path(sf)
        if path.exists():
            txt = path.read_text()
            txt = txt.replace("complete: false", "complete: true", 1)
            path.write_text(txt)


# ---------------------------------------------------------------------------
# JSONL reading
# ---------------------------------------------------------------------------

def read_from_cursor(jsonl_path: Path, cursor: int) -> list[tuple[int, dict]]:
    entries = []
    with open(jsonl_path) as f:
        for idx, line in enumerate(f):
            if idx < cursor:
                continue
            line = line.strip()
            if not line:
                continue
            try:
                entries.append((idx, json.loads(line)))
            except json.JSONDecodeError as e:
                debug(f"JSON decode error at line {idx}: {e}")
    return entries


# ---------------------------------------------------------------------------
# MAP phase
# ---------------------------------------------------------------------------

def map_entries(raw: list[tuple[int, dict]]) -> list[dict]:
    """
    Emit typed records from raw JSONL entries.

    Expected JSONL shapes (based on Anthropic Messages API):

    User text turn:
      {"type": "user", "message": {"role": "user", "content": "text"}, "timestamp": "..."}

    User turn carrying tool results:
      {"type": "user", "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "toolu_...", "content": "...", "is_error": false}
      ]}, "timestamp": "..."}

    Assistant text + tool call turn:
      {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "text", "text": "..."},
        {"type": "tool_use", "id": "toolu_...", "name": "Bash", "input": {"command": "..."}}
      ]}, "timestamp": "..."}

    Adjust the field names below if real JSONL differs.
    """
    records = []

    for idx, entry in raw:
        ts  = entry.get("timestamp", "")
        msg = entry.get("message", entry)  # some formats inline the message fields
        role    = msg.get("role", "")
        content = msg.get("content", "")

        if role == "user":
            if isinstance(content, str) and content.strip():
                records.append(_user_record(content, idx, ts))
            elif isinstance(content, list):
                for block in content:
                    btype = block.get("type", "")
                    if btype == "tool_result":
                        records.append(_tool_result_record(block, idx, ts))
                    elif btype == "text" and block.get("text", "").strip():
                        records.append(_user_record(block["text"], idx, ts))

        elif role == "assistant":
            if isinstance(content, str) and content.strip():
                records.append(_agent_record(content, idx, ts))
            elif isinstance(content, list):
                for block in content:
                    btype = block.get("type", "")
                    if btype == "text" and block.get("text", "").strip():
                        records.append(_agent_record(block["text"], idx, ts))
                    elif btype == "tool_use":
                        records.append(_tool_call_record(block, idx, ts))

    return records


def _user_record(text: str, idx: int, ts: str) -> dict:
    return {"kind": "user", "text": text.strip(), "idx": idx, "timestamp": ts}


def _agent_record(text: str, idx: int, ts: str) -> dict:
    return {"kind": "agent", "text": text.strip(), "idx": idx, "timestamp": ts}


def _tool_call_record(block: dict, idx: int, ts: str) -> dict:
    name  = block.get("name", "Unknown")
    inp   = block.get("input", {})
    return {
        "kind":        "tool_call",
        "tool_use_id": block.get("id", ""),
        "tool":        name,
        "input":       _format_tool_input(name, inp),
        "idx":         idx,
        "timestamp":   ts,
    }


def _tool_result_record(block: dict, idx: int, ts: str) -> dict:
    is_error = block.get("is_error", False)
    content  = block.get("content", "")
    return {
        "kind":        "tool_result",
        "tool_use_id": block.get("tool_use_id", ""),
        "exit_code":   _extract_exit_code(content, is_error),
        "idx":         idx,
        "timestamp":   ts,
    }


def _format_tool_input(name: str, inp: dict) -> str:
    """Return only the meaningful part of the tool input — never the output."""
    if name == "Bash":
        return inp.get("command", "")
    if name in ("Read", "Write", "Edit", "MultiEdit"):
        return inp.get("file_path", inp.get("path", ""))
    if name == "Glob":
        return inp.get("pattern", "")
    if name == "Grep":
        return f"{inp.get('pattern', '')} {inp.get('path', '')}".strip()
    # Fallback: first string value found, truncated
    for v in inp.values():
        if isinstance(v, str):
            return v[:120]
    return json.dumps(inp)[:120]


def _extract_exit_code(content, is_error: bool) -> int | str:
    if is_error:
        return 1
    # Claude Code includes exit code in the tool_result content.
    # Common formats: "Exit code: 0" or trailing "\nexit_code=0".
    # Adjust pattern if your JSONL uses a different convention.
    if isinstance(content, str):
        for line in reversed(content.splitlines()):
            l = line.strip().lower()
            if l.startswith("exit code:"):
                try:
                    return int(l.split(":", 1)[1].strip())
                except ValueError:
                    pass
            if l.startswith("exit_code="):
                try:
                    return int(l.split("=", 1)[1].strip())
                except ValueError:
                    pass
    return 0


# ---------------------------------------------------------------------------
# REDUCE phase
# ---------------------------------------------------------------------------

def reduce_records(mapped: list[dict]) -> list[dict]:
    """
    Merge tool_call + tool_result pairs by tool_use_id.
    Everything else passes through unchanged.
    Sort the result by original JSONL line index.
    """
    tool_calls   = {}   # tool_use_id → record
    tool_results = {}   # tool_use_id → record
    others       = []

    for r in mapped:
        if r["kind"] == "tool_call":
            tool_calls[r["tool_use_id"]] = r
        elif r["kind"] == "tool_result":
            tool_results[r["tool_use_id"]] = r
        else:
            others.append(r)

    merged_tools = []
    for uid, call in tool_calls.items():
        result = tool_results.get(uid, {})
        merged_tools.append({
            "kind":      "tool",
            "tool":      call["tool"],
            "input":     call["input"],
            "exit_code": result.get("exit_code", "?"),
            "idx":       call["idx"],
            "timestamp": call["timestamp"],
        })

    return sorted(others + merged_tools, key=lambda r: r["idx"])


# ---------------------------------------------------------------------------
# FORMAT phase
# ---------------------------------------------------------------------------

def format_records(records: list[dict]) -> str:
    parts = []

    for r in records:
        ts  = _fmt_ts(r.get("timestamp", ""))
        idx = r["idx"]
        header = f"[{ts}] [idx:{idx}]"

        if r["kind"] == "user":
            lines = [header, "Actor: User"]
            for line in r["text"].splitlines():
                lines.append(f"> {line}")

        elif r["kind"] == "agent":
            lines = [header, "Actor: Agent"]
            for line in r["text"].splitlines():
                lines.append(f"> {line}")

        elif r["kind"] == "tool":
            tool  = r["tool"]
            inp   = r["input"]
            code  = r["exit_code"]

            if tool == "Bash":
                lines = [
                    header,
                    "Tool call: Bash",
                    "```",
                    inp,
                    "```",
                    f"> exit code: {code}",
                ]
            else:
                lines = [
                    header,
                    f"Tool call: {tool}",
                    f"> {inp}",
                ]
                if code != "?":
                    lines.append(f"> exit code: {code}")
        else:
            continue

        parts.append("\n".join(lines))

    return "\n\n---\n\n".join(parts) + "\n\n---\n\n" if parts else ""


def _fmt_ts(ts: str) -> str:
    """Normalize timestamp to 'YYYY-MM-DD HH:MM:SS'."""
    return ts[:19].replace("T", " ") if ts else "??:??:??"


# ---------------------------------------------------------------------------
# Session file
# ---------------------------------------------------------------------------

def get_or_create_session_file(session_id: str, state: dict, project: str) -> Path:
    if sf := state.get("session_file"):
        p = Path(sf)
        if p.exists():
            return p

    date_str     = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    short_id     = session_id[:8]
    session_file = SESSIONS_DIR / f"{date_str}-{short_id}.md"

    session_file.write_text(
        f"---\n"
        f"session_id: {session_id}\n"
        f"date: {date_str}\n"
        f"project: {project}\n"
        f"complete: false\n"
        f"---\n\n"
    )

    state["session_file"] = str(session_file)
    return session_file


def append_log(session_file: Path, records: list[dict]) -> None:
    formatted = format_records(records)
    if formatted:
        with open(session_file, "a") as f:
            f.write(formatted)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def load_hook_payload() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def debug(msg: str) -> None:
    try:
        with open(DEBUG_LOG, "a") as f:
            ts = datetime.now(timezone.utc).isoformat()
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def dump_raw(session_id: str) -> None:
    """Print raw JSONL entries for debugging. Does not modify any state."""
    path = find_jsonl(session_id)
    if not path:
        print(f"JSONL not found for session {session_id}", file=sys.stderr)
        sys.exit(1)
    print(f"Found: {path}\n")
    with open(path) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line:
                try:
                    obj = json.loads(line)
                    print(f"--- line {i} ---")
                    print(json.dumps(obj, indent=2))
                except json.JSONDecodeError:
                    print(f"--- line {i} (parse error) ---")
                    print(line)


if __name__ == "__main__":
    main()
