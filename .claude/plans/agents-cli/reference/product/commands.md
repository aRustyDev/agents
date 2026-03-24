# CLI

1. Add concrete exit code spec

## CLI Commands

```markdown
agents [-h, -y/--yes, --json (alias for --output json), --output '', --fail-on '', --debug, --trace , -vvv]
├── init [--hooks (adds claude/agent hooks for 'agents') ]
│   ├── skill           # Scaffold Skill from template
│   ├── persona         # Scaffold persona from template
│   ├── lsp             # Scaffold lsp from template
│   ├── mcp             #
│   │   ├── server      # Scaffold mcp-server from template
│   │   ├── client      # Scaffold mcp-client from template
│   │   └── tool        # Scaffold mcp-tool from template
│   ├── rule            # Scaffold rule from template
│   ├── hook            # Scaffold hook from template
│   ├── plugin          # Scaffold plugin from template
│   ├── output-style    # Scaffold output-style from template
│   ├── script          # Scaffold script from template
│   ├── command         # Scaffold command from template
│   └── setting         # Scaffold setting from template
├── add [--copy, ]
│   ├── skill           # Add Skill (Ex: `agents add skill owner/repo[/tree/tag/]@<skill>`)
│   ├── persona         # Add persona (Ex: `agents add persona owner/repo[/tree/tag/]@<persona>`)
│   ├── lsp             # Add lsp config (Ex: `agents add lsp owner/repo[/tree/tag/]@<language>`)
│   ├── mcp [-c <client>]
│   │   └── server      # Add mcp-server config (Ex: `agents add mcp server owner/repo[/tree/tag/]@<mcp>`)
│   ├── rule            # Add rule (Ex: `agents add rule owner/repo[/tree/tag/]@<rule>`)
│   ├── hook            # Add hook (Ex: `agents add hook owner/repo[/tree/tag/]@<hook>`)
│   ├── plugin          # Add plugin (Ex: `agents add plugin owner/repo[/tree/tag/]@<plugin>`)
│   ├── output-style    # Add output-style (Ex: `agents add style owner/repo[/tree/tag/]@<output-style>`)
│   ├── script          # Add script (Ex: `agents add script owner/repo[/tree/tag/]@<script>`)
│   ├── command         # Add command (Ex: `agents add command owner/repo[/tree/tag/]@<command>`)
│   └── setting         # Add setting (Ex: `agents add settings owner/repo[/tree/tag/]@<setting-profile>`)
├── remove/rm           # Ex: `agents add rm owner/repo@<skill>`
│   └── ...             # Same as `add`
├── list/ls             # Ex: `agents ls <component> ['owner/repo'|'name']`
│   └── ...             # Same as `add`
├── lint [--output '']  # Ex: `agents lint <component-csv> ['owner/repo'|'name']` (empty == `all`)
│   └── ...             # Same as `add`
├── search/find [--similarity 'x.y', --regex '', --glob '', --matrix 'path/to/foo.[csv|json]']
│   ├── skill           # Add Skill (Ex: `agents add skill owner/repo[/tree/tag/]@<skill>`)
│   ├── persona         # Add persona (Ex: `agents add persona owner/repo[/tree/tag/]@<persona>`)
│   ├── lsp             # Add lsp config (Ex: `agents add lsp owner/repo[/tree/tag/]@<language>`)
│   ├── mcp [-c <client>]
│   │   └── server      # Add mcp-server config (Ex: `agents add mcp server owner/repo[/tree/tag/]@<mcp>`)
│   ├── rule            # Add rule (Ex: `agents add rule owner/repo[/tree/tag/]@<rule>`)
│   ├── hook            # Add hook (Ex: `agents add hook owner/repo[/tree/tag/]@<hook>`)
│   ├── plugin          # Add plugin (Ex: `agents add plugin owner/repo[/tree/tag/]@<plugin>`)
│   ├── output-style    # Add output-style (Ex: `agents add style owner/repo[/tree/tag/]@<output-style>`)
│   ├── script          # Add script (Ex: `agents add script owner/repo[/tree/tag/]@<script>`)
│   ├── command         # Add command (Ex: `agents add command owner/repo[/tree/tag/]@<command>`)
│   └── setting         # Add setting (Ex: `agents add settings owner/repo[/tree/tag/]@<setting-profile>`)
├── info/describe       # Ex: `agents info <component> [--provider 'foo'] ['owner/repo'|'name']`
│   └── ...             # Same as `add`
├── update              # Ex: `agents lint <component-csv> [--provider 'foo'] ['owner/repo'|'name']` (empty == `all`); should execute the full download and update workflow
│   └── ...             # Same as `add`
├── check               # This may need to be deferred, it SHOULD be very quick but I don't have any ideas on how to do that atm.
│   └── ...             # Same as `add`
├── config              # Used to configure `agents` interactively. Similar to gitconfig
├── doctor              # check the health of the dev env, plugin, or system. 
│                       # Identifies potential issues, misconfigs, or outdated deps & suggests fixes.; should be based off shared schemas configured in tool
│                       # I'm not sure how to implement this, we may need to defer it?
├── completions         # Generate shell completions for `<shell>`
└── serve               # [--web, --api, --mcp, --rag]
```

