# Gap Severity Matrix

Evidence-backed 9x9 matrix of conversion difficulty between all language families.

**Generated:** 2026-02-04
**Task:** ai-p29.3
**Data Sources:** family-pairs.md, gap-patterns.md, gap-classification.md, coverage-gaps.md

---

## 1. The Definitive 9x9 Matrix

### 1.1 ASCII Visualization

```
FROM / TO        | ML-FP | BEAM | LISP | Sys  | Dyn  | Mgd  | Apple| Logic| Proc |
-----------------|-------|------|------|------|------|------|------|------|------|
ML-FP            |   2   |  3   |  2   |  4   |  2   |  3   |  3   |  4   |  4   |
BEAM             |   3   |  2   |  2   |  4   |  2   |  3   |  3   |  5   |  4   |
LISP             |   3   |  2   |  2   |  4   |  2   |  3   |  3   |  4   |  4   |
Systems          |   3   |  4   |  3   |  2   |  2   |  2   |  3   |  5   |  2   |
Dynamic          |   3   |  3   |  2   |  4   |  2   |  2   |  3   |  4   |  2   |
Managed-OOP      |   3   |  3   |  3   |  3   |  2   |  2   |  2   |  5   |  2   |
Apple            |   3   |  4   |  3   |  3   |  2   |  2   |  2   |  5   |  3   |
Logic            |   4   |  4   |  3   |  5   |  4   |  5   |  5   |  2   |  4   |
Procedural       |   4   |  4   |  3   |  2   |  3   |  3   |  3   |  5   |  2   |
```

### 1.2 Table Format

| FROM / TO | ML-FP | BEAM | LISP | Systems | Dynamic | Managed-OOP | Apple | Logic | Procedural |
|-----------|-------|------|------|---------|---------|-------------|-------|-------|------------|
| **ML-FP** | 2 | 3 | 2 | 4 | 2 | 3 | 3 | 4 | 4 |
| **BEAM** | 3 | 2 | 2 | 4 | 2 | 3 | 3 | 5 | 4 |
| **LISP** | 3 | 2 | 2 | 4 | 2 | 3 | 3 | 4 | 4 |
| **Systems** | 3 | 4 | 3 | 2 | 2 | 2 | 3 | 5 | 2 |
| **Dynamic** | 3 | 3 | 2 | 4 | 2 | 2 | 3 | 4 | 2 |
| **Managed-OOP** | 3 | 3 | 3 | 3 | 2 | 2 | 2 | 5 | 2 |
| **Apple** | 3 | 4 | 3 | 3 | 2 | 2 | 2 | 5 | 3 |
| **Logic** | 4 | 4 | 3 | 5 | 4 | 5 | 5 | 2 | 4 |
| **Procedural** | 4 | 4 | 3 | 2 | 3 | 3 | 3 | 5 | 2 |

### 1.3 Heatmap (ASCII)

Symbols: ` ` (1 Easy), `+` (2 Moderate), `#` (3 Hard), `@` (4 Very Hard), `X` (5 Extreme)

```
            ML-FP  BEAM  LISP  Sys   Dyn   Mgd   Apple Logic Proc
           +------+-----+-----+-----+-----+-----+-----+-----+-----+
ML-FP      |  +   |  #  |  +  |  @  |  +  |  #  |  #  |  @  |  @  |
           +------+-----+-----+-----+-----+-----+-----+-----+-----+
BEAM       |  #   |  +  |  +  |  @  |  +  |  #  |  #  |  X  |  @  |
           +------+-----+-----+-----+-----+-----+-----+-----+-----+
LISP       |  #   |  +  |  +  |  @  |  +  |  #  |  #  |  @  |  @  |
           +------+-----+-----+-----+-----+-----+-----+-----+-----+
Systems    |  #   |  @  |  #  |  +  |  +  |  +  |  #  |  X  |  +  |
           +------+-----+-----+-----+-----+-----+-----+-----+-----+
Dynamic    |  #   |  #  |  +  |  @  |  +  |  +  |  #  |  @  |  +  |
           +------+-----+-----+-----+-----+-----+-----+-----+-----+
Managed    |  #   |  #  |  #  |  #  |  +  |  +  |  +  |  X  |  +  |
           +------+-----+-----+-----+-----+-----+-----+-----+-----+
Apple      |  #   |  @  |  #  |  #  |  +  |  +  |  +  |  X  |  #  |
           +------+-----+-----+-----+-----+-----+-----+-----+-----+
Logic      |  @   |  @  |  #  |  X  |  @  |  X  |  X  |  +  |  @  |
           +------+-----+-----+-----+-----+-----+-----+-----+-----+
Procedural |  @   |  @  |  #  |  +  |  #  |  #  |  #  |  X  |  +  |
           +------+-----+-----+-----+-----+-----+-----+-----+-----+
```

---

## 2. Difficulty Scale Definition

| Score | Label | Criteria | Gap Profile |
|-------|-------|----------|-------------|
| 1 | Easy | Trivial syntax differences | 0 impossible, 0 runtime, <5 structural |
| 2 | Moderate | Mostly idiomatic changes | 0 impossible, 0-1 runtime, 5-15 structural |
| 3 | Hard | Significant structural changes | 0-1 impossible, 1-3 runtime, 15-25 structural |
| 4 | Very Hard | Major paradigm differences | 1-3 impossible, 3-5 runtime, 25+ structural |
| 5 | Extreme | Fundamental paradigm mismatch | 3+ impossible, 5+ runtime, requires complete rethinking |

### Automation Levels by Score

| Score | Typical Automation | Human Intervention |
|-------|-------------------|-------------------|
| 1 | 95%+ | Minimal review |
| 2 | 70-90% | Light review, some decisions |
| 3 | 40-70% | Significant review, architecture decisions |
| 4 | 10-40% | Heavy refactoring, paradigm shifts |
| 5 | <10% | Complete redesign required |

---

## 3. Evidence for Each Cell

### 3.1 ML-FP Family Conversions

#### ML-FP to ML-FP: 2 (Moderate)

**Languages:** Scala, Haskell, F#, Elm, Roc, Gleam

**Gap Counts:**
- Impossible: 0 (all features representable)
- Lossy: 3-5 (lazy vs strict, HKT variations)
- Structural: 8-12 (type class encodings, module systems)
- Runtime: 1-2 (lazy vs strict evaluation)

**Key Blockers:**
1. Lazy vs strict evaluation (Haskell vs Roc/Elm)
2. Type class encoding differences (Haskell vs Elm/Roc)
3. Effect system variations (IO monad vs explicit effects)

**Existing Skills:** 10+ (haskell-roc, haskell-scala, fsharp-haskell, fsharp-scala, fsharp-roc, elm-haskell, elm-scala, elm-fsharp, elm-roc, roc-scala)

**Semantic Gaps (from classification):**
- haskell-roc: Lazy vs Strict - Infinite Lists
- haskell-scala: Assuming Lazy Evaluation
- fsharp-haskell: Confusing Either Direction
- elm-haskell: Assuming Elm's Simplicity Limits

---

#### ML-FP to BEAM: 3 (Hard)

**Languages:** Scala, Haskell, F#, Elm, Roc, Gleam -> Elixir, Erlang

**Gap Counts:**
- Impossible: 2-3 (HKT, GADTs, type classes)
- Lossy: 4-6 (static type guarantees)
- Structural: 10-15 (modules, protocols, behaviours)
- Runtime: 2-3 (pure to actors)

**Key Blockers:**
1. Loss of compile-time type safety (Dialyzer is optional)
2. Type classes to protocols/behaviours
3. Pure functions to process-based state

**Existing Skills:** 1 (elm-erlang)

**Pattern References:**
- TS-003: Higher-Kinded Types to No HKT
- TS-010: Type Classes to Interface Dispatch
- CC-002: Threads to Actors

