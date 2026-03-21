# Phase B1: Bridge — Typed-FP ↔ Dynamic-FP

**ID:** B1
**Status:** pending
**Beads:** ai-x3e.19

## Objective

Define the bridge protocol for conversions between Typed-FP and Dynamic-FP communities. This bridge handles static↔dynamic type system transitions, type classes↔protocols, and lazy↔strict evaluation. Within the tiered IR architecture, this bridge transforms L2 (Control Flow) and L3 (Type) layers while passing L0 (Expression), L1 (Data Flow), and L4 (Structural) layers through unchanged.

## Bridge Scope

| Layer | Behavior | Rationale |
|-------|----------|-----------|
| L0: Expression | **Pass through** | AST/operators/literals are universal across FP paradigms |
| L1: Data Flow | **Pass through** | Bindings and transforms are similar in both communities |
| L2: Control Flow | **Transform** | Pure functions with effects ↔ actor-based dispatch with message passing; lazy evaluation (Haskell) ↔ strict evaluation (BEAM/LISP) |
| L3: Type | **Transform** | Static types (HKT, type classes, ADTs) ↔ dynamic types (specs, protocols, behaviours) |
| L4: Structural | **Pass through** | Module/import structure maps cleanly across FP communities |

## Dependencies

- C1 (Community: Typed-FP) — provides Typed-FP community IR with L1-L3 schemas
- C2 (Community: Dynamic-FP) — provides Dynamic-FP community IR with L1-L3 schemas

## Success Criteria

- [ ] Bridge protocol document covers all L2 and L3 transform rules
- [ ] Transform rules validated against 15 source skills (cross-community FP pairs)
- [ ] Information loss catalog documents what is lost in each direction
- [ ] Decision point registry identifies all human-judgment points in the bridge
- [ ] Per-step preservation tracking shows L0/L1/L4 pass-through at 100%
- [ ] Round-trip validation passes at ≥85% (global default; may be adjusted per-pair with justification)
- [ ] Chained conversion path (Typed-FP → Dynamic-FP) validated end-to-end
- [ ] SKILL.md < 200 lines (progressive disclosure)

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Bridge skill | `context/skills/meta-convert-bridge-typed-dynamic-dev/SKILL.md` | Bridge protocol and conversion guide |
| L2 transform rules | `context/skills/meta-convert-bridge-typed-dynamic-dev/reference/l2-control-flow.md` | Effects ↔ actors, lazy ↔ strict |
| L3 transform rules | `context/skills/meta-convert-bridge-typed-dynamic-dev/reference/l3-type-system.md` | Static types ↔ dynamic types |
| Information loss catalog | `context/skills/meta-convert-bridge-typed-dynamic-dev/reference/information-loss.md` | Per-direction loss documentation |
| Decision point registry | `context/skills/meta-convert-bridge-typed-dynamic-dev/reference/decision-points.md` | Human-judgment points |
| Validation report | `analysis/phaseB1-validation-report.md` | Bridge quality assessment |

## Files

**Create:**
- `context/skills/meta-convert-bridge-typed-dynamic-dev/SKILL.md`
- `context/skills/meta-convert-bridge-typed-dynamic-dev/reference/l2-control-flow.md`
- `context/skills/meta-convert-bridge-typed-dynamic-dev/reference/l3-type-system.md`
- `context/skills/meta-convert-bridge-typed-dynamic-dev/reference/information-loss.md`
- `context/skills/meta-convert-bridge-typed-dynamic-dev/reference/decision-points.md`
- `analysis/phaseB1-validation-report.md`

**Modify:**
- `index.md` — Update B1 status to complete

## Source Skills (15)

These are the convert-* skills that cross the Typed-FP ↔ Dynamic-FP community boundary:

