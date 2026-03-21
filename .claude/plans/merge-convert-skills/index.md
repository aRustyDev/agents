# Convert Skills Consolidation & IR Design Plan

Multi-phase plan for consolidating 49 convert-* skills into a cluster-based architecture backed by an Intermediate Representation (IR) schema for cross-language codebase conversion.

## Objectives

| # | Objective | Measurable | Success Metric |
|---|-----------|------------|----------------|
| 1 | Design a tiered IR with shared layers + community-specific schemas | Yes | IR represents 80%+ of patterns; community IRs cover within-community pairs natively |
| 2 | Consolidate 49 convert-* skills into community-aligned architecture | Yes | Skills organized by 4 communities + 3 bridges |
| 3 | Support layer-decomposed conversion (per-layer sub-problems) | Yes | Round-trip conversion preserves L3 semantic equivalence; per-layer preservation tracking |
| 4 | Enable tooling ecosystem (extraction, synthesis, validation) | Yes | Python MVP retargeted to community IR with 85%+ round-trip success |

## Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Convert-* skills | 49 (after bidirectional merge from 78) | ~25 cluster-based skills | 24 skills to consolidate |
| IR specification | Complete (5-layer schema, JSON Schema, SQL) | Validated against all families | Need cluster-based validation |
| Language profiles | 29 documented (17 Tier 1, 5 Tier 2, 7 Tier 3) | All languages in convert-* skills | Complete |
| Semantic gaps cataloged | 320 gaps classified (54 patterns, 16 decision points) | All gaps with mitigations | Complete |
| Tooling (extractors) | 6 language extractors (Python MVP + 5 stubs) | Validated cluster merging | Need cluster merge tooling |
| Round-trip validation | Python MVP passing (8/10 review) | Multi-language validation | Python complete, others pending |

## Phases

### Research Phases (Complete)

| ID | Name | Status | Dependencies | Progress |
|----|------|--------|--------------|----------|
| phase-0 | [Pattern Extraction](phase/0-pattern-extraction.md) | complete | — | 100% |
| phase-1 | [Language Families](phase/1-language-families.md) | complete | — | 100% |
| phase-2 | [Language Survey](phase/2-language-survey.md) | complete | phase-0, phase-1 | 100% |
| phase-3 | [Semantic Gaps](phase/3-semantic-gaps.md) | complete | phase-0, phase-1, phase-2 | 100% |
| phase-4 | [IR Schema Design](phase/4-ir-schema-design.md) | complete | phase-3 | 100% |
| phase-5 | [Validation & Tooling (Python MVP)](phase/5-validation-tooling.md) | complete | phase-4 | 100% |
| phase-5.1 | [Tech Debt Cleanup](phase/5.1-tech-debt-cleanup.md) | complete | phase-5 | 100% |

### Implementation Phases (Tiered IR Architecture — ADR-010)

| ID | Name | Status | Dependencies | Progress |
|----|------|--------|--------------|----------|
| S0 | [Shared Layers (L0 + L4)](phase/S0-shared-layers.md) | pending | phase-5.1 | 0% |
| V0 | [Validation Framework](phase/V0-validation-framework.md) | pending | phase-5.1 | 0% |
| C1 | [Community: Typed-FP](phase/C1-typed-fp.md) | pending | S0, V0 | 0% |
| C2 | [Community: Dynamic-FP](phase/C2-dynamic-fp.md) | pending | S0, V0 | 0% |
| C3 | [Community: Object/Managed](phase/C3-object-managed.md) | pending | S0, V0 | 0% |
| C4 | [Community: Systems](phase/C4-systems.md) | pending | S0, V0 | 0% |
| B1 | [Bridge: Typed-FP ↔ Dynamic-FP](phase/B1-bridge-typed-fp-dynamic-fp.md) | pending | C1, C2 | 0% |
| B2 | [Bridge: Dynamic-FP ↔ Object/Managed](phase/B2-bridge-dynamic-fp-object-managed.md) | pending | C2, C3 | 0% |
| B3 | [Bridge: Object/Managed ↔ Systems](phase/B3-bridge-object-managed-systems.md) | pending | C3, C4 | 0% |
| F1 | [Final Consolidation](phase/F1-final-consolidation.md) | pending | B1, B2, B3 | 0% |

#### Phase Dependencies