---

#### ML-FP to LISP: 2 (Moderate)

**Languages:** Scala, Haskell, F#, Elm, Roc, Gleam -> Clojure, Common Lisp, Scheme

**Gap Counts:**
- Impossible: 0 (LISP is highly flexible)
- Lossy: 4-6 (static types become runtime)
- Structural: 8-12 (ADTs to maps/records, type classes to protocols)
- Runtime: 0-1 (both mostly functional)

**Key Blockers:**
1. Type safety becomes runtime checks
2. Compile-time errors become runtime errors
3. ADTs to map-based representations

**Existing Skills:** 0 (gap identified)

**Pattern References:**
- TS-001: Dynamic to Static Typing (reverse)
- EF-004: Monadic Effects to Direct Style

---

#### ML-FP to Systems: 4 (Very Hard)

**Languages:** Scala, Haskell, F#, Elm, Roc, Gleam -> Rust, C, C++, Go, Zig

**Gap Counts:**
- Impossible: 2-4 (HKT, type classes, lazy evaluation, GADTs)
- Lossy: 8-10 (type inference, purity, arbitrary precision)
- Structural: 12-18 (ADTs, pattern matching, currying, monads)
- Runtime: 5-7 (GC to ownership, lazy to strict)

**Key Blockers:**
1. Memory model transition (GC to ownership/manual)
2. Type system downgrade (HKT to monomorphized)
3. Effect system change (pure/IO to imperative)
4. Lazy to strict evaluation

**Existing Skills:** 0 (major gap - no ML-FP to Systems skills)

**Pattern References:**
- MM-002: GC to Ownership/Borrowing (severity: high)
- TS-003: Higher-Kinded Types to No HKT (severity: high)
- EF-009: Lazy to Strict Evaluation (severity: high)
- TS-010: Type Classes to Interface Dispatch (severity: high)

---

#### ML-FP to Dynamic: 2 (Moderate)

**Languages:** Scala, Haskell, F#, Elm, Roc, Gleam -> Python, TypeScript, JavaScript, Ruby

**Gap Counts:**
- Impossible: 0 (all features can be simulated)
- Lossy: 5-7 (type safety, exhaustiveness)
- Structural: 8-12 (ADTs to classes, type classes to duck typing)
- Runtime: 1-2 (lazy to generators)

**Key Blockers:**
1. Loss of compile-time type safety
2. Pattern exhaustiveness becomes runtime error
3. Immutability by convention only

**Existing Skills:** 0 (major gap identified)

**Pattern References:**
- EF-004: Monadic Effects to Direct Style
- TS-001: Dynamic to Static Typing (reverse)
- MM-004: Mutable Default to Immutable Default (reverse)

---

#### ML-FP to Managed-OOP: 3 (Hard)

**Languages:** Scala, Haskell, F#, Elm, Roc, Gleam -> Java, Kotlin

**Gap Counts:**
- Impossible: 1-2 (HKT limited, type classes complex)
- Lossy: 3-5 (type inference, implicits)
- Structural: 15-20 (ADTs to class hierarchies, FP to OOP)
- Runtime: 1 (lazy to strict)

**Key Blockers:**
1. ADTs to visitor pattern or sealed classes
2. Type classes to interface hierarchies
3. Functional composition to method chaining

**Existing Skills:** 0 (Scala-Java interop exists but different direction)

**Pattern References:**
- TS-010: Type Classes to Interface Dispatch
- EF-004: Monadic Effects to Direct Style

---

#### ML-FP to Apple: 3 (Hard)

**Languages:** Scala, Haskell, F#, Elm, Roc, Gleam -> Swift, Objective-C

**Gap Counts:**
- Impossible: 1-2 (HKT, type classes)
- Lossy: 3-5 (type inference depth)
- Structural: 12-16 (ADTs to enums, protocols)
- Runtime: 2-3 (GC to ARC)

**Key Blockers:**
1. Type classes to protocol-oriented programming
2. GC to ARC memory model
3. Pure to protocol extensions with state

**Existing Skills:** 0 (gap identified)

---

#### ML-FP to Logic: 4 (Very Hard)

**Languages:** Scala, Haskell, F#, Elm, Roc, Gleam -> Prolog

**Gap Counts:**
- Impossible: 3-4 (execution model completely different)
- Lossy: 5-7 (type system, guarantees)
- Structural: 15-20 (functions to rules, data to facts)
- Runtime: 5+ (forward evaluation to backtracking)

**Key Blockers:**
1. Forward computation to backward search
2. Functions to rules with unification
3. Type safety to untyped logic

**Existing Skills:** 0 (no skills exist)

---

#### ML-FP to Procedural: 4 (Very Hard)

**Languages:** Scala, Haskell, F#, Elm, Roc, Gleam -> COBOL, Fortran, Pascal, Ada

**Gap Counts:**
- Impossible: 2-3 (HKT, type classes, ADTs)
- Lossy: 6-8 (type inference, precision guarantees)
- Structural: 18-25 (FP to imperative)
- Runtime: 2-3 (GC to manual, lazy to strict)

**Key Blockers:**
1. Functional to imperative paradigm shift
2. Recursion to iteration
3. Immutability to mutation
4. Modern to legacy ecosystem

**Existing Skills:** 0 (no skills exist)

---

### 3.2 BEAM Family Conversions

#### BEAM to ML-FP: 3 (Hard)

**Languages:** Elixir, Erlang -> Scala, Haskell, F#, Elm, Roc, Gleam

**Gap Counts:**
- Impossible: 3 (hot code reload, process isolation, let-it-crash)
- Lossy: 4-6 (process mailbox, supervisor trees, per-process GC)
- Structural: 8-12 (tagged tuples to ADTs, protocols to type classes)
- Runtime: 3-4 (actors to pure, OTP patterns)

**Key Blockers:**
1. Actor/process model to pure functions
2. OTP supervision to error handling
3. Hot code reload has no equivalent

**Existing Skills:** 10 (elixir-haskell, elixir-scala, elixir-fsharp, elixir-elm, elixir-roc, erlang-haskell, erlang-scala, erlang-fsharp, erlang-roc, elm-erlang reverse)

**Semantic Gaps:**
- Process-Based Thinking in Pure Code
- Expecting Runtime Dynamism

---

#### BEAM to BEAM: 2 (Moderate)

**Languages:** Elixir, Erlang (internal)

**Gap Counts:**
- Impossible: 0
- Lossy: 1-2 (syntax sugars)
- Structural: 5-8 (macros, syntax differences)
- Runtime: 0 (same VM)

**Key Blockers:**
1. Elixir macros to Erlang
2. Syntax differences (pipes, pattern matching sugar)
3. Framework-specific code (Phoenix)

**Existing Skills:** 1 (elixir-erlang)

---

#### BEAM to LISP: 2 (Moderate)

**Languages:** Elixir, Erlang -> Clojure, Common Lisp, Scheme

**Gap Counts:**
- Impossible: 1-2 (OTP patterns, hot reload)
- Lossy: 2-3 (actor isolation)
- Structural: 6-10 (protocols to protocols, similar FP style)
- Runtime: 2-3 (actor to STM/threads)

**Key Blockers:**
1. Actor model to STM (Clojure)
2. Supervision to exception handling
3. Both dynamic, both immutable - relatively compatible

**Existing Skills:** 0 (gap)

---

#### BEAM to Systems: 4 (Very Hard)

**Languages:** Elixir, Erlang -> Rust, C, C++, Go, Zig

**Gap Counts:**
- Impossible: 3-4 (actors, hot reload, supervision, per-process GC)
- Lossy: 5-7 (fault tolerance guarantees)
- Structural: 15-20 (processes to threads/async)
- Runtime: 6-8 (BEAM VM to native)