| Skill | Typed-FP Side | Dynamic-FP Side | Key Transform |
|-------|---------------|-----------------|---------------|
| convert-clojure-elm | Elm | Clojure | Specs ↔ types |
| convert-clojure-fsharp | F# | Clojure | Discriminated unions ↔ multimethods |
| convert-clojure-haskell | Haskell | Clojure | Multimethods ↔ type classes |
| convert-clojure-roc | Roc | Clojure | Platform model ↔ runtime polymorphism |
| convert-clojure-scala | Scala | Clojure | Case classes ↔ records |
| convert-elixir-elm | Elm | Elixir | Behaviours ↔ union types |
| convert-elixir-fsharp | F# | Elixir | Pipelines ↔ pipelines (similar) |
| convert-elixir-haskell | Haskell | Elixir | Protocols ↔ type classes |
| convert-elixir-roc | Roc | Elixir | Tag unions ↔ protocols |
| convert-elixir-scala | Scala | Elixir | Implicits ↔ protocols |
| convert-elm-erlang | Elm | Erlang | OTP patterns ↔ TEA |
| convert-erlang-fsharp | F# | Erlang | Computation expressions ↔ OTP |
| convert-erlang-haskell | Haskell | Erlang | Process model ↔ monadic IO |
| convert-erlang-roc | Roc | Erlang | Abilities ↔ behaviours |
| convert-erlang-scala | Scala | Erlang | Akka actors ↔ OTP actors |

## Transform Rules

### L3: Type System Transforms

| Typed-FP Concept | Dynamic-FP Equivalent | Direction Asymmetry |
|-------------------|-----------------------|---------------------|
| Higher-kinded types (HKT) | No equivalent; flatten to concrete types | High — HKT lost in Typed→Dynamic |
| Type classes | Protocols (Elixir), behaviours (Erlang), multimethods (Clojure) | Medium — structural match but no compile-time enforcement |
| Algebraic data types (ADTs) | Tagged tuples (BEAM), tagged maps (Clojure) | Low — structural match, type safety lost |
| Parametric polymorphism | Runtime polymorphism via specs/contracts | Medium — generic behavior preserved, static guarantees lost |
| Phantom types | No equivalent; documentation only | High — information lost entirely |

### L2: Control Flow Transforms

| Typed-FP Concept | Dynamic-FP Equivalent | Direction Asymmetry |
|-------------------|-----------------------|---------------------|
| Monadic effects (IO, Effect) | Actor-based message passing | High — fundamentally different models |
| Lazy evaluation (Haskell) | Strict evaluation with explicit streams | Medium — semantics change |
| Pure functions with effect tracking | Functions with side effects (untracked) | High — purity guarantees lost |
| Pattern matching (exhaustive, type-checked) | Pattern matching (runtime, non-exhaustive) | Low — syntax similar, guarantees differ |

## Approach

1. **Extract cross-community patterns** — Analyze the 15 source skills to identify shared bridge patterns between Typed-FP and Dynamic-FP languages
2. **Define L3 transform rules** — Map each static type concept to its dynamic equivalent, documenting asymmetry ratios and information loss
3. **Define L2 transform rules** — Map control flow paradigms (effects, evaluation strategy) with explicit conversion recipes
4. **Build information loss catalog** — For each transform rule, document what is lost in each direction and available mitigations
5. **Create decision point registry** — Identify points where human judgment is needed (e.g., choosing between Elixir protocols vs behaviours for a type class)
6. **Validate with round-trip tests** — Run Typed-FP → Dynamic-FP → Typed-FP conversions through the bridge and measure preservation

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| HKT and phantom types cause high information loss in Typed→Dynamic direction | High | Medium | Document as known limitation; provide "best approximation" recipes rather than exact translations |
| Lazy↔strict evaluation changes program semantics (not just syntax) | Medium | High | Require explicit annotation of evaluation-sensitive code; flag sections needing manual review |
| 15 source skills may have inconsistent patterns for same concept | Medium | Medium | Prioritize most-used pairs (Haskell↔Elixir, Scala↔Clojure); resolve conflicts via Phase 3 decision points |
