---
id: bc665f41-261e-4c8a-ab8d-b35083186044
project:
  id: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
status: draft
---

# Roadmap: Catalog Pipeline Refactor

## Version Targets

| Phase | Version Bump | Rationale |
|-------|-------------|-----------|
| Phase 1 (Schema) | patch | Additive type changes, no behavioral change |
| Phase 2 (Discovery) | minor | New `catalog discover` command |
| Phase 3 (Reconciliation) | minor | New catalog state, move/rename detection |
| Phase 4 (Tier 1 Refactor) | minor | Refactored `catalog analyze` pipeline |
| Phase 5 (Tier 2) | minor | New `catalog analyze-deep` command |

## Issue Tracking

Issues will be created via `/beads:string` after plan approval.

| Phase | Epic | Status |
|-------|------|--------|
| Phase 1 | TBD | Not created |
| Phase 2 | TBD | Not created |
| Phase 3 | TBD | Not created |
| Phase 4 | TBD | Not created |
| Phase 5 | TBD | Not created |

## MVP Timeline

- **Phase 1-2:** Schema + Discovery = minimum viable per-repo scanning
- **Phase 3:** Reconciliation = catalog becomes self-healing
- **Phase 4:** Tier 1 refactor = cheaper, faster, more reliable analysis
- **Phase 5:** Tier 2 = quality grading for the full catalog

## Cross-Plan Dependencies

This plan must complete phases 1-4 before the skill-inspection plan's phases 4-5 can start.
Both plans share `cli/commands/skill.ts` as a modification target.