**Key Blockers:**
1. Actor model to threads/async
2. Per-process heap to shared memory
3. Hot code reload impossible
4. Supervision to error handling

**Existing Skills:** 0 (major gap)

**Pattern References:**
- CC-001: Actors to Threads (severity: high)
- MM-010: Per-Process Heap to Shared Heap
- CC-009: Supervision Trees to Exception Handling

---

#### BEAM to Dynamic: 2 (Moderate)

**Languages:** Elixir, Erlang -> Python, TypeScript, JavaScript, Ruby

**Gap Counts:**
- Impossible: 2 (hot reload, OTP supervision)
- Lossy: 3-4 (actor isolation, fault tolerance)
- Structural: 8-12 (processes to async/threads)
- Runtime: 2-3 (BEAM to interpreter)

**Key Blockers:**
1. Actor model to async/await
2. Both dynamic typed - compatible
3. Immutability by convention in target

**Existing Skills:** 0 (gap)

---

#### BEAM to Managed-OOP: 3 (Hard)

**Languages:** Elixir, Erlang -> Java, Kotlin

**Gap Counts:**
- Impossible: 2-3 (actors, hot reload)
- Lossy: 4-5 (fault tolerance, isolation)
- Structural: 12-16 (FP to OOP, processes to threads)
- Runtime: 3-4 (BEAM to JVM)

**Key Blockers:**
1. Actors to objects with threads
2. Functional to OOP style
3. Immutability to mutable defaults

**Existing Skills:** 0 (gap)

---

#### BEAM to Apple: 3 (Hard)

**Languages:** Elixir, Erlang -> Swift, Objective-C

**Gap Counts:**
- Impossible: 2-3 (actors, hot reload)
- Lossy: 4-5 (fault tolerance)
- Structural: 12-16 (processes to GCD)
- Runtime: 3-4 (BEAM to native)

**Key Blockers:**
1. Actors to GCD/async
2. Dynamic to static types (Swift)
3. BEAM patterns to iOS patterns

**Existing Skills:** 0 (gap)

---

#### BEAM to Logic: 5 (Extreme)

**Languages:** Elixir, Erlang -> Prolog

**Gap Counts:**
- Impossible: 5+ (execution model, actors, concurrency)
- Lossy: 6-8 (all BEAM guarantees)
- Structural: 20+ (complete redesign)
- Runtime: 7+ (completely different)

**Key Blockers:**
1. Actor model to logic programming
2. Forward to backward reasoning
3. Message passing to unification

**Existing Skills:** 0 (no skills)

---

#### BEAM to Procedural: 4 (Very Hard)

**Languages:** Elixir, Erlang -> COBOL, Fortran, Pascal, Ada

**Gap Counts:**
- Impossible: 3-4 (actors, FP patterns)
- Lossy: 5-7 (concurrency model)
- Structural: 18-22 (FP to imperative)
- Runtime: 4-5 (modern to legacy)

**Key Blockers:**
1. Functional to procedural
2. Actors to batch processing
3. Modern to legacy ecosystem

**Existing Skills:** 0 (no skills)

---

### 3.3 LISP Family Conversions

#### LISP to ML-FP: 3 (Hard)

**Languages:** Clojure, Common Lisp, Scheme -> Scala, Haskell, F#, Elm, Roc, Gleam

**Gap Counts:**
- Impossible: 2-3 (macros, code-as-data, reader macros)
- Lossy: 4-5 (dynamic typing, runtime modification)
- Structural: 10-15 (protocols to type classes, macros to static)
- Runtime: 2-3 (STM to other models)

**Key Blockers:**
1. Macros must be expanded before translation
2. Dynamic to static typing
3. Code-as-data not representable

**Existing Skills:** 5 (clojure-haskell, clojure-scala, clojure-fsharp, clojure-elm, clojure-roc)

**Semantic Gaps:**
- Assuming Dynamic Typing
- Atom Table Exhaustion
- Dynamic Type Assumptions to Static

---

#### LISP to BEAM: 2 (Moderate)

**Languages:** Clojure, Common Lisp, Scheme -> Elixir, Erlang

**Gap Counts:**
- Impossible: 1-2 (macro systems differ)
- Lossy: 2-3 (JVM interop for Clojure)
- Structural: 6-10 (similar FP style)
- Runtime: 2-3 (STM to actors)

**Key Blockers:**
1. STM to actor model
2. Macro systems differ
3. Both dynamic, both immutable

**Existing Skills:** 2 (clojure-elixir, clojure-erlang)

---

#### LISP to LISP: 2 (Moderate)

**Languages:** Clojure, Common Lisp, Scheme (internal)

**Gap Counts:**
- Impossible: 0
- Lossy: 2-3 (runtime differences)
- Structural: 5-10 (macro systems, libraries)
- Runtime: 1-2 (JVM vs native)

**Key Blockers:**
1. Different macro systems
2. Runtime environments (JVM, native, JS)
3. Library ecosystems

**Existing Skills:** 0 (within-family gap)

---

#### LISP to Systems: 4 (Very Hard)

**Languages:** Clojure, Common Lisp, Scheme -> Rust, C, C++, Go, Zig

**Gap Counts:**
- Impossible: 3-4 (macros, dynamic typing, runtime metaprogramming)
- Lossy: 6-8 (flexibility, REPL development)
- Structural: 15-20 (dynamic to static, FP to systems)
- Runtime: 5-6 (GC to manual/ownership)

**Key Blockers:**
1. Dynamic typing to static
2. Macros to codegen/templates
3. GC to ownership/manual memory

**Existing Skills:** 0 (major gap)

---

#### LISP to Dynamic: 2 (Moderate)

**Languages:** Clojure, Common Lisp, Scheme -> Python, TypeScript, JavaScript, Ruby

**Gap Counts:**
- Impossible: 1 (macros)
- Lossy: 2-3 (homoiconicity)
- Structural: 6-10 (S-expressions to syntax)
- Runtime: 1 (both dynamic)

**Key Blockers:**
1. Macros to functions/decorators
2. S-expression syntax to conventional
3. Both dynamic - compatible

**Existing Skills:** 1 (clojure to Python implied)

---

#### LISP to Managed-OOP: 3 (Hard)

**Languages:** Clojure, Common Lisp, Scheme -> Java, Kotlin

**Gap Counts:**
- Impossible: 2 (macros, homoiconicity)
- Lossy: 3-5 (dynamic flexibility)
- Structural: 12-16 (FP to OOP, macros)
- Runtime: 1-2 (Clojure already on JVM)

**Key Blockers:**
1. FP to OOP paradigm
2. Macros to annotations/codegen
3. Immutability to mutable

**Existing Skills:** 0 (Clojure-Java interop exists but not conversion)

---

#### LISP to Apple: 3 (Hard)

**Languages:** Clojure, Common Lisp, Scheme -> Swift, Objective-C

**Gap Counts:**
- Impossible: 2-3 (macros, dynamic features)
- Lossy: 4-5 (flexibility)
- Structural: 12-16 (dynamic to static)
- Runtime: 2-3 (JVM/native to Apple)

**Key Blockers:**
1. Dynamic to static typing
2. Macros to protocol extensions
3. Different ecosystems

**Existing Skills:** 0 (gap)

---

#### LISP to Logic: 4 (Very Hard)

**Languages:** Clojure, Common Lisp, Scheme -> Prolog

**Gap Counts:**
- Impossible: 3-4 (execution model)
- Lossy: 5-6 (computation model)
- Structural: 15-18 (functions to rules)
- Runtime: 5-6 (forward to backward)

**Key Blockers:**
1. Both declarative - some alignment
2. Functions to rules
3. Data structures to facts

**Existing Skills:** 0 (no skills)

---

