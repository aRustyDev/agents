# Phase Plans Review: Round 2

> **Date**: 2026-03-14 (post-fix review)
> **Status**: All fixes applied on 2026-03-14

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Gaps | 7 | ✅ Fixed |
| Inconsistencies | 4 | ✅ Fixed |
| Minor Issues | 3 | ✅ Fixed |

Overall the plans are now complete after both rounds of fixes. All review checklists are defined, artifact paths are specified, and consistency issues are resolved.

---

## Gaps

### 1. Missing Review Checklists for Research Artifacts (Phase 3)

**Issue**: Phase 3 creates research findings and analysis artifacts, but there are no review checklists for them.

**Current checklists**: `research-plan.md` only

**Missing**:

- `research-findings.md` — for evaluating source quality, coverage, documentation
- `research-analysis.md` — for evaluating synthesis quality, insight depth

**Impact**: The `research/review.md` command "evaluates analysis quality" but has no checklist to reference.

**Fix**: Add to Phase 3 deliverables:

- `content/_templates/review-checklists/research-findings.md`
- `content/_templates/review-checklists/research-analysis.md`

---

### 2. Missing Review Checklists for Post Spec/Outline (Phase 5)

**Issue**: Post spec and outline use self-review but have no dedicated checklists.

**Current checklist**: `post-draft.md` only

**Missing**:

- `post-spec.md` — for evaluating audience definition, takeaways, prerequisites
- `post-outline.md` — for evaluating structure, word estimates, section balance

**Impact**: Self-review in `post/spec.md` and `post/plan.md` have no criteria to check against.

**Fix**: Add to Phase 5 deliverables:

- `content/_templates/review-checklists/post-spec.md`
- `content/_templates/review-checklists/post-outline.md`

---

### 3. Missing Phase File Checklist (Phase 4)

**Issue**: Individual phase files are created but have no review checklist.

**Current**: `content/review.md` validates overall decomposition, but not individual phase quality.

**Missing**:

- `phase.md` — for evaluating single phase scope, prerequisites, feasibility

**Fix**: Add to Phase 4 deliverables:

- `content/_templates/review-checklists/phase.md`

---

### 4. Content-Plan Artifact Path Undefined (Phase 4)

**Issue**: Phase 4 creates a `content-plan` artifact but doesn't specify the file path.

**Current**: `draft.md` says "Create content-plan artifact" but no path given.

**Expected path**: `content/_projects/<slug>/content-plan.md`

**Fix**: Clarify in Phase 4 `draft.md` behavior:

```text
**Output**: `content/_projects/<slug>/content-plan.md` (`type: content-plan`)
```

---

### 5. Project README.md Creation Timing (Phase 1)

**Issue**: Phase 0 creates the README template, but no phase actually creates `README.md` in projects.

**Expected**: When a project is created via `brainstorm.md`, it should also create `README.md` from the template.

**Fix**: Add to Phase 1 `brainstorm.md` logic:

```text
5. Create `README.md` from project-readme.md template
```

---

### 6. Missing `brainstorm-plans/` and `schemas/` in Plugin requiredDirectories (Phase 7)

**Issue**: The plugin manifest lists required directories but omits two that `/blog:init` creates.

**Current `requiredDirectories`**:

```json
[
  "content/_projects",
  "content/_drafts",
  "content/_templates/personas",
  "content/_templates/outlines",
  "content/_templates/research-plans",
  "content/_templates/review-checklists"
]
```

**Missing**:

- `content/_templates/brainstorm-plans`
- `content/_templates/schemas`

**Fix**: Add to Phase 7 plugin manifest `requiredDirectories`.

---

### 7. Self-Review Mechanism Needs Clarification (All Phases)

**Issue**: Plans mention "self-review" but don't specify which checklist subset is used or how it differs from full review.

**Current**: "Run self-review (fail items only)"

**Needed**: Explicit statement like:
> Self-review uses the same checklist as the dedicated review command, but only flags `fail` items (warnings are left for dedicated review).