```
S0 + V0 (parallel) ──→ C1, C2, C3, C4 (parallel) ──→ B1, B2, B3 (parallel) ──→ F1
                                                        B1 needs C1+C2
                                                        B2 needs C2+C3
                                                        B3 needs C3+C4
```

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Community boundary disputes (e.g., Go placement) | Medium | Low | Documented boundary decisions in ADR-010 with rationale; annotation system handles edge cases |
| Chained bridge quality degradation | Medium | Medium | Per-step preservation tracking detects degradation; shortcut bridges added if metrics warrant |
| Increased schema count (shared + 4 communities + 3 bridges) | Medium | Low | Layer decomposition means each schema is smaller; shared layers reduce duplication |
| Phase 5 rework scope creep | Low | Medium | Rework is narrowing (remove unused annotations), not widening; community IR is a subset |
| Merged skills too large for Claude context window | Medium | High | Progressive disclosure: SKILL.md ≤ 500 lines (soft), reference docs on-demand |
| Roc/Gleam ecosystem instability (pre-1.0) | Medium | Low | Document version assumptions; defer deep Roc tooling until stable |
| Tech debt accumulation across phases | Medium | Medium | Run Phase 5.1 cleanup pattern after each phase |

## Architecture (ADR-010: Tiered IR with Layer Decomposition)

The implementation phases use a **tiered community IR architecture** with **layer decomposition**. See [ADR-010](docs/src/adr/adr-010-tiered-ir-architecture.md) for full rationale.

### Layer Architecture

| Layer | Scope | Description |
|-------|-------|-------------|
| **L0: Expression** | Shared (universal) | AST, operators, literals — syntax mapping |
| **L1: Data Flow** | Community-specific | Bindings, lifetimes, transforms — varies by paradigm |
| **L2: Control Flow** | Community-specific | Functions, effects, concurrency — varies by paradigm |
| **L3: Type** | Community-specific | Type definitions, relationships, constraints — varies by paradigm |
| **L4: Structural** | Shared (universal) | Modules, packages, imports/exports — structural mapping |

### 4 Communities

| Community | Families | Languages | Coupled Core |
|-----------|----------|-----------|-------------|
| **Typed-FP** | ML-FP | Haskell, Elm, Scala, F#, OCaml, Roc | None (fully decomposable) |
| **Dynamic-FP** | BEAM, LISP | Erlang, Elixir, Gleam, Clojure | L2+L3 |
| **Object/Managed** | Dynamic, Managed-OOP, Apple | Python, TS, JS, Java, C#, Kotlin, Swift, ObjC | L2+L3 |
| **Systems** | Systems | Rust, C, C++, Go, Zig | L1+L3 |

### 3 Chained Bridges

```
Typed-FP ←─B1─→ Dynamic-FP ←─B2─→ Object/Managed ←─B3─→ Systems
```

Non-adjacent conversions chain through intermediates. Shortcut bridges deferred until validation data justifies them.

### Target Architecture

```
context/skills/
├── meta-ir-shared-layers-dev/                  # Shared L0 + L4 schemas
│
├── meta-convert-community-typed-fp-dev/        # Typed-FP community (C1)
├── meta-convert-community-dynamic-fp-dev/      # Dynamic-FP community (C2)
├── meta-convert-community-object-managed-dev/  # Object/Managed community (C3)
├── meta-convert-community-systems-dev/         # Systems community (C4)
│
├── meta-convert-bridge-typed-dynamic-dev/      # B1: Typed-FP ↔ Dynamic-FP
├── meta-convert-bridge-dynamic-object-dev/     # B2: Dynamic-FP ↔ Object/Managed
├── meta-convert-bridge-object-systems-dev/     # B3: Object/Managed ↔ Systems
│
├── meta-codebase-analysis-eng/                 # IR extraction from source code
├── meta-codebase-implement-ir-dev/             # IR synthesis to target code
│
└── idiomatic-{lang}-dev/                       # Language-specific idiom skills
```

### Definitive Skill → Phase Mapping (49 skills)

Each of the 49 convert-* skills is assigned to exactly one phase. No double-counting.

