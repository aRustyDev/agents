---
id: a1b2c3d4-3333-4aaa-bbbb-333333333333
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 3: Agent Definitions & Tooling"
status: pending
---

# Phase 3: Agent Definitions & Tooling

**ID:** `phase-3`
**Dependencies:** None
**Status:** pending
**Effort:** Medium

## Objective

Create the two inspector agent definitions (Tier 1 Haiku, Tier 2 Sonnet), the catalog justfile module, and the CLI scaffolding for the analyze/grade/stats/search subcommands.

## Success Criteria

- [ ] `content/agents/catalog/skill-inspector-t1.md` agent definition complete with tool permissions and NDJSON output format
- [ ] `content/agents/catalog/skill-inspector-t2.md` agent definition complete with gating criteria and merge semantics
- [ ] `content/skills/.catalog/justfile` module created with all recipes delegating to `ai-tools`
- [ ] `ai-tools skill catalog analyze --help` works (stub implementation)
- [ ] `ai-tools skill catalog grade --help` works (stub implementation)
- [ ] `ai-tools skill catalog stats --help` works (stub implementation)
- [ ] `ai-tools skill catalog search --help` works (stub implementation)
- [ ] `ai-tools skill catalog run --help` works (stub implementation)
- [ ] `mdq` added to brewfile and verified working

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Tier 1 agent | `content/agents/catalog/skill-inspector-t1.md` | Markdown (agent def) |
| Tier 2 agent | `content/agents/catalog/skill-inspector-t2.md` | Markdown (agent def) |
| Catalog justfile | `content/skills/.catalog/justfile` | Just |
| CLI stubs | `cli/commands/skill.ts` (additions) | TypeScript |

## Files

**Create:**
- `content/agents/catalog/skill-inspector-t1.md`
- `content/agents/catalog/skill-inspector-t2.md`
- `content/skills/.catalog/justfile`

**Modify:**
- `content/skills/justfile` — add `mod catalog ".catalog/justfile"`
- `cli/commands/skill.ts` — add `catalog analyze|grade|stats|search|run` stubs
- `brewfile` — add `mdq`

## Tasks

### Agent Definitions
- [ ] Write `skill-inspector-t1.md`:
  - System prompt: "You are a batch skill analyzer. For each skill in the batch..."
  - Allowed tools: `Bash(npx:*,mdq:*,wc:*,find:*,stat:*,curl:*,mktemp:*,rm:*)`, `Read`, `Glob`, `Grep`
  - Input format: list of `owner/repo@skill` entries
  - Output format: NDJSON to stdout, one line per skill
  - Include the full Tier 1 checklist (metadata, keywords, complexity, PD, mechanical best practices, regex security, fork hash)
  - Include error handling: if `npx skills add` fails for a skill, emit an error entry and continue
  - Include worktree setup/teardown instructions
- [ ] Write `skill-inspector-t2.md`:
  - System prompt: "You are a qualitative skill reviewer. For each skill..."
  - Same allowed tools as Tier 1
  - Input format: NDJSON entries from Tier 1 (with downloaded skill paths)
  - Output format: NDJSON merge entries (contentQuality, bestPractices judgment, security injection review)
  - Include the Tier 2 checklist (content quality, actionable trigger, prompt injection)
  - Include gating criteria: only review if `availability==available && possibleForkOf==null && (complexity!="simple" || wordCount>=200)`

### Catalog Justfile Module
- [ ] Create `content/skills/.catalog/justfile` with recipes:
  - `run *FLAGS` — full pipeline: taxonomy → availability → analyze → grade
  - `taxonomy *FLAGS` — Phase 1
  - `availability *FLAGS` — Phase 2
  - `analyze *FLAGS` — Phase 4+5 (Tier 1 then Tier 2)
  - `grade *FLAGS` — Phase 6
  - `stats *FLAGS` — show summary
  - `search *FLAGS` — query catalog
  - `cleanup` — remove orphan worktrees
- [ ] All recipes delegate to `bun run cli/bin/ai-tools.ts skill catalog <verb>`
- [ ] Add `mod catalog ".catalog/justfile"` to `content/skills/justfile`

### CLI Stubs
- [ ] Add `catalog` subcommand to `commands/skill.ts` with Citty subcommands:
  - `taxonomy`, `availability`, `analyze`, `grade`, `stats`, `search`, `run`
- [ ] Each stub: parse args, print "not yet implemented", exit 0
- [ ] Real implementation comes in Phases 1, 2, 4, 5, 6

### Brewfile Update
- [ ] Add `mdq` to brewfile: `brew "yshavit/mdq/mdq"` (or verify tap name)
- [ ] Verify `mdq -o json` works after install

## Notes

- This phase has no data dependencies — can run in parallel with Phases 1 and 2
- Agent definitions follow the pattern in `content/agents/` (see existing agents for format reference)
- The justfile module pattern matches `.external/justfile` from the external skill tracking design
- CLI stubs allow other phases to be developed against the command interface without blocking
