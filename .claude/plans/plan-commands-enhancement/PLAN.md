# Plan Commands Enhancement

**Created:** 2025-03-16
**Updated:** 2025-03-16
**Owner:** Claude Code AI

Enhance `/context:plan:create`, `/context:plan:review`, and `/context:plan:refine` commands with schema validation, logic gap analysis, and consistency checking.

## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | Enforce consistent plan structure | Yes | 100% of plans created via `/context:plan:create` pass `--validate-schema=strict` |
| 2 | Identify logic gaps in plans | Yes | Review reports include causal/completeness/dependency gaps |
| 3 | Check internal consistency | Yes | Cross-reference validation catches misalignments |
| 4 | Check external consistency | Yes | Plans align with project standards (CLAUDE.md, naming conventions) |
| 5 | Auto-fix schema violations | Yes | `--fix-schema` adds missing required sections with placeholders |

## Current State

| Metric | Current Value | Target Value | Gap |
|--------|---------------|--------------|-----|
| Schema validation | None | Full validation | Missing |
| Logic gap analysis | None | Causal + completeness | Missing |
| Internal consistency | Partial (review.md) | Full cross-ref | Incomplete |
| External consistency | None | Project + industry | Missing |
| Auto-fix capability | None | Schema auto-fix | Missing |

## Required Plan Schema (Preview)

> **Note:** This is a preview. The canonical schema will be defined in Phase 1 deliverable: `context/commands/context/plan/SCHEMA.md`

```yaml
# Required top-level elements
objectives:        # Table with Measurable column
currentState:      # Table with Current/Target/Gap columns
phases:            # Table with ID/Dependencies/Status columns
risks:             # Table with Mitigation column

# Required per-phase elements
phase.success:     # Checklist format, measurable criteria
phase.deliverables: # Table with Location column
phase.files:       # Create/Modify sections
```

## Phases

| ID | Name | Status | Dependencies | Effort | Success Criteria |
|----|------|--------|--------------|--------|------------------|
| phase-0 | Audit Existing Plans | **complete** | - | 1h | Survey of legacy plans, migration guidance |
| phase-1 | Schema Definition | **complete** | phase-0 | 2h | Schema spec documented, validation rules defined |
| phase-2 | Create Command | **complete** | phase-1 | 2h | create.md generates schema-compliant plans |
| phase-3 | Review Command | **complete** | phase-1, phase-2 | 3h | review.md validates schema + gaps + consistency |
| phase-4 | Refine Command | **complete** | phase-2, phase-3 | 2h | refine.md applies fixes with --fix-schema |
| phase-5 | Integration Test | **complete** | phase-2, phase-3, phase-4 | 2h | Full create→review→refine cycle works |

**Total estimated effort:** 12 hours

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing plans | Medium | High | Schema validation optional via flag (`--validate-schema=off`) |
| Over-engineering | Medium | Medium | Start minimal, iterate |
| Inconsistent enforcement | Low | Medium | Single source of truth: SCHEMA.md |
| Changes cause regressions | Low | High | Backup original commands before modification |

## Rollback Strategy

If changes break existing workflows:

1. **Immediate:** Restore original commands from git: `git checkout HEAD~1 -- context/commands/context/plan/`
2. **Graceful degradation:** Use `--validate-schema=off` to bypass new validation
3. **Legacy mode:** Keep old behavior as default, new features opt-in initially

## Timeline

| Milestone | Target | Actual |
|-----------|--------|--------|
| Audit complete | After Phase 0 | 2025-03-16 |
| Schema spec complete | After Phase 1 | 2025-03-16 |
| Create command updated | After Phase 2 | 2025-03-16 |
| Review command updated | After Phase 3 | 2025-03-16 |
| Refine command updated | After Phase 4 | 2025-03-16 |
| Integration tested | After Phase 5 | 2025-03-16 |

## Notes

- Commands are in `context/commands/context/plan/`
- Schema should allow graceful degradation for legacy plans
- SCHEMA.md is the single source of truth for validation rules
- Default validation mode: `warn` (inform but don't block)
- `--validate-schema=strict` intended for CI/formal plans

## Future Enhancements (Out of Scope)

- User-facing documentation for new schema requirements
- Auto-migration tool for bulk legacy plan updates
- IDE/editor integration for schema validation
