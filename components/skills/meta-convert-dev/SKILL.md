---
name: meta-convert-dev
description: Create language conversion skills for translating code from language A to language B. Use when building 'convert-X-Y' skills, designing type mappings between languages, establishing idiom translation patterns, or defining conversion methodologies. Provides foundational patterns that specific conversion skills extend.
---

# Language Conversion Skill Development

Foundational patterns for creating one-way language conversion skills. This meta-skill guides the creation of `convert-X-Y` skills (e.g., `convert-typescript-rust`, `convert-python-golang`) that assist in translating/refactoring code from a source language to a target language.

## When to Use This Skill

- Creating a new `convert-X-Y` skill for language translation
- Designing type system mappings between languages
- Establishing idiom translation strategies
- Defining conversion workflows and validation approaches
- Building tooling recommendations for transpilation

## This Skill Does NOT Cover

- Actual code conversion (use specific `convert-X-Y` skills)
- Language tutorials (see `lang-*-dev` skills)
- Bidirectional translation (each direction is a separate skill)
- Runtime interop/FFI (see language-specific interop skills)

---

## Existing Conversion Skills

For concrete, language-pair-specific examples, see these skills:

| Skill | Description |
|-------|-------------|
| `convert-typescript-rust` | TypeScript → Rust (GC → ownership, exceptions → Result) |
| `convert-typescript-python` | TypeScript → Python (static → dynamic typing) |
| `convert-typescript-golang` | TypeScript → Go (OOP → simplicity, Promise → goroutine) |
| `convert-golang-rust` | Go → Rust (GC → ownership, interface → trait) |
| `convert-python-rust` | Python → Rust (dynamic → static, GC → ownership) |

**Note:** This list may not be complete. Search `components/skills/convert-*` for all available conversion skills.

When this meta-skill shows illustrative examples below, they demonstrate patterns conceptually. For production-ready, comprehensive examples with full context, refer to the specific `convert-X-Y` skills.

---

## Conversion Skill Naming Convention

```
convert-<source>-<target>
```

| Component | Description | Example |
|-----------|-------------|---------|
| `convert` | Fixed prefix | `convert-` |
| `<source>` | Source language (lowercase) | `typescript`, `python`, `golang` |
| `<target>` | Target language (lowercase) | `rust`, `python`, `golang` |

**Examples:**
- `convert-typescript-rust` - TypeScript → Rust
- `convert-python-golang` - Python → Go
- `convert-golang-rust` - Go → Rust

**Note:** Each skill is ONE-WAY. `convert-A-B` and `convert-B-A` are separate skills with different patterns.

---

## Conversion Skill Structure

Every `convert-X-Y` skill should follow this structure:

```markdown
# Convert <Source> to <Target>

## Overview
Brief description of the conversion, common use cases, and what to expect.

## When to Use
- Scenarios where this conversion makes sense
- Benefits of the target language for this use case

## When NOT to Use
- Scenarios where conversion is not recommended
- Better alternatives

## Type System Mapping
Complete mapping table from source types to target types.

## Idiom Translation
Source patterns and their idiomatic target equivalents.

## Error Handling
How to convert error handling patterns.

## Concurrency Patterns
How async/threading models translate.

## Memory & Ownership
If applicable, how memory models differ and translate.

## Testing Strategy
How to verify functional equivalence.

## Tooling
Available tools, transpilers, and validation helpers.

## Common Pitfalls
Mistakes to avoid during conversion.

## Examples
Concrete before/after conversion examples.
```

---

## Core Conversion Methodology

### The APTV Workflow

Every conversion follows: **Analyze → Plan → Transform → Validate**

```
┌─────────────────────────────────────────────────────────────┐
│                    CONVERSION WORKFLOW                       │
├─────────────────────────────────────────────────────────────┤
│  1. ANALYZE    │  Understand source code structure          │
│                │  • Parse and identify components            │
│                │  • Map dependencies                         │
│                │  • Identify language-specific patterns      │
├─────────────────────────────────────────────────────────────┤
│  2. PLAN       │  Design the target architecture            │
│                │  • Create type mapping table                │
│                │  • Identify idiom translations              │
│                │  • Plan module/package structure            │
├─────────────────────────────────────────────────────────────┤
│  3. TRANSFORM  │  Convert code systematically               │
│                │  • Types and interfaces first               │
│                │  • Core logic second                        │
│                │  • Adopt target idioms (don't transliterate)│
├─────────────────────────────────────────────────────────────┤
│  4. VALIDATE   │  Verify functional equivalence             │
│                │  • Run original tests against new code      │
│                │  • Property-based testing for edge cases    │
│                │  • Performance comparison if relevant       │
└─────────────────────────────────────────────────────────────┘
```

