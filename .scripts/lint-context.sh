#!/usr/bin/env bash
# Lint Claude Code context files (agents, commands).
# When called as a PostToolUse hook, reads file path from stdin JSON.
# When called directly with no stdin, runs full lint.
#
# Usage:
#   As hook:  piped JSON with tool_input.file_path on stdin
#   Direct:   scripts/lint-context.sh          (full scan)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Ensure symlinks exist for cclint discovery
# Note: .claude/commands is now a symlink to context/commands (no nested symlink needed)
# Only .claude/agents still needs the internal symlink since it's a directory
[ -d .claude/agents ] && [ ! -L .claude/agents/_context-agents ] &&
  ln -sfn "$ROOT/context/agents" .claude/agents/_context-agents

# --- Hook mode: check single file from stdin ---
if [ -t 0 ]; then
  # No stdin (interactive terminal) — run full lint below
  FILE=""
else
  INPUT=$(cat)
  FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null || true)
fi

if [ "${FILE:-}" != "" ]; then
  # Only lint .md files in agent/command directories
  case "$FILE" in
    *agents/*.md | *commands/*.md)
      # Skip README/TODO
      case "$(basename "$FILE")" in
        README.md | TODO.md) exit 0 ;;
      esac
      # Check for frontmatter (must start with ---)
      if [ -f "$FILE" ] && ! head -1 "$FILE" | grep -q '^---$'; then
        echo "LINT ERROR: $FILE is missing YAML frontmatter (must start with ---)"
        echo "  Agents require: name, description"
        echo "  Commands require: description"
        exit 1
      fi
      ;;
  esac
  exit 0
fi

# --- Full lint mode ---
ERRORS=0

echo "Linting agents..."
if ! npx @carlrannaberg/cclint agents --follow-symlinks --fail-on error --quiet 2>&1; then
  ERRORS=$((ERRORS + 1))
fi

echo "Linting commands..."
if ! npx @carlrannaberg/cclint commands --follow-symlinks --fail-on error --quiet 2>&1; then
  ERRORS=$((ERRORS + 1))
fi

# Check for .md files without frontmatter in agent directories
echo "Checking frontmatter coverage..."
for dir in .claude/agents context/agents; do
  [ -d "$dir" ] || continue
  find "$dir" -name '*.md' \
    -not -name 'README.md' -not -name 'TODO.md' -not -name '.notes.md' \
    -not -name 'prompt.md' \
    -not -path '*/subagents/*' \
    -not -path '*/skill-agents-common/*' \
    -not -path '*/01-*' -not -path '*/02-*' -not -path '*/03-*' \
    -not -path '*/04-*' -not -path '*/05-*' -not -path '*/06-*' \
    -not -path '*/07-*' -not -path '*/08-*' -not -path '*/09-*' \
    -not -path '*/10-*' | while read -r f; do
    real=$(realpath "$f" 2>/dev/null || echo "$f")
    if ! head -1 "$real" | grep -q '^---$'; then
      echo "  MISSING FRONTMATTER: $f"
      ERRORS=$((ERRORS + 1))
    fi
  done
done

if [ "$ERRORS" -gt 0 ]; then
  echo "Lint failed with $ERRORS issue(s)"
  exit 1
fi

echo "All context files pass lint."