| # | Skill | Source Community | Target Community | Phase | Notes |
|---|-------|----------------|-----------------|-------|-------|
| 1 | convert-elm-fsharp | Typed-FP | Typed-FP | **C1** | |
| 2 | convert-elm-haskell | Typed-FP | Typed-FP | **C1** | |
| 3 | convert-elm-roc | Typed-FP | Typed-FP | **C1** | |
| 4 | convert-elm-scala | Typed-FP | Typed-FP | **C1** | |
| 5 | convert-fsharp-haskell | Typed-FP | Typed-FP | **C1** | |
| 6 | convert-fsharp-roc | Typed-FP | Typed-FP | **C1** | |
| 7 | convert-fsharp-scala | Typed-FP | Typed-FP | **C1** | |
| 8 | convert-haskell-roc | Typed-FP | Typed-FP | **C1** | |
| 9 | convert-haskell-scala | Typed-FP | Typed-FP | **C1** | |
| 10 | convert-roc-scala | Typed-FP | Typed-FP | **C1** | |
| 11 | convert-clojure-elixir | Dynamic-FP | Dynamic-FP | **C2** | |
| 12 | convert-clojure-erlang | Dynamic-FP | Dynamic-FP | **C2** | |
| 13 | convert-elixir-erlang | Dynamic-FP | Dynamic-FP | **C2** | |
| 14 | convert-objc-swift | Object/Managed | Object/Managed | **C3** | |
| 15 | convert-python-typescript | Object/Managed | Object/Managed | **C3** | |
| 16 | convert-c-cpp | Systems | Systems | **C4** | |
| 17 | convert-c-rust | Systems | Systems | **C4** | |
| 18 | convert-cpp-rust | Systems | Systems | **C4** | |
| 19 | convert-golang-rust | Systems | Systems | **C4** | |
| 20 | convert-clojure-elm | Dynamic-FP | Typed-FP | **B1** | |
| 21 | convert-clojure-fsharp | Dynamic-FP | Typed-FP | **B1** | |
| 22 | convert-clojure-haskell | Dynamic-FP | Typed-FP | **B1** | |
| 23 | convert-clojure-roc | Dynamic-FP | Typed-FP | **B1** | |
| 24 | convert-clojure-scala | Dynamic-FP | Typed-FP | **B1** | |
| 25 | convert-elixir-elm | Dynamic-FP | Typed-FP | **B1** | |
| 26 | convert-elixir-fsharp | Dynamic-FP | Typed-FP | **B1** | |
| 27 | convert-elixir-haskell | Dynamic-FP | Typed-FP | **B1** | |
| 28 | convert-elixir-roc | Dynamic-FP | Typed-FP | **B1** | |
| 29 | convert-elixir-scala | Dynamic-FP | Typed-FP | **B1** | |
| 30 | convert-elm-erlang | Typed-FP | Dynamic-FP | **B1** | |
| 31 | convert-erlang-fsharp | Dynamic-FP | Typed-FP | **B1** | |
| 32 | convert-erlang-haskell | Dynamic-FP | Typed-FP | **B1** | |
| 33 | convert-erlang-roc | Dynamic-FP | Typed-FP | **B1** | |
| 34 | convert-erlang-scala | Dynamic-FP | Typed-FP | **B1** | |
| 35 | convert-python-clojure | Object/Managed | Dynamic-FP | **B2** | |
| 36 | convert-python-elixir | Object/Managed | Dynamic-FP | **B2** | |
| 37 | convert-python-erlang | Object/Managed | Dynamic-FP | **B2** | |
| 38 | convert-python-elm | Object/Managed | Typed-FP | **B2** | Chained: B2→B1 |
| 39 | convert-python-fsharp | Object/Managed | Typed-FP | **B2** | Chained: B2→B1 |
| 40 | convert-python-haskell | Object/Managed | Typed-FP | **B2** | Chained: B2→B1 |
| 41 | convert-python-roc | Object/Managed | Typed-FP | **B2** | Chained: B2→B1 |
| 42 | convert-python-scala | Object/Managed | Typed-FP | **B2** | Chained: B2→B1 |
| 43 | convert-java-c | Object/Managed | Systems | **B3** | |
| 44 | convert-java-cpp | Object/Managed | Systems | **B3** | |
| 45 | convert-java-rust | Object/Managed | Systems | **B3** | |
| 46 | convert-python-golang | Object/Managed | Systems | **B3** | |
| 47 | convert-python-rust | Object/Managed | Systems | **B3** | |
| 48 | convert-typescript-golang | Object/Managed | Systems | **B3** | |
| 49 | convert-typescript-rust | Object/Managed | Systems | **B3** | |

**Summary:**

