# Language Family Taxonomy

Comprehensive taxonomy of 13 language families for IR design and conversion strategies.

## Family Overview

### By Category

| Category | Count | Families |
|----------|-------|----------|
| Paradigm | 7 | ML-FP, BEAM, LISP, Systems, Managed-OOP, Dynamic, Apple |
| Feature | 4 | Gradual-Typing, Ownership, Actors, Dependent-Types |
| Specialized | 2 | Logic, Array |

### Paradigm Families (7)

These are the primary classification based on programming model.

| Family | Description | Languages | Priority |
|--------|-------------|-----------|----------|
| **ML-FP** | Functional with type inference, pattern matching, ADTs | Haskell, Elm, Scala, F#, OCaml, Roc | 1 |
| **Dynamic** | Dynamically-typed, flexible, rapid development | Python, Ruby, JavaScript, TypeScript | 2 |
| **BEAM** | Actor model, fault tolerance, distributed | Erlang, Elixir, Gleam | 3 |
| **LISP** | Homoiconic, macros, code-as-data | Clojure, Racket, Common Lisp, Scheme | 4 |
| **Systems** | Hardware access, manual/ownership memory | Rust, C, C++, Zig | 5 |
| **Managed-OOP** | Class-based OOP with GC | Java, C#, Kotlin | 6 |
| **Apple** | Apple platform languages with ARC | Objective-C, Swift | 7 |

### Feature Families (4)

Cross-cutting concerns that span paradigm families.

| Family | Description | Languages | Base Family |
|--------|-------------|-----------|-------------|
| **Gradual-Typing** | Optional static types | TypeScript, Python (typed), Hack | Dynamic |
| **Ownership** | Memory safety via ownership | Rust, Linear Haskell, Austral | Systems/ML-FP |
| **Actors** | Message-passing concurrency | Erlang, Elixir, Akka (Scala), Pony | BEAM/ML-FP |
| **Dependent-Types** | Types depending on values | Idris, Agda, Coq, Lean | ML-FP |

### Specialized Families (2)

Niche paradigms with unique characteristics.

| Family | Description | Languages |
|--------|-------------|-----------|
| **Logic** | Logical inference, unification | Prolog, Datalog, Mercury |
| **Array** | Implicit iteration, rank polymorphism | APL, J, K, BQN |

## Dimension Reference

Each family is characterized across 7 dimensions:

### 1. Typing

| Value | Description | Example Families |
|-------|-------------|------------------|
| dynamic | Types checked at runtime | Dynamic, LISP, BEAM |
| gradual | Mix of static and dynamic | Gradual-Typing |
| static | Types checked at compile time | ML-FP, Systems, Managed-OOP |
| dependent | Types can depend on values | Dependent-Types |

### 2. Type Inference

