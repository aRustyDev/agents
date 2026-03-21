# Phase C4: Community -- Systems

**ID:** C4
**Status:** pending
**Beads:** ai-x3e.18

## Objective

Define the Systems community IR (L1-L3) and merge relevant convert-* skills covering Rust, C, C++, Go, Zig. This community has a coupled core at L1+L3 -- ownership and lifetime decisions (L1) depend on type definitions (L3), and conversely, type representations (sized/unsized, generic monomorphization) are constrained by data flow semantics (L1). Go's garbage collector is handled as an annotated variant within the Systems IR rather than placing Go in a separate community.

## Dependencies

- S0 (Shared Layers) -- L0 + L4 schemas must be finalized
- V0 (Validation Framework) -- round-trip and benchmark infrastructure must be available

## Success Criteria

- [ ] Systems community IR schema defined for L1 (Data Flow), L2 (Control Flow), L3 (Type)
- [ ] L1+L3 coupling formally documented with joint conversion constraints
- [ ] JSON Schema files for all three community layers published
- [ ] Within-community conversion rules defined for all 10 Systems language pairs
- [ ] Round-trip validation passes at ≥85% preservation for within-community pairs (global default; individual pair thresholds may be adjusted with documented justification)
- [ ] Ownership, lifetime, and memory management patterns preserved in IR with high fidelity
- [ ] Community skill created at `context/skills/meta-convert-community-systems-dev/`
- [ ] SKILL.md under 500 lines with progressive disclosure to reference docs

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Community skill | `context/skills/meta-convert-community-systems-dev/SKILL.md` | Merged Systems conversion skill |
| Memory model reference | `context/skills/meta-convert-community-systems-dev/reference/memory-model.md` | Ownership, lifetimes, borrow checking, stack/heap, GC |
| C family reference | `context/skills/meta-convert-community-systems-dev/reference/c-family.md` | C, C++ specific patterns (manual memory, RAII, templates) |
| Rust patterns reference | `context/skills/meta-convert-community-systems-dev/reference/rust-patterns.md` | Ownership, traits, Result/Option, unsafe |
| Go patterns reference | `context/skills/meta-convert-community-systems-dev/reference/go-patterns.md` | Goroutines, channels, interfaces, GC annotation |
| Examples | `context/skills/meta-convert-community-systems-dev/examples/` | Representative conversion examples |
| L1+L3 schema | `schemas/ir-community-systems-l1l3.json` | Coupled Data Flow + Type layer JSON Schema |
| L2 schema | `schemas/ir-community-systems-l2.json` | Control Flow layer JSON Schema |
| Validation report | `analysis/phaseC4-validation-report.md` | Merge quality and round-trip results |

## Files

**Create:**
- `context/skills/meta-convert-community-systems-dev/SKILL.md`
- `context/skills/meta-convert-community-systems-dev/reference/memory-model.md`
- `context/skills/meta-convert-community-systems-dev/reference/c-family.md`
- `context/skills/meta-convert-community-systems-dev/reference/rust-patterns.md`
- `context/skills/meta-convert-community-systems-dev/reference/go-patterns.md`
- `context/skills/meta-convert-community-systems-dev/examples/`
- `schemas/ir-community-systems-l1l3.json`
- `schemas/ir-community-systems-l2.json`
- `analysis/phaseC4-validation-report.md`

**Modify:**
- `index.md` -- Update C4 status to complete
- `schemas/ir-v1.json` -- Reference community-specific L1-L3 schemas

## Source Skills (4)

| Skill | Languages | Key Patterns |
|-------|-----------|--------------|
| convert-c-cpp | C, C++ | C subset to C++ superset, malloc/free to RAII, function pointers to virtual methods, structs to classes |
| convert-c-rust | C, Rust | Manual memory to ownership, pointers to references/Box, undefined behavior to safe Rust, header files to modules |
| convert-cpp-rust | C++, Rust | RAII to ownership, templates to generics+traits, exceptions to Result, shared_ptr to Arc, virtual to trait objects |
| convert-golang-rust | Go, Rust | GC to ownership, goroutines to async/tokio, interfaces to traits, error values to Result, channels to mpsc |

**Note:** No Zig convert-* skills currently exist. Zig is included in the community definition for future extensibility but has no source skills to merge. Cross-community skills like convert-java-rust, convert-python-rust, convert-python-golang, convert-typescript-rust, and convert-typescript-golang involve Object/Managed sources and are handled by bridge B3, not this phase. Skills like convert-java-c and convert-java-cpp also cross community boundaries.

