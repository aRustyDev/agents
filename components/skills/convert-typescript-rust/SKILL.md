---
name: convert-typescript-rust
description: Convert TypeScript code to idiomatic Rust. Use when migrating TypeScript projects to Rust, translating TypeScript patterns to idiomatic Rust, or refactoring TypeScript codebases. Extends meta-convert-dev with TypeScript-to-Rust specific patterns.
---

# Convert TypeScript to Rust

Convert TypeScript code to idiomatic Rust. This skill extends `meta-convert-dev` with TypeScript-to-Rust specific type mappings, idiom translations, and tooling.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: TypeScript types → Rust types
- **Idiom translations**: TypeScript patterns → idiomatic Rust
- **Error handling**: TypeScript exceptions → Rust Result types
- **Async patterns**: TypeScript Promise/async → Rust Future with tokio
- **Memory/Ownership**: JavaScript GC → Rust ownership and borrowing

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- TypeScript language fundamentals - see `lang-typescript-dev`
- Rust language fundamentals - see `lang-rust-dev`
- Reverse conversion (Rust → TypeScript) - see `convert-rust-typescript`

---

## Quick Reference

| TypeScript | Rust | Notes |
|------------|------|-------|
| `string` | `String` / `&str` | Owned vs borrowed |
| `number` | `i32` / `f64` | Specify precision |
| `boolean` | `bool` | Direct mapping |
| `T[]` | `Vec<T>` | Growable array |
| `readonly T[]` | `&[T]` | Borrowed slice |
| `T \| null` | `Option<T>` | Nullable types |
| `T \| U` | `enum { A(T), B(U) }` | Tagged union |
| `Promise<T>` | `Future<Output=T>` | Async with tokio |
| `interface X` | `struct X` / `trait X` | Depends on usage |
| `class X` | `struct X` + `impl` | No inheritance |
| `Map<K, V>` | `HashMap<K, V>` | Hash-based map |
| `Set<T>` | `HashSet<T>` | Unique values |
| `any` | - | Avoid; use generics |
| `void` | `()` | Unit type |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - create type equivalence table
3. **Preserve semantics** over syntax similarity
4. **Adopt Rust idioms** - don't write "TypeScript code in Rust syntax"
5. **Handle edge cases** - null/undefined, error paths, resource cleanup
6. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| TypeScript | Rust | Notes |
|------------|------|-------|
| `string` | `String` | Owned, heap-allocated UTF-8 |
| `string` | `&str` | Borrowed string slice (prefer for parameters) |
| `number` | `i32` | Default signed 32-bit integer |
| `number` | `i64` | Large integers |
| `number` | `u32` / `u64` | Unsigned integers |
| `number` | `f32` / `f64` | Floating point (f64 default) |
| `bigint` | `i128` / `u128` | 128-bit integers |
| `bigint` | `num_bigint::BigInt` | Arbitrary precision |
| `boolean` | `bool` | Direct mapping |
| `null` | - | Use `Option<T>` |
| `undefined` | - | Use `Option<T>` |
| `symbol` | - | No direct equivalent |
| `any` | - | Avoid; use generics or enums |
| `unknown` | - | Use generics with trait bounds |
| `never` | `!` | Never type (unstable feature) |
| `void` | `()` | Unit type |

### Collection Types

| TypeScript | Rust | Notes |
|------------|------|-------|
| `T[]` | `Vec<T>` | Owned, growable array |
| `readonly T[]` | `&[T]` | Borrowed slice (immutable view) |
| `[T, U]` | `(T, U)` | Tuple (fixed size) |
| `[T, U, V]` | `(T, U, V)` | Tuple with 3+ elements |
| `Array<T>` | `Vec<T>` | Same as `T[]` |
| `ReadonlyArray<T>` | `&[T]` | Same as `readonly T[]` |
| `Map<K, V>` | `HashMap<K, V>` | Hash-based map |
| `Map<K, V>` | `BTreeMap<K, V>` | Sorted map |
| `Set<T>` | `HashSet<T>` | Hash-based set |
| `Set<T>` | `BTreeSet<T>` | Sorted set |
| `Record<K, V>` | `HashMap<K, V>` | Object as map |
| `Partial<T>` | `Option<T>` for each field | All fields optional |

### Composite Types

| TypeScript | Rust | Notes |
|------------|------|-------|
| `interface X { ... }` | `struct X { ... }` | Data-only types |
| `interface X { method(): T }` | `trait X { fn method(&self) -> T }` | Behavior contracts |
| `class X implements Y` | `struct X` + `impl Y for X` | Implementation |
| `class X extends Y` | Composition | Rust avoids inheritance |
| `abstract class X` | `trait X` | Abstract contracts |
| `T \| U` | `enum { A(T), B(U) }` | Tagged union (sum type) |
| `T & U` | `struct { ...T, ...U }` | Intersection (limited) |
| `type X = ...` | `type X = ...` | Type alias |
| `enum X { A, B }` | `enum X { A, B }` | Similar but different |
| `T extends U ? V : W` | - | No conditional types |

### Generic Type Mappings

| TypeScript | Rust | Notes |
|------------|------|-------|
| `<T>` | `<T>` | Unconstrained generic |
| `<T extends U>` | `<T: U>` | Trait bound |
| `<T extends A & B>` | `<T: A + B>` | Multiple trait bounds |
| `<T = Default>` | `<T = Default>` | Default type parameter |
| `<T extends keyof U>` | - | No direct equivalent |
| `Array<T>` | `Vec<T>` | Generic array |
| `Promise<T>` | `Future<Output = T>` | Generic future |
| `Readonly<T>` | `&T` | Immutable borrow |
| `Pick<T, K>` | - | Manual struct creation |
| `Omit<T, K>` | - | Manual struct creation |

### Special TypeScript Types → Rust

| TypeScript | Rust | Strategy |
|------------|------|----------|
| `any` | Avoid | Use `enum` for known variants, generics for flexibility |
| `unknown` | `T: ?Sized` or generics | Bounded generics safer |
| `object` | `HashMap<String, Value>` | For dynamic objects |
| `Function` | `Fn()` / `FnMut()` / `FnOnce()` | Depends on usage |
| `constructor` | `new()` method or `Default` | Associated function |
| `this` in methods | `&self` / `&mut self` / `self` | Explicit receiver |

---

## Idiom Translation

### Pattern 1: Null/Undefined Handling

