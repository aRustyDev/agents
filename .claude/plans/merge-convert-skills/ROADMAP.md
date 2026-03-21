# Convert Skills Consolidation — Roadmap

Key architecture decision: [ADR-010: Tiered IR with Layer Decomposition](docs/src/adr/adr-010-tiered-ir-architecture.md)

## Milestones

| Milestone | Target | Scope | Version Bump |
|-----------|--------|-------|--------------|
| M1: Foundation | Pending | S0 (Shared Layers L0 + L4) + V0 (Validation Framework) | — |
| M2: Communities | Pending | C1 (Typed-FP, 10 skills) + C2 (Dynamic-FP, 3) + C3 (Object/Managed, 2) + C4 (Systems, 4) | minor per community |
| M3: Bridges | Pending | B1 (Typed-FP ↔ Dynamic-FP, 15 skills) + B2 (Dynamic-FP ↔ Object/Managed, 8) + B3 (Object/Managed ↔ Systems, 7) | minor per bridge |
| M4: Consolidation | Pending | F1 (archive 49 original skills, migration guide, final validation) | major |

### Prior Milestones (Complete)

| Milestone | Status | Scope |
|-----------|--------|-------|
| Research Complete | Complete | Phases 0-5.1 (pattern extraction, language survey, gaps, IR, tooling MVP) |

## Phase Dependency Diagram

```
phase-5.1 (complete)
    │
    ├──→ S0 (Shared Layers: L0 + L4) ──┐
    │                                    ├──→ C1 (Typed-FP)       ──┐
    └──→ V0 (Validation Framework) ─────┤                          ├──→ B1 (Typed-FP ↔ Dynamic-FP)  ──┐
                                         ├──→ C2 (Dynamic-FP)     ──┤                                   │
                                         │                          ├──→ B2 (Dynamic-FP ↔ Obj/Mgd) ─────┤
                                         ├──→ C3 (Object/Managed) ──┤                                   ├──→ F1
                                         │                          ├──→ B3 (Obj/Mgd ↔ Systems)   ───────┤
                                         └──→ C4 (Systems)        ──┘                                   │
                                                                                                         │
                                                                                                    Consolidation
```

**Parallelism rules:**
- S0 and V0 run in parallel; both must complete before any community phase
- C1, C2, C3, C4 run in parallel (no inter-community dependencies)
- Each bridge requires its two adjacent communities to complete (B1 needs C1+C2, B2 needs C2+C3, B3 needs C3+C4)
- B1, B2, B3 can run in parallel once their respective dependencies are met
- F1 requires all three bridges to complete

## Issues

Issues tracked via beads (`bd`). Parent issue links child phase issues.

### Research Phases (Complete)

| Phase | Beads ID | Status |
|-------|----------|--------|
| Parent: Convert Skills Consolidation | ai-x3e | open |
| Phase 0: Pattern Extraction | ai-x3e.1 | closed |
| Phase 1: Language Families | ai-x3e.2 | closed |
| Phase 2: Language Survey | ai-x3e.3 | closed |
| Phase 3: Semantic Gaps | ai-x3e.4 | closed |
| Phase 4: IR Schema Design | ai-x3e.5 | closed |
| Phase 5: Validation & Tooling | ai-x3e.6 | closed |
| Phase 5.1: Tech Debt Cleanup | ai-x3e.7 | closed |

### Superseded Issues (Needs Remapping)

The following beads issues were created under the old cluster-based phase structure (Phases 6-10). They are **superseded by ADR-010** and need remapping to the new tiered IR phases.

| Old Phase | Old Beads ID | Old Status | Superseded By |
|-----------|-------------|------------|---------------|
| Phase 6: Cluster A — FP Internal | ai-x3e.8 | closed (superseded) | C1 + C2 + B1 |
| Phase 7: Cluster B — Dynamic→FP | ai-x3e.9 | closed (superseded) | B2 + B1 (chained) |
| Phase 8: Cluster C — Systems | ai-x3e.10 | closed (superseded) | C4 |
| Phase 9: Cluster D — Cross-Paradigm | ai-x3e.11 | closed (superseded) | B1 + B2 + B3 |
| Phase 10: Final Consolidation | ai-x3e.12 | closed (superseded) | F1 |

