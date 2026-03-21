# Phase 2: MVP

**Status:** ✅ Complete

Stale dependency detection and one plugin migration.

> **Completed:** 2026-03-16. All deliverables implemented and tested with homebrew-dev.

## Goal

Integrate hash validation into build workflow with user-friendly prompts.

## Prerequisites

- Phase 1 complete (hash computation and verification)

## Deliverables

### 1. Stale detection in build-plugin

Modify `just build-plugin` to:
1. Read `plugin.sources.json`
2. Compute current hash of each source
3. Compare against stored hash
4. If mismatch: prompt user with options

```
⚠ Source changed: context/commands/add-formula.md
  Stored hash: sha256:abc123...
  Current hash: sha256:def456...

  [U]pdate hash and rebuild
  [S]kip this component
  [A]bort build
  Choice:
```

### 2. Update command

New justfile task: `plugin-update`

```just
[group('plugins')]
plugin-update name:
    # Recompute all hashes
    # Update plugin.sources.json
    # Rebuild plugin
```

### 3. Check command

New justfile task: `plugin-check`

```just
[group('plugins')]
plugin-check name:
    # Verify all hashes match
    # Report stale components
    # Exit 0 if fresh, 1 if stale
```

### 4. Migrate homebrew-dev plugin

- Convert existing `plugin.sources.json` to new format
- Add hashes for all components
- Test build/check/update cycle
- Document migration steps

## Tasks

- [x] Add stale detection to `build-plugin`
- [x] Implement interactive prompt for mismatches
- [x] Create `plugin-update` task
- [x] Create `plugin-check` task
- [x] Migrate homebrew-dev to new format
- [x] Update `plugin.sources.json` with hashes
- [x] Test full build cycle
- [x] Document migration process (`.claude/rules/plugin-sources-format.md`)

## Success Criteria

- [x] Build warns when sources have changed
- [x] User can update, skip, or abort
- [x] `plugin-check` reports stale status (exit 1 on stale)
- [x] `plugin-update` refreshes all hashes
- [x] homebrew-dev works with new format (5 components, all fresh)
- [x] Backward compatible with old format (graceful degradation, exit 2 warning)

## Implementation

| Deliverable | Location |
|-------------|----------|
| Stale detection in build | `justfile` (`build-plugin` task) |
| Interactive prompts | `.scripts/plugin-hash.py` (`--interactive` mode) |
| Check command | `justfile` (`plugin-check` task) |
| Update command | `justfile` (`plugin-update` task) |
| Migration documentation | `.claude/rules/plugin-sources-format.md` |

### homebrew-dev Migration

Fixed source paths and updated hashes:

| Component | Old Path | New Path |
|-----------|----------|----------|
| add command | `context/commands/add-formula.md` | `context/commands/homebrew/formula/add.md` |
| validate command | `context/commands/validate-formula.md` | `context/commands/homebrew/formula/validate.md` |
| batch command | `context/commands/batch-formulas.md` | `context/commands/homebrew/formula/batch-add.md` |

## Estimated Effort

- Stale detection: 3 hours
- Interactive prompts: 2 hours
- Update/check commands: 2 hours
- Migration + testing: 3 hours
- Documentation: 2 hours
- **Total: ~12 hours**

## Dependencies

- Phase 1: Hash computation script

## Rollback Plan

If MVP integration causes issues:
1. Keep hash computation as standalone tool (Phase 1 deliverable)
2. Revert build-plugin to non-interactive mode
3. Use manual hash verification workflow until issues resolved

## Risks

| Risk | Mitigation |
|------|------------|
| Breaking existing plugins | Backward compatibility mode |
| Complex interactive prompts | Simple Y/N first, enhance later |
| Migration errors | Test thoroughly on one plugin first |
