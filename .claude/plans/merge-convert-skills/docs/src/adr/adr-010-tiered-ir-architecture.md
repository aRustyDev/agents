# ADR-010: Tiered IR Architecture with Layer Decomposition

**Status**: Accepted
**Date**: 2026-03-18
**Context**: Convert Skills IR Schema (Phase 4 revision, before Phase 6 execution)
**Deciders**: Project maintainers
**Supersedes**: None (amends Phase 4 IR design)

## Context

Phase 4 designed a single global 5-layer IR schema where language-family-specific concepts are captured as semantic annotations on IR nodes. This design was chosen for simplicity: one schema, one set of tools, one validation pipeline.

Before beginning Phase 6 (cluster merging), we re-evaluated whether a **tiered IR architecture** would yield better conversion quality. This analysis revealed two orthogonal improvements:

1. **Community-tiered IR** — Languages group into paradigm communities with native IR representations, connected by explicit bridge layers for cross-community conversion.

2. **Layer decomposition** — The 5 IR layers have varying degrees of independence. Some layers (L0, L4) are universal across all communities. Others have community-specific coupling patterns. Conversions can be decomposed into per-layer sub-problems and merged.

### The Problem

The current global IR treats all conversions uniformly. An Erlang→Elixir conversion (difficulty 2, near-identical paradigm) passes through the same IR machinery as an Erlang→Rust conversion (difficulty 4, fundamental paradigm shift). This has consequences:

1. **Within-family overhead**: BEAM→BEAM conversion doesn't need ownership annotations, GC→ownership patterns, or thread safety analysis — yet the global IR schema carries slots for all 54 annotation patterns.

2. **Implicit paradigm crossing**: The annotation system marks family-specific concepts but doesn't structurally separate "same-paradigm translation" from "paradigm-crossing transformation." The difficulty gap between these two operations (2 vs 4-5) suggests they are qualitatively different problems.

3. **Bridge complexity hiding**: Cross-family conversion requires resolving 40 cross-cutting annotation patterns. In the global IR, these are spread across individual annotations. There is no explicit layer where paradigm-crossing decisions are made and documented.

4. **Monolithic conversion**: All 5 layers are converted as a unit, even when some layers are trivially identical between source and target (e.g., L0 Expression IR is nearly the same across all languages).

### Scale of the Design Space

The existing 49 convert-* skills represent a fraction of the full conversion space:

| Scope | Directed Pairs | Coverage |
|-------|----------------|----------|
| Existing skills | 49 | Baseline |
| 23 in-scope languages (all pairs) | 506 | Full matrix |
| Within-family pairs | 82 (16%) | Difficulty 2, near-trivial |
| Cross-family pairs | 424 (84%) | Difficulty 2-5, varies |

The IR architecture must serve all 506 potential pairs, not just the 49 that exist today.

### Key Data Points

**Annotation pattern clustering** (from Phase 3, 54 patterns):

| Scope | Count | % | Implication |
|-------|-------|---|-------------|
| Cross-cutting (4+ families) | 40 | 74% | These are bridge-layer concerns |
| Semi-specific (2-3 families) | 9 | 17% | May live in community or bridge |
| Family-specific (1 family) | 5 | 9% | Native to family/community IR |

**Conversion difficulty matrix** (families, scale 1-5):

|  | ML-FP | BEAM | LISP | Systems | Dynamic | Managed-OOP | Apple |
|--|-------|------|------|---------|---------|-------------|-------|
| **ML-FP** | 2 | 3 | 2 | 4 | 2 | 3 | 3 |
| **BEAM** | 3 | 2 | 2 | 4 | 2 | 3 | 3 |
| **LISP** | 3 | 2 | 2 | 4 | 2 | 3 | 3 |
| **Systems** | 3 | 4 | 3 | 2 | 2 | 2 | 3 |
| **Dynamic** | 3 | 3 | 2 | 4 | 2 | 2 | 3 |
| **Managed-OOP** | 3 | 3 | 3 | 3 | 2 | 2 | 2 |
| **Apple** | 3 | 4 | 3 | 3 | 2 | 2 | 2 |

**Asymmetry ratios** (directional difficulty):