### Analyze Phase

Before writing any target code:

1. **Parse the source** - Understand structure, not just syntax
2. **Identify components**:
   - Types/interfaces/classes
   - Functions/methods
   - Module boundaries
   - External dependencies
3. **Note language-specific features**:
   - Generics usage
   - Error handling patterns
   - Async patterns
   - Memory management approach

### Plan Phase

Create explicit mappings before transforming:

```markdown
## Type Mapping Table

| Source (TypeScript) | Target (Rust) | Notes |
|---------------------|---------------|-------|
| `string` | `String` / `&str` | Owned vs borrowed |
| `number` | `i32` / `f64` | Specify precision |
| `boolean` | `bool` | Direct |
| `T[]` | `Vec<T>` | Owned collection |
| `T \| null` | `Option<T>` | Nullable handling |
| `Promise<T>` | `Future<Output=T>` | Async handling |
| `interface X` | `trait X` / `struct X` | Depends on usage |
```

### Transform Phase

**Golden Rule: Adopt target idioms, don't write "Source code in Target syntax"**

```typescript
// Source: TypeScript
function findUser(id: string): User | null {
  const user = users.find(u => u.id === id);
  return user || null;
}
```

```rust
// BAD: Transliterated (TypeScript in Rust clothing)
fn find_user(id: String) -> Option<User> {
    let user = users.iter().find(|u| u.id == id);
    match user {
        Some(u) => Some(u.clone()),
        None => None,
    }
}

// GOOD: Idiomatic Rust
fn find_user(id: &str) -> Option<&User> {
    users.iter().find(|u| u.id == id)
}
```

### Validate Phase

1. **Functional equivalence**: Same inputs → same outputs
2. **Edge case coverage**: Property-based tests
3. **Error behavior**: Same error conditions trigger appropriately
4. **Performance baseline**: Comparable or better performance

---

## Type System Mapping Strategies

### Primitive Type Mappings

Create a complete primitive mapping table for each language pair:

```markdown
## Primitive Mappings: TypeScript → Rust

| TypeScript | Rust | Notes |
|------------|------|-------|
| `string` | `String` | Owned, heap-allocated |
| `string` | `&str` | Borrowed, for parameters |
| `number` | `i32` | Default integer |
| `number` | `i64` | Large integers |
| `number` | `f64` | Floating point |
| `boolean` | `bool` | Direct mapping |
| `null` | - | Use Option<T> |
| `undefined` | - | Use Option<T> |
| `any` | - | Avoid; use generics or enums |
| `unknown` | - | Use generics with trait bounds |
| `never` | `!` | Never type (unstable) |
| `void` | `()` | Unit type |
```

### Composite Type Mappings

```markdown
## Composite Mappings: TypeScript → Rust

| TypeScript | Rust | Notes |
|------------|------|-------|
| `T[]` | `Vec<T>` | Owned, growable |
| `readonly T[]` | `&[T]` | Borrowed slice |
| `[T, U]` | `(T, U)` | Tuple |
| `Record<K, V>` | `HashMap<K, V>` | Owned map |
| `Map<K, V>` | `HashMap<K, V>` | Same |
| `Set<T>` | `HashSet<T>` | Unique values |
| `T \| U` | `enum { A(T), B(U) }` | Tagged union |
| `T & U` | `struct { ...T, ...U }` | Combine fields |
```

### Interface/Class to Struct/Trait

```markdown
## Structural Mappings

| TypeScript Pattern | Rust Pattern | When to Use |
|--------------------|--------------|-------------|
| `interface X { ... }` | `struct X { ... }` | Data-only types |
| `interface X { method(): T }` | `trait X { fn method(&self) -> T }` | Behavior contracts |
| `class X implements Y` | `struct X` + `impl Y for X` | Implementation |
| `class X extends Y` | Composition over inheritance | Rust avoids inheritance |
| `abstract class X` | `trait X` | Abstract contracts |
```

