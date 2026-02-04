# Systems Programming Family

> Languages designed for low-level programming with direct hardware access and precise memory control.

## Overview

The Systems family includes languages for building operating systems, embedded systems, and performance-critical applications:

- **Memory control** - Direct management or ownership-based safety
- **Hardware access** - Pointers, memory-mapped I/O
- **Zero-cost abstractions** - High-level features compile to efficient code
- **Predictable performance** - No GC pauses, deterministic behavior
- **Unsafe escape hatches** - Bypass safety when needed

Rust has fundamentally changed this family by providing memory safety without garbage collection.

## Subtypes

| Subtype | Description | Languages |
|---------|-------------|-----------|
| **ownership** | Memory safety via ownership/borrowing | Rust |
| **manual** | Manual memory management | C, C++, Zig |

### Ownership vs Manual Differences

| Aspect | Ownership (Rust) | Manual (C/C++) |
|--------|------------------|----------------|
| Memory safety | Compile-time guaranteed | Developer responsibility |
| Null pointers | No null (Option<T>) | Nullable pointers |
| Use-after-free | Impossible | Common bug source |
| Data races | Prevented by type system | Possible |
| Unsafe code | Explicit `unsafe` blocks | Everywhere |
| Learning curve | Steep (borrow checker) | Moderate to steep |

## Key Characteristics

- **Compiled to native** - Direct machine code execution
- **No runtime** - Minimal or no runtime overhead
- **Manual memory** - Or ownership-tracked automatic
- **Pointer arithmetic** - Direct memory manipulation (C/C++)
- **Zero-cost abstractions** - Generics, traits without overhead
- **ABI control** - Precise control over calling conventions
- **Inline assembly** - Embed assembly when needed

## Languages in Family

| Language | Subtype | Memory Model | Notes |
|----------|---------|--------------|-------|
| Rust | ownership | Ownership + borrowing | Memory safe without GC |
| C | manual | Manual malloc/free | Universal systems language |
| C++ | manual | Manual + RAII + smart pointers | OOP + templates |
| Zig | manual | Manual + comptime | No hidden control flow |
| Go | (gc-based) | GC | Sometimes grouped here |

> **Note**: Go uses garbage collection but is often used for systems programming. It's included for completeness but differs significantly from the core family.

## Type System

### Static Typing

- **Compile-time checking** - Types verified before runtime
- **Local inference** - Rust infers more; C requires declarations

### Type Features

| Feature | Rust | C | C++ |
|---------|------|---|-----|
| Generics | ● Native | ○ None | ● Templates |
| Type inference | ◕ Good | ○ None | ◔ Limited (auto) |
| Sum types | ● Enums | ○ None | ◔ std::variant |
| Null safety | ● Option<T> | ○ No | ○ No |
| Pattern matching | ● Native | ○ None | ◔ Limited (C++17) |

### Rust Type Patterns

```rust
// Sum types (enums)
enum Result<T, E> {
    Ok(T),
    Err(E),
}

// Pattern matching
match result {
    Ok(value) => process(value),
    Err(e) => handle_error(e),
}

// Generics with trait bounds
fn process<T: Display + Clone>(item: T) -> String {
    format!("{}", item.clone())
}
```

## Memory Model

### Rust Ownership

```rust
// Ownership transfer
let s1 = String::from("hello");
let s2 = s1;  // s1 is now invalid

// Borrowing (immutable)
let s = String::from("hello");
let len = calculate_length(&s);  // s still valid

// Borrowing (mutable)
let mut s = String::from("hello");
change(&mut s);

// Lifetimes
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

### C/C++ Manual Memory

```c
// C malloc/free
int* arr = malloc(10 * sizeof(int));
// ... use arr ...
free(arr);

// C++ new/delete
int* arr = new int[10];
// ... use arr ...
delete[] arr;

// C++ smart pointers (RAII)
auto ptr = std::make_unique<MyClass>();
// Automatically freed when ptr goes out of scope
```

### Memory Characteristics

| Feature | Rust | C | C++ |
|---------|------|---|-----|
| Stack allocation | ✓ | ✓ | ✓ |
| Heap allocation | Box, Vec, etc. | malloc | new, smart ptrs |
| RAII | ✓ (Drop trait) | ✗ | ✓ |
| Move semantics | Default | N/A | ✓ (C++11) |
| Unsafe raw pointers | In `unsafe` | Default | Default |

## Concurrency Model

### Rust

- **Fearless concurrency** - Data races prevented at compile time
- **Threads** - `std::thread`
- **Async/await** - Zero-cost async with Tokio, async-std
- **Channels** - Message passing via `mpsc`
- **Mutex/RwLock** - Interior mutability patterns

```rust
// Threads with move
let handle = std::thread::spawn(move || {
    println!("Hello from thread");
});

