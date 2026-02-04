# Bidirectional Gap Analysis

Analysis of asymmetric conversion gaps where A to B does not equal B to A.

**Generated:** 2026-02-04
**Task:** ai-p29.4
**Input Data:** family-pairs.md, gap-patterns.md, gap-classification.md

---

## 1. Asymmetry Classification

Difficulty scale: 1 (Easy) to 5 (Very Hard)
Asymmetry ratio: Higher difficulty / Lower difficulty

| Gap Type | A to B | B to A | Asymmetry | Reason |
|----------|--------|--------|-----------|--------|
| **Type System** |||||
| Static to Dynamic | Easy (1) | Hard (3) | 3:1 | Type info lost (erasure is easy, inference is hard) |
| Nullable to Non-Null | Medium (2) | Easy (1) | 2:1 | Adding Option is harder than removing |
| HKT to No HKT | N/A | N/A | Symmetric | Both directions are lossy/impossible |
| Duck to Explicit | Medium (2) | Easy (1) | 2:1 | Extracting interfaces requires analysis |
| Structural to Nominal | Medium (2) | Easy (1) | 2:1 | Creating nominal wrappers is harder |
| **Memory Model** |||||
| GC to Ownership | Hard (4) | Easy (1) | 4:1 | Ownership must be inferred/designed |
| GC to Manual | Very Hard (5) | Easy (1) | 5:1 | Lifetime tracking required |
| ARC to GC | Easy (1) | Medium (2) | 1:2 | Adding weak refs harder than removing |
| Mutable to Immutable | Hard (3) | Easy (1) | 3:1 | Restructuring data flow required |
| Value to Reference | Medium (2) | Low (1) | 2:1 | Defensive copies may be needed |
| **Effects** |||||
| Exceptions to Result | Medium (2) | Easy (1) | 2:1 | Must map all throw sites |
| Pure to Impure | Easy (1) | Hard (3) | 1:3 | Effects allowed vs isolated |
| Implicit to Explicit | Medium (2) | Easy (1) | 2:1 | Effect tracking requires analysis |
| Lazy to Strict | Hard (3) | Medium (2) | 1.5:1 | Infinite structures problematic |
| Strict to Lazy | Medium (2) | N/A | - | Space leak concerns only |
| **Concurrency** |||||
| Actors to Threads | Hard (4) | Hard (4) | 1:1 | Both require restructuring |
| STM to Locks | Medium (2) | Hard (3) | 1:1.5 | Lock ordering is harder |
| Green to OS Threads | Easy (1) | Medium (2) | 1:2 | Performance characteristics change |
| Channels to Async | Medium (2) | Medium (2) | 1:1 | Both have complex semantics |

---

## 2. Detailed Asymmetry Analysis

### 2.1 GC to Ownership (Asymmetry Ratio: 4:1)

The most significant asymmetry in language conversion.

#### GC to Ownership (Difficulty: 4)

Converting from garbage-collected memory to Rust-style ownership requires:

1. **Ownership determination** - Every value needs an owner
2. **Lifetime annotations** - Borrowed references require explicit lifetimes
3. **Data flow restructuring** - May need to change function signatures
4. **Clone vs borrow decisions** - Performance vs ergonomics tradeoffs

**Example:**

```python
# GC (Python) - Implicit memory management
def process(items):
    result = items      # Reference? Copy? Doesn't matter
    for item in result:
        transform(item)
    return result       # items still usable
```

```rust
// Ownership (Rust) - Multiple valid translations exist

// Option 1: Take ownership (move)
fn process(items: Vec<T>) -> Vec<T> {
    for item in &items {  // Must borrow to iterate
        transform(item);
    }
    items  // Return owned value
}

// Option 2: Borrow
fn process(items: &[T]) -> &[T] {
    for item in items {
        transform(item);
    }
    items  // Return borrowed slice
}

// Option 3: Clone for mutation
fn process(items: &[T]) -> Vec<T> {
    let mut result = items.to_vec();  // Clone
    for item in &mut result {
        transform(item);
    }
    result
}
```

