---
name: lang-rust-dev
description: Foundational Rust patterns covering core syntax, traits, generics, lifetimes, and common idioms. Use when writing Rust code, understanding ownership basics, working with Option/Result, or needing guidance on which specialized Rust skill to use. This is the entry point for Rust development.
---

# Rust Fundamentals

Foundational Rust patterns and core language features. This skill serves as both a reference for common patterns and an index to specialized Rust skills.

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Rust Skill Hierarchy                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                    ┌───────────────────┐                        │
│                    │   lang-rust-dev   │ ◄── You are here       │
│                    │   (foundation)    │                        │
│                    └─────────┬─────────┘                        │
│                              │                                  │
│     ┌────────────┬───────────┼───────────┬────────────┐        │
│     │            │           │           │            │        │
│     ▼            ▼           ▼           ▼            ▼        │
│ ┌────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐   │
│ │ errors │ │  cargo   │ │library │ │ memory  │ │ profiling│   │
│ │  -dev  │ │   -dev   │ │  -dev  │ │  -eng   │ │   -eng   │   │
│ └────────┘ └──────────┘ └────────┘ └─────────┘ └──────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**This skill covers:**
- Core syntax (structs, enums, match, impl blocks)
- Traits and generics basics
- Lifetime fundamentals
- Option and Result patterns
- Iterators and closures
- Common idioms and conventions

**This skill does NOT cover (see specialized skills):**
- Error handling with error-stack → `lang-rust-errors-dev`
- Cargo.toml and dependencies → `lang-rust-cargo-dev`
- Library/crate publishing → `lang-rust-library-dev`
- Documentation patterns → `lang-rust-docs-dev`
- Memory safety engineering → `lang-rust-memory-eng`
- Benchmarking → `lang-rust-benchmarking-eng`
- Profiling/debugging → `lang-rust-profiling-eng`

---

## Quick Reference

| Task | Pattern |
|------|---------|
| Create struct | `struct Name { field: Type }` |
| Create enum | `enum Name { Variant1, Variant2(T) }` |
| Implement trait | `impl Trait for Type { ... }` |
| Generic function | `fn name<T: Trait>(x: T) -> T` |
| Lifetime annotation | `fn name<'a>(x: &'a str) -> &'a str` |
| Error propagation | `let x = fallible()?;` |
| Pattern match | `match value { Pattern => expr }` |
| Iterate | `for item in collection { ... }` |
| Map/filter | `iter.map(\|x\| ...).filter(\|x\| ...)` |

---

## Skill Routing

Use this table to find the right specialized skill:

| When you need to... | Use this skill |
|---------------------|----------------|
| Handle errors with Result/Report types | `lang-rust-errors-dev` |
| Configure Cargo.toml, add dependencies | `lang-rust-cargo-dev` |
| Design public APIs, publish crates | `lang-rust-library-dev` |
| Write documentation, rustdoc | `lang-rust-docs-dev` |
| Understand ownership deeply, unsafe code | `lang-rust-memory-eng` |
| Write benchmarks, measure performance | `lang-rust-benchmarking-eng` |
| Profile code, find bottlenecks | `lang-rust-profiling-eng` |

---

## Core Types

### Structs

```rust
// Named fields
struct User {
    name: String,
    email: String,
    age: u32,
}

// Tuple struct
struct Point(f64, f64);

// Unit struct
struct Marker;

// Creating instances
let user = User {
    name: String::from("Alice"),
    email: String::from("alice@example.com"),
    age: 30,
};

// Struct update syntax
let user2 = User {
    email: String::from("bob@example.com"),
    ..user  // Take remaining fields from user
};

// Destructuring
let User { name, email, .. } = user2;
```

### Enums

```rust
// Simple enum
enum Direction {
    North,
    South,
    East,
    West,
}

// Enum with data
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(u8, u8, u8),
}

// Using enums
let msg = Message::Move { x: 10, y: 20 };

match msg {
    Message::Quit => println!("Quit"),
    Message::Move { x, y } => println!("Move to {x}, {y}"),
    Message::Write(text) => println!("Write: {text}"),
    Message::ChangeColor(r, g, b) => println!("Color: {r},{g},{b}"),
}
```

### Option and Result

```rust
// Option: value that might not exist
fn find_user(id: u32) -> Option<User> {
    if id == 1 {
        Some(User { /* ... */ })
    } else {
        None
    }
}

// Using Option
match find_user(1) {
    Some(user) => println!("Found: {}", user.name),
    None => println!("Not found"),
}

// Option methods
let name = find_user(1)
    .map(|u| u.name)
    .unwrap_or_else(|| String::from("Anonymous"));

// Result: operation that might fail
fn parse_config(path: &str) -> Result<Config, ConfigError> {
    let content = std::fs::read_to_string(path)?;
    let config = serde_json::from_str(&content)?;
    Ok(config)
}

// Error propagation with ?
fn process() -> Result<(), Error> {
    let config = parse_config("config.json")?;  // Returns early on error
    // ... use config
    Ok(())
}
```