### Generic Type Mappings

```markdown
## Generics: TypeScript → Rust

| TypeScript | Rust | Notes |
|------------|------|-------|
| `<T>` | `<T>` | Unconstrained generic |
| `<T extends U>` | `<T: U>` | Trait bound |
| `<T extends A & B>` | `<T: A + B>` | Multiple bounds |
| `<T = Default>` | `<T = Default>` | Default type |
| `<T extends keyof U>` | Custom trait | No direct equivalent |
```

---

## Idiom Translation Patterns

> **Note:** The examples below are illustrative snippets showing the *concept* of idiom translation. For complete, production-ready examples with full error handling and edge cases, see specific `convert-X-Y` skills like `convert-typescript-rust` or `convert-python-rust`.

### Translation Philosophy

| Approach | When to Use | Example |
|----------|-------------|---------|
| **Literal** | Simple operations, primitives | `x + y` → `x + y` |
| **Semantic** | Same concept, different syntax | `arr.map()` → `.iter().map()` |
| **Idiomatic** | Different paradigm | Class hierarchy → Trait + Structs |
| **Redesign** | No equivalent | Prototype chain → Explicit composition |

### Common Idiom Translations

#### Null Handling

```typescript
// TypeScript: null coalescing
const name = user?.name ?? "Anonymous";
```

```rust
// Rust: Option combinators
let name = user.as_ref()
    .map(|u| u.name.as_str())
    .unwrap_or("Anonymous");
```

```go
// Go: explicit nil check
var name string
if user != nil && user.Name != "" {
    name = user.Name
} else {
    name = "Anonymous"
}
```

```python
# Python: or operator (careful with falsy values)
name = (user and user.name) or "Anonymous"

# Safer Python
name = user.name if user and user.name else "Anonymous"
```

#### Collection Operations

```typescript
// TypeScript: chained methods
const result = items
  .filter(x => x.active)
  .map(x => x.value)
  .reduce((a, b) => a + b, 0);
```

```rust
// Rust: iterator adaptors
let result: i32 = items.iter()
    .filter(|x| x.active)
    .map(|x| x.value)
    .sum();
```

```go
// Go: explicit loops (pre-generics style)
var result int
for _, x := range items {
    if x.Active {
        result += x.Value
    }
}
```

```python
# Python: generator expressions
result = sum(x.value for x in items if x.active)
```

---

## Error Handling Translation

> **Note:** These examples show error handling translation concepts. For comprehensive error hierarchy translations and real-world patterns, see `convert-typescript-rust`, `convert-python-rust`, or `convert-golang-rust`.

### Error Model Comparison

| Language | Primary Model | Error Type | Propagation |
|----------|--------------|------------|-------------|
| TypeScript | Exceptions | `Error` class | `throw` / `try-catch` |
| Python | Exceptions | `Exception` hierarchy | `raise` / `try-except` |
| Go | Error returns | `error` interface | Multiple return values |
| Rust | Result type | `Result<T, E>` | `?` operator |

### Exception → Result Type

```typescript
// TypeScript: throws exception
function parseConfig(path: string): Config {
  const content = fs.readFileSync(path, 'utf-8');
  try {
    return JSON.parse(content);
  } catch (e) {
    throw new Error(`Failed to parse config: ${e.message}`);
  }
}
```

```rust
// Rust: returns Result
fn parse_config(path: &Path) -> Result<Config, ConfigError> {
    let content = fs::read_to_string(path)
        .map_err(|e| ConfigError::ReadFailed(e))?;
    serde_json::from_str(&content)
        .map_err(|e| ConfigError::ParseFailed(e))
}
```

### Exception → Error Return

```typescript
// TypeScript: throws
function divide(a: number, b: number): number {
  if (b === 0) throw new Error("division by zero");
  return a / b;
}
```

```go
// Go: error return
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}
```

### Error Hierarchy Translation

```typescript
// TypeScript: class hierarchy
class AppError extends Error {
  constructor(message: string, public code: string) {
    super(message);
  }
}
class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`, "NOT_FOUND");
  }
}
```

```rust
// Rust: enum variants
#[derive(Debug, thiserror::Error)]
enum AppError {
    #[error("{resource} not found")]
    NotFound { resource: String },

