# Phase S0: Shared Layers (L0 + L4)

**ID:** S0
**Status:** pending
**Beads:** ai-x3e.13

## Objective

Define the universal shared layer schemas for L0 (Expression IR) and L4 (Structural IR) that are used by all 4 community IRs. These layers are nearly identical across all languages regardless of paradigm — L0 handles AST/expressions/literals, L4 handles modules/packages/imports/exports. Defining them once eliminates duplication and establishes the foundation for community-specific L1-L3 schemas.

## Dependencies

- phase-5.1 (Tech Debt Cleanup) — complete

## Success Criteria

- [ ] L0 Expression IR schema defined (JSON Schema + YAML spec)
- [ ] L4 Structural IR schema defined (JSON Schema + YAML spec)
- [ ] Schemas validated against Phase 4's existing L0/L4 definitions (should be extraction, not redesign)
- [ ] Test coverage: at least 4 languages (one per community) parsed to L0+L4
- [ ] SQL schema extensions for shared layers
- [ ] Documentation: how community IRs reference shared layers

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| L0 schema | schemas/ir-shared-l0.json | Expression IR JSON Schema |
| L4 schema | schemas/ir-shared-l4.json | Structural IR JSON Schema |
| YAML specs | docs/src/ir-schema/shared-layer-0.md | L0 documentation |
| YAML specs | docs/src/ir-schema/shared-layer-4.md | L4 documentation |
| SQL extensions | data/ir-shared-layers.sql | Database schema for shared layers |
| Integration guide | docs/src/ir-schema/community-integration.md | How community IRs use shared layers |

## Files

**Create:**
- schemas/ir-shared-l0.json
- schemas/ir-shared-l4.json
- docs/src/ir-schema/shared-layer-0.md
- docs/src/ir-schema/shared-layer-4.md
- docs/src/ir-schema/community-integration.md
- data/ir-shared-layers.sql

**Modify:**
- schemas/ir-v1.json — Extract L0+L4 into separate shared schemas, reference from main
- docs/src/ir-schema/overview.md — Update to reflect tiered architecture
- index.md — Update S0 status

## Approach

1. Extract L0 (Expression IR) from Phase 4's ir-v1.json into standalone schema
2. Extract L4 (Structural IR) from Phase 4's ir-v1.json into standalone schema
3. Validate extractions are complete — no concepts left behind that belong in shared layers
4. Test against 4 representative languages (Python, Haskell, Rust, Elixir) — parse source to L0+L4 only
5. Write SQL schema extensions for shared layer storage
6. Document the integration interface: how community IRs import/reference shared layers

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| L0/L4 aren't as universal as assumed | Low | Medium | Phase 4 already defined them; this is extraction, not design |
| Community-specific structural concepts (e.g., C headers vs Python packages) | Medium | Low | Handle via optional extension fields, not separate schemas |