| Phase | Type | Count | Description |
|-------|------|-------|-------------|
| C1 | Community | 10 | Within Typed-FP |
| C2 | Community | 3 | Within Dynamic-FP |
| C3 | Community | 2 | Within Object/Managed |
| C4 | Community | 4 | Within Systems |
| B1 | Bridge | 15 | Typed-FP ↔ Dynamic-FP |
| B2 | Bridge | 8 | Object/Managed → Dynamic-FP (3 direct) + Object/Managed → Typed-FP (5 chained via B1) |
| B3 | Bridge | 7 | Object/Managed ↔ Systems |
| **Total** | | **49** | |

## Directory Structure

```
.claude/plans/merge-convert-skills/
├── index.md                      # This file
├── ROADMAP.md                    # Issue tracking and milestones
├── ANALYSIS.md                   # Original merge analysis (78→49)
├── IR-RESEARCH-PLAN.md           # Original IR research notes
├── cluster-skill-template.md     # Community skill merge template
├── phase/                        # Phase plans
│   ├── 0-pattern-extraction.md   # ✓ Complete
│   ├── 1-language-families.md    # ✓ Complete
│   ├── 2-language-survey.md      # ✓ Complete
│   ├── 3-semantic-gaps.md        # ✓ Complete
│   ├── 4-ir-schema-design.md     # ✓ Complete (amended by ADR-010)
│   ├── 5-validation-tooling.md   # ✓ Complete
│   ├── 5.1-tech-debt-cleanup.md  # ✓ Complete
│   ├── S0-shared-layers.md       # Foundation: L0 + L4
│   ├── V0-validation-framework.md # Foundation: test infrastructure
│   ├── C1-typed-fp.md            # Community: Typed-FP
│   ├── C2-dynamic-fp.md          # Community: Dynamic-FP
│   ├── C3-object-managed.md      # Community: Object/Managed
│   ├── C4-systems.md             # Community: Systems
│   ├── B1-bridge-typed-fp-dynamic-fp.md      # Bridge B1
│   ├── B2-bridge-dynamic-fp-object-managed.md # Bridge B2
│   ├── B3-bridge-object-managed-systems.md    # Bridge B3
│   └── F1-final-consolidation.md # Archive + migration
├── analysis/                     # 37+ analysis documents
│   ├── index.md
│   ├── bidirectional-merge.md
│   ├── post-merge-state.md
│   ├── pattern-extraction.md
│   ├── family-taxonomy.md
│   ├── coverage-gaps.md
│   ├── gap-classification.md
│   ├── gap-patterns.md           # 54 patterns
│   ├── severity-matrix.md        # 9x9 family difficulty
│   ├── bidirectional-gaps.md
│   ├── decision-points.md        # 16 human decision points
│   ├── ir-implications.md
│   ├── ir-validation.md
│   ├── phase5-validation-report.md
│   ├── phase5-final-review.md
│   ├── phase5.1-review.md
│   └── phase5.1-validation-report.md
├── data/                         # SQL and data files
│   ├── schema.sql
│   ├── families.sql
│   ├── languages.sql
│   ├── patterns.sql              # 7,195 patterns
│   ├── gaps.sql                  # 320 gaps
│   └── ir-schema.sql
├── docs/src/                     # Research documentation
│   ├── language-families/        # 13 family docs
│   ├── languages/                # 29 language profiles
│   ├── ir-schema/                # 5-layer IR docs
│   ├── validation/               # Equivalence levels
│   └── adr/                      # Architecture decisions
├── schemas/
│   └── ir-v1.json                # JSON Schema definitions
└── tools/                        # Extraction/synthesis tooling
    ├── ir-core/                  # Base infrastructure
    ├── ir-extract-python/        # Python extractor (MVP)
    ├── ir-synthesize-python/     # Python synthesizer (MVP)
    ├── ir-validate/              # Schema validator
    ├── ir-query/                 # Database query interface
    └── ir-roundtrip/             # Round-trip testing
```

## Quick Links

### Completed Research Phases
- [Phase 0: Pattern Extraction](phase/0-pattern-extraction.md) — 7,195 patterns from 49 skills
- [Phase 1: Language Families](phase/1-language-families.md) — 13 families documented
- [Phase 2: Language Survey](phase/2-language-survey.md) — 29 language profiles
- [Phase 3: Semantic Gaps](phase/3-semantic-gaps.md) — 320 gaps, 54 patterns, 16 decision points
- [Phase 4: IR Schema Design](phase/4-ir-schema-design.md) — 5-layer IR, JSON Schema (amended by ADR-010)
- [Phase 5: Validation & Tooling](phase/5-validation-tooling.md) — Python MVP (8/10 review)
- [Phase 5.1: Tech Debt Cleanup](phase/5.1-tech-debt-cleanup.md) — All items resolved

