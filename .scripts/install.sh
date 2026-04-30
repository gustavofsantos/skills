#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="$(pwd)"

echo "Installing custom skills..."
mkdir -p "$HOME/.claude/skills"
mkdir -p "$HOME/.cursor/skills"
mkdir -p "$HOME/.agents/skills"
for skill in "$DOTFILES_DIR"/skills/*/; do
  [ -d "$skill" ] || continue
  name=$(basename "$skill")
  # Claude Code and Gemini CLI (agents): symlinks work
  ln -sfn "$skill" "$HOME/.claude/skills/$name"
  ln -sfn "$skill" "$HOME/.agents/skills/$name"
  # Cursor: symlinks are broken for global skills (known bug), use copies
  rm -rf "$HOME/.cursor/skills/$name"
  cp -R "$skill" "$HOME/.cursor/skills/$name"
done
echo "Installing custom skills... OK"
