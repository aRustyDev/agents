# Phase 1: Proof of Concept

Hash generation and validation for plugin components.

## Goal

Demonstrate that content-addressed hashing works for plugin components.

## Deliverables

### 1. Hash computation script

Create `.scripts/plugin-hash.py` that:
- Computes SHA256 hash of a file or directory
- For directories, hashes all files recursively (sorted, deterministic)
- Outputs hash in format: `sha256:<hex>`

```bash
# Usage
uv run python .scripts/plugin-hash.py context/commands/add-formula.md
# Output: sha256:a1b2c3d4e5f6...

uv run python .scripts/plugin-hash.py context/skills/pkgmgr-homebrew-formula-dev/
# Output: sha256:1a2b3c4d5e6f...
```

### 2. Justfile task: `plugin-hash`

```just
[group('plugins')]
plugin-hash path:
    @uv run python .scripts/plugin-hash.py "{{ path }}"
```

### 3. Extended plugin.sources.json schema

Define new format with hash field:

```json
{
  "$schema": "https://...",
  "sources": {
    "<local-path>": {
      "source": "<central-path>",
      "hash": "sha256:<hex>"
    }
  }
}
```

### 4. Hash verification function

Add to `.scripts/plugin-hash.py`:
- `verify_sources(plugin_dir)` - Check all hashes match
- Returns list of mismatched components

## Tasks

- [ ] Create `.scripts/plugin-hash.py` with hash computation
- [ ] Add directory hashing (recursive, deterministic)
- [ ] Add `plugin-hash` justfile task
- [ ] Document extended `plugin.sources.json` schema
- [ ] Add `verify_sources()` function
- [ ] Write tests for hash computation
- [ ] Test with homebrew-dev plugin

## Success Criteria

- [ ] Can compute deterministic hash of any component
- [ ] Can verify hashes match between source and plugin
- [ ] Hash changes when source content changes
- [ ] Hash stable when content unchanged (deterministic)

## Estimated Effort

- Hash script: 2 hours
- Schema documentation: 1 hour
- Testing: 2 hours
- **Total: ~5 hours**

## Dependencies

- None (standalone PoC)

## Risks

| Risk | Mitigation |
|------|------------|
| Non-deterministic hashing | Sort files, normalize line endings |
| Large directories slow | Use incremental/cached hashing |
| Binary files | Include in hash, don't special-case |
