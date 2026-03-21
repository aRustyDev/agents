# Phase C3: Community -- Object/Managed

**ID:** C3
**Status:** pending
**Beads:** ai-x3e.17

## Objective

Define the Object/Managed community IR (L1-L3) and merge relevant convert-* skills covering Dynamic + Managed-OOP + Apple families: Python, TypeScript, JavaScript, Java, C#, Kotlin, Swift, Objective-C. This community has a coupled core at L2+L3 -- method dispatch depends on class hierarchy, and type definitions (interfaces, abstract classes, generics) dictate control flow through virtual calls, exceptions, and async patterns.

## Dependencies

- S0 (Shared Layers) -- L0 + L4 schemas must be finalized
- V0 (Validation Framework) -- round-trip and benchmark infrastructure must be available

## Success Criteria

- [ ] Object/Managed community IR schema defined for L1 (Data Flow), L2 (Control Flow), L3 (Type)
- [ ] L2+L3 coupling formally documented with joint conversion constraints
- [ ] JSON Schema files for all three community layers published
- [ ] Within-community conversion rules defined for all 28 Object/Managed language pairs
- [ ] Round-trip validation passes at ≥85% preservation for within-community pairs (global default; individual pair thresholds may be adjusted with documented justification)
- [ ] Class hierarchy and inheritance patterns preserved in IR with high fidelity
- [ ] Community skill created at `context/skills/meta-convert-community-object-managed-dev/`
- [ ] SKILL.md under 500 lines with progressive disclosure to reference docs

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Community skill | `context/skills/meta-convert-community-object-managed-dev/SKILL.md` | Merged Object/Managed conversion skill |
| Apple family reference | `context/skills/meta-convert-community-object-managed-dev/reference/apple-family.md` | Swift, Objective-C, ARC patterns |
| Dynamic languages reference | `context/skills/meta-convert-community-object-managed-dev/reference/dynamic-languages.md` | Python, TypeScript, JavaScript patterns |
| JVM managed reference | `context/skills/meta-convert-community-object-managed-dev/reference/jvm-managed.md` | Java, C#, Kotlin patterns |
| OOP patterns reference | `context/skills/meta-convert-community-object-managed-dev/reference/oop-patterns.md` | Inheritance, interfaces, generics mapping |
| Examples | `context/skills/meta-convert-community-object-managed-dev/examples/` | Representative conversion examples |
| L1 schema | `schemas/ir-community-object-managed-l1.json` | Data Flow layer JSON Schema |
| L2+L3 schema | `schemas/ir-community-object-managed-l2l3.json` | Coupled Control Flow + Type layer JSON Schema |
| Validation report | `analysis/phaseC3-validation-report.md` | Merge quality and round-trip results |

## Files

**Create:**
- `context/skills/meta-convert-community-object-managed-dev/SKILL.md`
- `context/skills/meta-convert-community-object-managed-dev/reference/apple-family.md`
- `context/skills/meta-convert-community-object-managed-dev/reference/dynamic-languages.md`
- `context/skills/meta-convert-community-object-managed-dev/reference/jvm-managed.md`
- `context/skills/meta-convert-community-object-managed-dev/reference/oop-patterns.md`
- `context/skills/meta-convert-community-object-managed-dev/examples/`
- `schemas/ir-community-object-managed-l1.json`
- `schemas/ir-community-object-managed-l2l3.json`
- `analysis/phaseC3-validation-report.md`

**Modify:**
- `index.md` -- Update C3 status to complete
- `schemas/ir-v1.json` -- Reference community-specific L1-L3 schemas

## Source Skills (2)

| Skill | Languages | Key Patterns |
|-------|-----------|--------------|
| convert-objc-swift | Objective-C, Swift | Manual retain/release vs ARC, message passing vs method calls, categories vs extensions, NSObject hierarchy vs protocols |
| convert-python-typescript | Python, TypeScript | Duck typing vs structural typing, decorators vs decorators, async/await mapping, None vs undefined/null |

**Note:** Many Object/Managed languages appear in cross-community convert-* skills rather than within-community ones. Skills like convert-python-rust, convert-python-golang, convert-java-rust, convert-typescript-rust, and convert-typescript-golang are cross-community (handled by bridges B2 and B3). Skills like convert-python-haskell, convert-python-scala, convert-python-clojure are also cross-community (handled by bridges B1 and B2). The within-community skill count is low (2) because most existing convert-* skills target systems or FP languages from Object/Managed sources. No existing skills exist for pairs like Java-Kotlin, Java-C#, Python-Java, TypeScript-Swift, etc.

