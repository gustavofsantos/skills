#!/usr/bin/env bash
set -euo pipefail

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Installing local Cursor plugin..."
mkdir -p "$HOME/.cursor/plugins/local"
cp -R "$PLUGIN_DIR" "$HOME/.cursor/plugins/local/gustavofsantos"
echo "Installing local Cursor plugin... OK"