### New Phase Issues

New beads issues will be created for the tiered IR phase structure. Expected mapping:

| Phase | Beads ID | Status | Dependencies |
|-------|----------|--------|--------------|
| S0: Shared Layers (L0 + L4) | ai-x3e.13 | pending | phase-5.1 |
| V0: Validation Framework | ai-x3e.14 | pending | phase-5.1 |
| C1: Community Typed-FP | ai-x3e.15 | pending (blocked) | S0, V0 |
| C2: Community Dynamic-FP | ai-x3e.16 | pending (blocked) | S0, V0 |
| C3: Community Object/Managed | ai-x3e.17 | pending (blocked) | S0, V0 |
| C4: Community Systems | ai-x3e.18 | pending (blocked) | S0, V0 |
| B1: Bridge Typed-FP ↔ Dynamic-FP | ai-x3e.19 | pending (blocked) | C1, C2 |
| B2: Bridge Dynamic-FP ↔ Object/Managed | ai-x3e.20 | pending (blocked) | C2, C3 |
| B3: Bridge Object/Managed ↔ Systems | ai-x3e.21 | pending (blocked) | C3, C4 |
| F1: Final Consolidation | ai-x3e.22 | pending (blocked) | B1, B2, B3 |

## Version Strategy

- **Current**: 49 convert-* skills exist as individual files (after bidirectional merge from 78)
- **After M1**: No version bump — foundation layers and validation infrastructure are internal
- **After M2**: Minor version bump per community phase (C1, C2, C3, C4) — non-breaking; old skills remain alongside new community skills during transition
  - Each community delivers a community IR schema (L1-L3) and within-community conversion rules
  - Old convert-* skills for within-community pairs are soft-deprecated but not removed
- **After M3**: Minor version bump per bridge phase (B1, B2, B3) — non-breaking; bridges enable cross-community conversion without removing old skills
  - Each bridge delivers a bridge protocol with per-layer transform rules and preservation tracking
- **After M4 (F1)**: Major version — old individual convert-* skills archived, replaced by community skills + bridge protocols + shared IR layers

### Skill Count Progression

| Phase | Skills Added | Skills Deprecated | Net Active |
|-------|-------------|-------------------|------------|
| Pre-M2 | 0 | 0 | 49 original |
| C1 | 1 community skill | 10 soft-deprecated | 40 active |
| C2 | 1 community skill | 3 soft-deprecated | 38 active |
| C3 | 1 community skill | 2 soft-deprecated | 37 active |
| C4 | 1 community skill | 4 soft-deprecated | 34 active |
| B1 | 1 bridge skill | 15 soft-deprecated | 20 active |
| B2 | 1 bridge skill | 8 soft-deprecated | 13 active |
| B3 | 1 bridge skill | 7 soft-deprecated | 7 active |
| F1 | 0 | 49 archived (all originals removed) | ~11 (4 communities + 3 bridges + shared + analysis + synthesis + idiomatics) |

## Phase Summary

### M1: Foundation (S0 + V0)

| Phase | Scope | Delivers | Source Skills |
|-------|-------|----------|---------------|
| S0 | Shared Layers | L0 (Expression IR) + L4 (Structural IR) universal schemas; shared across all communities | — |
| V0 | Validation Framework | Round-trip test harness, benchmark project selection, per-step preservation measurement infrastructure | — |

S0 and V0 have no source skills — they are infrastructure phases that partition the Phase 4 global IR into shared and community-specific components.

### M2: Communities (C1 + C2 + C3 + C4)

| Phase | Community | Source Skills | Languages | Coupled Core |
|-------|-----------|---------------|-----------|-------------|
| C1 | Typed-FP | 10 | Haskell, Elm, Scala, F#, OCaml, Roc | None (fully decomposable) |
| C2 | Dynamic-FP | 3 | Erlang, Elixir, Gleam, Clojure | L2+L3 |
| C3 | Object/Managed | 2 | Python, TS, JS, Java, C#, Kotlin, Swift, ObjC | L2+L3 |
| C4 | Systems | 4 | Rust, C, C++, Go, Zig | L1+L3 |

