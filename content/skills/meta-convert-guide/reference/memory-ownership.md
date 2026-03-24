# Memory & Ownership Reference

Comprehensive reference for memory model translation, especially GC → Ownership.

---

## Memory Model Comparison

| Language   | Memory Model              | Cleanup              | Ownership          |
| ---------- | ------------------------- | -------------------- | ------------------ |
| TypeScript | GC (V8)                   | Automatic            | Shared references  |
| Python     | GC (ref counting + cycle) | Automatic            | Shared references  |
| Go         | GC (concurrent)           | Automatic            | Shared references  |
| Rust       | Ownership + Borrowing     | Deterministic (RAII) | Explicit ownership |
| C++        | Manual / RAII             | Deterministic        | Explicit           |
| Swift      | ARC                       | Deterministic        | Explicit           |

---

## GC → Ownership Translation

### Key Differences

| GC Languages                            | Ownership Languages                  |
| --------------------------------------- | ------------------------------------ |
| Allocate freely                         | Consider ownership at creation       |
| Share references anywhere               | One owner, many borrows              |
| Cleanup "sometime later"                | Cleanup when owner goes out of scope |
| Circular refs OK (with cycle detection) | Circular refs need Rc/Arc            |
| Simple mental model                     | More planning required               |

### Ownership Decision Tree

```
START: Is this data shared across components?
│
├─ YES: Is it mutated by multiple parts?
│   │
│   ├─ YES: Multi-threaded access?
│   │   ├─ YES → Arc<Mutex<T>> or channels
│   │   └─ NO  → Rc<RefCell<T>>
│   │
│   └─ NO: → Arc<T> or Rc<T> (shared, immutable)
│
└─ NO: Single owner
    │
    ├─ Does data outlive its creator?
    │   ├─ YES → Return owned value (move)
    │   └─ NO  → Return borrowed reference (&T)
    │
    └─ Is mutation needed?
        ├─ YES → &mut T (exclusive borrow)
        └─ NO  → &T (shared borrow)
```

---

## Borrowing Pattern Reference

| Source Pattern      | Rust Pattern              | When to Use                                       |
| ------------------- | ------------------------- | ------------------------------------------------- |
| Pass by reference   | `&T`                      | Read-only access, no mutation needed              |
| Mutable reference   | `&mut T`                  | Single mutator, temporary access                  |
| Shared ownership    | `Rc<T>` / `Arc<T>`        | Multiple owners, single-threaded / multi-threaded |
| Interior mutability | `RefCell<T>` / `Mutex<T>` | Shared + mutable, single / multi-threaded         |
| Optional ownership  | `Option<Box<T>>`          | Nullable owned values                             |

---

## Lifetime Patterns

### Borrowing from Owner

```rust
// Struct that borrows from external data
struct Parser<'a> {
    source: &'a str,  // Borrows source, doesn't own it
}

impl<'a> Parser<'a> {
    fn new(source: &'a str) -> Self {
        Self { source }
    }

    fn parse(&self) -> Vec<Token<'a>> {
        // Tokens can reference source
    }
}
```

### Avoiding Self-Referential Structs

```rust
// DON'T: Self-referential (won't compile)
struct Bad {
    data: String,
    slice: &str,  // Can't reference data
}

// DO: Use indices instead
struct Good {
    source: String,
    tokens: Vec<(usize, usize)>,  // (start, end) indices
}

impl Good {
    fn get_token(&self, i: usize) -> &str {
        let (start, end) = self.tokens[i];
        &self.source[start..end]
    }
}
```

---

## Clone vs Borrow Decision

```
START: Is the data expensive to clone?
│
├─ YES: Use borrowing with lifetimes
│   │
│   ├─ Single owner? → &T / &mut T
│   └─ Multiple owners? → Arc<T>
│
└─ NO: Clone freely
    │
    ├─ Small data (< ~64 bytes)?
    │   └─ Implement Copy if possible
    │
    └─ Larger data?
        ├─ Clone explicitly
        └─ Consider Cow<T> for optional cloning
```