**Why it's hard:**
- Python programmer doesn't think about ownership
- Multiple valid Rust translations exist
- Wrong choice leads to borrow checker errors or over-cloning
- May require redesigning data structures entirely

#### Ownership to GC (Difficulty: 1)

Converting Rust ownership to GC is trivial:

```rust
// Rust source
fn process(items: &[T]) -> Vec<T> {
    items.to_vec()
}
```

```python
# Python target - just ignore ownership annotations
def process(items):
    return list(items)  # GC handles memory
```

**Why it's easy:**
- Simply ignore ownership annotations
- Remove lifetime specifiers
- GC handles all memory automatically
- No decisions required

---

### 2.2 Static to Dynamic Typing (Asymmetry Ratio: 3:1)

#### Static to Dynamic (Difficulty: 1)

Type information can simply be erased:

```rust
fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

```python
def add(a, b):
    return a + b
```

**Why it's easy:**
- Remove type annotations
- Runtime handles type checking
- All static type features have dynamic equivalents

#### Dynamic to Static (Difficulty: 3)

Type information must be recovered:

```python
def process(data):
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, list):
        return [x * 2 for x in data]
    return data
```

```rust
// Must create explicit enum for dynamic behavior
enum Data {
    Text(String),
    Numbers(Vec<i32>),
    Other(Box<dyn Any>),
}

fn process(data: Data) -> Data {
    match data {
        Data::Text(s) => Data::Text(s.to_uppercase()),
        Data::Numbers(nums) => Data::Numbers(nums.iter().map(|x| x * 2).collect()),
        other => other,
    }
}
```

**Why it's hard:**
- Must analyze all possible runtime types
- isinstance checks become ADT variants
- Type inference tools (mypy, pyright) can help but aren't perfect
- Duck typing patterns require interface extraction

---

### 2.3 Mutable to Immutable Default (Asymmetry Ratio: 3:1)

#### Mutable to Immutable (Difficulty: 3)

Restructuring mutable algorithms:

```java
// Mutable (Java)
public List<Integer> process(List<Integer> items) {
    for (int i = 0; i < items.size(); i++) {
        items.set(i, items.get(i) * 2);  // Mutation
    }
    return items;
}
```

```haskell
-- Immutable (Haskell) - Must rebuild structure
process :: [Int] -> [Int]
process items = map (* 2) items  -- Creates new list
```

**Why it's hard:**
- In-place algorithms become recursive/fold patterns
- State threading through computations
- Graph algorithms particularly challenging
- May need persistent data structures

#### Immutable to Mutable (Difficulty: 1)

```haskell
process :: [Int] -> [Int]
process = map (* 2)
```

```java
public List<Integer> process(List<Integer> items) {
    return items.stream()
        .map(x -> x * 2)
        .collect(Collectors.toList());
    // Or use mutable version if desired
}
```

**Why it's easy:**
- Can directly translate or add mutation
- More options available, not fewer
- No structural changes required

---

### 2.4 Exceptions to Result Types (Asymmetry Ratio: 2:1)

#### Exceptions to Result (Difficulty: 2)

```java
public User findUser(String id) throws UserNotFoundException {
    User user = db.find(id);
    if (user == null) {
        throw new UserNotFoundException(id);
    }
    return user;
}
```

```rust
fn find_user(id: &str) -> Result<User, UserError> {
    db.find(id).ok_or(UserError::NotFound(id.to_string()))
}
```

**Why it's moderately difficult:**
- Must identify all throw sites
- Convert catch blocks to match expressions
- Propagation becomes explicit (? operator)
- Exception hierarchies become error enums

#### Result to Exceptions (Difficulty: 1)

```rust
fn find_user(id: &str) -> Result<User, UserError> {
    db.find(id).ok_or(UserError::NotFound(id.to_string()))
}
```

```java
public User findUser(String id) throws UserNotFoundException {
    return db.find(id)
        .orElseThrow(() -> new UserNotFoundException(id));
}
```

**Why it's easy:**
- Convert Ok to return
- Convert Err to throw
- Pattern is mechanical

---

### 2.5 Pure to Impure Effects (Asymmetry Ratio: 1:3)

This asymmetry is **reversed** - going to purity is harder.

#### Pure to Impure (Difficulty: 1)

```haskell
-- Pure (Haskell)
process :: String -> IO String
process input = do
    putStrLn $ "Processing: " ++ input
    return (map toUpper input)
