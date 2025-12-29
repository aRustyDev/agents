# Performance Considerations

Guide for understanding and optimizing performance when converting between languages.

## Performance Impact Overview

| Conversion | Typical Impact | Key Factors |
|------------|----------------|-------------|
| GC → Ownership (e.g., TS→Rust) | +50-500% faster | No GC pauses, stack allocation |
| Dynamic → Static typing | +20-100% faster | No runtime type checks |
| Interpreted → Compiled | +10-100x faster | Direct machine code |
| Single-threaded → Multi-threaded | Variable | Depends on workload |
| Sync → Async | Variable | IO-bound vs CPU-bound |

---

## Memory Model Impact

### Garbage Collection vs Manual/Ownership

| Aspect | GC Languages | Ownership (Rust) |
|--------|--------------|------------------|
| Allocation | Fast (bump allocator) | Similar or faster |
| Deallocation | Batched (GC pause) | Immediate (RAII) |
| Latency | Unpredictable spikes | Predictable |
| Throughput | Good | Often better |
| Memory usage | Higher (delayed free) | Lower |

### When GC Overhead Matters

```
High-frequency allocation:  GC overhead significant
Long-lived objects:         GC overhead minimal
Real-time requirements:     GC problematic
Batch processing:           GC often acceptable
```

### Mitigation Patterns

**Source (TypeScript) - many allocations:**
```typescript
function processItems(items: Item[]): Result[] {
  return items.map(item => ({
    id: item.id,
    value: computeValue(item),  // New object per iteration
  }));
}
```

**Target (Rust) - avoid unnecessary allocations:**
```rust
fn process_items(items: &[Item]) -> Vec<Result> {
    // Pre-allocate with capacity
    let mut results = Vec::with_capacity(items.len());

    for item in items {
        results.push(Result {
            id: item.id,
            value: compute_value(item),
        });
    }
    results
}
```

---

## Type System Impact

### Dynamic vs Static Typing

| Aspect | Dynamic Typing | Static Typing |
|--------|----------------|---------------|
| Type checks | Runtime | Compile time |
| Dispatch | Often indirect | Direct (monomorphized) |
| Optimization | Limited | Extensive |
| Inlining | Difficult | Easy |

### Pattern: Avoid Polymorphism Overhead

**Source (Python) - dynamic dispatch:**
```python
def process(handler):  # Type unknown at compile time
    return handler.handle(data)
```

**Target (Rust) - static dispatch when possible:**
```rust
// Dynamic dispatch (trait object)
fn process_dyn(handler: &dyn Handler) -> Result {
    handler.handle(&data)  // Indirect call
}

// Static dispatch (generics) - prefer when possible
fn process<H: Handler>(handler: &H) -> Result {
    handler.handle(&data)  // Can be inlined
}
```

---

## Collection Performance

### Collection Choice by Operation

| Operation | Best Choice | Avoid |
|-----------|-------------|-------|
| Index access | `Vec`/Array | `LinkedList` |
| Key lookup | `HashMap` | `Vec` + search |
| Ordered iteration | `Vec`, `BTreeMap` | `HashMap` |
| Insertion order | `IndexMap` | `HashMap` |
| Deque (both ends) | `VecDeque` | `Vec` |
| Unique values | `HashSet` | `Vec` + contains |

### Language-Specific Equivalents

| Operation | TypeScript | Python | Rust | Go |
|-----------|------------|--------|------|-----|
| Dynamic array | `Array` | `list` | `Vec<T>` | `[]T` slice |
| Hash map | `Map` | `dict` | `HashMap<K,V>` | `map[K]V` |
| Hash set | `Set` | `set` | `HashSet<T>` | `map[T]struct{}` |
| Ordered map | N/A | `dict` (3.7+) | `BTreeMap` | N/A |

### Capacity Pre-allocation

**Inefficient (reallocations):**
```rust
let mut vec = Vec::new();
for i in 0..1000 {
    vec.push(i);  // May reallocate multiple times
}
```

**Efficient (pre-allocated):**
```rust
let mut vec = Vec::with_capacity(1000);
for i in 0..1000 {
    vec.push(i);  // No reallocations
}
```

---

## String Performance

### String Handling Patterns

| Language | Mutable String | Immutable | Slice/View |
|----------|----------------|-----------|------------|
| TypeScript | `string` (immutable) | `string` | N/A |
| Python | `list` of chars | `str` | Slicing creates copy |
| Rust | `String` | `String` | `&str` |
| Go | `[]byte` | `string` | `string` (view) |