---

## Pattern Matching

### Match Expressions

```rust
let x = 5;

match x {
    1 => println!("one"),
    2 | 3 => println!("two or three"),
    4..=6 => println!("four through six"),
    n if n > 10 => println!("greater than ten: {n}"),
    _ => println!("something else"),
}

// Destructuring in match
let point = (3, 4);
match point {
    (0, 0) => println!("origin"),
    (x, 0) => println!("on x-axis at {x}"),
    (0, y) => println!("on y-axis at {y}"),
    (x, y) => println!("at ({x}, {y})"),
}
```

### If Let and Let Else

```rust
// if let: match single pattern
if let Some(user) = find_user(1) {
    println!("Found: {}", user.name);
}

// let else: match or diverge
fn get_name(id: u32) -> String {
    let Some(user) = find_user(id) else {
        return String::from("Unknown");
    };
    user.name
}
```

---

## Traits

### Defining Traits

```rust
trait Summary {
    // Required method
    fn summarize(&self) -> String;

    // Default implementation
    fn preview(&self) -> String {
        format!("{}...", &self.summarize()[..50])
    }
}
```

### Implementing Traits

```rust
struct Article {
    title: String,
    content: String,
}

impl Summary for Article {
    fn summarize(&self) -> String {
        format!("{}: {}", self.title, self.content)
    }
}

// Use the trait
let article = Article { /* ... */ };
println!("{}", article.summarize());
```

### Common Standard Traits

| Trait | Purpose | Derive? |
|-------|---------|---------|
| `Debug` | Debug formatting `{:?}` | Yes |
| `Clone` | Explicit duplication | Yes |
| `Copy` | Implicit copying | Yes (if all fields Copy) |
| `Default` | Default value | Yes |
| `PartialEq` / `Eq` | Equality comparison | Yes |
| `PartialOrd` / `Ord` | Ordering | Yes |
| `Hash` | Hash for HashMap keys | Yes |
| `Display` | User-facing formatting | No |
| `From` / `Into` | Type conversion | No |

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash, Default)]
struct Config {
    name: String,
    value: i32,
}
```

### Trait Bounds

```rust
// Function with trait bound
fn print_summary<T: Summary>(item: &T) {
    println!("{}", item.summarize());
}

// Multiple bounds
fn process<T: Summary + Clone>(item: T) { /* ... */ }

// Where clause (cleaner for complex bounds)
fn complex<T, U>(t: T, u: U) -> String
where
    T: Summary + Clone,
    U: Debug + Default,
{
    // ...
}
```

---

## Generics

### Generic Functions

```rust
fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut largest = &list[0];
    for item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}
```

### Generic Structs

```rust
struct Wrapper<T> {
    value: T,
}

impl<T> Wrapper<T> {
    fn new(value: T) -> Self {
        Wrapper { value }
    }

    fn get(&self) -> &T {
        &self.value
    }
}

// Conditional implementation
impl<T: Display> Wrapper<T> {
    fn print(&self) {
        println!("{}", self.value);
    }
}
```

### Generic Enums

```rust
// Option and Result are generic enums
enum Option<T> {
    Some(T),
    None,
}

enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

---

## Lifetimes

### Basic Lifetime Annotations

```rust
// Lifetime ensures returned reference is valid
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// Usage
let s1 = String::from("short");
let s2 = String::from("longer string");
let result = longest(&s1, &s2);
```

### Lifetime in Structs

```rust
// Struct containing references
struct Excerpt<'a> {
    text: &'a str,
}

impl<'a> Excerpt<'a> {
    fn level(&self) -> i32 {
        3  // Doesn't use the reference, no annotation needed
    }

    fn announce(&self, announcement: &str) -> &'a str {
        println!("Attention: {announcement}");
        self.text
    }
}
```

### Lifetime Elision

The compiler infers lifetimes in common cases:

```rust
// These are equivalent:
fn first_word(s: &str) -> &str { /* ... */ }
fn first_word<'a>(s: &'a str) -> &'a str { /* ... */ }

// Rules:
// 1. Each input reference gets its own lifetime
// 2. If exactly one input lifetime, output gets same
// 3. If &self, output gets lifetime of self
```

---

## Iterators

### Creating Iterators

```rust
let v = vec![1, 2, 3, 4, 5];

// Borrowing iterator
for x in &v {
    println!("{x}");
}

// Consuming iterator
for x in v {
    println!("{x}");
}

// Mutable iterator
let mut v = vec![1, 2, 3];
for x in &mut v {
    *x *= 2;
}
```

### Iterator Adapters

```rust
let v = vec![1, 2, 3, 4, 5];

// map: transform each element
let doubled: Vec<_> = v.iter().map(|x| x * 2).collect();

// filter: keep matching elements
let evens: Vec<_> = v.iter().filter(|x| *x % 2 == 0).collect();

// chain adapters
let result: Vec<_> = v.iter()
    .filter(|x| *x > 2)
    .map(|x| x * 10)
    .collect();

// find: first matching element
let found = v.iter().find(|x| **x > 3);

// fold: accumulate
let sum: i32 = v.iter().fold(0, |acc, x| acc + x);
// Or use sum()
let sum: i32 = v.iter().sum();
```

