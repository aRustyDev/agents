# Phase B3: Bridge — Object/Managed ↔ Systems

**ID:** B3
**Status:** pending
**Beads:** ai-x3e.21

## Objective

Define the bridge protocol for conversions between Object/Managed and Systems communities. This is the widest paradigm gap in the architecture — spanning GC↔ownership, null↔Option, exceptions↔Result, and classes↔traits. Within the tiered IR architecture, this bridge transforms L1 (Data Flow), L2 (Control Flow), and L3 (Type) layers — all three community-specific layers — while passing only L0 (Expression) and L4 (Structural) through unchanged. The GC→ownership direction has a 4:1 asymmetry ratio, making it significantly harder than the reverse.

## Bridge Scope

| Layer | Behavior | Rationale |
|-------|----------|-----------|
| L0: Expression | **Pass through** | AST/operators/literals are universal |
| L1: Data Flow | **Transform** | GC references ↔ ownership/borrowing/lifetimes; this is the hardest transform in the entire architecture (4:1 asymmetry) |
| L2: Control Flow | **Transform** | Exceptions ↔ Result types; async/await models differ; virtual dispatch ↔ static dispatch + monomorphization |
| L3: Type | **Transform** | Classes/interfaces/inheritance ↔ traits/impls/generics; null ↔ Option; reference types ↔ value types |
| L4: Structural | **Pass through** | Module/package structure maps across communities |

## Dependencies

- C3 (Community: Object/Managed) — provides Object/Managed community IR with L1-L3 schemas
- C4 (Community: Systems) — provides Systems community IR with L1-L3 schemas

## Success Criteria

- [ ] Bridge protocol document covers L1, L2, and L3 transform rules (all community layers)
- [ ] GC↔ownership transform rules documented with 4:1 asymmetry handling
- [ ] Information loss catalog documents all losses, particularly in the Object→Systems direction
- [ ] Decision point registry identifies all human-judgment points (ownership inference is the largest)
- [ ] Per-step preservation tracking shows L0/L4 pass-through at 100%
- [ ] Round-trip validation passes at ≥85% (global default; may be adjusted per-pair with justification)
- [ ] Full chain validation (Typed-FP → B1 → Dynamic-FP → B2 → Object/Managed → B3 → Systems) passes thresholds
- [ ] SKILL.md < 200 lines (progressive disclosure)

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Bridge skill | `context/skills/meta-convert-bridge-object-systems-dev/SKILL.md` | Bridge protocol and conversion guide |
| L1 transform rules | `context/skills/meta-convert-bridge-object-systems-dev/reference/l1-data-flow.md` | GC ↔ ownership/borrowing/lifetimes |
| L2 transform rules | `context/skills/meta-convert-bridge-object-systems-dev/reference/l2-control-flow.md` | Exceptions ↔ Result, dispatch models |
| L3 transform rules | `context/skills/meta-convert-bridge-object-systems-dev/reference/l3-type-system.md` | Classes ↔ traits, null ↔ Option |
| Information loss catalog | `context/skills/meta-convert-bridge-object-systems-dev/reference/information-loss.md` | Per-direction loss documentation |
| Decision point registry | `context/skills/meta-convert-bridge-object-systems-dev/reference/decision-points.md` | Human-judgment points (ownership inference) |
| Validation report | `analysis/phaseB3-validation-report.md` | Bridge quality assessment |

## Files

**Create:**
- `context/skills/meta-convert-bridge-object-systems-dev/SKILL.md`
- `context/skills/meta-convert-bridge-object-systems-dev/reference/l1-data-flow.md`
- `context/skills/meta-convert-bridge-object-systems-dev/reference/l2-control-flow.md`
- `context/skills/meta-convert-bridge-object-systems-dev/reference/l3-type-system.md`
- `context/skills/meta-convert-bridge-object-systems-dev/reference/information-loss.md`
- `context/skills/meta-convert-bridge-object-systems-dev/reference/decision-points.md`
- `analysis/phaseB3-validation-report.md`

**Modify:**
- `index.md` — Update B3 status to complete

## Source Skills (7)