Each community phase delivers:
- Community IR schema (L1-L3 using shared L0+L4)
- Within-community conversion rules for all member language pairs
- Community-specific annotation definitions
- Round-trip tests + benchmarks for within-community pairs

### M3: Bridges (B1 + B2 + B3)

| Phase | Bridge | Source Skills | Chained | Key Transforms |
|-------|--------|--------------|---------|----------------|
| B1 | Typed-FP ↔ Dynamic-FP | 15 | 0 | Static ↔ dynamic types, type classes ↔ protocols, lazy ↔ strict |
| B2 | Dynamic-FP ↔ Object/Managed | 8 | 5 | Actors ↔ objects, pattern match ↔ dispatch, macros ↔ annotations |
| B3 | Object/Managed ↔ Systems | 7 | 0 | GC ↔ ownership, null ↔ Option, exceptions ↔ Result, classes ↔ traits |

Each bridge phase delivers:
- Bridge protocol definition (which layers transform, which pass through)
- Per-layer transform rules with information loss catalog
- Decision point registry (human judgment points)
- Cross-community benchmarks + preservation tracking through bridge
- Chained conversion validation (for bridges enabling non-adjacent paths)

B2 includes 5 chained skills (Object/Managed → Typed-FP via B2→B1) in addition to 3 direct skills.

### M4: Consolidation (F1)

| Phase | Scope | Delivers |
|-------|-------|----------|
| F1 | Archive + Migration | Archive 49 original convert-* skills, migration guide, final validation suite across all communities and bridges |

F1 acceptance criteria:
- All 49 original skills archived with provenance links
- Migration guide for users of old skills
- Full validation suite passing across all communities and bridges
- No regression in conversion quality vs. original skills

## Dependencies on External Work

| Dependency | Impact | Status |
|------------|--------|--------|
| Roc language stability (pre-1.0) | Roc is in Typed-FP community (C1); skills marked provisional until Roc 1.0 | Monitoring |
| Gleam language stability | Gleam is in Dynamic-FP community (C2); document version assumptions | Monitoring |
| IR schema adoption by other plans | None currently — IR is self-contained | N/A |
| Phase 5 Python MVP retargeting | Python extractor/synthesizer must be retargeted to Object/Managed community IR (bounded rework) | Required for C3 |

## Architecture Reference

The tiered IR architecture replaces the Phase 4 global IR with:

- **Shared Layers (L0 + L4)**: Defined once, universal across all communities
- **4 Community IRs**: Each defines L1-L3 with community-specific layer coupling
- **3 Chained Bridges**: Adjacent-community bridge protocols; non-adjacent pairs chain through intermediates

```
                    Shared Layers (L0 + L4)
                 ┌────────────────────────────┐
                 │  L0: Expression IR          │  Defined once.
                 │  L4: Structural IR          │  Universal across all communities.
                 └────────────────────────────┘

       ┌─────────────┬──────────────┬──────────────┬─────────────┐
       │  Typed-FP   │  Dynamic-FP  │ Object/Mgd   │  Systems    │
       │  (C1)       │  (C2)        │  (C3)        │  (C4)       │
       │             │              │              │             │
       │  L1,L2,L3   │  L1,[L2+L3]  │  L1,[L2+L3]  │  [L1+L3],L2 │
       │  all indep  │  coupled     │  coupled     │  coupled    │
       └──────┬──────┴──────┬───────┴──────┬───────┴──────┬──────┘
              │             │              │              │
              └──── B1 ─────┘              │              │
                      └──────── B2 ────────┘              │
                                   └──────── B3 ──────────┘
```

Non-adjacent conversions chain: `Typed-FP →B1→ Dynamic-FP →B2→ Object/Managed →B3→ Systems`

Shortcut bridges deferred until validation data from M3 justifies them.

See [ADR-010](docs/src/adr/adr-010-tiered-ir-architecture.md) for full rationale, evaluation criteria, and migration plan.
