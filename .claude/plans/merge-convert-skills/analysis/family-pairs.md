# Family Pair Analysis

Comprehensive semantic gap analysis for all 72 directed family pairs (9 families x 8 targets).

**Generated:** 2026-02-04
**Task:** ai-p29.2
**Total Pairs:** 72 directed pairs
**Source Data:** gap-classification.md (320 gaps), family-taxonomy.md, language profiles

---

## Family Reference

| ID | Family | Languages | Key Characteristics |
|----|--------|-----------|---------------------|
| 1 | **ML-FP** | Scala, Haskell, F#, Elm, Roc, Gleam | HKT, ADTs, pattern matching, type inference |
| 2 | **BEAM** | Elixir, Erlang | Actor model, processes, fault tolerance |
| 3 | **LISP** | Clojure, Common Lisp, Scheme | Homoiconic, macros, code-as-data |
| 4 | **Systems** | Rust, C, C++, Go, Zig | Low-level, manual/ownership memory |
| 5 | **Dynamic** | Python, TypeScript, JavaScript, Ruby | Dynamic typing, rapid development |
| 6 | **Managed-OOP** | Java, Kotlin | Class-based OOP, GC, enterprise |
| 7 | **Apple** | Swift, Objective-C | ARC, protocol-oriented, Apple ecosystem |
| 8 | **Logic** | Prolog | Unification, backtracking, declarative |
| 9 | **Procedural** | COBOL, Fortran, Pascal, Ada | Structured, batch processing, legacy |

---

## Priority 0: High-Traffic Pairs

### ML-FP to Systems

**Difficulty:** 4 (Very Hard)
**Existing Skills:** haskell-rust (implied via patterns), scala-rust (none), elm-rust (none), fsharp-rust (none)
**Pattern Coverage:** 5,597 ML-FP patterns, 2,108 Systems patterns

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| Higher-kinded types | Rust/C/C++/Go lack HKT | Monomorphize, defunctionalize |
| Type classes (open) | No equivalent in Systems | Trait impl at definition site (Rust), templates (C++) |
| Lazy evaluation | Systems languages are strict | Explicit thunks, lazy crate (Rust) |
| GADTs | No dependent-style patterns | Simplify to regular ADTs |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Arbitrary precision integers | Fixed-width by default | Use num_bigint (Rust), GMP (C) |
| Immutability guarantees | Must enforce by convention | const, ownership patterns |
| Referential transparency | Can't prove purity | Documentation, code review |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| ADTs | enum + struct (Rust), tagged union (C) | Medium |
| Pattern matching | match (Rust), switch (C/Go) | Medium |
| Currying | Explicit closures | High |
| Monads | Result (Rust), manual chaining | High |
| Type inference | Explicit annotations | Low |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| GC to Ownership | Lifetime analysis | Yes (Rust) |
| GC to Manual | Explicit free | Yes (C/C++) |
| Lazy to Strict | Thunks, reordering | Partial |

#### Key Considerations
- Rust is the most natural target due to algebraic types and pattern matching
- C/C++ require more manual work for ADTs (tagged unions)
- Go lacks sum types; use interfaces with type assertions
- Memory management is the primary challenge
- Effect handling (IO monad) must become explicit

---

### Systems to ML-FP

**Difficulty:** 3 (Hard)
**Existing Skills:** c-rust (exists but rust is systems), cpp-rust
**Pattern Coverage:** 2,108 Systems patterns

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| Pointer arithmetic | No direct equivalent | Abstract to indices, iterators |
| Undefined behavior | ML-FP languages are safe | Must eliminate UB first |
| Manual memory free | GC handles this | Remove explicit deallocation |
| Inline assembly | No equivalent | FFI to native code |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Fine-grained memory control | GC manages memory | Accept abstraction |
| Cache-friendly layouts | Less control | Profile and optimize |
| Zero-copy patterns | May need copies | Use views where possible |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Structs | Records, case classes | Low |
| Enums (C) | ADTs | Low |
| Pointers | References, indices | Medium |
| Mutation | Immutable + state monad | High |
| Loops | Recursion, folds | Medium |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| Ownership (Rust) | Not needed with GC | No |
| Manual alloc | GC automatic | No |
| Threads | Green threads, actors | Partial |

