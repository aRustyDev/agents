# Phase B2: Bridge — Dynamic-FP ↔ Object/Managed

**ID:** B2
**Status:** pending
**Beads:** ai-x3e.20

## Objective

Define the bridge protocol for conversions between Dynamic-FP and Object/Managed communities. This bridge handles actors↔objects, pattern matching↔method dispatch, and process supervision↔exception handling. Within the tiered IR architecture, this bridge transforms L2 (Control Flow) and L3 (Type) layers while passing L0 (Expression), L1 (Data Flow), and L4 (Structural) layers through unchanged. This bridge also enables chained conversion paths: Typed-FP → B1 → Dynamic-FP → B2 → Object/Managed.

## Bridge Scope

| Layer | Behavior | Rationale |
|-------|----------|-----------|
| L0: Expression | **Pass through** | AST/operators/literals are universal |
| L1: Data Flow | **Pass through** | Bindings and data transforms map cleanly between these communities |
| L2: Control Flow | **Transform** | Actor dispatch + supervision ↔ method dispatch + exceptions; macro-based metaprogramming ↔ annotation/decorator-based metaprogramming |
| L3: Type | **Transform** | Dynamic FP types (specs, behaviours) ↔ OOP types (classes, interfaces, inheritance) |
| L4: Structural | **Pass through** | Module/package structure maps across communities |

## Dependencies

- C2 (Community: Dynamic-FP) — provides Dynamic-FP community IR with L1-L3 schemas
- C3 (Community: Object/Managed) — provides Object/Managed community IR with L1-L3 schemas

## Success Criteria

- [ ] Bridge protocol document covers all L2 and L3 transform rules
- [ ] Transform rules validated against 8 source skills (3 direct + 5 chained via B1)
- [ ] Information loss catalog documents what is lost in each direction (actors↔objects, supervision↔exceptions)
- [ ] Decision point registry identifies human-judgment points (e.g., GenServer→class or GenServer→service pattern)
- [ ] Per-step preservation tracking shows L0/L1/L4 pass-through at 100%
- [ ] Round-trip validation passes at ≥85% (global default; may be adjusted per-pair with justification)
- [ ] Chained path validation (Typed-FP → B1 → Dynamic-FP → B2 → Object/Managed) passes preservation thresholds
- [ ] SKILL.md < 200 lines (progressive disclosure)

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Bridge skill | `context/skills/meta-convert-bridge-dynamic-object-dev/SKILL.md` | Bridge protocol and conversion guide |
| L2 transform rules | `context/skills/meta-convert-bridge-dynamic-object-dev/reference/l2-control-flow.md` | Actors ↔ objects, supervision ↔ exceptions |
| L3 transform rules | `context/skills/meta-convert-bridge-dynamic-object-dev/reference/l3-type-system.md` | Dynamic FP types ↔ OOP types |
| Information loss catalog | `context/skills/meta-convert-bridge-dynamic-object-dev/reference/information-loss.md` | Per-direction loss documentation |
| Decision point registry | `context/skills/meta-convert-bridge-dynamic-object-dev/reference/decision-points.md` | Human-judgment points |
| Validation report | `analysis/phaseB2-validation-report.md` | Bridge quality assessment |

## Files

**Create:**
- `context/skills/meta-convert-bridge-dynamic-object-dev/SKILL.md`
- `context/skills/meta-convert-bridge-dynamic-object-dev/reference/l2-control-flow.md`
- `context/skills/meta-convert-bridge-dynamic-object-dev/reference/l3-type-system.md`
- `context/skills/meta-convert-bridge-dynamic-object-dev/reference/information-loss.md`
- `context/skills/meta-convert-bridge-dynamic-object-dev/reference/decision-points.md`
- `analysis/phaseB2-validation-report.md`

**Modify:**
- `index.md` — Update B2 status to complete

## Source Skills (8)