#### LISP to Procedural: 4 (Very Hard)

**Languages:** Clojure, Common Lisp, Scheme -> COBOL, Fortran, Pascal, Ada

**Gap Counts:**
- Impossible: 2-3 (macros, higher-order functions)
- Lossy: 5-7 (dynamic features)
- Structural: 18-22 (FP to procedural)
- Runtime: 3-4 (modern to legacy)

**Key Blockers:**
1. Functional to procedural
2. Recursion to iteration
3. Modern to legacy

**Existing Skills:** 0 (no skills)

---

### 3.4 Systems Family Conversions

#### Systems to ML-FP: 3 (Hard)

**Languages:** Rust, C, C++, Go, Zig -> Scala, Haskell, F#, Elm, Roc, Gleam

**Gap Counts:**
- Impossible: 3-4 (pointer arithmetic, undefined behavior, inline assembly, manual free)
- Lossy: 4-6 (fine-grained memory control, cache layouts)
- Structural: 10-15 (structs to ADTs, mutation to immutable)
- Runtime: 2-3 (ownership to GC, threads to pure)

**Key Blockers:**
1. Imperative to functional style
2. Mutable state to immutable
3. Loops to recursion/folds

**Existing Skills:** 0 (gap - Systems as source rarely covered)

**Pattern References:**
- MM-004: Mutable Default to Immutable Default
- EF-006: Global State to Pure Functions

---

#### Systems to BEAM: 4 (Very Hard)

**Languages:** Rust, C, C++, Go, Zig -> Elixir, Erlang

**Gap Counts:**
- Impossible: 3-4 (low-level features)
- Lossy: 5-7 (performance control)
- Structural: 15-20 (threads to actors)
- Runtime: 5-6 (native to BEAM VM)

**Key Blockers:**
1. Threads to actor model
2. Manual memory to per-process GC
3. Low-level to high-level

**Existing Skills:** 0 (gap)

---

#### Systems to LISP: 3 (Hard)

**Languages:** Rust, C, C++, Go, Zig -> Clojure, Common Lisp, Scheme

**Gap Counts:**
- Impossible: 2-3 (low-level features)
- Lossy: 4-5 (performance)
- Structural: 10-15 (static to dynamic)
- Runtime: 2-3 (native to managed)

**Key Blockers:**
1. Static to dynamic typing
2. Manual memory to GC
3. Imperative to functional

**Existing Skills:** 0 (gap)

---

#### Systems to Systems: 2 (Moderate)

**Languages:** Rust, C, C++, Go, Zig (internal)

**Gap Counts:**
- Impossible: 1-2 (specific low-level features)
- Lossy: 2-4 (memory model nuances)
- Structural: 8-12 (syntax, idioms)
- Runtime: 1-3 (ownership vs manual vs GC)

**Key Blockers:**
1. Rust ownership to C manual memory
2. C++ RAII to C explicit
3. Go GC to Rust ownership

**Existing Skills:** 4 (c-cpp, c-rust, cpp-rust, golang-rust)

**Semantic Gaps:**
- Use-After-Free (c-rust)
- Overusing Rc/Arc (cpp-rust)
- Trying to Return Borrowed References (golang-rust)
- Over-cloning to Satisfy Borrow Checker (ts-rust)

---

#### Systems to Dynamic: 2 (Moderate)

**Languages:** Rust, C, C++, Go, Zig -> Python, TypeScript, JavaScript, Ruby

**Gap Counts:**
- Impossible: 0 (all expressible)
- Lossy: 3-5 (performance, memory control)
- Structural: 6-10 (types to dynamic)
- Runtime: 1-2 (native to interpreter)

**Key Blockers:**
1. Performance loss acceptable
2. Memory management automatic
3. Static to dynamic typing

**Existing Skills:** 0 (major gap - no "from Systems" skills)

---

#### Systems to Managed-OOP: 2 (Moderate)

**Languages:** Rust, C, C++, Go, Zig -> Java, Kotlin

**Gap Counts:**
- Impossible: 0
- Lossy: 3-4 (low-level control)
- Structural: 8-12 (to OOP patterns)
- Runtime: 1-2 (native to JVM)

**Key Blockers:**
1. Memory management simplification
2. Low-level to high-level abstraction
3. Similar imperative style

**Existing Skills:** 0 (gap)

---

#### Systems to Apple: 3 (Hard)

**Languages:** Rust, C, C++, Go, Zig -> Swift, Objective-C

**Gap Counts:**
- Impossible: 1 (specific low-level)
- Lossy: 3-5 (memory control)
- Structural: 10-15 (to Apple patterns)
- Runtime: 2-3 (native to ARC)

**Key Blockers:**
1. Memory models differ (ownership to ARC)
2. Ecosystem differences
3. Platform-specific concerns

**Existing Skills:** 0 (gap)

---

#### Systems to Logic: 5 (Extreme)

**Languages:** Rust, C, C++, Go, Zig -> Prolog

**Gap Counts:**
- Impossible: 5+ (paradigm mismatch)
- Lossy: 7+ (all low-level features)
- Structural: 25+ (complete redesign)
- Runtime: 8+ (completely different)

**Key Blockers:**
1. Imperative to declarative
2. Control flow to backtracking
3. Data structures to facts/rules

**Existing Skills:** 0 (no skills)

---

#### Systems to Procedural: 2 (Moderate)

**Languages:** Rust, C, C++, Go, Zig -> COBOL, Fortran, Pascal, Ada

**Gap Counts:**
- Impossible: 0-1
- Lossy: 2-4 (modern features)
- Structural: 8-12 (syntax modernization reverse)
- Runtime: 1-2 (similar execution model)

**Key Blockers:**
1. Similar imperative paradigm
2. Syntax differences
3. Modern to legacy ecosystem

**Existing Skills:** 0 (gap)

---

### 3.5 Dynamic Family Conversions

#### Dynamic to ML-FP: 3 (Hard)

**Languages:** Python, TypeScript, JavaScript, Ruby -> Scala, Haskell, F#, Elm, Roc, Gleam

**Gap Counts:**
- Impossible: 2-3 (monkey patching, runtime type modification, duck typing)
- Lossy: 4-6 (dynamic dispatch flexibility, None semantics)
- Structural: 12-16 (classes to ADTs, inheritance to composition)
- Runtime: 2-4 (mutable state to immutable, GIL to parallelism)

**Key Blockers:**
1. Type inference required from source
2. Null handling to Option/Maybe
3. Inheritance to composition/type classes

**Existing Skills:** 10 (python-haskell, python-scala, python-fsharp, python-elm, python-roc, plus typescript variants)

**Semantic Gaps:**
- Forgetting About Laziness
- Mutable State to Immutable
- Integer Overflow (precision)
- None vs null/undefined
- Mutability Assumptions

---

#### Dynamic to BEAM: 3 (Hard)

**Languages:** Python, TypeScript, JavaScript, Ruby -> Elixir, Erlang

**Gap Counts:**
- Impossible: 1-2 (some dynamic features)
- Lossy: 3-4 (runtime modification)
- Structural: 10-14 (OOP to FP/actors)
- Runtime: 3-4 (threads to processes)

**Key Blockers:**
1. Learn actor model
2. Mutable to immutable
3. OOP to functional

**Existing Skills:** 2 (python-elixir, python-erlang)

---

#### Dynamic to LISP: 2 (Moderate)

**Languages:** Python, TypeScript, JavaScript, Ruby -> Clojure, Common Lisp, Scheme

**Gap Counts:**
- Impossible: 0
- Lossy: 2-3 (minor differences)
- Structural: 6-10 (learn macros, S-expressions)
- Runtime: 1 (both dynamic)

**Key Blockers:**
1. Both dynamic - compatible
2. Learn macro systems
3. Syntax adjustment

