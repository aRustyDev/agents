# ADR-026: Use Blue/Green Switches for Feature Migration

## Status

Accepted

## Context

Replacing an established code path with a new implementation carries risk proportional to the blast radius. When the old and new paths have meaningfully different characteristics — different error types, different I/O patterns, different failure modes — a hard cutover risks discovering bugs only after they've affected real data, with no rollback short of reverting commits.

This pattern emerged during the catalog download pipeline replacement (ADR-024), but applies to any migration where:

- The old path is working in production (even if imperfectly)
- The new path has different observable behavior (better errors, different performance, new edge cases)
- Rollback must be instant (no redeploy, no git revert)
- Validation requires running on real data, not just tests

## Decision Drivers

1. **Instant rollback** — must revert to the old path via a flag, not a code change
2. **Production validation** — new path must be confirmed on real data before legacy removal
3. **No double-cost** — shadow mode (running both paths) is not acceptable for resource-heavy operations
4. **Clear removal signal** — legacy path removal must have an observable, documented criterion

## Considered Options

### Option 1: Hard Cutover

Delete old code, replace with new. Deploy and observe.

- Pro: Clean codebase immediately; no flag complexity
- Con: No rollback without git revert; bugs discovered only in production; loss of comparison baseline

### Option 2: CLI Flag with Blue/Green Switch (Chosen)

Boolean flag (default: new path) selects between old and new implementations at the call site.

- Pro: Instant rollback via flag; both paths coexist during validation; flag removed with legacy code after validation
- Con: Two code paths to maintain during the validation window; flag visible in `--help`

### Option 3: Shadow Mode

Run both paths for every invocation, compare results, log divergences.

- Pro: Maximum observability
- Con: Doubles resource usage; impractical for I/O-heavy operations; complex comparison logic

## Decision

**For high-risk code path replacements, introduce a boolean flag that defaults to the new path (green) and falls back to the old path (blue) when set.**

The pattern:

```typescript
if (opts.legacyFoo) {
  // blue: old implementation (preserved for rollback)
} else {
  // green: new implementation (default)
}
```

**Naming convention:** `--legacy-<feature>` — the negative framing communicates "escape hatch, not supported mode."

**Validation criterion:** Define before implementing. Example: "2+ successful batch runs, N+ items processed, no regressions vs baseline." Document the criterion in the plan.

**Removal timing:** Remove the blue path in a separate commit immediately after validation passes. Don't let it linger — dead code accumulates.

### When to use this pattern

- Replacing a data pipeline's I/O path
- Swapping authentication mechanisms
- Changing serialization formats
- Migrating from exec-based to library-based implementations

### When NOT to use this pattern

- Pure refactors with identical observable behavior (just refactor)
- New features with no predecessor (no blue path exists)
- Changes with comprehensive test coverage and low blast radius

## Consequences

### Positive

- Zero-downtime migration — flag is an instant rollback
- Validation on real data builds confidence before full commitment
- Pattern is reusable across the codebase for future migrations

### Negative

- Temporary code duplication during the validation window
- Flag appears in `--help` output, potentially confusing users
- Discipline required to remove legacy code promptly after validation

### Neutral

- The flag name convention (`--legacy-*`) discourages routine use
- Error counts from blue and green paths may not be directly comparable due to different classification