| Skill | Dynamic-FP Side | Object/Managed Side | Route | Key Transform |
|-------|-----------------|---------------------|-------|---------------|
| convert-python-clojure | Clojure | Python | Direct | Persistent data ↔ mutable state, multimethods ↔ polymorphism |
| convert-python-elixir | Elixir | Python | Direct | GenServer ↔ classes, supervision ↔ try/except |
| convert-python-erlang | Erlang | Python | Direct | OTP processes ↔ objects, pattern match ↔ if/elif |
| convert-python-elm | Elm | Python | Chained: B2→B1 | TEA ↔ classes, union types ↔ dynamic types |
| convert-python-fsharp | F# | Python | Chained: B2→B1 | Discriminated unions ↔ dynamic types, pipelines ↔ method chains |
| convert-python-haskell | Haskell | Python | Chained: B2→B1 | Type classes ↔ duck typing, monadic IO ↔ side effects |
| convert-python-roc | Roc | Python | Chained: B2→B1 | Abilities ↔ duck typing, tag unions ↔ dynamic types |
| convert-python-scala | Scala | Python | Chained: B2→B1 | Case classes ↔ dataclasses, implicits ↔ decorators |

## Transform Rules

### L3: Type System Transforms

| Dynamic-FP Concept | Object/Managed Equivalent | Direction Asymmetry |
|---------------------|---------------------------|---------------------|
| Specs/typespecs (Elixir/Erlang) | Type annotations (Python), interfaces (Java/TS) | Low — both are optional/gradual |
| Behaviours (Erlang/Elixir) | Abstract classes / interfaces | Low — structural match |
| Protocols (Elixir) | Interfaces + dispatch (Java/TS), protocols (Python) | Low — good structural match |
| Multimethods (Clojure) | Method overloading / visitor pattern | Medium — dispatch mechanism differs |
| Records/structs (immutable) | Data classes / POJOs (mutable by default) | Medium — mutability semantics differ |
| Tagged tuples | Discriminated unions (TS) / enum classes (Java/Kotlin) | Medium — representation differs |

### L2: Control Flow Transforms

| Dynamic-FP Concept | Object/Managed Equivalent | Direction Asymmetry |
|---------------------|---------------------------|---------------------|
| Actor-based dispatch (GenServer, Agent) | Object method dispatch + state encapsulation | High — concurrency model fundamentally different |
| Process supervision trees | Exception handling + restart logic / circuit breakers | High — fault tolerance model lost |
| Pattern matching (function heads) | Method dispatch + conditionals | Medium — expressiveness reduced |
| Macro-based metaprogramming | Annotation/decorator-based metaprogramming | High — compile-time code generation ↔ runtime decoration |
| Pipeline operator (`\|>`) | Method chaining / builder pattern | Low — syntactic difference, semantics preserved |
| Message passing (async) | Method calls (sync) + async/await | Medium — communication model differs |

## Approach

1. **Analyze direct source skills** — Extract bridge patterns from the 3 skills that directly cross the Dynamic-FP ↔ Object/Managed boundary
2. **Supplement with chained patterns** — Pull relevant cross-boundary patterns from the 5 chained skills (routed through B1)
3. **Define L3 transform rules** — Map dynamic FP type concepts to OOP equivalents, documenting asymmetry and loss
4. **Define L2 transform rules** — Map actor/supervision patterns to object/exception patterns with explicit conversion recipes
5. **Build information loss catalog** — Focus on the supervision→exceptions direction (highest information loss in this bridge)
6. **Validate chained paths** — Test the Typed-FP → B1 → Dynamic-FP → B2 → Object/Managed chain to measure cumulative preservation loss

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Actor→object conversion loses fault tolerance semantics (supervision trees have no OOP equivalent) | High | High | Document as known limitation; provide "best approximation" patterns (circuit breaker, retry decorators); flag for manual review |
| Macro metaprogramming cannot be fully represented by decorators/annotations | Medium | Medium | Emit macros as generated code with documentation; mark expansion points for manual porting |
| Chained B1→B2 path accumulates information loss from both bridges | Medium | High | Per-step preservation tracking detects degradation; shortcut bridge from Typed-FP→Object/Managed added if metrics warrant |
