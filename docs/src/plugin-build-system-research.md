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

```json
{
  "$schema": "Plugin source mapping with content hashes",
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

```
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

## References

- [npm package-lock.json](https://docs.npmjs.com/cli/v9/configuring-npm/package-lock-json)
- [Go Module Reference](https://go.dev/ref/mod)
- [Nix Content-Addressed Store](https://nixos.wiki/wiki/Content-Addressed_Store)
