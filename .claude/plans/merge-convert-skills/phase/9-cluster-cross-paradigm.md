# Phase 9: Cluster D — Cross-Paradigm & Outliers

**ID:** phase-9
**Status:** pending
**Beads:** ai-x3e.11

## Objective

Merge 4 cross-paradigm convert-* skills into a single `meta-convert-cross-paradigm-dev` skill. These skills span paradigm boundaries (OOP→protocol-oriented, managed→systems) and have varying similarity scores, making them the most challenging cluster to merge.

## Dependencies

- phase-7 (Cluster B: Dynamic→FP) — completes dynamic language source patterns
- phase-8 (Cluster C: Systems) — completes systems target patterns

## Success Criteria

- [ ] Single `meta-convert-cross-paradigm-dev/SKILL.md` covers all 4 source skills
- [ ] SKILL.md < 200 lines (progressive disclosure)
- [ ] Paradigm-crossing patterns (OOP→functional, managed→unmanaged) well-documented
- [ ] Direction-specific sections preserved (these skills have the lowest inter-similarity)
- [ ] Round-trip validation passes for representative conversions

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Cluster skill | `context/skills/meta-convert-cross-paradigm-dev/SKILL.md` | Merged cross-paradigm skill |
| Reference docs | `context/skills/meta-convert-cross-paradigm-dev/reference/` | Per-pair conversion details |
| Validation report | `analysis/phase9-validation-report.md` | Merge quality assessment |

## Files

**Create:**
- `context/skills/meta-convert-cross-paradigm-dev/SKILL.md`
- `context/skills/meta-convert-cross-paradigm-dev/reference/objc-swift.md` (Apple platform migration)
- `context/skills/meta-convert-cross-paradigm-dev/reference/java-to-systems.md` (Java→C, Java→C++)
- `context/skills/meta-convert-cross-paradigm-dev/reference/python-typescript.md` (Dynamic↔Dynamic)
- `analysis/phase9-validation-report.md`

**Modify:**
- `index.md` — Update phase-9 status to complete

## Source Skills (4)

| Skill | Source | Target | Paradigm Shift |
|-------|--------|--------|----------------|
| convert-objc-swift | Objective-C | Swift | OOP/message-passing → protocol-oriented |
| convert-java-c | Java | C | Managed OOP → procedural/manual memory |
| convert-java-cpp | Java | C++ | GC OOP → RAII OOP |
| convert-python-typescript | Python | TypeScript | Dynamic → gradual typing |

## Approach

1. **Identify paradigm-crossing patterns** — Each skill involves a fundamental paradigm shift, not just syntax translation
2. **Keep direction-specific sections** — Low inter-similarity means more pair-specific content
3. **Extract shared cross-paradigm principles** — Managed→unmanaged memory, dynamic→static types
4. **Document decision points** — These conversions have the most human judgment required (16 decision points from Phase 3)
