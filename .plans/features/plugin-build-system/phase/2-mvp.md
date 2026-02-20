# Phase 2: MVP

Stale dependency detection and one plugin migration.

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

- [ ] Add stale detection to `build-plugin`
- [ ] Implement interactive prompt for mismatches
- [ ] Create `plugin-update` task
- [ ] Create `plugin-check` task
- [ ] Migrate homebrew-dev to new format
- [ ] Update `plugin.sources.json` with hashes
- [ ] Test full build cycle
- [ ] Document migration process

## Success Criteria

- [ ] Build warns when sources have changed
- [ ] User can update, skip, or abort
- [ ] `plugin-check` reports stale status
- [ ] `plugin-update` refreshes all hashes
- [ ] homebrew-dev works with new format
- [ ] Backward compatible with old format (graceful degradation)

## Estimated Effort

- Stale detection: 3 hours
- Interactive prompts: 2 hours
- Update/check commands: 2 hours
- Migration + testing: 3 hours
- Documentation: 2 hours
- **Total: ~12 hours**

## Dependencies

- Phase 1: Hash computation script

## Risks

| Risk | Mitigation |
|------|------------|
| Breaking existing plugins | Backward compatibility mode |
| Complex interactive prompts | Simple Y/N first, enhance later |
| Migration errors | Test thoroughly on one plugin first |
