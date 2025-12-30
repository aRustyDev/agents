# Gotchas by Language Family

Common pitfalls when converting between language paradigms and memory models.

---

## OOP → Functional

### Inheritance → Composition

| OOP Pattern | FP Pitfall | Solution |
|-------------|------------|----------|
| Deep class hierarchies | Trying to replicate with traits | Use composition + traits |
| Protected members | No equivalent | Redesign with modules |
| Abstract classes | Partial implementation | Trait + default methods |

```rust
// ❌ Trying to replicate inheritance
trait Animal {
    fn speak(&self);
}
trait Dog: Animal {}  // This isn't inheritance!

// ✓ Composition
struct Dog {
    name: String,
}
impl Animal for Dog {
    fn speak(&self) { println!("Woof!"); }
}
```

### Mutable State → Immutability

| OOP Pattern | FP Pitfall | Solution |
|-------------|------------|----------|
| Object mutation | Excessive cloning | Use builders, functional updates |
| Setters | Clone on every set | Batch updates, builder pattern |
| Global state | Arc<Mutex> everywhere | Pass state explicitly |

### Method Chaining

```typescript
// OOP: Returns this for chaining
class Builder {
  setValue(v: string): this { this.value = v; return this; }
}
```

```rust
// Rust: Consumes self, returns new Self
impl Builder {
    fn set_value(mut self, v: String) -> Self {
        self.value = v;
        self
    }
}
```

---

## Dynamic → Static Typing

### Runtime Type Checks

| Dynamic Pattern | Static Pitfall | Solution |
|-----------------|----------------|----------|
| `isinstance()` | Match on wrong enum variant | Use exhaustive matching |
| Duck typing | Overly complex trait bounds | Accept simpler interfaces |
| `hasattr()` | Option everywhere | Design with known structure |

### Optional Fields

```python
# Python: Fields can be None anytime
user.email  # Might be None

# Easy but wrong pattern in Rust
struct User {
    email: Option<String>,  // Now you check everywhere
}
```

```rust
// ✓ Better: Separate types for different states
struct UnverifiedUser { /* no email */ }
struct VerifiedUser { email: String }  // Always has email
```

### Type Narrowing

```typescript
// TypeScript: Type narrowing with guards
if (typeof x === "string") {
  x.toUpperCase();  // x is string here
}
```

```rust
// Rust: Pattern matching
match x {
    Value::String(s) => s.to_uppercase(),
    _ => /* handle other cases */
}
```

---

## GC → Ownership

### Reference Cycles

| GC Pattern | Ownership Pitfall | Solution |
|------------|-------------------|----------|
| Parent ↔ Child refs | `Rc<RefCell>` cycles | Weak references |
| Observer pattern | Leaked Rc | Use indices or callbacks |
| Graph structures | Arc everywhere | Arena allocators |

```rust
// ❌ Creates cycle, memory leak
struct Node {
    parent: Option<Rc<RefCell<Node>>>,
    children: Vec<Rc<RefCell<Node>>>,
}

// ✓ Break cycle with Weak
struct Node {
    parent: Option<Weak<RefCell<Node>>>,  // Weak!
    children: Vec<Rc<RefCell<Node>>>,
}
```

### Shared Mutable State

```python
# Python: Easy shared mutation
shared_list = []
def add(x): shared_list.append(x)  # Just works
```

```rust
// Rust: Must be explicit
let shared_list = Arc::new(Mutex::new(Vec::new()));
shared_list.lock().unwrap().push(x);
```

### Lifetimes in Structs

```rust
// ❌ Common mistake: storing references
struct Cache<'a> {
    data: &'a str,  // Lifetime pain begins
}

// ✓ Usually better: own the data
struct Cache {
    data: String,  // Simple, no lifetime
}
```

---

## Interpreted → Compiled

### Runtime Reflection

| Interpreted | Compiled Pitfall | Solution |
|-------------|------------------|----------|
| `eval()` | No equivalent | Code generation, DSL |
| `getattr()` | Complex macros | Enum dispatch |
| Monkey patching | Can't modify at runtime | Trait objects, strategy pattern |

### Dynamic Dispatch

```python
# Python: Call any method by name
getattr(obj, method_name)()
```

```rust
// Rust: Must plan dispatch upfront
enum Command { Start, Stop, Restart }
match cmd {
    Command::Start => obj.start(),
    Command::Stop => obj.stop(),
    Command::Restart => obj.restart(),
}
```

### Hot Reload

| Interpreted | Compiled Alternative |
|-------------|----------------------|
| Module reload | Recompile (fast with incremental) |
| REPL modifications | `cargo watch`, test-driven |
| Runtime patches | Feature flags, config |

---

## Exception → Result

### Error Propagation

| Exception Pattern | Result Pitfall | Solution |
|-------------------|----------------|----------|
| Catch at top level | `.unwrap()` everywhere | Use `?` operator |
| Rethrow with context | Lost error chain | `anyhow`, `thiserror` |
| Finally blocks | Forgotten cleanup | `Drop` trait, RAII |

```python
# Python: Try/except/finally
try:
    resource = acquire()
    work(resource)
finally:
    resource.release()
```

```rust
// Rust: RAII handles cleanup
let resource = Resource::acquire()?;
work(&resource)?;
// Drop automatically calls release
```

### Multiple Error Types

```rust
// ❌ Fighting the type system
fn process() -> Result<(), Box<dyn Error>> {
    // Works but loses type info
}

// ✓ Use error enums or anyhow
#[derive(thiserror::Error)]
enum AppError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Parse error: {0}")]
    Parse(#[from] serde_json::Error),
}
```

---

## Lazy → Eager Evaluation

### Infinite Sequences

| Lazy Pattern | Eager Pitfall | Solution |
|--------------|---------------|----------|
| Infinite lists | Immediate OOM | Iterators |
| Take from stream | Collect everything | `.take(n)` |
| Lazy IO | Buffer entire file | Streaming readers |

```haskell
-- Haskell: Infinite list, no problem
take 10 [1..]  -- [1,2,3,4,5,6,7,8,9,10]
```

```rust
// Rust: Use iterators, not Vec
(1..).take(10).collect::<Vec<_>>()  // Works

// ❌ Don't try to collect infinite
let v: Vec<_> = (1..).collect();  // Hangs forever
```

### Memoization

```haskell
-- Haskell: Automatic memoization
fib = 0 : 1 : zipWith (+) fib (tail fib)
```

```rust
// Rust: Manual caching
fn fib_memo(n: u64, cache: &mut HashMap<u64, u64>) -> u64 {
    if let Some(&v) = cache.get(&n) { return v; }
    let result = fib_memo(n-1, cache) + fib_memo(n-2, cache);
    cache.insert(n, result);
    result
}
```

---

## Quick Reference: Family Transitions

| From → To | Primary Challenge | Key Strategy |
|-----------|-------------------|--------------|
| OOP → FP | Inheritance mindset | Composition + traits |
| Dynamic → Static | Runtime flexibility | Enums + pattern matching |
| GC → Ownership | Shared references | Clone, Rc, or redesign |
| Interpreted → Compiled | Reflection/eval | Code generation, macros |
| Exception → Result | Error propagation | `?` operator, error enums |
| Lazy → Eager | Infinite structures | Iterators, streaming |
