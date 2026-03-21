---
id: d0ac5493-5296-40d8-91f9-234f7321dd6d
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 7: Cleanup"
status: pending
related:
  depends-on: [c1015f4f-8204-4558-ad20-dcf426c77cf8, c3e48e7b-0900-48fb-9bef-5129cf813ad6, c4cfe5f0-946f-460a-9ef1-c981f8124971, a62e81bd-0b5a-4e00-837a-791140ba3ab7]
---

# Phase 7: Cleanup

**ID:** `phase-7`
**Dependencies:** phase-3, phase-4, phase-5, phase-6
**Status:** pending
**Effort:** Small

## Objective

Remove Python infrastructure once all commands are migrated to TypeScript. If Phase 6 (KG) was skipped, retain minimal Python deps for the knowledge graph only.

## Success Criteria

- [ ] No justfile recipe calls `uv run python cli/` (except KG fallback if applicable)
- [ ] `just init` installs Bun deps instead of (or in addition to) Python deps
- [ ] All pre-commit hooks reference correct tools for `cli/**/*.ts`
- [ ] CLAUDE.md reflects the new toolchain
- [ ] Repository passes all existing CI checks

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Cleaned cli/ | `cli/` | Directory |
| Updated justfile | `justfile` | Just |
| Updated CLAUDE.md | `CLAUDE.md` | Markdown |
| Updated settings | `.claude/settings.json` | JSON |

## Files

**Create:**
- None

**Modify:**
- `justfile` — remove `_init-python` step, add `_init-bun`
- `CLAUDE.md` — update dependency management section
- `.claude/settings.json` — update hooks for .ts files
- `brewfile` — remove `uv` if no Python remains
- `.pre-commit-config.yaml` — remove ruff hooks if no Python remains

**Delete (full migration):**
- `cli/*.py`
- `cli/lib/*.py`
- `cli/tests/` (Python test dir)
- `pyproject.toml`
- `uv.lock`
- `.venv/`

**Delete (KG fallback — keep these if Phase 6 was skipped):**
- Keep: `cli/embed.py`, `cli/init-db.py`, `cli/kg-stats.py`, `cli/watch-embed.py`
- Keep: `cli/lib/embedder.py`, `cli/lib/chunker.py`
- Keep: `pyproject.toml` (trimmed to sqlite-vec + ollama + watchdog only)
- Delete: everything else in `cli/*.py`

## Tasks

### If Phase 6 succeeded (full migration)
- [ ] Delete all Python scripts in `cli/`
- [ ] Delete `cli/lib/` Python modules
- [ ] Delete `cli/tests/` Python tests
- [ ] Delete `pyproject.toml`
- [ ] Delete `uv.lock`
- [ ] Delete `.venv/` directory
- [ ] Remove `uv` from `brewfile`
- [ ] Remove `_init-python` from `just init`
- [ ] Remove ruff-related pre-commit hooks
- [ ] Remove ruff hook from `.claude/settings.json`

### If Phase 6 was skipped (KG stays in Python)
- [ ] Delete migrated Python scripts (build-plugin.py, plugin-hash.py, crawl-registries.py, migrate-*.py)
- [ ] Keep KG scripts (embed.py, init-db.py, kg-stats.py, watch-embed.py, lib/embedder.py, lib/chunker.py)
- [ ] Trim `pyproject.toml` to KG-only deps (sqlite-vec, ollama, watchdog, pyyaml)
- [ ] Keep `uv` in `brewfile`
- [ ] Keep `_init-python` in `just init` but scope to KG deps only

### Common tasks (both paths)
- [ ] Add `_init-bun` step to `just init` (`cd cli && bun install`)
- [ ] Update CLAUDE.md: document Bun/TS toolchain, `ai-tools` CLI, updated dependency management
- [ ] Update `.claude/settings.json`: add biome hook for `cli/**/*.ts` files
- [ ] Verify `just init` is still idempotent
- [ ] Run full pre-commit suite: `pre-commit run --all-files`
- [ ] Verify all justfile recipes work end-to-end
- [ ] Remove any temporary parity test scripts

## Notes

- This is the only irreversible phase — all prior phases keep Python in place as a fallback
- Do not execute this phase until all command groups are validated
- The `.claude/plans/merge-convert-skills/` Python code is out of scope — it stays regardless
- If both Python and Bun are needed (KG fallback), `just init` runs both `_init-python` and `_init-bun`
- Consider keeping Python test fixtures (`cli/tests/`) for reference during early TS maintenance, deleting after confidence is established
