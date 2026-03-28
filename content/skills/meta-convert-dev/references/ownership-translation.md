# Ownership Model Translation Reference

Comprehensive guide for translating between different memory management and ownership paradigms.

## Ownership Models Comparison

| Language | Memory Model | Deallocation | Sharing Strategy | Mutability |
|----------|--------------|--------------|------------------|------------|
| **Python** | GC (refcount + cycle detection) | Automatic | References | Default mutable |
| **JavaScript** | GC (mark-and-sweep) | Automatic | References | Default mutable |
| **Java** | GC (generational) | Automatic | References | Default mutable |
| **Go** | GC (concurrent tri-color) | Automatic | Values + pointers | Default mutable |
| **C#** | GC (generational) | Automatic | Value/reference types | Default mutable |
| **Rust** | Ownership + borrowing | Deterministic (RAII) | Borrows (`&T`, `&mut T`) | Default immutable |
| **Swift** | ARC (automatic reference counting) | Deterministic | References + value types | `let` vs `var` |
| **C++** | Manual + RAII | Manual/RAII | Pointers, references | Default mutable |
| **Haskell** | GC (lazy evaluation) | Automatic | Immutable by default | Immutable |
| **Elixir** | GC (per-process) | Automatic | Message passing | Immutable |
| **Erlang** | GC (per-process) | Automatic | Message passing | Immutable |

---

## Core Ownership Concepts (Rust Model)

### Rule 1: Single Owner

Each value in Rust has exactly one owner at a time.

```rust
// Rust: Ownership transfer (move)
let s1 = String::from("hello");
let s2 = s1;  // s1 is moved to s2
// println!("{}", s1);  // ERROR: s1 no longer valid
```

**Translation to GC languages:**

```python
# Python: Both references point to same object
s1 = "hello"
s2 = s1  # Both s1 and s2 valid, reference same object
print(s1)  # Works fine
```

```go
// Go: Value copy for value types, pointer sharing for heap
s1 := "hello"
s2 := s1  // Copy (strings are immutable in Go)

// For mutable data, use explicit pointers
data := &MyStruct{value: 42}
data2 := data  // Both point to same struct
```

### Rule 2: Borrowing

References allow temporary access without ownership transfer.

```rust
// Rust: Borrowing
fn calculate_length(s: &String) -> usize {
    s.len()
}  // s goes out of scope but doesn't drop the String

let s = String::from("hello");
let len = calculate_length(&s);
println!("{} has length {}", s, len);  // s still valid
```

**Translation patterns:**

```python
# Python: No borrowing concept - just pass reference
def calculate_length(s: str) -> int:
    return len(s)

s = "hello"
length = calculate_length(s)  # No ownership concerns
print(f"{s} has length {length}")
```

```go
// Go: Pointer parameters for shared access
func calculateLength(s *string) int {
    return len(*s)
}

s := "hello"
length := calculateLength(&s)
```

### Rule 3: Borrowing Rules

1. At any time, you can have either one mutable reference OR any number of immutable references
2. References must always be valid (no dangling references)

```rust
// Rust: Can't have mutable and immutable borrows simultaneously
let mut s = String::from("hello");

let r1 = &s;      // OK: immutable borrow
let r2 = &s;      // OK: another immutable borrow
// let r3 = &mut s;  // ERROR: can't borrow mutably while borrowed immutably

println!("{} and {}", r1, r2);
// After this point, r1 and r2 are no longer used

let r3 = &mut s;  // OK: no more immutable borrows active
r3.push_str(" world");
```

**GC language equivalent (no enforcement):**

```python
# Python: No borrow checker - concurrent modification is allowed
s = ["hello"]

r1 = s  # "borrow" 1
r2 = s  # "borrow" 2
s.append("world")  # Mutation visible through r1 and r2

# This can lead to bugs that Rust prevents
for item in s:
    if item == "hello":
        s.remove(item)  # Bug: modifying while iterating
```

---

## Common GC → Ownership Patterns

### Pattern 1: Shared State → Clone or Arc

**GC (shared references):**
```python
class Config:
    def __init__(self):
        self.timeout = 30

config = Config()
process_a(config)  # Shares reference
process_b(config)  # Shares same reference
config.timeout = 60  # Both see change
```

