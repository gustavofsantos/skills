#!/usr/bin/env python3
"""
parse_session.py — Session log builder

Supports two agent runtimes, selected via --agent:

  --agent claude  (default)
    Called by Claude Code PostToolUse and Stop hooks via hooks.json.
    Reads new JSONL entries since last cursor position, runs a MapReduce
    pipeline to pair tool_use/tool_result entries, and appends structured
    log entries to ~/engineering/sessions/<date>-<session-id>.md.

    Sessions spawned by a parent agent (subagents) are tagged with
    `subagent: true` in their frontmatter. The dream consolidation pass
    processes them at reduced depth to avoid bloating the work list.

  --agent cursor
    Called by Cursor stop and afterFileEdit hooks.  On stop, reads the
    full JSONL transcript (transcript_path from the hook payload) and
    applies the same MapReduce pipeline as the Claude adapter, giving
    complete session coverage.  afterFileEdit events capture edit_diff
    signal that is stored in state and merged into the transcript pass.

Usage (Claude Code hooks.json):
  PostToolUse: python3 .../parse_session.py --agent claude
  Stop:        python3 .../parse_session.py --agent claude --finalize

Usage (Cursor hooks.json):
  afterFileEdit:        python3 .../parse_session.py --agent cursor
  beforeShellExecution: python3 .../parse_session.py --agent cursor
  stop:                 python3 .../parse_session.py --agent cursor --finalize

Cursor hooks that require a permission response (beforeShellExecution,
beforeMCPExecution, beforeReadFile, beforeSubmitPrompt) always receive
{"permission": "allow"} on stdout so the agent is never blocked.
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

# Cursor hook types that require a permission response on stdout.
CURSOR_PERMISSION_HOOKS = {
    "beforeShellExecution",
    "beforeMCPExecution",
    "beforeReadFile",
    "beforeSubmitPrompt",
}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--finalize", action="store_true",
                        help="Mark session complete (called by Stop/stop hook)")
    parser.add_argument("--dump-raw", metavar="SESSION_ID",
                        help="Print raw JSONL entries for a session and exit (claude only)")
    parser.add_argument("--agent", choices=["claude", "cursor"], default="claude",
                        help="Agent runtime whose hook payload format to expect")
    args = parser.parse_args()

    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    if args.dump_raw:
        dump_raw(args.dump_raw)
        return

    payload = load_hook_payload()

    if args.agent == "cursor":
        main_cursor(args, payload)
    else:
        main_claude(args, payload)


# ---------------------------------------------------------------------------
# Claude Code adapter
# ---------------------------------------------------------------------------

def main_claude(args, payload):
    """Read the JSONL transcript and append new entries to the session log."""
    session_id = payload.get("session_id", "")
    if not session_id:
        sys.exit(0)

    # parent_session_id is present when this session was spawned by an Agent
    # tool call. Tag the session file so dream can skip deep-mining it.
    is_subagent = bool(payload.get("parent_session_id"))

    project = payload.get("cwd", os.getcwd())
    jsonl_path = find_jsonl(session_id)
    if not jsonl_path:
        debug(f"JSONL not found for session {session_id}")
        sys.exit(0)

    state  = load_state(session_id)
    cursor = state.get("cursor", 0)

    raw = read_from_cursor(jsonl_path, cursor)
    if not raw:
        if args.finalize:
            finalize(session_id, state)
        sys.exit(0)

    mapped  = map_entries(raw)
    reduced = reduce_records(mapped)

    if reduced:
        session_file = get_or_create_session_file(
            session_id, state, project, is_subagent=is_subagent
        )
        append_log(session_file, reduced)

    state["cursor"] = raw[-1][0] + 1
    if args.finalize:
        state["complete"] = True
    save_state(session_id, state)


# ---------------------------------------------------------------------------
# Cursor adapter
# ---------------------------------------------------------------------------

def main_cursor(args, payload):
    """Handle Cursor hook events.

    On stop: read the full JSONL transcript via transcript_path (if present)
    and run the same MapReduce pipeline as the Claude adapter. Edit-diff data
    accumulated during earlier afterFileEdit events is merged in.

    On afterFileEdit: compute and store edit_diff in state for later merge.

    Other events: emit permission response only.
    """
    event           = payload.get("hook_event_name", "")
    workspace_roots = payload.get("workspace_roots", [])
    project         = workspace_roots[0] if workspace_roots else os.getcwd()
    conversation_id = payload.get("conversation_id") or payload.get("generation_id", "")
    ts              = datetime.now(timezone.utc).isoformat()

    if not conversation_id:
        debug(f"Cursor hook fired with no conversation_id: event={event}")
        _cursor_respond(event)
        sys.exit(0)

    state = load_state(conversation_id)

    is_stop = args.finalize or event == "stop"

    if event == "afterFileEdit":
        # Accumulate edit_diff per file for later merge into transcript pass.
        file_path = payload.get("file_path", "")
        if file_path:
            diff_summary = _compute_edit_diff(file_path)
            edits = state.setdefault("cursor_edits", [])
            edits.append({"file_path": file_path, "edit_diff": diff_summary, "timestamp": ts})
            save_state(conversation_id, state)

    elif is_stop:
        transcript_path = payload.get("transcript_path", "")
        if transcript_path and Path(transcript_path).exists():
            _cursor_process_full_transcript(
                conversation_id, state, project, transcript_path
            )
        else:
            # No transcript available — fall back to a lightweight stop record.
            record = _cursor_stop_record(payload, ts)
            if record:
                session_file = get_or_create_session_file(conversation_id, state, project)
                append_log(session_file, [record])
        finalize(conversation_id, state)
        _cursor_respond(event)
        return

    elif event not in CURSOR_PERMISSION_HOOKS:
        # Non-edit, non-stop, non-permission event — no log record needed.
        save_state(conversation_id, state)

    _cursor_respond(event)


def _cursor_process_full_transcript(
    conversation_id: str, state: dict, project: str, transcript_path: str
) -> None:
    """Read the Cursor JSONL transcript and apply MapReduce, then append to session log.

    Cursor JSONL format differs from Claude Code in two ways:
    - role lives at the top level of each entry, not inside 'message'
    - tool results are not emitted as separate 'user' entries; only tool_use
      blocks appear (exit codes remain unknown: '?')

    Edit-diff data stored by earlier afterFileEdit events is merged in by
    matching file paths that appear as tool call inputs.
    """
    raw = _cursor_read_transcript(transcript_path)
    if not raw:
        return

    mapped  = map_entries(raw, cursor_format=True)
    reduced = reduce_records(mapped)

    # Merge accumulated edit_diff into matching tool records.
    edit_index = {e["file_path"]: e["edit_diff"]
                  for e in state.get("cursor_edits", [])}
    if edit_index:
        for record in reduced:
            if record.get("kind") == "tool" and record.get("tool") in (
                "Edit", "Write", "StrReplace"
            ):
                inp = record.get("input", "")
                if inp in edit_index:
                    record["edit_diff"] = edit_index[inp]

    if reduced:
        session_file = get_or_create_session_file(conversation_id, state, project)
        append_log(session_file, reduced)


def _cursor_read_transcript(transcript_path: str) -> list[tuple[int, dict]]:
    """Read Cursor JSONL transcript from disk; return (line_index, entry) pairs."""
    entries = []
    try:
        with open(transcript_path) as f:
            for idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append((idx, json.loads(line)))
                except json.JSONDecodeError as e:
                    debug(f"Cursor transcript JSON error at line {idx}: {e}")
    except OSError as e:
        debug(f"Cannot read Cursor transcript {transcript_path}: {e}")
    return entries


def _cursor_stop_record(payload: dict, ts: str) -> dict | None:
    """Fallback stop record when no transcript_path is available."""
    stats = {k: payload.get(k)
             for k in ("input_tokens", "output_tokens", "cache_read_tokens",
                       "cache_write_tokens", "loop_count")
             if payload.get(k) is not None}
    if not stats:
        return None
    return {
        "kind":      "agent",
        "text":      f"[session ended] {json.dumps(stats)}",
        "idx":       0,
        "timestamp": ts,
    }


def _compute_edit_diff(file_path: str) -> dict:
    """
    Runs `git diff HEAD -- <file_path>` to capture what the user changed
    relative to the last committed (agent-written) state.

    Returns {"signal": "unknown"} on any failure — never raises.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD", "--", file_path],
            capture_output=True, text=True, timeout=5,
            cwd=os.path.dirname(os.path.abspath(file_path)) or "."
        )
        diff = result.stdout
        if not diff:
            return {"signal": "golden", "lines_added": 0, "lines_removed": 0, "edit_ratio": 0.0}

        added   = sum(1 for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
        removed = sum(1 for l in diff.splitlines() if l.startswith("-") and not l.startswith("---"))
        changed = added + removed

        try:
            total = sum(1 for _ in open(file_path))
        except Exception:
            total = max(changed, 1)

        ratio = min(changed / max(total, 1), 1.0)

        if ratio <= 0.10:
            signal = "golden"
        elif ratio <= 0.40:
            signal = "moderate"
        else:
            signal = "heavy_rewrite"

        return {
            "signal":        signal,
            "lines_added":   added,
            "lines_removed": removed,
            "edit_ratio":    round(ratio, 3),
        }
    except Exception:
        return {"signal": "unknown"}


def _cursor_respond(event: str) -> None:
    """Print the required JSON response for permission-gating hooks."""
    if event in CURSOR_PERMISSION_HOOKS:
        print(json.dumps({"permission": "allow"}))


# ---------------------------------------------------------------------------
# JSONL location (Claude Code only)
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


def _compute_quality_signal(session_file: Path) -> str:
    """
    Heuristic quality score for a finalized session.
    Scans the already-formatted session markdown for signal strings.
    Returns "high" | "medium" | "low".
    """
    try:
        text = session_file.read_text()
    except Exception:
        return "medium"

    lines = text.splitlines()
    success_count    = 0
    failure_count    = 0
    explicit_good    = 0
    explicit_bad     = 0
    golden_count     = 0
    heavy_count      = 0
    correction_count = 0

    prev_actor = None
    for line in lines:
        ll = line.strip().lower()
        if ll.startswith("> exit code:"):
            code_str = ll.split(":", 1)[1].strip()
            try:
                code = int(code_str)
                if code == 0:
                    success_count += 1
                else:
                    failure_count += 1
            except ValueError:
                pass
        if "[feedback:good]" in ll:
            explicit_good += 1
        if "[feedback:bad]" in ll or "[feedback:wrong]" in ll:
            explicit_bad += 1
        if "edit_diff: golden" in ll:
            golden_count += 1
        if "edit_diff: heavy_rewrite" in ll:
            heavy_count += 1
        # Count user turns immediately following agent turns as correction proxy
        if "actor: agent" in ll:
            prev_actor = "agent"
        elif "actor: user" in ll:
            if prev_actor == "agent":
                correction_count += 1
            prev_actor = "user"

    base_ratio         = success_count / max(1, success_count + failure_count)
    correction_penalty = min(correction_count, 5) / 5 * 0.30
    score = (base_ratio
             - correction_penalty
             + explicit_good  * 0.15
             - explicit_bad   * 0.20
             + golden_count   * 0.10
             - heavy_count    * 0.15)
    score = max(0.0, min(1.0, score))

    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def finalize(session_id: str, state: dict) -> None:
    state["complete"] = True
    save_state(session_id, state)
    if sf := state.get("session_file"):
        path = Path(sf)
        if path.exists():
            txt = path.read_text()
            txt = txt.replace("complete: false", "complete: true", 1)
            try:
                quality = _compute_quality_signal(path)
                txt = txt.replace("complete: true\n---", f"complete: true\nquality_signal: {quality}\n---", 1)
            except Exception:
                pass
            path.write_text(txt)


# ---------------------------------------------------------------------------
# JSONL reading (Claude Code only)
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

def map_entries(raw: list[tuple[int, dict]], cursor_format: bool = False) -> list[dict]:
    """
    Emit typed records from raw JSONL entries.

    Handles two JSONL layouts:

    Claude Code (cursor_format=False):
      {"type": "user"|"assistant", "message": {"role": "...", "content": [...]}, "timestamp": "..."}

    Cursor (cursor_format=True):
      {"role": "user"|"assistant", "message": {"content": [...]}}
      Role lives at the top level; tool results are not emitted as separate
      entries so tool records carry exit_code "?" and are not reduced.
    """
    records = []

    for idx, entry in raw:
        ts  = entry.get("timestamp", "")
        msg = entry.get("message", entry)

        # Claude Code puts role inside message; Cursor puts it at the top level.
        role = msg.get("role", "") or entry.get("role", "")
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
    record = {"kind": "user", "text": text.strip(), "idx": idx, "timestamp": ts}
    stripped = text.strip().lower()
    if stripped.startswith("/good"):
        record["feedback_tag"] = "good"
    elif stripped.startswith("/bad"):
        record["feedback_tag"] = "bad"
    elif stripped.startswith("/wrong"):
        record["feedback_tag"] = "wrong"
    return record


def _agent_record(text: str, idx: int, ts: str) -> dict:
    return {"kind": "agent", "text": text.strip(), "idx": idx, "timestamp": ts}


def _tool_call_record(block: dict, idx: int, ts: str) -> dict:
    name  = block.get("name", "Unknown")
    inp   = block.get("input", {})
    record = {
        "kind":        "tool_call",
        "tool_use_id": block.get("id", ""),
        "tool":        name,
        "input":       _format_tool_input(name, inp),
        "idx":         idx,
        "timestamp":   ts,
    }
    # For Agent tool calls, capture subagent metadata for richer log entries.
    if name == "Agent":
        subagent_type = inp.get("subagent_type", "general-purpose")
        record["subagent_type"] = subagent_type
        record["background"]    = bool(inp.get("run_in_background", False))
    return record


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
    if name in ("Bash", "Shell"):
        return inp.get("command", "")
    if name in ("Read", "Write", "Edit", "MultiEdit"):
        return inp.get("file_path", inp.get("path", ""))
    if name == "StrReplace":
        return inp.get("path", inp.get("file_path", ""))
    if name == "Glob":
        return inp.get("pattern", "")
    if name == "Grep":
        return f"{inp.get('pattern', '')} {inp.get('path', '')}".strip()
    if name == "Agent":
        subagent_type = inp.get("subagent_type", "general-purpose")
        description   = inp.get("description", "")
        suffix = " [bg]" if inp.get("run_in_background") else ""
        return f"[{subagent_type}] {description}{suffix}"[:120]
    if name == "AwaitShell":
        return f"[await task:{inp.get('task_id', '')}]"
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
    Tool calls with no matching result keep exit_code "?" (normal for Cursor
    transcripts which do not emit tool_result entries).
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
        merged = {
            "kind":      "tool",
            "tool":      call["tool"],
            "input":     call["input"],
            "exit_code": result.get("exit_code", "?"),
            "idx":       call["idx"],
            "timestamp": call["timestamp"],
        }
        if "subagent_type" in call:
            merged["subagent_type"] = call["subagent_type"]
            merged["background"]    = call.get("background", False)
        merged_tools.append(merged)

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
            if r.get("feedback_tag"):
                lines.append(f"> [FEEDBACK:{r['feedback_tag'].upper()}]")

        elif r["kind"] == "agent":
            lines = [header, "Actor: Agent"]
            for line in r["text"].splitlines():
                lines.append(f"> {line}")

        elif r["kind"] == "tool":
            tool  = r["tool"]
            inp   = r["input"]
            code  = r["exit_code"]

            if tool in ("Bash", "Shell"):
                lines = [
                    header,
                    f"Tool call: {tool}",
                    "```",
                    inp,
                    "```",
                    f"> exit code: {code}",
                ]
            elif tool == "Agent":
                subagent_type = r.get("subagent_type", "general-purpose")
                bg_flag = " [background]" if r.get("background") else ""
                lines = [
                    header,
                    f"Tool call: Agent [{subagent_type}]{bg_flag}",
                    f"> {inp}",
                ]
                if code != "?":
                    lines.append(f"> exit code: {code}")
            else:
                lines = [
                    header,
                    f"Tool call: {tool}",
                    f"> {inp}",
                ]
                if code != "?":
                    lines.append(f"> exit code: {code}")
            if diff := r.get("edit_diff"):
                lines.append(f"> edit_diff: {diff.get('signal', 'unknown')} "
                             f"(ratio={diff.get('edit_ratio', '?')})")
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

def get_or_create_session_file(
    session_id: str, state: dict, project: str, is_subagent: bool = False
) -> Path:
    if sf := state.get("session_file"):
        p = Path(sf)
        if p.exists():
            return p

    date_str     = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    short_id     = session_id[:8]
    session_file = SESSIONS_DIR / f"{date_str}-{short_id}.md"

    frontmatter = (
        f"---\n"
        f"session_id: {session_id}\n"
        f"date: {date_str}\n"
        f"project: {project}\n"
        f"complete: false\n"
    )
    if is_subagent:
        frontmatter += "subagent: true\n"
    frontmatter += "---\n\n"

    session_file.write_text(frontmatter)

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