| Conversion | Ratio | Implication |
|-----------|-------|-------------|
| GC → Ownership | 4:1 | Far harder in one direction |
| Static → Dynamic | 1:3 | Easier to erase types than infer them |
| Mutable → Immutable | 3:1 | Algorithm restructuring required |
| Actors ↔ Threads | 1:1 | Symmetric difficulty |

---

## Decision Drivers

1. **Conversion quality**: Within-community conversions should be near-perfect (L3 preservation). Cross-community should explicitly surface where quality degrades.
2. **Architectural honesty**: The IR structure should reflect the actual difficulty landscape — same-paradigm translation and paradigm-crossing transformation are different problems.
3. **Decomposability**: Layers that can be converted independently should be, reducing complexity per sub-problem.
4. **Complexity budget**: Adding tiers and decomposition adds schemas and tooling. The benefit must outweigh this cost.
5. **Tooling cost**: Phase 5 built a Python MVP extractor/synthesizer against the global IR. Rework should be bounded.
6. **Extensibility**: New languages should slot into an existing community without redesigning the bridge layer.

---

## Options Considered

### Option A: Single Global IR (Status Quo)

The Phase 4 design. One 5-layer schema. Family-specific concepts are semantic annotations.

```
Language A → [extract] → Global IR (all 5 layers) → [synthesize] → Language B
                              ↑
                       54 annotation patterns
                       (all carried, most unused per pair)
```

**Strengths:**
- Single schema to maintain, validate, and tool
- All conversions use the same pipeline
- Already designed and partially implemented (Phase 5 MVP)
- No bridge-layer complexity

**Weaknesses:**
- Within-family conversions carry 40+ irrelevant annotation slots
- No structural distinction between easy (difficulty 2) and hard (difficulty 4-5) conversions
- Paradigm-crossing decisions are implicit in annotation values, not explicit in architecture
- Annotation count will grow as more families are added; every conversion pays the cost
- All 5 layers treated as monolithic unit even when some are trivially identical

### Option B: Tiered Community IR with Layer Decomposition (Selected)

Languages extract into a **community IR** that natively represents their paradigm's coupled layers. **Shared layers** (L0, L4) are defined once. Cross-community conversion uses **chained bridges** between adjacent communities. Each conversion is decomposed into per-layer sub-problems.

```
                        Shared Layers (L0 + L4)
                     ┌────────────────────────────┐
                     │  L0: Expression IR          │  Defined once.
                     │  L4: Structural IR          │  Universal across all communities.
                     └────────────────────────────┘

           ┌─────────────┬──────────────┬──────────────┬─────────────┐
           │  Typed-FP   │  Dynamic-FP  │ Object/Mgd   │  Systems    │
           │  Community  │  Community   │  Community   │  Community  │
           │             │              │              │             │
           │  L1: Data   │  L1: Data    │  L1: Data    │  L1+L3:    │
           │  L2: Ctrl   │  L2+L3:      │  L2+L3:      │  Coupled   │
           │  L3: Type   │  Coupled     │  Coupled     │  Core      │
           │  (all indep)│  Core        │  Core        │             │
           │             │              │              │  L2: Ctrl   │
           └──────┬──────┴──────┬───────┴──────┬───────┴──────┬──────┘
                  │             │              │              │
                  └──── B1 ─────┘              │              │
                          └──────── B2 ────────┘              │
                                       └──────── B3 ──────────┘

           B1: Typed-FP ↔ Dynamic-FP bridge
           B2: Dynamic-FP ↔ Object/Managed bridge
           B3: Object/Managed ↔ Systems bridge

           Non-adjacent conversions chain: Typed-FP → B1 → Dynamic-FP → B2 → Object/Managed
```