**Rust (explicit sharing strategy):**
```rust
// Option A: Clone for independent copies
#[derive(Clone)]
struct Config { timeout: u32 }

let config = Config { timeout: 30 };
let config_a = config.clone();  // Independent copy
let config_b = config.clone();  // Independent copy

// Option B: Arc for shared ownership
use std::sync::Arc;

let config = Arc::new(Config { timeout: 30 });
let config_a = Arc::clone(&config);  // Shared, reference counted
let config_b = Arc::clone(&config);
```

### Pattern 2: Mutable Shared State → Mutex/RwLock

**GC (implicit shared mutation):**
```python
class Counter:
    def __init__(self):
        self.value = 0

counter = Counter()

def increment():
    counter.value += 1  # Race condition in threads

# Run in multiple threads (data race possible)
```

**Rust (explicit synchronization):**
```rust
use std::sync::{Arc, Mutex};

struct Counter { value: u32 }

let counter = Arc::new(Mutex::new(Counter { value: 0 }));

let counter_clone = Arc::clone(&counter);
std::thread::spawn(move || {
    let mut c = counter_clone.lock().unwrap();
    c.value += 1;
});
```

### Pattern 3: Return Local Reference → Return Owned Value

**GC (return reference to local):**
```python
def get_greeting(name: str) -> str:
    greeting = f"Hello, {name}!"
    return greeting  # Reference to local - fine in GC languages
```

**Rust (return owned value):**
```rust
fn get_greeting(name: &str) -> String {
    let greeting = format!("Hello, {}!", name);
    greeting  // Ownership transferred to caller
}

// Can't return reference to local:
// fn bad() -> &str {
//     let s = String::from("hello");
//     &s  // ERROR: s dropped, reference would be dangling
// }
```

### Pattern 4: Optional Values → Option<T>

**GC (null/None):**
```python
def find_user(id: int) -> User | None:
    if id in users:
        return users[id]
    return None

user = find_user(42)
if user is not None:
    print(user.name)  # Runtime check
```

**Rust (Option with ownership):**
```rust
fn find_user(id: u32) -> Option<User> {
    users.get(&id).cloned()  // Clone to transfer ownership
}

// Or return reference if collection outlives the call
fn find_user_ref(&self, id: u32) -> Option<&User> {
    self.users.get(&id)
}

if let Some(user) = find_user(42) {
    println!("{}", user.name);  // Compile-time safety
}
```

---

## Lifetimes: Explicit Validity Tracking

Rust lifetimes make reference validity explicit at compile time.

### Basic Lifetime Annotations

```rust
// Explicit lifetime: 'a means "some lifetime"
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// Usage: returned reference valid as long as both inputs
let string1 = String::from("long");
let result;
{
    let string2 = String::from("short");
    result = longest(&string1, &string2);
    println!("{}", result);  // OK: both strings in scope
}
// println!("{}", result);  // ERROR: string2 dropped
```

### Struct Lifetimes

```rust
// Struct containing references needs lifetime
struct Excerpt<'a> {
    part: &'a str,
}

fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().unwrap();
    let excerpt = Excerpt { part: first_sentence };
    // excerpt valid only as long as novel
}
```

**GC equivalent (no lifetime annotations):**

```python
class Excerpt:
    def __init__(self, part: str):
        self.part = part  # Reference to string

novel = "Call me Ishmael. Some years ago..."
first_sentence = novel.split('.')[0]
excerpt = Excerpt(first_sentence)
# Both novel and excerpt can live independently
# (GC tracks references)
```

---

## Decision Tree: Clone, Borrow, or Move?

```
Need the data?
├── Yes, for reading only
│   └── BORROW (&T)
│       └── Multiple readers OK
├── Yes, for modification
│   └── Need original after?
│       ├── Yes → CLONE then modify copy
│       └── No → MOVE or BORROW MUT (&mut T)
└── Yes, transfer ownership
    └── MOVE (take ownership)

Sharing across threads?
├── Read-only → Arc<T>
├── Read-write → Arc<Mutex<T>> or Arc<RwLock<T>>
└── Message passing → channels (mpsc)
```

### Quick Reference

