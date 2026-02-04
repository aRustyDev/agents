# Rust

> Systems programming language focused on safety, concurrency, and performance without garbage collection.

## Overview

Rust is a systems programming language developed by Mozilla Research, first released in 2010 and reaching 1.0 in 2015. It provides memory safety without garbage collection through its ownership system, enabling high-performance code with strong safety guarantees.

The language combines low-level control over memory and hardware with high-level abstractions like pattern matching, traits, and algebraic data types. Rust's borrow checker enforces memory safety at compile time, eliminating entire classes of bugs like null pointer dereferences, data races, and use-after-free.

Rust has gained adoption in systems programming, WebAssembly, CLI tools, and increasingly in web services, with major companies using it for performance-critical infrastructure.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | Systems | Low-level control, no GC |
| Secondary Family | ML-FP | Pattern matching, traits, ADTs |
| Subtype | ownership | Unique ownership model |

See: [Systems Family](../language-families/systems.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 1.0 | 2015-05 | Initial stable release |
| 1.18 | 2017-06 | impl Trait in return position |
| 1.26 | 2018-05 | impl Trait in argument position |
| 1.36 | 2019-07 | Future and async/await foundations |
| 1.39 | 2019-11 | async/await stabilized |
| 1.65 | 2022-11 | GATs (Generic Associated Types) |
| 1.75 | 2023-12 | async fn in traits |

## Feature Profile

### Type System

- **Strength:** strong (static, affine types for ownership)
- **Inference:** bidirectional (local, explicit for functions)
- **Generics:** bounded (trait bounds, associated types, GATs)
- **Nullability:** explicit (Option<T>, no null)

### Memory Model

- **Management:** ownership (borrow checker, no GC)
- **Mutability:** default-immutable (mut keyword required)
- **Allocation:** stack-default (Box for heap, explicit)
- **Lifetimes:** explicit (compile-time verified)

### Control Flow

- **Structured:** if-else, loop, while, for, match
- **Effects:** Result<T,E> (no exceptions)
- **Async:** async/await (executor-agnostic)

### Data Types

- **Primitives:** i8-i128, u8-u128, f32, f64, bool, char, ()
- **Composites:** structs, enums (ADTs), tuples
- **Collections:** Vec, HashMap, HashSet, BTreeMap, BTreeSet
- **Abstraction:** traits, modules, crates

### Metaprogramming

- **Macros:** procedural and declarative (macro_rules!)
- **Reflection:** limited (TypeId, Any trait)
- **Code generation:** derive macros, build.rs

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | Cargo | Built-in, excellent |
| Build System | Cargo | Unified tool |
| LSP | rust-analyzer | Excellent IDE support |
| Formatter | rustfmt | Standard, opinionated |
| Linter | clippy | Extensive, helpful |
| REPL | evcxr | Third-party |
| Test Framework | built-in | #[test], cargo test |

## Syntax Patterns

```rust
// Function definition
fn greet(name: &str, times: usize) -> String {
    format!("Hello, {}! ", name).repeat(times)
}

// Generic function with trait bounds
fn identity<T>(value: T) -> T {
    value
}

fn process<T: Clone + Debug>(item: T) -> T {
    println!("{:?}", item);
    item.clone()
}

// Async function
async fn fetch_data(url: &str) -> Result<Response, HttpError> {
    let response = client.get(url).await?;
    if response.status() != StatusCode::OK {
        return Err(HttpError::Status(response.status()));
    }
    Ok(response)
}

// Struct definition
#[derive(Debug, Clone)]
struct User {
    id: String,
    name: String,
    email: Option<String>,
}

// Enum (ADT)
enum Result<T, E> {
    Ok(T),
    Err(E),
}

enum Shape {
    Circle { radius: f64 },
    Rectangle { width: f64, height: f64 },
}

// Pattern matching
fn area(shape: &Shape) -> f64 {
    match shape {
        Shape::Circle { radius } => std::f64::consts::PI * radius * radius,
        Shape::Rectangle { width, height } => width * height,
    }
}

// Trait definition
trait Show {
    fn show(&self) -> String;
}

impl Show for User {
    fn show(&self) -> String {
        format!("User({})", self.name)
    }
}

// Trait with associated types
trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}

// Error handling with Result
fn divide(a: i64, b: i64) -> Result<i64, &'static str> {
    if b == 0 {
        Err("Division by zero")
    } else {
        Ok(a / b)
    }
}

// Ownership and borrowing
fn process_string(s: String) -> String {  // Takes ownership
    s.to_uppercase()
}

fn read_string(s: &str) -> usize {  // Borrows immutably
    s.len()
}

fn modify_string(s: &mut String) {  // Borrows mutably
    s.push_str(" modified");
}

// Iterator combinators
let numbers: Vec<i32> = vec![1, 2, 3, 4, 5];
let sum: i32 = numbers
    .iter()
    .filter(|&&x| x % 2 == 0)
    .map(|&x| x * 2)
    .sum();

// Closure
let add = |a: i32, b: i32| a + b;
let capture = |x| x + captured_value;

// Lifetime annotations
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| Steep learning curve (borrow checker) | high | Start with owned types, learn borrowing gradually |
| Long compile times | moderate | Use cargo check, incremental compilation |
| Orphan rules limit trait impls | moderate | Newtype pattern, wrapper types |
| No inheritance (by design) | minor | Composition, trait objects |
| Async ecosystem fragmentation | moderate | Choose runtime (tokio/async-std) early |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 0 | — |
| As Target | 6 | python-rust, c-rust, cpp-rust, golang-rust, java-rust, typescript-rust |

**Note:** Primary target for performance-critical conversions. Ownership concepts require careful mapping.

## Idiomatic Patterns

### Ownership → Move/Copy Semantics

```rust
// Rust: ownership transfer
let s1 = String::from("hello");
let s2 = s1;  // s1 moved to s2
// s1 no longer valid

// IR equivalent: explicit move annotation
// let s2 = move s1;
```

### Traits → Type Classes/Interfaces

```rust
// Rust: trait bound
fn process<T: Display + Clone>(item: T)

// IR equivalent: type class constraint
// fn process<T: (Display & Clone)>(item: T)
```

### Result → Error Handling

```rust
// Rust: Result with ?
fn read_file(path: &str) -> Result<String, io::Error> {
    let contents = fs::read_to_string(path)?;
    Ok(contents)
}

// IR equivalent: do-notation or try
// contents <- readFile path
```

### Pattern Matching → Destructuring

```rust
// Rust: match with guards
match value {
    Some(x) if x > 0 => positive(x),
    Some(x) => non_positive(x),
    None => default(),
}

// IR equivalent: case with guards
// case value of Just x | x > 0 -> ...
```

## Related Languages

- **Influenced by:** C++, Haskell, ML, Erlang, Cyclone
- **Influenced:** Swift (ownership ideas), Zig, Carbon
- **Compiles to:** Native (LLVM), WebAssembly
- **FFI compatible:** C (native ABI)

## Sources

- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [Rust Reference](https://doc.rust-lang.org/reference/)
- [Rustonomicon](https://doc.rust-lang.org/nomicon/)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)

## See Also

- [Systems Family](../language-families/systems.md)
- [C](c.md) - FFI target
- [C++](cpp.md) - Comparison
- [Go](golang.md) - GC alternative
