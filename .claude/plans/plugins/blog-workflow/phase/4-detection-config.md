---
id: 8dc50661-f068-4c5a-8463-d4353927e752
project:
  id: 6233cf65-b369-4afe-8fd9-b934b1dc8716
title: "Phase 4: Platform Detection & Configuration"
status: draft
related:
  depends-on: [a2284908-5c82-452f-b578-62f952ed3c25, 1eac04fd-7c9d-4646-8fd4-71a0616500c3]
---

# Phase 4: Platform Detection & Configuration

**ID:** `phase-4`
**Dependencies:** phase-2, phase-3
**Status:** pending
**Effort:** 3-4 hours

## Objective

Implement automatic platform detection and project-level configuration storage so the correct platform skill loads without manual intervention.

**Note on `init.md`:** This phase extends the `commands/init.md` changes from Phase 2 (which added `--platform` flag and basic config generation). This phase adds auto-detection logic on top of those changes. Review Phase 2's modifications before starting.

## Success Criteria

- [ ] `/blog/init` detects Astro projects by checking for `astro.config.mjs` or `astro.config.ts`
- [ ] `/blog/init` creates `.blog-workflow.yaml` with detected platform
- [ ] Platform skill loads automatically based on `.blog-workflow.yaml` or detection
- [ ] Manual override via `--platform <name>` flag works
- [ ] Ambiguous detection (multiple platforms) prompts user for selection

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Updated init command with detection | `commands/init.md` | Command file |
| Config file template | `.blog-workflow.yaml` (in user's project) | YAML config |
| Updated plugin.json | `.claude-plugin/plugin.json` | Plugin manifest |

## Tasks

- [ ] Add detection logic to `commands/init.md`:
  - `astro.config.mjs` or `astro.config.ts` → Astro
  - `hugo.toml` or `config.toml` with `[module]` → Hugo (future)
  - `next.config.js` + `@next/mdx` in dependencies → Next.js MDX (future)
  - Prompt user if ambiguous or no match
- [ ] Define `.blog-workflow.yaml` schema:
  - `platform`: string (required)
  - `overrides`: optional map for path/command overrides
- [ ] Add platform skill auto-loading to init workflow: write platform choice to config, instruct agent to load matching skill
- [ ] Update `plugin.json`: Add `platformSkills` metadata array listing available platform skills; bump version to 3.0.0
- [ ] Update `.claude-plugin/marketplace.json`: Sync version to 3.0.0 (per `rules/plugin-version-sync.md`)
- [ ] Test detection scenarios: Astro detected, no platform detected, manual override

## Files

**Create:**

- None (config file is created in user's project at runtime)

**Modify:**

- `context/plugins/blog-workflow/commands/init.md`
- `context/plugins/blog-workflow/.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json` (version sync)

## Notes

Detection logic runs in the user's project directory, not in this repository. The command instructs the agent to check for platform indicator files and act accordingly.
