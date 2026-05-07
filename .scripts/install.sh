#!/usr/bin/env bash
set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Installing local Cursor files..."
cp -R "$PLUGIN_DIR/skills/" "$HOME/.cursor/skills/"
cp -R "$PLUGIN_DIR/commands/" "$HOME/.cursor/commands/"
cp -R "$PLUGIN_DIR/agents/" "$HOME/.cursor/agents/"
echo "Installing local Cursor plugin... OK"