## Layer Coupling

The Object/Managed community has a **coupled core at L2+L3**. L1 is independent, but Control Flow and Type must be converted jointly:

| Layer Pair | Coupling | Rationale |
|------------|----------|-----------|
| L1 + L2 | Independent | Mutable variables and assignments (L1) can be mapped without knowledge of dispatch mechanisms (L2) |
| L1 + L3 | Independent | Reference semantics and GC/ARC (L1) are orthogonal to class definitions (L3) -- memory management strategy does not constrain variable binding |
| **L2 + L3** | **Coupled** | Virtual method dispatch (L2) depends on class hierarchy and interface definitions (L3); exception handling (L2) uses type-based catch clauses (L3); async/await patterns (L2) interact with Promise/Future type definitions (L3); generics variance (L3) constrains method overriding behavior (L2) |

**Conversion implication:** L1 can be converted independently, but L2 and L3 must be converted as a joint sub-problem. For example, converting Objective-C message dispatch to Swift method calls requires simultaneously transforming both the dispatch mechanism (L2) and the protocol/class hierarchy (L3). The schema reflects this by providing a combined L2+L3 JSON Schema.

### Community-Specific Layer Definitions

**L1 Data Flow:**
- Mutable variables (var, let, final, const -- varying immutability guarantees)
- Assignments and reference semantics (reference types vs value types)
- Garbage collection (JVM GC, Python GC, JavaScript GC)
- Automatic Reference Counting (Swift, Objective-C ARC)
- Closures capturing mutable state

**L2 Control Flow (coupled with L3):**
- Method dispatch (virtual calls, dynamic dispatch, static dispatch)
- Exception handling (try/catch/finally, typed exceptions)
- Async/await (coroutines, Promises, Futures, event loops)
- Event loops and callback patterns (JavaScript, Python asyncio)
- Iterator/generator protocols (yield, async generators)
- Property accessors (getters/setters, computed properties)

**L3 Type (coupled with L2):**
- Classes (concrete, abstract, sealed, data classes)
- Interfaces and protocols (Java interfaces, Swift protocols, TypeScript interfaces, Python Protocols)
- Inheritance (single, multiple via mixins/traits, protocol conformance)
- Generics (type parameters, bounded types, variance -- covariant, contravariant, invariant)
- Null safety (Optional, nullable types, None, undefined)
- Enums (simple, associated values, sealed classes as enums)

## Approach

1. **Extract L1-L3 from shared IR** -- Fork community-specific layers from Phase 4's ir-v1.json, scoped to Object/Managed concepts
2. **Define L2+L3 joint conversion constraints** -- Document which L2 constructs require simultaneous L3 conversion (virtual dispatch, exception hierarchies, async type mapping)
3. **Merge source skills into SKILL.md** -- Extract shared OOP patterns from the 2 source skills; organize by sub-family (Apple, Dynamic, JVM)
4. **Build OOP patterns reference** -- Consolidate inheritance, interface, and generics mapping patterns into dedicated reference doc covering all 8 member languages
5. **Validate coupled conversion** -- Run round-trip tests converting L2+L3 jointly; verify that converting them independently produces incorrect dispatch or type errors
6. **Run V0 validation suite** -- Execute round-trip benchmarks and per-layer preservation tracking against V0 framework

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Only 2 source skills limits pattern diversity for community IR validation | High | Medium | Supplement with patterns from cross-community skills (bridges B2, B3) during validation; define Object/Managed IR from language profiles rather than skill extraction alone |
| Community spans too many sub-families (Dynamic + Managed-OOP + Apple) with divergent semantics | Medium | Medium | Use sub-family reference docs to capture divergent patterns; shared SKILL.md focuses on universal OOP concepts (classes, interfaces, inheritance, generics) |
| TypeScript's structural typing vs Java's nominal typing creates tension in L3 schema | Medium | Low | Support both typing disciplines in L3 schema with a `typing_discipline` annotation; conversion rules handle structural-to-nominal and vice versa |
