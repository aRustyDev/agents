# Gleam

> Statically typed functional language for the BEAM with friendly errors and excellent tooling.

## Overview

Gleam is a statically typed functional programming language created by Louis Pilfold, first released in 2019. It runs on the Erlang VM (BEAM) and compiles to JavaScript, combining the reliability of the BEAM ecosystem with the safety of a type system.

Gleam offers a familiar syntax inspired by Rust and Elm, with static typing, exhaustive pattern matching, and no runtime exceptions. It maintains full interoperability with Erlang and Elixir, allowing gradual adoption in existing BEAM projects.

The language emphasizes developer experience with fast compilation, helpful error messages, and integrated tooling. It's particularly suited for building reliable concurrent systems that need the BEAM's fault tolerance with compile-time type safety.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | BEAM | Erlang VM, OTP compatible |
| Secondary Family | ML-FP | Static types, ADTs |
| Subtype | typed-beam | Type-safe BEAM alternative |

See: [BEAM Family](../language-families/beam.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 0.16 | 2021-09 | Use expressions |
| 0.25 | 2023-01 | Bit arrays, string prefixes |
| 0.32 | 2023-11 | Label shorthand |
| 1.0 | 2024-03 | First stable release |

## Feature Profile

### Type System

- **Strength:** strong (static, sound)
- **Inference:** bidirectional (Hindley-Milner based)
- **Generics:** parametric (type variables)
- **Nullability:** explicit (Option, Result types)

### Memory Model

- **Management:** gc (BEAM per-process GC)
- **Mutability:** immutable (all data immutable)
- **Allocation:** per-process heap

### Control Flow

- **Structured:** case, if (expression), use
- **Effects:** Result type (no exceptions in Gleam code)
- **Async:** BEAM processes, OTP

### Data Types

- **Primitives:** Int, Float, Bool, String, BitArray
- **Composites:** tuples, custom types (ADTs), records (labeled tuples)
- **Collections:** List, Dict, Set (via gleam_stdlib)
- **Abstraction:** modules, opaque types

### Metaprogramming

- **Macros:** none
- **Reflection:** none (BEAM reflection available via FFI)
- **Code generation:** none

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | gleam (Hex) | Built-in |
| Build System | gleam build | Built-in |
| LSP | gleam lsp | Built-in, excellent |
| Formatter | gleam format | Built-in |
| Linter | none (type system catches most) | — |
| REPL | gleam run (scripting) | No interactive REPL yet |
| Test Framework | gleeunit | Standard |

## Syntax Patterns

```gleam
// Function definition
pub fn greet(name: String, times: Int) -> String {
  string.repeat("Hello, " <> name <> "! ", times)
}

// Generic function
pub fn identity(value: a) -> a {
  value
}

// Function with labeled arguments
pub fn create_user(id id: String, name name: String) -> User {
  User(id: id, name: name, email: None)
}

// Custom type (record)
pub type User {
  User(id: String, name: String, email: Option(String))
}

// Custom type (ADT / sum type)
pub type Result(value, error) {
  Ok(value)
  Error(error)
}

pub type Shape {
  Circle(radius: Float)
  Rectangle(width: Float, height: Float)
}

// Pattern matching
pub fn area(shape: Shape) -> Float {
  case shape {
    Circle(radius) -> float.pi *. radius *. radius
    Rectangle(width, height) -> width *. height
  }
}

// Pattern matching with guards
pub fn describe(n: Int) -> String {
  case n {
    0 -> "zero"
    n if n > 0 -> "positive"
    _ -> "negative"
  }
}

// Result handling
pub fn divide(a: Int, b: Int) -> Result(Int, String) {
  case b {
    0 -> Error("Division by zero")
    _ -> Ok(a / b)
  }
}

// Use expression (monadic binding)
pub fn process(input: String) -> Result(Output, Error) {
  use parsed <- result.try(parse(input))
  use validated <- result.try(validate(parsed))
  use transformed <- result.try(transform(validated))
  Ok(transformed)
}

// Pipeline operator
pub fn process_numbers(numbers: List(Int)) -> Int {
  numbers
  |> list.filter(fn(x) { x > 0 })
  |> list.map(fn(x) { x * 2 })
  |> list.fold(0, fn(acc, x) { acc + x })
}

// Anonymous function
let double = fn(x) { x * 2 }

// Labeled tuple access
let user = User(id: "1", name: "Alice", email: None)
let name = user.name

// Option handling
pub fn get_email(user: User) -> String {
  case user.email {
    Some(email) -> email
    None -> "no-email@example.com"
  }
}

// List patterns
pub fn sum(numbers: List(Int)) -> Int {
  case numbers {
    [] -> 0
    [first, ..rest] -> first + sum(rest)
  }
}

// Bit arrays (binary data)
pub fn parse_header(data: BitArray) -> Result(Header, Error) {
  case data {
    <<version:8, length:16, payload:bytes>> ->
      Ok(Header(version, length, payload))
    _ -> Error(InvalidHeader)
  }
}

// External function (FFI to Erlang)
@external(erlang, "erlang", "system_time")
pub fn system_time() -> Int

// Module import
import gleam/io
import gleam/list.{filter, map}
import gleam/option.{type Option, None, Some}

// Type alias
pub type UserId = String

// Opaque type
pub opaque type Counter {
  Counter(value: Int)
}

pub fn new() -> Counter {
  Counter(0)
}

pub fn increment(counter: Counter) -> Counter {
  Counter(counter.value + 1)
}
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| No macros | minor | Use code generation, FFI to Elixir |
| No interactive REPL | minor | Use gleam run for scripts |
| Smaller ecosystem than Elixir | moderate | Use Erlang/Elixir libraries via FFI |
| No type classes | moderate | Use module patterns |
| Young language | moderate | Growing rapidly, 1.0 released |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 0 | — |
| As Target | 0 | — |

**Note:** Not in current convert-* skills. Natural target for typed BEAM development.

## Idiomatic Patterns

### Custom Types → ADTs

```gleam
// Gleam: custom type
pub type Option(a) {
  Some(a)
  None
}

// IR equivalent: enum ADT
// enum Option<T> { Some(T), None }
```

### Use Expression → Monadic Bind

```gleam
// Gleam: use expression
use value <- result.try(get_value())
Ok(process(value))

// IR equivalent: flatMap/bind
// get_value().flatMap(value => Ok(process(value)))
```

### Pipeline → Method Chain

```gleam
// Gleam: pipeline
x |> f |> g |> h

// IR equivalent: method chain or composition
// h(g(f(x)))
```

### FFI → External Functions

```gleam
// Gleam: external function
@external(erlang, "lists", "reverse")
pub fn reverse(list: List(a)) -> List(a)

// IR equivalent: FFI binding
// extern "erlang" fn reverse<T>(list: List<T>) -> List<T>
```

## Related Languages

- **Influenced by:** Elm, Rust, Erlang, OCaml
- **Influenced:** (New language, influence TBD)
- **Compiles to:** BEAM bytecode, JavaScript
- **FFI compatible:** Erlang (native), Elixir, JavaScript

## Sources

- [Gleam Documentation](https://gleam.run/documentation/)
- [Gleam Language Tour](https://tour.gleam.run/)
- [Gleam Standard Library](https://hexdocs.pm/gleam_stdlib/)
- [Gleam Packages (Hex)](https://hex.pm/packages?search=gleam)

## See Also

- [BEAM Family](../language-families/beam.md)
- [Elixir](elixir.md) - Dynamic BEAM alternative
- [Erlang](erlang.md) - BEAM foundation
- [Elm](elm.md) - Similar philosophy for web