**Fix**: Add a "Self-Review Standard" section to Phase 0 or PLAN.md explaining the mechanism.

---

## Inconsistencies

### 1. Template File Naming Mismatch (Phase 2)

**Issue**: Source templates use `.outline.md` suffix, but Phase 2 refers to them without clear suffix.

**Source files**: `tutorial.outline.md`, `dev-blog.outline.md`, etc.

**Phase 2 text**: "Copy 18 templates... to `content/_templates/outlines/`"

**Ambiguity**: Are files renamed to `tutorial.md` or kept as `tutorial.outline.md`?

**Fix**: Clarify in Phase 2 that templates are copied with their original names (`tutorial.outline.md`) OR explicitly state they're renamed.

---

### 2. Duplicate Section Numbering (Phase 7)

**Issue**: Phase 7 has two sections numbered "7":

- "7. Hook Delegation Model"
- "7. README.md"

**Fix**: Renumber to:

- "7. Hook Delegation Model"
- "8. README.md"

---

### 3. Plugin Template Directory vs Content Directory Naming

**Issue**: Plugin bundles templates at `templates/` but copies to `content/_templates/`.

**Plugin structure**:

```text
templates/
├── outlines/
├── personas/
```

**Repo structure**:

```text
content/_templates/
├── outlines/
├── personas/
```

**Status**: This is actually correct (plugin uses `templates/`, repo uses `content/_templates/`), but should be explicitly documented.

**Fix**: Add clarifying comment in Phase 7 about the rename during copy.

---

### 4. Review Command Status Update Inconsistency

**Issue**: Some review commands update status to `in-review`, others don't mention it.

**Phase 1 review.md**: "Update artifact status → `in-review`" ✅
**Phase 3 spec/review.md**: "Update artifact status → `in-review`" ✅
**Phase 4 review.md**: No status update mentioned ❌
**Phase 5 review.md**: "Update status → `in-review`" ✅

**Fix**: Add status update to Phase 4 `review.md` logic.

---

## Minor Issues

### 1. Estimated Effort Total Mismatch

**PLAN.md total**: 22-30 hours
**Sum of phases**: 1-2 + 3-4 + 2-3 + 4-5 + 3-4 + 4-5 + 3-4 + 2-3 = 22-30 hours ✅

Actually this matches. No issue.

### 2. Entry Points Section Position

**Issue**: Entry Points sections appear after Acceptance Tests in some phases, before in others.

**Phases 3, 4, 5, 6**: Entry Points after Acceptance Tests
**Suggestion**: Standardize position (recommend: before Dependencies, after Acceptance Tests)

### 3. Missing index.md Update in refine Commands

**Issue**: Most `refine.md` commands don't explicitly mention updating `index.md`.

**Phase 1 refine.md**: "Update `index.md`" ✅
**Phase 3 refine.md**: No mention ❌
**Phase 4 refine.md**: No mention ❌
**Phase 5 refine.md**: No mention ❌

**Fix**: Add "Update `index.md` with status change" to refine commands in Phases 3, 4, 5.

---

## Action Items

### High Priority

1. [x] Add missing research checklists: `research-findings.md`, `research-analysis.md` (Phase 3)
2. [x] Add missing post checklists: `post-spec.md`, `post-outline.md` (Phase 5)
3. [x] Add `phase.md` checklist (Phase 4)
4. [x] Define content-plan artifact path (Phase 4)

### Medium Priority

5. [x] Add README.md creation to brainstorm command (Phase 1)
6. [x] Add `brainstorm-plans`, `schemas` to requiredDirectories (Phase 7)
7. [x] Document self-review mechanism (Phase 0)
8. [x] Clarify template file naming (Phase 2)

### Low Priority

9. [x] Fix duplicate section numbering (Phase 7)
10. [x] Add status update to content/review.md (Phase 4)
11. [x] Add index.md update to refine commands (Phases 3, 4, 5)
12. [x] Standardize Entry Points section position — already consistent (after Acceptance Tests, before Dependencies)