| Skill | Object/Managed Side | Systems Side | Key Transform |
|-------|---------------------|--------------|---------------|
| convert-java-c | Java | C | GC → manual malloc/free, OOP → procedural |
| convert-java-cpp | Java | C++ | GC → RAII, checked exceptions → RAII/noexcept |
| convert-java-rust | Java | Rust | GC → ownership, exceptions → Result |
| convert-python-golang | Python | Go | Dynamic → static, GIL → goroutines |
| convert-python-rust | Python | Rust | GC → ownership, dynamic → static types |
| convert-typescript-golang | TypeScript | Go | Async/await → goroutines, classes → structs |
| convert-typescript-rust | TypeScript | Rust | Any/union → generics, async → futures |

## Transform Rules

### L1: Data Flow Transforms (Hardest Layer)

| Object/Managed Concept | Systems Equivalent | Direction Asymmetry |
|-------------------------|--------------------|---------------------|
| GC-managed references | Ownership + borrowing + lifetimes (Rust), manual malloc/free (C) | **4:1** — GC→ownership requires inferring ownership semantics from usage patterns |
| Shared mutable state | `Arc<Mutex<T>>` (Rust), mutex-guarded pointers (C/C++) | High — shared mutability is the default in managed, requires explicit wrapping in systems |
| Reference counting (Swift) | `Rc<T>` / `Arc<T>` (Rust) | Low — structural match |
| Nullable references | `Option<T>` (Rust), raw pointers (C/C++) | Medium — null semantics must be audited |
| Object graphs (cyclic) | Weak references + explicit ownership trees | High — GC handles cycles automatically; systems code must break them |

### L2: Control Flow Transforms

| Object/Managed Concept | Systems Equivalent | Direction Asymmetry |
|-------------------------|--------------------|---------------------|
| Exceptions (try/catch/finally) | Result<T, E> + ? operator (Rust), error codes (C), exceptions (C++) | High — exception semantics have no direct Rust/C equivalent |
| Virtual dispatch (vtable) | Static dispatch + monomorphization (Rust), vtable (C++) | Medium — performance characteristics change |
| Async/await (Promise-based) | Async/await (Future-based in Rust), goroutines (Go) | Medium — runtime model differs |
| Garbage collection pauses | No equivalent; deterministic destruction | Low — Systems side has advantage |
| Thread pools + executors | Async runtimes (tokio), OS threads, goroutines | Medium — concurrency primitives differ |

### L3: Type System Transforms

| Object/Managed Concept | Systems Equivalent | Direction Asymmetry |
|-------------------------|--------------------|---------------------|
| Classes + inheritance | Traits + impls + composition (Rust), structs + functions (C/Go) | High — inheritance hierarchies must be decomposed |
| Interfaces | Traits (Rust), interfaces (Go) | Low — good structural match |
| Generics (type erasure in Java) | Generics (monomorphized in Rust/C++) | Medium — runtime vs compile-time polymorphism |
| Null / undefined | Option<T> (Rust), NULL pointers (C) | Medium — every nullable must be audited |
| Reflection / RTTI | Limited or no equivalent (Rust: no reflection; C: none) | High — dynamic introspection lost |
| Annotations / attributes | Proc macros (Rust), pragmas (C), attributes (C++) | Medium — mechanism differs significantly |

## Approach

1. **Map the memory management spectrum** — Document the full GC → RC → Ownership → Manual continuum with conversion recipes at each step
2. **Define L1 transform rules first** — L1 (Data Flow / ownership) is the hardest and most asymmetric layer; all other transforms depend on ownership decisions
3. **Define L3 transform rules** — Map class hierarchies to trait/impl patterns, null to Option, with decision trees for ambiguous cases
4. **Define L2 transform rules** — Map exception handling to Result types, virtual dispatch to static dispatch, async models
5. **Build asymmetry-aware loss catalog** — The 4:1 asymmetry in GC→ownership means the Object→Systems direction needs significantly more documentation and decision points
6. **Validate the full chain** — Test the complete Typed-FP → B1 → Dynamic-FP → B2 → Object/Managed → B3 → Systems path to measure cumulative loss across all three bridges

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GC→ownership inference is fundamentally undecidable in the general case; no algorithm can always determine correct ownership | High | High | Provide heuristic-based ownership inference with explicit "needs human review" markers; document common patterns (single owner, shared immutable, shared mutable) |
| Cyclic object graphs cannot be directly represented in Rust's ownership model | High | Medium | Document cycle-breaking strategies (Rc+Weak, arena allocation, index-based); flag cycles for manual review |
| Full 3-bridge chain (Typed-FP→Systems) may have unacceptable cumulative information loss | Medium | High | Per-step preservation tracking at each bridge; shortcut Typed-FP↔Systems bridge added if chained quality falls below threshold |