    #[error("validation failed: {message}")]
    Validation { message: String },

    #[error(transparent)]
    Io(#[from] std::io::Error),
}
```

---

## Concurrency Model Translation

> **Note:** For complete async translation patterns including cancellation, streams, and parallel execution, see the specific conversion skills.

### Model Comparison

| Language | Async Model | Threading | Channels |
|----------|-------------|-----------|----------|
| TypeScript | `async/await`, Promises | Web Workers (limited) | - |
| Python | `async/await`, asyncio | Threading, multiprocessing | Queue |
| Go | Goroutines | Built-in | `chan` (first-class) |
| Rust | `async/await`, Futures | std::thread | mpsc, crossbeam |

### Promise/Future Translation

```typescript
// TypeScript: Promise-based
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/users/${id}`);
  return response.json();
}
```

```rust
// Rust: Future-based (with tokio)
async fn fetch_user(id: &str) -> Result<User, reqwest::Error> {
    let user = reqwest::get(format!("/users/{}", id))
        .await?
        .json::<User>()
        .await?;
    Ok(user)
}
```

```go
// Go: goroutine with channel
func fetchUser(id string) <-chan UserResult {
    ch := make(chan UserResult, 1)
    go func() {
        resp, err := http.Get(fmt.Sprintf("/users/%s", id))
        if err != nil {
            ch <- UserResult{Err: err}
            return
        }
        defer resp.Body.Close()
        var user User
        json.NewDecoder(resp.Body).Decode(&user)
        ch <- UserResult{User: user}
    }()
    return ch
}
```

### Parallel Execution

```typescript
// TypeScript: Promise.all
const [users, orders] = await Promise.all([
  fetchUsers(),
  fetchOrders()
]);
```

```rust
// Rust: tokio::join!
let (users, orders) = tokio::join!(
    fetch_users(),
    fetch_orders()
);
```

```go
// Go: goroutines with WaitGroup
var wg sync.WaitGroup
var users []User
var orders []Order

wg.Add(2)
go func() { defer wg.Done(); users = fetchUsers() }()
go func() { defer wg.Done(); orders = fetchOrders() }()
wg.Wait()
```

---

## Memory & Ownership Translation

> **Note:** For detailed ownership patterns when converting from GC languages, see `convert-typescript-rust`, `convert-python-rust`, or `convert-golang-rust`.

### Memory Model Comparison

| Language | Memory Model | Cleanup | Ownership |
|----------|--------------|---------|-----------|
| TypeScript | GC (V8) | Automatic | Shared references |
| Python | GC (ref counting + cycle) | Automatic | Shared references |
| Go | GC (concurrent) | Automatic | Shared references |
| Rust | Ownership + Borrowing | Deterministic (RAII) | Explicit ownership |

### GC → Ownership (e.g., TypeScript → Rust)

```typescript
// TypeScript: freely share references
class Cache {
  private data: Map<string, User> = new Map();

  get(id: string): User | undefined {
    return this.data.get(id);  // Returns reference
  }

  set(id: string, user: User): void {
    this.data.set(id, user);  // Stores reference
  }
}
```

```rust
// Rust: explicit ownership decisions
struct Cache {
    data: HashMap<String, User>,
}

impl Cache {
    // Return borrowed reference (doesn't transfer ownership)
    fn get(&self, id: &str) -> Option<&User> {
        self.data.get(id)
    }

    // Take ownership of user (caller gives up ownership)
    fn set(&mut self, id: String, user: User) {
        self.data.insert(id, user);
    }

    // Alternative: clone if shared ownership needed
    fn get_owned(&self, id: &str) -> Option<User> {
        self.data.get(id).cloned()
    }
}
```

### Ownership Decision Tree

```
When converting GC → Ownership:

1. Is this data shared across components?
   ├─ YES → Consider Arc<T> or Rc<T>
   └─ NO → Single owner, use moves

2. Is this data mutated by multiple parts?
   ├─ YES → Arc<Mutex<T>> or channels
   └─ NO → Immutable borrows (&T)

3. Does this data outlive its creator?
   ├─ YES → Return owned value or 'static
   └─ NO → Return borrowed reference
```

---

## Testing Strategy for Conversions

### Verification Approach

```
┌─────────────────────────────────────────────────────────────┐
│                    TESTING PYRAMID                          │
├─────────────────────────────────────────────────────────────┤
│                    ┌───────────────┐                        │
│                    │  Integration  │  Same API behavior      │
│                    └───────────────┘                        │
│               ┌─────────────────────────┐                   │
│               │    Property-Based       │  Invariants hold   │
│               └─────────────────────────┘                   │
│          ┌───────────────────────────────────┐              │
│          │           Unit Tests              │  Logic match   │
│          └───────────────────────────────────┘              │
│     ┌─────────────────────────────────────────────┐         │
│     │        Input/Output Comparison              │         │
│     └─────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 1. Port Existing Tests

```typescript
// Original TypeScript test
describe('Calculator', () => {
  it('should add numbers', () => {
    expect(add(2, 3)).toBe(5);
  });

  it('should handle negative numbers', () => {
    expect(add(-1, 1)).toBe(0);
  });
});
```

```rust
// Converted Rust test
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn should_add_numbers() {
        assert_eq!(add(2, 3), 5);
    }

