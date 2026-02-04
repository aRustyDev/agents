# Roc

> Fast, friendly, functional language with no runtime exceptions and platform-based effects.

## Overview

Roc is a functional programming language created by Richard Feldman (creator of elm-test), currently in development with first alpha in 2022. It aims to be a fast, friendly, functional language that compiles to efficient machine code while guaranteeing no runtime exceptions.

Roc's distinguishing feature is its "platforms" system, which cleanly separates pure application code from effectful platform code. Applications are pure functions that describe what effects to perform, while platforms handle the actual execution. This enables the same application logic to run on different platforms (CLI, web server, WASM).

The language draws from Elm's philosophy of no exceptions and friendly errors, while adding performance focus and broader applicability beyond web frontends.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | ML-FP | Pure FP with effects via platforms |
| Secondary Family | — | No OOP |
| Subtype | platform-effects | Unique effects model |

See: [ML-FP Family](../language-families/ml-fp.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| Pre-alpha | 2022 | Initial public release |
| Alpha | 2023 | Stabilizing syntax, platforms |

**Note:** Roc is pre-1.0 and syntax/features may change.

## Feature Profile

### Type System

- **Strength:** strong (static, sound)
- **Inference:** global (Hindley-Milner based)
- **Generics:** parametric (abilities for ad-hoc polymorphism)
- **Nullability:** explicit (Result for errors)

### Memory Model

- **Management:** gc (reference counting with cycle collection)
- **Mutability:** immutable (all values immutable)
- **Allocation:** arena-based (efficient allocation)

### Control Flow

- **Structured:** if-then-else, when-is (pattern matching)
- **Effects:** platform-managed (no exceptions, no IO monad)
- **Async:** Task (platform-provided)

### Data Types

- **Primitives:** I8-I128, U8-U128, F32, F64, Bool, Str
- **Composites:** records, tags (sum types), tuples
- **Collections:** List, Dict, Set
- **Abstraction:** modules, abilities (type classes)

### Metaprogramming

- **Macros:** none
- **Reflection:** none
- **Code generation:** none

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | roc (built-in) | URL-based packages |
| Build System | roc build | Built-in |
| LSP | roc (built-in) | Integrated |
| Formatter | roc format | Built-in |
| Linter | none (type system catches most) | — |
| REPL | roc repl | Built-in |
| Test Framework | roc test | Built-in |

## Syntax Patterns

```roc
# Function definition
greet : Str, U64 -> Str
greet = \name, times ->
    Str.repeat "Hello, $(name)! " times

# Generic function
identity : a -> a
identity = \x -> x

# Record type (anonymous)
User : { id : Str, name : Str, email : Result Str [NoEmail] }

# Tag union (sum type)
Result ok err : [Ok ok, Err err]

Shape : [Circle F64, Rectangle F64 F64]

# Pattern matching (when-is)
area : Shape -> F64
area = \shape ->
    when shape is
        Circle r -> Num.pi * r * r
        Rectangle w h -> w * h

# Record creation
createUser : Str, Str -> User
createUser = \id, name ->
    { id, name, email: Err NoEmail }

# Record update
updateName : User, Str -> User
updateName = \user, newName ->
    { user & name: newName }

# Error handling with Result
divide : I64, I64 -> Result I64 [DivByZero]
divide = \a, b ->
    if b == 0 then
        Err DivByZero
    else
        Ok (a // b)

# Chaining with Result
processNumbers : List I64 -> Result I64 [Empty, DivByZero]
processNumbers = \numbers ->
    numbers
    |> List.first
    |> Result.mapErr \_ -> Empty
    |> Result.try \first ->
        divide first 2

# Pipeline style
sumEvenDoubled : List I64 -> I64
sumEvenDoubled = \numbers ->
    numbers
    |> List.keepIf \x -> x % 2 == 0
    |> List.map \x -> x * 2
    |> List.sum

# Abilities (type classes)
Hash implements
    hash : a -> U64 where a implements Hash

# Platform application entry point
main : Task {} *
main =
    Stdout.line "Hello, World!"

# HTTP example (with basic-cli platform)
fetchData : Str -> Task Str [HttpErr Http.Error]
fetchData = \url ->
    Http.get url
    |> Task.mapErr HttpErr

# List operations
users : List User
users = [
    { id: "1", name: "Alice", email: Ok "alice@example.com" },
    { id: "2", name: "Bob", email: Err NoEmail },
]

validEmails : List Str
validEmails =
    users
    |> List.keepOks .email
    |> List.keepOks \x -> x

# Destructuring
getCoordinates : { x : F64, y : F64 }* -> (F64, F64)
getCoordinates = \{ x, y } -> (x, y)

# Optional record fields (with default)
Config : { timeout ? U64, retries ? U64 }
defaultConfig : Config
defaultConfig = { timeout: 30, retries: 3 }
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| Pre-1.0, API may change | high | Track language updates, use stable features |
| Limited ecosystem (new language) | moderate | Build needed libraries, use FFI |
| No exceptions (by design) | minor | Use Result/tags for all errors |
| Limited platform selection | moderate | Create custom platforms as needed |
| Documentation still developing | moderate | Reference source code, community Discord |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 1 | roc-scala |
| As Target | 7 | python-roc, elixir-roc, clojure-roc, elm-roc, erlang-roc, fsharp-roc, haskell-roc |

**Note:** Primary target for FP conversions - represents modern pure FP approach.

## Idiomatic Patterns

### Tag Unions → ADTs

```roc
# Roc: tag union
[Ok value, Err error]

# IR equivalent: enum
# enum Result<T, E> { Ok(T), Err(E) }
```

### Abilities → Type Classes

```roc
# Roc: ability
Eq implements
    eq : a, a -> Bool where a implements Eq

# IR equivalent: trait
# trait Eq { fn eq(&self, other: &Self) -> bool }
```

### Platform Effects → Effect System

```roc
# Roc: Task-based effects
main : Task {} *
main =
    Stdout.line "Hello"

# IR equivalent: IO monad or effect type
# fn main() -> IO<()>
```

### Backpassing → Continuation Style

```roc
# Roc: backpassing syntax
result <-
    fetchData url
    |> Task.await

# IR equivalent: monadic bind
# fetchData(url).flatMap(result => ...)
```

## Related Languages

- **Influenced by:** Elm, Rust (borrow ideas), Haskell
- **Influenced:** (New language, influence TBD)
- **Compiles to:** Native (LLVM), WASM
- **FFI compatible:** C (native ABI)

## Sources

- [Roc Documentation](https://www.roc-lang.org/docs)
- [Roc Tutorial](https://www.roc-lang.org/tutorial)
- [Roc Examples](https://www.roc-lang.org/examples)
- [Roc Builtins](https://www.roc-lang.org/builtins)

## See Also

- [ML-FP Family](../language-families/ml-fp.md)
- [Elm](elm.md) - Philosophical predecessor
- [Haskell](haskell.md) - Type system influence
- [Rust](rust.md) - Performance focus comparison
