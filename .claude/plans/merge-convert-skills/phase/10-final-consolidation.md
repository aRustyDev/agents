# Phase 10: Final Consolidation & Migration

**ID:** phase-10
**Status:** pending
**Beads:** ai-x3e.12

## Objective

Complete the consolidation by creating IR-backed analysis/synthesis skills, migrating users from individual convert-* skills to the cluster architecture, and removing the original 49 individual skills.

## Dependencies

- phase-9 (Cluster D: Cross-Paradigm) — all cluster merges complete

## Success Criteria

- [ ] `meta-codebase-analysis-eng` skill created with IR extraction capabilities
- [ ] `meta-codebase-implement-ir-dev` skill created with IR synthesis capabilities
- [ ] All 4 cluster skills validated against original skill test cases
- [ ] Original 49 convert-* skills archived to `legacy/skills/`
- [ ] Migration guide published for users of individual convert-* skills
- [ ] Skill count reduced from 49 to ≤8 (4 clusters + 2 IR skills + idiomatic-* as needed)
- [ ] Overall skill quality ≥ individual skills (validated by round-trip testing)

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| IR analysis skill | `context/skills/meta-codebase-analysis-eng/SKILL.md` | IR extraction from source code |
| IR synthesis skill | `context/skills/meta-codebase-implement-ir-dev/SKILL.md` | Code generation from IR |
| Migration guide | `docs/src/migration/convert-skills-v2.md` | User migration guide |
| Final validation report | `analysis/phase10-final-validation.md` | Comprehensive quality report |
| Archive | `legacy/skills/convert-*/` | Archived individual skills |

## Files

**Create:**
- `context/skills/meta-codebase-analysis-eng/SKILL.md`
- `context/skills/meta-codebase-analysis-eng/reference/ir/` (IR schema docs, extraction guide)
- `context/skills/meta-codebase-analysis-eng/reference/families/` (13 family docs)
- `context/skills/meta-codebase-analysis-eng/reference/languages/` (29 language profiles)
- `context/skills/meta-codebase-implement-ir-dev/SKILL.md`
- `context/skills/meta-codebase-implement-ir-dev/reference/synthesis-guide.md`
- `context/skills/meta-codebase-implement-ir-dev/reference/patterns/`
- `context/skills/meta-codebase-implement-ir-dev/reference/targets/`
- `docs/src/migration/convert-skills-v2.md`
- `analysis/phase10-final-validation.md`

**Modify:**
- `index.md` — Mark all phases complete, update Current State
- Move 49 individual convert-* skills to `legacy/skills/`

## Tasks

### 10.1 Create IR-Backed Skills

1. Build `meta-codebase-analysis-eng` from Phase 4 IR schema + Phase 5 tooling
2. Build `meta-codebase-implement-ir-dev` from Phase 5 synthesizer
3. Integrate language family docs from Phase 1 and language profiles from Phase 2

### 10.2 Final Validation

1. Run round-trip tests across all cluster skills
2. Compare conversion quality against original individual skills
3. Validate IR extraction/synthesis pipeline end-to-end
4. Document any quality regressions and their mitigations

### 10.3 Migration

1. Archive original 49 convert-* skills to `legacy/skills/`
2. Update any cross-references from other skills/commands
3. Write user-facing migration guide
4. Update skill-organization-strategy.md with cluster skill documentation

### 10.4 Cleanup

1. Run Phase 5.1 tech debt patterns on all new skills
2. Remove any temporary analysis/data files
3. Update ROADMAP.md with final status
4. Close parent beads issue (ai-x3e)