**TypeScript:**
```typescript
function findUser(id: string): User | null {
  const user = users.find(u => u.id === id);
  return user ?? null;
}

const name = user?.name ?? "Anonymous";
```

**Rust:**
```rust
fn find_user(id: &str) -> Option<&User> {
    users.iter().find(|u| u.id == id)
}

let name = user.as_ref()
    .map(|u| u.name.as_str())
    .unwrap_or("Anonymous");
```

**Why this translation:**
- TypeScript's `null` and `undefined` both map to Rust's `Option<T>`
- Option combinators (`map`, `unwrap_or`) replace optional chaining
- Rust's borrow checker requires explicit ownership decisions (`&User` vs `User`)

### Pattern 2: Array Methods

**TypeScript:**
```typescript
const result = items
  .filter(x => x.active)
  .map(x => x.value)
  .reduce((sum, val) => sum + val, 0);
```

**Rust:**
```rust
let result: i32 = items.iter()
    .filter(|x| x.active)
    .map(|x| x.value)
    .sum();
```

**Why this translation:**
- Iterator adaptors are zero-cost abstractions in Rust
- `.iter()` creates a borrowed iterator (doesn't consume the collection)
- `.sum()` is specialized and more efficient than manual reduce
- Type annotation may be needed for `sum()` to infer the result type

### Pattern 3: Object Destructuring

**TypeScript:**
```typescript
const { name, age } = user;
const { x, y, ...rest } = point;
```

**Rust:**
```rust
let User { name, age, .. } = user;

// Rest pattern not directly supported
// Instead, extract what you need:
let Point { x, y, .. } = point;
```

**Why this translation:**
- Rust supports struct destructuring but not rest patterns
- Use `..` to ignore remaining fields
- For true "rest" behavior, manually construct a new struct

### Pattern 4: Default Parameters

**TypeScript:**
```typescript
function greet(name: string = "World"): string {
  return `Hello, ${name}!`;
}
```

**Rust:**
```rust
fn greet(name: Option<&str>) -> String {
    format!("Hello, {}!", name.unwrap_or("World"))
}

// Or with multiple functions:
fn greet_default() -> String {
    greet_with_name("World")
}

fn greet_with_name(name: &str) -> String {
    format!("Hello, {}!", name)
}

// Or using Default trait for complex types:
fn process(config: Option<Config>) -> Result<()> {
    let config = config.unwrap_or_default();
    // ...
}
```

**Why this translation:**
- Rust doesn't have default parameters
- Use `Option<T>` to make parameters optional
- Use `Default` trait for complex types with sensible defaults
- Consider multiple function variants for different arities

### Pattern 5: Template Literals

**TypeScript:**
```typescript
const message = `User ${user.name} has ${user.points} points`;
```

**Rust:**
```rust
let message = format!("User {} has {} points", user.name, user.points);
```

**Why this translation:**
- `format!` macro provides type-safe string formatting
- Display trait must be implemented for custom types
- More verbose but catches type errors at compile time

### Pattern 6: Object Literals

**TypeScript:**
```typescript
const point = { x: 10, y: 20 };
const user = {
  name,
  age,
  greet() { return `Hello, ${this.name}`; }
};
```

**Rust:**
```rust
let point = Point { x: 10, y: 20 };

// Field init shorthand
let user = User { name, age };

// Methods defined in impl block
struct User {
    name: String,
    age: u32,
}

impl User {
    fn greet(&self) -> String {
        format!("Hello, {}", self.name)
    }
}
```

**Why this translation:**
- Rust separates data (struct) from behavior (impl)
- Methods require explicit `self` parameter
- No implicit `this` binding

### Pattern 7: Class Inheritance → Composition

**TypeScript:**
```typescript
class Animal {
  constructor(public name: string) {}
  speak(): string { return "Some sound"; }
}

class Dog extends Animal {
  speak(): string { return "Woof!"; }
}
```

**Rust:**
```rust
trait Animal {
    fn speak(&self) -> &str;
}

struct Dog {
    name: String,
}

impl Animal for Dog {
    fn speak(&self) -> &str {
        "Woof!"
    }
}

// For shared data, use composition:
struct AnimalData {
    name: String,
}

struct Dog {
    data: AnimalData,
}

impl Dog {
    fn name(&self) -> &str {
        &self.data.name
    }
}
```

**Why this translation:**
- Rust uses composition over inheritance
- Traits define shared behavior
- Structs can contain other structs for data sharing
- Delegation requires explicit methods

### Pattern 8: Method Chaining with Builder Pattern

**TypeScript:**
```typescript
const request = new RequestBuilder()
  .url("https://api.example.com")
  .method("POST")
  .header("Content-Type", "application/json")
  .build();
```

**Rust:**
```rust
let request = RequestBuilder::new()
    .url("https://api.example.com")
    .method("POST")
    .header("Content-Type", "application/json")
    .build();

// Builder implementation:
impl RequestBuilder {
    fn new() -> Self {
        RequestBuilder::default()
    }

    fn url(mut self, url: &str) -> Self {
        self.url = url.to_string();
        self
    }

    fn method(mut self, method: &str) -> Self {
        self.method = method.to_string();
        self
    }

    fn build(self) -> Request {
        Request { /* ... */ }
    }
}
```

**Why this translation:**
- Builder pattern is idiomatic in both languages
- Rust builders consume `self` and return `Self` for chaining
- Final `build()` consumes the builder

### Pattern 9: Async Iteration

**TypeScript:**
```typescript
async function* fetchPages(): AsyncIterable<Page> {
  let page = 1;
  while (true) {
    const data = await fetch(`/api/pages/${page}`);
    if (!data.ok) break;
    yield await data.json();
    page++;
  }
}

for await (const page of fetchPages()) {
  process(page);
}
```

**Rust:**
```rust
use futures::stream::{Stream, StreamExt};
use futures::stream;

fn fetch_pages() -> impl Stream<Item = Page> {
    stream::unfold(1, |page| async move {
        let url = format!("/api/pages/{}", page);
        match reqwest::get(&url).await {
            Ok(resp) if resp.status().is_success() => {
                let data: Page = resp.json().await.ok()?;
                Some((data, page + 1))
            }
            _ => None,
        }
    })
}

// Consuming the stream:
let mut pages = fetch_pages();
while let Some(page) = pages.next().await {
    process(page);
}
```

**Why this translation:**
- Rust uses Stream from futures crate for async iteration
- `stream::unfold` creates stateful streams
- `while let Some(...)` pattern for consuming streams

### Pattern 10: Namespace/Module Organization

**TypeScript:**
```typescript
// math.ts
export namespace Math {
  export function add(a: number, b: number): number {
    return a + b;
  }

  export const PI = 3.14159;
}

// usage
import { Math } from './math';
Math.add(1, 2);
```

**Rust:**
```rust
// math.rs
pub mod math {
    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }

    pub const PI: f64 = 3.14159;
}

// usage
use crate::math;
math::add(1, 2);

// Or with glob import:
use crate::math::*;
add(1, 2);
```

**Why this translation:**
- Rust modules are file-based or inline
- `pub` keyword controls visibility
- `use` statements import items into scope

---

## Error Handling

### TypeScript Exception Model → Rust Result Type

TypeScript uses exceptions for error handling, while Rust uses the `Result<T, E>` type for recoverable errors and panics for unrecoverable errors.

| TypeScript | Rust | Use Case |
|------------|------|----------|
| `throw new Error()` | `return Err(...)` | Recoverable errors |
| `try/catch` | `match result { Ok(..) => .., Err(..) => .. }` | Error handling |
| `try/catch` | `result?` | Error propagation |
| Uncaught exception | `panic!()` | Unrecoverable errors |
| `finally` | Drop trait | Resource cleanup |

### Basic Error Translation

**TypeScript:**
```typescript
function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error("Division by zero");
  }
  return a / b;
}

try {
  const result = divide(10, 0);
  console.log(result);
} catch (e) {
  console.error("Error:", e.message);
}
```

**Rust:**
```rust
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        return Err("Division by zero".to_string());
    }
    Ok(a / b)
}

match divide(10.0, 0.0) {
    Ok(result) => println!("{}", result),
    Err(e) => eprintln!("Error: {}", e),
}

// Or with error propagation:
fn calculate() -> Result<f64, String> {
    let result = divide(10.0, 2.0)?;  // ? propagates errors
    Ok(result * 2.0)
}
```

### Custom Error Types

**TypeScript:**
```typescript
class AppError extends Error {
  constructor(message: string, public code: string) {
    super(message);
    this.name = "AppError";
  }
}

class NotFoundError extends AppError {
  constructor(resource: string) {
    super(`${resource} not found`, "NOT_FOUND");
  }
}

class ValidationError extends AppError {
  constructor(message: string) {
    super(message, "VALIDATION_ERROR");
  }
}

function getUser(id: string): User {
  if (!id) {
    throw new ValidationError("User ID is required");
  }
  const user = users.find(u => u.id === id);
  if (!user) {
    throw new NotFoundError("User");
  }
  return user;
}
```

**Rust:**
```rust
use thiserror::Error;

#[derive(Debug, Error)]
enum AppError {
    #[error("{resource} not found")]
    NotFound { resource: String },

    #[error("validation failed: {message}")]
    Validation { message: String },

    #[error(transparent)]
    Io(#[from] std::io::Error),

    #[error(transparent)]
    Parse(#[from] serde_json::Error),
}

fn get_user(id: &str) -> Result<User, AppError> {
    if id.is_empty() {
        return Err(AppError::Validation {
            message: "User ID is required".to_string(),
        });
    }

    users.iter()
        .find(|u| u.id == id)
        .cloned()
        .ok_or_else(|| AppError::NotFound {
            resource: "User".to_string(),
        })
}
```

**Why this translation:**
- `thiserror` crate provides ergonomic error types
- Enum variants replace class hierarchy
- `#[from]` enables automatic conversion from other error types
- `?` operator works seamlessly with custom error types

### Error Context and Wrapping

**TypeScript:**
```typescript
async function loadConfig(path: string): Promise<Config> {
  try {
    const content = await fs.readFile(path, 'utf-8');
    return JSON.parse(content);
  } catch (e) {
    throw new Error(`Failed to load config from ${path}: ${e.message}`);
  }
}
```

**Rust:**
```rust
use anyhow::{Context, Result};

async fn load_config(path: &Path) -> Result<Config> {
    let content = tokio::fs::read_to_string(path).await
        .context(format!("Failed to read config from {}", path.display()))?;

    let config = serde_json::from_str(&content)
        .context("Failed to parse config JSON")?;

    Ok(config)
}

// Alternative with custom error type:
async fn load_config_custom(path: &Path) -> Result<Config, ConfigError> {
    let content = tokio::fs::read_to_string(path).await
        .map_err(|e| ConfigError::ReadFailed {
            path: path.to_owned(),
            source: e,
        })?;

    serde_json::from_str(&content)
        .map_err(|e| ConfigError::ParseFailed {
            path: path.to_owned(),
            source: e,
        })
}
```

**Why this translation:**
- `anyhow` provides `.context()` for adding error context
- `map_err` transforms error types
- Error chains preserve the original error

---

## Async Patterns

### Promise → Future with tokio

TypeScript uses Promises and `async/await` for asynchronous operations. Rust uses Futures with async runtimes like tokio.

| TypeScript | Rust (tokio) | Notes |
|------------|--------------|-------|
| `Promise<T>` | `Future<Output = T>` | Lazy evaluation |
| `async function` | `async fn` | Async function syntax |
| `await promise` | `promise.await` | Await syntax |
| `Promise.all([...])` | `tokio::join!(...)` | Concurrent execution |
| `Promise.race([...])` | `tokio::select!` | First to complete |
| `Promise.resolve(x)` | `async { x }` | Immediate future |
| `Promise.reject(e)` | `async { Err(e) }` | Immediate error |
| `new Promise((resolve, reject) => ...)` | Manual Future impl | Rare |
| `setTimeout` | `tokio::time::sleep` | Delayed execution |

### Basic Async Translation

**TypeScript:**
```typescript
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/users/${id}`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

async function main() {
  try {
    const user = await fetchUser("123");
    console.log(user);
  } catch (e) {
    console.error("Failed:", e);
  }
}
```

**Rust:**
```rust
use reqwest;

async fn fetch_user(id: &str) -> Result<User, reqwest::Error> {
    let response = reqwest::get(format!("/users/{}", id)).await?;
    response.error_for_status()?.json::<User>().await
}

#[tokio::main]
async fn main() {
    match fetch_user("123").await {
        Ok(user) => println!("{:?}", user),
        Err(e) => eprintln!("Failed: {}", e),
    }
}
```

**Why this translation:**
- `#[tokio::main]` macro sets up async runtime
- `.await` is a postfix operator in Rust
- `?` propagates errors in async context
- reqwest provides ergonomic HTTP client

### Parallel Execution

**TypeScript:**
```typescript
async function fetchAll(): Promise<[User[], Order[]]> {
  const [users, orders] = await Promise.all([
    fetchUsers(),
    fetchOrders(),
  ]);
  return [users, orders];
}

// With individual error handling:
async function fetchAllSafe() {
  const results = await Promise.allSettled([
    fetchUsers(),
    fetchOrders(),
  ]);

  results.forEach((result, i) => {
    if (result.status === 'rejected') {
      console.error(`Task ${i} failed:`, result.reason);
    }
  });
}
```

**Rust:**
```rust
async fn fetch_all() -> Result<(Vec<User>, Vec<Order>), Error> {
    let (users, orders) = tokio::try_join!(
        fetch_users(),
        fetch_orders(),
    )?;
    Ok((users, orders))
}

// Non-failing version (both must succeed):
async fn fetch_all_join() -> (Result<Vec<User>>, Result<Vec<Order>>) {
    tokio::join!(
        fetch_users(),
        fetch_orders(),
    )
}

// With individual error handling:
async fn fetch_all_safe() {
    let (users_result, orders_result) = tokio::join!(
        fetch_users(),
        fetch_orders(),
    );

    match users_result {
        Ok(users) => println!("Got {} users", users.len()),
        Err(e) => eprintln!("Users failed: {}", e),
    }

    match orders_result {
        Ok(orders) => println!("Got {} orders", orders.len()),
        Err(e) => eprintln!("Orders failed: {}", e),
    }
}
```

**Why this translation:**
- `tokio::try_join!` fails fast if any future fails
- `tokio::join!` waits for all futures, returning individual Results
- More explicit about error handling strategy

### Timeout and Cancellation

**TypeScript:**
```typescript
async function fetchWithTimeout(
  url: string,
  timeoutMs: number
): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, { signal: controller.signal });
    return response;
  } finally {
    clearTimeout(timeout);
  }
}
```

**Rust:**
```rust
use tokio::time::{timeout, Duration};

async fn fetch_with_timeout(
    url: &str,
    timeout_ms: u64,
) -> Result<reqwest::Response, FetchError> {
    timeout(
        Duration::from_millis(timeout_ms),
        reqwest::get(url)
    )
    .await
    .map_err(|_| FetchError::Timeout)?
    .map_err(FetchError::Request)
}

// With select for more control:
use tokio::select;

async fn fetch_with_cancel(
    url: &str,
    mut cancel: tokio::sync::oneshot::Receiver<()>,
) -> Result<reqwest::Response, FetchError> {
    select! {
        result = reqwest::get(url) => {
            result.map_err(FetchError::Request)
        }
        _ = &mut cancel => {
            Err(FetchError::Cancelled)
        }
    }
}
```

**Why this translation:**
- `tokio::time::timeout` provides built-in timeout
- `tokio::select!` for custom cancellation logic
- Dropping a future cancels it (structured concurrency)

### Sequential Async Operations

**TypeScript:**
```typescript
async function processItems(items: Item[]): Promise<Result[]> {
  const results: Result[] = [];

  for (const item of items) {
    const result = await processItem(item);
    results.push(result);
  }

  return results;
}
```

**Rust:**
```rust
async fn process_items(items: Vec<Item>) -> Result<Vec<ItemResult>> {
    let mut results = Vec::new();

    for item in items {
        let result = process_item(item).await?;
        results.push(result);
    }

    Ok(results)
}

// Or using futures::stream for better control:
use futures::stream::{self, StreamExt};

async fn process_items_stream(items: Vec<Item>) -> Result<Vec<ItemResult>> {
    stream::iter(items)
        .then(|item| process_item(item))
        .collect::<Vec<_>>()
        .await
}
```

**Why this translation:**
- Direct for loop works for sequential processing
- `futures::stream` provides combinators for complex flows
- `?` operator works in async context

---

## Memory & Ownership

### TypeScript GC → Rust Ownership

TypeScript relies on garbage collection, while Rust uses ownership and borrowing for memory safety.

| Concept | TypeScript | Rust |
|---------|------------|------|
| Memory allocation | Automatic (GC) | Explicit (ownership) |
| Sharing references | Freely shared | Borrowed (&) or shared (Arc) |
| Mutation | Mutable by default | Immutable by default (`mut`) |
| Lifetime | GC determines | Compile-time lifetimes |
| Resource cleanup | Finalizers (unreliable) | RAII (Drop trait) |
| Circular references | Allowed (ref counting handles) | Prevented by borrow checker |

### Ownership Decision Tree

```
When converting TypeScript to Rust:

1. Is this data shared across components?
   ├─ YES → Consider Arc<T> (thread-safe) or Rc<T> (single-thread)
   └─ NO → Single owner, use moves

2. Is this data mutated by multiple parts?
   ├─ YES → Arc<Mutex<T>> or Arc<RwLock<T>>
   └─ NO → Immutable borrows (&T)

3. Does this data outlive its creator?
   ├─ YES → Return owned value or use 'static
   └─ NO → Return borrowed reference (&T)

4. Is this a callback that captures environment?
   ├─ YES → Use closures with appropriate captures
   └─ NO → Function pointer
```

### Pattern: Sharing Data

**TypeScript:**
```typescript
class Cache {
  private data: Map<string, User> = new Map();

  get(id: string): User | undefined {
    return this.data.get(id);
  }

  set(id: string, user: User): void {
    this.data.set(id, user);
  }
}

// Multiple references to the same cache
const cache = new Cache();
const service1 = new UserService(cache);
const service2 = new OrderService(cache);
```

**Rust:**
```rust
use std::collections::HashMap;
use std::sync::{Arc, RwLock};

struct Cache {
    data: Arc<RwLock<HashMap<String, User>>>,
}

impl Cache {
    fn new() -> Self {
        Cache {
            data: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    fn get(&self, id: &str) -> Option<User> {
        self.data.read().unwrap()
            .get(id)
            .cloned()
    }

    fn set(&self, id: String, user: User) {
        self.data.write().unwrap()
            .insert(id, user);
    }
}

impl Clone for Cache {
    fn clone(&self) -> Self {
        Cache {
            data: Arc::clone(&self.data),
        }
    }
}

// Sharing cache across services
let cache = Cache::new();
let service1 = UserService::new(cache.clone());
let service2 = OrderService::new(cache.clone());
```

**Why this translation:**
- `Arc` enables shared ownership across threads
- `RwLock` allows multiple readers or single writer
- `.clone()` on `Arc` increments reference count (cheap)
- Explicit locking makes synchronization visible

### Pattern: Builder Pattern (Consuming self)

**TypeScript:**
```typescript
class RequestBuilder {
  private url?: string;
  private method?: string;
  private headers: Record<string, string> = {};

  setUrl(url: string): this {
    this.url = url;
    return this;
  }

  setMethod(method: string): this {
    this.method = method;
    return this;
  }

  build(): Request {
    if (!this.url) throw new Error("URL is required");
    return new Request(this.url, this.method, this.headers);
  }
}
```

**Rust:**
```rust
struct RequestBuilder {
    url: Option<String>,
    method: Option<String>,
    headers: HashMap<String, String>,
}

impl RequestBuilder {
    fn new() -> Self {
        RequestBuilder {
            url: None,
            method: None,
            headers: HashMap::new(),
        }
    }

    fn url(mut self, url: impl Into<String>) -> Self {
        self.url = Some(url.into());
        self
    }

    fn method(mut self, method: impl Into<String>) -> Self {
        self.method = Some(method.into());
        self
    }

    fn build(self) -> Result<Request, &'static str> {
        let url = self.url.ok_or("URL is required")?;
        Ok(Request {
            url,
            method: self.method.unwrap_or_else(|| "GET".to_string()),
            headers: self.headers,
        })
    }
}

// Usage:
let request = RequestBuilder::new()
    .url("https://api.example.com")
    .method("POST")
    .build()?;
```

**Why this translation:**
- Methods take `self` by value and return `Self` for chaining
- Final `build()` consumes the builder
- Can't accidentally reuse builder after building

### Pattern: RAII Resource Management

**TypeScript:**
```typescript
class FileHandle {
  private fd: number;

  constructor(path: string) {
    this.fd = fs.openSync(path, 'r');
  }

  read(): Buffer {
    return fs.readFileSync(this.fd);
  }

  close(): void {
    fs.closeSync(this.fd);
  }
}

// Manual cleanup required:
const file = new FileHandle('data.txt');
try {
  const data = file.read();
  process(data);
} finally {
  file.close();
}
```

**Rust:**
```rust
use std::fs::File;
use std::io::Read;

struct FileHandle {
    file: File,
}

impl FileHandle {
    fn new(path: &str) -> std::io::Result<Self> {
        Ok(FileHandle {
            file: File::open(path)?,
        })
    }

    fn read(&mut self) -> std::io::Result<Vec<u8>> {
        let mut buffer = Vec::new();
        self.file.read_to_end(&mut buffer)?;
        Ok(buffer)
    }
}

// Drop trait automatically closes file
impl Drop for FileHandle {
    fn drop(&mut self) {
        // File's Drop is called automatically
        println!("FileHandle dropped, file closed");
    }
}

// No explicit close needed:
{
    let mut file = FileHandle::new("data.txt")?;
    let data = file.read()?;
    process(data);
}  // file automatically closed here
```

**Why this translation:**
- Drop trait ensures cleanup happens automatically
- Scope-based resource management (RAII)
- No need for try/finally
- Resources cleaned up in reverse order of creation

### Pattern: Avoiding Clones

**TypeScript (doesn't apply):**
```typescript
function processUsers(users: User[]): void {
  // TypeScript freely shares references
  for (const user of users) {
    analyzeUser(user);
    validateUser(user);
    saveUser(user);
  }
}
```

**Rust (inefficient):**
```rust
// ❌ Unnecessary cloning
fn process_users_bad(users: Vec<User>) {
    for user in users.clone() {
        analyze_user(&user.clone());
        validate_user(&user.clone());
        save_user(&user.clone());
    }
}
```

**Rust (efficient):**
```rust
// ✓ Use references
fn process_users(users: &[User]) {
    for user in users {
        analyze_user(user);
        validate_user(user);
        save_user(user);
    }
}

fn analyze_user(user: &User) { /* ... */ }
fn validate_user(user: &User) { /* ... */ }
fn save_user(user: &User) { /* ... */ }
```

**Why this matters:**
- Cloning in Rust is explicit and potentially expensive
- Prefer borrowing (`&T`) when you don't need ownership
- Use slices (`&[T]`) instead of owned vectors when possible

---

## Common Pitfalls

### 1. Over-cloning to Satisfy Borrow Checker

**Problem:** Coming from TypeScript, new Rust developers often clone excessively to avoid borrow checker errors.

**Example:**
```rust
// ❌ Bad: Cloning everything
fn get_full_name_bad(user: &User) -> String {
    let first = user.first_name.clone();
    let last = user.last_name.clone();
    format!("{} {}", first, last)
}

// ✓ Good: Borrow instead
fn get_full_name(user: &User) -> String {
    format!("{} {}", user.first_name, user.last_name)
}
```

**Solution:** Learn to work with references. Clone only when you truly need owned data.

### 2. Fighting the Borrow Checker with Mutation

**Problem:** Trying to mutate data while holding immutable borrows.

**Example:**
```rust
// ❌ Won't compile
fn process_bad(items: &mut Vec<Item>) {
    for item in items.iter() {  // Immutable borrow
        items.push(item.clone());  // Error: mutable borrow while immutable borrow exists
    }
}

// ✓ Good: Collect then extend
fn process_good(items: &mut Vec<Item>) {
    let to_add: Vec<Item> = items.iter()
        .map(|item| item.clone())
        .collect();
    items.extend(to_add);
}
```

**Solution:** Separate reading and writing phases, or use indices instead of iterators.

### 3. Misunderstanding String vs &str

**Problem:** Using `String` everywhere when `&str` would be more appropriate.

**Example:**
```rust
// ❌ Bad: Forces caller to own strings
fn greet_bad(name: String) -> String {
    format!("Hello, {}!", name)
}

// ✓ Good: Accepts borrowed strings
fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

// Usage:
let name = "Alice";
greet(name);  // Works with &str
greet(&String::from("Bob"));  // Also works with String
```

**Solution:** Use `&str` for parameters unless you need to own the string.

### 4. Ignoring Error Types

**Problem:** Using `String` for all errors instead of proper error types.

**Example:**
```rust
// ❌ Bad: String errors
fn parse_config_bad(path: &str) -> Result<Config, String> {
    let content = std::fs::read_to_string(path)
        .map_err(|e| e.to_string())?;
    serde_json::from_str(&content)
        .map_err(|e| e.to_string())
}

// ✓ Good: Proper error types
use thiserror::Error;

#[derive(Debug, Error)]
enum ConfigError {
    #[error("failed to read config file")]
    Io(#[from] std::io::Error),

    #[error("failed to parse config")]
    Parse(#[from] serde_json::Error),
}

fn parse_config(path: &str) -> Result<Config, ConfigError> {
    let content = std::fs::read_to_string(path)?;
    let config = serde_json::from_str(&content)?;
    Ok(config)
}
```

**Solution:** Use `thiserror` or `anyhow` for proper error handling.

### 5. Not Leveraging Pattern Matching

**Problem:** Using if/else chains instead of pattern matching.

**Example:**
```rust
// ❌ Bad: Nested if/else
fn handle_response_bad(response: Response) -> String {
    if response.status == 200 {
        response.body
    } else if response.status == 404 {
        "Not found".to_string()
    } else if response.status >= 500 {
        "Server error".to_string()
    } else {
        "Unknown error".to_string()
    }
}

// ✓ Good: Pattern matching
fn handle_response(response: Response) -> String {
    match response.status {
        200 => response.body,
        404 => "Not found".to_string(),
        500..=599 => "Server error".to_string(),
        _ => "Unknown error".to_string(),
    }
}
```

**Solution:** Use `match` for clarity and exhaustiveness checking.

### 6. Not Using Iterator Combinators

**Problem:** Using manual loops when iterator methods would be clearer.

**Example:**
```rust
// ❌ Bad: Manual loop
fn sum_active_values_bad(items: &[Item]) -> i32 {
    let mut sum = 0;
    for item in items {
        if item.active {
            sum += item.value;
        }
    }
    sum
}

// ✓ Good: Iterator combinators
fn sum_active_values(items: &[Item]) -> i32 {
    items.iter()
        .filter(|item| item.active)
        .map(|item| item.value)
        .sum()
}
```

**Solution:** Learn iterator methods for cleaner, more functional code.

### 7. Forgetting to Handle Option/Result

**Problem:** Using `unwrap()` in production code.

**Example:**
```rust
// ❌ Bad: Will panic if None
fn get_user_name_bad(users: &[User], id: &str) -> String {
    users.iter()
        .find(|u| u.id == id)
        .unwrap()  // Panics if not found!
        .name
        .clone()
}

// ✓ Good: Proper error handling
fn get_user_name(users: &[User], id: &str) -> Option<String> {
    users.iter()
        .find(|u| u.id == id)
        .map(|u| u.name.clone())
}

// Or with Result:
fn get_user_name_result(users: &[User], id: &str) -> Result<String, UserError> {
    users.iter()
        .find(|u| u.id == id)
        .map(|u| u.name.clone())
        .ok_or(UserError::NotFound)
}
```

**Solution:** Use `?`, `map`, `and_then`, or match instead of `unwrap`.

### 8. Misunderstanding Async Runtimes

**Problem:** Forgetting to add `#[tokio::main]` or trying to call async from sync.

**Example:**
```rust
// ❌ Bad: Can't await without async runtime
fn main() {
    let result = fetch_data().await;  // Error: can't await outside async
}

// ✓ Good: Use tokio::main
#[tokio::main]
async fn main() {
    let result = fetch_data().await;
}

// For sync code calling async:
fn sync_wrapper() -> Result<Data> {
    tokio::runtime::Runtime::new()
        .unwrap()
        .block_on(async {
            fetch_data().await
        })
}
```

**Solution:** Use `#[tokio::main]` for main, or create a runtime for sync/async boundaries.

---

## Tooling

### TypeScript → Rust Transpilers

| Tool | Status | Notes |
|------|--------|-------|
| ts2rs | Experimental | Limited scope, not production-ready |
| Manual conversion | Recommended | No mature automated tool exists |

**Recommendation:** Manual conversion following this skill guide.

### Code Analysis Tools

| Category | TypeScript | Rust Equivalent |
|----------|------------|-----------------|
| AST Parsing | `typescript` compiler API, `ts-morph` | `syn`, `proc-macro2` |
| Linting | ESLint | Clippy (built-in) |
| Formatting | Prettier | rustfmt (built-in) |
| Type Checking | tsc | rustc |
| Testing | Jest, Vitest | cargo test (built-in) |
| Coverage | c8, nyc | cargo-tarpaulin, cargo-llvm-cov |
| Benchmarking | Benchmark.js | Criterion |

### Helpful Rust Crates for TypeScript Patterns

| Pattern | TypeScript | Rust Crate | Notes |
|---------|------------|------------|-------|
| JSON | `JSON.parse()` | `serde_json` | Serialization/deserialization |
| HTTP Client | `fetch`, `axios` | `reqwest` | Async HTTP client |
| HTTP Server | Express, Fastify | `axum`, `actix-web` | Web frameworks |
| Async Runtime | Built-in | `tokio`, `async-std` | Required for async |
| Error Handling | - | `thiserror`, `anyhow` | Ergonomic errors |
| CLI Parsing | `commander`, `yargs` | `clap` | Command-line parser |
| Logging | `winston`, `pino` | `tracing`, `log` | Structured logging |
| Date/Time | `Date`, `date-fns` | `chrono` | Date manipulation |
| UUID | `uuid` | `uuid` | UUID generation |
| Regex | Built-in | `regex` | Regular expressions |
| Environment | `dotenv` | `dotenvy` | .env file loading |
| Testing | `jest` | `rstest`, `proptest` | Enhanced testing |
| Mocking | `jest.mock()` | `mockall` | Mock objects |

### Development Workflow

| Stage | Command |
|-------|---------|
| Check syntax | `cargo check` |
| Run tests | `cargo test` |
| Run with output | `cargo run` |
| Lint | `cargo clippy` |
| Format | `cargo fmt` |
| Benchmark | `cargo bench` |
| Documentation | `cargo doc --open` |
| Watch mode | `cargo watch -x check -x test` |

---

## Examples

### Example 1: Simple - Basic CRUD Operations

**Before (TypeScript):**
```typescript
interface User {
  id: string;
  name: string;
  email: string;
}

class UserRepository {
  private users: Map<string, User> = new Map();

  create(user: User): void {
    this.users.set(user.id, user);
  }

  get(id: string): User | undefined {
    return this.users.get(id);
  }

  update(id: string, updates: Partial<User>): boolean {
    const user = this.users.get(id);
    if (!user) return false;

    this.users.set(id, { ...user, ...updates });
    return true;
  }

  delete(id: string): boolean {
    return this.users.delete(id);
  }
}
```

**After (Rust):**
```rust
use std::collections::HashMap;

#[derive(Debug, Clone)]
struct User {
    id: String,
    name: String,
    email: String,
}

struct UserRepository {
    users: HashMap<String, User>,
}

impl UserRepository {
    fn new() -> Self {
        UserRepository {
            users: HashMap::new(),
        }
    }

    fn create(&mut self, user: User) {
        self.users.insert(user.id.clone(), user);
    }

    fn get(&self, id: &str) -> Option<&User> {
        self.users.get(id)
    }

    fn update(&mut self, id: &str, name: Option<String>, email: Option<String>) -> bool {
        if let Some(user) = self.users.get_mut(id) {
            if let Some(n) = name {
                user.name = n;
            }
            if let Some(e) = email {
                user.email = e;
            }
            true
        } else {
            false
        }
    }

    fn delete(&mut self, id: &str) -> bool {
        self.users.remove(id).is_some()
    }
}
```

### Example 2: Medium - HTTP API Client with Error Handling

**Before (TypeScript):**
```typescript
interface ApiResponse<T> {
  data?: T;
  error?: string;
}

class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public response?: any
  ) {
    super(message);
  }
}

class ApiClient {
  constructor(private baseUrl: string) {}

  async get<T>(path: string): Promise<T> {
    try {
      const response = await fetch(`${this.baseUrl}${path}`);

      if (!response.ok) {
        throw new ApiError(
          `HTTP ${response.status}`,
          response.status,
          await response.text()
        );
      }

      const data: ApiResponse<T> = await response.json();

      if (data.error) {
        throw new ApiError(data.error, response.status);
      }

      if (!data.data) {
        throw new ApiError("No data in response", response.status);
      }

      return data.data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(`Network error: ${error.message}`, 0);
    }
  }

  async post<T, U>(path: string, body: T): Promise<U> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new ApiError(`HTTP ${response.status}`, response.status);
    }

    const data: ApiResponse<U> = await response.json();
    if (data.error || !data.data) {
      throw new ApiError(data.error || "Invalid response", response.status);
    }

    return data.data;
  }
}
```

**After (Rust):**
```rust
use reqwest;
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Deserialize)]
struct ApiResponse<T> {
    data: Option<T>,
    error: Option<String>,
}

#[derive(Debug, Error)]
enum ApiError {
    #[error("HTTP error {status}: {message}")]
    Http {
        status: u16,
        message: String,
        response: Option<String>,
    },

    #[error("API error: {0}")]
    Api(String),

    #[error("Network error: {0}")]
    Network(#[from] reqwest::Error),

    #[error("No data in response")]
    NoData,
}

struct ApiClient {
    base_url: String,
    client: reqwest::Client,
}

impl ApiClient {
    fn new(base_url: impl Into<String>) -> Self {
        ApiClient {
            base_url: base_url.into(),
            client: reqwest::Client::new(),
        }
    }

    async fn get<T>(&self, path: &str) -> Result<T, ApiError>
    where
        T: for<'de> Deserialize<'de>,
    {
        let url = format!("{}{}", self.base_url, path);
        let response = self.client.get(&url).send().await?;

        let status = response.status();
        if !status.is_success() {
            let text = response.text().await.ok();
            return Err(ApiError::Http {
                status: status.as_u16(),
                message: format!("HTTP {}", status),
                response: text,
            });
        }

        let api_response: ApiResponse<T> = response.json().await?;

        if let Some(error) = api_response.error {
            return Err(ApiError::Api(error));
        }

        api_response.data.ok_or(ApiError::NoData)
    }

    async fn post<T, U>(&self, path: &str, body: &T) -> Result<U, ApiError>
    where
        T: Serialize,
        U: for<'de> Deserialize<'de>,
    {
        let url = format!("{}{}", self.base_url, path);
        let response = self.client
            .post(&url)
            .json(body)
            .send()
            .await?;

        let status = response.status();
        if !status.is_success() {
            return Err(ApiError::Http {
                status: status.as_u16(),
                message: format!("HTTP {}", status),
                response: None,
            });
        }

        let api_response: ApiResponse<U> = response.json().await?;

        if let Some(error) = api_response.error {
            return Err(ApiError::Api(error));
        }

        api_response.data.ok_or(ApiError::NoData)
    }
}

// Usage:
#[tokio::main]
async fn main() -> Result<(), ApiError> {
    let client = ApiClient::new("https://api.example.com");

    let user: User = client.get("/users/123").await?;
    println!("User: {:?}", user);

    let new_user = CreateUserRequest {
        name: "Alice".to_string(),
        email: "alice@example.com".to_string(),
    };
    let created: User = client.post("/users", &new_user).await?;
    println!("Created: {:?}", created);

    Ok(())
}
```

### Example 3: Complex - Event-Driven Architecture with Async Streams

**Before (TypeScript):**
```typescript
interface Event {
  id: string;
  type: string;
  timestamp: Date;
  data: any;
}

type EventHandler<T = any> = (event: Event) => Promise<void>;

class EventBus {
  private handlers: Map<string, Set<EventHandler>> = new Map();
  private eventQueue: Event[] = [];
  private processing = false;

  subscribe(eventType: string, handler: EventHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }

    this.handlers.get(eventType)!.add(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.handlers.get(eventType);
      if (handlers) {
        handlers.delete(handler);
      }
    };
  }

  async publish(event: Event): Promise<void> {
    this.eventQueue.push(event);

    if (!this.processing) {
      await this.processQueue();
    }
  }

  private async processQueue(): Promise<void> {
    this.processing = true;

    while (this.eventQueue.length > 0) {
      const event = this.eventQueue.shift()!;
      const handlers = this.handlers.get(event.type);

      if (handlers) {
        // Process handlers in parallel
        await Promise.all(
          Array.from(handlers).map(handler =>
            handler(event).catch(error =>
              console.error(`Handler error for ${event.type}:`, error)
            )
          )
        );
      }
    }

    this.processing = false;
  }

  async publishAndWait(event: Event): Promise<void> {
    const handlers = this.handlers.get(event.type);

    if (handlers) {
      await Promise.all(
        Array.from(handlers).map(handler => handler(event))
      );
    }
  }
}

// Usage example:
class UserService {
  constructor(private eventBus: EventBus) {}

  async createUser(name: string, email: string): Promise<User> {
    const user = { id: generateId(), name, email, createdAt: new Date() };

    await this.eventBus.publish({
      id: generateId(),
      type: 'user.created',
      timestamp: new Date(),
      data: user,
    });

    return user;
  }
}

class EmailService {
  constructor(eventBus: EventBus) {
    eventBus.subscribe('user.created', async (event) => {
      const user = event.data;
      await this.sendWelcomeEmail(user.email);
    });
  }

  private async sendWelcomeEmail(email: string): Promise<void> {
    console.log(`Sending welcome email to ${email}`);
    // Send email...
  }
}

class AnalyticsService {
  constructor(eventBus: EventBus) {
    eventBus.subscribe('user.created', async (event) => {
      await this.trackUserCreation(event.data);
    });
  }

  private async trackUserCreation(user: any): Promise<void> {
    console.log(`Tracking user creation: ${user.id}`);
    // Track analytics...
  }
}
```

**After (Rust):**
```rust
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::{mpsc, RwLock};
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Event {
    id: String,
    event_type: String,
    timestamp: DateTime<Utc>,
    data: serde_json::Value,
}

type EventHandler = Arc<dyn Fn(Event) -> BoxFuture<'static, ()> + Send + Sync>;
type BoxFuture<'a, T> = std::pin::Pin<Box<dyn std::future::Future<Output = T> + Send + 'a>>;

struct EventBus {
    handlers: Arc<RwLock<HashMap<String, Vec<EventHandler>>>>,
    tx: mpsc::UnboundedSender<Event>,
}

impl EventBus {
    fn new() -> Self {
        let (tx, mut rx) = mpsc::unbounded_channel::<Event>();
        let handlers: Arc<RwLock<HashMap<String, Vec<EventHandler>>>> =
            Arc::new(RwLock::new(HashMap::new()));

        let handlers_clone = Arc::clone(&handlers);

        // Spawn background task to process events
        tokio::spawn(async move {
            while let Some(event) = rx.recv().await {
                let handlers_map = handlers_clone.read().await;

                if let Some(event_handlers) = handlers_map.get(&event.event_type) {
                    // Process handlers in parallel
                    let futures: Vec<_> = event_handlers
                        .iter()
                        .map(|handler| {
                            let event = event.clone();
                            let handler = Arc::clone(handler);
                            tokio::spawn(async move {
                                handler(event).await;
                            })
                        })
                        .collect();

                    // Wait for all handlers to complete
                    for future in futures {
                        if let Err(e) = future.await {
                            eprintln!("Handler error: {:?}", e);
                        }
                    }
                }
            }
        });

        EventBus { handlers, tx }
    }

    async fn subscribe<F, Fut>(&self, event_type: impl Into<String>, handler: F)
    where
        F: Fn(Event) -> Fut + Send + Sync + 'static,
        Fut: std::future::Future<Output = ()> + Send + 'static,
    {
        let event_type = event_type.into();
        let handler: EventHandler = Arc::new(move |event| {
            Box::pin(handler(event))
        });

        let mut handlers = self.handlers.write().await;
        handlers
            .entry(event_type)
            .or_insert_with(Vec::new)
            .push(handler);
    }

    fn publish(&self, event: Event) -> Result<(), mpsc::error::SendError<Event>> {
        self.tx.send(event)
    }

    async fn publish_and_wait(&self, event: Event) {
        let handlers_map = self.handlers.read().await;

        if let Some(event_handlers) = handlers_map.get(&event.event_type) {
            let futures: Vec<_> = event_handlers
                .iter()
                .map(|handler| {
                    let event = event.clone();
                    let handler = Arc::clone(handler);
                    async move { handler(event).await }
                })
                .collect();

            futures::future::join_all(futures).await;
        }
    }
}

impl Clone for EventBus {
    fn clone(&self) -> Self {
        EventBus {
            handlers: Arc::clone(&self.handlers),
            tx: self.tx.clone(),
        }
    }
}

// Domain types
#[derive(Debug, Clone, Serialize, Deserialize)]
struct User {
    id: String,
    name: String,
    email: String,
    created_at: DateTime<Utc>,
}

struct UserService {
    event_bus: EventBus,
}

impl UserService {
    fn new(event_bus: EventBus) -> Self {
        UserService { event_bus }
    }

    async fn create_user(&self, name: String, email: String) -> User {
        let user = User {
            id: Uuid::new_v4().to_string(),
            name,
            email,
            created_at: Utc::now(),
        };

        let event = Event {
            id: Uuid::new_v4().to_string(),
            event_type: "user.created".to_string(),
            timestamp: Utc::now(),
            data: serde_json::to_value(&user).unwrap(),
        };

        self.event_bus.publish(event).ok();

        user
    }
}

struct EmailService;

impl EmailService {
    fn new(event_bus: EventBus) -> Self {
        let service = EmailService;

        tokio::spawn(async move {
            event_bus.subscribe("user.created", |event| async move {
                if let Ok(user) = serde_json::from_value::<User>(event.data) {
                    EmailService::send_welcome_email(&user.email).await;
                }
            }).await;
        });

        service
    }

    async fn send_welcome_email(email: &str) {
        println!("Sending welcome email to {}", email);
        // Send email...
    }
}

struct AnalyticsService;

impl AnalyticsService {
    fn new(event_bus: EventBus) -> Self {
        let service = AnalyticsService;

        tokio::spawn(async move {
            event_bus.subscribe("user.created", |event| async move {
                if let Ok(user) = serde_json::from_value::<User>(event.data) {
                    AnalyticsService::track_user_creation(&user).await;
                }
            }).await;
        });

        service
    }

    async fn track_user_creation(user: &User) {
        println!("Tracking user creation: {}", user.id);
        // Track analytics...
    }
}

// Usage:
#[tokio::main]
async fn main() {
    let event_bus = EventBus::new();

    let _email_service = EmailService::new(event_bus.clone());
    let _analytics_service = AnalyticsService::new(event_bus.clone());

    let user_service = UserService::new(event_bus.clone());

    let user = user_service.create_user(
        "Alice".to_string(),
        "alice@example.com".to_string(),
    ).await;

    println!("Created user: {:?}", user);

    // Give handlers time to process
    tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
}
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `lang-typescript-dev` - TypeScript development patterns
- `lang-rust-dev` - Rust development patterns
- `convert-python-rust` - Similar GC → ownership conversion patterns
- `convert-golang-rust` - Similar concurrency model translations
