# Language Family Overview

Comparison matrices for cross-family analysis and conversion planning.

## Graduated Scale Reference

All matrices use a graduated scale:

| Symbol | Level | Description |
|--------|-------|-------------|
| ○ | none | Feature not available |
| ◔ | limited | Basic support, significant restrictions |
| ◑ | partial | Supported with notable gaps |
| ◕ | full | Complete support, standard patterns |
| ● | native | First-class, idiomatic support |

## Feature × Family Matrix

### Type System Features

| Feature | ML-FP | BEAM | LISP | Systems | Managed | Dynamic | Apple |
|---------|-------|------|------|---------|---------|---------|-------|
| Static Typing | ● | ○¹ | ○ | ● | ● | ○² | ◑³ |
| Type Inference | ● | ○ | ○ | ◑ | ◔ | ○ | ◔ |
| Generics | ●⁴ | ○ | ○ | ◕ | ◕ | ○ | ◕ |
| Higher-Kinded Types | ◕⁵ | ○ | ○ | ○ | ○ | ○ | ○ |
| Null Safety | ● | ○ | ○ | ◑⁶ | ◔⁷ | ○ | ◕⁸ |
| ADTs/Sum Types | ● | ◔ | ◔ | ●⁹ | ◔¹⁰ | ○ | ●¹¹ |
| Pattern Matching | ● | ● | ◑ | ●⁹ | ◔¹² | ○ | ●¹¹ |

**Notes:**

1. Gleam has static typing
2. TypeScript/typed Python add gradual typing
3. Swift is static, Obj-C is dynamic
4. Haskell/Scala have HKT
5. Not all ML-FP languages (e.g., Elm lacks HKT)
6. Rust has Option<T>, C/C++ have nullable pointers
7. Kotlin has null safety
8. Swift optionals
9. Rust enums are ADTs
10. Java 17+ sealed classes
11. Swift enums with associated values
12. Java 21+ pattern matching

### Memory & Safety Features

| Feature | ML-FP | BEAM | LISP | Systems | Managed | Dynamic | Apple |
|---------|-------|------|------|---------|---------|---------|-------|
| Memory Safety | ● | ● | ● | ◑¹ | ● | ● | ● |
| Immutability | ●² | ● | ◑³ | ○ | ○ | ○ | ◔⁴ |
| Ownership/Borrowing | ○ | ○ | ○ | ●⁵ | ○ | ○ | ○ |
| Automatic Memory | ● | ● | ● | ◔⁶ | ● | ● | ●⁷ |
| Value Types | ◕ | ● | ○ | ● | ◔⁸ | ○ | ●⁹ |

**Notes:**

1. Rust has memory safety, C/C++ do not
2. Pure: enforced; Hybrid: default
3. Clojure immutable, CL mutable
4. Swift value types (structs)
5. Rust only
6. Rust automatic via ownership; C/C++ manual
7. ARC (reference counting)
8. C# structs, Java primitives
9. Swift structs are value types

### Concurrency Features

| Feature | ML-FP | BEAM | LISP | Systems | Managed | Dynamic | Apple |
|---------|-------|------|------|---------|---------|---------|-------|
| Threads | ◕ | ○¹ | ◕ | ● | ● | ◑² | ● |
| Async/Await | ◑³ | ○ | ◔ | ●⁴ | ● | ●⁵ | ●⁶ |
| Actors | ◔⁷ | ● | ○ | ◔⁸ | ◔⁹ | ○ | ●¹⁰ |
| Channels/CSP | ◔ | ○ | ●¹¹ | ●¹² | ◔ | ○ | ○ |
| STM | ◕¹³ | ○ | ●¹⁴ | ○ | ○ | ○ | ○ |
| Green Threads | ●¹⁵ | ●¹⁶ | ○ | ◕¹⁷ | ◔¹⁸ | ◔¹⁹ | ○ |

**Notes:**

1. BEAM uses processes, not OS threads
2. Python GIL limits; JS single-threaded
3. Haskell async; varies by language
4. Rust async/await
5. JS Promise/async, Python asyncio
6. Swift 5.5+ async/await
7. Akka on Scala
8. Rust actix, etc.
9. Akka on JVM
10. Swift actors
11. Clojure core.async
12. Rust channels, Go channels
13. Haskell STM
14. Clojure STM
15. Haskell green threads
16. BEAM processes
17. Rust tokio, Go goroutines
18. Project Loom (Java 21+)
19. Python greenlet, JS no native

### Metaprogramming Features

| Feature | ML-FP | BEAM | LISP | Systems | Managed | Dynamic | Apple |
|---------|-------|------|------|---------|---------|---------|-------|
| Macros | ◔¹ | ●² | ● | ◑³ | ○ | ○ | ◔⁴ |
| Runtime Reflection | ◔ | ● | ● | ◔⁵ | ● | ● | ●⁶ |
| Compile-time Codegen | ◕⁷ | ◔ | ○ | ●⁸ | ◕⁹ | ○ | ◔¹⁰ |
| Homoiconicity | ○ | ○ | ● | ○ | ○ | ○ | ○ |
| Eval | ○ | ◕ | ● | ○ | ○ | ● | ○ |

**Notes:**

1. Template Haskell, Scala 3 macros
2. Elixir hygienic macros
3. C/C++ preprocessor, Rust procedural macros
4. Swift 5.9+ macros
5. C++ RTTI, Rust none
6. Obj-C runtime, Swift Mirror
7. Deriving, type-level programming
8. Rust derive macros
9. Annotation processors, source generators
10. Swift property wrappers

### Effect Handling