### Avoid String Concatenation in Loops

**Inefficient:**
```rust
let mut result = String::new();
for word in words {
    result = result + &word + " ";  // O(n²) - copies entire string
}
```

**Efficient:**
```rust
// Option 1: join
let result = words.join(" ");

// Option 2: with_capacity + push_str
let total_len: usize = words.iter().map(|w| w.len() + 1).sum();
let mut result = String::with_capacity(total_len);
for word in words {
    result.push_str(&word);
    result.push(' ');
}
```

---

## Async/Concurrency Performance

### Model Comparison

| Model | Best For | Overhead |
|-------|----------|----------|
| Async/await | IO-bound, many connections | Low (single thread) |
| Thread pool | CPU-bound, parallelism | Medium |
| Green threads | Mixed workloads | Variable |
| Actor model | Distributed, isolation | Higher |

### Common Pitfalls

**Blocking in async context:**
```rust
// ❌ Blocks the async runtime
async fn bad_example() {
    std::thread::sleep(Duration::from_secs(1));  // Blocks thread!
}

// ✓ Use async sleep
async fn good_example() {
    tokio::time::sleep(Duration::from_secs(1)).await;
}
```

**Unnecessary async:**
```rust
// ❌ Async overhead for sync operation
async fn get_cached_value(&self) -> Value {
    self.cache.get(&key).cloned()  // No await, no IO
}

// ✓ Keep it sync
fn get_cached_value(&self) -> Value {
    self.cache.get(&key).cloned()
}
```

---

## Optimization Checklist

### Before Converting

- [ ] Profile the original code
- [ ] Identify hot paths (80/20 rule)
- [ ] Document performance requirements
- [ ] Create benchmark suite

### During Conversion

- [ ] Use appropriate data structures
- [ ] Avoid unnecessary allocations
- [ ] Prefer borrowing over cloning
- [ ] Use static dispatch when possible
- [ ] Pre-allocate collections when size is known
- [ ] Avoid string concatenation in loops

### After Conversion

- [ ] Run benchmark suite
- [ ] Profile converted code
- [ ] Compare with original performance
- [ ] Document any regressions

---

## Profiling Tools

| Language | CPU Profiler | Memory Profiler | Benchmarking |
|----------|--------------|-----------------|--------------|
| TypeScript | Chrome DevTools | Chrome DevTools | Benchmark.js |
| Python | cProfile, py-spy | memory_profiler | pytest-benchmark |
| Rust | perf, flamegraph | heaptrack, valgrind | criterion |
| Go | pprof | pprof | testing.B |

### Rust Profiling Example

```rust
// Cargo.toml
[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "my_benchmark"
harness = false

// benches/my_benchmark.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark_function(c: &mut Criterion) {
    c.bench_function("function_name", |b| {
        b.iter(|| {
            function_to_benchmark(black_box(input))
        })
    });
}

criterion_group!(benches, benchmark_function);
criterion_main!(benches);
```

---

## Common Performance Regressions

### 1. Over-cloning

```rust
// ❌ Cloning when borrowing works
fn process(data: Vec<Item>) {
    for item in data.clone().iter() { ... }
}

// ✓ Borrow instead
fn process(data: &[Item]) {
    for item in data.iter() { ... }
}
```

### 2. Wrong Collection Type

```rust
// ❌ O(n) lookup
let items: Vec<Item> = ...;
if items.iter().any(|i| i.id == target_id) { ... }

// ✓ O(1) lookup
let items: HashMap<Id, Item> = ...;
if items.contains_key(&target_id) { ... }
```

### 3. Unnecessary Boxing

```rust
// ❌ Heap allocation for small types
struct Config {
    value: Box<i32>,  // Unnecessary indirection
}

// ✓ Stack allocation
struct Config {
    value: i32,
}
```

### 4. Missed Parallelization

```rust
// ❌ Sequential when parallel is possible
let results: Vec<_> = items.iter()
    .map(|item| expensive_compute(item))
    .collect();

// ✓ Parallel with rayon
use rayon::prelude::*;
let results: Vec<_> = items.par_iter()
    .map(|item| expensive_compute(item))
    .collect();
```

---

## Related

- `meta-convert-dev` - Core conversion patterns
- `patterns-concurrency-dev` - Concurrency patterns (when created)
- Language-specific `lang-*-dev` skills