**Existing Skills:** 1 (python-clojure)

---

#### Dynamic to Systems: 4 (Very Hard)

**Languages:** Python, TypeScript, JavaScript, Ruby -> Rust, C, C++, Go, Zig

**Gap Counts:**
- Impossible: 2-3 (monkey patching, runtime metaprogramming)
- Lossy: 5-7 (arbitrary precision, reflection, REPL)
- Structural: 15-20 (classes to structs, dynamic to static)
- Runtime: 4-6 (GC to ownership/manual)

**Key Blockers:**
1. Memory management (GC to ownership)
2. Type inference from untyped code
3. Error handling philosophy

**Existing Skills:** 4 (python-rust, python-golang, typescript-rust, typescript-golang)

**Semantic Gaps:**
- Over-cloning to Satisfy Borrow Checker
- Integer Overflow

---

#### Dynamic to Dynamic: 2 (Moderate)

**Languages:** Python, TypeScript, JavaScript, Ruby (internal)

**Gap Counts:**
- Impossible: 0
- Lossy: 1-2 (minor semantics)
- Structural: 5-8 (syntax, idioms)
- Runtime: 0-1 (similar models)

**Key Blockers:**
1. Similar paradigms
2. Syntax differences
3. Library ecosystem

**Existing Skills:** 1 (python-typescript)

---

#### Dynamic to Managed-OOP: 2 (Moderate)

**Languages:** Python, TypeScript, JavaScript, Ruby -> Java, Kotlin

**Gap Counts:**
- Impossible: 0
- Lossy: 2-3 (dynamic features)
- Structural: 8-12 (add types, structure)
- Runtime: 1 (both managed)

**Key Blockers:**
1. Add explicit types
2. Structure code more formally
3. Similar OOP style

**Existing Skills:** 0 (gap)

---

#### Dynamic to Apple: 3 (Hard)

**Languages:** Python, TypeScript, JavaScript, Ruby -> Swift, Objective-C

**Gap Counts:**
- Impossible: 1 (some dynamic features)
- Lossy: 3-5 (flexibility)
- Structural: 10-14 (types, ARC)
- Runtime: 2-3 (managed to ARC)

**Key Blockers:**
1. Dynamic to static types (Swift)
2. Memory model (to ARC)
3. Platform differences

**Existing Skills:** 0 (gap)

---

#### Dynamic to Logic: 4 (Very Hard)

**Languages:** Python, TypeScript, JavaScript, Ruby -> Prolog

**Gap Counts:**
- Impossible: 3-4 (paradigm mismatch)
- Lossy: 5-6 (execution model)
- Structural: 15-20 (imperative to logic)
- Runtime: 5-6 (iteration to backtracking)

**Key Blockers:**
1. Paradigm shift
2. Generators can simulate backtracking partially
3. Libraries like pyDatalog exist

**Existing Skills:** 0 (no skills)

---

#### Dynamic to Procedural: 2 (Moderate)

**Languages:** Python, TypeScript, JavaScript, Ruby -> COBOL, Fortran, Pascal, Ada

**Gap Counts:**
- Impossible: 0-1
- Lossy: 3-4 (modern features)
- Structural: 8-12 (style simplification)
- Runtime: 1-2 (similar in some ways)

**Key Blockers:**
1. Modernization in reverse
2. Decimal precision (Python)
3. Syntax translation

**Existing Skills:** 0 (gap)

---

### 3.6 Managed-OOP Family Conversions

#### Managed-OOP to ML-FP: 3 (Hard)

**Languages:** Java, Kotlin -> Scala, Haskell, F#, Elm, Roc, Gleam

**Gap Counts:**
- Impossible: 0 (all OOP expressible as FP)
- Lossy: 3-5 (inheritance chains, mutable idioms)
- Structural: 15-20 (classes to ADTs, inheritance to type classes)
- Runtime: 2-3 (mutable to immutable state)

**Key Blockers:**
1. Inheritance to composition
2. Mutable to immutable
3. OOP patterns to FP patterns

**Existing Skills:** 0 (Java-Scala interop exists but not pure conversion)

---

#### Managed-OOP to BEAM: 3 (Hard)

**Languages:** Java, Kotlin -> Elixir, Erlang

**Gap Counts:**
- Impossible: 1-2 (OOP patterns)
- Lossy: 3-5 (OOP flexibility)
- Structural: 12-16 (objects to actors)
- Runtime: 2-3 (JVM to BEAM)

**Key Blockers:**
1. Objects to actors
2. Shared state to message passing
3. OOP to FP

**Existing Skills:** 0 (gap)

---

#### Managed-OOP to LISP: 3 (Hard)

**Languages:** Java, Kotlin -> Clojure, Common Lisp, Scheme

**Gap Counts:**
- Impossible: 0-1
- Lossy: 3-4 (OOP structure)
- Structural: 12-16 (OOP to FP)
- Runtime: 1 (Clojure on JVM)

**Key Blockers:**
1. OOP to FP paradigm
2. Classes to data + functions
3. Clojure interop possible

**Existing Skills:** 0 (gap)

---

#### Managed-OOP to Systems: 3 (Hard)

**Languages:** Java, Kotlin -> Rust, C, C++, Go, Zig

**Gap Counts:**
- Impossible: 1-2 (type erasure, runtime reflection)
- Lossy: 3-5 (GC simplicity, checked exceptions)
- Structural: 12-16 (classes to structs, inheritance to composition)
- Runtime: 3-4 (GC to ownership/manual)

**Key Blockers:**
1. GC to ownership/manual memory
2. Inheritance flattening
3. Null to Option

**Existing Skills:** 3 (java-rust, java-c, java-cpp)

---

#### Managed-OOP to Dynamic: 2 (Moderate)

**Languages:** Java, Kotlin -> Python, TypeScript, JavaScript, Ruby

**Gap Counts:**
- Impossible: 0
- Lossy: 2-3 (type safety)
- Structural: 6-10 (remove types)
- Runtime: 0-1 (similar managed)

**Key Blockers:**
1. Remove explicit types
2. Simplify structure
3. Similar OOP style

**Existing Skills:** 0 (gap)

---

#### Managed-OOP to Managed-OOP: 2 (Moderate)

**Languages:** Java, Kotlin (internal)

**Gap Counts:**
- Impossible: 0
- Lossy: 1-2 (minor features)
- Structural: 5-8 (syntax, null handling)
- Runtime: 0 (same JVM)

**Key Blockers:**
1. Kotlin null safety to Java
2. Extension functions to static
3. Similar overall

**Existing Skills:** 0 (gap - Java-Kotlin needed)

---

#### Managed-OOP to Apple: 2 (Moderate)

**Languages:** Java, Kotlin -> Swift, Objective-C

**Gap Counts:**
- Impossible: 0
- Lossy: 2-3 (platform features)
- Structural: 8-12 (similar OOP)
- Runtime: 1-2 (GC to ARC)

**Key Blockers:**
1. GC to ARC
2. Similar OOP paradigm
3. Platform differences

**Existing Skills:** 0 (gap)

---

#### Managed-OOP to Logic: 5 (Extreme)

**Languages:** Java, Kotlin -> Prolog

**Gap Counts:**
- Impossible: 4+ (paradigm completely different)
- Lossy: 6-8 (all OOP features)
- Structural: 20+ (complete redesign)
- Runtime: 6+ (JVM to Prolog)

**Key Blockers:**
1. OOP to logic programming
2. Objects to facts/rules
3. Methods to predicates

**Existing Skills:** 0 (no skills)

---

#### Managed-OOP to Procedural: 2 (Moderate)

**Languages:** Java, Kotlin -> COBOL, Fortran, Pascal, Ada

