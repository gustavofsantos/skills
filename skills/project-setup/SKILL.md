---
description: >
  Installs or updates provenance git hooks in the current project's .git/hooks/.
  Safe to re-run — merges into existing hook scripts using markers, never removes
  unrelated content.
when_to_use: >
  Use when entering a new project for the first time, when the user says
  "set up this project", "instala os hooks", "configura este projeto",
  "project-setup", "install provenance hooks", or after pulling the plugin
  on a fresh clone. Also re-run after the plugin updates so newly added
  hooks land in .git/hooks/.
allowed-tools: Bash(git:*) Bash(chmod:*) Bash(python3:*)
---

# Project Setup

Installs the git hooks required by the provenance workflow into `.git/hooks/`
of the current project. Safe to run multiple times — idempotent.

---

## Preflight

Confirm this is a git repository and resolve the hooks directory:

```bash
git rev-parse --git-dir
```

If this fails, stop:
> "Not a git repository. Run this command from the root of a project."

Store the result as `GIT_DIR`. The hooks directory is `$GIT_DIR/hooks`.

Display the project name:

```bash
basename "$(git rev-parse --show-toplevel)"
```

---

## Hook injection

Apply this procedure to each of the three hooks.

### Procedure

1. Read `$GIT_DIR/hooks/<name>` — if the file does not exist, start with `"#!/bin/bash\n"`.
2. Check whether the marker `# === skills-plugin:begin ===` is present.
   - **Present** → replace the block between the markers with the new content.
   - **Absent** → append the block at the end of the existing content.
3. Write the result back to `$GIT_DIR/hooks/<name>`.
4. `chmod +x $GIT_DIR/hooks/<name>`.

Track the outcome per hook: `created`, `updated`, or `already current`.

### Marker format

```
# === skills-plugin:begin ===
<content>
# === skills-plugin:end ===
```

Use this script for the inject/replace step — pass the file path and block content as arguments:

```python
import re, sys

path  = sys.argv[1]
block = sys.argv[2]

BEGIN = "# === skills-plugin:begin ==="
END   = "# === skills-plugin:end ==="

try:
    with open(path) as f:
        content = f.read()
except FileNotFoundError:
    content = "#!/bin/bash\n"

new_block = f"{BEGIN}\n{block}\n{END}"
pattern   = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.DOTALL)

if pattern.search(content):
    replaced = pattern.sub(new_block, content)
    status   = "already current" if replaced == content else "updated"
    content  = replaced
else:
    content = content.rstrip("\n") + "\n\n" + new_block + "\n"
    status  = "created"

with open(path, "w") as f:
    f.write(content)

print(status)
```

---

### Hook: `post-rewrite`

Migrates git notes to rewritten commit hashes after rebase or amend.

Block content:

```bash
# Migrate git notes to rewritten hashes (provenance)
git notes copy --for-rewrite="$1" 2>/dev/null || true
```

After writing the hook, set `notes.rewriteRef` for this repository:

```bash
git config notes.rewriteRef "refs/notes/commits"
```

---

### Hook: `pre-push`

Consolidates all git notes from the current branch into a local namespace
(`refs/notes/branches/<branch>`) before push. Enables context recovery
after a squash merge on the remote.

Block content:

```bash
# Consolidate branch notes before push (provenance)
_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
[ "$_BRANCH" = "main" ] || [ "$_BRANCH" = "master" ] && exit 0

_BASE=$(git merge-base HEAD origin/main 2>/dev/null) || exit 0

_NOTES=$(git log "$_BASE..HEAD" --format="%H" 2>/dev/null | while read _h; do
  _n=$(git notes show "$_h" 2>/dev/null)
  [ -n "$_n" ] && printf "## %s\n%s\n\n" "$_h" "$_n"
done)

[ -n "$_NOTES" ] && \
  git notes --ref=refs/notes/branches/"$_BRANCH" add -f -m "$_NOTES" HEAD \
  2>/dev/null || true
```

---

### Hook: `post-merge`

After `git pull` or `git merge`, migrates consolidated branch notes to squash
commits that arrived on the main branch. Uses `gh` to resolve which PR
introduced each new commit. Skips silently if `gh` is not available.

Block content:

```bash
# Migrate branch notes to squash commits (provenance)
[ -f "$(git rev-parse --git-dir)/ORIG_HEAD" ] || exit 0
command -v gh &>/dev/null || exit 0

git log ORIG_HEAD..HEAD --format="%H" 2>/dev/null | while read _hash; do
  git notes show "$_hash" &>/dev/null && continue

  _branch=$(gh api "repos/:owner/:repo/commits/$_hash/pulls" \
    --jq '.[0].head.ref' 2>/dev/null)
  [ -z "$_branch" ] || [ "$_branch" = "null" ] && continue

  _note=$(git notes --ref=refs/notes/branches/"$_branch" show HEAD 2>/dev/null)
  [ -z "$_note" ] && continue

  git notes add -m "$_note" "$_hash" 2>/dev/null || true
done
```

---

## Output

```
Project setup — <project-name>

  ✓ notes.rewriteRef = refs/notes/commits   [set | already set]
  ✓ post-rewrite   [created | updated | already current]
  ✓ pre-push       [created | updated | already current]
  ✓ post-merge     [created | updated | already current]

Hooks installed in <git-dir>/hooks/.
Run /gustavofsantos:project-setup again after updating the plugin to apply changes.
```

If any step failed, say which step and what to run manually to fix it.
