# Phase Plans Review: Gaps & Inconsistencies

> **Status**: All fixes applied on 2026-03-14

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Critical Gaps | 3 | ✅ Fixed |
| Minor Gaps | 6 | ✅ Fixed |
| Inconsistencies | 8 | ✅ Fixed |

---

## Critical Gaps

### 1. Missing `README.md` Template (Phase 0)

**SPEC Reference**: Line 222 shows `README.md` in project structure

```text
content/_projects/<slug>/
├── ...
└── README.md             # Human-readable summary
```

**Phase 0 Status**: Not mentioned in deliverables

**Fix**: Add to Phase 0 deliverables:

- Create `content/_templates/project-readme.md` template
- Add task: "Create README.md template with sections for overview, status, links"

---

### 2. Post Artifact Storage Location Undefined (Phase 5)

**SPEC Reference**: Lines 140-148 define post artifacts (post-spec, post-outline) but don't explicitly state where they're stored within the project.

**Phase 5 Status**: Says "Post spec (`type: post-spec`)" but doesn't specify path

**Fix**: Clarify in Phase 5 that post artifacts go in project directory:

```text
content/_projects/<slug>/
├── ...
└── posts/                    # NEW: post artifacts
    ├── <post-slug>/
    │   ├── spec.md           # type: post-spec
    │   └── outline.md        # type: post-outline
```

Or inline with phase:

```text
content/_projects/<slug>/
├── phase/
│   ├── 0-tutorial.md         # phase file
│   ├── 0-tutorial-spec.md    # post-spec for phase 0
│   └── 0-tutorial-outline.md # post-outline for phase 0
```

**Decision needed**: Which storage pattern?

---

### 3. Missing `brainstorm-plans/` Template (Phase 0, 3, 7)

**SPEC Reference**: Line 201 lists `brainstorm-plans/` as a template type, Line 319 shows `standard.md`

**Current Status**:

- Phase 0: Creates directory but no template
- Phase 3: Creates `research-plans/standard.md` but no brainstorm template
- Phase 7: Bundles templates but doesn't mention `brainstorm-plans/`

**Fix**:

- Phase 0: Add task to create `content/_templates/brainstorm-plans/standard.md`
- Phase 7: Add `brainstorm-plans/` to bundled templates

---

## Minor Gaps

### 4. Second Seed Persona Missing (Phase 2)

**SPEC Reference**: Line 309 shows `educator.md` as example persona

**Phase 2 Status**: Only seeds `practitioner.md`

**Fix**: Add `educator.md` to Phase 2 seed personas (optional, but helpful for demonstrating variety)

---

### 5. Missing spec/review index.md Update (Phase 3)

**SPEC Reference**: Line 280-283 states every command must update index.md

**Phase 3 Status**: `spec/review.md` behavior says "Update status → `in-review`" but doesn't mention index.md

**Fix**: Add to spec/review.md logic: "6. Update `index.md` with artifact status change"

---

### 6. Draft File Deletion Ambiguity (Phase 6)

**Phase 6 Status**: `promote.md` says "Remove from `content/_drafts/`"

**Ambiguity**: Does "remove" mean delete or move? SPEC is also ambiguous (line 166: "Moves file")

**Fix**: Clarify: "Delete the file from `content/_drafts/<slug>.md` (it's now in `src/data/blog/`)"

---

### 7. Entry Point Flexibility Not Documented (Phase 4, 5)

**SPEC Reference**: Lines 565-571 show multiple entry points

**Current Status**: Phase 4 and 5 dependencies suggest linear flow only

**Fix**: Add "Entry Points" section to Phase 4 and 5:

- Phase 4: "Can be entered directly with existing research (skip Phase 3)"
- Phase 5: "Can be entered directly with a phase file or even manually created spec"

---

### 8. Plan Review Checklist Missing (Phase 1)

**SPEC Reference**: Line 86 shows `review.md` auto-detects idea vs plan

**Phase 1 Status**: Creates `idea.md` checklist but no `plan.md` checklist

**Fix**: Add task to create `content/_templates/review-checklists/plan.md` for project plan review

---

### 9. Hook `${CLAUDE_PROJECT_ROOT}` vs `.claude/hooks/` Confusion (Phase 6, 7)

**Phase 6**: Creates hooks at `.claude/hooks/` in repo
**Phase 7**: Plugin references `${CLAUDE_PROJECT_ROOT}/.claude/hooks/`

**Ambiguity**: Where do hooks actually live? Plugin cache or repo?

**Fix**: Clarify the delegation model:

1. Plugin ships stub hooks that delegate to repo
2. Repo has the actual implementation at `.claude/hooks/`
3. Both work independently (repo hooks work without plugin)

---

## Inconsistencies

### 1. Persona Verification Timing (Phase 1 vs Phase 2)

**Phase 1**: `brainstorm.md` logic step 2 says "Check for persona configuration (prompt if none)"

**Phase 2**: Says "Update Phase 1 commands to check for persona"

**Problem**: Phase 1 can't check for persona if persona commands don't exist yet

**Fix**: Phase 1 should say:

