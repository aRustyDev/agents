---
id: 8f03a234-a8f6-45a8-ab63-5515fee9706d
project:
  id: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
status: pending
related:
  depends-on: [b62a5469-b722-4cee-ad9a-41c7f446d0ad]
---

# Phase 4: Tier 1 Analysis Refactor

**ID:** `phase-4`
**Dependencies:** phase-3
**Status:** complete
**Effort:** Medium

## Objective

Refactor the Tier 1 Haiku agent to receive ALL mechanical data pre-computed and perform judgment-only analysis. The agent does zero I/O — no file reads, no shell commands, no tool use. It receives a structured manifest and returns structured judgments.

## Success Criteria

- [ ] Agent prompt contains zero tool-use instructions (no `Read`, `Glob`, `Grep`)
- [ ] Agent receives pre-computed manifest: content, headingTree, sectionMap, wordCount, fileTree, keywords (mechanical), contentHash
- [ ] Agent produces judgment-only output: complexity, progressiveDisclosure, pdTechniques, bestPracticesMechanical, securityMechanical, refined keywords
- [ ] Agent output is pure NDJSON — no markdown fences, no prose
- [ ] `catalog analyze` uses discovery results (Phase 2) as input, not its own download logic
- [ ] ALLOWED_TOOLS reduced to empty set (or removed entirely)
- [ ] Agent cost per skill reduced (smaller prompt, no tool round-trips)

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Refactored agent prompt | `cli/commands/skill.ts` | String template in `processBatch` |
| Manifest builder | `cli/lib/catalog-manifest.ts` | TypeScript module |
| Tier1 judgment type | `cli/lib/catalog.ts` | TypeScript interface |
| Tests | `cli/test/catalog-manifest.test.ts` | bun:test |

## Files

**Create:**
- `cli/lib/catalog-manifest.ts` — builds the pre-computed manifest for agent consumption
- `cli/test/catalog-manifest.test.ts`

**Modify:**
- `cli/commands/skill.ts` — refactor `processBatch` to use discovery + manifest flow
- `cli/lib/catalog.ts` — add `Tier1Judgment` interface (agent-only output fields)

## Tasks

- [ ] Define `Tier1Judgment` interface: complexity, progressiveDisclosure, pdTechniques, bestPracticesMechanical, securityMechanical, refinedKeywords
- [ ] Define `SkillManifest` interface: source, skill, content (full SKILL.md text), wordCount, sectionCount, fileCount, headingTree, sectionMap, fileTree, contentHash, mechanicalKeywords, isSimple
- [ ] Implement `buildManifest(entry, discoveryResult)` — assembles the manifest from discovery data
- [ ] Rewrite agent prompt to receive manifest and return judgment-only NDJSON
- [ ] Remove ALLOWED_TOOLS from agent dispatch (agent needs no tools)
- [ ] Refactor `processBatch` to: (1) read discovery results, (2) build manifests, (3) dispatch agent, (4) merge judgments
- [ ] Add `--skip-discovery` flag: errors if `.catalog-repos.ndjson` absent, warns if last discovery >24h old, uses cached discovery data
- [ ] Validate agent output schema (reject malformed NDJSON before merging)
- [ ] Compare quality: run 100 skills through old vs new prompt — validation criterion: >90% agreement on `complexity` classification, zero regressions in FullyComplete count
- [ ] Blue/green: `--legacy-analyze` flag during validation (ADR-026 pattern) — removal criterion: 2+ successful batch runs (500+ skills), no regressions vs baseline

## Agent Prompt Design

### Current (judgment + mechanical mixed)

```
You are a skill inspector. For each skill:
1. Read the SKILL.md
2. Extract keywords from headings
3. Check for <details> blocks
4. Assess complexity
5. Check for security concerns
Output NDJSON.
```

### Proposed (judgment only, pre-computed data provided)

```
You are a skill quality assessor. You receive pre-computed mechanical data
for each skill. Your job is JUDGMENT ONLY — assess quality, complexity,
and patterns. Do NOT read files or run commands.

For each skill in the manifest below, output ONE NDJSON line with:
- complexity: "simple" | "moderate" | "complex"
- progressiveDisclosure: true | false
- pdTechniques: string[] (e.g., ["details-blocks", "collapsible-sections"])
- bestPractices: { score: 1-10, violations: string[] }
- security: { score: 1-10, concerns: string[] }
- refinedKeywords: string[] (improve/expand the mechanical keywords)

MANIFEST:
<pre-computed data for batch of skills>
```

## Notes

- The agent prompt size shrinks significantly because we're not including tool-use instructions
- The manifest includes the full SKILL.md content so the agent can read it inline
- `refinedKeywords` lets the agent improve on mechanical keyword extraction (e.g., adding domain-specific terms the heading parser missed)
- This is a "judgment amplification" pattern — mechanical data provides the scaffolding, LLM provides the insight
