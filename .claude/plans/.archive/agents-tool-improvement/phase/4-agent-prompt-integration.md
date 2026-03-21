# Phase 4: Agent Prompt + Orchestrator Integration

**ID:** `phase-4`
**Dependencies:** phase-1, phase-2
**Status:** pending
**Effort:** Medium

## Objective

Wire the mechanical compute functions (Phase 2) into `preDownloadSkills`, reduce the Haiku agent prompt from 9 steps to 5 judgment-only steps, update `--allowedTools` to remove Bash, ensure the orchestrator's mechanical data takes merge priority over agent output, and add automated post-batch validation.

## Success Criteria

- [ ] `preDownloadSkills` computes `contentHash`, `wordCount`, `fileCount`, `sectionCount`, `headingTree` after successful download
- [ ] Agent manifest includes pre-computed metrics for each skill
- [ ] Agent prompt reduced to 5 steps: keywords, progressive disclosure, best practices, security, complexity (using provided metrics)
- [ ] `--allowedTools` changed to `"Read Glob Grep"` (no Bash)
- [ ] Stronger NDJSON-only output instruction in prompt
- [ ] `processBatch` merges orchestrator mechanical data as authoritative, agent judgment data on top
- [ ] `processBatch` routes errors to error log (Phase 1) via `mergeTier1Results(catalogPath, errorLogPath, results)`
- [ ] `validateBatchResults` function catches `sha256:pending`, missing `contentHash`, and missing `wordCount`
- [ ] Test batch of 5 skills produces clean results with real content hashes and no prose wrapping

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Updated `preDownloadSkills` | `cli/commands/skill.ts` | TypeScript |
| Reduced agent prompt | `cli/commands/skill.ts` | TypeScript |
| Updated merge logic in `processBatch` | `cli/commands/skill.ts` | TypeScript |
| `validateBatchResults` function | `cli/lib/catalog.ts` | TypeScript |
| Validation tests | `cli/test/catalog-tier1.test.ts` | TypeScript |
| Integration test results | Manual test batch | NDJSON |

## Files

**Create:**

- None

**Modify:**

- `cli/lib/catalog.ts` — add `validateBatchResults` function
- `cli/commands/skill.ts` — update `preDownloadSkills` to call compute functions, update manifest format, rewrite agent prompt, change `ALLOWED_TOOLS`, update `processBatch` merge logic and error routing, call `validateBatchResults` after merge
- `cli/test/catalog-tier1.test.ts` — tests for validation function

## Tasks

- [ ] Update `preDownloadSkills`: after confirming `SKILL.md` exists, read content and call `computeContentHash`, `computeWordCount`, `computeSectionCount`, `computeHeadingTree`, `computeFileCount`
- [ ] Attach computed fields to `DownloadResult`
- [ ] Update manifest format: include `wordCount`, `sectionCount`, `fileCount`, `contentHash` in each skill entry
- [ ] Rewrite agent prompt:
  - Remove steps 2-4 and 9 (wc, headings, find, shasum)
  - Keep: read SKILL.md, keywords, progressive disclosure, best practices, security
  - Add: "Use the provided wordCount/sectionCount/fileCount to determine complexity"
  - Strengthen: "Output ONLY raw JSON lines. No markdown, no code fences, no prose."
- [ ] Change `ALLOWED_TOOLS` from `"Bash(mdq:*,wc:*,...) Read Glob Grep"` to `"Read Glob Grep"`
- [ ] Update `processBatch` merge: orchestrator's mechanical fields (`contentHash`, `wordCount`, `sectionCount`, `fileCount`, `headingTree`) are written directly, not from agent output
- [ ] Update `processBatch` to pass `errorLogPath` to `mergeTier1Results`
- [ ] Implement `validateBatchResults(results: Tier1Result[]): ValidationReport`:

  ```typescript
  interface ValidationReport {
    total: number
    missingContentHash: number    // entries without contentHash
    pendingContentHash: number    // entries with "sha256:pending" or similar
    missingWordCount: number      // entries without wordCount
    missingKeywords: number       // entries without keywords array
    issues: string[]              // human-readable issue descriptions
  }
  ```

  - Called after each batch merge, logged to stderr as warnings
  - Called at end of run with aggregated results, logged as summary
- [ ] Run test batch: `just agents skill catalog analyze --limit 1 --batch-size 5 --force`
- [ ] Verify: real content hashes, no `sha256:pending`, no prose wrapping in output
- [ ] Verify: validation report shows 0 issues

## Notes

- This phase depends on Phase 1 (error routing to log) and Phase 2 (compute functions)
- The agent definition files in `context/agents/catalog/` are NOT used by the orchestrator — it builds inline prompts. No changes to agent definition files needed.
- The manifest JSON passed to the agent will be larger (includes metrics per skill) but the prompt itself is shorter (5 steps vs 9), net reduction in tokens
- After this phase, the Haiku agent has no Bash access — it can only Read/Glob/Grep files in the worktree
- The `validateBatchResults` function is a safety net — with mechanical compute in the orchestrator, `contentHash` and `wordCount` should never be missing. But if they are, we catch it immediately instead of discovering it in a post-hoc analysis.
