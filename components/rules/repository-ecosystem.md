# aRustyDev Repository Ecosystem

When working in any of my repositories, be aware of these central resources:

## Source of Truth Repositories

### Infrastructure & Config

- **arustydev/ai** - Central AI configuration library and Claude plugin marketplace
  - Plugin marketplace at `ai.arusty.dev/plugins` (planned)
  - Components: skills, commands, agents, hooks, rules
  - See `legacy/plugins/` for available plugin bundles

- **arustydev/dotfiles** - Central dotfiles repository
  - Exceptions: justfiles and AI configs managed separately (see below)

- **arustydev/just** - Central justfile library
  - Serves: `just.arusty.dev`
  - Contains standard library modules for justfiles
  - The `just/` dir in dotfiles installs contents from https://just.arusty.dev

- **arustydev/schemas** - Central JSON/YAML schema registry
  - Serves: `schemas.arusty.dev`
  - Reference schemas from here, don't duplicate

## Development Tools

### GitHub Actions

Always prefer actions from `arustydev/gha`

- All newly developed GitHub Actions should be published here via Issue+PR
- If needed action doesn't exist, create issue in `arustydev/gha`
- Use third-party temporarily with tracking comment

### Pre-commit Hooks

Multi-repo ecosystem at `arustydev/pre-commit-hooks`

- `arustydev/pre-commit-hooks` - Index/management repo only
- Language-specific registries (each is a standalone pre-commit source):
  - `arustydev/pre-commit-hooks-rs` (Rust)
  - `arustydev/pre-commit-hooks-py` (Python)
  - `arustydev/pre-commit-hooks-go` (Go)
  - `arustydev/pre-commit-hooks-js` (JavaScript)
- Same hooks available in each language; swap `repo:` URL to compare performance

### MCP Servers

Index at `arustydev/mcp`

- Functions as central project management repo for MCP server development
- Individual MCP servers in separate repos

### Helm Charts

`arustydev/helm-charts`

- Published to ArtifactHub
- Serves: `charts.arusty.dev` (planned)

## Content & Brand

### Documentation

`arustydev/docs`

- Super-module aggregating docs from all repos
- Serves: `docs.arusty.dev` (planned)

### Blog

`arustydev/blog`

- Serves: `blog.arusty.dev`

### Brand Assets

`arustydev/brand`

- Logos, colors, typography, guidelines
- Serves: `brand.arusty.dev`
- Use CDN URLs in production, direct refs in development

## Repository Relationships

```
dotfiles ─────────────────────────────────────────┐
│                                                 │
├── ai (submodule)                                │
│   ├── plugins/                                  │
│   ├── components/                               │
│   └── .claude-plugin/marketplace.json           │
│                                                 │
└── just (installs from just.arusty.dev)          │
                                                  │
gha ──────────── (GitHub Actions source)          │
schemas ──────── (JSON/YAML schemas)              │
pre-commit-hooks (management repo) ───────────────│
├── pre-commit-hooks-rs                           │
├── pre-commit-hooks-py                           │
├── pre-commit-hooks-go                           │
└── pre-commit-hooks-js                           │
mcp ──────────── (MCP server management) ──────────┘
```

## Dotfiles Exceptions

The following are managed separately from dotfiles:

- `arustydev/just` - Justfiles (installed via https://just.arusty.dev)
- `arustydev/ai` - AI configs (lives in dotfiles as a git-submodule)