- "If persona system exists (Phase 2 complete), check for persona"
- "Otherwise, skip persona verification (will be added in Phase 2)"

Or: Move persona check to Phase 2's integration task only.

---

### 2. Dependencies Listed as Required When Optional (Phase 4, 5)

**Phase 4 Dependencies**: "Phase 3 (Research) — needs research report"
**Phase 5 Dependencies**: "Phase 4 (Content Planning) — needs phase files"

**SPEC Reality**: Entry points table (lines 565-571) shows these are optional

**Fix**: Change to:

- Phase 4: "Phase 3 (Research) — *or* existing research from another source"
- Phase 5: "Phase 4 (Content Planning) — *or* manually created phase file"

---

### 3. Project Status Transitions Not Fully Specified (All Phases)

**SPEC Reference**: Lines 256-264 define project status values

**Current Status**: Only Phase 6 mentions updating project status to `complete`

**Fix**: Add project status transitions to each phase:

- Phase 1: `ideation` (set on project creation)
- Phase 3: `research` (set when research starts)
- Phase 4: `content-planning` (set when content planning starts)
- Phase 5: `post` (set when post writing starts)
- Phase 6: `publish` → `complete` (on promote)

---

### 4. Index.md Template Location Unclear (Phase 0)

**Phase 0**: Creates `content/_templates/project-index.md`

**Problem**: This is documentation, not a fillable template. Should be either:

- A reference doc in `content/_templates/`
- Or just inline in the command that creates new projects

**Fix**: Clarify purpose:

- Keep as reference template for commands to copy/adapt
- Or rename to `content/_templates/schemas/project-index-schema.md` to distinguish from fillable templates

---

### 5. Plugin Template Copying Flow Missing (Phase 7)

**Phase 7**: Says plugin bundles templates at `templates/outlines/` etc.

**Missing**: How do bundled templates get to user's `content/_templates/`?

**Fix**: Add to Phase 7:

- First-run initialization skill: `/blog:init`
- Copies bundled templates to `content/_templates/` if not present
- Acceptance test: "Plugin initialization copies templates to repo"

---

### 6. Research Spec Refine Path Ambiguous (Phase 3)

**SPEC Reference**: Line 108 says `refine.md` accepts "Any research artifact"

**Phase 3**: Lists `spec/refine.md` as a command but SPEC only has top-level `refine.md`

**Reality Check**: SPEC command structure (lines 36-44) shows NO `spec/refine.md`:

```text
├── research/
│   ├── spec/
│   │   ├── draft.md
│   │   ├── plan.md
│   │   └── review.md      # No refine!
│   ├── draft.md
│   ├── plan.md
│   ├── refine.md          # Handles ALL research artifacts
│   └── review.md
```

**Fix**: Remove `spec/refine.md` references from Phase 3. The top-level `refine.md` handles research plans too.

Actually, looking at my Phase 3 plan again - I don't have `spec/refine.md`. Good. But the tasks list says:

```text
- [ ] Write `spec/draft.md` command
- [ ] Write `spec/plan.md` command
- [ ] Write `spec/review.md` command
```

This is correct. ✅

---

### 7. Settings.json Hook Structure (Phase 6)

**Phase 6**: Shows `hooks` as top-level key in settings.json

**Reality**: Hooks in settings.json might need to be scoped or merged with existing settings

**Fix**: Add explicit merge instructions:

```text
// Merge into existing .claude/settings.json, preserving other keys
```

---

### 8. Artifact Type Naming Inconsistency

**Phase 3**: Uses `type: research-plan` (hyphenated)
**Phase 4**: Uses `type: content-plan` (hyphenated)
**Phase 5**: Uses `type: post-spec`, `type: post-outline` (hyphenated)

**SPEC Line 232**: Shows types WITHOUT hyphens for some:

```text
type: idea | plan | research-plan | research-findings | analysis | report | phase | content-plan | post-spec | post-outline | draft
```

**Status**: Actually consistent ✅ - SPEC uses hyphens for compound types. No fix needed.

---

## Action Items

### High Priority

1. [x] Define post artifact storage location (Phase 5) — `phase/<N>-<slug>.spec.md` pattern
2. [x] Add `brainstorm-plans/standard.md` template (Phase 0)
3. [x] Fix persona verification timing (Phase 1/2) — Phase 1 defers, Phase 2 integrates
4. [x] Add project status transitions to all phases

### Medium Priority

5. [x] Add `README.md` template (Phase 0) — `project-readme.md`
6. [x] Add `plan.md` review checklist (Phase 1)
7. [x] Add entry point flexibility notes (Phase 3, 4, 5, 6)
8. [x] Add `/blog:init` skill for template copying (Phase 7)
9. [x] Clarify hook delegation model (Phase 7) — plugin stubs delegate to repo

### Low Priority

10. [x] Add `educator.md` seed persona (Phase 2)
11. [x] Add index.md update to spec/review (Phase 3)
12. [x] Clarify draft file deletion (Phase 6) — explicitly delete after promote
13. [x] Rename index template to schema (Phase 0) — `schemas/artifact-schema.md`