    #[test]
    fn should_handle_negative_numbers() {
        assert_eq!(add(-1, 1), 0);
    }
}
```

### 2. Property-Based Testing

Test that invariants hold across random inputs:

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn add_is_commutative(a: i32, b: i32) {
        prop_assert_eq!(add(a, b), add(b, a));
    }

    #[test]
    fn add_has_identity(a: i32) {
        prop_assert_eq!(add(a, 0), a);
    }
}
```

### 3. Golden Testing

Compare outputs between original and converted code:

```python
# Generate test cases from original implementation
import json

test_cases = []
for input_data in generate_inputs():
    output = original_function(input_data)
    test_cases.append({
        "input": input_data,
        "expected": output
    })

with open("golden_tests.json", "w") as f:
    json.dump(test_cases, f)
```

```rust
// Verify converted implementation matches golden outputs
#[test]
fn golden_tests() {
    let test_cases: Vec<TestCase> =
        serde_json::from_str(include_str!("golden_tests.json")).unwrap();

    for case in test_cases {
        let actual = converted_function(&case.input);
        assert_eq!(actual, case.expected, "Failed for input: {:?}", case.input);
    }
}
```

---

## Tooling Recommendations

### AST Analysis Tools

| Language | Tool | Purpose |
|----------|------|---------|
| TypeScript | `ts-morph`, `typescript` compiler API | Parse and analyze TS/JS |
| Python | `ast` module, `libcst` | Parse Python code |
| Go | `go/ast`, `go/parser` | Parse Go code |
| Rust | `syn`, `proc-macro2` | Parse Rust code |

### Transpilers & Converters

| Conversion | Tool | Notes |
|------------|------|-------|
| JS/TS → Rust | - | Manual (no mature tool) |
| Python → Rust | `py2rs` (limited) | Experimental |
| Go → Rust | - | Manual |
| TypeScript → Go | - | Manual |
| C → Rust | `c2rust` | Produces unsafe Rust |

### Validation Tools

1. **Differential Testing**: Run both versions with same inputs
2. **Coverage Comparison**: Ensure test coverage is equivalent
3. **Benchmark Comparison**: Compare performance characteristics
4. **Static Analysis**: Run linters on converted code

---

## Common Pitfalls

### 1. Transliteration Instead of Translation

```
❌ Writing "TypeScript in Rust syntax"
✓ Writing idiomatic Rust that achieves the same goal
```

### 2. Ignoring Target Language Strengths

```
❌ Porting class hierarchies to Rust (fighting the borrow checker)
✓ Using Rust's enums and traits to achieve polymorphism
```

### 3. One-to-One Function Mapping

```
❌ Every source function becomes one target function
✓ Restructure to fit target language patterns (may split or merge)
```

### 4. Preserving Source Inefficiencies

```
❌ Port the inefficient algorithm just because it worked
✓ Identify and optimize for target language characteristics
```

### 5. Ignoring Ecosystem Conventions

```
❌ Using camelCase in Python (because source was TypeScript)
✓ Using snake_case (Python convention)
```

---

## Advanced Ownership & Borrowing Patterns

When converting from GC languages to ownership-based languages (especially Rust), deeper understanding of borrowing patterns is essential.

### Borrowing Pattern Decision Matrix

