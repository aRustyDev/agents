# Plugin Build System Research

Research findings for the plugin build/compile workflow (ai-aj5).

## Problem Statement

Current plugin architecture has two pain points:

1. **Component Duplication**: Same skill/agent exists in multiple plugins, making updates painful
2. **Version Drift**: Plugins use different versions of shared components, causing inconsistency

## Current State

### Two Patterns in Use

| Pattern | Example | Description |
|---------|---------|-------------|
| Embedded | terraform | Components live directly in plugin directory |
| Referenced | homebrew-dev | `plugin.sources.json` maps local → central paths |

### Existing `plugin.sources.json` Format

```json
{
  "sources": {
    "commands/add-formula.md": "context/commands/add-formula.md",
    "skills/homebrew-formula-dev": "context/skills/pkgmgr-homebrew-formula-dev"
  }
}
```

### Existing Build Tasks

| Task | Purpose |
|------|---------|
| `build-plugin <name>` | Copies from central to plugin directory |
| `install-plugin <name>` | Creates symlinks to `~/.claude/` |

## Research Questions & Answers

### 1. How should plugins reference shared components?

**Decision**: Extend existing `plugin.sources.json` with version/hash metadata.

**Rationale**: Builds on existing infrastructure, minimal migration effort.

### 2. What level of isolation do plugins need?

**Decision**: Full bundle after build (self-contained).

**Rationale**: Plugins should work without external dependencies at runtime.

### 3. How should component versions be tracked?

**Decision**: Content-based hashing (like lockfiles).

**Rationale**:

- Reproducible builds without managing semver for every component
- Similar to Go's `go.sum`, npm's `package-lock.json`, Nix store
- Hash changes automatically when content changes

### 4. When should version conflicts be detected?

**Decision**: Build-time validation (fail fast).

**Rationale**: Catch issues before deployment, not at runtime.

### 5. What happens when source components change?

**Decision**: Auto-detect + prompt during build.

**Rationale**: Balance between awareness and convenience.

### 6. How to handle plugin-specific customizations?

**Decision**: Fork component locally (breaks link to source).

**Rationale**: Pragmatic approach - if you need customization, own it fully.

### 7. Lockfile format?

**Decision**: Extend `plugin.sources.json` with hash field.

**Rationale**: Single file, no new concepts, backward compatible.

### 8. Build artifacts in git?

**Decision**: Yes, committed (ready to use without build step).

**Rationale**: Simplifies consumption - clone and use.

## Proposed Architecture

### Extended `plugin.sources.json`

**JSON Schema**: `context/plugins/.template/.claude-plugin/plugin.sources.schema.json`

#### Legacy Format (deprecated)

```json
{
  "sources": {
    "commands/add-formula.md": "context/commands/add-formula.md"
  }
}
```

#### Extended Format (recommended)

```json
{
  "$schema": "./plugin.sources.schema.json",
  "sources": {
    "commands/add-formula.md": {
      "source": "context/commands/add-formula.md",
      "hash": "sha256:a1b2c3d4e5f6..."
    },
    "skills/homebrew-formula-dev": {
      "source": "context/skills/pkgmgr-homebrew-formula-dev",
      "hash": "sha256:1a2b3c4d5e6f...",
      "forked": true
    }
  }
}
```

### Build Workflow

```text
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│ plugin.sources  │────▶│ just build   │────▶│ Self-contained  │
│ .json (refs)    │     │ -plugin      │     │ plugin dir      │
└─────────────────┘     └──────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌──────────────┐
                        │ Validate     │
                        │ hashes or    │
                        │ prompt user  │
                        └──────────────┘
```

## Comparable Systems

| System | Approach | Relevant Pattern |
|--------|----------|------------------|
| npm | package.json + package-lock.json | Separate manifest and lockfile |
| Go modules | go.mod + go.sum | Content hashes for verification |
| Nix | Content-addressed store | Hash-based immutable artifacts |
| Cargo | Cargo.toml + Cargo.lock | Workspace with shared deps |
| Homebrew | Formula with bottle hashes | Pre-built artifacts with verification |

## Migration Guide

### Migrating a Plugin to Extended Format

1. **Check current status**:

   ```bash
   just plugin-check <plugin-name>
   ```

   If you see `no-hash` status, the plugin uses legacy format.

2. **Update all hashes**:

   ```bash
   just plugin-update <plugin-name>
   ```

   This converts legacy format to extended format and computes SHA256 hashes.

