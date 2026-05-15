#!/usr/bin/env bash
set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_PATH="$PLUGIN_DIR/hooks/parse_session.py"

echo "Installing local Cursor files..."
cp -R "$PLUGIN_DIR/skills/" "$HOME/.cursor/skills/"
cp -R "$PLUGIN_DIR/agents/" "$HOME/.cursor/agents/"
echo "Installing local Cursor plugin... OK"

echo "Installing Cursor hooks..."
python3 - "$HOME/.cursor/hooks.json" "$SCRIPT_PATH" <<'PYEOF'
import sys, json
from pathlib import Path

hooks_file  = Path(sys.argv[1])
script_path = sys.argv[2]

if hooks_file.exists():
    config = json.loads(hooks_file.read_text())
else:
    hooks_file.parent.mkdir(parents=True, exist_ok=True)
    config = {
        "version": 1,
        "$schema": "https://unpkg.com/cursor-hooks@latest/schema/hooks.schema.json",
        "hooks": {},
    }

config.setdefault("hooks", {})

for event, suffix in [
    ("afterFileEdit",        "--agent cursor"),
    ("stop",                 "--agent cursor --finalize"),
]:
    # Remove any stale entries from a previous install of this plugin.
    existing = [h for h in config["hooks"].get(event, [])
                if "parse_session.py" not in h.get("command", "")]
    config["hooks"][event] = existing + [{"command": f"python3 {script_path} {suffix}"}]

hooks_file.write_text(json.dumps(config, indent=2) + "\n")
print(f"  wrote {hooks_file}")
PYEOF
echo "Installing local Cursor hooks... OK"

echo "Installing local Gemini CLI files..."
mkdir -p "$HOME/.gemini/skills/"
mkdir -p "$HOME/.gemini/agents/"
# Symlink skills
for skill in "$PLUGIN_DIR/skills"/*; do
  [ -d "$skill" ] || continue
  name=$(basename "$skill")
  ln -sfn "$skill" "$HOME/.gemini/skills/$name"
done
# Symlink Gemini-specific agents
if [ -d "$PLUGIN_DIR/.gemini/agents" ]; then
  for agent in "$PLUGIN_DIR/.gemini/agents"/*; do
    [ -f "$agent" ] || continue
    name=$(basename "$agent")
    ln -sfn "$agent" "$HOME/.gemini/agents/$name"
  done
fi
echo "Installing local Gemini CLI files... OK"
