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

### TypeScript Dependencies (.scripts/package.json)

TypeScript tooling is managed via Bun:

```bash
# Install all deps
cd .scripts && bun install

# Run the CLI tool
bun run .scripts/bin/ai-tools.ts <noun> <verb> [args]

# Or via justfile
just ai-tools <noun> <verb> [args]

# Run tests
cd .scripts && bun test
```

The `bun.lock` file is version controlled for reproducible installs.

### Python Dependencies (pyproject.toml) — KG only

Python is used only for the knowledge graph system (sqlite-vec + Ollama embeddings):

```bash
# Install KG deps (creates .venv automatically)
uv sync

# Run embedding CLI
uv run python .scripts/embed.py
```

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
│   ├── bin/ai-tools.ts         # Unified CLI (Bun + Citty)
│   ├── lib/                    # TypeScript modules (hash, output, schemas, etc.)
│   ├── commands/               # CLI subcommands (plugin, skill, kg, registry)
│   ├── test/                   # bun:test suites
│   ├── embed.py                # KG embedding CLI (Python, sqlite-vec)
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
| **CLI tool** | `just ai-tools <noun> <verb> [args]` |
| Plugin check | `just ai-tools plugin check <name>` |
| Skill validate | `just ai-tools skill validate <name>` |
| External skill check | `just skill external:check` |
| Semantic search | `just kg-search "query"` |

## Issue Tracking with Beads

This project uses [beads](https://github.com/steveyegge/beads) (`bd` CLI) as the primary issue tracker. Beads provides persistent task memory that survives conversation compaction.

### Planning Workflow

1. **Create Plans as Markdown** — Write detailed plans in `.claude/plans/`
2. **Review & Refine Plans** — Use `/review-plan` to identify gaps and improvements
3. **Convert Plans to Beads** — Use `/string-beads` to create issues with dependencies
4. **Implement via Beads** — Work through issues using the beads session protocol

### Session Protocol

```bash
bd ready              # Find unblocked work
bd show <id>          # Get full context
bd update <id> --status in_progress  # Start work
# ... do work, add notes ...
bd close <id>         # Complete task
bd sync               # Persist to git (always at session end)
```

### When to Use Beads vs TodoWrite

| Use Beads (`bd`) | Use TodoWrite |
|------------------|---------------|
| Multi-session work | Single-session tasks |
| Complex dependencies | Linear execution |
| Need context after compaction | All context in conversation |
| Team collaboration (git sync) | Solo immediate work |

**Decision test**: "Will I need this context in 2 weeks?" → YES = beads

### Key Commands

| Command | Purpose |
|---------|---------|
| `bd ready` | List unblocked work |
| `bd create "title"` | Create new issue |
| `bd show <id>` | View issue details |
| `bd update <id> --status in_progress` | Start working |
| `bd close <id>` | Complete issue |
| `bd dep add <blocker> <blocked>` | Add dependency |
| `bd sync` | Sync to git |

See `.claude/skills/beads/` for full documentation.

## Conventions

- **Brewfile**: Tool-level dependencies only (ollama, uv, bun, yq, etc.)
- **package.json** (`.scripts/`): TypeScript packages for `ai-tools` CLI (Bun)
- **pyproject.toml**: Python packages for KG only (sqlite-vec, ollama, watchdog)
- **`just init`**: Must be idempotent — safe to run multiple times
- **SQL dumps**: `.data/**/*.sql` files are version controlled; `.db` files are gitignored
- **Plans**: Written as markdown in `.claude/plans/`, converted to beads issues
- **`ai-tools`**: Unified CLI tool — `just ai-tools <noun> <verb>` for plugin/skill/registry operations