| Value | Description | Example Families |
|-------|-------------|------------------|
| none | All types must be explicit | BEAM (Erlang), Dynamic |
| local | Infer within expressions | Managed-OOP, Systems (C++) |
| global | Hindley-Milner style | ML-FP (Haskell, OCaml) |
| bidirectional | Both directions | ML-FP (Scala, F#) |

### 3. Generics

| Value | Description | Example Families |
|-------|-------------|------------------|
| none | No parametric polymorphism | BEAM (Erlang) |
| runtime | Duck typing / structural | Dynamic, LISP |
| parametric | Type parameters | Systems (Rust) |
| bounded | Type params with constraints | Managed-OOP, Systems |
| higher-kinded | Type constructors as params | ML-FP (Haskell, Scala) |

### 4. Memory Model

| Value | Description | Example Families |
|-------|-------------|------------------|
| manual | Explicit malloc/free | Systems (C, C++) |
| gc | Garbage collection | ML-FP, BEAM, Managed-OOP, Dynamic, LISP |
| rc | Reference counting | Apple (ARC) |
| ownership | Ownership/borrowing | Systems (Rust) |

### 5. Evaluation Strategy

| Value | Description | Example Families |
|-------|-------------|------------------|
| strict | Eager evaluation | Most families |
| lazy | Call-by-need | ML-FP (Haskell) |
| partial | Mix | Some ML-FP variants |

### 6. Effect Handling

| Value | Description | Example Families |
|-------|-------------|------------------|
| exceptions | Throw/catch | Managed-OOP, Dynamic, Apple |
| results | Error as return value | Systems (Rust), ML-FP (Elm, Roc) |
| monadic | Effects in monads | ML-FP (Haskell) |
| algebraic | Effect handlers | ML-FP (Roc, some Haskell) |

### 7. Concurrency Model

| Value | Description | Example Families |
|-------|-------------|------------------|
| threads | OS threads | Systems, Managed-OOP |
| actors | Message-passing | BEAM, Actors |
| async | Async/await | Dynamic (JS), Systems (Rust) |
| green-threads | User-space threads | ML-FP (Haskell), some BEAM |

## Family Subtypes

### ML-FP Subtypes

| Subtype | Characteristics | Languages |
|---------|-----------------|-----------|
| **pure** | No side effects, referential transparency | Haskell, Elm, PureScript, Idris |
| **hybrid** | Functional-first with imperative escape | Scala, F#, OCaml, ReasonML, Roc |

### Systems Subtypes

| Subtype | Characteristics | Languages |
|---------|-----------------|-----------|
| **ownership** | Memory safety via ownership | Rust |
| **manual** | Manual memory management | C, C++, Zig |

### Dynamic Subtypes

| Subtype | Characteristics | Languages |
|---------|-----------------|-----------|
| **scripting** | General-purpose | Python, Ruby, Perl |
| **web** | Web-focused | JavaScript, PHP |

### LISP Subtypes

| Subtype | Characteristics | Languages |
|---------|-----------------|-----------|
| **modern** | Contemporary tooling | Clojure, Racket |
| **classic** | Traditional | Common Lisp, Scheme |

## Language-to-Family Mapping

Complete mapping of languages in existing convert-* skills:

| Language | Primary Family | Secondary Families | Subtype |
|----------|---------------|-------------------|---------|
| Python | Dynamic | Gradual-Typing (with hints) | scripting |
| TypeScript | Dynamic | Gradual-Typing | web |
| JavaScript | Dynamic | - | web |
| Clojure | LISP | - | modern |
| Erlang | BEAM | Actors | core |
| Elixir | BEAM | Actors | core |
| Gleam | BEAM | - | core |
| Haskell | ML-FP | - | pure |
| Elm | ML-FP | - | pure |
| F# | ML-FP | - | hybrid |
| Scala | ML-FP | Actors (Akka) | hybrid |
| OCaml | ML-FP | - | hybrid |
| Roc | ML-FP | - | hybrid |
| Rust | Systems | Ownership | ownership |
| C | Systems | - | manual |
| C++ | Systems | - | manual |
| Go | Systems | - | (gc-based) |
| Zig | Systems | - | manual |
| Java | Managed-OOP | - | classic |
| C# | Managed-OOP | - | classic |
| Kotlin | Managed-OOP | - | modern |
| Objective-C | Apple | - | legacy |
| Swift | Apple | - | modern |

## Conversion Complexity Matrix

Based on Phase 0 gap analysis (320 gaps identified):

### High Complexity Conversions (20+ gaps)

| From → To | Gaps | Primary Challenges |
|-----------|------|-------------------|
| ML-FP → ML-FP | 63 | Subtype differences (pure↔hybrid), HKT variance |
| Dynamic → ML-FP | 39 | Type inference, null handling, immutability |
| BEAM → ML-FP | 36 | Actor model translation, process state |
| Dynamic → Systems | 29 | Memory management, type strictness |
| LISP → ML-FP | 27 | Macro expansion, dynamic typing |
| Systems → Systems | 23 | Memory model differences (manual↔ownership) |

### Medium Complexity Conversions (10-19 gaps)

| From → To | Gaps | Primary Challenges |
|-----------|------|-------------------|
| Managed-OOP → Systems | 13 | GC → ownership, class → trait |
| LISP → BEAM | 12 | Macro systems differ, STM → processes |
| ML-FP → Dynamic | 11 | Type erasure, lazy → strict |
| ML-FP → BEAM | 10 | Pure functions → processes |

### Low Complexity Conversions (<10 gaps)

Intra-family and compatible paradigm conversions are generally easier.

## Phase 0 Cross-Reference Results (Task 1.5)

Full analysis: [phase0-crossref.md](phase0-crossref.md)

### Pattern Cluster Validation

- [x] **Universal patterns (173)** - Mapped to family characteristics
  - Core types (`bool`, `string`, `int`, `float`) confirmed across all families
  - Methodology patterns consistent (analyze → map types → preserve semantics)
- [x] **Family-specific patterns (417)** - Assigned to correct families
  - ML-FP: `unit`, `IO a`, `Either e a` patterns validated
  - BEAM: `{:ok, value}`, `pid()`, supervisor patterns validated
  - Systems: `T*`, smart pointer patterns validated
  - Apple: `@property (weak)`, ARC patterns validated
- [x] **Language-specific patterns (3,293)** - Verified within families

### Characteristic Verification

- [x] **Type system characteristics** - Match Phase 0 type mappings
  - 6,026 type_mapping patterns (83.8%) validate type system docs
  - Static vs dynamic distinction clear in patterns
- [x] **Memory model characteristics** - Match ownership patterns
  - Systems family: ownership vs manual patterns distinct
  - Apple family: ARC patterns (weak/strong) captured
- [x] **Concurrency characteristics** - Match async/actor patterns
  - BEAM: Actor patterns (`pid()`, supervisor) validated
  - 48 concurrency patterns extracted (underextracted)

### Validation Summary

| Family | Patterns | Gaps | Status |
|--------|----------|------|--------|
| ML-FP | 5,597 | 256 | ✓ Validated |
| Dynamic | 2,449 | 121 | ✓ Validated |
| BEAM | 2,018 | 88 | ✓ Validated |
| Systems | 2,108 | 93 | ✓ Validated |
| LISP | 1,259 | 57 | ✓ Validated |
| Managed-OOP | 513 | 13 | ✓ Validated |
| Apple | 446 | 12 | ✓ Validated |

### Identified Gaps

- **Idioms underextracted**: 214 vs expected 400+ (code blocks not fully parsed)
- **Negative patterns underextracted**: 29 vs expected 250+ (prose sections vary)
- **Concurrency patterns limited**: 48 patterns for complex async/actor systems

## Detailed Feature Dimensions (Task 1.2)

Each paradigm family has been documented with 5 dimension categories:

### Dimension Categories

| Category | Attributes | Description |
|----------|------------|-------------|
| **typing** | strength, inference, generics, nullability | Type system characteristics |
| **memory** | model, mutability, allocation | Memory management approach |
| **control** | structured, effects, async | Control flow and effect handling |
| **data** | primitives, composites, abstraction | Data type support |
| **meta** | macros, reflection, codegen | Metaprogramming capabilities |

### Family Dimension Summary

| Family | Typing | Memory | Effects | Async | Abstraction |
|--------|--------|--------|---------|-------|-------------|
| ML-FP | static/global | gc/immutable | monadic | green-threads | typeclasses |
| BEAM | dynamic | gc/immutable | exceptions | actors | modules |
| LISP | dynamic | gc/varies | exceptions | varies | protocols |
| Systems | static/local | varies | varies | varies | traits |
| Managed-OOP | static/local | gc/mutable | exceptions | async-await | classes |
| Dynamic | dynamic | gc/mutable | exceptions | varies | classes |
| Apple | varies | rc/mutable | varies | gcd/async | protocols |

### Subtype Variations

Key families have significant subtype variations:

**ML-FP:**

- **pure** (Haskell, Elm): Enforced immutability, monadic effects, global inference
- **hybrid** (Scala, F#): Mutable available, mixed effects, bidirectional inference

**Systems:**

- **ownership** (Rust): Borrow checker, Result types, async/await
- **manual** (C, C++): Manual memory, exceptions/codes, threads

**Apple:**

- **legacy** (Obj-C): Dynamic typing, exceptions, GCD
- **modern** (Swift): Static typing, throws, async/await

### Graduated Scale Reference

For Task 1.3 comparison matrices, characteristics map to a graduated scale:

| Scale | Meaning | Example |
|-------|---------|---------|
| `none` | Feature not available | No null safety in C |
| `limited` | Basic support, restrictions | Manual memory in C |
| `partial` | Supported with gaps | Gradual typing in TypeScript |
| `full` | Complete, standard patterns | GC in Java |
| `native` | First-class, idiomatic | Actors in Erlang |

## Validation Sampling Results (Task 1.6)

Full report: [validation-sampling.md](validation-sampling.md)

| Family | Skills Reviewed | Type System | Memory Model | Difficulty | Status |
|--------|-----------------|-------------|--------------|------------|--------|
| ML-FP | python-haskell, elixir-roc, fsharp-scala | ✓ | ✓ | ✓ | **Validated** |
| Dynamic | python-haskell, typescript-rust | ✓ | ✓ | ✓ | **Validated** |
| BEAM | elixir-roc, python-elixir | ✓ | ✓ | ✓ | **Validated** |
| Systems | java-rust, python-rust | ✓ | ✓ | ✓ | **Validated** |
| LISP | clojure-fsharp, clojure-haskell | ✓ | ✓ | ✓ | **Validated** |
| Apple | objc-swift | ✓ | ✓ | ✓ | **Validated** |

**Result:** All 6 high-priority families validated. No structural changes required.

## Data Files

| File | Description |
|------|-------------|
| `data/families/taxonomy.yaml` | Family taxonomy and language mappings |
| `data/families/dimensions.yaml` | Detailed feature dimensions (Task 1.2) |
| `data/families.sql` | SQL schema and data (pending) |
| `analysis/family-priority.md` | Prioritization rationale (Task 1.0) |
| `analysis/phase0-crossref.md` | Phase 0 cross-reference analysis (Task 1.5) |
| `analysis/validation-sampling.md` | Skill validation sampling (Task 1.6) |

## Notes

- Go is categorized under Systems despite having GC (it's a systems language by design)
- TypeScript is both Dynamic (base) and Gradual-Typing (feature)
- Scala can be in both ML-FP (paradigm) and Actors (with Akka)
- Subtype information is critical for accurate ML-FP conversions
