# Gap Patterns Analysis

**Generated:** 2026-02-04
**Total Patterns:** 54
**Data Sources:** gap-classification.md, patterns.sql, clustering-and-gaps.md, language profiles

---

## Type System Patterns (16 patterns)

### Pattern: TS-001 Dynamic to Static Typing

**Category:** type_system
**Severity:** high
**Automation:** partial

#### Description
Converting from dynamically typed languages where types are checked at runtime to statically typed languages where types must be declared and verified at compile time.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Python, Ruby, JavaScript, Clojure, Elixir | Rust, Java, Go, Haskell, Scala, TypeScript |

#### Example

**Source (Python):**
```python
def process(data):
    return data.upper()  # Type inferred at runtime
```

**Target (Rust):**
```rust
fn process(data: &str) -> String {
    data.to_uppercase()  // Explicit types required
}
```

#### Mitigation Strategies
1. Use type inference tools (mypy, pyright) on source to discover types
2. Analyze runtime behavior to infer likely types
3. Use gradual migration with `Any` or `unknown` as intermediate step

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes
- Lossy: no (information can be reconstructed)

---

### Pattern: TS-002 Nullable to Non-Null Types

**Category:** type_system
**Severity:** medium
**Automation:** partial

#### Description
Converting from languages with pervasive null/nil values to languages requiring explicit Option/Maybe wrappers.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java, C, C++, Objective-C | Rust, Swift, Kotlin, Haskell |

#### Example

**Source (Java):**
```java
public String getName() {
    return user != null ? user.name : null;  // Nullable everywhere
}
```

**Target (Rust):**
```rust
fn get_name(&self) -> Option<&str> {
    self.user.as_ref().map(|u| u.name.as_str())  // Explicit Option
}
```

#### Mitigation Strategies
1. Track all nullable values through data flow analysis
2. Use @Nullable annotations if available in source
3. Convert null checks to Option/Maybe pattern matching

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes (nullability markers)
- Lossy: no

---

### Pattern: TS-003 Higher-Kinded Types to No HKT

**Category:** type_system
**Severity:** high
**Automation:** none

#### Description
Converting code using higher-kinded types (Functor, Monad, etc.) to languages without HKT support.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Haskell, Scala, OCaml | Go, Java, Python, C++ |

#### Example

**Source (Haskell):**
```haskell
fmap :: Functor f => (a -> b) -> f a -> f b
traverse :: (Traversable t, Applicative f) => (a -> f b) -> t a -> f (t b)
```

**Target (Go):**
```go
// Must specialize for each container type
func MapSlice[A, B any](f func(A) B, xs []A) []B {
    result := make([]B, len(xs))
    for i, x := range xs {
        result[i] = f(x)
    }
    return result
}
```

#### Mitigation Strategies
1. Specialize generic code for each concrete type
2. Use code generation to produce type-specific implementations
3. Accept some code duplication for common patterns

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes (HKT patterns)
- Lossy: yes (abstraction lost)

---

### Pattern: TS-004 Gradual Typing to Full Static

**Category:** type_system
**Severity:** medium
**Automation:** partial

#### Description
Converting from gradual typing where type annotations are optional to systems requiring full type coverage.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| TypeScript, Python (typed), PHP 8+, Hack | Rust, Java, Haskell, Go |

#### Example

**Source (TypeScript):**
```typescript
function process(data: any): unknown {
    return data.transform();  // Escape hatches available
}
```

**Target (Java):**
```java
public <T extends Transformable> Object process(T data) {
    return data.transform();  // Every type must be declared
}
```

#### Mitigation Strategies
1. Run type coverage tools to find untyped sections
2. Replace `any`/`dynamic` with concrete types or interfaces
3. Use bounded generics for truly polymorphic code

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes
- Lossy: no

---

### Pattern: TS-005 Duck Typing to Explicit Interfaces

**Category:** type_system
**Severity:** medium
**Automation:** partial

#### Description
Converting from structural "duck typing" to languages requiring explicit interface declarations.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Python, Ruby, JavaScript | Java, C# |

#### Example

**Source (Python):**
```python
def serialize(obj):
    return obj.to_json()  # Anything with to_json() works
```

**Target (Java):**
```java
interface JsonSerializable {
    String toJson();
}

public String serialize(JsonSerializable obj) {
    return obj.toJson();
}
```

#### Mitigation Strategies
1. Identify common method signatures used in duck-typed patterns
2. Extract interfaces from usage patterns
3. Document implicit contracts as explicit interfaces

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes (interface extraction markers)
- Lossy: no

---

### Pattern: TS-006 Union Types to Tagged Unions/Variants

**Category:** type_system
**Severity:** medium
**Automation:** full

#### Description
Converting from untagged union types to tagged union/variant types with explicit discriminators.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| TypeScript, Python (Union) | Rust (enum), Haskell (ADT), Go |

#### Example

**Source (TypeScript):**
```typescript
type Result = string | number | Error;

function handle(r: Result) {
    if (typeof r === 'string') return r.length;
    // ...
}
```

**Target (Rust):**
```rust
enum Result {
    Text(String),
    Number(i64),
    Err(Error),
}

fn handle(r: Result) -> usize {
    match r {
        Result::Text(s) => s.len(),
        // ...
    }
}
```

#### Mitigation Strategies
1. Analyze type guards to determine discriminator logic
2. Create explicit variant types for each union member
3. Convert runtime type checks to pattern matching

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes
- Lossy: no

---

### Pattern: TS-007 Structural Typing to Nominal Typing

**Category:** type_system
**Severity:** medium
**Automation:** partial

#### Description
Converting from structural type systems (types match by shape) to nominal systems (types match by name).

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| TypeScript, Go (interfaces), OCaml | Java, C#, C++, Rust (traits) |

#### Example

**Source (TypeScript):**
```typescript
// Any object with these properties works
function greet(person: { name: string; age: number }) {
    console.log(`Hello ${person.name}`);
}
```

**Target (Java):**
```java
// Must explicitly implement the interface
interface Person {
    String getName();
    int getAge();
}

void greet(Person person) {
    System.out.println("Hello " + person.getName());
}
```

#### Mitigation Strategies
1. Create named interfaces for structural shapes
2. Add explicit implements/extends declarations
3. Use adapter pattern for third-party types

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes
- Lossy: no

---