3. **Verify migration**:

   ```bash
   just plugin-check <plugin-name>
   ```

   All components should show `fresh` status.

4. **Commit the changes**:

   ```bash
   git add context/plugins/<name>/.claude-plugin/plugin.sources.json
   git commit -m "feat: migrate <name> plugin to extended format"
   ```

### Handling Stale Sources

When `build-plugin` detects stale sources, it prompts for each:

| Choice | Action |
|--------|--------|
| `U` | Update hash in plugin.sources.json to match current source |
| `S` | Skip copying this component (useful for local modifications) |
| `A` | Abort the build |

### Forking Components

To fork a component for plugin-specific customization:

1. Copy the source into the plugin directory
2. Edit `plugin.sources.json` to add `"forked": true`:

   ```json
   {
     "commands/custom.md": {
       "source": "context/commands/original.md",
       "hash": "sha256:...",
       "forked": true,
       "forked_at": "2026-02-20T12:00:00Z"
     }
   }
   ```

3. Forked components are always treated as fresh (hash not verified)

### Available Commands

#### Single Plugin Commands

| Command | Purpose |
|---------|---------|
| `just plugin-check <name>` | Verify hashes (exit 0=fresh, 1=stale) |
| `just plugin-update <name>` | Recompute all hashes and rebuild |
| `just plugin-hash <path>` | Compute hash for any file/directory |
| `just build-plugin <name>` | Build with interactive stale handling |

#### Batch Commands

| Command | Purpose |
|---------|---------|
| `just plugin-check-all` | Check all plugins (for CI) |
| `just plugin-build-all` | Build all plugins |
| `just plugin-update-all` | Update all plugin hashes |

#### Python CLI (Direct Access)

The Python CLI provides additional flags:

```bash
# Single plugin operations
uv run python cli/build-plugin.py check <name> [--json] [--verbose]
uv run python cli/build-plugin.py build <name> [--force] [--check-only] [--update-hashes]
uv run python cli/build-plugin.py update <name>
uv run python cli/build-plugin.py hash <path> [--hex-only]

# Batch operations
uv run python cli/build-plugin.py check-all [--json]
uv run python cli/build-plugin.py build-all [--force] [--check-only] [--update-hashes]
uv run python cli/build-plugin.py update-all
```

| Flag | Description |
|------|-------------|
| `--json` | Output in JSON format (for programmatic use) |
| `--verbose` | Show hash details for each component |
| `--force` | Force rebuild, update hashes |
| `--check-only` | Verify hashes without copying files |
| `--update-hashes` | Update hashes without prompting |
| `--hex-only` | Output hash without sha256: prefix |

#### Migration Commands

Dedicated tools for migrating plugins to the extended format:

```bash
# Check migration status of all plugins
just migrate-check

# Migrate a single plugin
just migrate-plugin <name>

# Migrate all plugins
just migrate-all-plugins [--dry-run]
```

The migration script:
1. Converts legacy string paths to object format
2. Computes SHA256 hashes for all sources
3. Preserves forked status and other metadata

### CI Integration

Plugin validation runs automatically on push/PR when plugin-related files change:

```yaml
# .github/workflows/plugin-validation.yml
- name: Validate all plugins
  run: uv run python cli/build-plugin.py check-all

- name: Build all plugins (check-only)
  run: uv run python cli/build-plugin.py build-all --check-only
```

### Planning Format

For plugins that reference external sources (not yet implemented), use the planning format:

```json
{
  "sources": {
    "skills/some-feature": {
      "type": "extend",
      "base": "https://github.com/example/plugin/tree/main/skills/feature",
      "notes": "Adapt for specific use case"
    },
    "mcp/some-server": {
      "type": "reuse",
      "package": "@example/mcp-server",
      "install": "npx @example/mcp-server"
    }
  }
}
```

Planning format components are treated as "forked" (skipped from hash verification).

## Migration Status

As of Phase 4 completion:

| Status | Count | Description |
|--------|-------|-------------|
| Extended | 17 | Buildable with hash verification |
| Planning | 1 | Uses external sources (browser-extension-dev) |
| Empty | 2 | No shared components (cad-dev, job-hunting) |

All 18 plugins now pass `just plugin-check-all`.

## References

- [npm package-lock.json](https://docs.npmjs.com/cli/v9/configuring-npm/package-lock-json)
- [Go Module Reference](https://go.dev/ref/mod)
- [Nix Content-Addressed Store](https://nixos.wiki/wiki/Content-Addressed_Store)
