# Phase 3: Full Build System

Complete rewrite of build-plugin with all features.

## Goal

Production-ready build system with full feature set.

## Prerequisites

- Phase 2 complete (MVP validated with homebrew-dev)

## Deliverables

### 1. Rewritten build-plugin command

Full rewrite in Python (`.scripts/build-plugin.py`) with:

```bash
just build-plugin <name> [--force] [--check-only] [--update-hashes]
```

| Flag | Behavior |
|------|----------|
| (none) | Interactive mode with prompts |
| `--force` | Rebuild all, update hashes silently |
| `--check-only` | Verify hashes, no changes |
| `--update-hashes` | Update hashes without prompting |

### 2. Fork detection

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

### 3. Batch operations

```bash
just build-all-plugins [--check-only]
just update-all-plugins
```

### 4. CI integration

GitHub Action for plugin validation:

```yaml
- name: Check plugin hashes
  run: just build-all-plugins --check-only
```

### 5. Detailed reporting

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

## Tasks

- [ ] Create `.scripts/build-plugin.py`
- [ ] Implement all CLI flags
- [ ] Add fork tracking
- [ ] Add batch operations
- [ ] Create CI workflow
- [ ] Implement detailed reporting
- [ ] Add JSON output mode for tooling
- [ ] Write comprehensive tests
- [ ] Update documentation

## Success Criteria

- [ ] All flags work as documented
- [ ] Forked components tracked and skipped
- [ ] Batch operations work on all plugins
- [ ] CI catches hash mismatches
- [ ] Clear, actionable output

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

## Risks

| Risk | Mitigation |
|------|------------|
| Python vs bash complexity | Python better for complex logic |
| CI false positives | Clear error messages, easy override |
| Performance on many plugins | Parallel processing for batch |
