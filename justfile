set unstable := true

# Default recipe - show available commands
default:
    @just --list

# TypeScript CLI tooling
[group('tools')]
agents *args:
    @bun run packages/cli/src/bin/agents.ts {{ args }}

# Matrix review viewer
[group('tools')]
matrixng *args:
    @bun run packages/matrixng/src/bin.ts {{ args }}

# Claude Code configuration directory

CLAUDE_DIR := env("HOME") / ".claude"
EMBEDDING_MODEL := "nomic-embed-text"

# Install project dependencies (idempotent)
[group('install')]
init: _init-brew _init-bun _init-python _init-pre-commit _init-docker _init-ollama _init-db
    @echo "✓ Project initialized"

[private]
_init-brew:
    @echo "Installing Homebrew dependencies..."
    @brew bundle --quiet

[private]
_init-pre-commit:
    @echo "Installing Pre-commit Hooks..."
    @pre-commit install --install-hooks

[private]
_init-bun:
    @echo "Installing TypeScript dependencies..."
    @bun install --silent

[private]
_init-python:
    @echo "Installing Python dependencies..."
    @uv sync --quiet

[private]
_init-docker: mcp-up

[private]
_init-ollama:
    #!/usr/bin/env bash
    echo "Checking Ollama embedding model..."
    if ollama list 2>/dev/null | grep -q "{{ EMBEDDING_MODEL }}"; then
        echo "  ✓ {{ EMBEDDING_MODEL }} available"
    else
        echo "  Pulling {{ EMBEDDING_MODEL }}..."
        ollama pull "{{ EMBEDDING_MODEL }}" || echo "  ⚠ Ollama not running - will use sentence-transformers fallback"
    fi

[private]
_init-db:
    @echo "Initializing knowledge graph database..."
    @just kg-init

# Docker MCP services
[group('docker')]
mcp-up:
    @"{{ which("docker") }}" compose -f .docker/compose.yaml up -d
    @echo "✓ MCP services started"
    @echo "  Add crawl4ai to Claude: claude mcp add --transport sse crawl4ai http://localhost:11235/mcp/sse"

[group('docker')]
mcp-down:
    @"{{ which("docker") }}" compose -f .docker/compose.yaml down

[group('docker')]
mcp-logs service="crawl4ai":
    @"{{ which("docker") }}" compose -f .docker/compose.yaml logs -f "{{ service }}"

[group('docker')]
mcp-status:
    @"{{ which("docker") }}" compose -f .docker/compose.yaml ps

# Install Claude Code components to ~/.claude/
[group('install')]
install target='all':
    @just _install-{{ target }}

[private]
_install-all: _install-claude

[private]
_install-claude: _install-claude-commands _install-claude-rules _install-claude-skills _install-claude-hooks _install-claude-settings
    @echo "✓ Claude Code components installed to {{ CLAUDE_DIR }}"

[private]
_install-claude-settings:
    @echo "Installing settings..."
    @mkdir -p "{{ CLAUDE_DIR }}"
    @ln -sf "$(pwd)/settings/claude.json" "{{ CLAUDE_DIR }}/settings.json" && echo "  → ~/claude/settings.json" || true

[private]
_install-claude-commands:
    @echo "Installing commands..."
    @mkdir -p "{{ CLAUDE_DIR }}/commands"
    @for f in content/commands/*.md; do \
        [ -f "$f" ] && ln -sf "$(pwd)/$f" "{{ CLAUDE_DIR }}/commands/$(basename $f)" && echo "  → $(basename $f)"; \
    done || true

[private]
_install-claude-rules:
    @echo "Installing rules..."
    @mkdir -p "{{ CLAUDE_DIR }}/rules"
    @for f in content/rules/*.md; do \
        [ -f "$f" ] && ln -sf "$(pwd)/$f" "{{ CLAUDE_DIR }}/rules/$(basename $f)" && echo "  → $(basename $f)"; \
    done || true

[private]
_install-claude-skills:
    @echo "Installing skills..."
    @mkdir -p "{{ CLAUDE_DIR }}/skills"
    @for d in content/skills/*/; do \
        name=$(basename "$d"); \
        target="{{ CLAUDE_DIR }}/skills/$name"; \
        if [ -d "$d" ]; then \
            if [ -L "$target" ]; then \
                rm -f "$target"; \
            elif [ -d "$target" ]; then \
                rm -rf "$target"; \
            fi; \
            ln -sfn "$(pwd)/$d" "$target" && echo "  → $name/"; \
        fi; \
    done || true