| Source Pattern | Rust Pattern | When to Use |
|----------------|--------------|-------------|
| Pass by reference | `&T` | Read-only access, no mutation needed |
| Mutable reference | `&mut T` | Single mutator, temporary access |
| Shared ownership | `Rc<T>` / `Arc<T>` | Multiple owners, single-threaded / multi-threaded |
| Interior mutability | `RefCell<T>` / `Mutex<T>` | Shared + mutable, single / multi-threaded |
| Optional ownership | `Option<Box<T>>` | Nullable owned values |

### Lifetime Patterns

```rust
// Pattern 1: Struct borrowing from owner
struct Parser<'a> {
    source: &'a str,  // Borrows source, doesn't own it
}

// Pattern 2: Self-referential alternatives
// Instead of self-referential structs, use indices:
struct TokenStream {
    source: String,
    tokens: Vec<(usize, usize)>,  // (start, end) indices into source
}

// Pattern 3: Owned vs Borrowed parameters
// Prefer borrowed for read-only, owned for consumed
fn process_borrowed(data: &[u8]) -> Result<()> { ... }
fn consume_owned(data: Vec<u8>) -> Result<Output> { ... }
```

### Clone vs Borrow Decision Tree

```
Is the data expensive to clone?
├─ YES → Use borrowing with lifetimes
│        ├─ Single owner? → &T / &mut T
│        └─ Multiple owners? → Arc<T>
└─ NO → Clone freely (Copy types, small structs)
        └─ Consider #[derive(Clone)] for value semantics
```

### Shared State Patterns

```typescript
// TypeScript: Shared mutable state is easy
class SharedCounter {
  private count = 0;
  increment() { this.count++; }
  get() { return this.count; }
}
// Multiple references can call increment()
```

```rust
// Rust: Explicit about sharing and mutation
use std::sync::{Arc, Mutex};

struct SharedCounter {
    count: Arc<Mutex<i32>>,
}

impl SharedCounter {
    fn increment(&self) {
        let mut guard = self.count.lock().unwrap();
        *guard += 1;
    }

    fn get(&self) -> i32 {
        *self.count.lock().unwrap()
    }
}
// Arc allows sharing, Mutex allows mutation
```

---

## Async Pattern Translation (Deep Dive)

### Runtime Comparison

| Aspect | JS/TS | Python | Go | Rust |
|--------|-------|--------|-----|------|
| Runtime | V8 event loop | asyncio event loop | Go scheduler | tokio/async-std |
| Default | Single-threaded | Single-threaded | Multi-threaded | Multi-threaded |
| Blocking | Never block! | Never block! | Goroutines can block | Use spawn_blocking |
| Cancellation | AbortController | asyncio.CancelledError | Context | Drop / select! |

### Cancellation Patterns

```typescript
// TypeScript: AbortController
async function fetchWithTimeout(url: string, ms: number): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), ms);
  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}
```

```rust
// Rust: tokio::select! for cancellation
use tokio::time::{timeout, Duration};

async fn fetch_with_timeout(url: &str, ms: u64) -> Result<Response, Error> {
    timeout(Duration::from_millis(ms), reqwest::get(url))
        .await
        .map_err(|_| Error::Timeout)?
        .map_err(Error::Request)
}

// Or with explicit select:
tokio::select! {
    result = fetch(url) => result,
    _ = tokio::time::sleep(duration) => Err(Error::Timeout),
}
```

```go
// Go: Context for cancellation
func fetchWithTimeout(url string, timeout time.Duration) (*http.Response, error) {
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()

    req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
    return http.DefaultClient.Do(req)
}
```

### Stream/Iterator Translation

```typescript
// TypeScript: AsyncIterable
async function* fetchPages(baseUrl: string): AsyncIterable<Page> {
  let page = 1;
  while (true) {
    const data = await fetch(`${baseUrl}?page=${page}`);
    if (!data.ok) break;
    yield await data.json();
    page++;
  }
}

for await (const page of fetchPages(url)) {
  process(page);
}
```

```rust
// Rust: Stream (futures crate or tokio_stream)
use futures::stream::{self, Stream, StreamExt};

fn fetch_pages(base_url: &str) -> impl Stream<Item = Page> {
    stream::unfold(1, move |page| async move {
        let url = format!("{}?page={}", base_url, page);
        match reqwest::get(&url).await {
            Ok(resp) if resp.status().is_success() => {
                let data: Page = resp.json().await.ok()?;
                Some((data, page + 1))
            }
            _ => None,
        }
    })
}

// Consuming
let mut pages = fetch_pages(url);
while let Some(page) = pages.next().await {
    process(page);
}
```

