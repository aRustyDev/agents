# Repository Ecosystem Strategy Discussion

## Strategic Considerations

### 1. Brand Assets Strategy

**What are brand assets?**
Brand assets typically include:

- **Visual identity**: Logos (full, icon, wordmark), favicons, app icons
- **Color palette**: Primary, secondary, accent colors (hex, RGB, HSL values)
- **Typography**: Font families, weights, sizes
- **Imagery**: Profile photos, banners, social media templates, thumbnails
- **Guidelines**: Usage rules, spacing, do's and don'ts

**Three approaches:**

| Approach                        | Pros                                      | Cons                                        | Best For                           |
| ------------------------------- | ----------------------------------------- | ------------------------------------------- | ---------------------------------- |
| **Git repo (direct reference)** | Version controlled, simple, works offline | Large binaries bloat repo, no CDN benefits  | Source of truth, development       |
| **Gist**                        | Quick sharing, embeddable                 | No CDN, limited organization, no versioning | One-off sharing, small assets      |
| **CDN via web endpoint**        | Fast delivery, cache, optimized formats   | Requires infrastructure, more complex       | Production use, external consumers |

**Recommended hybrid approach:**

```
arustydev/brand/
├── source/              # Original files (AI, SVG, PSD) - Git LFS for large files
│   ├── logos/
│   ├── colors/
│   └── typography/
├── dist/                # Optimized outputs (PNG, WebP, JSON)
│   ├── logos/
│   ├── favicons/
│   └── palette.json
├── brand-guide.md       # Usage guidelines
└── .github/workflows/   # Auto-optimize on push, deploy to CDN
```

Then serve via:

- **Development**: Direct GitHub raw URLs or local references
- **Production**: `https://brand.arusty.dev/` or `https://cdn.arusty.dev/brand/`

---

### 2. Claude Plugin Marketplace Analysis

**Current state of `arustydev/ai`:**

- Has `.claude-plugin/` directory with `marketplace.json` (empty) and a README outlining intended structure
- Has `legacy/plugins/` with **50+ plugin directories** already structured with `agents/`, `commands/`, `skills/`
- Missing: Individual `plugin.json` manifests in each plugin

**Gap analysis vs Claude Plugin spec:**

| Requirement             | Current State            | Action Needed           |
| ----------------------- | ------------------------ | ----------------------- |
| `plugin.json` manifest  | Missing                  | Add to each plugin      |
| Directory structure     | ✅ Already correct       | None                    |
| Commands in `commands/` | ✅ Present               | None                    |
| Agents in `agents/`     | ✅ Present               | None                    |
| Skills in `skills/`     | ✅ Present               | None                    |
| Marketplace registry    | Empty `marketplace.json` | Define schema, populate |

**Recommended structure for marketplace:**

```
arustydev/ai/
├── .claude-plugin/
│   ├── marketplace.json      # Registry of all available plugins
│   └── README.md
├── plugins/                  # Move from legacy/, add manifests
│   ├── backend-development/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json   # Add this
│   │   ├── agents/
│   │   ├── commands/
│   │   └── skills/
│   └── cicd-automation/
│       └── ...
└── components/               # Atomic pieces (current structure)
    ├── skills/
    ├── commands/
    └── agents/
```

**marketplace.json schema suggestion:**

```json
{
  "version": "1.0.0",
  "plugins": [
    {
      "name": "backend-development",
      "description": "Backend development tools",
      "version": "1.0.0",
      "path": "plugins/backend-development",
      "tags": ["backend", "api", "architecture"]
    }
  ]
}
```

---

### 3. Pre-commit Hooks Multi-Language Strategy

**Two viable patterns:**

#### Option A: Central Registry, Multiple Hook Repos

```
arustydev/pre-commit-hooks/          # Registry/index only
├── .pre-commit-hooks.yaml           # Points to implementations
├── hooks-index.json                 # Metadata about all hooks
└── README.md

arustydev/pre-commit-hooks-python/   # Python implementations
├── .pre-commit-hooks.yaml
└── hooks/
    └── my-hook/

arustydev/pre-commit-hooks-rust/     # Rust implementations
├── .pre-commit-hooks.yaml
└── src/

arustydev/pre-commit-hooks-go/       # Go implementations
└── ...
```

**Pros**: Clean separation, each repo has its own CI/releases, users only clone what they need
**Cons**: More repos to manage, harder to ensure parity between implementations

#### Option B: Single Repo, Multiple Implementations (Recommended)