### Pending Implementation Phases (Tiered IR — ADR-010)

**Foundation:**
- [S0: Shared Layers](phase/S0-shared-layers.md) — L0 + L4 universal schemas
- [V0: Validation Framework](phase/V0-validation-framework.md) — Round-trip, benchmarks, per-step preservation

**Communities (can run in parallel):**
- [C1: Typed-FP](phase/C1-typed-fp.md) — Haskell, Elm, Scala, F#, OCaml, Roc
- [C2: Dynamic-FP](phase/C2-dynamic-fp.md) — Erlang, Elixir, Gleam, Clojure
- [C3: Object/Managed](phase/C3-object-managed.md) — Python, TS, JS, Java, C#, Kotlin, Swift, ObjC
- [C4: Systems](phase/C4-systems.md) — Rust, C, C++, Go, Zig

**Bridges (can run in parallel after adjacent communities):**
- [B1: Typed-FP ↔ Dynamic-FP](phase/B1-bridge-typed-fp-dynamic-fp.md)
- [B2: Dynamic-FP ↔ Object/Managed](phase/B2-bridge-dynamic-fp-object-managed.md)
- [B3: Object/Managed ↔ Systems](phase/B3-bridge-object-managed-systems.md)

**Consolidation:**
- [F1: Final Consolidation](phase/F1-final-consolidation.md) — Archive, migration, final validation

### Analysis & Data
- [Analysis Index](analysis/index.md) — 37+ analysis documents
- [ROADMAP](ROADMAP.md) — Issues and milestones

## Completed Research Summary

| Phase | Key Outputs | Volume |
|-------|-------------|--------|
| Phase 0 | Pattern database | 7,195 patterns from 49 skills |
| Phase 1 | Family taxonomy | 13 families, comparison matrices |
| Phase 2 | Language profiles | 29 profiles (17 full, 5 standard, 7 minimal) |
| Phase 3 | Gap catalog | 320 gaps, 54 patterns, 9×9 severity matrix |
| Phase 4 | IR schema | 5-layer architecture, JSON Schema, SQL schema |
| Phase 5 | Python MVP | Extractor + synthesizer + validator (8/10 review) |
| Phase 5.1 | Tech debt | 7/8 items resolved, 1 deferred |

## GAP Review Notes

Reviewed 2026-03-18 after ADR-010 acceptance.

### Gaps

| Gap | Severity | Resolution |
|-----|----------|------------|
| No rollback strategy for community merges | Medium | Original skills preserved until F1 validation passes |
| Phase 5.1 deferred item (M4: CFG) | Low | Not blocking any community phase; remains deferred |
| Roc/Gleam pre-1.0 instability | Low | Document version assumptions; mark as provisional in C1 (Typed-FP) |
| Chained bridge quality for non-adjacent pairs | Medium | Per-step preservation tracking; shortcut bridges added if metrics warrant |
| Community boundary edge cases (Go, TypeScript) | Low | Documented in ADR-010 with rationale |

### Areas for Refinement

- Community skill template should include layer-decomposition checklist per community's coupling pattern
- Each community/bridge phase should run Phase 5.1 tech debt cleanup pattern after completion
- Validation framework (V0) should define concrete pass/fail thresholds for preservation levels

### Potential Extensions

- `idiomatic-{lang}-dev` skills not yet scoped — defer to post-F1
- Shortcut bridges for high-demand non-adjacent pairs (e.g., Typed-FP↔Systems) — add only if chained quality is insufficient
- TypeScript→FP conversions covered by B1+B2 chaining, but may warrant dedicated bridge if demand is high

## Next Actions

1. [x] Create cluster phase plan files (6-10) — superseded by ADR-010
2. [x] Convert plan to beads issues (ai-x3e) — need update for new phases
3. [x] Accept ADR-010: Tiered IR with Layer Decomposition
4. [x] Create new phase plan files (S0, V0, C1-C4, B1-B3, F1)
5. [x] Update beads issues for new phase structure (ai-x3e.8-12 closed, ai-x3e.13-22 created)
6. [ ] Begin S0 + V0 (foundation phases, can run in parallel)
