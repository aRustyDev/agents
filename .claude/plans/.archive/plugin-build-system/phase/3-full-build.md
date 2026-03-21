# Phase 3: Full Build System

**ID:** `phase-3`
**Dependencies:** phase-2
**Status:** complete
**Completed:** 2026-03-16
**Effort:** 19 hours (estimated) / ~8 hours (actual)

Complete build system with justfile modules for all component types.

## Goal

Production-ready build system with tiered validation and justfile modules.

## Prerequisites

- Phase 2 complete (MVP validated with homebrew-dev)
- Phase 0.5 complete (CLI research decisions)

## Deliverables

### 1. Justfile Module Structure

Organize build commands into modules per component tier:

```just
# justfile with modules
mod plugin    # just plugin:build, plugin:check, plugin:update
mod skill     # just skill:build, skill:check, skill:validate
mod command   # just command:build, command:validate
mod agent     # just agent:build, agent:validate
mod rule      # just rule:validate
```

### 2. Plugin Build Command

Full rewrite in Python (`.scripts/build-plugin.py`) with:

```bash
just plugin:build <name> [--force] [--check-only] [--update-hashes]
```

| Flag | Behavior |
|------|----------|
| (none) | Interactive mode with prompts |
| `--force` | Rebuild all, update hashes silently |
| `--check-only` | Verify hashes, no changes |
| `--update-hashes` | Update hashes without prompting |

### 3. Fork Detection

Track forked components with `"forked": true`:

```json
{
  "sources": {
    "skills/my-custom-skill": {
      "source": "context/skills/base-skill",
      "hash": "sha256:...",
      "forked": true,
      "forked_at": "2026-02-20T12:00:00Z"
    }
  }
}
```

Forked components:
- Skipped during hash validation
- Marked in status output
- Can be "un-forked" with `--reset-fork`

### 4. Skill Composition Tracking

Extend `plugin.sources.json` to track skills and their components:

```json
{
  "sources": {
    "skills/homebrew-formula-dev": {
      "source": "context/skills/homebrew-formula-dev",
      "hash": "sha256:...",
      "components": {
        "commands/add-formula.md": "sha256:...",
        "agents/homebrew-expert.md": "sha256:..."
      }
    }
  }
}
```

**Prerequisite:** Skills must be extracted to `context/skills/` before referencing. Direct references to external skills are not supported.

### 5. Batch Operations

```bash
just build-all-plugins [--check-only]
just update-all-plugins
```

### 6. CI Integration

GitHub Action for plugin validation:

```yaml
- name: Check plugin hashes
  run: just build-all-plugins --check-only
```

### 7. Detailed Reporting

```
Building plugin: homebrew-dev

Components:
  ✓ commands/add-formula.md (fresh)
  ✓ commands/validate-formula.md (fresh)
  ⚠ skills/homebrew-formula-dev (stale)
  ○ agents/homebrew-expert.md (forked)

Actions:
  Updated: 1 component
  Skipped: 1 forked
  Fresh: 2 components

✓ Plugin built successfully
```

### 8. Justfile Module Migration

Migrate Phase 2 standalone tasks into module structure:

| Phase 2 Task | Phase 3 Module Command |
|--------------|------------------------|
| `plugin-hash` | `just plugin:hash` |
| `plugin-check` | `just plugin:check` |
| `plugin-update` | `just plugin:update` |
| `build-plugin` | `just plugin:build` |

Create module files:
- `just/plugin.just` - Plugin build commands
- `just/skill.just` - Skill build commands
- `just/command.just` - Command validation
- `just/agent.just` - Agent validation
- `just/rule.just` - Rule validation

## Tasks

- [x] Create justfile module structure (`just/*.just`)
- [x] Migrate Phase 2 tasks to `plugin` module
- [x] Create `.scripts/build-plugin.py` (already existed, verified)
- [x] Implement all CLI flags (build, check, update, hash, check-all, build-all, update-all)
- [x] Add fork tracking (forked flag in plugin.sources.json)
- [x] Add batch operations (build-all, check-all, update-all)
- [x] Create CI workflow (.github/workflows/plugin-validation.yml)
- [x] Implement detailed reporting (JSON and text output)
- [x] Add JSON output mode for tooling (--json flag)
- [x] Write comprehensive tests (10/10 passing)
- [ ] Add skill composition tracking (deferred - requires skill extraction first)
- [ ] Update documentation (deferred to Phase 4)

## Success Criteria

- [x] Justfile modules work (`just plugin build`, `just skill validate`, etc.)
- [x] All flags work as documented
- [x] Forked components tracked and skipped
- [x] Batch operations work on all plugins (20 plugins validated)
- [x] CI catches hash mismatches (plugin-validation.yml)
- [x] Clear, actionable output (detailed status reporting)
- [ ] Skill composition tracked in plugin.sources.json (deferred)

## Estimated Effort

- Python rewrite: 6 hours
- Fork tracking: 3 hours
- Batch operations: 2 hours
- CI integration: 2 hours
- Testing: 4 hours
- Documentation: 2 hours
- **Total: ~19 hours**

## Dependencies

- Phase 2: MVP validation

## Rollback Plan

If full build system has issues:
1. Keep Phase 2 standalone tasks working alongside modules
2. Use `just plugin-*` (legacy) while debugging `just plugin:*` (modules)
3. Revert to simpler JSON schema without skill composition if too complex

## Risks

| Risk | Mitigation |
|------|------------|
| Python vs bash complexity | Python better for complex logic |
| CI false positives | Clear error messages, easy override |
| Performance on many plugins | Parallel processing for batch |