```
arustydev/pre-commit-hooks/
├── .pre-commit-hooks.yaml           # All hooks defined here
├── hooks/
│   ├── check-secrets/
│   │   ├── python/
│   │   │   ├── check_secrets.py
│   │   │   └── pyproject.toml
│   │   ├── rust/
│   │   │   ├── src/main.rs
│   │   │   └── Cargo.toml
│   │   ├── go/
│   │   │   └── main.go
│   │   └── README.md               # Documents all implementations
│   └── validate-yaml/
│       └── ...
└── .pre-commit-hooks.yaml
```

**.pre-commit-hooks.yaml example:**

```yaml
- id: check-secrets-python
  name: Check for secrets (Python)
  entry: python hooks/check-secrets/python/check_secrets.py
  language: python
  types: [text]

- id: check-secrets-rust
  name: Check for secrets (Rust)
  entry: hooks/check-secrets/rust/target/release/check-secrets
  language: rust
  types: [text]

- id: check-secrets-go
  name: Check for secrets (Go)
  entry: go run hooks/check-secrets/go/main.go
  language: golang
  types: [text]
```

**Pros**: Single source of truth, easier to ensure feature parity, one CI pipeline
**Cons**: Larger repo, all languages in one place

**My recommendation**: **Option B** - Single repo with multiple implementations. It's easier to maintain feature parity, document differences, and users can choose their preferred runtime from one location.

---

## Updated Repository Reference Notes

Based on our discussion, here are the refined notes:

### Core Infrastructure

| Repo                 | Purpose                                       | Serves                    |
| -------------------- | --------------------------------------------- | ------------------------- |
| `arustydev/ai`       | Central AI config library, plugin marketplace | `ai.arusty.dev` (planned) |
| `arustydev/dotfiles` | Source of truth for personal dotfiles         | N/A                       |
| `arustydev/just`     | Central justfile library with std modules     | `just.arusty.dev`         |
| `arustydev/schemas`  | Central JSON/YAML schema registry             | `schemas.arusty.dev`      |

### Development Tools

| Repo                         | Purpose                                    | Serves                        |
| ---------------------------- | ------------------------------------------ | ----------------------------- |
| `arustydev/gha`              | Preferred source for GitHub Actions        | N/A                           |
| `arustydev/pre-commit-hooks` | Pre-commit hooks registry (multi-language) | N/A                           |
| `arustydev/mcp`              | Index of MCP server repos                  | N/A                           |
| `arustydev/helm-charts`      | Helm charts registry for ArtifactHub       | `charts.arusty.dev` (planned) |

### Content & Documentation

| Repo              | Purpose                                  | Serves                      |
| ----------------- | ---------------------------------------- | --------------------------- |
| `arustydev/docs`  | Super-module aggregating all repo docs   | `docs.arusty.dev` (planned) |
| `arustydev/blog`  | Blog content                             | `blog.arusty.dev`           |
| `arustydev/brand` | Brand assets (logos, colors, guidelines) | CDN planned                 |

### Exceptions to dotfiles

- `arustydev/just` - Justfiles managed separately
- `arustydev/ai` - AI configs managed separately

---

## Proposed CLAUDE.md Section

Here's what I recommend adding to your global CLAUDE.md:

````markdown
## aRustyDev Repository Ecosystem

When working in any of my repositories, be aware of these central resources:

### Source of Truth Repositories

**Infrastructure & Config:**

- **arustydev/ai** - Central AI configuration library and Claude plugin marketplace
  - Install plugins via marketplace at `ai.arusty.dev` (planned)
  - Components: skills, commands, agents, hooks, rules
  - See `legacy/plugins/` for available plugin bundles

- **arustydev/dotfiles** - Central dotfiles repository
  - Exceptions: justfiles (`arustydev/just`) and AI configs (`arustydev/ai`) managed separately

- **arustydev/just** - Central justfile library
  - Serves: `just.arusty.dev`
  - Contains standard library modules for justfiles

- **arustydev/schemas** - Central schema registry
  - Serves: `schemas.arusty.dev`
  - Reference schemas from here, don't duplicate

### Development Tools

**GitHub Actions:** Always prefer actions from `arustydev/gha`

- If needed action doesn't exist, create issue in `arustydev/gha`
- Use third-party temporarily with tracking comment

**Pre-commit Hooks:** Multi-repo ecosystem

- `arustydev/pre-commit-hooks` - Index/management repo
- Language-specific registries:
  - `arustydev/pre-commit-hooks-rs` (Rust)
  - `arustydev/pre-commit-hooks-py` (Python)
  - `arustydev/pre-commit-hooks-go` (Go)
  - `arustydev/pre-commit-hooks-js` (JavaScript)
- Same hooks available in each language; swap `repo:` to compare performance

**MCP Servers:** Index at `arustydev/mcp`

- Individual MCP servers in separate repos
- Reference via the index

**Helm Charts:** `arustydev/helm-charts`

- Published to ArtifactHub
- Serves: `charts.arusty.dev` (planned)

