# Ownership Family

> Type systems that track resource ownership and lifetimes, enabling memory safety without garbage collection.

## Overview

Ownership systems ensure memory safety at compile time:

- **Single owner** - Each value has exactly one owner
- **Borrowing** - Temporary access without ownership transfer
- **Lifetimes** - Compiler tracks how long references are valid
- **No GC** - Memory freed deterministically when owner goes out of scope
- **No use-after-free** - Impossible by construction

## Base Families

This is a **feature family** primarily associated with [Systems](systems.md) and experimental [ML-FP](ml-fp.md) extensions.

## Languages

| Language | Base Family | Notes |
|----------|-------------|-------|
| Rust | Systems | Primary ownership language |
| Linear Haskell | ML-FP | Linear types extension |
| Austral | Systems | Capability-based, linear |
| Vale | Systems | Generational references |

## Key Concepts

### Ownership Rules (Rust)

1. Each value has exactly one owner
2. When owner goes out of scope, value is dropped
3. Ownership can be transferred (moved)

```rust
let s1 = String::from("hello");
let s2 = s1;  // Ownership moved to s2
// s1 is now invalid - compile error if used
```

### Borrowing

```rust
// Immutable borrow (multiple allowed)
fn calculate(data: &Vec<i32>) -> i32 {
    data.iter().sum()
}

// Mutable borrow (exclusive)
fn modify(data: &mut Vec<i32>) {
    data.push(42);
}

// Borrow rules:
// - Many immutable borrows OR one mutable borrow
// - Borrows must not outlive owner
```

### Lifetimes

```rust
// Explicit lifetime annotation
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// Lifetime in structs
struct Parser<'a> {
    input: &'a str,
}
```

### Interior Mutability

```rust
use std::cell::RefCell;
use std::rc::Rc;

// Single-threaded shared ownership + mutability
let shared = Rc::new(RefCell::new(5));
*shared.borrow_mut() += 1;

// Thread-safe version
use std::sync::{Arc, Mutex};
let shared = Arc::new(Mutex::new(5));
*shared.lock().unwrap() += 1;
```

## Conversion Considerations

### Converting FROM Ownership

**What's easy:**

- Pure functions → pure functions
- Value semantics → copy (if target has GC)
- Algorithms → direct mapping

**What's lost:**

- Compile-time memory safety guarantees
- Deterministic destruction timing
- Zero-cost abstractions

### Converting TO Ownership

**What requires restructuring:**

- Shared mutable state → Arc<Mutex<T>> or redesign
- Circular references → weak references or indices
- Exceptions → Result types
- Null → Option types

**Common patterns:**

- Use `clone()` sparingly (prefer borrowing)
- Prefer passing references over ownership
- Use enums for state machines
- Leverage iterators (zero-cost)

## Sources

- [The Rust Book: Ownership](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html)
- [Rustonomicon](https://doc.rust-lang.org/nomicon/)
- [Linear Haskell](https://arxiv.org/abs/1710.09756)

## See Also

- [Systems](systems.md) - Primary family
- [ML-FP](ml-fp.md) - Linear types extension
- [Overview](overview.md) - Comparison matrices