// Async
async fn fetch_data() -> Result<Data, Error> {
    let response = client.get(url).await?;
    Ok(response.json().await?)
}

// Channels
let (tx, rx) = mpsc::channel();
tx.send(42).unwrap();
let received = rx.recv().unwrap();
```

### C/C++

- **POSIX threads** - pthread library
- **C++11 threads** - `std::thread`
- **Atomics** - `std::atomic`
- **Manual synchronization** - Mutexes, condition variables

## Common Patterns

### RAII (Resource Acquisition Is Initialization)

```rust
// Rust: automatic cleanup
{
    let file = File::open("data.txt")?;
    // file automatically closed at end of scope
}
```

```cpp
// C++: smart pointers
{
    auto ptr = std::make_unique<Resource>();
    // Resource automatically freed at end of scope
}
```

### Error Handling

```rust
// Rust: Result type
fn read_file(path: &str) -> Result<String, io::Error> {
    let content = fs::read_to_string(path)?;
    Ok(content)
}
```

```cpp
// C++: exceptions
std::string read_file(const std::string& path) {
    std::ifstream file(path);
    if (!file) throw std::runtime_error("Cannot open file");
    // ...
}
```

### Zero-Cost Iterators (Rust)

```rust
let sum: i32 = numbers
    .iter()
    .filter(|&x| x % 2 == 0)
    .map(|x| x * 2)
    .sum();
// Compiles to efficient loop, no allocations
```

## Conversion Considerations

### Converting FROM Systems

**What's easy to preserve:**

- Algorithms and logic
- Struct/class layouts
- Function signatures
- Numeric operations

**What's hard to translate:**

- Manual memory management → GC (may leak patterns)
- Pointer arithmetic → array indexing
- Unsafe code → must make safe or wrap
- Ownership (Rust) → GC languages lose guarantees
- Low-level bit manipulation → varies by target

**Common pitfalls:**

- Assuming target has similar performance
- Losing safety guarantees (Rust → C)
- Ignoring undefined behavior (C/C++)

**Semantic gaps:**

- Systems → Systems: 23 gaps (ownership ↔ manual)
- Systems → any: Performance characteristics differ

### Converting TO Systems

**What maps naturally:**

- Functional pure code → pure functions
- Immutable data → ownership transfer or Copy types
- Strong types → strong types

**What requires restructuring:**

- GC memory → explicit ownership/lifetimes
- Exceptions → Result types (Rust) or error codes (C)
- Null → Option<T> (Rust) or careful null handling
- Shared mutable state → Mutex/Arc or redesign
- Dynamic dispatch → trait objects or enums

**Idiomatic patterns to target (Rust):**

- Use ownership and borrowing properly
- Prefer `Result` over panics
- Use iterators for collections
- Leverage enums for state machines
- Use traits for polymorphism

**Anti-patterns to avoid:**

- Fighting the borrow checker with excessive `clone()`
- Overusing `Rc<RefCell<T>>`
- Unsafe code without good reason
- Ignoring Clippy warnings

## Cross-References

### Phase 0 Pattern Clusters

- **Universal patterns**: int sizes, float, bool, String
- **Family-specific**: T* (4 patterns), std::unique_ptr (4 patterns), nullptr (3 patterns)
- **Gap patterns**: 23 gaps Systems → Systems, 29 gaps Dynamic → Systems

### Related convert-* Skills

- convert-typescript-rust (244 patterns)
- convert-java-rust (235 patterns)
- convert-python-rust (234 patterns)
- convert-c-rust (178 patterns)
- convert-cpp-rust (114 patterns)
- convert-golang-rust (97 patterns)

## Sources

- [The Rust Programming Language](https://doc.rust-lang.org/book/)
- [Rust Reference](https://doc.rust-lang.org/reference/)
- [C++ Reference](https://en.cppreference.com/)
- [Modern C](https://modernc.gforge.inria.fr/)
- [Zig Documentation](https://ziglang.org/documentation/)

## See Also

- [Ownership](ownership.md) - Ownership as cross-cutting concern
- [ML-FP](ml-fp.md) - Functional patterns apply
- [Overview](overview.md) - Cross-family comparison matrices