### Content & Brand

**Documentation:** `arustydev/docs`

- Super-module aggregating docs from all repos
- Serves: `docs.arusty.dev` (planned)

**Blog:** `arustydev/blog`

- Serves: `blog.arusty.dev`

**Brand Assets:** `arustydev/brand`

- Logos, colors, typography, guidelines
- Use CDN URLs in production, direct refs in development

### Repository Relationship Diagram

```asciidoc

dotfiles ─────────────────────────────────────────┐
│                                                 │
├── ai (submodule)                                │
│   ├── plugins/                                  │
│   ├── components/                               │
│   └── .claude-plugin/marketplace.json           │
│                                                 │
└── just (submodule)                              │
    └── std/                                      │
                                                  │
gha ──────────── (GitHub Actions source)          │
schemas ──────── (JSON/YAML schemas)              │
pre-commit-hooks (hook implementations)           │
mcp ──────────── (MCP server index) ───────────────┘
```
````

```

---

## Decisions Made (2025-12-19)

### 1. Brand Assets
**Decision**: Hybrid approach (repo + CDN)
- Serve via `brand.arusty.dev`
- Source files in Git (with LFS for large binaries)
- Optimized assets auto-deployed to CDN

### 2. Plugin Marketplace
**Decision**: Marketplace at `ai.arusty.dev/plugins`
- Recommended structure approved
- Need to add `plugin.json` manifests to existing plugins
- Populate `marketplace.json` registry

### 3. Pre-commit Hooks
**Decision**: Multi-repo/registry approach (Option A, modified)
- `arustydev/pre-commit-hooks` - Management/index repo only (like arustydev/mcp)
- Language-specific repos, each is its own pre-commit registry:
  - `arustydev/pre-commit-hooks-rs` (Rust)
  - `arustydev/pre-commit-hooks-py` (Python)
  - `arustydev/pre-commit-hooks-go` (Go)
  - `arustydev/pre-commit-hooks-js` (JavaScript/Node)

**Rationale**: Users can use identical hook configs with only `repo:` changed to compare performance across languages and easily swap between implementations.

---

## Updated Repository Reference Notes (Final)

### Core Infrastructure

| Repo                 | Purpose                                       | Serves                    |
| -------------------- | --------------------------------------------- | ------------------------- |
| `arustydev/ai`       | Central AI config library, plugin marketplace | `ai.arusty.dev` (planned) |
| `arustydev/dotfiles` | Source of truth for personal dotfiles         | N/A                       |
| `arustydev/just`     | Central justfile library with std modules     | `just.arusty.dev`         |
| `arustydev/schemas`  | Central JSON/YAML schema registry             | `schemas.arusty.dev`      |

### Development Tools

| Repo                          | Purpose                                         | Serves |
| ----------------------------- | ----------------------------------------------- | ------ |
| `arustydev/gha`               | Preferred source for GitHub Actions (via Issue+PR) | N/A    |
| `arustydev/mcp`               | Central project management for MCP server development | N/A    |
| `arustydev/pre-commit-hooks`  | Management repo for pre-commit hooks ecosystem  | N/A    |
| `arustydev/pre-commit-hooks-rs` | Rust pre-commit hook implementations          | N/A    |
| `arustydev/pre-commit-hooks-py` | Python pre-commit hook implementations        | N/A    |
| `arustydev/pre-commit-hooks-go` | Go pre-commit hook implementations            | N/A    |
| `arustydev/pre-commit-hooks-js` | JavaScript pre-commit hook implementations    | N/A    |
| `arustydev/helm-charts`       | Helm charts registry for ArtifactHub           | `charts.arusty.dev` (planned) |

### Content & Documentation

| Repo              | Purpose                                  | Serves                      |
| ----------------- | ---------------------------------------- | --------------------------- |
| `arustydev/docs`  | Super-module aggregating all repo docs   | `docs.arusty.dev` (planned) |
| `arustydev/blog`  | Blog content                             | `blog.arusty.dev`           |
| `arustydev/brand` | Brand assets (logos, colors, guidelines) | `brand.arusty.dev`          |

### Exceptions to dotfiles

- `arustydev/just` - Justfiles managed separately; the `just/` dir in dotfiles installs contents from https://just.arusty.dev
- `arustydev/ai` - AI configs managed separately; lives in dotfiles as a git-submodule

---

## Action Items

- [x] Update this strategy document with decisions
- [x] Create issue in `arustydev/brand` for hybrid assets implementation ([#1](https://github.com/aRustyDev/brand/issues/1))
- [x] Create issue in `arustydev/ai` for plugin marketplace structure ([#17](https://github.com/aRustyDev/ai/issues/17))
- [x] Create rule file `components/rules/repository-ecosystem.md`
