# Phase C1: Community -- Typed-FP

**ID:** C1
**Status:** pending
**Beads:** ai-x3e.15

## Objective

Define the Typed-FP community IR (L1-L3) and merge relevant convert-* skills covering ML-FP family languages: Haskell, Elm, Scala, F#, OCaml, Roc. This community is unique in having NO coupled core -- all layers (L1, L2, L3) are fully independent and can be converted as separate sub-problems. Each layer maps cleanly between all member languages, enabling the simplest community IR of the four.

## Dependencies

- S0 (Shared Layers) -- L0 + L4 schemas must be finalized
- V0 (Validation Framework) -- round-trip and benchmark infrastructure must be available

## Success Criteria

- [ ] Typed-FP community IR schema defined for L1 (Data Flow), L2 (Control Flow), L3 (Type)
- [ ] JSON Schema files for all three community layers published
- [ ] Within-community conversion rules defined for all 15 Typed-FP language pairs
- [ ] Layer independence validated -- each layer converts correctly in isolation
- [ ] Round-trip validation passes at ≥85% preservation for within-community pairs (global default; individual pair thresholds may be adjusted with documented justification)
- [ ] Benchmark baselines established for Typed-FP conversions via V0 framework
- [ ] Community skill created at `context/skills/meta-convert-community-typed-fp-dev/`
- [ ] SKILL.md under 500 lines with progressive disclosure to reference docs

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Community skill | `context/skills/meta-convert-community-typed-fp-dev/SKILL.md` | Merged Typed-FP conversion skill |
| ML-family reference | `context/skills/meta-convert-community-typed-fp-dev/reference/ml-family.md` | Haskell, Elm, F#, OCaml, Roc patterns |
| JVM-FP reference | `context/skills/meta-convert-community-typed-fp-dev/reference/jvm-fp.md` | Scala-specific patterns and JVM interop |
| Type system reference | `context/skills/meta-convert-community-typed-fp-dev/reference/type-systems.md` | ADTs, HKT, type classes across languages |
| Examples | `context/skills/meta-convert-community-typed-fp-dev/examples/` | Representative conversion examples |
| L1 schema | `schemas/ir-community-typed-fp-l1.json` | Data Flow layer JSON Schema |
| L2 schema | `schemas/ir-community-typed-fp-l2.json` | Control Flow layer JSON Schema |
| L3 schema | `schemas/ir-community-typed-fp-l3.json` | Type layer JSON Schema |
| Validation report | `analysis/phaseC1-validation-report.md` | Merge quality and round-trip results |

## Files

**Create:**
- `context/skills/meta-convert-community-typed-fp-dev/SKILL.md`
- `context/skills/meta-convert-community-typed-fp-dev/reference/ml-family.md`
- `context/skills/meta-convert-community-typed-fp-dev/reference/jvm-fp.md`
- `context/skills/meta-convert-community-typed-fp-dev/reference/type-systems.md`
- `context/skills/meta-convert-community-typed-fp-dev/examples/`
- `schemas/ir-community-typed-fp-l1.json`
- `schemas/ir-community-typed-fp-l2.json`
- `schemas/ir-community-typed-fp-l3.json`
- `analysis/phaseC1-validation-report.md`

**Modify:**
- `index.md` -- Update C1 status to complete
- `schemas/ir-v1.json` -- Reference community-specific L1-L3 schemas

## Source Skills (10)

| Skill | Languages | Key Patterns |
|-------|-----------|--------------|
| convert-elm-fsharp | Elm, F# | TEA vs pipelines, discriminated unions |
| convert-elm-haskell | Elm, Haskell | Restricted IO vs monadic IO, TEA vs free monads |
| convert-elm-roc | Elm, Roc | TEA vs abilities, platform/package model |
| convert-elm-scala | Elm, Scala | TEA vs Akka/ZIO, sealed traits vs custom types |
| convert-fsharp-haskell | F#, Haskell | Computation expressions vs monads, .NET interop |
| convert-fsharp-roc | F#, Roc | Pipelines vs chained transforms, .NET types vs Roc types |
| convert-fsharp-scala | F#, Scala | .NET ADTs vs Scala sealed hierarchies, LINQ vs collections |
| convert-haskell-roc | Haskell, Roc | Lazy vs strict, type classes vs abilities |
| convert-haskell-scala | Haskell, Scala | Pure FP vs hybrid OOP-FP, HKT mapping |
| convert-roc-scala | Roc, Scala | Abilities vs implicits, platform model vs build tool |

**Note:** No OCaml convert-* skills currently exist. OCaml is included in the community definition for future extensibility but has no source skills to merge. Skills involving BEAM or LISP languages (e.g., convert-clojure-haskell, convert-elixir-roc) are cross-community and handled by bridge B1, not this phase.

## Layer Coupling

The Typed-FP community has **no coupled core**. All three community-specific layers are fully independent:

| Layer Pair | Coupling | Rationale |
|------------|----------|-----------|
| L1 + L2 | Independent | Pure data transformations (L1) do not depend on control flow dispatch (L2) |
| L1 + L3 | Independent | Immutable bindings (L1) are orthogonal to type definitions (L3) |
| L2 + L3 | Independent | Pattern matching and recursion (L2) work uniformly regardless of type system details (L3) |

**Conversion implication:** Each layer can be converted as a separate sub-problem. A Haskell-to-Scala conversion can independently solve: (1) immutable binding mapping, (2) pattern match / recursion translation, and (3) type class to implicit conversion. This makes Typed-FP the simplest community to validate layer decomposition.

### Community-Specific Layer Definitions

**L1 Data Flow:**
- Immutable bindings (`let`, `val`, `def`)
- Pure transformations (map, filter, fold, bind)
- No mutation -- all state change via new bindings
- Referential transparency guarantees

**L2 Control Flow:**
- Pattern matching (exhaustive, nested, guard clauses)
- Recursion (direct, mutual, tail-call optimized)
- Algebraic effects / abilities (Roc, some Haskell)
- Lazy evaluation (Haskell-specific, annotated)
- Monadic sequencing (do-notation, for-comprehension)

**L3 Type:**
- Algebraic Data Types (sum types, product types)
- Type classes / traits / abilities / implicits
- Higher-Kinded Types (HKT) -- Haskell, Scala
- Type constraints and contexts
- Type inference (Hindley-Milner variants)
- Phantom types, row polymorphism (language-specific extensions)

## Approach

1. **Extract L1-L3 from shared IR** -- Fork community-specific layers from Phase 4's ir-v1.json, scoped to Typed-FP concepts only
2. **Define per-layer conversion rules** -- For each of L1, L2, L3 independently, define how each concept maps between all 6 member languages
3. **Merge source skills into SKILL.md** -- Extract shared patterns from all 10 source skills into a unified skill with progressive disclosure
4. **Build reference docs** -- Organize pair-specific and family-specific details into reference/ directory
5. **Validate layer independence** -- Run round-trip tests converting each layer in isolation to confirm no cross-layer dependencies
6. **Run V0 validation suite** -- Execute round-trip benchmarks and per-layer preservation tracking against V0 framework

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Roc pre-1.0 instability invalidates conversion rules | Medium | Low | Document Roc version assumptions; mark Roc patterns as provisional |
| Haskell lazy evaluation creates hidden L1-L2 coupling | Low | Medium | Annotate laziness in L2 with L1 evaluation strategy markers; validate independence empirically |
| Scala's hybrid OOP-FP nature bleeds Object/Managed concepts into Typed-FP IR | Medium | Medium | Scope Scala's Typed-FP representation to pure FP subset; OOP patterns handled by bridge B2 |