```

```python
# Impure (Python) - Just call effects directly
def process(input):
    print(f"Processing: {input}")
    return input.upper()
```

**Why it's easy:**
- Remove IO monad wrapper
- Call effects directly
- No restructuring needed

#### Impure to Pure (Difficulty: 3)

```python
# Impure with hidden state
counter = 0

def process(input):
    global counter
    counter += 1
    print(f"Call #{counter}: {input}")
    return input.upper()
```

```haskell
-- Must isolate effects
data AppState = AppState { counter :: Int }

process :: String -> StateT AppState IO String
process input = do
    modify (\s -> s { counter = counter s + 1 })
    c <- gets counter
    liftIO $ putStrLn $ "Call #" ++ show c ++ ": " ++ input
    return (map toUpper input)
```

**Why it's hard:**
- Must identify ALL side effects
- Thread state explicitly
- Separate pure and impure code
- May need significant restructuring

---

### 2.6 Lazy to Strict Evaluation (Asymmetry Ratio: 1.5:1)

#### Lazy to Strict (Difficulty: 3)

```haskell
-- Lazy (Haskell) - Infinite list
naturals :: [Integer]
naturals = [0..]

firstTen = take 10 naturals  -- Works fine
```

```roc
# Strict (Roc) - Cannot represent infinite list
# Must use bounded or lazy wrapper

# Option 1: Bounded
naturals = List.range { start: At 0, end: Before maxInt }

# Option 2: Iterator/Stream type
naturals = \n -> { value: n, next: \() -> naturals (n + 1) }
```

**Why it's hard:**
- Infinite structures become impossible or require wrapping
- Evaluation order changes program semantics
- Space/time tradeoffs differ
- Some algorithms rely on laziness

#### Strict to Lazy (Difficulty: 2)

```python
def expensive():
    print("Computing...")  # Side effect reveals evaluation
    return 42

result = expensive()  # Evaluated immediately
```

```haskell
expensive :: IO Int
expensive = do
    putStrLn "Computing..."
    return 42

-- Result is a thunk, not evaluated until needed
result :: IO Int
result = expensive

-- Force evaluation when required
main = do
    r <- result
    r `seq` print r
