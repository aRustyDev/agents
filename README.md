# Agents — AI Context Library

Reusable Claude Code components: skills, agents, commands, rules, plugins, MCP server configurations, and a universal component management system.

## Quick Start

```bash
just init          # Install deps, init knowledge graph, pull embedding model
just agents --help # CLI tool for component management
```

## Architecture

```
content/               Component source of truth
├── skills/            SKILL.md files (130+)
├── agents/            Agent definitions (markdown + frontmatter)
├── commands/          Slash commands (markdown + frontmatter)
├── rules/             Instruction rules (markdown)
├── plugins/           Plugin bundles (.claude-plugin/plugin.json)
├── hooks/             Hook configurations
├── output-styles/     Output formatting templates
└── reference/         Reference documentation

packages/cli/              TypeScript tooling (Bun + Citty)
├── bin/agents.ts      CLI entrypoint
├── commands/          CLI command trees (skill, mcp, component, plugin, ...)
├── lib/               Library modules
│   ├── component/     Universal component model (7 providers)
│   ├── skill-*.ts     Skill lifecycle (add/find/list/outdated/update/remove/info/init)
│   └── ...            Hash, lockfile, output, runtime, schemas, etc.
└── test/              bun:test suites (900+ tests)

settings/mcp/          MCP server configurations
docs/src/adr/          Architecture Decision Records
```

## CLI Commands

### Skill Management

```bash
just agents skill add owner/repo@skill   # Install a skill
just agents skill find "kubernetes"       # Search registries
just agents skill list                    # List installed skills
just agents skill list --agent claude-code # Filter by agent
just agents skill outdated                # Check for updates
just agents skill update                  # Update outdated skills
just agents skill remove skill-name       # Remove a skill
just agents skill info skill-name         # Detailed metadata
just agents skill init my-skill           # Scaffold new skill
```

### MCP Server Management

```bash
just agents mcp search "postgres"                        # Search Smithery registry
just agents mcp add smithery://ns/server --client cursor  # Add to client config
just agents mcp list --client claude-desktop              # List in client config
just agents mcp remove server-name --client cursor        # Remove from client
just agents mcp info ns/server-name                       # Server details
just agents mcp publish --name ns/server --url https://...# Publish to Smithery
```

### Cross-Type Component Search

```bash
just agents component search "kubernetes"   # Search all types
just agents component list                  # List all installed
just agents component list --type agent     # Filter by type
```

### Other Commands

```bash
just agents plugin check <name>    # Validate a plugin
just agents skill validate <name>  # Validate skill frontmatter
just kg-search "query"             # Semantic search (knowledge graph)
```

## Component Model

All entity types flow through a universal `ComponentProvider` interface:

| Provider | ID | Entity Types | Backend |
|----------|----|-------------|---------|
| LocalProvider | `local` | skill | Filesystem (wraps skill-* modules) |
| LocalAgentProvider | `local-agent` | agent | `content/agents/**/*.md` |
| LocalPluginProvider | `local-plugin` | plugin | `content/plugins/**/.claude-plugin/` |
| LocalRuleProvider | `local-rule` | rule | `content/rules/**/*.md` |
| LocalCommandProvider | `local-command` | command | `content/commands/**/*.md` |
| LocalOutputStyleProvider | `local-output-style` | output-style | `content/output-styles/**/*.md` |
| SmitheryProvider | `smithery` | mcp-server | registry.smithery.ai API |

The `ComponentManager` aggregates search across all providers, deduplicates results, and handles pagination.

## AI Client Config Support

MCP servers can be installed to 19 AI client config files:

| Client | Method | Format |
|--------|--------|--------|
| Claude Desktop | file | JSON |
| Claude Code | command | `claude mcp add` |
| Cursor | file | JSON |
| Windsurf | file | JSON |
| VS Code | command | `code --add-mcp` |
| Cline, Roo Code, Continue, Zed, Goose, OpenCode, ... | file | JSON/YAML/JSONC |

## Plugin Marketplace

Curated plugins at `.claude-plugin/marketplace.json`:

| Plugin | Description |
|--------|-------------|
| `homebrew-dev` | Homebrew formula development |
| `browser-extension-dev` | Cross-browser extension development |
| `blog-workflow` | Technical blog post creation |
| `job-hunting` | Job hunting toolkit |
| `swiftui-dev` | SwiftUI development |
| `design-to-code` | Design-to-code conversion |

## Dependencies

| Layer | Tool | Config |
|-------|------|--------|
| System tools | Homebrew | `brewfile` |
| TypeScript | Bun | `packages/cli/package.json` |
| Python (KG only) | uv | `pyproject.toml` |
| Task runner | just | `justfile` |
| Issue tracking | beads (bd) | `.beads/config.yaml` |

## Development

```bash
just init                          # One-time setup
cd cli && bun test            # Run all tests
cd cli && bun test test/component/  # Component tests only
just agents skill validate <name>  # Validate a skill
just agents plugin check <name>    # Validate a plugin
```

## License

MIT