Full architecture described in [Decision](#decision) section below.

### Option C: Global IR with Community Projections (Middle Ground)

Keep the single global IR schema, but define **community projections** — views that subset the schema and add community-specific sugar.

**Rejected because**: Projections are less semantically rich than true community IRs, and cross-community conversion still works through the annotation system rather than an explicit bridge. Does not fully address the architectural honesty driver.

---

## Decision

**Option B: Tiered Community IR with Layer Decomposition**, using:
- **4 communities**: Typed-FP, Dynamic-FP, Object/Managed, Systems
- **Chained bridges**: 3 adjacent bridges with chaining for non-adjacent pairs
- **Shared layers**: L0 + L4 defined once, shared across all communities
- **Layer decomposition**: Conversions decomposed into per-layer sub-problems with community-specific coupling

### 4-Community Model

| Community | Families | Languages | Coupled Core |
|-----------|----------|-----------|-------------|
| **Typed-FP** | ML-FP | Haskell, Elm, Scala, F#, OCaml, Roc | None (fully decomposable) |
| **Dynamic-FP** | BEAM, LISP | Erlang, Elixir, Gleam, Clojure | L2+L3 |
| **Object/Managed** | Dynamic, Managed-OOP, Apple | Python, TS, JS, Java, C#, Kotlin, Swift, ObjC | L2+L3 |
| **Systems** | Systems | Rust, C, C++, Go, Zig | L1+L3 |

**Rationale for 4 over 3**: ML-FP ↔ BEAM difficulty is 3, and ML-FP's type system concepts (HKT, type classes, variance) are absent from BEAM/LISP. The split keeps each community internally cohesive at difficulty ≤ 2.

### Layer Architecture

#### Shared Layers (defined once)

**Layer 0: Expression IR** — Full AST, operator semantics, literal values. Nearly identical across all languages. Conversion is syntax mapping.

**Layer 4: Structural IR** — Modules, packages, namespaces, imports/exports. Surface syntax differs but concepts are universal. Conversion is structural mapping.

These layers are **always independent** of the conversion's paradigm. Every community uses the same L0 and L4 definitions.

#### Community Layers (L1-L3)

Each community defines its own L1-L3, with community-specific coupling:

| Community | L1 Data Flow | L2 Control Flow | L3 Type | Coupling |
|-----------|-------------|----------------|---------|----------|
| **Typed-FP** | Immutable bindings, transforms | Pattern match, recursion, effects | ADTs, type classes, HKT, constraints | None — all independent |
| **Dynamic-FP** | Dynamic bindings, transforms | Actor dispatch, message passing, macros | Dynamic types, protocols, specs | L2+L3 coupled (dispatch depends on type info) |
| **Object/Managed** | Mutable variables, assignments | Method dispatch, exceptions, async/await | Classes, interfaces, inheritance, generics | L2+L3 coupled (method dispatch depends on class hierarchy) |
| **Systems** | Ownership, lifetimes, borrows | Unsafe blocks, inline, intrinsics | Traits, generics, raw types, sized | L1+L3 coupled (ownership depends on types) |

#### Layer Coupling Analysis

The degree of inter-layer dependency varies by community:

```
Typed-FP:       L0  L1  L2  L3  L4    ← all independent, fully decomposable
Dynamic-FP:     L0  L1  [L2+L3]  L4   ← L2+L3 solved together
Object/Managed: L0  L1  [L2+L3]  L4   ← L2+L3 solved together
Systems:        L0  [L1+L3]  L2  L4   ← L1+L3 solved together
```

**Implication**: A conversion is a combination of sub-problems. The coupled core is solved as a unit; independent layers are solved separately. The final output merges all layer solutions.

#### Conversion as Composed Sub-Problems

```
Source → [L0 convert] → [L1 convert*] → [L2 convert*] → [L3 convert*] → [L4 convert] → [merge] → Target
              ↑                                                               ↑
         shared layer                                                    shared layer
         (community-independent)                                        (community-independent)

         * coupled layers solved together as a unit within each community
```

For **within-community** conversion (e.g., Haskell → Scala, both Typed-FP):
- L0: syntax mapping (independent, trivial)
- L1: binding model mapping (independent, often near-identity)
- L2: control flow mapping (independent)
- L3: type system mapping (independent)
- L4: module structure mapping (independent, trivial)
- Each layer is a small, focused sub-problem.

For **cross-community** conversion (e.g., Python → Rust, Object/Managed → Systems):
- L0: syntax mapping (shared layer, trivial)
- L4: module mapping (shared layer, trivial)
- Source community coupled core (L2+L3): extract into community IR
- Bridge: transform from source community's coupled core to target's
- Target community coupled core (L1+L3): synthesize from community IR
- The bridge focuses only on the layers that diverge.

### Bridge Architecture

#### Chained Adjacent Bridges

Three bridges connect adjacent communities:

| Bridge | Communities | Key Transforms | Difficulty |
|--------|-----------|---------------|------------|
| **B1** | Typed-FP ↔ Dynamic-FP | Static types ↔ dynamic types, type classes ↔ protocols, lazy ↔ strict | 3 |
| **B2** | Dynamic-FP ↔ Object/Managed | Actors/processes ↔ objects/threads, pattern match ↔ dispatch, macros ↔ annotations | 2-3 |
| **B3** | Object/Managed ↔ Systems | GC ↔ ownership, null ↔ Option, exceptions ↔ Result, classes ↔ traits | 3-4 |

**Adjacency chain**: `Typed-FP ←B1→ Dynamic-FP ←B2→ Object/Managed ←B3→ Systems`

#### Non-Adjacent Conversion via Chaining

Non-adjacent pairs chain through intermediate communities:

| Conversion | Path | Bridges Used |
|-----------|------|-------------|
| Typed-FP → Object/Managed | Typed-FP →B1→ Dynamic-FP →B2→ Object/Managed | B1 + B2 |
| Typed-FP → Systems | Typed-FP →B1→ Dynamic-FP →B2→ Object/Managed →B3→ Systems | B1 + B2 + B3 |
| Dynamic-FP → Systems | Dynamic-FP →B2→ Object/Managed →B3→ Systems | B2 + B3 |

**Shortcut bridge policy**: Start with pure chaining (3 bridges). Add direct shortcut bridges later only if validation metrics show unacceptable quality degradation on chained paths. The layer decomposition already limits what each bridge transforms (only divergent coupled-core layers), so chaining overhead may be tolerable.

#### Bridge Scope

Each bridge only transforms the layers that diverge between the two communities. Shared layers (L0, L4) and identical independent layers pass through untouched.

| Bridge | Layers Transformed | Layers Passed Through |
|--------|-------------------|--------------------|
| B1 (Typed-FP ↔ Dynamic-FP) | L2, L3 (static↔dynamic types, effect models) | L0, L1, L4 |
| B2 (Dynamic-FP ↔ Object/Managed) | L2, L3 (actors↔objects, dispatch models) | L0, L1, L4 |
| B3 (Object/Managed ↔ Systems) | L1, L2, L3 (GC↔ownership, exceptions↔Result, classes↔traits) | L0, L4 |

Note: B3 transforms the most layers because the paradigm gap between Object/Managed and Systems is the widest (GC→ownership affects data flow L1, not just types L3).

#### Bridge Protocol

```yaml
bridge_conversion:
  source_community: typed_fp | dynamic_fp | object_managed | systems
  target_community: typed_fp | dynamic_fp | object_managed | systems
  bridge_id: B1 | B2 | B3

  # Which layers this bridge transforms
  transformed_layers: [L1, L2, L3]  # varies by bridge
  passed_through_layers: [L0, L4]   # always includes shared layers

  # Per-layer paradigm transforms
  layer_transforms:
    L3:  # example: type system
      - pattern_id: "TS-001"
        source_concept: "gc_reference"
        target_concept: "owned_value"
        decision: "infer_lifetime_from_scope"
        confidence: 0.7
        human_review: true

  # Information loss tracking
  lossy_transforms:
    - pattern_id: "EF-009"
      layer: L2
      information_lost: "lazy_evaluation_semantics"
      mitigation: "wrap_in_thunk_where_needed"
      preservation_level: 2

  # Decision points requiring human judgment
  decision_points:
    - id: "DP-003"
      layer: L1
      question: "How should actor state be modeled in ownership-based language?"
      options: ["Arc<Mutex<T>>", "channel-based", "actor-framework"]
      default: "channel-based"
```

### Community Boundary Decisions

#### Go: Systems Community

| Factor | Verdict |
|--------|---------|
| Concurrency | Goroutines + channels align with systems concurrency patterns |
| Memory | GC, but manual allocation available; annotate GC in community IR |
| Existing skills | 2 Go→Systems skills, 0 Go→OOP skills |

Go's goroutines and channels align more with systems concurrency patterns than OOP event loops. GC is captured as an annotation within the Systems community IR.

#### Scala: Typed-FP Community

| Factor | Verdict |
|--------|---------|
| Type system | ADTs, pattern matching, HKT — functional first |
| Existing skills | 8 Scala↔FP skills, 1 Scala→Java |
| Runtime | JVM is implementation detail, not paradigm concern |

#### TypeScript: Object/Managed Community

| Factor | Verdict |
|--------|---------|
| Type system | Classes, interfaces, generics align with C#/Java |
| Paradigm | Multi-paradigm but class-based is primary path |

JavaScript is also Object/Managed. Both share the community despite JS lacking static types — the bridge to Dynamic-FP handles that concern.

### Validation Strategy

Three complementary approaches, all required:

#### 1. Round-Trip Tests (Resilience)

Verify that `A → IR → B → IR → A` preserves semantics:

```
Source A → [extract to community IR] → [synthesize to B] → [extract to community IR] → [synthesize to A'] → compare A ≈ A'
```

Measure: Does A still look like A after a round trip? Capture structural diff, semantic diff, and preservation level.

#### 2. Benchmark Projects (Real-World Quality)

Select 10-20 example projects per language (scoped to 1-2 languages initially). Test how well the IR supports various conversion types:

| Category | Example Projects | Tests |
|----------|-----------------|-------|
| Within-community | Small Haskell lib → Scala | Measure all 5 layers independently |
| Cross-community (adjacent) | Python module → Elixir | Measure bridge quality |
| Cross-community (chained) | Haskell module → Rust | Measure chained bridge quality |

#### 3. Per-Step Preservation Tracking (Granular Quality)

Measure preservation level (0-3) after **each conversion step**, not just end-to-end:

```
Source
  → [L0 convert] → measure(L0)
  → [L1 convert] → measure(L1)
  → [L2 convert] → measure(L2)
  → [L3 convert] → measure(L3)
  → [L4 convert] → measure(L4)
  → [merge]      → measure(final)
```

If bridge chaining is involved:
```
Source
  → [extract to Community A IR]   → measure(per-layer)
  → [Bridge B1: transform layers] → measure(per-layer)
  → [Bridge B2: transform layers] → measure(per-layer)
  → [synthesize to Target]        → measure(final)
```

Each measurement captures:
- **Preservation level** (0=syntactically valid, 1=semantically equivalent, 2=idiomatically correct, 3=optimized)
- **Information loss catalog** (what was lost, why, mitigation applied)
- **Decision points hit** (which required human judgment, which were auto-resolved)
- **Per-layer quality** (which layer degraded, by how much)

This tells us *which layer* and *which bridge* is losing information, enabling targeted improvement.

---

## Evaluation

### Criteria Scoring

| Criterion | Weight | Option A (Global) | Option B (Tiered + Decomposed) |
|-----------|--------|-------------------|-------------------------------|
| Within-community quality | High | 3 — annotations add overhead | 5 — native coupled-core, no noise |
| Cross-community quality | High | 3 — decisions implicit | 5 — bridge makes decisions explicit, per-layer |
| Architectural honesty | Medium | 2 — one-size-fits-all | 5 — structure matches difficulty + coupling |
| Decomposability | Medium | 1 — monolithic conversion | 5 — per-layer sub-problems |
| Implementation complexity | Medium | 5 — already designed | 2 — shared layers + 4 communities + 3 bridges |
| Phase 5 rework cost | Medium | 5 — no rework | 3 — retarget to community IR |
| Extensibility (new languages) | Low | 4 — add annotations | 5 — slot into community |
| Extensibility (new families) | Low | 3 — annotation count grows | 4 — new community or expand existing |

**Weighted scores** (High=3, Medium=2, Low=1):
- **Option A**: (3×3) + (3×3) + (2×2) + (1×2) + (5×2) + (5×2) + (4×1) + (3×1) = 9+9+4+2+10+10+4+3 = **51**
- **Option B**: (5×3) + (5×3) + (5×2) + (5×2) + (2×2) + (3×2) + (5×1) + (4×1) = 15+15+10+10+4+6+5+4 = **69**

### Annotation Burden Analysis

For a within-community conversion (e.g., Erlang→Elixir):

| Approach | Annotations Processed | Relevant | Overhead |
|----------|----------------------|----------|----------|
| Option A (Global) | 54 | ~5 | 91% waste |
| Option B (Community IR) | ~10 (Dynamic-FP) | ~5 | 50% waste |

For a cross-community conversion (e.g., Python→Rust):

| Approach | Annotations Processed | Relevant | Overhead |
|----------|----------------------|----------|----------|
| Option A (Global) | 54 | ~25 | 54% waste |
| Option B (Bridge) | ~25 (bridge-scoped) | ~25 | 0% waste |

---

## Revised Phase Structure

The current Phases 6-10 are replaced with a restructured plan:

### Foundation Phases

| Phase | ID | Scope | Delivers |
|-------|----|-------|----------|
| **S0** | Shared Layers | L0 + L4 schema definitions | Universal Expression IR and Structural IR, shared across all communities |
| **V0** | Validation Framework | Test infrastructure | Round-trip harness, benchmark project selection, per-step preservation measurement |

### Community Phases (1 per community)

| Phase | ID | Community | Coupled Core | Key Challenge |
|-------|----|-----------|-------------|---------------|
| **C1** | Typed-FP | Typed-FP | None (fully decomposable) | Type class mapping, HKT representation, variance |
| **C2** | Dynamic-FP | Dynamic-FP | L2+L3 | Actor/process model, dynamic dispatch, macro systems |
| **C3** | Object/Managed | Object/Managed | L2+L3 | Inheritance hierarchies, null handling, GC semantics |
| **C4** | Systems | Systems | L1+L3 | Ownership model, lifetime inference, borrow checking |

Each community phase delivers:
- Community IR schema (L1-L3, using shared L0+L4)
- Within-community conversion rules for all member language pairs
- Community-specific annotation definitions
- Validation: round-trip tests + benchmarks for within-community pairs

### Bridge Phases (1 per adjacent bridge)

| Phase | ID | Bridge | Communities | Key Transforms |
|-------|----|--------|-----------|---------------|
| **B1** | Bridge: Typed-FP ↔ Dynamic-FP | B1 | Typed-FP, Dynamic-FP | Static ↔ dynamic types, type classes ↔ protocols |
| **B2** | Bridge: Dynamic-FP ↔ Object/Managed | B2 | Dynamic-FP, Object/Managed | Actors ↔ objects, pattern match ↔ dispatch |
| **B3** | Bridge: Object/Managed ↔ Systems | B3 | Object/Managed, Systems | GC ↔ ownership, exceptions ↔ Result |

Each bridge phase delivers:
- Bridge protocol definition (which layers transform, which pass through)
- Per-layer transform rules
- Information loss catalog and decision point registry
- Validation: cross-community benchmarks + preservation tracking through bridge
- Chained conversion validation (for bridges that enable non-adjacent paths)

### Consolidation Phase

| Phase | ID | Scope |
|-------|----|-------|
| **F1** | Final Consolidation | Archive 49 original skills, create migration guide, final validation suite |

### Phase Dependencies

```
S0 (Shared Layers) ──────────────────────────────────────────────┐
V0 (Validation) ─────────────────────────────────────────────────┤
    │                                                            │
    ├── C1 (Typed-FP) ──────┐                                   │
    ├── C2 (Dynamic-FP) ────┤                                   │
    ├── C3 (Object/Managed) ┤                                   │
    └── C4 (Systems) ───────┤                                   │
                            │                                    │
            C1 + C2 ────── B1 (Typed-FP ↔ Dynamic-FP)          │
            C2 + C3 ────── B2 (Dynamic-FP ↔ Object/Managed)    │
            C3 + C4 ────── B3 (Object/Managed ↔ Systems)       │
                            │                                    │
                            └── F1 (Consolidation) ◄────────────┘
```

- S0 and V0 can run in parallel; both must complete before any community phase
- C1-C4 can run in parallel (no dependencies between communities)
- Each bridge requires its two adjacent community phases to complete
- B1, B2, B3 can run in parallel once their dependencies are met
- F1 requires all bridges to complete

### Mapping from Old to New Phases

| Old Phase | Status | Maps To |
|-----------|--------|---------|
| Phase 6 (Cluster A: 28 FP-internal) | Replaced | C1 + C2 (FP skills split across Typed-FP and Dynamic-FP communities) |
| Phase 7 (Cluster B: 8 Dynamic→FP) | Replaced | B2 (these are bridge patterns: Object/Managed → Functional) |
| Phase 8 (Cluster C: 9 Systems) | Replaced | C4 (Systems community definition) |
| Phase 9 (Cluster D: 4 Cross-Paradigm) | Replaced | B1 + B3 (these are bridge patterns across various communities) |
| Phase 10 (Final Consolidation) | Renamed | F1 (same scope, updated references) |

---

## Migration from Current Design

| Current Artifact | New Role | Changes Needed |
|-----------------|----------|---------------|
| Phase 4 global IR schema (5 layers) | Refactored: L0+L4 → shared; L1-L3 → community templates | Partition, not rewrite |
| Phase 4 annotation system (54 patterns) | Partitioned: ~14 per community + ~40 in bridges | Classify each pattern by scope |
| Phase 5 Python extractor | Object/Managed community extractor | Narrow output to community L1-L3 + shared L0+L4 |
| Phase 5 Python synthesizer | Object/Managed community synthesizer | Narrow input schema |
| Cluster merge template | Community-aligned template | Update for layer decomposition + bridge references |
| 49 existing convert-* skills | Source material for community + bridge phases | Classify each into community or bridge |

---

## Consequences

### Accepted

- Phase 4 IR schema is partitioned: L0+L4 shared, L1-L3 per community (structural refactoring)
- Four community IR schemas must be defined (community-specific L1-L3 + coupling rules)
- Three bridge protocols must be designed (layer transform rules + loss tracking)
- Shared layer schemas defined once (L0 Expression + L4 Structural)
- Validation framework built with all three approaches (round-trip, benchmark, per-step preservation)
- Phases 6-10 replaced with S0, V0, C1-C4, B1-B3, F1 (10 phases)
- Community phases (C1-C4) can run in parallel, potentially faster than sequential cluster merges
- Phase 5 MVP needs retargeting to community IR (~bounded rework)
- New languages slot into existing community without touching bridges
- Shortcut bridges for high-demand non-adjacent pairs deferred until validation data justifies them

### Risks

| Risk | Mitigation |
|------|-----------|
| Community boundary disputes (e.g., Go) | Documented boundary decisions with rationale; annotation system handles edge cases |
| Chained bridge quality degradation | Per-step preservation tracking detects degradation; shortcut bridges added if metrics warrant |
| Increased schema count (shared + 4 communities + 3 bridges) | Layer decomposition means each schema is smaller; shared layers reduce duplication |
| Phase 5 rework scope creep | Rework is narrowing (remove unused annotations), not widening; community IR is a subset of global |

---

## Appendix: Layer Coupling Evidence

To validate the coupling analysis, we tested representative conversions:

### Python → Rust (Object/Managed → Systems)

| Layer | Python | Rust | Independent? |
|-------|--------|------|-------------|
| L4 | `import greeting` | `mod greeting; use greeting::*;` | **Yes** — structural mapping |
| L3 | `name: str` | `&str` or `String`? | **No** — type depends on ownership (L1) |
| L2 | `def greet(name): return f"..."` | `fn greet(name: ...) -> String { format!(...) }` | **Yes** — control flow mapping |
| L1 | `name` is GC'd reference | Borrowed or owned? | **No** — depends on type choice (L3) |
| L0 | `f"Hello, {name}"` | `format!("Hello, {}", name)` | **Yes** — syntax mapping |

**Result**: L1+L3 coupled (ownership + types), confirming Systems community coupling pattern.

### Haskell → Scala (Typed-FP, within-community)

| Layer | Independent? | Why |
|-------|-------------|-----|
| L4 | Yes | module → package object |
| L3 | Yes | type class → implicit, ADT → sealed trait |
| L2 | Yes | lazy→strict is expression-local |
| L1 | Yes (near-identity) | both immutable bindings |
| L0 | Yes | syntax mapping |

**Result**: Fully decomposable, confirming Typed-FP has no coupled core.

### Elixir → Python (Dynamic-FP → Object/Managed)

| Layer | Independent? | Why |
|-------|-------------|-----|
| L4 | Yes | modules → packages |
| L3 | **No** (coupled with L2) | protocol dispatch determines type mapping |
| L2 | **No** (coupled with L3) | pattern matching → method dispatch depends on types |
| L1 | Yes | dynamic bindings in both |
| L0 | Yes | syntax mapping |

**Result**: L2+L3 coupled, confirming both Dynamic-FP and Object/Managed coupling patterns. Bridge B2 transforms L2+L3 as a unit.