## Layer Coupling

The Systems community has a **coupled core at L1+L3**. L2 is independent, but Data Flow and Type must be converted jointly:

| Layer Pair | Coupling | Rationale |
|------------|----------|-----------|
| **L1 + L3** | **Coupled** | Ownership semantics (L1) depend on whether types are Copy/Clone/Move (L3); lifetime annotations (L1) are part of type signatures (L3); stack vs heap allocation (L1) depends on Sized trait bounds (L3); borrow checking (L1) uses type information to determine validity (L3) |
| L1 + L2 | Independent | Data flow and ownership (L1) can be determined without knowledge of control flow (L2) -- ownership transfer happens at binding sites, not at control flow boundaries |
| L2 + L3 | Independent | Unsafe blocks, FFI calls, and intrinsics (L2) operate uniformly regardless of the specific types involved (L3) -- an unsafe block works the same whether it manipulates a `*mut u8` or a `*mut MyStruct` |

**Conversion implication:** L2 can be converted independently, but L1 and L3 must be converted as a joint sub-problem. For example, converting C's `malloc`/`free` pattern to Rust requires simultaneously deciding both the ownership model (L1: `Box`, `Rc`, `Arc`, stack allocation) and the type representation (L3: sized type, trait object, generic parameter). The schema reflects this by providing a combined L1+L3 JSON Schema.

### Community-Specific Layer Definitions

**L1 Data Flow (coupled with L3):**
- Ownership (move semantics, copy semantics, clone)
- Lifetimes (named lifetimes, elision rules, static lifetime)
- Borrow checking (shared references, mutable references, reborrowing)
- Move semantics (Rust move, C++ std::move, Go value/pointer receivers)
- Stack vs heap allocation (Box, Vec, manual malloc/free, Go escape analysis)
- Memory management spectrum: manual (C) -- RAII (C++) -- ownership (Rust) -- GC (Go)

**L2 Control Flow:**
- Unsafe blocks (Rust unsafe, C raw operations, C++ reinterpret_cast)
- Inline and intrinsics (compiler intrinsics, inline assembly, SIMD)
- Raw pointer operations (dereferencing, arithmetic, casting)
- FFI boundaries (C ABI, extern blocks, cgo, bindgen)
- Error handling patterns (C error codes, C++ exceptions, Rust Result, Go error values)
- Concurrency primitives (pthreads, std::thread, goroutines, tokio tasks)

**L3 Type (coupled with L1):**
- Traits and interfaces (Rust traits, Go interfaces, C++ virtual classes, C function pointer tables)
- Sized and unsized types (Rust Sized trait, dynamically sized types, thin/fat pointers)
- Raw types (C primitive types, pointer types, void)
- Generic monomorphization (Rust/C++ compile-time specialization vs Go interface boxing)
- Zero-cost abstractions (trait dispatch, inline generics, no runtime overhead)
- Algebraic types (Rust enums with data, C tagged unions, C++ std::variant)

## Approach

1. **Extract L1-L3 from shared IR** -- Fork community-specific layers from Phase 4's ir-v1.json, scoped to Systems concepts
2. **Define L1+L3 joint conversion constraints** -- Document which L1 constructs require simultaneous L3 conversion (ownership depends on Copy/Clone/Move types; lifetimes are part of type signatures)
3. **Build memory model reference** -- Map the full memory management spectrum (manual -- RAII -- ownership -- GC) with conversion rules between each level
4. **Merge source skills into SKILL.md** -- Extract shared systems patterns from the 4 source skills; organize "to Rust" patterns prominently as 3 of 4 skills target Rust
5. **Annotate Go's GC within Systems IR** -- Define how Go's GC is represented as a memory management annotation rather than creating a separate community placement
6. **Run V0 validation suite** -- Execute round-trip benchmarks and per-layer preservation tracking against V0 framework; pay special attention to ownership/lifetime correctness

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Go's GC creates semantic distance from other Systems languages (C, C++, Rust) | Medium | Medium | Annotate Go's memory model as `gc_managed` variant in L1+L3 schema; conversion rules explicitly handle GC-to-ownership transitions; document rationale in ADR-010 |
| L1+L3 coupling makes the Systems IR the most complex community schema | High | Medium | Start with Rust ownership model as the canonical representation; map C/C++/Go onto it with annotations; keep L2 simple to compensate |
| Unsafe code patterns resist formal IR representation | Medium | Low | Mark unsafe regions with explicit boundaries in IR; preserve raw pointer operations verbatim; do not attempt to "safe-ify" during IR extraction |