[private]
_install-claude-hooks:
    @echo "Installing hooks..."
    @mkdir -p "{{ CLAUDE_DIR }}/hooks"
    @for f in content/hooks/*; do \
        [ -f "$f" ] && [ "$(basename $f)" != ".gitkeep" ] && ln -sf "$(pwd)/$f" "{{ CLAUDE_DIR }}/hooks/$(basename $f)" && echo "  → $(basename $f)"; \
    done || true

# Uninstall Claude Code components from ~/.claude/
[group('install')]
uninstall target='all':
    @just _uninstall-{{ target }}

[private]
_uninstall-all: _uninstall-claude

[private]
_uninstall-claude:
    @echo "Uninstalling Claude Code components..."
    @for f in content/commands/*.md; do \
        [ -f "$f" ] && rm -f "{{ CLAUDE_DIR }}/commands/$(basename $f)"; \
    done || true
    @for f in content/rules/*.md; do \
        [ -f "$f" ] && rm -f "{{ CLAUDE_DIR }}/rules/$(basename $f)"; \
    done || true
    @for d in content/skills/*/; do \
        [ -d "$d" ] && rm -f "{{ CLAUDE_DIR }}/skills/$(basename $d)"; \
    done || true
    @for f in content/hooks/*; do \
        [ -f "$f" ] && [ "$(basename $f)" != ".gitkeep" ] && rm -f "{{ CLAUDE_DIR }}/hooks/$(basename $f)"; \
    done || true
    @echo "✓ Claude Code components uninstalled"

# List installed Claude Code components
[group('install')]
list-claude:
    @echo "Commands:"
    @ls -la "{{ CLAUDE_DIR }}/commands/" 2>/dev/null | grep -E "\.md$" || echo "  (none)"
    @echo "\nRules:"
    @ls -la "{{ CLAUDE_DIR }}/rules/" 2>/dev/null | grep -E "\.md$" || echo "  (none)"
    @echo "\nSkills:"
    @ls -la "{{ CLAUDE_DIR }}/skills/" 2>/dev/null | grep -v "^total" | grep -v "^\." || echo "  (none)"
    @echo "\nHooks:"
    @ls -la "{{ CLAUDE_DIR }}/hooks/" 2>/dev/null | grep -v "^total" | grep -v "^\." || echo "  (none)"

# Knowledge graph operations (Python-based)

# Initialize knowledge graph database
[group('kg')]
kg-init:
    @"{{ which("uv") }}" run python packages/cli/init-db.py

# Ingest all context files into knowledge graph
[group('kg')]
kg-ingest:
    @"{{ which("uv") }}" run python packages/cli/embed.py ingest --all

# Semantic search
[group('kg')]
kg-search query:
    @"{{ which("uv") }}" run python packages/cli/embed.py search "{{ query }}"

# Watch for changes and auto-embed
[group('kg')]
kg-watch:
    @"{{ which("uv") }}" run python packages/cli/watch-embed.py

# Dump knowledge graph to SQL
[group('kg')]
kg-dump:
    @"{{ which("uv") }}" run python packages/cli/init-db.py --dump

# Load knowledge graph from SQL dump
[group('kg')]
kg-load:
    @"{{ which("uv") }}" run python packages/cli/init-db.py --load

# Force re-embed all entities
[group('kg')]
kg-rebuild:
    @echo "Rebuilding knowledge graph..."
    @rm -f .data/mcp/knowledge-graph.db
    @just kg-init
    @just kg-ingest
    @"{{ which("uv") }}" run python packages/cli/embed.py similarity
    @just kg-dump
    @echo "✓ Knowledge graph rebuilt"
