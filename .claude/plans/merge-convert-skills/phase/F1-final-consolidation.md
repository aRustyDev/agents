# Phase F1: Final Consolidation

**ID:** F1
**Status:** pending
**Beads:** ai-x3e.22

## Objective

Archive the original 49 convert-* skills, create a migration guide for users, run final end-to-end validation across all communities and bridges, and produce the definitive tiered IR documentation. This phase completes the consolidation by ensuring the new architecture (4 communities + 3 bridges + 2 IR skills) fully replaces the original 49 individual skills with no regression in conversion quality.

## Dependencies

- B1 (Bridge: Typed-FP ↔ Dynamic-FP) — all bridge protocols defined
- B2 (Bridge: Dynamic-FP ↔ Object/Managed) — all bridge protocols defined
- B3 (Bridge: Object/Managed ↔ Systems) — all bridge protocols defined

## Success Criteria

- [ ] All 49 original convert-* skills archived to `.archive/skills/convert-*/`
- [ ] Migration guide maps every original skill to its replacement (community, bridge, or chained path)
- [ ] End-to-end validation: chained conversions across all 3 bridges pass at ≥85% preservation (global default; individual pair thresholds may be adjusted with documented justification)
- [ ] `meta-codebase-analysis-eng` skill created with IR extraction capabilities
- [ ] `meta-codebase-implement-ir-dev` skill created with IR synthesis capabilities
- [ ] Documentation complete: IR overview, 4 community guides, 3 bridge guides
- [ ] No regression in conversion quality vs original individual skills (validated by round-trip testing)
- [ ] Skill count reduced from 49 to ≤ 12 (4 communities + 3 bridges + 2 IR skills + shared layers + idiomatic-* as needed)

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Migration guide | `docs/src/migration/convert-skills-v2.md` | "I used convert-X-Y, what do I use now?" |
| Archive | `.archive/skills/convert-*/` | Original 49 convert-* skills preserved |
| IR analysis skill | `context/skills/meta-codebase-analysis-eng/SKILL.md` | IR extraction from source code |
| IR synthesis skill | `context/skills/meta-codebase-implement-ir-dev/SKILL.md` | Code generation from IR |
| End-to-end validation | `analysis/phaseF1-e2e-validation.md` | Cross-bridge chain validation report |
| Final quality report | `analysis/phaseF1-final-quality-report.md` | Comparison: new architecture vs original skills |
| IR documentation | `docs/src/ir-schema/` | Updated overview, community guides, bridge guides |

## Files

**Create:**
- `docs/src/migration/convert-skills-v2.md`
- `context/skills/meta-codebase-analysis-eng/SKILL.md`
- `context/skills/meta-codebase-analysis-eng/reference/ir/` (IR schema docs, extraction guide)
- `context/skills/meta-codebase-analysis-eng/reference/families/` (13 family docs)
- `context/skills/meta-codebase-analysis-eng/reference/languages/` (29 language profiles)
- `context/skills/meta-codebase-implement-ir-dev/SKILL.md`
- `context/skills/meta-codebase-implement-ir-dev/reference/synthesis-guide.md`
- `context/skills/meta-codebase-implement-ir-dev/reference/patterns/`
- `context/skills/meta-codebase-implement-ir-dev/reference/targets/`
- `analysis/phaseF1-e2e-validation.md`
- `analysis/phaseF1-final-quality-report.md`

**Modify:**
- `index.md` — Mark all phases complete, update Current State
- Move 49 individual convert-* skills to `.archive/skills/`
- `docs/src/ir-schema/overview.md` — Final IR documentation with community and bridge references
- Update any cross-references from other skills/commands pointing to archived convert-* skills

## Approach

1. **Build IR-backed skills** — Create `meta-codebase-analysis-eng` from Phase 4 IR schema + Phase 5 tooling; create `meta-codebase-implement-ir-dev` from Phase 5 synthesizer. Integrate language family docs from Phase 1 and language profiles from Phase 2
2. **Run final validation suite** — Execute round-trip tests across all 4 community skills and all 3 bridge protocols. Test chained conversions for every non-adjacent community pair (Typed-FP↔Object/Managed via B1+B2, Typed-FP↔Systems via B1+B2+B3, Dynamic-FP↔Systems via B2+B3). Compare quality against original individual skills
3. **Build migration guide** — For each of the 49 original convert-* skills, document the replacement path: which community skill, which bridge, or which chained path replaces it. Include examples for the most common conversions
4. **Archive original skills** — Move all 49 convert-* skills to `.archive/skills/` with git history preserved. Update any cross-references from other skills, commands, or documentation
5. **Complete documentation** — Finalize IR overview documentation, community guides, bridge guides. Ensure all documentation is internally consistent and cross-referenced
6. **Run cleanup** — Apply Phase 5.1 tech debt patterns to all new skills. Remove temporary analysis/data files. Close parent beads issue (ai-x3e). Update ROADMAP.md with final status

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Some original skills have unique patterns not captured by any community or bridge skill | Medium | High | Run diff analysis comparing original skill content against merged output before archiving; preserve any uncaptured patterns in community reference docs |
| Users depend on specific convert-X-Y skill names in their workflows or documentation | Medium | Medium | Migration guide provides exact mapping; leave symlinks or aliases for 1 version cycle if feasible |
| End-to-end chained validation reveals unacceptable quality for 3-bridge chains (Typed-FP↔Systems) | Medium | High | If chained quality is below threshold, create shortcut bridge (Typed-FP↔Systems) rather than blocking the entire consolidation |