## Templates

- agent
- lsp.json
- mcp.json
- skill.md
- command
- persona
- plugin
- output-style
- setting
- rule
- settings
- claude-md
- agents-md

## Schemas
- agent
- lsp.json
- mcp.json
- skill.md
- command
- persona
- plugin
- output-style
- setting
- rule
- settings

## Modules

### Verbs

- Add
- Rm
- Init
- Check
- Update
- Config
  - graph (knowledge graph)
  - backend
  - schemas (runtime edittable schemas; git aware for `git revert`)
    - remote (default https://schemas.arusty.dev)
    - local ()
  - file (default `gitconfig:agents.cli.*` > .agents.toml > ~/.agents.toml > ~/.agents/cli.toml > ~/.config/agents.toml > ~/.config/agents/cli.toml)
- Lint: schema + component -> violations + recommendations
- Search/Find
- Info/Describe
- Update
- Check
- Doctor: diagnose internal errors
- Serve
  - Web (default)
  - MCP
  - RAG

### Nouns

- graph: mapping json -> graph relations
  - taxonomy
  - crawler
- components:
  - skill
    - schema
    - entry: registry+version+latest
    - taxonomy: relations graph/hints
  - persona
  - lsp
  - mcp-server
  - mcp-client
  - mcp-tool
  - rule
  - hook
  - plugin
  - output-style
  - script
  - command
  - setting
- registry: like spiders for web-crawling
  - smithery
    - component-map: list of mappings from registry data-structure -> internal representation of components
    - pagination
    - scraper
  - skills.sh
    - component-map: ...
  - skillsmp
    - component-map: ...
  - github
    - component-map: ...
- utils: Utility/Helper functions used by all other components
  - o11y: structured schemas
    - error
    - log
    - trace
    - metrics
  - file-io: internal file IO API for unified access pattern
    - symlink
    - copy
    - delete
    - create
    - update
    - find-dir
    - find-file
    - search-file
    - file-metadata
    - get-tree
    - tree-metadata
  - lockfile: special lockfile helpers (structured wrapper around file-io)
  - parsers
    - glob
    - regex
  - search
    - glob
    - regex
    - matrix
  - embedders
  - chunkers
  - output: structured output helpers
  - git: git helper functions
  - storage: pluggable storage interfaces
    - file
    - meilisearch
    - cloudflare
    - sqlite
    - duckdb
    - qdrant
- catalog: the index/database of what 'components' are available/known
- backend
  - kv
  - docdb
  - filestore
  - filetree
  - searxng
  - meilisearch
  - vector
- config: configuration schema
- interfaces: Ways to interact with the tool
  - gui
  - mcp
  - api
  - cli
  - tui

## Open Questions
- How does `scope` get represented? Its used to limit the targeted body of search/analysis (ie certain directories, or certain urls, or certain indexes, etc)
- How does `filter` get represented? Its used to limit what of the returned body of results is, or to apply a filter/search to the target backend.