### Common Iterator Methods

| Method | Purpose |
|--------|---------|
| `map` | Transform elements |
| `filter` | Keep matching elements |
| `filter_map` | Filter and transform in one |
| `flat_map` | Map and flatten |
| `take(n)` | First n elements |
| `skip(n)` | Skip first n elements |
| `enumerate` | Add index to elements |
| `zip` | Combine two iterators |
| `collect` | Collect into container |
| `fold` | Reduce to single value |
| `find` | First matching element |
| `any` / `all` | Boolean predicates |

---

## Closures

### Closure Syntax

```rust
// Full syntax
let add = |a: i32, b: i32| -> i32 { a + b };

// Type inference
let add = |a, b| a + b;

// Single expression (no braces needed)
let double = |x| x * 2;

// Capturing environment
let multiplier = 3;
let multiply = |x| x * multiplier;
```

### Closure Traits

| Trait | Captures | Can be called |
|-------|----------|---------------|
| `Fn` | Immutable borrow | Multiple times |
| `FnMut` | Mutable borrow | Multiple times |
| `FnOnce` | Takes ownership | Once |

```rust
// Function taking a closure
fn apply<F>(f: F, x: i32) -> i32
where
    F: Fn(i32) -> i32,
{
    f(x)
}

let result = apply(|x| x * 2, 5);
```

### Move Closures

```rust
// Force closure to take ownership
let s = String::from("hello");
let print = move || println!("{s}");
// s is no longer valid here

print();  // Works because closure owns s
```

---

## Common Idioms

### Builder Pattern

```rust
struct RequestBuilder {
    url: String,
    method: String,
    headers: Vec<(String, String)>,
}

impl RequestBuilder {
    fn new(url: impl Into<String>) -> Self {
        Self {
            url: url.into(),
            method: String::from("GET"),
            headers: Vec::new(),
        }
    }

    fn method(mut self, method: impl Into<String>) -> Self {
        self.method = method.into();
        self
    }

    fn header(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.headers.push((key.into(), value.into()));
        self
    }

    fn build(self) -> Request {
        Request { /* ... */ }
    }
}

// Usage
let request = RequestBuilder::new("https://api.example.com")
    .method("POST")
    .header("Content-Type", "application/json")
    .build();
```

### Newtype Pattern

```rust
// Wrap primitive types for type safety
struct UserId(u64);
struct OrderId(u64);

fn process_user(id: UserId) { /* ... */ }
fn process_order(id: OrderId) { /* ... */ }

// Can't mix them up
let user_id = UserId(1);
let order_id = OrderId(1);
// process_user(order_id);  // Compile error!
```

### Type State Pattern

```rust
// Compile-time state machine
struct Request<State> {
    url: String,
    _state: std::marker::PhantomData<State>,
}

struct Unvalidated;
struct Validated;

impl Request<Unvalidated> {
    fn validate(self) -> Result<Request<Validated>, Error> {
        // Validation logic
        Ok(Request {
            url: self.url,
            _state: std::marker::PhantomData,
        })
    }
}

impl Request<Validated> {
    fn send(self) -> Response {
        // Only valid requests can be sent
    }
}
```

---

## Troubleshooting

### Ownership Errors

**Problem:** `value borrowed here after move`

```rust
let s = String::from("hello");
let s2 = s;
println!("{s}");  // Error: s was moved to s2
```

**Fix:** Clone if you need both, or use references:
```rust
let s = String::from("hello");
let s2 = s.clone();
println!("{s}");  // Works
```

### Lifetime Errors

**Problem:** `missing lifetime specifier`

```rust
fn get_first(s: &str, t: &str) -> &str {
    s  // Error: which lifetime?
}
```

**Fix:** Add explicit lifetimes:
```rust
fn get_first<'a>(s: &'a str, _t: &str) -> &'a str {
    s
}
```

### Trait Bound Errors

**Problem:** `the trait X is not implemented for Y`

```rust
fn print_it<T>(x: T) {
    println!("{}", x);  // Error: T doesn't implement Display
}
```

**Fix:** Add trait bound:
```rust
fn print_it<T: std::fmt::Display>(x: T) {
    println!("{}", x);
}
```

### Mutability Errors

**Problem:** `cannot borrow as mutable`

```rust
let v = vec![1, 2, 3];
v.push(4);  // Error: v is not mutable
```

**Fix:** Make it mutable:
```rust
let mut v = vec![1, 2, 3];
v.push(4);
```

---

## References

- [The Rust Book](https://doc.rust-lang.org/book/)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [Rust Reference](https://doc.rust-lang.org/reference/)
- Specialized skills: `lang-rust-errors-dev`, `lang-rust-cargo-dev`, `lang-rust-library-dev`, `lang-rust-docs-dev`, `lang-rust-memory-eng`