---

## Dependency Management Translation

### Package Ecosystem Mapping

| Source | Target | Equivalent Ecosystem |
|--------|--------|---------------------|
| npm (TypeScript) | Cargo (Rust) | Direct mapping |
| pip (Python) | Cargo (Rust) | Direct mapping |
| go mod (Go) | Cargo (Rust) | Direct mapping |
| npm (TypeScript) | pip (Python) | Direct mapping |
| npm (TypeScript) | go mod (Go) | Direct mapping |

### Common Dependency Translations

| Category | TypeScript (npm) | Python (pip) | Go | Rust (Cargo) |
|----------|-----------------|--------------|-----|--------------|
| HTTP Client | axios, fetch | requests, httpx | net/http | reqwest |
| JSON | built-in | json (stdlib) | encoding/json | serde_json |
| Async Runtime | built-in | asyncio | built-in | tokio, async-std |
| CLI Parsing | commander, yargs | argparse, click | flag, cobra | clap |
| Logging | winston, pino | logging, loguru | log, zap | tracing, log |
| Testing | jest, vitest | pytest | testing | built-in + cargo test |
| Date/Time | date-fns, luxon | datetime, arrow | time | chrono |
| Regex | built-in | re | regexp | regex |
| Env Config | dotenv | python-dotenv | os.Getenv, godotenv | dotenvy |
| Database | prisma, typeorm | sqlalchemy | gorm, sqlx | diesel, sqlx |
| Validation | zod, joi | pydantic | validator | validator |
| Serialization | class-transformer | dataclasses, attrs | encoding/* | serde |

### Dependency Version Strategy

When converting, choose dependency versions strategically:

```toml
# Rust Cargo.toml - prefer recent stable versions
[dependencies]
tokio = { version = "1", features = ["full"] }  # Major version pin
serde = { version = "1.0", features = ["derive"] }
reqwest = { version = "0.11", features = ["json"] }  # Pre-1.0, minor matters
```

```python
# Python pyproject.toml - allow compatible updates
[project]
dependencies = [
    "httpx>=0.25,<1.0",  # Pre-1.0, be conservative
    "pydantic>=2.0,<3.0",  # Major version constraint
]
```

---

## Performance Considerations

### Performance Impact Matrix

| Conversion | Performance Impact | Why |
|------------|-------------------|-----|
| GC → Ownership | Usually faster | No GC pauses, predictable cleanup |
| Dynamic → Static typing | Usually faster | No runtime type checks |
| Interpreted → Compiled | Much faster | Direct machine code |
| Async → Sync | Context-dependent | May lose concurrency benefits |
| Class hierarchy → Enums | Often faster | Better cache locality |

### Common Performance Pitfalls

#### 1. Unnecessary Cloning

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

#### 2. String Allocation Overhead

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
```

#### 3. Dynamic Dispatch Overhead

```rust
// ❌ Trait objects when static dispatch is possible
fn process(handler: &dyn Handler) { ... }

// ✓ Generics for static dispatch (when possible)
fn process<H: Handler>(handler: &H) { ... }
```

#### 4. Inefficient Collection Choice

| Need | Wrong Choice | Right Choice |
|------|-------------|--------------|
| Fast lookup by key | `Vec` + linear search | `HashMap` |
| Ordered iteration | `HashMap` | `BTreeMap` or `Vec` |
| Unique values | `Vec` + contains check | `HashSet` |
| Stack behavior | `VecDeque` | `Vec` (push/pop) |
| Queue behavior | `Vec` | `VecDeque` |

### Benchmarking After Conversion

Always benchmark converted code:

```rust
// Rust: criterion for benchmarks
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn benchmark_conversion(c: &mut Criterion) {
    c.bench_function("converted_function", |b| {
        b.iter(|| converted_function(black_box(input)))
    });
}

criterion_group!(benches, benchmark_conversion);
criterion_main!(benches);
```

---

## Language-Specific Gotchas

### Python → Rust

| Python Behavior | Rust Reality | Mitigation |
|-----------------|--------------|------------|
| Arbitrary precision integers | Fixed-size (i32, i64, i128) | Use `num-bigint` if needed |
| Everything is an object | Primitives are stack-allocated | Embrace value semantics |
| Duck typing | Strict static types | Use generics and traits |
| `None` is everywhere | `Option<T>` is explicit | Map None → None, value → Some(value) |
| Exceptions unwind the stack | Panics are for bugs, Results for errors | Use Result<T, E> everywhere |
| GIL limits threading | True parallelism | Use rayon for data parallelism |

### TypeScript → Rust

| TypeScript Behavior | Rust Reality | Mitigation |
|--------------------|--------------|------------|
| `any` escape hatch | No equivalent | Use enums or generics |
| Optional properties | All fields required | Use `Option<T>` for optional |
| Structural typing | Nominal typing | Define explicit types |
| Prototype inheritance | No inheritance | Use composition and traits |
| `undefined` vs `null` | Only `None` | Both map to `Option<T>` |
| Mutable by default | Immutable by default | Use `let mut` explicitly |

### Go → Rust

| Go Behavior | Rust Reality | Mitigation |
|-------------|--------------|------------|
| `nil` for zero values | No implicit nil | Use `Default` trait or Option |
| Interface satisfaction implicit | Explicit impl blocks | impl Trait for Type |
| Goroutines lightweight | async tasks or threads | Use tokio::spawn or rayon |
| Error as return value | Result<T, E> | Similar pattern, more type-safe |
| No generics (pre-1.18) | Full generics | Take advantage of them |
| Defer for cleanup | RAII (Drop trait) | Resources clean up automatically |

---

## Skill Template

When creating a new `convert-X-Y` skill, use this template:

```markdown
---
name: convert-<source>-<target>
description: Convert <Source> code to <Target>. Use when migrating <Source> projects to <Target>, translating <Source> patterns to idiomatic <Target>, or refactoring <Source> codebases into <Target>. Extends meta-convert-dev with <Source>-to-<Target> specific patterns.
---

# Convert <Source> to <Target>

Convert <Source> code to idiomatic <Target>. This skill extends `meta-convert-dev` with <Source>-to-<Target> specific type mappings, idiom translations, and tooling.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

## This Skill Adds

- **Type mappings**: <Source> types → <Target> types
- **Idiom translations**: <Source> patterns → idiomatic <Target>
- **Error handling**: <Source> exceptions/errors → <Target> approach
- **Async patterns**: <Source> async → <Target> async
- **Tooling**: <Source>-to-<Target> specific tools

## Quick Reference

| <Source> | <Target> | Notes |
|----------|----------|-------|
| `<type1>` | `<type1>` | ... |
| `<type2>` | `<type2>` | ... |

## [Continue with detailed sections...]
```

---

## Reference Documentation

This skill includes detailed reference documents for common conversion topics:

| Document | Purpose |
|----------|---------|
| [`references/migration-strategies.md`](references/migration-strategies.md) | Incremental vs full rewrite decision framework |
| [`references/naming-conventions.md`](references/naming-conventions.md) | Case style and naming translation tables |
| [`references/build-system-mapping.md`](references/build-system-mapping.md) | Package manifest and dependency translation |
| [`references/module-system-comparison.md`](references/module-system-comparison.md) | Import/export and visibility patterns |
| [`references/performance-considerations.md`](references/performance-considerations.md) | Optimization and profiling guidance |

---

## References

### Skills That Extend This Meta-Skill

These skills provide concrete, language-pair-specific implementations:

- `convert-typescript-rust` - TypeScript → Rust conversion
- `convert-typescript-python` - TypeScript → Python conversion
- `convert-typescript-golang` - TypeScript → Go conversion
- `convert-golang-rust` - Go → Rust conversion
- `convert-python-rust` - Python → Rust conversion

### Related Meta-Skills

- `meta-library-dev` - Library development patterns

### Language Skills

For language-specific fundamentals (not conversion):

- `lang-typescript-dev` - TypeScript development patterns
- `lang-python-dev` - Python development patterns
- `lang-golang-dev` - Go development patterns
- `lang-rust-dev` - Rust development patterns

### Commands

- `/create-lang-conversion-skill <source> <target>` - Create a new conversion skill using this meta-skill as foundation
