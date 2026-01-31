# Performance Reference

Performance considerations when converting between languages.

---

## Performance Impact Matrix

| Conversion              | Performance Impact | Why                               |
| ----------------------- | ------------------ | --------------------------------- |
| GC → Ownership          | Usually faster     | No GC pauses, predictable cleanup |
| Dynamic → Static typing | Usually faster     | No runtime type checks            |
| Interpreted → Compiled  | Much faster        | Direct machine code               |
| Async → Sync            | Context-dependent  | May lose concurrency benefits     |
| Class hierarchy → Enums | Often faster       | Better cache locality             |

---

## Common Performance Pitfalls

### 1. Unnecessary Cloning

```rust
// ❌ Cloning when borrowing would work
fn process(items: Vec<Item>) {
    for item in items.clone() {  // Unnecessary clone
        handle(&item);
    }
}

// ✓ Borrow instead
fn process(items: &[Item]) {
    for item in items {
        handle(item);
    }
}
```

### 2. String Allocation Overhead

```rust
// ❌ Many small allocations
fn build_message(parts: &[&str]) -> String {
    let mut result = String::new();
    for part in parts {
        result = result + part;  // Reallocates each time
    }
    result
}

// ✓ Pre-allocate or use join
fn build_message(parts: &[&str]) -> String {
    parts.join("")  // Single allocation
}

// ✓ Or with capacity
fn build_message(parts: &[&str]) -> String {
    let total_len: usize = parts.iter().map(|s| s.len()).sum();
    let mut result = String::with_capacity(total_len);
    for part in parts {
        result.push_str(part);
    }
    result
}
```

### 3. Dynamic Dispatch Overhead

```rust
// ❌ Trait objects when static dispatch possible
fn process(handler: &dyn Handler) {
    handler.handle();  // Virtual call
}

// ✓ Generics for static dispatch (when possible)
fn process<H: Handler>(handler: &H) {
    handler.handle();  // Inlined, no virtual call
}
```

### 4. Inefficient Collection Choice

| Need               | Wrong Choice           | Right Choice        |
| ------------------ | ---------------------- | ------------------- |
| Fast lookup by key | `Vec` + linear search  | `HashMap`           |
| Ordered iteration  | `HashMap`              | `BTreeMap` or `Vec` |
| Unique values      | `Vec` + contains check | `HashSet`           |
| Stack behavior     | `VecDeque`             | `Vec` (push/pop)    |
| Queue behavior     | `Vec`                  | `VecDeque`          |

### 5. Boxing When Not Needed

```rust
// ❌ Unnecessary heap allocation
struct Config {
    name: Box<String>,  // Box is unnecessary here
}

// ✓ Direct ownership
struct Config {
    name: String,  // Already heap-allocated internally
}
```

---

## Memory Efficiency

### Stack vs Heap

| Allocation | Cost            | When to Use                    |
| ---------- | --------------- | ------------------------------ |
| Stack      | Free            | Small, known-size data         |
| Heap       | Allocation cost | Large, dynamic, or shared data |

```rust
// Stack (fast)
let arr = [0u8; 1024];  // 1KB on stack

// Heap (necessary for large)
let vec = vec![0u8; 1_000_000];  // 1MB on heap
```

### Reducing Allocations

```rust
// ❌ Creates new Vec each call
fn get_filtered(items: &[Item]) -> Vec<&Item> {
    items.iter().filter(|i| i.active).collect()
}

// ✓ Return iterator, let caller decide
fn get_filtered(items: &[Item]) -> impl Iterator<Item = &Item> {
    items.iter().filter(|i| i.active)
}
```

---

## Cache Efficiency

### Data Layout

```rust
// ❌ Poor cache locality (AoS)
struct Particles {
    particles: Vec<Particle>,  // Each particle has x, y, z, mass, ...
}

// ✓ Better cache locality for position updates (SoA)
struct Particles {
    x: Vec<f32>,
    y: Vec<f32>,
    z: Vec<f32>,
    mass: Vec<f32>,
}
```

### Contiguous Memory

```rust
// ❌ Pointer chasing
struct Node {
    value: i32,
    children: Vec<Box<Node>>,  // Each child is a heap allocation
}

// ✓ Flat structure with indices
struct Tree {
    nodes: Vec<NodeData>,
}
struct NodeData {
    value: i32,
    children: Vec<usize>,  // Indices into nodes
}
```

---

## Async Performance

### Avoid Blocking in Async

```rust
// ❌ Blocks the executor
async fn bad_read_file(path: &str) -> String {
    std::fs::read_to_string(path).unwrap()  // Blocking!
}

// ✓ Use async I/O or spawn_blocking
async fn good_read_file(path: &str) -> String {
    tokio::fs::read_to_string(path).await.unwrap()
}

// ✓ For CPU-intensive work
async fn cpu_work(data: Vec<u8>) -> Result {
    tokio::task::spawn_blocking(move || {
        expensive_computation(&data)
    }).await?
}
```

### Buffer Sizes

```rust
// Tune buffer sizes for throughput
let (tx, rx) = tokio::sync::mpsc::channel(1000);  // Buffer 1000 items

// For streams
stream
    .buffer_unordered(10)  // 10 concurrent operations
    .collect()
```

---

## Benchmarking

### Rust: Criterion

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark_function(c: &mut Criterion) {
    c.bench_function("my_function", |b| {
        b.iter(|| my_function(black_box(input)))
    });
}

criterion_group!(benches, benchmark_function);
criterion_main!(benches);
```

### Go: Built-in

```go
func BenchmarkMyFunction(b *testing.B) {
    for i := 0; i < b.N; i++ {
        myFunction(input)
    }
}
```

### Python: timeit

```python
import timeit

result = timeit.timeit(
    lambda: my_function(input),
    number=1000
)
print(f"Average: {result / 1000:.6f}s")
```

---

## Profiling Tools

| Language   | CPU Profiler     | Memory Profiler | Flamegraph       |
| ---------- | ---------------- | --------------- | ---------------- |
| Rust       | perf, samply     | heaptrack, dhat | cargo-flamegraph |
| Go         | pprof            | pprof           | go tool pprof    |
| Python     | cProfile, py-spy | memory_profiler | py-spy           |
| TypeScript | Node --prof      | heapdump        | 0x               |

---

## Quick Wins

| Pattern                          | Impact     | Effort   |
| -------------------------------- | ---------- | -------- |
| Use references instead of clones | High       | Low      |
| Pre-allocate collections         | Medium     | Low      |
| Choose right collection type     | High       | Low      |
| Use iterators over loops         | Low-Medium | Low      |
| Avoid allocations in hot paths   | High       | Medium   |
| Use static dispatch              | Medium     | Low      |
| Profile before optimizing        | N/A        | Required |