```

**Why it's moderately difficult:**
- Must be aware of space leaks
- Side effect ordering changes
- May need explicit strictness annotations
- Generally easier because lazy is more permissive

---

## 3. Symmetric Gaps

These gaps are equally difficult in both directions for different reasons.

### 3.1 Actors to Threads (Both: Difficulty 4)

**Actors to Threads:**
- Convert mailbox to synchronized queue
- Replace message patterns with method calls
- Add explicit locking for state
- Lose isolation guarantees

**Threads to Actors:**
- Identify shared mutable state
- Wrap in GenServer/Actor
- Convert locks to message passing
- Design supervision trees

Both require fundamental restructuring of concurrency model.

### 3.2 CSP Channels to Async/Await (Both: Difficulty 2-3)

**Channels to Async:**
- Convert channels to Promises/Futures
- select becomes Promise.race
- Multi-producer patterns complex

**Async to Channels:**
- Create channel wrappers
- Await becomes channel receive
- Backpressure handling differs

### 3.3 HKT Languages (Both: Lossy)

Converting between Haskell/Scala (with HKT) and Go/Java (without):
- **HKT to No HKT:** Must monomorphize, lose abstraction
- **No HKT to HKT:** Cannot add abstraction that doesn't exist (but also nothing to lose)

This is symmetric in the sense that both directions have fundamental limitations.

---

## 4. Asymmetry by Family Pair

### 4.1 High Asymmetry Pairs (Ratio >= 3:1)

| From | To | Difficulty | Reverse | Ratio | Primary Asymmetry |
|------|----|-----------:|--------:|------:|-------------------|
| Dynamic | Systems | 4 | 2 | 2:1 | Type + Memory |
| ML-FP | Systems | 4 | 3 | 1.3:1 | Memory model |
| Managed-OOP | Systems | 3 | 2 | 1.5:1 | GC to ownership |
| Dynamic | ML-FP | 3 | 2 | 1.5:1 | Type inference |
| BEAM | Systems | 4 | - | High | Actor + memory |
| LISP | Systems | 4 | 3 | 1.3:1 | Macros + types |

### 4.2 Moderate Asymmetry Pairs (Ratio 1.5:1 - 2:1)

| From | To | Difficulty | Reverse | Ratio | Primary Asymmetry |
|------|----|-----------:|--------:|------:|-------------------|
| Managed-OOP | ML-FP | 3 | 3 | 1:1 | OOP to FP paradigm |
| BEAM | ML-FP | 3 | 3 | 1:1 | Concurrency model |
| Apple | Systems | 3 | 3 | 1:1 | ARC similarities |
| LISP | ML-FP | 3 | 2 | 1.5:1 | Macros, dynamic |

### 4.3 Low Asymmetry Pairs (Ratio ~1:1)

| From | To | Difficulty | Reverse | Ratio | Notes |
|------|----|-----------:|--------:|------:|-------|
| ML-FP | ML-FP | 2-3 | 2-3 | 1:1 | Within family |
| Dynamic | Dynamic | 2 | 2 | 1:1 | Within family |
| Systems | Systems | 2-3 | 2-3 | 1:1 | Memory model key |
| BEAM | LISP | 2 | 2 | 1:1 | Both FP, dynamic |

---

## 5. Implications for IR Design

### 5.1 Preserve Information in Hard Direction

The IR should preserve information that's hard to recover:

| Information Type | Hard to Recover From | Preserve For |
|-----------------|---------------------|--------------|
| Type annotations | Dynamic languages | Static targets |
| Ownership hints | GC languages | Ownership targets |
| Purity markers | Impure languages | Pure targets |
| Effect boundaries | Implicit effects | Explicit effects |
| Concurrency model | Thread-based | Actor-based |

### 5.2 Annotation Priorities

Based on asymmetry ratios, prioritize IR annotations:

1. **Priority 1 (4:1+ asymmetry):**
   - Ownership/lifetime hints
   - Type information from dynamic sources

2. **Priority 2 (2:1 - 3:1 asymmetry):**
   - Mutability markers
   - Effect boundaries
   - Nullability analysis

3. **Priority 3 (1:1 symmetric):**
   - Concurrency model markers (needed both ways)
   - Evaluation strategy hints

### 5.3 Lossy Conversion Warnings

The IR should track when conversions are lossy:

```yaml
conversion:
  from: haskell
  to: go
  warnings:
    - type: hkt_loss
      severity: high
      message: "Higher-kinded type abstraction will be monomorphized"
      patterns_affected: ["Functor", "Monad", "Traversable"]
    - type: laziness_loss
      severity: medium
      message: "Infinite data structures will require bounded alternatives"
```

### 5.4 Bidirectional Skill Pairing

Skills should be paired with awareness of asymmetry:

```yaml
skill_pair:
  forward: convert-python-rust
  reverse: convert-rust-python
  asymmetry_ratio: 4
  forward_challenges:
    - ownership_inference
    - type_annotation
    - borrow_checker_satisfaction
  reverse_challenges:
    - type_erasure  # Easy
  recommended_direction: reverse  # When possible