| Situation | GC Language | Rust |
|-----------|-------------|------|
| Pass to function, use after | Just pass | Borrow (`&T`) |
| Pass to function, don't need after | Just pass | Move or borrow |
| Store in struct | Just store | Clone, move, or lifetime |
| Share between threads | Share reference | Arc<T> |
| Mutate from multiple threads | Lock (or not...) | Arc<Mutex<T>> |
| Return from function | Return reference | Return owned or use lifetime |

---

## Common Translation Gotchas

### 1. String Ownership

```rust
// Rust has two string types
let s1: &str = "literal";        // Borrowed, static lifetime
let s2: String = String::from("owned");  // Owned, heap-allocated
let s3: &str = &s2;              // Borrow of owned string
```

```python
# Python: Just one string type
s1 = "literal"  # Interned, immutable
s2 = "owned"    # Same type
```

### 2. Collection Iteration

```rust
// Rust: Choose iteration ownership
let v = vec![1, 2, 3];

for x in &v { }      // Borrow elements
for x in &mut v { }  // Mutably borrow elements
for x in v { }       // Take ownership (v consumed)
```

```python
# Python: Always iterate by reference
v = [1, 2, 3]
for x in v:  # x is reference (or copy for primitives)
    pass
# v still usable
```

### 3. Closure Captures

```rust
// Rust: Closures capture by reference or move
let s = String::from("hello");

let closure = || println!("{}", s);  // Borrows s
closure();
println!("{}", s);  // s still valid

let closure = move || println!("{}", s);  // Moves s
closure();
// println!("{}", s);  // ERROR: s moved
```

```python
# Python: Closures capture by reference
s = "hello"
closure = lambda: print(s)
closure()
print(s)  # Always works
```

### 4. Error Handling Ownership

```rust
// Rust: Result owns its values
fn parse_int(s: &str) -> Result<i32, ParseIntError> {
    s.parse()  // Returns owned Result
}

match parse_int("42") {
    Ok(n) => println!("{}", n),   // n moved out of Result
    Err(e) => println!("{}", e),  // e moved out of Result
}
```

---

## Smart Pointer Reference

| Type | Ownership | Thread-Safe | Use Case |
|------|-----------|-------------|----------|
| `Box<T>` | Single owner | No | Heap allocation, recursive types |
| `Rc<T>` | Shared (ref counted) | No | Single-thread shared ownership |
| `Arc<T>` | Shared (atomic ref counted) | Yes | Multi-thread shared ownership |
| `RefCell<T>` | Interior mutability | No | Runtime borrow checking |
| `Mutex<T>` | Interior mutability | Yes | Thread-safe mutation |
| `RwLock<T>` | Interior mutability | Yes | Multiple readers, single writer |
| `Cell<T>` | Interior mutability | No | Copy types only |

### Combining Smart Pointers

```rust
// Thread-safe shared mutable state
use std::sync::{Arc, Mutex};

let counter = Arc::new(Mutex::new(0));

let handles: Vec<_> = (0..10)
    .map(|_| {
        let counter = Arc::clone(&counter);
        std::thread::spawn(move || {
            let mut num = counter.lock().unwrap();
            *num += 1;
        })
    })
    .collect();

for handle in handles {
    handle.join().unwrap();
}

println!("Final: {}", *counter.lock().unwrap());  // 10
```

---

## Translation Checklist

When converting from GC language to Rust:

- [ ] Identify all shared references → determine if clone, borrow, or Arc
- [ ] Find mutable shared state → add Mutex/RwLock protection
- [ ] Check function signatures → add lifetime annotations if returning references
- [ ] Review collection iteration → choose appropriate iteration method
- [ ] Audit closure captures → add `move` keyword where needed
- [ ] Replace null checks → use Option<T>
- [ ] Handle errors → use Result<T, E> with proper ownership

When converting from Rust to GC language:

- [ ] Remove lifetime annotations → not needed
- [ ] Simplify smart pointers → use plain references
- [ ] Remove explicit clones → GC handles sharing
- [ ] Simplify error handling → Option/None patterns
- [ ] Remove borrow annotations → all borrows become references
- [ ] Consider thread safety → GC doesn't prevent data races