| Feature | ML-FP | BEAM | LISP | Systems | Managed | Dynamic | Apple |
|---------|-------|------|------|---------|---------|---------|-------|
| Exceptions | ◔¹ | ● | ● | ◑² | ● | ● | ●³ |
| Result Types | ● | ◔ | ○ | ●⁴ | ◔⁵ | ○ | ●⁶ |
| Monadic Effects | ● | ○ | ○ | ○ | ○ | ○ | ○ |
| Algebraic Effects | ◔⁷ | ○ | ○ | ○ | ○ | ○ | ○ |
| Checked Exceptions | ○ | ○ | ○ | ○ | ◔⁸ | ○ | ○ |

**Notes:**

1. Available but discouraged in pure FP
2. C++ exceptions, Rust no exceptions
3. Obj-C @try, Swift throws
4. Rust Result<T, E>
5. Java Optional, Kotlin Result
6. Swift Result type
7. Roc, Koka, experimental Haskell
8. Java only

## Conversion Difficulty Matrix

Difficulty converting FROM row TO column. Based on Phase 0 gap analysis (320 gaps).

### Overall Difficulty

| FROM ↓ TO → | ML-FP | BEAM | LISP | Systems | Managed | Dynamic | Apple |
|-------------|-------|------|------|---------|---------|---------|-------|
| **ML-FP** | ◑¹ | ◕ | ◕ | ◐² | ◕ | ● | ◕ |
| **BEAM** | ◑³ | ● | ◕ | ◐ | ◕ | ◕ | ◐ |
| **LISP** | ◑⁴ | ◕ | ● | ◐ | ◕ | ● | ◐ |
| **Systems** | ◐⁵ | ◐ | ◐ | ◑⁶ | ◕ | ◐ | ◕ |
| **Managed** | ◕ | ◕ | ◕ | ◑⁷ | ● | ◕ | ◕ |
| **Dynamic** | ◑⁸ | ◕ | ● | ◐⁹ | ◕ | ● | ◕ |
| **Apple** | ◕ | ◐ | ◐ | ◕ | ◕ | ◕ | ● |

**Scale:** ● Easy | ◕ Moderate | ◑ Challenging | ◐ Hard | ○ Very Hard

**Notes:**

1. ML-FP → ML-FP: 63 gaps (subtype differences: pure↔hybrid)
2. ML-FP → Systems: Lazy evaluation, HKT, no ownership
3. BEAM → ML-FP: 36 gaps (actor model translation)
4. LISP → ML-FP: 27 gaps (macro expansion, dynamic typing)
5. Systems → ML-FP: Manual memory → GC, imperative → functional
6. Systems → Systems: 23 gaps (ownership models differ)
7. Managed → Systems: GC → ownership
8. Dynamic → ML-FP: 39 gaps (type inference required)
9. Dynamic → Systems: 29 gaps (memory + typing)

### Specific Challenge Areas

| Conversion | Primary Challenges | Gap Count |
|------------|-------------------|-----------|
| Dynamic → ML-FP | Type inference, null handling, immutability | 39 |
| Dynamic → Systems | Memory management, strict typing, lifetimes | 29 |
| BEAM → ML-FP | Actor model → pure functions, process state | 36 |
| ML-FP → ML-FP | Pure ↔ hybrid, HKT availability, effect systems | 63 |
| LISP → ML-FP | Macro expansion, homoiconicity loss | 27 |
| Systems → Systems | Ownership (Rust) ↔ manual (C/C++) | 23 |

### Lossy Conversions

Information/guarantees lost when converting:

| FROM → TO | What's Lost |
|-----------|-------------|
| ML-FP → Dynamic | Type safety, compile-time guarantees |
| ML-FP → BEAM | Purity guarantees, HKT |
| Systems (Rust) → Systems (C) | Memory safety, ownership guarantees |
| BEAM → any | Actor isolation, fault tolerance model |
| LISP → any | Homoiconicity, macro system |

### Human Decision Points

Conversions requiring manual architectural decisions:

| Conversion | Decisions Required |
|------------|-------------------|
| Any → BEAM | Actor boundaries, supervision trees |
| Any → Systems (Rust) | Ownership design, lifetime annotations |
| Dynamic → Static | Type annotations, interface extraction |
| OOP → FP | Class hierarchy → ADTs/modules |
| Mutable → Immutable | State management strategy |

## Quick Reference Tables

### Best Source Languages (by target)

| Target Family | Best Sources | Reason |
|---------------|--------------|--------|
| ML-FP | LISP, Dynamic | Similar paradigm (LISP), straightforward inference (Dynamic) |
| BEAM | LISP, ML-FP | Actor-friendly, functional patterns |
| Systems | Managed-OOP, ML-FP | Structured typing helps |
| Dynamic | Any | Flexible target, accepts all patterns |
| Managed-OOP | Dynamic, ML-FP | Class-friendly, typed sources help |

### Best Target Languages (by source)

| Source Family | Best Targets | Reason |
|---------------|--------------|--------|
| Dynamic | Dynamic, LISP | Preserve flexibility |
| ML-FP | ML-FP, Managed | Preserve types |
| BEAM | BEAM, ML-FP | Preserve functional patterns |
| Systems | Systems, Managed | Preserve performance intent |
| LISP | Dynamic, ML-FP | Preserve expressiveness |

## Data Sources

- **Phase 0 Pattern Extraction**: 7,195 patterns from 49 skills
- **Gap Analysis**: 320 semantic gaps identified
- **Feature Dimensions**: `data/families/dimensions.yaml`
- **Expert Judgment**: Initial ratings, to be validated in Phase 3

## Revision History

| Date | Change |
|------|--------|
| 2026-02-04 | Initial matrices based on Phase 0 data |
| TBD | Post-Phase 3 semantic gap validation |
| TBD | Post-Phase 5 IR validation updates |