### Pattern: TS-008 Implicit to Explicit Generics

**Category:** type_system
**Severity:** low
**Automation:** full

#### Description
Converting from implicit generic instantiation to explicit type parameters.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Haskell, F#, Scala | Java, C#, Go |

#### Example

**Source (Haskell):**
```haskell
identity x = x  -- Generic type inferred
```

**Target (Java):**
```java
public static <T> T identity(T x) {  // Explicit type parameter
    return x;
}
```

#### Mitigation Strategies
1. Use type inference to discover generic type parameters
2. Add explicit type parameter declarations
3. Convert type class constraints to bounded generics

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: no
- Lossy: no

---

### Pattern: TS-009 Type Erasure Boundaries

**Category:** type_system
**Severity:** medium
**Automation:** partial

#### Description
Converting from reified generics (runtime type information) to type-erased generics.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| C#, Kotlin, TypeScript (with reflection) | Java, Go |

#### Example

**Source (C#):**
```csharp
public T CreateInstance<T>() where T : new() {
    return new T();  // Can instantiate generic type
}
```

**Target (Java):**
```java
public <T> T createInstance(Class<T> clazz) throws Exception {
    return clazz.getDeclaredConstructor().newInstance();  // Class token needed
}
```

#### Mitigation Strategies
1. Add class token parameters for reflection operations
2. Use factory patterns for generic instantiation
3. Document runtime type requirements

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes
- Lossy: yes (runtime type info lost)

---

### Pattern: TS-010 Type Classes to Interface Dispatch

**Category:** type_system
**Severity:** high
**Automation:** partial

#### Description
Converting from type class based polymorphism to interface/vtable dispatch.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Haskell, Rust (traits), Scala | Java, C#, Go |

#### Example

**Source (Haskell):**
```haskell
class Eq a where
    (==) :: a -> a -> Bool

instance Eq Int where
    x == y = x `primEqInt` y
```

**Target (Java):**
```java
interface Eq<T> {
    boolean eq(T other);
}

class MyInt implements Eq<MyInt> {
    int value;
    public boolean eq(MyInt other) {
        return this.value == other.value;
    }
}
```

#### Mitigation Strategies
1. Convert type class to interface
2. Add self-referential generic bounds
3. Accept some loss of type-level abstraction

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes
- Lossy: yes (retroactive conformance lost)

---

### Pattern: TS-011 Dependent Types to Runtime Checks

**Category:** type_system
**Severity:** critical
**Automation:** none

#### Description
Converting from dependent type systems to conventional static or dynamic typing.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Idris, Agda, Coq | Haskell, Rust, Java, Python |

#### Example

**Source (Idris):**
```idris
append : Vect n a -> Vect m a -> Vect (n + m) a
append [] ys = ys
append (x :: xs) ys = x :: append xs ys
```

**Target (Haskell):**
```haskell
append :: [a] -> [a] -> [a]
append [] ys = ys
append (x:xs) ys = x : append xs ys
-- Length guarantee lost; must validate at runtime
```

#### Mitigation Strategies
1. Add runtime assertions for type-level properties
2. Use property-based testing to verify invariants
3. Document lost guarantees

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes
- Lossy: yes (proofs become runtime checks)

---

### Pattern: TS-012 Row Polymorphism to Fixed Records

**Category:** type_system
**Severity:** medium
**Automation:** partial

#### Description
Converting extensible records with row polymorphism to fixed record types.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| PureScript, Elm | Java, Go, Rust |

#### Example

**Source (PureScript):**
```purescript
getName :: forall r. { name :: String | r } -> String
getName record = record.name
```

**Target (Go):**
```go
type Named interface {
    GetName() string
}

func getName(obj Named) string {
    return obj.GetName()
}
```

#### Mitigation Strategies
1. Create interfaces for common field sets
2. Use composition instead of extension
3. Accept fixed record boundaries

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes
- Lossy: yes (extensibility lost)

---

### Pattern: TS-013 Refinement Types to Runtime Validation

**Category:** type_system
**Severity:** high
**Automation:** partial

#### Description
Converting refinement types (types with predicates) to runtime validation.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Liquid Haskell, F* | Haskell, Rust, Java |

#### Example

**Source (Liquid Haskell):**
```haskell
{-@ type Pos = {v:Int | v > 0} @-}
{-@ divide :: Int -> Pos -> Int @-}
divide x y = x `div` y
```

**Target (Rust):**
```rust
fn divide(x: i32, y: i32) -> Result<i32, &'static str> {
    if y <= 0 {
        return Err("divisor must be positive");
    }
    Ok(x / y)
}
```

#### Mitigation Strategies
1. Convert refinements to runtime checks
2. Use newtype wrappers with smart constructors
3. Document preconditions

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes
- Lossy: yes (compile-time guarantees become runtime)

---

### Pattern: TS-014 Phantom Types to Documentation

**Category:** type_system
**Severity:** low
**Automation:** partial

#### Description
Converting phantom type parameters (unused in data, used for type safety) to non-phantom equivalents.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Haskell, Rust, OCaml | Java, Go, Python |

#### Example

**Source (Rust):**
```rust
struct Id<T> {
    value: u64,
    _phantom: PhantomData<T>,
}

// Type prevents mixing user IDs with product IDs
fn get_user(id: Id<User>) -> User { ... }
```

**Target (Java):**
```java
// Type safety lost; must rely on naming conventions
class UserId {
    private long value;
}
class ProductId {
    private long value;
}
```

#### Mitigation Strategies
1. Create separate wrapper types
2. Document type constraints in comments
3. Use naming conventions consistently

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes
- Lossy: yes (type-level distinction may be lost)

---

### Pattern: TS-015 Type Inference Direction Change

**Category:** type_system
**Severity:** low
**Automation:** full

#### Description
Converting between local type inference and global/bidirectional inference systems.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Haskell (global) | Java (local), Go (local) |

#### Example

**Source (Haskell):**
```haskell
-- Types inferred globally
f x = x + 1
g = map f  -- f's type inferred from usage in g
```

**Target (Go):**
```go
// Must annotate function signatures
func f(x int) int {
    return x + 1
}
func g(xs []int) []int {
    result := make([]int, len(xs))
    for i, x := range xs {
        result[i] = f(x)
    }
    return result
}
```

#### Mitigation Strategies
1. Run type inference on source to extract signatures
2. Add explicit type annotations
3. Preserve type information in IR

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: no
- Lossy: no

---

### Pattern: TS-016 Variance Handling

**Category:** type_system
**Severity:** medium
**Automation:** partial

#### Description
Converting between different variance annotation systems (covariant, contravariant, invariant).

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Scala (+/-), Kotlin (in/out) | Java (wildcards), Go (none) |

#### Example

**Source (Scala):**
```scala
class Box[+A](val value: A)  // Covariant
def process[A](box: Box[A]): A = box.value
```

**Target (Java):**
```java
class Box<T> {
    private T value;
}
// Must use wildcards for variance
static <T> T process(Box<? extends T> box) {
    return box.getValue();
}
```

#### Mitigation Strategies
1. Map variance annotations to wildcards
2. Use bounded type parameters
3. Document variance constraints

#### IR Implications
- Layer affected: 1 (Type layer)
- Annotation needed: yes
- Lossy: no

---

## Memory Model Patterns (12 patterns)

### Pattern: MM-001 GC to Manual Allocation

**Category:** memory
**Severity:** critical
**Automation:** none

#### Description
Converting from garbage-collected memory management to manual malloc/free.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java, Python, Go, Haskell | C |

#### Example

**Source (Java):**
```java
public String concat(String a, String b) {
    return a + b;  // GC handles memory
}
```

**Target (C):**
```c
char* concat(const char* a, const char* b) {
    size_t len = strlen(a) + strlen(b) + 1;
    char* result = malloc(len);
    if (!result) return NULL;
    strcpy(result, a);
    strcat(result, b);
    return result;  // Caller must free!
}
```

#### Mitigation Strategies
1. Track all allocations and their lifetimes
2. Document ownership transfer in API
3. Use static analysis to detect leaks
4. Consider arena allocators for grouped lifetimes

#### IR Implications
- Layer affected: 2 (Memory layer)
- Annotation needed: yes (ownership markers)
- Lossy: no (but requires significant transformation)

---

### Pattern: MM-002 GC to Ownership/Borrowing

**Category:** memory
**Severity:** high
**Automation:** partial

#### Description
Converting from garbage collection to Rust-style ownership with borrow checking.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Python, Java, Go, JavaScript | Rust |

#### Example

**Source (Python):**
```python
def process_items(items):
    for item in items:
        process(item)  # items still accessible after
    return items
```

**Target (Rust):**
```rust
fn process_items(items: &[Item]) -> &[Item] {
    for item in items {
        process(item);  // Borrowing, not ownership
    }
    items
}
```

#### Mitigation Strategies
1. Identify data ownership patterns in source
2. Determine borrow vs move for each parameter
3. Add lifetime annotations where needed
4. Convert shared mutable state to interior mutability

#### IR Implications
- Layer affected: 2 (Memory layer)
- Annotation needed: yes (ownership and lifetime)
- Lossy: no

---

### Pattern: MM-003 Shared Mutable to Linear Types

**Category:** memory
**Severity:** high
**Automation:** partial

#### Description
Converting shared mutable state to linear/affine types where values are used exactly once.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java, Python, JavaScript | Rust, Clean, Linear Haskell |

#### Example

**Source (Java):**
```java
void transfer(Account from, Account to, int amount) {
    from.balance -= amount;  // Shared mutable
    to.balance += amount;
}
```

**Target (Rust):**
```rust
fn transfer(mut from: Account, mut to: Account, amount: i32) -> (Account, Account) {
    from.balance -= amount;
    to.balance += amount;
    (from, to)  // Return ownership
}
```

#### Mitigation Strategies
1. Track mutation points for each value
2. Convert mutating methods to value transformers
3. Thread state through function returns

#### IR Implications
- Layer affected: 2 (Memory layer)
- Annotation needed: yes
- Lossy: no

---

### Pattern: MM-004 Mutable Default to Immutable Default

**Category:** memory
**Severity:** medium
**Automation:** partial

#### Description
Converting from mutable-by-default to immutable-by-default semantics.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java, Python, JavaScript, C++ | Rust, Haskell, Elixir, Scala |

#### Example

**Source (Java):**
```java
List<String> items = new ArrayList<>();
items.add("a");  // Mutating in place
items.add("b");
```

**Target (Elixir):**
```elixir
items = []
items = ["a" | items]  # Rebinding, not mutation
items = ["b" | items]
```

#### Mitigation Strategies
1. Identify mutation sites
2. Convert mutations to new value creation
3. Use persistent data structures
4. Thread state through computations

#### IR Implications
- Layer affected: 2 (Memory layer)
- Annotation needed: yes (mutability markers)
- Lossy: no

---

### Pattern: MM-005 Stack Allocation to Heap Allocation

**Category:** memory
**Severity:** low
**Automation:** full

#### Description
Converting from stack-allocated values to heap-allocated (boxed) values.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Rust, C++ (value semantics) | Java, Python (most objects) |

#### Example

**Source (Rust):**
```rust
fn create_point() -> Point {
    Point { x: 1, y: 2 }  // Returned on stack (moved)
}
```

**Target (Java):**
```java
Point createPoint() {
    return new Point(1, 2);  // Heap allocated
}
```

#### Mitigation Strategies
1. Generally automatic in GC languages
2. Consider escape analysis for optimization
3. Document performance implications

#### IR Implications
- Layer affected: 2 (Memory layer)
- Annotation needed: no
- Lossy: no (semantic equivalent)

---

### Pattern: MM-006 Reference Counting to Tracing GC

**Category:** memory
**Severity:** medium
**Automation:** full

#### Description
Converting from reference counting (ARC) to tracing garbage collection.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Swift, Objective-C, Rust (Rc/Arc) | Java, Go, Python |

#### Example

**Source (Swift):**
```swift
class Node {
    weak var parent: Node?  // Weak to break cycles
    var children: [Node] = []
}
```

**Target (Java):**
```java
class Node {
    Node parent;  // No weak needed, GC handles cycles
    List<Node> children = new ArrayList<>();
}
```

#### Mitigation Strategies
1. Remove weak/unowned reference markers
2. GC handles cycles automatically
3. May need to add explicit cleanup for resources

#### IR Implications
- Layer affected: 2 (Memory layer)
- Annotation needed: no
- Lossy: no

---

### Pattern: MM-007 ARC Cycle Management

**Category:** memory
**Severity:** medium
**Automation:** partial

#### Description
Converting from tracing GC to ARC where reference cycles must be explicitly broken.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java, Python, Go | Swift, Objective-C |

#### Example

**Source (Java):**
```java
class Node {
    Node parent;
    List<Node> children;  // Cycles handled by GC
}
```

**Target (Swift):**
```swift
class Node {
    weak var parent: Node?  // Must be weak to break cycle
    var children: [Node] = []
}
```

#### Mitigation Strategies
1. Identify cyclic reference patterns
2. Mark back-references as weak/unowned
3. Use capture lists in closures
4. Test for memory leaks

#### IR Implications
- Layer affected: 2 (Memory layer)
- Annotation needed: yes (cycle markers)
- Lossy: no

---

### Pattern: MM-008 Deep Copy to Shallow Copy

**Category:** memory
**Severity:** medium
**Automation:** partial

#### Description
Converting between deep copy semantics and shallow/reference copy semantics.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Rust (Clone), Python (copy.deepcopy) | Java (reference), JavaScript |

#### Example

**Source (Rust):**
```rust
let original = vec![1, 2, 3];
let copy = original.clone();  // Deep copy
copy[0] = 99;  // Doesn't affect original
```

**Target (JavaScript):**
```javascript
const original = [1, 2, 3];
const copy = [...original];  // Shallow copy of primitives
// For nested objects, need structuredClone()
```

#### Mitigation Strategies
1. Document copy semantics clearly
2. Use appropriate copy method (spread, slice, structuredClone)
3. Consider immutable data structures

#### IR Implications
- Layer affected: 2 (Memory layer)
- Annotation needed: yes (copy depth)
- Lossy: no

---

### Pattern: MM-009 Value Semantics to Reference Semantics

**Category:** memory
**Severity:** medium
**Automation:** partial

#### Description
Converting from value types (copied on assignment) to reference types (aliased on assignment).

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Swift (struct), Rust, C++ | Java (objects), Python |

#### Example

**Source (Swift):**
```swift
var a = Point(x: 1, y: 2)
var b = a  // Copy
b.x = 10  // a.x still 1
```

**Target (Java):**
```java
Point a = new Point(1, 2);
Point b = a;  // Reference
b.x = 10;  // a.x also 10!
```

#### Mitigation Strategies
1. Document semantic difference
2. Add defensive copies where needed
3. Use immutable types when possible

#### IR Implications
- Layer affected: 2 (Memory layer)
- Annotation needed: yes
- Lossy: yes (implicit copy behavior)

---

### Pattern: MM-010 Per-Process Heap to Shared Heap

**Category:** memory
**Severity:** medium
**Automation:** partial

#### Description
Converting from isolated per-process heaps (BEAM) to shared heap models.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Elixir, Erlang | Java, Python, Go |

#### Example

**Source (Elixir):**
```elixir
# Each process has isolated heap
spawn(fn ->
    data = expensive_computation()
    send(parent, {:result, data})  # Data is copied
end)
```

**Target (Java):**
```java
// Shared heap, need synchronization
ExecutorService exec = Executors.newFixedThreadPool(4);
exec.submit(() -> {
    Data data = expensiveComputation();
    synchronized(results) {
        results.add(data);  // Shared memory
    }
});
```

#### Mitigation Strategies
1. Add synchronization for shared data
2. Use concurrent data structures
3. Consider message passing patterns

#### IR Implications
- Layer affected: 2 (Memory layer)
- Annotation needed: yes (isolation boundaries)
- Lossy: yes (isolation guarantees)

---

### Pattern: MM-011 Arena/Region Allocation

**Category:** memory
**Severity:** medium
**Automation:** partial

#### Description
Converting between arena-based allocation and individual allocation patterns.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Zig, Rust (with arenas) | C (malloc), Java |

#### Example

**Source (Zig):**
```zig
var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
defer arena.deinit();  // Free everything at once
const allocator = arena.allocator();
// All allocations freed together
```

**Target (C):**
```c
// Must track each allocation
void* ptrs[100];
int count = 0;
// ... allocate ...
for (int i = 0; i < count; i++) {
    free(ptrs[i]);  // Free individually
}
```

#### Mitigation Strategies
1. Group related allocations
2. Use object pools where appropriate
3. Consider RAII patterns

#### IR Implications
- Layer affected: 2 (Memory layer)
- Annotation needed: yes
- Lossy: yes (batch deallocation lost)

---

### Pattern: MM-012 Copy-on-Write Optimization

**Category:** memory
**Severity:** low
**Automation:** full

#### Description
Converting between languages with copy-on-write optimization and eager copy languages.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Swift, PHP | Rust, Java |

#### Example

**Source (Swift):**
```swift
var a = [1, 2, 3, 4, 5]
var b = a  // No copy yet (COW)
b[0] = 99  // Copy happens here
```

**Target (Rust):**
```rust
let a = vec![1, 2, 3, 4, 5];
let mut b = a.clone();  // Explicit clone
b[0] = 99;
```

#### Mitigation Strategies
1. Add explicit clone calls where needed
2. Use Cow<T> for deferred cloning in Rust
3. Profile to identify unnecessary copies

#### IR Implications
- Layer affected: 2 (Memory layer)
- Annotation needed: no
- Lossy: no (performance optimization only)

---

## Effect System Patterns (12 patterns)

### Pattern: EF-001 Exceptions to Result/Either

**Category:** effects
**Severity:** high
**Automation:** partial

#### Description
Converting from exception-based error handling to explicit Result/Either types.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java, Python, C++, JavaScript | Rust, Go, Haskell |

#### Example

**Source (Java):**
```java
public User findUser(String id) throws UserNotFoundException {
    User user = db.find(id);
    if (user == null) {
        throw new UserNotFoundException(id);
    }
    return user;
}
```

**Target (Rust):**
```rust
fn find_user(id: &str) -> Result<User, UserError> {
    db.find(id).ok_or(UserError::NotFound(id.to_string()))
}
```

#### Mitigation Strategies
1. Identify all throw sites and exception types
2. Convert checked exceptions to Result type
3. Use ? operator for propagation
4. Convert try-catch to match/map_err

#### IR Implications
- Layer affected: 3 (Effect layer)
- Annotation needed: yes (error types)
- Lossy: no

---

### Pattern: EF-002 Null/Nil to Option/Maybe

**Category:** effects
**Severity:** medium
**Automation:** full

#### Description
Converting null returns to explicit Option/Maybe types.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java, C++, JavaScript, Python | Rust, Haskell, Swift, Kotlin |

#### Example

**Source (Java):**
```java
public User getUser(String id) {
    return users.get(id);  // Returns null if not found
}
```

**Target (Rust):**
```rust
fn get_user(&self, id: &str) -> Option<&User> {
    self.users.get(id)  // Returns None if not found
}
```

#### Mitigation Strategies
1. Track all nullable return points
2. Convert null checks to Option operations
3. Use map/and_then for chaining

#### IR Implications
- Layer affected: 3 (Effect layer)
- Annotation needed: yes
- Lossy: no

---

### Pattern: EF-003 Callbacks to Async/Await

**Category:** effects
**Severity:** medium
**Automation:** partial

#### Description
Converting callback-based async code to async/await syntax.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| JavaScript (callbacks), C | JavaScript (async), Rust, Python |

#### Example

**Source (JavaScript callbacks):**
```javascript
function fetchData(url, callback) {
    request(url, (err, response) => {
        if (err) callback(err);
        else callback(null, response.data);
    });
}
```

**Target (JavaScript async):**
```javascript
async function fetchData(url) {
    const response = await fetch(url);
    return response.json();
}
```

#### Mitigation Strategies
1. Identify callback chains
2. Convert to Promise-based API
3. Use async/await for sequential operations
4. Handle error propagation

#### IR Implications
- Layer affected: 3 (Effect layer)
- Annotation needed: yes (async markers)
- Lossy: no

---

### Pattern: EF-004 Monadic Effects to Direct Style

**Category:** effects
**Severity:** high
**Automation:** partial

#### Description
Converting monadic effect handling (do-notation) to direct-style imperative code.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Haskell, Scala (for-comprehensions) | Python, Java, Go |

#### Example

**Source (Haskell):**
```haskell
fetchUser :: IO (Maybe User)
fetchUser = do
    response <- httpGet "/user"
    case response of
        Just json -> return $ parseUser json
        Nothing   -> return Nothing
```

**Target (Python):**
```python
def fetch_user():
    response = http_get("/user")
    if response is None:
        return None
    return parse_user(response)
```

#### Mitigation Strategies
1. Flatten monadic binds to sequential statements
2. Convert pattern matching to conditionals
3. Handle effects through return values or exceptions

#### IR Implications
- Layer affected: 3 (Effect layer)
- Annotation needed: yes
- Lossy: yes (effect tracking lost)

---

### Pattern: EF-005 Implicit Effects to Explicit

**Category:** effects
**Severity:** medium
**Automation:** partial

#### Description
Converting from implicit side effects to explicit effect tracking.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Python, Java, JavaScript | Haskell, Koka |

#### Example

**Source (Python):**
```python
def process(data):
    print(f"Processing {data}")  # Implicit IO effect
    return data.upper()
```

**Target (Haskell):**
```haskell
process :: String -> IO String
process data = do
    putStrLn $ "Processing " ++ data  -- Explicit IO
    return (map toUpper data)
```

#### Mitigation Strategies
1. Identify all side effects in code
2. Lift effectful operations to effect type
3. Separate pure and effectful code

#### IR Implications
- Layer affected: 3 (Effect layer)
- Annotation needed: yes (effect markers)
- Lossy: no

---

### Pattern: EF-006 Global State to Pure Functions

**Category:** effects
**Severity:** high
**Automation:** partial

#### Description
Converting code relying on global mutable state to pure functions with explicit state passing.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Python, JavaScript, Java | Haskell, Elixir, Rust |

#### Example

**Source (Python):**
```python
counter = 0

def increment():
    global counter
    counter += 1
    return counter
```

**Target (Elixir):**
```elixir
def increment(counter) do
    {counter + 1, counter + 1}  # Return new state and result
end
```

#### Mitigation Strategies
1. Identify all global state access
2. Thread state through function parameters
3. Use State monad or similar patterns
4. Consider Agent/GenServer for managed state

#### IR Implications
- Layer affected: 3 (Effect layer)
- Annotation needed: yes (state dependencies)
- Lossy: no

---

### Pattern: EF-007 Checked to Unchecked Exceptions

**Category:** effects
**Severity:** low
**Automation:** full

#### Description
Converting between checked exceptions (must be declared) and unchecked exceptions.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java (checked) | Kotlin, Python, JavaScript |

#### Example

**Source (Java):**
```java
public void readFile(String path) throws IOException {
    Files.readAllLines(Path.of(path));
}
```

**Target (Kotlin):**
```kotlin
fun readFile(path: String) {
    Files.readAllLines(Path.of(path))  // No throws clause needed
}
```

#### Mitigation Strategies
1. Remove throws declarations
2. Document error conditions
3. Consider Result types for critical errors

#### IR Implications
- Layer affected: 3 (Effect layer)
- Annotation needed: no
- Lossy: yes (compile-time error tracking)

---

### Pattern: EF-008 Tagged Tuples to Exceptions

**Category:** effects
**Severity:** medium
**Automation:** partial

#### Description
Converting from {:ok, value}/{:error, reason} patterns to exceptions.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Elixir, Erlang | Python, Java, JavaScript |

#### Example

**Source (Elixir):**
```elixir
case File.read(path) do
    {:ok, content} -> process(content)
    {:error, reason} -> handle_error(reason)
end
```

**Target (Python):**
```python
try:
    content = open(path).read()
    process(content)
except IOError as e:
    handle_error(e)
```

#### Mitigation Strategies
1. Convert :error tuples to exception raises
2. Convert pattern matching to try-except
3. Map error reasons to exception types

#### IR Implications
- Layer affected: 3 (Effect layer)
- Annotation needed: yes
- Lossy: no

---

### Pattern: EF-009 Lazy to Strict Evaluation

**Category:** effects
**Severity:** high
**Automation:** partial

#### Description
Converting from lazy evaluation (thunks) to strict/eager evaluation.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Haskell | Scala, Rust, Roc, Python |

#### Example

**Source (Haskell):**
```haskell
naturals = [0..]  -- Infinite list, lazily evaluated
take 5 naturals   -- Only evaluates first 5
```

**Target (Roc):**
```roc
# Must use finite range or iterator
naturals = List.range { start: At 0, end: Before 5 }
```

#### Mitigation Strategies
1. Identify lazy patterns (infinite structures, etc.)
2. Convert to iterators/generators where available
3. Use explicit Stream types for lazy sequences
4. Bound infinite computations

#### IR Implications
- Layer affected: 3 (Effect layer)
- Annotation needed: yes (laziness markers)
- Lossy: yes (infinite structures not possible)

---

### Pattern: EF-010 Strict to Lazy Evaluation

**Category:** effects
**Severity:** medium
**Automation:** partial

#### Description
Converting from strict evaluation to lazy evaluation with potential for space leaks.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Python, Rust, Java | Haskell |

#### Example

**Source (Python):**
```python
def expensive():
    print("Computing...")
    return 42

result = expensive()  # Evaluated immediately
```

**Target (Haskell):**
```haskell
expensive :: IO Int
expensive = do
    putStrLn "Computing..."
    return 42

-- Force evaluation when needed
main = do
    result <- expensive
    result `seq` putStrLn $ "Got: " ++ show result
```

#### Mitigation Strategies
1. Be aware of space leak potential
2. Use seq/deepseq for strict evaluation when needed
3. Use strict data types (!) where appropriate

#### IR Implications
- Layer affected: 3 (Effect layer)
- Annotation needed: yes (strictness markers)
- Lossy: no

---

### Pattern: EF-011 Synchronous to Asynchronous

**Category:** effects
**Severity:** medium
**Automation:** partial

#### Description
Converting from synchronous blocking code to asynchronous non-blocking code.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Python (sync), Java (sync) | JavaScript, Rust (async) |

#### Example

**Source (Python sync):**
```python
def fetch_all(urls):
    results = []
    for url in urls:
        results.append(requests.get(url))  # Blocking
    return results
```

**Target (JavaScript async):**
```javascript
async function fetchAll(urls) {
    return Promise.all(urls.map(url => fetch(url)));  // Concurrent
}
```

#### Mitigation Strategies
1. Identify blocking operations
2. Convert to async equivalents
3. Use concurrent patterns (Promise.all, join!)
4. Handle backpressure

#### IR Implications
- Layer affected: 3 (Effect layer)
- Annotation needed: yes (async markers)
- Lossy: no

---

### Pattern: EF-012 Error Codes to Result Types

**Category:** effects
**Severity:** medium
**Automation:** partial

#### Description
Converting from integer error codes to rich Result/Either types.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| C, Go | Rust, Haskell, Scala |

#### Example

**Source (C):**
```c
int read_file(const char* path, char** out) {
    FILE* f = fopen(path, "r");
    if (!f) return -1;  // Error code
    // ...
    return 0;  // Success
}
```

**Target (Rust):**
```rust
fn read_file(path: &str) -> Result<String, io::Error> {
    std::fs::read_to_string(path)  // Rich error type
}
```

#### Mitigation Strategies
1. Map error codes to enum variants
2. Create descriptive error types
3. Use From/Into for error conversion

#### IR Implications
- Layer affected: 3 (Effect layer)
- Annotation needed: yes (error mappings)
- Lossy: no

---

## Concurrency Patterns (14 patterns)

### Pattern: CC-001 Actors to Threads

**Category:** concurrency
**Severity:** high
**Automation:** partial

#### Description
Converting from actor-based concurrency to thread-based concurrency with shared memory.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Elixir, Erlang, Scala (Akka) | Java, C++, Python |

#### Example

**Source (Elixir):**
```elixir
defmodule Counter do
    def loop(count) do
        receive do
            :increment -> loop(count + 1)
            {:get, pid} -> send(pid, count); loop(count)
        end
    end
end
```

**Target (Java):**
```java
class Counter {
    private final AtomicInteger count = new AtomicInteger(0);

    public void increment() {
        count.incrementAndGet();
    }

    public int get() {
        return count.get();
    }
}
```

#### Mitigation Strategies
1. Convert mailbox to thread-safe queue
2. Use locks or atomics for state
3. Convert message patterns to method calls
4. Handle supervision through try-catch

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: yes (actor boundaries)
- Lossy: yes (isolation guarantees)

---

### Pattern: CC-002 Threads to Actors

**Category:** concurrency
**Severity:** high
**Automation:** partial

#### Description
Converting from shared-memory threads to isolated actor processes.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java, C++, Python | Elixir, Erlang |

#### Example

**Source (Java):**
```java
class BankAccount {
    private int balance;

    synchronized void transfer(BankAccount to, int amount) {
        this.balance -= amount;
        to.balance += amount;
    }
}
```

**Target (Elixir):**
```elixir
defmodule BankAccount do
    use GenServer

    def transfer(from_pid, to_pid, amount) do
        GenServer.call(from_pid, {:withdraw, amount})
        GenServer.call(to_pid, {:deposit, amount})
    end
end
```

#### Mitigation Strategies
1. Identify shared mutable state
2. Wrap state in GenServer/Actor
3. Convert synchronized blocks to message passing
4. Design supervision trees

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: yes (state boundaries)
- Lossy: no

---

### Pattern: CC-003 Green Threads to OS Threads

**Category:** concurrency
**Severity:** medium
**Automation:** partial

#### Description
Converting from lightweight green threads to OS-level threads.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Go (goroutines), Erlang (processes) | Java, C, Python |

#### Example

**Source (Go):**
```go
for i := 0; i < 10000; i++ {
    go process(i)  // Cheap goroutines
}
```

**Target (Java):**
```java
// Must use thread pool to avoid overhead
ExecutorService pool = Executors.newFixedThreadPool(100);
for (int i = 0; i < 10000; i++) {
    final int id = i;
    pool.submit(() -> process(id));
}
```

#### Mitigation Strategies
1. Use thread pools to limit concurrency
2. Consider Java virtual threads (21+)
3. Batch work for efficiency
4. Profile for thread overhead

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: yes
- Lossy: yes (performance characteristics)

---

### Pattern: CC-004 CSP Channels to Async/Await

**Category:** concurrency
**Severity:** medium
**Automation:** partial

#### Description
Converting from CSP-style channel communication to async/await patterns.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Go, Clojure (core.async) | JavaScript, Python, Rust |

#### Example

**Source (Go):**
```go
ch := make(chan int)
go func() {
    ch <- 42
}()
result := <-ch
```

**Target (JavaScript):**
```javascript
async function example() {
    const result = await new Promise(resolve => {
        setTimeout(() => resolve(42), 0);
    });
}
```

#### Mitigation Strategies
1. Convert channels to Promises/Futures
2. Use async queues for multi-producer scenarios
3. Convert select to Promise.race

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: yes (channel boundaries)
- Lossy: yes (select semantics differ)

---

### Pattern: CC-005 Shared Memory to Message Passing

**Category:** concurrency
**Severity:** high
**Automation:** partial

#### Description
Converting from shared memory concurrency to message passing between isolated processes.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java, C++, Python | Elixir, Erlang, Go |

#### Example

**Source (Java):**
```java
class SharedState {
    private volatile int value;

    synchronized void update(int v) {
        this.value = v;
    }
}
```

**Target (Elixir):**
```elixir
defmodule State do
    use Agent

    def start_link(initial) do
        Agent.start_link(fn -> initial end, name: __MODULE__)
    end

    def update(value) do
        Agent.update(__MODULE__, fn _ -> value end)
    end
end
```

#### Mitigation Strategies
1. Identify shared state
2. Wrap in Agent/GenServer
3. Convert mutations to messages
4. Handle state consistency

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: yes (sharing boundaries)
- Lossy: no

---

### Pattern: CC-006 Locks/Mutex to STM

**Category:** concurrency
**Severity:** high
**Automation:** none

#### Description
Converting from lock-based synchronization to Software Transactional Memory.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java, C++, Rust | Haskell, Clojure |

#### Example

**Source (Java):**
```java
synchronized void transfer(Account from, Account to, int amount) {
    from.balance -= amount;
    to.balance += amount;
}
```

**Target (Haskell):**
```haskell
transfer :: TVar Int -> TVar Int -> Int -> STM ()
transfer from to amount = do
    fromBal <- readTVar from
    writeTVar from (fromBal - amount)
    toBal <- readTVar to
    writeTVar to (toBal + amount)
```

#### Mitigation Strategies
1. Identify atomic operation boundaries
2. Convert to STM transactions
3. Remove explicit locks
4. Handle retry/conflict logic

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: yes
- Lossy: no

---

### Pattern: CC-007 Async/Await to Callbacks

**Category:** concurrency
**Severity:** medium
**Automation:** full

#### Description
Converting from async/await to callback-based patterns (reverse of EF-003).

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| JavaScript (async), Rust, Python | C, older JavaScript |

#### Example

**Source (JavaScript async):**
```javascript
async function fetchData() {
    const response = await fetch(url);
    return response.json();
}
```

**Target (JavaScript callbacks):**
```javascript
function fetchData(callback) {
    fetch(url)
        .then(response => response.json())
        .then(data => callback(null, data))
        .catch(err => callback(err));
}
```

#### Mitigation Strategies
1. Convert await points to callbacks
2. Handle error propagation
3. Manage callback nesting (use named functions)

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: yes
- Lossy: no

---

### Pattern: CC-008 Futures/Promises to Blocking

**Category:** concurrency
**Severity:** low
**Automation:** full

#### Description
Converting from Future/Promise-based code to synchronous blocking calls.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Scala, Java (CompletableFuture) | C, older Java |

#### Example

**Source (Scala):**
```scala
val future: Future[User] = fetchUser(id)
future.map(user => process(user))
```

**Target (Java blocking):**
```java
User user = fetchUserBlocking(id);  // Blocks until complete
process(user);
```

#### Mitigation Strategies
1. Add blocking calls at async boundaries
2. Handle timeouts
3. Consider thread pool implications

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: no
- Lossy: yes (non-blocking lost)

---

### Pattern: CC-009 Supervision Trees to Exception Handling

**Category:** concurrency
**Severity:** high
**Automation:** partial

#### Description
Converting from OTP-style supervision to exception-based error recovery.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Elixir, Erlang | Java, Python |

#### Example

**Source (Elixir):**
```elixir
children = [
    {Worker, restart: :permanent},
    {Cache, restart: :temporary}
]
Supervisor.start_link(children, strategy: :one_for_one)
```

**Target (Java):**
```java
while (true) {
    try {
        worker.run();
    } catch (Exception e) {
        logger.error("Worker failed", e);
        // Restart logic
        worker = new Worker();
    }
}
```

#### Mitigation Strategies
1. Convert supervision strategies to restart loops
2. Use circuit breakers for failure handling
3. Implement health checks
4. Consider Resilience4j or similar libraries

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: yes
- Lossy: yes (supervision semantics)

---

### Pattern: CC-010 Single-Threaded to Multi-Threaded

**Category:** concurrency
**Severity:** medium
**Automation:** none

#### Description
Converting single-threaded event-loop code to multi-threaded execution.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| JavaScript (Node.js) | Java, Go, Rust |

#### Example

**Source (JavaScript):**
```javascript
// Single event loop, no threading concerns
let state = {};
app.get('/data', (req, res) => {
    state.count++;  // Safe in single thread
    res.json(state);
});
```

**Target (Java):**
```java
// Multi-threaded, needs synchronization
AtomicInteger count = new AtomicInteger(0);

app.get("/data", (req, res) -> {
    int current = count.incrementAndGet();  // Thread-safe
    return Map.of("count", current);
});
```

#### Mitigation Strategies
1. Identify shared mutable state
2. Add appropriate synchronization
3. Use thread-safe data structures
4. Consider immutable patterns

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: yes (threading model)
- Lossy: no

---

### Pattern: CC-011 Parallel Collections to Sequential

**Category:** concurrency
**Severity:** low
**Automation:** full

#### Description
Converting parallel collection operations to sequential iteration.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java (parallelStream), Scala (par) | C, older languages |

#### Example

**Source (Java):**
```java
list.parallelStream()
    .map(this::process)
    .collect(toList());
```

**Target (C):**
```c
for (int i = 0; i < count; i++) {
    result[i] = process(items[i]);
}
```

#### Mitigation Strategies
1. Convert to sequential loop
2. Document performance implications
3. Consider manual parallelization if needed

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: yes (parallel markers)
- Lossy: yes (parallelism lost)

---

### Pattern: CC-012 Reactive Streams to Pull-Based

**Category:** concurrency
**Severity:** medium
**Automation:** partial

#### Description
Converting from reactive push-based streams to pull-based iteration.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| RxJava, Reactor, Akka Streams | Go, Python |

#### Example

**Source (RxJava):**
```java
Flowable.fromIterable(items)
    .map(this::transform)
    .filter(this::isValid)
    .subscribe(this::process);
```

**Target (Python):**
```python
for item in items:
    transformed = transform(item)
    if is_valid(transformed):
        process(transformed)
```

#### Mitigation Strategies
1. Convert operators to loop operations
2. Handle backpressure with manual buffering
3. Use generators for lazy evaluation

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: yes
- Lossy: yes (backpressure handling)

---

### Pattern: CC-013 Coroutines to State Machines

**Category:** concurrency
**Severity:** medium
**Automation:** partial

#### Description
Converting coroutine-based code to explicit state machine implementations.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Kotlin, Python, Lua | C, older Java |

#### Example

**Source (Python):**
```python
async def fetch_and_process():
    data = await fetch()
    result = await process(data)
    return result
```

**Target (C state machine):**
```c
enum State { FETCHING, PROCESSING, DONE };

struct Context {
    enum State state;
    void* data;
    void* result;
};

int step(struct Context* ctx) {
    switch (ctx->state) {
        case FETCHING:
            ctx->data = fetch_start();
            ctx->state = PROCESSING;
            return PENDING;
        case PROCESSING:
            ctx->result = process_start(ctx->data);
            ctx->state = DONE;
            return PENDING;
        case DONE:
            return COMPLETE;
    }
}
```

#### Mitigation Strategies
1. Identify yield/await points
2. Create state enum for each suspension point
3. Store local variables in context struct
4. Convert to switch-based state machine

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: yes
- Lossy: no

---

### Pattern: CC-014 Virtual Threads to Thread Pools

**Category:** concurrency
**Severity:** low
**Automation:** partial

#### Description
Converting from virtual/lightweight threads to traditional thread pool patterns.

#### From -> To
| From Languages | To Languages |
|----------------|--------------|
| Java 21+, Go | Java 8-17, C++ |

#### Example

**Source (Java 21):**
```java
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<User> user = scope.fork(() -> fetchUser(id));
    Future<Orders> orders = scope.fork(() -> fetchOrders(id));
    scope.join();
    return combine(user.get(), orders.get());
}
```

**Target (Java 8):**
```java
ExecutorService executor = Executors.newFixedThreadPool(10);
Future<User> user = executor.submit(() -> fetchUser(id));
Future<Orders> orders = executor.submit(() -> fetchOrders(id));
return combine(user.get(), orders.get());
```

#### Mitigation Strategies
1. Use thread pool with bounded size
2. Consider work-stealing pools
3. Monitor thread utilization

#### IR Implications
- Layer affected: 4 (Concurrency layer)
- Annotation needed: no
- Lossy: yes (scalability characteristics)

---

## Summary Statistics

### Pattern Count by Category

| Category | Count | Percentage |
|----------|-------|------------|
| Type System | 16 | 29.6% |
| Memory Model | 12 | 22.2% |
| Effect System | 12 | 22.2% |
| Concurrency | 14 | 25.9% |
| **Total** | **54** | **100%** |

### Patterns by Severity

| Severity | Count | Patterns |
|----------|-------|----------|
| critical | 2 | TS-011, MM-001 |
| high | 16 | TS-001, TS-003, TS-010, TS-013, MM-002, MM-003, EF-001, EF-004, EF-006, EF-009, CC-001, CC-002, CC-005, CC-006, CC-009 |
| medium | 28 | TS-002, TS-004, TS-005, TS-006, TS-007, TS-009, TS-012, TS-014, TS-016, MM-004, MM-006, MM-007, MM-008, MM-009, MM-010, MM-011, EF-002, EF-003, EF-005, EF-08, EF-10, EF-11, EF-12, CC-03, CC-04, CC-10, CC-12, CC-13 |
| low | 8 | TS-008, TS-015, MM-005, MM-012, EF-007, CC-08, CC-11, CC-14 |

### Patterns by Automation Level

| Automation | Count | Patterns |
|------------|-------|----------|
| none | 5 | TS-003, TS-011, MM-001, CC-06, CC-10 |
| partial | 38 | Most patterns |
| full | 11 | TS-006, TS-008, TS-015, MM-005, MM-006, MM-012, EF-002, EF-007, CC-07, CC-08, CC-11 |

### Cross-Reference: Family Pairs to Patterns

| Family Pair | Primary Patterns |
|-------------|------------------|
| dynamic -> systems | TS-001, TS-002, MM-002, EF-001 |
| dynamic -> ml-fp | TS-001, EF-004, EF-005 |
| systems -> systems | MM-001, MM-011, CC-13 |
| ml-fp -> ml-fp | TS-003, EF-09, EF-10 |
| ml-fp -> managed-oop | TS-010, EF-04, CC-11 |
| beam -> managed-oop | CC-01, CC-09, MM-10 |
| managed-oop -> beam | CC-02, CC-05, MM-10 |
| apple -> apple | MM-07, TS-02 |
| gradual -> static | TS-04, TS-06, TS-07 |

### IR Layer Impact Summary

| IR Layer | Patterns Affecting | Primary Concerns |
|----------|-------------------|------------------|
| Layer 0 (Syntax) | 0 | Handled by parsers |
| Layer 1 (Types) | 16 | Type annotations, inference |
| Layer 2 (Memory) | 12 | Ownership, allocation, lifetimes |
| Layer 3 (Effects) | 12 | Error handling, side effects |
| Layer 4 (Concurrency) | 14 | Threading model, synchronization |

### Annotation Requirements

| Annotation Type | Pattern Count | Examples |
|-----------------|---------------|----------|
| Type annotations | 14 | TS-001 to TS-016 |
| Ownership markers | 8 | MM-001 to MM-003 |
| Lifetime annotations | 3 | MM-002, MM-003, MM-011 |
| Effect markers | 10 | EF-001 to EF-012 |
| Concurrency boundaries | 12 | CC-001 to CC-014 |

---

## Data Files

- **Source Classification:** `gap-classification.md`
- **Pattern Database:** `patterns.sql`
- **Clustering Analysis:** `clustering-and-gaps.md`
- **Language Profiles:** `languages/*.yaml`
