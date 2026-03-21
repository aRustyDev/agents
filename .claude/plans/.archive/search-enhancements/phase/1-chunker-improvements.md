---
id: 3211e30a-5f8a-4920-b889-1ec70ffcbe71
project:
  id: 00000000-0000-0000-0000-000000000000
title: "Phase 1: Chunker Improvements"
status: pending
related:
  depends-on: [33e4f823-9e9d-4e9b-8e5d-62ab50d07466]
---

# Phase 1: Chunker Improvements

**ID:** `phase-1`
**Dependencies:** None
**Status:** pending
**Effort:** Small

## Objective

Add chunk overlap and title-context prepending to improve embedding quality. These are small, targeted changes to existing modules.

## Success Criteria

- [ ] `chunkMarkdown()` accepts `overlapChars` option (default: 256, ~64 tokens)
- [ ] Paragraph chunks include trailing content from the previous chunk when overlap > 0
- [ ] Title/heading is prepended to chunk text when generating embeddings
- [ ] Existing tests still pass (backward compatible — overlap defaults to 0 in tests that check exact output)
- [ ] New tests verify overlap content and title prepending

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Updated chunker | `cli/lib/chunker.ts` | TypeScript |
| Updated embedder | `cli/lib/embedder.ts` | TypeScript |
| Updated tests | `cli/test/chunker.test.ts` | TypeScript |

## Files

**Create:**
- None

**Modify:**
- `cli/lib/chunker.ts` — add `overlapChars` option to `chunkMarkdown()` and `splitIntoParagraphs()`
- `cli/lib/embedder.ts` — add `prepareEmbeddingText(title: string, chunk: string): string` helper
- `cli/test/chunker.test.ts` — add overlap tests

## Tasks

### Chunk overlap
- [ ] Add `overlapChars?: number` to `ChunkOptions` (default: 0 for backward compat)
- [ ] In `splitIntoParagraphs()`, when overlap > 0, prepend the last `overlapChars` characters from the previous paragraph to each subsequent paragraph
- [ ] Skip overlap for the first paragraph (no previous content)
- [ ] Add smart split-point detection for overlap boundary: prefer paragraph break > sentence end > word boundary (don't cut mid-word)

### Title context prepending
- [ ] Add `prepareEmbeddingText(entityName: string, chunkText: string): string` to `lib/embedder.ts`
- [ ] Format: `"${entityName}\n\n${chunkText}"`
- [ ] This function is called by the embedding pipeline, not by the chunker itself (separation of concerns)

### Tests
- [ ] Test overlap: chunk with `overlapChars: 256`, verify second chunk starts with content from end of first chunk
- [ ] Test overlap: verify first chunk has no prepended content
- [ ] Test overlap: verify overlap doesn't exceed available content from previous chunk
- [ ] Test `prepareEmbeddingText()`: verify format
- [ ] Test backward compat: `overlapChars: 0` produces same output as before

## Notes

- Token estimation: ~4 chars per token, so 256 chars ≈ 64 tokens (matching mdq's approach)
- The overlap is applied at the paragraph level, not the section level
- Title prepending happens at embedding time, not chunking time — chunks stored without title prefix, embedding includes it
