#!/usr/bin/env bash
# Sync every skill in this repo into each tool's personal skills directory.
# Default: symlink (repo edits are reflected immediately).
#
# Usage: scripts/sync.sh [--copy] [--clean]
#   --copy    copy instead of symlinking (use where symlinks aren't permitted)
#   --clean   remove existing links/dirs for this repo's skills before syncing
set -euo pipefail

MODE="link"
CLEAN=0
for arg in "$@"; do
  case "$arg" in
    --copy) MODE="copy" ;;
    --clean) CLEAN=1 ;;
    *) echo "unknown option: $arg" >&2; exit 1 ;;
  esac
done

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGETS=(
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.agents/skills"
  "$HOME/.gemini/antigravity-cli/skills"
)

# Collect skill dirs: plugins/*/skills/*/ that contain a SKILL.md
SKILLS=()
for d in "$REPO"/plugins/*/skills/*/; do
  [ -f "${d}SKILL.md" ] || continue
  SKILLS+=("${d%/}")
done
[ ${#SKILLS[@]} -gt 0 ] || { echo "no skills found under plugins/*/skills/*" >&2; exit 1; }

for target in "${TARGETS[@]}"; do
  mkdir -p "$target"
  for src in "${SKILLS[@]}"; do
    name="$(basename "$src")"
    dest="$target/$name"
    if [ $CLEAN -eq 1 ] || [ -e "$dest" ] || [ -L "$dest" ]; then
      rm -rf "$dest"
    fi
    if [ "$MODE" = "copy" ]; then
      cp -R "$src" "$dest"
    else
      ln -s "$src" "$dest"
    fi
  done
  echo "synced ${#SKILLS[@]} skill(s) -> $target ($MODE)"
done
