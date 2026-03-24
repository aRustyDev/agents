# ADR-0003: Plugin Build System with Content-Addressed Components

## Status

Proposed

## Context

The plugin system currently has two modes of operation:

1. **Embedded**: Components live directly in plugin directories
2. **Referenced**: `plugin.sources.json` maps local paths to central source paths

This creates problems:
- **Component Duplication**: Same component copied to multiple plugins
- **Version Drift**: No tracking of which version a plugin uses
- **Update Pain**: Changing a shared component requires updating all plugins manually

## Decision

Implement a content-addressed build system for plugins:

### 1. Extend `plugin.sources.json` with content hashes

```json
{
  "sources": {
    "commands/example.md": {
      "source": "content/commands/example.md",
      "hash": "sha256:abc123..."
    }
  }
}
```

### 2. Build-time validation

The `build-plugin` command will:
- Compute hash of each source component
- Compare against stored hash
- Prompt user if hashes differ (source changed)
- Copy components to plugin directory
- Update hashes in `plugin.sources.json`

### 3. Committed build artifacts

Built plugins (with copied components) are committed to git, making them ready to use without a build step.

### 4. Local forks for customization

When a plugin needs customization, the component is forked locally and marked with `"forked": true`, breaking the link to the source.

## Consequences

### Positive

- **Reproducible builds**: Hash verification ensures consistency
- **Change detection**: Automatic detection when sources update
- **Single source of truth**: Shared components live in central directories
- **Simple migration**: Extends existing `plugin.sources.json` format
- **No new dependencies**: Uses standard tools (sha256sum, jq)

### Negative

- **Build step required**: Changes to shared components need rebuild
- **Larger commits**: Built artifacts committed to git
- **Fork divergence**: Forked components can drift from source

### Neutral

- **Learning curve**: Developers need to understand build workflow
- **Tooling investment**: Need to build validation and update commands

## Alternatives Considered

### Git submodules

Rejected: Too complex for single-repo components, poor UX.

### Semantic versioning per component

Rejected: Overhead of managing versions for many small components.

### Package registry (npm-style)

Rejected: Over-engineering for current scale, adds external dependencies.

### Symlink-only (keep current)

Rejected: Doesn't solve version drift or change detection.

## Implementation Plan

See `.plans/features/plugin-build-system/` for phased implementation.

## References

- Research: `docs/src/plugin-build-system-research.md`
- Issue: ai-aj5