**Gap Counts:**
- Impossible: 0-1
- Lossy: 3-4 (OOP features)
- Structural: 10-14 (OOP to procedural)
- Runtime: 1-2 (JVM to native)

**Key Blockers:**
1. OOP to procedural style
2. Natural modernization path (COBOL to Java reverse)
3. Decimal precision

**Existing Skills:** 0 (gap)

---

### 3.7 Apple Family Conversions

#### Apple to ML-FP: 3 (Hard)

**Languages:** Swift, Objective-C -> Scala, Haskell, F#, Elm, Roc, Gleam

**Gap Counts:**
- Impossible: 1-2 (ARC cycles, Obj-C runtime)
- Lossy: 3-5 (framework integration)
- Structural: 12-16 (protocols to type classes)
- Runtime: 2-3 (ARC to GC)

**Key Blockers:**
1. Swift enums translate well to ADTs
2. Protocol-oriented to type class
3. Framework-specific code

**Existing Skills:** 0 (gap)

---

#### Apple to BEAM: 4 (Very Hard)

**Languages:** Swift, Objective-C -> Elixir, Erlang

**Gap Counts:**
- Impossible: 2-3 (ARC, platform specific)
- Lossy: 4-6 (ecosystem)
- Structural: 15-18 (to actors)
- Runtime: 4-5 (native to BEAM)

**Key Blockers:**
1. ARC to actor model
2. GCD to OTP
3. Platform specific code

**Existing Skills:** 0 (gap)

---

#### Apple to LISP: 3 (Hard)

**Languages:** Swift, Objective-C -> Clojure, Common Lisp, Scheme

**Gap Counts:**
- Impossible: 1-2 (platform specific)
- Lossy: 3-5 (static types)
- Structural: 12-15 (static to dynamic)
- Runtime: 2-3 (ARC to GC)

**Key Blockers:**
1. Static to dynamic
2. ARC to GC
3. Ecosystem differences

**Existing Skills:** 0 (gap)

---

#### Apple to Systems: 3 (Hard)

**Languages:** Swift, Objective-C -> Rust, C, C++, Go, Zig

**Gap Counts:**
- Impossible: 1-2 (Obj-C runtime)
- Lossy: 3-5 (ARC automation)
- Structural: 10-14 (protocols to traits)
- Runtime: 2-4 (ARC to ownership/manual)

**Key Blockers:**
1. ARC to ownership (Rust) or manual (C)
2. Swift is relatively close to Rust
3. Objective-C more challenging (dynamic)

**Existing Skills:** 0 (gap)

---

#### Apple to Dynamic: 2 (Moderate)

**Languages:** Swift, Objective-C -> Python, TypeScript, JavaScript, Ruby

**Gap Counts:**
- Impossible: 0
- Lossy: 2-4 (type safety)
- Structural: 8-12 (types to dynamic)
- Runtime: 1-2 (ARC to GC)

**Key Blockers:**
1. ARC to GC (simpler)
2. Static to dynamic types
3. Platform differences

**Existing Skills:** 0 (gap)

---

#### Apple to Managed-OOP: 2 (Moderate)

**Languages:** Swift, Objective-C -> Java, Kotlin

**Gap Counts:**
- Impossible: 0
- Lossy: 2-3 (platform features)
- Structural: 8-12 (similar OOP)
- Runtime: 1-2 (ARC to GC)

**Key Blockers:**
1. Similar OOP paradigm
2. ARC to GC simplification
3. Platform differences

**Existing Skills:** 0 (gap)

---

#### Apple to Apple: 2 (Moderate)

**Languages:** Swift, Objective-C (internal)

**Gap Counts:**
- Impossible: 0 (Swift designed as Obj-C successor)
- Lossy: 2-3 (dynamic message passing)
- Structural: 5-8 (syntax, patterns)
- Runtime: 0-1 (same platform)

**Key Blockers:**
1. Swift is Obj-C successor
2. Apple provides migration tools
3. @objc bridging available

**Existing Skills:** 1 (objc-swift)

**Semantic Gaps:**
- Force Unwrapping Optionals

---

#### Apple to Logic: 5 (Extreme)

**Languages:** Swift, Objective-C -> Prolog

**Gap Counts:**
- Impossible: 5+ (paradigm mismatch)
- Lossy: 6+ (all OOP/platform features)
- Structural: 20+ (complete redesign)
- Runtime: 7+ (native to Prolog)

**Key Blockers:**
1. OOP to logic
2. Platform-specific impossible
3. Complete paradigm shift

**Existing Skills:** 0 (no skills)

---

#### Apple to Procedural: 3 (Hard)

**Languages:** Swift, Objective-C -> COBOL, Fortran, Pascal, Ada

**Gap Counts:**
- Impossible: 1-2 (platform specific)
- Lossy: 4-5 (modern features)
- Structural: 14-18 (OOP to procedural)
- Runtime: 2-3 (modern to legacy)

**Key Blockers:**
1. OOP to procedural
2. Modern to legacy
3. Platform differences

**Existing Skills:** 0 (gap)

---

### 3.8 Logic Family Conversions

#### Logic to ML-FP: 4 (Very Hard)

**Languages:** Prolog -> Scala, Haskell, F#, Elm, Roc, Gleam

**Gap Counts:**
- Impossible: 4 (unification, backtracking, logic variables, cut)
- Lossy: 5-7 (declarative search)
- Structural: 15-20 (rules to functions, facts to data)
- Runtime: 5-6 (SLD resolution to forward evaluation)

**Key Blockers:**
1. Backtracking to explicit search
2. Unification to pattern matching
3. LogicT monad in Haskell can help

**Existing Skills:** 0 (no skills)

**Pattern References:**
- No direct patterns - paradigm too different

---

#### Logic to BEAM: 4 (Very Hard)

**Languages:** Prolog -> Elixir, Erlang

**Gap Counts:**
- Impossible: 4 (unification, backtracking)
- Lossy: 5-6 (logic search)
- Structural: 15-18 (rules to processes)
- Runtime: 5-6 (backtracking to actors)

**Key Blockers:**
1. Backtracking to actor patterns
2. Rules to GenServer
3. Both declarative - some alignment

**Existing Skills:** 0 (no skills)

---

#### Logic to LISP: 3 (Hard)

**Languages:** Prolog -> Clojure, Common Lisp, Scheme

**Gap Counts:**
- Impossible: 2-3 (automatic backtracking)
- Lossy: 4-5 (declarative search)
- Structural: 12-15 (rules to functions)
- Runtime: 3-4 (minikanren libraries help)

**Key Blockers:**
1. minikanren/core.logic in Clojure
2. Both declarative - closest match
3. Macros can help with DSL

**Existing Skills:** 0 (no skills)

---

#### Logic to Systems: 5 (Extreme)

**Languages:** Prolog -> Rust, C, C++, Go, Zig

**Gap Counts:**
- Impossible: 5+ (paradigm completely different)
- Lossy: 7+ (all logic features)
- Structural: 25+ (complete redesign)
- Runtime: 8+ (backtracking to imperative)

**Key Blockers:**
1. No good embedding options
2. Must extract specific algorithms
3. Consider keeping Prolog for logic portions

**Existing Skills:** 0 (no skills)

---

#### Logic to Dynamic: 4 (Very Hard)

**Languages:** Prolog -> Python, TypeScript, JavaScript, Ruby

**Gap Counts:**
- Impossible: 3-4 (backtracking, unification)
- Lossy: 5-6 (declarative search)
- Structural: 15-18 (rules to imperative)
- Runtime: 4-5 (generators can simulate)

**Key Blockers:**
1. pyDatalog, kanren libraries
2. Generators can simulate backtracking
3. More flexible but still paradigm shift

**Existing Skills:** 0 (no skills)

---

#### Logic to Managed-OOP: 5 (Extreme)

**Languages:** Prolog -> Java, Kotlin