### When to Clone

| Situation             | Clone?       | Alternative                    |
| --------------------- | ------------ | ------------------------------ |
| Storing in collection | Often yes    | Arc for large data             |
| Passing to thread     | Yes (or Arc) | -                              |
| Returning to caller   | Usually yes  | Return reference with lifetime |
| Internal computation  | Usually no   | Borrow                         |
| Small Copy types      | Implicit     | -                              |

---

## Shared State Patterns

### GC Language (TypeScript)

```typescript
// Freely share references
class Cache {
  private data: Map<string, User> = new Map();

  get(id: string): User | undefined {
    return this.data.get(id); // Returns reference
  }

  set(id: string, user: User): void {
    this.data.set(id, user); // Stores reference
  }
}
```

### Ownership Language (Rust)

```rust
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

---

## Smart Pointers

| Pointer      | Thread-Safe        | Use Case                           |
| ------------ | ------------------ | ---------------------------------- |
| `Box<T>`     | N/A (single owner) | Heap allocation, recursive types   |
| `Rc<T>`      | No                 | Multiple owners, single thread     |
| `Arc<T>`     | Yes                | Multiple owners, multi-thread      |
| `RefCell<T>` | No                 | Interior mutability, single thread |
| `Mutex<T>`   | Yes                | Interior mutability, multi-thread  |
| `RwLock<T>`  | Yes                | Read-heavy interior mutability     |

### Common Combinations

```rust
// Single-threaded shared mutable
type SharedState = Rc<RefCell<State>>;

// Multi-threaded shared mutable
type ThreadSafeState = Arc<Mutex<State>>;

// Multi-threaded read-heavy
type ReadHeavyState = Arc<RwLock<State>>;
```

---

## RAII Pattern

Resources are tied to object lifetime.

### GC Language Cleanup

```typescript
// Need explicit cleanup
async function withFile(path: string, fn: (file: File) => void) {
  const file = await fs.open(path);
  try {
    await fn(file);
  } finally {
    await file.close(); // Must remember to close
  }
}
```

### Rust RAII

```rust
// Automatic cleanup via Drop
fn with_file(path: &Path) -> io::Result<()> {
    let file = File::open(path)?;
    // file automatically closed when it goes out of scope
    process(&file)
}

// Custom Drop implementation
struct Connection {
    handle: Handle,
}

impl Drop for Connection {
    fn drop(&mut self) {
        self.handle.disconnect();  // Always called
    }
}
```

---

## Common Ownership Mistakes

### Mistake 1: Fighting the Borrow Checker

```rust
// DON'T: Clone everything to avoid borrowing
fn process(items: Vec<Item>) {
    for item in items.clone() {  // Unnecessary clone
        handle(&item);
    }
}

// DO: Borrow instead
fn process(items: &[Item]) {
    for item in items {
        handle(item);
    }
}
```

### Mistake 2: Unnecessary Indirection

```rust
// DON'T: Box when not needed
struct Config {
    name: Box<String>,  // Unnecessary
}

// DO: Direct ownership
struct Config {
    name: String,
}
```

### Mistake 3: Mutex When Not Needed

```rust
// DON'T: Mutex for read-only shared data
let data = Arc::new(Mutex::new(config));

// DO: Arc for immutable sharing
let data = Arc::new(config);
```

---

## Performance Implications

| Pattern                 | Cost                 | When to Use                    |
| ----------------------- | -------------------- | ------------------------------ |
| Move                    | Free                 | Default for owned values       |
| Borrow (&T)             | Free                 | Read access                    |
| Mutable borrow (&mut T) | Free                 | Exclusive write access         |
| Clone                   | O(n)                 | When you need independent copy |
| Rc/Arc clone            | O(1)                 | Shared ownership               |
| Mutex lock              | Synchronization cost | Shared mutable access          |
