# Stage 8-13 Remediation Plan

> Addressing gaps identified in pipeline refactor stages, ordered by severity.

## Overview

| Severity | Count | Status |
|----------|-------|--------|
| 🔴 Critical | 3 | ✅ Complete |
| 🟡 Medium | 5 | ✅ Complete |
| 🟢 Minor | 4 | ✅ Complete |

---

## 🔴 Critical Fixes

### C1: Define Missing Types in Stage 8 ✅

**Problem**: Several types are referenced but never defined:
- `RawFeedback` - used in Stage 9 but defined in Stage 12
- `ActionGroup` - referenced in Stage 10.7, 12.3
- `FixResult` - referenced in Stage 10.7, 12.3
- `Location` - needed for ActionGroup
- `TokenUsage` - needed for OTEL metrics

**Solution**: Add all types to Stage 8 (data models) to eliminate circular dependencies.

**Files Modified**: `stage-8-data-models.md` (section 8.8 added)

---

### C2: Document Missing Modules ✅

**Problem**: These modules are imported but never defined in stages 8-13:
- `src/discovery.py` - PR info and feedback fetching
- `src/consolidate.py` - LLM consolidation logic
- `src/planner.py` - Execution plan creation
- `src/commit.py` - Git commit and PR comment operations

**Solution**: Create Stage 7.5 documenting these as prerequisites from earlier stages, with interface contracts.

**Files Created**: `stage-7.5-prerequisites.md`

---

### C3: Fix Circular Dependency ✅

**Problem**: Stage 9 imports `RawFeedback` which is defined in Stage 12.

**Solution**: Already addressed by C1 - moving `RawFeedback` to Stage 8.

---

## 🟡 Medium Fixes

### M1: Cross-Reference Integration Not Consumed ✅

**Problem**: Stage 9 sets `thread.linked_to_review` but consolidation doesn't use it.

**Solution**: Update Stage 12 consolidation stage to pass links to consolidator and handle linked threads as group.

**Files Modified**: `stage-12-pipeline.md`
- Added `_extract_thread_links()` helper in `_stage_filter`
- Added `thread_links` parameter to `_stage_consolidate`
- Added `thread_links` field to `ConsolidatedFeedback` and `PipelineContext`

---

### M2: Missing Worktree Management ✅

**Problem**: Pipeline assumes worktree exists but doesn't manage it.

**Solution**: Add worktree setup/teardown to Stage 10 infrastructure.

**Files Modified**: `stage-10-infrastructure.md` (section 10.9 added)

---

### M3: External Dependency Undeclared ✅

**Problem**: `skill_agents_common.session.AgentSession` imported but not documented.

**Solution**: Add dependencies section to Stage 12 with pip install requirements and fallback implementation.

**Files Modified**: `stage-12-pipeline.md` (External Dependencies section added)

---

### M4: Rate Limit Hook Never Triggered ✅

**Problem**: `on_rate_limit` hook defined but never called.

**Solution**: Add rate limit detection to Stage 10 GitHub operations.

**Files Modified**: `stage-10-infrastructure.md` (section 10.10 added)

---

### M5: Token Usage Tracking Incomplete ✅

**Problem**: OTEL hooks reference `token_usage` but structure undefined.

**Solution**: Already addressed by C1 - adding `TokenUsage` dataclass to Stage 8.

---

## 🟢 Minor Fixes

### m1: Test Fixtures Incomplete ✅

**Problem**: Test examples use `...` placeholders that won't compile.

**Solution**: Replace all `...` with complete fixture data in Stage 13.

**Files Modified**: `stage-13-testing.md`
- Fixed `TestMarkLinkedThreads` with complete data
- Fixed `TestLinkReviewsToThreads` with complete data
- Fixed `TestE2EDryRun` and `TestE2EFullRun` with complete mock data

---

### m2: Deprecated datetime Usage ✅

**Problem**: Uses `datetime.utcnow()` which is deprecated.

**Solution**: Replace with `datetime.now(timezone.utc)` across all stages.

**Files Modified**:
- `stage-12-pipeline.md` (in `_load_progress`)
- `stage-13-testing.md` (all test methods updated with timezone-aware datetimes)

---

### m3: Inconsistent Logging Pattern ✅

**Problem**: Mixed usage of `ctx.app.log`, `ctx.log()`, `app.log`.

**Solution**: Standardize on `ctx.app.log` pattern, remove `ctx.log()` method.

**Files Modified**: `stage-12-pipeline.md`
- Removed `ctx.log()` helper method from `PipelineContext`
- Added docstring clarifying logging convention

---

### m4: Missing PR Comment Format ✅

**Problem**: `post_pr_comment` referenced but format not defined.

**Solution**: Add comment template to Stage 10.

**Files Modified**: `stage-10-infrastructure.md` (section 10.11 added)

---

## Implementation Order

1. ✅ **Stage 7.5** - Create prerequisites document (C2)
2. ✅ **Stage 8** - Add missing types (C1, C3, M5)
3. ✅ **Stage 10** - Add worktree, rate limit, PR comment format (M2, M4, m4)
4. ✅ **Stage 12** - Add cross-ref integration, dependencies, fix logging (M1, M3, m3)
5. ✅ **Stage 13** - Fix test fixtures, datetime usage (m1, m2)

---

## Validation Checklist

After implementing all fixes:

- [x] No circular imports between stages
- [x] All referenced types are defined before use
- [x] All imported modules are documented
- [x] Test code compiles without `...` placeholders
- [x] No deprecated `datetime.utcnow()` usage
- [x] Rate limit hook has trigger path
- [x] Cross-references flow to consolidation
- [x] Worktree lifecycle is managed