#### Key Considerations
- Systems to ML-FP is generally easier than reverse
- Main challenge is imperative to functional style
- Mutable state becomes immutable with threading
- Loops become recursion or higher-order functions
- Rust translates more naturally due to pattern matching

---

### Dynamic to ML-FP

**Difficulty:** 3 (Hard)
**Existing Skills:** python-haskell, python-scala, python-fsharp, python-elm, python-roc, typescript-rust (target is Systems)
**Gap Count:** 39 (from taxonomy)
**Pattern Coverage:** 2,449 Dynamic patterns, 5,597 ML-FP patterns

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| Monkey patching | Types are closed | Use type classes, extension methods |
| Runtime type modification | Types fixed at compile time | Redesign with ADTs |
| Duck typing | Explicit interfaces required | Define protocols/traits |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Arbitrary precision (Python) | Fixed or explicit BigInt | Use Integer (Haskell), bigint (F#) |
| Dynamic dispatch flexibility | Static dispatch | Define all variants upfront |
| None/null semantics | Explicit Option/Maybe | Partial - analyze nullability |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Classes | ADTs + functions | Medium |
| Inheritance | Composition, type classes | High |
| Exceptions | Result/Either types | Medium |
| Mutable collections | Persistent data structures | Medium |
| Decorators | Higher-order functions | Low |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| Mutable state | State monad, STRef | Partial |
| GIL concurrency | True parallelism | Yes |
| Dynamic imports | Static modules | Yes |

#### Semantic Gaps (12 from classification)

| Source | Target | Gap | Mitigation |
|--------|--------|-----|------------|
| python | haskell | Forgetting About Laziness | Use seq, BangPatterns |
| python | clojure | Mutable State to Immutable | Use atoms or rebinding |
| python | rust | Integer Overflow | Use num_bigint::BigInt |
| python | typescript | None vs null/undefined | Choose convention |
| python | scala | Mutability Assumptions | Use immutable collections |
| python | elm | Fable.Python toolchain | Different ecosystem |
| python | haskell | Web frameworks | Django/Flask to Servant/Yesod |

#### Key Considerations
- Type inference required for source analysis
- Use type hints in Python/TypeScript to guide conversion
- null/None handling is critical (11 skills exist)
- Framework-specific patterns rarely transfer directly
- Error handling shift from exceptions to Result types

---

### ML-FP to Dynamic

**Difficulty:** 2 (Medium)
**Existing Skills:** None (major gap)
**Gap Count:** 11 (from taxonomy)

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| None | All ML-FP features can be simulated at runtime | N/A |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Type safety | Runtime type checks only | Add type hints, tests |
| Compile-time errors | Become runtime errors | Unit tests |
| Pattern exhaustiveness | No compiler check | Test coverage |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| ADTs | Classes with isinstance checks | Medium |
| Type classes | Duck typing, protocols | Medium |
| Pattern matching | if/elif chains, match (Python 3.10+) | Low |
| Immutability | Convention, frozen dataclasses | Low |
| Monads | Method chaining, comprehensions | Medium |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| Lazy evaluation | Generators | Partial |
| Pure functions | Discipline only | No |
| Strict types | Type hints optional | No |

#### Key Considerations
- Conversion is relatively straightforward
- Main loss is compile-time safety
- Consider runtime type checking libraries
- Pattern matching available in Python 3.10+, TypeScript
- Add comprehensive tests to replace type checks

---

### Dynamic to Systems

**Difficulty:** 4 (Very Hard)
**Existing Skills:** python-rust, python-golang, typescript-rust, typescript-golang
**Gap Count:** 29 (from taxonomy)

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| Monkey patching | Types closed at compile | Redesign |
| Runtime metaprogramming | No runtime reflection (C/Rust) | Code generation |
| Dynamic typing | Must be fully typed | Type inference/annotation |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Arbitrary precision | Fixed-width or external library | BigInt libraries |
| Reflection | Limited or none | Macros, codegen |
| REPL development | Compile cycle required | Hot reload tools |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Classes | structs + impl (Rust), structs (Go) | Medium |
| Dynamic dicts | HashMap with typed values | High |
| Exceptions | Result (Rust), error returns (Go) | Medium |
| Lists | Vec (Rust), slice (Go) | Low |
| Generators | Iterator (Rust), channels (Go) | Medium |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| GC to Ownership | Lifetime analysis | Yes (Rust) |
| None handling | Option (Rust), pointer (Go) | Partial |
| async/await | async (Rust), goroutines (Go) | Partial |

#### Key Considerations
- 4 skills exist for this direction
- Over-cloning is common anti-pattern (Rust)
- Error handling philosophy differs significantly
- Go's nil interface gotchas
- Memory safety requires careful attention in C/C++

---

### Systems to Dynamic

**Difficulty:** 2 (Medium)
**Existing Skills:** None (gap - Rust/C/C++/Go as sources have 0-1 skills)

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| None | Systems features implementable in dynamic | N/A |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Memory control | GC handles it | Accept abstraction |
| Performance tuning | Less control | Profile as needed |
| Zero-copy | May need copies | Use views |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Ownership (Rust) | Not needed | N/A |
| Pointers | References | Low |
| Manual memory | Automatic GC | N/A |
| Static typing | Optional type hints | Low |
| Enums | Classes/dicts | Low |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| Threads | Async or threads | Partial |
| Mutexes | threading module, locks | Low |

#### Key Considerations
- Generally easy conversion
- Lose performance characteristics
- Memory management becomes automatic
- FFI often preferred over full conversion

---

## Priority 1: Secondary High-Traffic Pairs

### BEAM to ML-FP

**Difficulty:** 3 (Hard)
**Existing Skills:** elixir-haskell, elixir-scala, elixir-fsharp, elixir-elm, elixir-roc, erlang-haskell, erlang-scala, erlang-fsharp, erlang-roc
**Gap Count:** 36 (from taxonomy)

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| Hot code reload | No equivalent in ML-FP | Design for restart |
| Process isolation | Different concurrency model | Actor libraries |
| Let-it-crash philosophy | Exceptions/Results don't crash | Explicit error boundaries |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Process mailbox | Must redesign messaging | Actor libraries |
| Supervisor trees | No built-in equivalent | Error handling redesign |
| Per-process GC | Global GC | Accept |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Tagged tuples | ADTs | Low |
| Modules | Modules/objects | Low |
| Protocols (Elixir) | Type classes | Medium |
| Behaviours | Type classes | Medium |
| Pattern matching | Pattern matching | Low |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| Actors to pure | State monad, STM | Yes |
| Process-based thinking | Pure functions | Yes |
| Distributed BEAM | External coordination | Yes |

#### Key Considerations
- 10 skills exist (100% coverage BEAM->ML-FP)
- Process/actor model is main challenge
- Pattern matching translates well
- OTP patterns need complete redesign
- Both use immutable data by default

---

### ML-FP to BEAM

**Difficulty:** 3 (Hard)
**Existing Skills:** elm-erlang (1 skill)
**Gap Count:** 10 (from taxonomy)

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| Type classes | No equivalent | Protocols, behaviours |
| HKT | Not supported | Monomorphize |
| GADTs | Not supported | Simplify types |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Static type safety | Dynamic + Dialyzer | Typespecs, Gleam |
| Compile-time guarantees | Runtime checks | Dialyzer, tests |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| ADTs | Tagged tuples, structs | Low |
| Modules | Modules | Low |
| Type inference | Typespecs (optional) | Low |
| Monads | {:ok, x}/{:error, e} | Medium |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| Lazy evaluation | Streams | Partial |
| Pure functions | Functions | No |
| Type system | Dynamic | Accept |

#### Key Considerations
- Only 1 skill exists (elm-erlang)
- Gleam provides typed BEAM if desired
- Lose type safety, gain actors
- Pattern matching maps well
- OTP provides rich concurrency abstractions

---

### Managed-OOP to Systems

**Difficulty:** 3 (Hard)
**Existing Skills:** java-rust, java-c, java-cpp
**Gap Count:** 13 (from taxonomy)

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| Type erasure (Java) | Must handle explicitly | Monomorphize |
| Runtime reflection | Limited (Rust) or manual (C) | Codegen |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| GC simplicity | Manual/ownership memory | Restructure |
| Checked exceptions | Must encode explicitly | Result types |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Classes | structs + impl (Rust) | Medium |
| Inheritance | Composition, traits | High |
| Interfaces | Traits | Medium |
| Generics | Monomorphized generics | Medium |
| Collections | std collections | Low |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| GC to Ownership | Lifetime analysis | Yes |
| Object Slicing | Trait objects, Box | Partial |
| Virtual dispatch | dyn Trait, vtables | Medium |

#### Key Considerations
- 3 skills exist (75% coverage)
- Inheritance hierarchies need flattening
- Null handling critical (NPE -> Option)
- JVM memory model differs from native
- Consider Kotlin for better null safety first

---

### Managed-OOP to ML-FP

**Difficulty:** 3 (Hard)
**Existing Skills:** None (java-scala implied on same JVM)

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| None | All OOP can be expressed functionally | N/A |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Inheritance chains | Must flatten | Composition |
| Mutable idioms | Immutable style | Restructure |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Classes | ADTs + functions | Medium |
| Inheritance | Type classes, composition | High |
| Interfaces | Type classes | Medium |
| Mutations | Immutable + State monad | High |
| for loops | map/filter/fold | Medium |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| Mutable state | STRef, StateT | Yes |
| Exceptions | Either/Result | Partial |

#### Key Considerations
- Natural on JVM (Java to Scala)
- Inheritance is main structural challenge
- Null handling maps to Option/Maybe
- Factory patterns become smart constructors
- Consider gradual migration via Kotlin

---

### LISP to ML-FP

**Difficulty:** 3 (Hard)
**Existing Skills:** clojure-haskell, clojure-scala, clojure-fsharp, clojure-elm, clojure-roc
**Gap Count:** 27 (from taxonomy)

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| Macros | No equivalent (expand first) | Inline macro expansions |
| Code-as-data | Not homoiconic | AST libraries |
| Reader macros | No syntax extension | Preprocess |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Dynamic typing | Static types required | Type inference |
| Runtime modification | Compile-time fixed | Accept |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Lists | Lists | Low |
| Maps | Maps/Records | Low |
| Protocols | Type classes | Medium |
| Multimethods | Pattern matching | Medium |
| defrecord | ADTs | Low |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| STM (Clojure) | STM (Haskell) or other | Partial |
| Atom state | IORef, STRef | Partial |
| core.async | Async libraries | Partial |

#### Semantic Gaps

| Source | Target | Gap | Mitigation |
|--------|--------|-----|------------|
| clojure | elm | Assuming Dynamic Typing | Define explicit types with Maybe |
| clojure | erlang | Atom Table Exhaustion | Avoid dynamic atom creation |
| clojure | haskell | Dynamic Type Assumptions | Use ADTs for heterogeneous data |

#### Key Considerations
- 5 skills exist (100% coverage LISP->ML-FP target subset)
- Macro expansion required before translation
- Both families favor immutability
- LISP to Haskell STM maps reasonably
- Dynamic typing is main challenge

---

### LISP to BEAM

**Difficulty:** 2 (Medium)
**Existing Skills:** clojure-elixir, clojure-erlang
**Gap Count:** 12 (from taxonomy)

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| Macros (different) | Elixir has own macros | Rewrite |
| Reader macros | Not in BEAM | Expand first |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| JVM interop (Clojure) | BEAM interop instead | Replace libraries |
| STM | Actors instead | Redesign concurrency |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Lists | Lists | Low |
| Maps | Maps | Low |
| Protocols | Protocols (Elixir) | Low |
| Namespaces | Modules | Low |
| defrecord | defstruct | Low |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| STM | Actors/GenServer | Yes |
| Agents | Elixir Agent | Low |
| Refs | GenServer state | Medium |

#### Key Considerations
- 2 skills exist (100% LISP->BEAM coverage)
- Both dynamically typed, both immutable
- Both have macros (different systems)
- Concurrency model shift (STM -> actors)
- ClojureScript to Erlang is two-step

---

## Priority 2: Apple and Additional ML-FP Pairs

### Apple to Systems

**Difficulty:** 3 (Hard)
**Existing Skills:** None

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| ARC | Ownership (Rust) or manual (C) | Restructure memory |
| Objective-C runtime | No equivalent | Static compilation |
| Swift protocols with extensions | Traits (Rust) | Partial match |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| ARC automatic memory | Must manage explicitly | Manual lifetime design |
| Cocoa/UIKit frameworks | No equivalent | Different frameworks |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Swift optionals | Option (Rust), pointers | Medium |
| Classes (value semantics) | structs | Medium |
| Enums with values | enums | Low |
| Protocols | Traits | Medium |
| Extensions | impl blocks (Rust) | Medium |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| ARC weak/unowned | Weak/Rc/Arc (Rust) | Partial |
| GCD | Threads, async | Partial |

#### Key Considerations
- Swift is relatively close to Rust
- ARC maps reasonably to Rc/Arc
- Protocol-oriented maps to trait-oriented
- Objective-C is more challenging (dynamic)

---

### Apple to ML-FP

**Difficulty:** 3 (Hard)
**Existing Skills:** None

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| ARC retain cycles | GC handles this | Not an issue |
| Obj-C message passing | Method calls | Static dispatch |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Framework integration | Different ecosystems | Replace frameworks |
| Platform-specific code | Cross-platform needed | Redesign |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Swift enums | ADTs | Low |
| Optionals | Maybe/Option | Low |
| Classes | ADTs + functions | Medium |
| Protocols | Type classes | Medium |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| Async/await | Async monads, IO | Partial |
| ARC | GC | No |

#### Key Considerations
- Swift's ADTs translate well to ML-FP
- Optional/Maybe mapping is natural
- Protocol-oriented aligns with type classes
- Main challenge is ecosystem/framework

---

### Apple to Apple (Obj-C to Swift)

**Difficulty:** 2 (Medium)
**Existing Skills:** objc-swift (1 skill)

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| None | Swift is designed as Obj-C successor | N/A |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Dynamic message passing | Mostly static in Swift | @objc, dynamic keyword |
| Categories flexibility | Extensions more limited | Accept |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Header/impl files | Single file | Low |
| Properties | Properties | Low |
| Protocols | Protocols | Low |
| Blocks | Closures | Low |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| Manual memory (pre-ARC) | ARC | No |
| Obj-C runtime features | Swift equivalents | Partial |

#### Semantic Gaps

| Source | Target | Gap | Mitigation |
|--------|--------|-----|------------|
| objc | swift | Force Unwrapping Optionals | Use guard let, optional chaining |

#### Key Considerations
- 1 skill exists (50% Apple->Apple coverage)
- Apple provides migration tools
- nullability annotations guide Optional usage
- @objc bridging available

---

### ML-FP to ML-FP (Intra-family)

**Difficulty:** 2-3 (Medium to Hard)
**Existing Skills:** haskell-roc, haskell-scala, fsharp-haskell, fsharp-scala, fsharp-roc, elm-haskell, elm-scala, elm-fsharp, elm-roc, elm-erlang, roc-scala
**Gap Count:** 63 (from taxonomy)

#### Impossible Gaps

| Concept | From | To | Mitigation |
|---------|------|----|----|
| Lazy evaluation | Haskell | Elm, Roc, F#, Scala | Explicit thunks |
| Type classes | Haskell, Scala | Elm | Module pattern |
| Implicits | Scala | Haskell | Type classes |
| Effect tracking | Haskell (IO) | Scala | Discipline |
| HKT | Haskell, Scala | Elm, Roc | Monomorphize |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Laziness benefits | Space/time tradeoffs | Manual thunks |
| Full HKT | Limited abstraction | Concrete types |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| ADTs | ADTs | Low |
| Pattern matching | Pattern matching | Low |
| Modules | Modules/objects | Low |
| Type classes | Interfaces, implicits, type classes | Medium |
| Records | Records/case classes | Low |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| Haskell lazy | Strict evaluation | Partial |
| Haskell IO | Effect systems vary | Partial |

#### Semantic Gaps

| Source | Target | Gap | Mitigation |
|--------|--------|-----|------------|
| haskell | roc | Lazy vs Strict - Infinite Lists | Use finite, Stream |
| haskell | scala | Assuming Lazy Evaluation | Be explicit |
| fsharp | haskell | Confusing Either Direction | Right is success |
| elm | haskell | Assuming Elm's Simplicity Limits | Use full Haskell power |

#### Key Considerations
- 10+ skills exist within ML-FP
- Highest internal coverage
- Lazy vs strict is main runtime difference
- Type class encoding varies
- Pure vs hybrid (effect handling)

---

## Priority 3: Logic and Procedural Pairs

### Logic to Others

**Difficulty:** 5 (Extremely Hard)
**Existing Skills:** None

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| Unification | No direct equivalent | Pattern matching + equality |
| Backtracking | No implicit search | Explicit search/generators |
| Logic variables | No unbound variables | State threading |
| Cut (!) | Control flow differs | Explicit conditionals |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Declarative search | Must be explicit | Search libraries |
| Pattern matching++ | Simplified matching | Multiple patterns |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| Facts | Data structures | Low |
| Rules | Functions | High |
| Queries | Function calls | High |
| DCGs | Parser combinators | High |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| SLD resolution | Explicit algorithm | Yes |
| Backtracking search | Generators, continuations | Yes |

#### Key Considerations
- **No existing skills** - major paradigm gap
- Complete redesign typically required
- Consider embedding Prolog (SWI-Prolog FFI)
- minikanren libraries exist for some languages
- Best suited for specific algorithm extraction

### Logic to ML-FP

**Difficulty:** 4 (Very Hard)

- Haskell: LogicT monad for backtracking
- Pattern matching helps but not unification
- Consider embedding (SWI-Prolog, Kanren)

### Logic to Dynamic

**Difficulty:** 4 (Very Hard)

- Python: pyDatalog, kanren library
- More flexible but still paradigm shift
- Generators can simulate backtracking

### Logic to Systems

**Difficulty:** 5 (Extremely Hard)

- No good embedding options
- Must extract specific algorithms
- Consider keeping Prolog for logic portions

---

### Procedural to Others

**Difficulty:** 3-4 (Hard to Very Hard)
**Existing Skills:** None

#### Impossible Gaps

| Concept | Reason | Mitigation |
|---------|--------|------------|
| None fundamental | Style differences mainly | N/A |

#### Lossy Gaps

| Concept | Loss | Automation |
|---------|------|------------|
| Fixed-point decimal (COBOL) | IEEE floats by default | Decimal libraries |
| Array column-major (Fortran) | Row-major (C style) | Transpose awareness |

#### Structural Gaps

| Concept | Translation | Complexity |
|---------|-------------|------------|
| PERFORM loops | for/while | Low |
| GO TO | Structured control | Medium |
| COPYBOOKs | Imports/includes | Low |
| DIVISIONS | Modules/files | Low |
| Fixed format | Free format | Low |

#### Runtime Gaps

| Concept | Translation | Requires Redesign |
|---------|-------------|-------------------|
| Batch processing | Event-driven or batch | Partial |
| Record I/O | Stream I/O | Medium |

#### Key Considerations
- **No existing skills** - legacy modernization gap
- COBOL: 220B+ lines in production
- Main challenges are ecosystem and decimal precision
- Consider automated modernization tools
- Often better to wrap than rewrite

### Procedural to Managed-OOP

**Difficulty:** 3 (Hard)

- Natural modernization path (COBOL to Java)
- IBM provides tools
- Maintain decimal precision

### Procedural to Dynamic

**Difficulty:** 3 (Hard)

- Python Decimal for COBOL precision
- Easier syntax translation
- Good for prototyping/validation

### Procedural to ML-FP

**Difficulty:** 4 (Very Hard)

- Imperative to functional shift
- Mutation to immutability
- Rarely the best choice for COBOL

---

## Complete Family Pair Reference

### BEAM to Others

| Target | Difficulty | Skills | Key Challenges |
|--------|------------|--------|----------------|
| ML-FP | 3 | 10 | Actor model, process state |
| LISP | 2 | 0 | Similar FP style, macros differ |
| Systems | 4 | 0 | Actor to threads, GC to ownership |
| Dynamic | 2 | 0 | Both dynamic, simpler translation |
| Managed-OOP | 3 | 0 | Actor to objects |
| Apple | 3 | 0 | Actor to GCD/async |
| Logic | 5 | 0 | Paradigm mismatch |
| Procedural | 4 | 0 | FP to imperative |

### LISP to Others

| Target | Difficulty | Skills | Key Challenges |
|--------|------------|--------|----------------|
| ML-FP | 3 | 5 | Macros, dynamic typing |
| BEAM | 2 | 2 | STM to actors, similar FP |
| Systems | 4 | 0 | Dynamic to static, macros |
| Dynamic | 2 | 1 | Both dynamic, macros |
| Managed-OOP | 3 | 0 | FP to OOP |
| Apple | 3 | 0 | Dynamic to static |
| Logic | 4 | 0 | Different paradigms |
| Procedural | 4 | 0 | FP to imperative |

### Systems to Others

| Target | Difficulty | Skills | Key Challenges |
|--------|------------|--------|----------------|
| ML-FP | 3 | 0 | Mutation to immutability |
| BEAM | 4 | 0 | Threads to actors |
| LISP | 3 | 0 | Static to dynamic |
| Dynamic | 2 | 0 | Lose control, gain flexibility |
| Managed-OOP | 2 | 0 | Memory model simplification |
| Apple | 3 | 0 | Memory models differ |
| Logic | 5 | 0 | Paradigm mismatch |
| Procedural | 2 | 0 | Similar imperative style |

### Dynamic to Others

| Target | Difficulty | Skills | Key Challenges |
|--------|------------|--------|----------------|
| ML-FP | 3 | 10 | Type inference, immutability |
| BEAM | 3 | 0 | Learn actor model |
| LISP | 2 | 0 | Both dynamic, learn macros |
| Systems | 4 | 4 | Memory, types, performance |
| Managed-OOP | 2 | 0 | Add types, structure |
| Apple | 3 | 0 | Types, ARC |
| Logic | 4 | 0 | Paradigm shift |
| Procedural | 2 | 0 | Style simplification |

### Managed-OOP to Others

| Target | Difficulty | Skills | Key Challenges |
|--------|------------|--------|----------------|
| ML-FP | 3 | 0 | Inheritance to composition |
| BEAM | 3 | 0 | Objects to actors |
| LISP | 3 | 0 | OOP to FP, macros |
| Systems | 3 | 3 | GC to ownership |
| Dynamic | 2 | 0 | Remove types |
| Apple | 2 | 0 | Similar OOP style |
| Logic | 5 | 0 | Paradigm mismatch |
| Procedural | 2 | 0 | OOP to procedural |

### Apple to Others

| Target | Difficulty | Skills | Key Challenges |
|--------|------------|--------|----------------|
| ML-FP | 3 | 0 | ARC, protocols |
| BEAM | 4 | 0 | ARC to actors |
| LISP | 3 | 0 | Static to dynamic |
| Systems | 3 | 0 | ARC to ownership/manual |
| Dynamic | 2 | 0 | ARC to GC |
| Managed-OOP | 2 | 0 | ARC to GC, similar OOP |
| Logic | 5 | 0 | Paradigm mismatch |
| Procedural | 3 | 0 | OOP to procedural |

### Logic to Others

| Target | Difficulty | Skills | Key Challenges |
|--------|------------|--------|----------------|
| ML-FP | 4 | 0 | Backtracking, unification |
| BEAM | 4 | 0 | Backtracking to actors |
| LISP | 3 | 0 | Both declarative, macros help |
| Systems | 5 | 0 | Paradigm mismatch |
| Dynamic | 4 | 0 | Backtracking to iteration |
| Managed-OOP | 5 | 0 | Paradigm mismatch |
| Apple | 5 | 0 | Paradigm mismatch |
| Procedural | 4 | 0 | Declarative to imperative |

### Procedural to Others

| Target | Difficulty | Skills | Key Challenges |
|--------|------------|--------|----------------|
| ML-FP | 4 | 0 | Imperative to FP |
| BEAM | 4 | 0 | Imperative to actors |
| LISP | 3 | 0 | Imperative to FP |
| Systems | 2 | 0 | Similar style, modern syntax |
| Dynamic | 3 | 0 | Modernization |
| Managed-OOP | 3 | 0 | Natural modernization |
| Apple | 3 | 0 | Modernization with ARC |
| Logic | 5 | 0 | Paradigm mismatch |

---

## Summary Tables

### Difficulty Matrix (9x9)

Scale: 1 (Trivial) - 5 (Extremely Hard)

|  | ML-FP | BEAM | LISP | Systems | Dynamic | Managed | Apple | Logic | Procedural |
|--|-------|------|------|---------|---------|---------|-------|-------|------------|
| **ML-FP** | 2 | 3 | 2 | 4 | 2 | 3 | 3 | 4 | 4 |
| **BEAM** | 3 | 2 | 2 | 4 | 2 | 3 | 3 | 5 | 4 |
| **LISP** | 3 | 2 | 2 | 4 | 2 | 3 | 3 | 4 | 4 |
| **Systems** | 3 | 4 | 3 | 2 | 2 | 2 | 3 | 5 | 2 |
| **Dynamic** | 3 | 3 | 2 | 4 | 2 | 2 | 3 | 4 | 2 |
| **Managed** | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 5 | 2 |
| **Apple** | 3 | 4 | 3 | 3 | 2 | 2 | 2 | 5 | 3 |
| **Logic** | 4 | 4 | 3 | 5 | 4 | 5 | 5 | 2 | 4 |
| **Procedural** | 4 | 4 | 3 | 2 | 3 | 3 | 3 | 5 | 2 |

### Gap Count by Pair (Estimated)

Based on gap-classification.md (320 total gaps) and taxonomy patterns:

| Direction | Estimated Gaps | Notes |
|-----------|---------------|-------|
| ML-FP <-> ML-FP | 63 | Highest due to skill coverage |
| Dynamic -> ML-FP | 39 | Type inference challenges |
| BEAM -> ML-FP | 36 | Actor model translation |
| Dynamic -> Systems | 29 | Memory + types |
| LISP -> ML-FP | 27 | Macros + types |
| Systems <-> Systems | 23 | Memory model differences |
| Managed -> Systems | 13 | GC to ownership |
| LISP -> BEAM | 12 | Concurrency model |
| ML-FP -> Dynamic | 11 | Type erasure |
| ML-FP -> BEAM | 10 | Pure to actors |
| Others | < 10 | Lower coverage |

### Coverage Gaps (Pairs with No Skills)

Total pairs: 72
Pairs with skills: ~25
**Coverage: 35%**

**Critical gaps (high-traffic, no skills):**

| Pair | Priority | Rationale |
|------|----------|-----------|
| Systems -> Dynamic | P0 | Rust/C/Go to Python/TS needed |
| ML-FP -> Dynamic | P0 | Haskell/Scala to Python needed |
| Systems -> ML-FP | P1 | Rust to Haskell/Scala |
| Managed-OOP -> ML-FP | P1 | Java to Scala/Haskell |
| BEAM -> Systems | P1 | Elixir to Rust |
| Apple -> * | P2 | Swift as source |
| Logic -> * | P3 | Prolog has no skills |
| Procedural -> * | P3 | COBOL/Fortran have no skills |

### Skill Development Priorities

**Immediate (based on traffic and gap analysis):**

1. `scala-python` - Reverse of highest-use skill
2. `rust-python` - Systems to Dynamic
3. `haskell-python` - ML-FP to Dynamic
4. `java-scala` - Same-JVM modernization

**Short-term:**

5. `rust-typescript` - Systems to web
6. `elixir-rust` - BEAM to Systems
7. `swift-rust` - Apple to Systems
8. `scala-typescript` - JVM to web

**Medium-term:**

9. Logic family skills (Prolog to Python/Haskell)
10. Procedural modernization (COBOL to Java/Python)

---

## Appendix: Semantic Gap Categories

From gap-classification.md:

| Category | Count | % | Description |
|----------|-------|---|-------------|
| **lossy** | 108 | 33.8% | Numeric precision, arbitrary precision |
| **structural** | 176 | 55.0% | Code reorganization, skill boundaries |
| **runtime** | 22 | 6.9% | Memory model, evaluation strategy |
| **semantic** | 12 | 3.8% | Subtle meaning changes |
| **idiomatic** | 2 | 0.6% | Style conventions |
| **impossible** | 0 | 0.0% | (Potential: dependent types, linear types, continuations) |

---

*Generated for task ai-p29.2*