**Gap Counts:**
- Impossible: 4+ (paradigm mismatch)
- Lossy: 6-7 (logic features)
- Structural: 20+ (rules to objects)
- Runtime: 6+ (backtracking to methods)

**Key Blockers:**
1. Logic to OOP - extreme mismatch
2. JProlog libraries exist
3. Usually embed rather than convert

**Existing Skills:** 0 (no skills)

---

#### Logic to Apple: 5 (Extreme)

**Languages:** Prolog -> Swift, Objective-C

**Gap Counts:**
- Impossible: 4+ (paradigm mismatch)
- Lossy: 6+ (logic features)
- Structural: 20+ (complete redesign)
- Runtime: 6+ (different execution)

**Key Blockers:**
1. Paradigm mismatch
2. No good libraries
3. Usually FFI to Prolog

**Existing Skills:** 0 (no skills)

---

#### Logic to Logic: 2 (Moderate)

**Languages:** Prolog (internal - SWI, GNU, etc.)

**Gap Counts:**
- Impossible: 0
- Lossy: 1-2 (dialect differences)
- Structural: 4-8 (syntax, extensions)
- Runtime: 0-1 (similar execution)

**Key Blockers:**
1. Same paradigm
2. Dialect differences
3. Library availability

**Existing Skills:** 0 (gap)

---

#### Logic to Procedural: 4 (Very Hard)

**Languages:** Prolog -> COBOL, Fortran, Pascal, Ada

**Gap Counts:**
- Impossible: 4 (backtracking, unification)
- Lossy: 5-6 (logic search)
- Structural: 18-22 (declarative to imperative)
- Runtime: 5-6 (different execution)

**Key Blockers:**
1. Declarative to imperative
2. Backtracking to explicit loops
3. No libraries to help

**Existing Skills:** 0 (no skills)

---

### 3.9 Procedural Family Conversions

#### Procedural to ML-FP: 4 (Very Hard)

**Languages:** COBOL, Fortran, Pascal, Ada -> Scala, Haskell, F#, Elm, Roc, Gleam

**Gap Counts:**
- Impossible: 0-1 (style differences mainly)
- Lossy: 4-6 (decimal precision, array layouts)
- Structural: 18-22 (imperative to FP)
- Runtime: 2-4 (batch to functional)

**Key Blockers:**
1. Imperative to functional paradigm
2. Mutation to immutability
3. Loops to recursion

**Existing Skills:** 0 (no skills)

---

#### Procedural to BEAM: 4 (Very Hard)

**Languages:** COBOL, Fortran, Pascal, Ada -> Elixir, Erlang

**Gap Counts:**
- Impossible: 1-2 (batch processing)
- Lossy: 4-6 (processing model)
- Structural: 16-20 (batch to actors)
- Runtime: 4-5 (batch to concurrent)

**Key Blockers:**
1. Batch to actor model
2. Imperative to functional
3. Legacy to modern

**Existing Skills:** 0 (no skills)

---

#### Procedural to LISP: 3 (Hard)

**Languages:** COBOL, Fortran, Pascal, Ada -> Clojure, Common Lisp, Scheme

**Gap Counts:**
- Impossible: 0-1
- Lossy: 3-5 (precision, style)
- Structural: 12-16 (imperative to FP)
- Runtime: 2-3 (batch to interactive)

**Key Blockers:**
1. Imperative to FP
2. Less extreme than to ML-FP
3. Dynamic typing helps

**Existing Skills:** 0 (no skills)

---

#### Procedural to Systems: 2 (Moderate)

**Languages:** COBOL, Fortran, Pascal, Ada -> Rust, C, C++, Go, Zig

**Gap Counts:**
- Impossible: 0
- Lossy: 2-4 (precision, formats)
- Structural: 8-12 (syntax modernization)
- Runtime: 1-2 (similar execution)

**Key Blockers:**
1. Similar imperative style
2. Syntax differences
3. Decimal precision (COBOL)

**Existing Skills:** 0 (gap)

---

#### Procedural to Dynamic: 3 (Hard)

**Languages:** COBOL, Fortran, Pascal, Ada -> Python, TypeScript, JavaScript, Ruby

**Gap Counts:**
- Impossible: 0
- Lossy: 3-4 (precision)
- Structural: 10-14 (modernization)
- Runtime: 1-2 (batch to interactive)

**Key Blockers:**
1. Modernization path
2. Python Decimal for COBOL precision
3. Good for prototyping

**Existing Skills:** 0 (gap)

---

#### Procedural to Managed-OOP: 3 (Hard)

**Languages:** COBOL, Fortran, Pascal, Ada -> Java, Kotlin

**Gap Counts:**
- Impossible: 0
- Lossy: 2-4 (precision)
- Structural: 12-16 (procedural to OOP)
- Runtime: 1-2 (similar execution)

**Key Blockers:**
1. Natural modernization path (COBOL to Java)
2. IBM provides tools
3. Decimal precision important

**Existing Skills:** 0 (gap)

---

#### Procedural to Apple: 3 (Hard)

**Languages:** COBOL, Fortran, Pascal, Ada -> Swift, Objective-C

**Gap Counts:**
- Impossible: 0-1
- Lossy: 3-4 (features)
- Structural: 12-16 (to OOP)
- Runtime: 2-3 (batch to app)

**Key Blockers:**
1. Modernization with ARC
2. Procedural to protocol-oriented
3. Platform differences

**Existing Skills:** 0 (gap)

---

#### Procedural to Logic: 5 (Extreme)

**Languages:** COBOL, Fortran, Pascal, Ada -> Prolog

**Gap Counts:**
- Impossible: 4+ (paradigm mismatch)
- Lossy: 5+ (execution model)
- Structural: 20+ (complete redesign)
- Runtime: 6+ (batch to backtracking)

**Key Blockers:**
1. Paradigm mismatch
2. Imperative to declarative
3. No practical use case

**Existing Skills:** 0 (no skills)

---

#### Procedural to Procedural: 2 (Moderate)

**Languages:** COBOL, Fortran, Pascal, Ada (internal)

**Gap Counts:**
- Impossible: 0
- Lossy: 2-3 (precision, formats)
- Structural: 6-10 (syntax, idioms)
- Runtime: 0-1 (similar execution)

**Key Blockers:**
1. Similar paradigm
2. Syntax differences
3. Era-specific features

**Existing Skills:** 0 (gap)

---

## 4. Summary Statistics

### 4.1 Average Difficulty by Source Family

| Source Family | Avg Difficulty | Easiest Target | Hardest Target |
|---------------|----------------|----------------|----------------|
| ML-FP | 2.89 | Dynamic (2), LISP (2) | Systems (4), Logic (4), Proc (4) |
| BEAM | 3.11 | BEAM (2), LISP (2), Dyn (2) | Logic (5) |
| LISP | 2.89 | BEAM (2), LISP (2), Dyn (2) | Systems (4), Logic (4), Proc (4) |
| Systems | 2.78 | Systems (2), Dyn (2), Mgd (2), Proc (2) | Logic (5) |
| Dynamic | 2.67 | LISP (2), Dyn (2), Mgd (2), Proc (2) | Systems (4), Logic (4) |
| Managed-OOP | 2.78 | Dyn (2), Mgd (2), Apple (2), Proc (2) | Logic (5) |
| Apple | 3.00 | Dyn (2), Mgd (2), Apple (2) | Logic (5) |
| Logic | 4.00 | Logic (2), LISP (3) | Systems (5), Mgd (5), Apple (5), Proc (4) |
| Procedural | 3.11 | Systems (2), Proc (2) | Logic (5) |

**Easiest source families:** Dynamic (2.67), Systems (2.78), Managed-OOP (2.78)
**Hardest source family:** Logic (4.00)