```

---

## 6. Summary Matrix

### 6.1 Asymmetry Heatmap

Difficulty of converting FROM row TO column. Higher = harder.

```
                ML-FP  BEAM  LISP  Systems  Dynamic  Managed  Apple  Logic  Proc
ML-FP             2     3     2      4        2        3       3      4      4
BEAM              3     2     2      4        2        3       3      5      4
LISP              3     2     2      4        2        3       3      4      4
Systems           3     4     3      2        2        2       3      5      2
Dynamic           3     3     2      4        2        2       3      4      2
Managed           3     3     3      3        2        2       2      5      2
Apple             3     4     3      3        2        2       2      5      3
Logic             4     4     3      5        4        5       5      2      4
Procedural        4     4     3      2        3        3       3      5      2
```

### 6.2 Asymmetry Ratio Matrix

Ratio of A-to-B difficulty vs B-to-A difficulty. Values > 1 mean A-to-B is harder.

```
                ML-FP  BEAM  LISP  Systems  Dynamic  Managed  Apple
ML-FP             1.0   1.0   1.0    1.3      0.7      1.0    1.0
BEAM              1.0   1.0   1.0    -        0.7      1.0    1.3
LISP              1.0   1.0   1.0    1.3      1.0      1.0    1.0
Systems           0.8   -     0.8    1.0      1.0      0.7    1.0
Dynamic           1.5   1.5   1.0    2.0      1.0      1.0    1.5
Managed           1.0   1.0   1.0    1.5      1.0      1.0    1.0
Apple             1.0   0.8   1.0    1.0      0.7      1.0    1.0
```

Key insights:
- **Dynamic to Systems (2.0):** Highest asymmetry, avoid this direction when possible
- **Systems to Dynamic (0.5):** Easiest cross-paradigm conversion
- **Logic family:** Asymmetric with almost everything (paradigm mismatch)

### 6.3 Recommended Conversion Directions

When bidirectional conversion is needed, prefer:

| Scenario | Preferred Direction | Reason |
|----------|---------------------|--------|
| Python <-> Rust | Rust to Python | Ownership info preserved |
| Java <-> Haskell | Haskell to Java | Type info preserved |
| JavaScript <-> Go | Go to JavaScript | Type erasure easier |
| Elixir <-> Rust | Rust to Elixir | Memory model simpler |
| Scala <-> Python | Scala to Python | Type info available |

---

## 7. Recommendations

### 7.1 Skill Development Priority

Based on asymmetry analysis, prioritize skills for the **harder direction**:

1. **Highest priority (4:1 asymmetry):**
   - `convert-python-rust` (GC to ownership)
   - `convert-javascript-rust`
   - `convert-python-golang`

2. **High priority (3:1 asymmetry):**
   - `convert-python-haskell` (dynamic to static + pure)
   - `convert-java-rust` (GC to ownership)
   - `convert-javascript-typescript` (type inference)

3. **Medium priority (2:1 asymmetry):**
   - `convert-java-haskell` (OOP to FP)
   - `convert-python-scala`

### 7.2 IR Layer Recommendations

| IR Layer | Key Annotations | Asymmetry Addressed |
|----------|-----------------|---------------------|
| Layer 1 (Types) | Inferred types from dynamic code | Static to Dynamic |
| Layer 2 (Memory) | Ownership hints, lifetime regions | GC to Ownership |
| Layer 3 (Effects) | Purity markers, effect boundaries | Impure to Pure |
| Layer 4 (Concurrency) | Actor boundaries, state isolation | Both directions |

### 7.3 Tooling Opportunities

High-asymmetry gaps indicate tooling opportunities:

| Gap | Tool Opportunity |
|-----|------------------|
| Dynamic to Static | Better type inference (mypy++, pyright++) |
| GC to Ownership | Ownership inference analyzer |
| Impure to Pure | Effect inference system |
| Callbacks to Async | Automatic async/await transform |

---

*Generated for task ai-p29.4*
