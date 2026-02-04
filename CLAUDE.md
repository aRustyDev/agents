# AI Context Library

This repository contains reusable Claude Code components: skills, agents, commands, rules, plugins, and MCP server configurations.

## Project Setup

```bash
just init
```

This command is idempotent and:
1. Installs tool dependencies via Homebrew (`brew bundle`)
2. Installs Python dependencies via uv (`uv sync`)
3. Initializes the knowledge graph database
4. Pulls the default embedding model (`ollama pull nomic-embed-text`)

## Dependency Management

### Tool Dependencies (brewfile)

System-level tools are managed via Homebrew:

```bash
# View dependencies
cat brewfile

# Install manually
brew bundle
```

Add new tools to `brewfile`, not installed ad-hoc.

### Python Dependencies (pyproject.toml)

Python packages are managed via uv:

```bash
# Install all deps (creates .venv automatically)
uv sync

# Add a new dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>

# Run a script in the venv
uv run python .scripts/embed.py
```

The `uv.lock` file is version controlled for reproducible installs.

## Knowledge Graph

The project maintains a semantic knowledge graph of all context components in SQLite with vector embeddings.

```bash
# Initialize database
just kg-init

# Ingest all context files
just kg-ingest

# Search semantically
just kg-search "kubernetes deployment"

# Watch for changes and auto-embed
just kg-watch
```

See `docs/src/adr/` for architecture decisions.

## Directory Structure

```
.
├── brewfile                    # Tool dependencies (Homebrew)
├── pyproject.toml              # Python dependencies (uv)
├── justfile                    # Task runner
├── CLAUDE.md                   # This file
├── .data/
│   └── mcp/
│       ├── knowledge-graph.db      # SQLite database (gitignored)
│       └── knowledge-graph.sql     # SQL dump (version controlled)
├── context/
│   ├── agents/                 # Agent definitions
│   ├── commands/               # Slash commands
│   ├── skills/                 # SKILL.md files
│   ├── rules/                  # Rule files
│   ├── plugins/                # Plugin bundles
│   └── output-styles/          # Output formatting styles
├── .scripts/
│   ├── embed.py                # Embedding CLI
│   ├── lib/                    # Python modules
│   └── sql/                    # SQL query files
├── settings/
│   └── mcp/                    # MCP server configurations
└── docs/
    └── src/
        ├── adr/                # Architecture Decision Records
        └── sql/                # Query documentation
```

## Common Tasks

| Task | Command |
|------|---------|
| Initialize project | `just init` |
| Install to ~/.claude | `just install` |
| Create a new skill | `just create-skill <name>` |
| Install a plugin | `just install-plugin <name>` |
| Search MCP servers | `just mcp-cache-search "query"` |
| Semantic search | `just kg-search "query"` |

## Conventions

- **Brewfile**: Tool-level dependencies only (ollama, uv, yq, etc.)
- **pyproject.toml**: Python packages (sqlite-vec, watchdog, etc.)
- **`just init`**: Must be idempotent — safe to run multiple times
- **SQL dumps**: `.data/**/*.sql` files are version controlled; `.db` files are gitignored
