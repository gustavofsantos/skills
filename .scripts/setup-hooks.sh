#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_SRC="$REPO_ROOT/.scripts/hooks"
HOOKS_DST="$REPO_ROOT/.git/hooks"

echo "Installing git hooks..."
for hook in "$HOOKS_SRC"/*; do
  [ -f "$hook" ] || continue
  name=$(basename "$hook")
  cp "$hook" "$HOOKS_DST/$name"
  chmod +x "$HOOKS_DST/$name"
  echo "  installed $name"
done
echo "Installing git hooks... OK"

# echo "Installing git-ai CLI..."
# if command -v git-ai &>/dev/null; then
#   echo "  git-ai already installed, skipping"
# else
#   curl -sSL https://usegitai.com/install.sh | bash
#   echo "Installing git-ai CLI... OK"
# fi
