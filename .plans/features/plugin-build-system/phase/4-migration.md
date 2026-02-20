# Phase 4: Migration

Migrate all existing plugins to the new build system.

## Goal

All plugins use content-addressed builds with hash verification.

## Prerequisites

- Phase 3 complete (full build system)

## Deliverables

### 1. Migration script

Create `.scripts/migrate-plugin-sources.py`:

```bash
# Migrate single plugin
uv run python .scripts/migrate-plugin-sources.py context/plugins/terraform

# Migrate all plugins
uv run python .scripts/migrate-plugin-sources.py --all
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
    @uv run python .scripts/migrate-plugin-sources.py "context/plugins/{{ name }}"

[group('plugins')]
migrate-all-plugins:
    @uv run python .scripts/migrate-plugin-sources.py --all
```

### 3. Migrate all 18 plugins

| Plugin | Has Sources | Status |
|--------|-------------|--------|
| android-dev | No | Create |
| api-dev | No | Create |
| blog-workflow | No | Create |
| browser-extension-dev | No | Create |
| cad-dev | No | Create |
| content-creation | No | Create |
| frontend-dev | No | Create |
| go-projects | No | Create |
| homebrew-dev | Yes | Migrate |
| infrastructure | No | Create |
| ios-dev | No | Create |
| job-hunting | No | Create |
| mcp-server-dev | No | Create |
| model-dev | No | Create |
| pcb-design | No | Create |
| rust-projects | No | Create |
| siem-ops | No | Create |
| terraform | No | Create |

### 4. Documentation

- Update plugin development guide
- Add troubleshooting for common migration issues
- Update scaffold-plugin to use new format

## Tasks

- [ ] Create migration script
- [ ] Add justfile tasks
- [ ] Migrate homebrew-dev (already has sources)
- [ ] Audit other plugins for potential shared components
- [ ] Create/migrate sources for each plugin
- [ ] Verify all plugins build successfully
- [ ] Update scaffold-plugin template
- [ ] Update documentation
- [ ] Remove old format support (breaking change)

## Success Criteria

- [ ] All plugins have `plugin.sources.json` with hashes
- [ ] All plugins pass `just build-plugin --check-only`
- [ ] scaffold-plugin creates new format by default
- [ ] Documentation updated
- [ ] Old format deprecated with clear migration path

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
