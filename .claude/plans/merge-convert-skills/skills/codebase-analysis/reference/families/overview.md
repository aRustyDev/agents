# Language Family Overview

Languages are grouped into families based on shared paradigms, type systems, and patterns. Understanding families helps predict conversion complexity.

## Family Classification

### ML/FP Family

**Languages**: Haskell, OCaml, F#, Scala, Roc, Elm, PureScript

**Characteristics**:
- Strong static typing
- Algebraic data types
- Pattern matching
- Immutability by default
- Expression-oriented
- Higher-order functions
- Type inference

**Signature Patterns**:
- `Option`/`Maybe` for nullability
- `Result`/`Either` for errors
- Pattern matching for control flow
- Curried functions
- Type classes/traits

**Conversion Notes**:
- Converts well within family
- HKT may need monomorphization for OOP targets
- Pattern matching → switch/if-else
- Immutability may need explicit enforcement

### Systems Family

**Languages**: Rust, C, C++, Zig, Ada

**Characteristics**:
- Manual or ownership-based memory
- Low-level control
- Zero-cost abstractions
- Explicit lifetimes
- Performance critical

**Signature Patterns**:
- Ownership and borrowing (Rust)
- Pointers and references
- RAII patterns
- Explicit memory allocation
- Unsafe blocks

**Conversion Notes**:
- Ownership → GC or manual tracking
- Lifetimes → N/A in GC languages
- Unsafe → Trust runtime safety
- Performance may degrade with GC

### BEAM Family

**Languages**: Erlang, Elixir, Gleam

**Characteristics**:
- Actor model concurrency
- Message passing
- Fault tolerance
- Hot code loading
- Pattern matching
- Dynamic (Erlang/Elixir) or static (Gleam)

**Signature Patterns**:
- Processes and mailboxes
- `receive` blocks
- Supervision trees
- OTP behaviors
- Binary pattern matching

**Conversion Notes**:
- Actors → threads + queues or async
- Supervision → try/catch + restart
- Hot loading → restart required
- Binary patterns → manual parsing

### Lisp Family

**Languages**: Clojure, Common Lisp, Scheme, Racket, Emacs Lisp

**Characteristics**:
- Homoiconic (code as data)
- Macro systems
- Dynamic typing
- REPL-driven development
- Persistent data structures
- Multi-paradigm

**Signature Patterns**:
- S-expressions
- Quoting and unquoting
- Macros
- Multi-methods
- Atoms and refs (Clojure)

**Conversion Notes**:
- Macros → manual expansion
- Homoiconicity → standard AST
- Dynamic typing → type hints
- Persistent data → immutable copies

### Managed OOP Family

**Languages**: Java, C#, Kotlin, Swift

**Characteristics**:
- Class-based OOP
- Garbage collected
- Static typing with inference
- Generics
- Null safety (Kotlin, Swift)

**Signature Patterns**:
- Class hierarchies
- Interfaces
- Properties and getters/setters
- Annotations/attributes
- Nullable types

**Conversion Notes**:
- Maps well to each other
- Null handling differences
- Generic variance differences
- Platform-specific APIs

### Dynamic Family

**Languages**: Python, Ruby, JavaScript, PHP, Perl

**Characteristics**:
- Dynamic typing
- Runtime flexibility
- Duck typing
- Metaprogramming
- Interpreted

**Signature Patterns**:
- No type annotations (optional in some)
- Runtime type checks
- Monkey patching
- Decorators/method missing
- First-class everything

**Conversion Notes**:
- Need type inference for static targets
- Duck typing → interface extraction
- Metaprogramming → static generation
- Runtime features may not convert

## Family Compatibility Matrix

Conversion complexity between families:

|  | ML/FP | Systems | BEAM | Lisp | OOP | Dynamic |
|--|-------|---------|------|------|-----|---------|
| **ML/FP** | Low | Medium | Low | Low | Medium | High |
| **Systems** | Medium | Low | High | Medium | Medium | Medium |
| **BEAM** | Medium | High | Low | Medium | High | Medium |
| **Lisp** | Low | Medium | Medium | Low | Medium | Low |
| **OOP** | Medium | Medium | High | Medium | Low | Low |
| **Dynamic** | High | High | Medium | Low | Low | Low |

**Low**: Direct pattern mappings exist
**Medium**: Some patterns need adaptation
**High**: Significant semantic gaps

## Cross-Family Pattern Mapping

### Error Handling

| Family | Primary Pattern | IR Mapping |
|--------|-----------------|------------|
| ML/FP | `Result[T,E]` | `ResultType` |
| Systems | `Result<T,E>` | `ResultType` |
| BEAM | `{:ok, val}` | `ResultType` |
| Lisp | Conditions | `ExceptionAnnotation` |
| OOP | Exceptions | `ExceptionAnnotation` |
| Dynamic | Exceptions | `ExceptionAnnotation` |

### Nullability

| Family | Primary Pattern | IR Mapping |
|--------|-----------------|------------|
| ML/FP | `Option[T]` | `OptionType` |
| Systems | `Option<T>` | `OptionType` |
| BEAM | `nil` or tagged | `NullableType` |
| Lisp | `nil` | `NullableType` |
| OOP | `T?` | `NullableType` |
| Dynamic | `None`/`null` | `NullableType` |

### Concurrency

| Family | Primary Pattern | IR Mapping |
|--------|-----------------|------------|
| ML/FP | Async/Effects | `AsyncAnnotation` |
| Systems | Threads/Async | `ThreadAnnotation` |
| BEAM | Actors | `ActorAnnotation` |
| Lisp | Agents/Refs | `ConcurrencyAnnotation` |
| OOP | Threads/Async | `AsyncAnnotation` |
| Dynamic | Async/Callbacks | `AsyncAnnotation` |

## Family-Specific IR Extensions

Each family may enable additional IR constructs:

```yaml
ir_extensions:
  ml_fp:
    - PatternMatch
    - ADTDef
    - TypeClass
    - HigherKindedType

  systems:
    - Ownership
    - Lifetime
    - UnsafeBlock
    - ConstGeneric

  beam:
    - Actor
    - Message
    - Supervision
    - BinaryMatch

  lisp:
    - Quote
    - MacroDef
    - MultiMethod
    - PersistentData

  oop:
    - Class
    - Interface
    - Inheritance
    - Property

  dynamic:
    - DuckType
    - Decorator
    - Metaclass
    - DynamicProperty
```