### 4.2 Average Difficulty by Target Family

| Target Family | Avg Difficulty | Easiest Source | Hardest Source |
|---------------|----------------|----------------|----------------|
| ML-FP | 3.11 | ML-FP (2) | Logic (4), Proc (4) |
| BEAM | 3.22 | ML-FP (3), BEAM (2), LISP (2), Dyn (3) | Logic (4), Proc (4), Systems (4), Apple (4) |
| LISP | 2.56 | ML-FP (2), BEAM (2), LISP (2), Dyn (2) | Logic (3), Systems (3) |
| Systems | 3.33 | Systems (2), Proc (2) | ML-FP (4), BEAM (4), LISP (4), Dyn (4), Logic (5) |
| Dynamic | 2.22 | All mostly 2 | Logic (4) |
| Managed-OOP | 2.78 | Dyn (2), Mgd (2), Apple (2), Proc (2), Systems (2) | Logic (5) |
| Apple | 2.78 | ML-FP (3), Dyn (2), Mgd (2), Apple (2) | Logic (5) |
| Logic | 4.67 | Logic (2) | All others (4-5) |
| Procedural | 2.89 | Systems (2), Mgd (2), Proc (2), Dyn (2) | ML-FP (4), BEAM (4), LISP (4), Logic (4) |

**Easiest target families:** Dynamic (2.22), LISP (2.56)
**Hardest target families:** Logic (4.67), Systems (3.33), BEAM (3.22)

### 4.3 Symmetric vs Asymmetric Pairs

| Pair | A->B | B->A | Delta | Notes |
|------|------|------|-------|-------|
| ML-FP <-> Systems | 4 | 3 | 1 | Systems to ML-FP easier (no memory redesign) |
| ML-FP <-> BEAM | 3 | 3 | 0 | Symmetric |
| ML-FP <-> Dynamic | 2 | 3 | 1 | ML-FP to Dynamic easier (just loses safety) |
| BEAM <-> Systems | 4 | 4 | 0 | Symmetric (both hard) |
| BEAM <-> Dynamic | 2 | 3 | 1 | BEAM to Dynamic easier |
| Logic <-> ML-FP | 4 | 4 | 0 | Symmetric (both very hard) |
| Logic <-> Systems | 5 | 5 | 0 | Symmetric (both extreme) |
| Procedural <-> Systems | 2 | 2 | 0 | Symmetric (both moderate) |
| Apple <-> Managed-OOP | 2 | 2 | 0 | Symmetric |

**Most asymmetric pairs:**
1. ML-FP <-> Systems (Delta: 1) - Memory model direction matters
2. BEAM <-> Dynamic (Delta: 1) - Actor model easier to leave
3. ML-FP <-> Dynamic (Delta: 1) - Type safety asymmetric

### 4.4 Easiest and Hardest Pairs

**Top 5 Easiest Pairs (Score: 2)**
1. ML-FP -> ML-FP (shared ADTs, pattern matching, type classes)
2. BEAM -> BEAM (same VM, similar concepts)
3. LISP -> LISP (same paradigm)
4. Systems -> Systems (similar imperative style)
5. Dynamic -> Dynamic (same paradigm)

**Top 5 Hardest Pairs (Score: 5)**
1. Logic -> Systems (paradigm mismatch)
2. Logic -> Managed-OOP (paradigm mismatch)
3. Logic -> Apple (paradigm mismatch)
4. BEAM -> Logic (actor to logic)
5. Procedural -> Logic (imperative to declarative)

### 4.5 Distribution Summary

| Difficulty | Count | Percentage |
|------------|-------|------------|
| 2 (Moderate) | 28 | 38.9% |
| 3 (Hard) | 26 | 36.1% |
| 4 (Very Hard) | 13 | 18.1% |
| 5 (Extreme) | 5 | 6.9% |

**Note:** No pairs rated as 1 (Easy) - all cross-family conversions require some effort.

---

## 5. Key Gap Patterns Applied

### 5.1 Patterns by Severity Impact

| Pattern ID | Pattern Name | Severity | Pairs Affected |
|------------|--------------|----------|----------------|
| MM-001 | GC to Manual Allocation | critical | * -> Systems (C) |
| MM-002 | GC to Ownership/Borrowing | high | * -> Rust |
| TS-003 | Higher-Kinded Types to No HKT | high | ML-FP -> Systems/Managed |
| CC-001 | Actors to Threads | high | BEAM -> Systems/Managed |
| EF-009 | Lazy to Strict Evaluation | high | Haskell -> * |
| TS-010 | Type Classes to Interface Dispatch | high | ML-FP -> Java/Go |
| EF-001 | Exceptions to Result/Either | high | Dynamic/Managed -> ML-FP |

### 5.2 Pattern Categories by Family Pair

| Family Pair | Primary Pattern Categories |
|-------------|---------------------------|
| * -> Systems | Memory (MM-001, MM-002), Type (TS-003) |
| ML-FP -> * | Type (TS-003, TS-010), Effect (EF-004, EF-009) |
| BEAM -> * | Concurrency (CC-001, CC-009), Memory (MM-010) |
| * -> ML-FP | Type (TS-001), Effect (EF-001, EF-005) |
| Dynamic -> * | Type (TS-001, TS-004, TS-005) |
| Logic -> * | All patterns - complete paradigm redesign |

---

## 6. Skill Coverage Status

### 6.1 Coverage by Cell

| FROM / TO | ML-FP | BEAM | LISP | Systems | Dynamic | Managed-OOP | Apple | Logic | Procedural |
|-----------|-------|------|------|---------|---------|-------------|-------|-------|------------|
| **ML-FP** | 10+ | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **BEAM** | 10 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **LISP** | 5 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| **Systems** | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 |
| **Dynamic** | 10 | 2 | 1 | 4 | 1 | 0 | 0 | 0 | 0 |
| **Managed-OOP** | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 |
| **Apple** | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| **Logic** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Procedural** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**Total cells with skills:** 18/72 (25%)
**Total skill count:** 49

### 6.2 Priority Matrix (Difficulty vs Coverage)

| Priority | Difficulty | Coverage | Action | Example Pairs |
|----------|------------|----------|--------|---------------|
| P0 | 2-3 | 0 | Create immediately | ML-FP -> Dynamic, Systems -> Dynamic |
| P1 | 3-4 | Low (<25%) | Expand coverage | ML-FP -> Systems, Dynamic -> Systems |
| P2 | 2-3 | Medium | Fill gaps | BEAM -> LISP, Systems -> ML-FP |
| P3 | 4-5 | 0 | Research first | Logic -> *, * -> Logic |

---

## 7. Recommendations

### 7.1 Immediate Priorities

Based on difficulty (<=3) and zero coverage:

1. **ML-FP -> Dynamic** (Score: 2) - Reverse the most common conversion paths
2. **Systems -> Dynamic** (Score: 2) - Enable Rust/C to Python/TS
3. **BEAM -> Dynamic** (Score: 2) - Enable Elixir to Python/TS
4. **LISP -> LISP** (Score: 2) - Complete within-family coverage

### 7.2 High-Value Medium-Difficulty

Score 3 pairs with high traffic potential:

1. **Dynamic -> ML-FP** - Already has 10 skills, add more
2. **Managed-OOP -> ML-FP** - Java to Scala/Haskell
3. **Systems -> ML-FP** - Rust to Haskell/Scala

### 7.3 Long-Term Research

Score 4-5 pairs requiring paradigm research:

1. **Logic -> *** - Prolog conversion research
2. ***** -> Logic** - Logic programming embedding
3. **ML-FP -> Systems** - Memory model transformation

---

*Generated for task ai-p29.3*
*Data derived from family-pairs.md, gap-patterns.md, gap-classification.md, coverage-gaps.md*
