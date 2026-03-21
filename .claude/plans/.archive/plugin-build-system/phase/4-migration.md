# Phase 4: Migration

**Status:** Complete
**Completed:** 2026-03-16

Migrate all existing plugins to the new build system.

## Goal

All plugins use content-addressed builds with hash verification.

## Prerequisites

- Phase 3 complete (full build system)

## Deliverables

### 1. Migration script

Create `cli/migrate-plugin-sources.py`:

```bash
# Migrate single plugin
uv run python cli/migrate-plugin-sources.py context/plugins/terraform

# Migrate all plugins
uv run python cli/migrate-plugin-sources.py --all
```

Migration steps:
1. Read existing `plugin.sources.json`
2. Convert old format to new format
3. Compute hashes for all sources
4. Write updated `plugin.sources.json`
5. Rebuild plugin

### 2. Migration justfile task

```just
[group('plugins')]
migrate-plugin name:
    @uv run python cli/migrate-plugin-sources.py "context/plugins/{{ name }}"

[group('plugins')]
migrate-all-plugins:
    @uv run python cli/migrate-plugin-sources.py --all
```

### 3. Plugin Status (20 total)

**Central Sources Tracked (16):**

| Plugin | Fresh | Status |
|--------|-------|--------|
| android-dev | 2 | ✓ Ready |
| api-dev | 4 | ✓ Ready |
| blog-workflow | 1 | ✓ Ready |
| content-creation | 3 | ✓ Ready |
| frontend-dev | 5 | ✓ Ready |
| go-projects | 1 | ✓ Ready |
| homebrew-dev | 5 | ✓ Ready |
| infrastructure | 5 | ✓ Ready |
| ios-dev | 2 | ✓ Ready |
| mcp-server-dev | 1 | ✓ Ready |
| model-dev | 3 | ✓ Ready |
| pcb-design | 1 | ✓ Ready |
| rust-projects | 1 | ✓ Ready |
| siem-ops | 4 | ✓ Ready |
| swiftui-dev | 3 | ✓ Ready |
| terraform | 2 | ✓ Ready |

**Planning Entries - Forked (2):**

| Plugin | Forked | Status |
|--------|--------|--------|
| browser-extension-dev | 7 | ○ Planned |
| design-to-code | 3 | ○ Planned |

**Self-Contained - Empty Sources (2):**

| Plugin | Status |
|--------|--------|
| cad-dev | ✓ Valid (no central sources) |
| job-hunting | ✓ Valid (no central sources) |

### 4. Documentation

- Update plugin development guide
- Add troubleshooting for common migration issues
- Update scaffold-plugin to use new format

## Tasks

- [x] Create migration script (not needed - plugins already migrated)
- [x] Add justfile tasks (`just plugin {check,build,update}`)
- [x] Migrate homebrew-dev (already has sources)
- [x] Audit other plugins for potential shared components
- [x] Create/migrate sources for each plugin (20/20 complete)
- [x] Verify all plugins build successfully (`just plugin check-all`)
- [ ] Update scaffold-plugin template (deferred - works as-is)
- [ ] Update documentation (deferred)
- [x] Remove old format support (not needed - no legacy format in use)

## Success Criteria

- [x] All plugins have `plugin.sources.json` with hashes (20/20)
- [x] All plugins pass `just plugin check-all` (0 stale, 0 missing)
- [x] Forked/planning entries treated correctly (10 forked entries)
- [x] Self-contained plugins have valid empty sources (2 plugins)
- [ ] scaffold-plugin creates new format by default (deferred)
- [ ] Documentation updated (deferred)

## Estimated Effort

- Migration script: 3 hours
- Per-plugin migration: 0.5 hours × 18 = 9 hours
- Template updates: 2 hours
- Documentation: 2 hours
- Testing: 3 hours
- **Total: ~19 hours**

## Dependencies

- Phase 3: Full build system

## Risks

| Risk | Mitigation |
|------|------------|
| Plugins without shared components | Create empty sources, document pattern |
| Breaking changes | Announce deprecation, provide migration tool |
| Missed edge cases | Thorough testing, rollback plan |

## Rollback Plan

If migration causes issues:
1. Keep old `build-plugin` as `build-plugin-legacy`
2. Allow both formats during transition
3. Provide `migrate-plugin --reverse` to undo
