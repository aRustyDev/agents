# ADR-000: Migration from Monolithic Plan

## Status
Accepted

## Context
The original TYPED_VALUES_DEVELOPMENT_PLAN.md was a comprehensive 1900+ line document containing the entire development plan for the tree-sitter-dotenv typed values feature. This monolithic approach made it difficult to:
- Navigate to specific phases
- Track progress through phases
- Reference specific implementation details
- Maintain the document as development progressed

## Decision
Split the monolithic plan into the .claude project structure:
- Individual phase documents in `.claude/plans/tree-sitter/kvconf/`
- Test files moved to `.claude/tests/tree-sitter/kvconf/fixtures/`
- Build automation (justfile) moved to `.claude/`
- ADRs created in `.claude/docs/tree-sitter/kvconf/adr/`

## Consequences

### Positive Consequences
- Better organization with clear separation of concerns
- Easier navigation between phases
- Test files organized with the project
- Build automation centralized in .claude
- Clear location for ADRs and documentation

### Negative Consequences
- Need to update all path references
- Multiple files to maintain instead of one
- Initial migration effort required

## Implementation Notes
The original plan has been fully captured in:
- `00-overview.md` - Goals, principles, strategy
- `01-phase1-foundation.md` through `07-phase7-documentation.md` - Implementation phases
- `08-testing-strategy.md` - Testing approach
- `09-documentation-structure.md` - Documentation plan
- Test files moved to organized structure
- Justfile paths updated for new location

## References
- Original file: TYPED_VALUES_DEVELOPMENT_PLAN.md (now removed)
- New structure: .claude/plans/tree-sitter/kvconf/