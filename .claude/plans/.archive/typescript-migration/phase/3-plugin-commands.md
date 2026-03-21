---
id: c1015f4f-8204-4558-ad20-dcf426c77cf8
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 3: Plugin Commands"
status: pending
related:
  depends-on: [1105f062-33cf-4eff-a759-f17fb55296c3, c4d1eba9-dea5-4b58-af0a-53113a016208]
---

# Phase 3: Plugin Commands

**ID:** `phase-3`
**Dependencies:** phase-1, phase-2
**Status:** pending
**Effort:** Medium

## Objective

Wire library modules into the first full vertical: plugin build, check, hash, and lint commands. This is the first justfile recipe cutover from Python to TypeScript.

## Success Criteria

- [ ] `ai-tools plugin check <name> --json` output matches `build-plugin.py check <name> --json`
- [ ] `ai-tools plugin build <name>` copies sources and updates hashes correctly
- [ ] `ai-tools plugin hash <path>` matches `plugin-hash.py <path>` output
- [ ] `ai-tools plugin lint <name>` runs cclint SDK and reports results
- [ ] `ai-tools plugin check-all` and `build-all` work for all plugins
- [ ] All justfile plugin recipes point to TypeScript

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Plugin commands | `cli/commands/plugin.ts` | TypeScript |
| Updated justfile | `justfile` | Just |
| Integration tests | `cli/test/plugin.test.ts` | TypeScript |

## Files

**Create:**
- `cli/test/plugin.test.ts`

**Modify:**
- `cli/commands/plugin.ts` (replace stub with full implementation)
- `justfile` (update plugin recipes to use `ai-tools`)

## Tasks

### commands/plugin.ts
- [ ] Implement `build` subcommand — copy sources, verify hashes, report via OutputFormatter
- [ ] Implement `check` subcommand — verify source hashes, output SourceStatus table
- [ ] Implement `hash` subcommand — compute and display hash for a path
- [ ] Implement `lint` subcommand — invoke cclint SDK programmatically
- [ ] Implement `check-all` subcommand — iterate all plugins, aggregate results
- [ ] Implement `build-all` subcommand — iterate all plugins, show progress bar
- [ ] Wire OutputFormatter: tables for check results, success/error messages, JSON mode

### Parity validation
- [ ] Run `build-plugin.py check <name> --json` for every plugin, capture output
- [ ] Run `ai-tools plugin check <name> --json` for every plugin, capture output
- [ ] Diff all outputs — must be identical (or intentionally improved)
- [ ] Run `plugin-hash.py <path>` for test paths, compare to `ai-tools plugin hash <path>`

### Justfile cutover
- [ ] Update `plugin-check` recipe to call `ai-tools plugin check`
- [ ] Update `plugin-build` recipe to call `ai-tools plugin build`
- [ ] Update `plugin-hash` recipe to call `ai-tools plugin hash`
- [ ] Update `plugin-check-all` recipe to call `ai-tools plugin check-all`
- [ ] Update `plugin-build-all` recipe to call `ai-tools plugin build-all`
- [ ] Verify all plugin recipes work end-to-end

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success, all checks passed |
| 1 | Validation/check failures found |
| 2 | Process error (I/O, parse failure) |

## Notes

- This is the validation phase for the entire architecture — if the plugin commands work cleanly, the pattern is proven for skill/kg/registry
- The cclint SDK integration replaces the current `npx @carlrannaberg/cclint` shell invocations
- The `build` command is the most complex: it reads sources manifest, copies files, computes hashes, and optionally updates the manifest — test each step independently
- Keep Python scripts in place during this phase — only remove them in Phase 7
