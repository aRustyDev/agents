# Human Decision Points Catalog

Comprehensive catalog of decision points extracted from 183 human_decision gaps requiring human intervention during language conversions.

**Generated:** 2026-02-04
**Source Data:** gap-analysis.json, patterns.sql, clustering-and-gaps.md
**Total Human Decision Gaps:** 183

---

## Executive Summary

The 183 human_decision gaps fall into distinct categories requiring different levels of human intervention:

| Decision Category | Count | Automation Potential |
|-------------------|-------|---------------------|
| Skill Reference (lang fundamentals) | 92 | High - redirect to skill |
| Methodology Reference | 46 | High - redirect to meta skill |
| Reverse Conversion | 18 | High - redirect to reverse skill |
| Platform/Runtime Decisions | 15 | Low - requires architecture input |
| Advanced Pattern Translation | 12 | None - case-by-case analysis |

---

## 1. Error Handling Decisions

### Decision: Exception vs Result Type

**Category:** error_handling
**Frequency:** common
**Automation:** partial (can suggest based on target language)

#### Context
When converting from exception-based languages (Python, Java) to result-based languages (Rust, Haskell, Go), developers must choose error handling strategy.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Result/Either types | Explicit, composable, no hidden control flow | More verbose, requires unwrapping | Rust, Haskell, F# |
| Exceptions/panic | Familiar, less ceremony | Hidden control flow, harder to reason | Python, Java fallback |
| Error returns (Go-style) | Simple, explicit | Repetitive, easy to ignore | Go |

#### Heuristics
- If target is Rust -> prefer `Result<T, E>`
- If target is Haskell -> prefer `Either` or custom error type
- If target is Go -> prefer `(value, error)` tuple returns
- If source uses exceptions for control flow -> restructure logic first

#### Example Scenario
**Source (Python):**
```python
def fetch_user(id: str) -> User:
    if not id:
        raise ValueError("ID required")
    user = db.get(id)
    if not user:
        raise NotFoundError(f"User {id} not found")
    return user
```

**Option A (Rust Result):**
```rust
fn fetch_user(id: &str) -> Result<User, UserError> {
    if id.is_empty() {
        return Err(UserError::InvalidId);
    }
    db.get(id).ok_or(UserError::NotFound(id.to_string()))
}
```

**Option B (Go errors):**
```go
func fetchUser(id string) (*User, error) {
    if id == "" {
        return nil, errors.New("ID required")
    }
    user, err := db.Get(id)
    if err != nil {
        return nil, fmt.Errorf("user %s not found: %w", id, err)
    }
    return user, nil
}
```

#### Tool Guidance
- Default recommendation: Match target language idiom
- When to prompt user: Mixed exception usage in source
- Information needed: Error recovery requirements, API contracts

---

### Decision: Ignoring Error Returns

**Category:** error_handling
**Frequency:** common
**Automation:** heuristic (lint-based detection)

**Source Pattern:** TypeScript -> Go
**Anti-pattern:** Ignoring error returns

#### Context
TypeScript developers may forget to check Go error returns, leading to silent failures.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Always check err != nil | Safe, idiomatic Go | Verbose | All Go code |
| Use must_ wrapper | Concise for panics | Crashes on error | Tests, CLI tools |
| Use errgroup | Concurrent error handling | More complex | Goroutine error aggregation |

#### Heuristics
- Always check errors in production code
- Use `must_` prefix functions only in tests
- Use `errgroup` for concurrent operations

#### Example Scenario
**Source (TypeScript):**
```typescript
const user = await fetchUser("123");
console.log(user.name);
```

**Correct (Go):**
```go
user, err := FetchUser("123")
if err != nil {
    return fmt.Errorf("failed to fetch user: %w", err)
}
fmt.Println(user.Name)
```

#### Tool Guidance
- Default: Generate error checks for all fallible operations
- Lint: Warn on unchecked errors
- Information needed: Error handling policy (log, return, panic)

---

## 2. Null/Optional Handling

### Decision: Force Unwrapping vs Safe Unwrapping

**Category:** null_handling
**Frequency:** common
**Automation:** partial (can detect force unwraps)

**Source Pattern:** Objective-C -> Swift
**Anti-pattern:** Force Unwrapping Optionals

#### Context
Objective-C's nil messaging is safe but Swift's `!` operator crashes on nil.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Optional chaining (`?.`) | Safe, concise | May propagate nil | Chained access |
| Guard let | Early exit, clear intent | Verbose | Function entry |
| If let | Scoped unwrap | Nested blocks | Conditional use |
| Nil coalescing (`??`) | Provides default | May hide nil issues | Default values |

#### Heuristics
- If Obj-C uses nil messaging chains -> use optional chaining
- If Obj-C checks nil explicitly -> use guard let
- Never use `!` unless 100% certain of non-nil

#### Example Scenario
**Source (Objective-C):**
```objc
NSString *name = [user name];
NSString *upper = [name uppercaseString];  // Safe: nil returns nil
```

**Correct (Swift):**
```swift
let name = user?.name
let upper = name?.uppercased() ?? ""
```

**Incorrect (Swift):**
```swift
let name = user!.name  // Crashes if user is nil
```

#### Tool Guidance
- Default: Use optional chaining
- Lint: Flag all `!` operators for review
- Information needed: Nil guarantees from context

---

### Decision: None/Null/Undefined Mapping

**Category:** null_handling
**Frequency:** common
**Automation:** partial (can suggest convention)

**Source Pattern:** Python -> TypeScript
**Decision:** Python `None` -> TypeScript `null` vs `undefined`

#### Context
Python has one null value (`None`), TypeScript has two (`null` and `undefined`).

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Always use `undefined` | Simpler, JS default | May conflict with JSON | Internal APIs |
| Always use `null` | JSON compatible, explicit | Not JS default | External APIs, JSON |
| Semantic distinction | Clear intent | Inconsistent, confusing | Domain-specific |

#### Heuristics
- If interfacing with JSON -> use `null`
- If optional parameters -> use `undefined`
- Pick one and be consistent within codebase

#### Example Scenario
**Source (Python):**
```python
def find_user(id: str) -> User | None:
    return users.get(id)  # Returns None if not found
```

**Option A (undefined):**
```typescript
function findUser(id: string): User | undefined {
    return users.get(id);
}
```

**Option B (null):**
```typescript
function findUser(id: string): User | null {
    return users.get(id) ?? null;
}
```

#### Tool Guidance
- Default: Use `undefined` for optional, `null` for explicit absence
- When to prompt: Project-wide convention not established
- Information needed: API contracts, JSON serialization needs

---

## 3. Concurrency Model

### Decision: Process-Based vs Pure State

**Category:** concurrency
**Frequency:** common
**Automation:** none (requires architecture redesign)

**Source Pattern:** Elixir -> Roc
**Anti-pattern:** Process-Based Thinking in Pure Code

#### Context
Elixir uses BEAM processes for state; Roc is purely functional without processes.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Explicit state passing | Pure, testable | Verbose | Pure functions |
| Platform-provided state | Familiar pattern | Platform-dependent | IO-heavy code |
| Immutable snapshots | Thread-safe | Memory overhead | Concurrent reads |

#### Heuristics
- If Elixir uses GenServer -> extract state type, pass explicitly
- If Elixir uses Agent -> convert to function parameters
- If Elixir uses ETS -> consider platform capabilities

#### Example Scenario
**Source (Elixir):**
```elixir
defmodule Counter do
  use GenServer
  def init(_), do: {:ok, 0}
  def handle_call(:increment, _from, count), do: {:reply, count + 1, count + 1}
end
```

**Target (Roc):**
```roc
State : I64

increment : State -> State
increment = \count -> count + 1

# State is passed explicitly, platform manages lifecycle
```

#### Tool Guidance
- Default: Extract state types, convert to pure functions
- When to prompt: Complex OTP supervision trees
- Information needed: State persistence requirements

---

### Decision: Lazy vs Strict Evaluation

**Category:** concurrency
**Frequency:** occasional
**Automation:** partial (can detect infinite structures)

**Source Pattern:** Haskell -> Roc, Haskell -> Scala
**Anti-pattern:** Assuming Lazy Evaluation

#### Context
Haskell is lazy by default; Roc and Scala are strict.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Finite bounds | Works everywhere | May need refactoring | Most cases |
| LazyList/Stream | Preserves semantics | Performance overhead | Large/infinite sequences |
| Iterator pattern | Memory efficient | More complex | Processing pipelines |

#### Heuristics
- If Haskell uses infinite lists -> add explicit bounds
- If Haskell uses `take n` on infinite -> use finite range
- If target is Scala -> use `LazyList` for deferred

#### Example Scenario
**Source (Haskell):**
```haskell
naturals = [0..]
evens = filter even naturals
take 10 evens  -- Works: only evaluates what's needed
```

**Target (Roc) - Finite:**
```roc
naturals = List.range { start: At 0, end: Before 1000 }
evens = List.keepIf naturals Num.isEven
List.takeFirst evens 10
```

**Target (Scala) - LazyList:**
```scala
val naturals = LazyList.from(0)
val evens = naturals.filter(_ % 2 == 0)
evens.take(10).toList
```

#### Tool Guidance
- Default: Convert to finite with explicit bounds
- Lint: Flag infinite structure patterns
- Information needed: Required element count, memory constraints

---

### Decision: OTP Distributed Systems

**Category:** concurrency
**Frequency:** rare
**Automation:** none (requires architectural redesign)

**Source Pattern:** Elixir -> F#
**Decision:** OTP distributed systems require .NET architectural redesign

#### Context
BEAM's OTP provides fault-tolerant distributed computing; .NET has different patterns.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Akka.NET | Actor model similar to OTP | Different semantics | Actor-based designs |
| Orleans | Virtual actors, managed | Less explicit supervision | Cloud-native |
| Raw async/await | Simple, familiar | No supervision tree | Simple concurrency |
| Message queues | Distributed-friendly | External dependency | Microservices |

#### Heuristics
- If using supervision trees -> consider Orleans virtual actors
- If using GenServer for state -> evaluate Akka.NET actors
- If using distributed Erlang -> consider message broker

#### Tool Guidance
- Default: Cannot automate; flag for architecture review
- When to prompt: Always for OTP-dependent code
- Information needed: Fault tolerance requirements, scale needs

---

## 4. Memory Management

### Decision: Clone vs Borrow vs Arc

**Category:** memory
**Frequency:** common
**Automation:** partial (can suggest based on usage patterns)

**Source Pattern:** C++ -> Rust, TypeScript -> Rust
**Anti-pattern:** Overusing Rc/Arc, Over-cloning to Satisfy Borrow Checker

#### Context
Developers from GC languages or C++ often over-use reference counting in Rust.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Borrowing (`&T`) | Zero cost, no allocation | Lifetime constraints | Most read access |
| Owned (`T`) | Simple, clear ownership | May require clone | Returned values |
| Box | Heap allocation, single owner | Indirection | Large types, recursion |
| Rc/Arc | Shared ownership | Overhead, cycles | Truly shared data |
| Clone | Simple, safe | Memory/CPU overhead | Small data, rare paths |

#### Heuristics
- Start with borrowing; add ownership only when needed
- Use `Box` for recursive types
- Use `Arc` only for cross-thread sharing
- Clone is acceptable for small types (< 64 bytes)

#### Example Scenario
**Source (C++):**
```cpp
std::shared_ptr<Node> parent;
std::vector<std::shared_ptr<Node>> children;
```

**Better (Rust):**
```rust
struct Node {
    value: i32,
    children: Vec<Box<Node>>,  // Owned children
}

fn process_nodes(nodes: &[Node]) {  // Borrowed slice
    // Work with borrowed references
}
```

#### Tool Guidance
- Default: Prefer borrowing, then owned, then Arc
- Lint: Flag excessive Rc/Arc usage
- Information needed: Lifetime requirements, threading model

---

### Decision: Lifetime Annotations

**Category:** memory
**Frequency:** common
**Automation:** partial (compiler assists)

**Source Pattern:** Go -> Rust
**Anti-pattern:** Trying to Return Borrowed References Without Lifetimes

#### Context
Go's GC handles memory; Rust requires explicit lifetime annotations for references.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Return owned | Simple, no lifetimes | May clone | Most cases |
| Return Box | Heap allocated, owned | Indirection | Large returns |
| Explicit lifetimes | Zero-copy | Complex signatures | Performance-critical |
| Static lifetime | Always valid | Restricts usage | Constants, statics |

#### Heuristics
- If returning data created in function -> return owned
- If returning subset of input -> use lifetime annotation
- If data is large and must be returned -> use Box

#### Example Scenario
**Source (Go):**
```go
func getData() *Data {
    return &Data{value: 42}  // GC handles memory
}
```

**Option A (Owned):**
```rust
fn get_data() -> Data {
    Data { value: 42 }
}
```

**Option B (Box):**
```rust
fn get_data() -> Box<Data> {
    Box::new(Data { value: 42 })
}
```

**Option C (Lifetime - for slices of input):**
```rust
fn get_slice<'a>(data: &'a [u8]) -> &'a [u8] {
    &data[0..10]
}
```

#### Tool Guidance
- Default: Return owned values
- When to prompt: Performance-sensitive code with large data
- Information needed: Data size, call frequency

---

## 5. Type Decisions

### Decision: Dynamic to Static Type Conversion

**Category:** types
**Frequency:** common
**Automation:** partial (can infer from usage)

**Source Pattern:** Clojure -> Haskell, Elixir -> Scala, Python -> any static
**Anti-pattern:** Dynamic Type Assumptions

#### Context
Dynamic languages allow heterogeneous collections; static languages require type uniformity.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Sum types (ADT) | Type-safe, exhaustive | More boilerplate | Known variants |
| Generics | Flexible, reusable | Type erasure issues | Homogeneous collections |
| Any/Object | Flexible | Type-unsafe | Legacy interop |
| Union types | Concise (TS) | Limited languages | TypeScript |

#### Heuristics
- If source has fixed set of types -> use sum type/sealed trait
- If source is always homogeneous -> use generic
- Avoid `Any` except for FFI/interop

#### Example Scenario
**Source (Clojure):**
```clojure
(def mixed [1 "two" :three 4.0])  ; Heterogeneous vector
```

**Target (Haskell):**
```haskell
data Value
    = IntVal Int
    | StringVal String
    | KeywordVal String
    | DoubleVal Double

mixed :: [Value]
mixed = [IntVal 1, StringVal "two", KeywordVal "three", DoubleVal 4.0]
```

**Target (Scala):**
```scala
sealed trait Data
case class IntData(value: Int) extends Data
case class StringData(value: String) extends Data
case class ListData[A](values: List[A]) extends Data
```

#### Tool Guidance
- Default: Create sum type with observed variants
- When to prompt: Unknown/open set of types
- Information needed: All possible value types

---

### Decision: Advanced Type System Features

**Category:** types
**Frequency:** rare
**Automation:** none (case-by-case analysis)

**Source Pattern:** Haskell -> Roc
**Decision:** GADTs, Type Families, DataKinds

#### Context
Advanced Haskell type features don't have direct equivalents in simpler type systems.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Simplify to basic types | Portable | Loses guarantees | Most cases |
| Runtime checks | Preserves logic | Not compile-time | Critical invariants |
| Phantom types | Some safety | Limited | Type-level tags |
| Manual encoding | Full control | Complex, error-prone | Experts only |

#### Heuristics
- If using GADTs for invariants -> add runtime checks
- If using type families -> use explicit type parameters
- If using DataKinds -> consider phantom types or simplify

#### Tool Guidance
- Default: Cannot automate; flag for manual review
- When to prompt: Any advanced GHC extension usage
- Information needed: Which invariants must be preserved

---

### Decision: Either Direction Convention

**Category:** types
**Frequency:** occasional
**Automation:** heuristic (can detect)

**Source Pattern:** F# -> Haskell
**Anti-pattern:** Confusing Either Direction

#### Context
F#'s `Result` uses `Ok/Error`; Haskell's `Either` uses `Right/Left` with Right being success.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Remember "Right is right" | Idiomatic Haskell | Counterintuitive | Haskell code |
| Use explicit Error type | Clearer semantics | More boilerplate | Production code |
| Use mtl/transformers | Compositional | Learning curve | Complex error handling |

#### Heuristics
- Right = success, Left = error (mnemonic: "right is right")
- Consider custom error types for clarity

#### Example Scenario
**Source (F#):**
```fsharp
let validate x = if x > 0 then Ok x else Error "Invalid"
```

**Correct (Haskell):**
```haskell
validate x = if x > 0 then Right x else Left "Invalid"
-- Right is success, Left is error
```

**Incorrect (Haskell):**
```haskell
validate x = if x > 0 then Left x else Right "Error"
-- WRONG: swapped semantics
```

#### Tool Guidance
- Default: Map Ok->Right, Error->Left
- Lint: Flag reversed Either usage patterns

---

## 6. Collection Choices

### Decision: Precision Integer Types

**Category:** collections
**Frequency:** common
**Automation:** partial (can suggest based on bounds)

**Source Pattern:** Python -> Rust
**Anti-pattern:** Arbitrary Precision Integer Overflow

#### Context
Python integers have arbitrary precision; Rust integers have fixed sizes and can overflow.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| i32/i64 | Fast, native | Overflow possible | Known bounds |
| u32/u64 | Fast, no negative | Smaller range | Counts, indices |
| BigInt (num_bigint) | No overflow | Slower, heap | Crypto, arbitrary math |
| Checked arithmetic | Safe, explicit | Verbose | Critical paths |

#### Heuristics
- If source uses integers < 2^63 -> use i64
- If source does big number math -> use BigInt
- If overflow is catastrophic -> use checked_*

#### Example Scenario
**Source (Python):**
```python
x = 10 ** 100  # No overflow, arbitrary precision
```

**Target (Rust):**
```rust
use num_bigint::BigInt;
use num_traits::pow::Pow;

let x = BigInt::from(10).pow(100_u32);  // No overflow
```

#### Tool Guidance
- Default: Use i64, flag large literals
- Lint: Warn on potential overflow patterns
- Information needed: Value ranges, overflow handling policy

---

### Decision: Mutable to Immutable Collections

**Category:** collections
**Frequency:** common
**Automation:** partial (can restructure)

**Source Pattern:** Python -> Clojure, Python -> Elixir, Python -> Scala
**Anti-pattern:** Mutable State / Expecting Mutable State

#### Context
Imperative languages mutate collections in-place; functional languages create new versions.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Rebinding | Pure, simple | Variable shadowing | Local transformations |
| Atoms/Refs | Mutable in FP way | Requires coordination | Shared state |
| Fold/Reduce | Functional, explicit | Learning curve | Aggregations |
| Transducers | Efficient composition | Complex | Pipelines |

#### Heuristics
- If mutation is local -> rebind with `let`
- If mutation is shared -> use language's ref type (atom, ref)
- If building up collection -> use fold/reduce

#### Example Scenario
**Source (Python):**
```python
items = [1, 2, 3]
items.append(4)
items.append(5)
```

**Target (Clojure):**
```clojure
;; Option A: Rebinding
(def items [1 2 3])
(def items (conj items 4))
(def items (conj items 5))

;; Option B: Atom for shared state
(def items (atom [1 2 3]))
(swap! items conj 4)
(swap! items conj 5)

;; Option C: Thread-first (best)
(-> [1 2 3]
    (conj 4)
    (conj 5))
```

#### Tool Guidance
- Default: Use threading macros or fold
- When to prompt: Stateful loops with complex logic
- Information needed: Scope of mutation, concurrent access

---

## 7. API Design

### Decision: Naming Conventions

**Category:** api
**Frequency:** common
**Automation:** full (mechanical transformation)

**Source Pattern:** F# -> Scala
**Issue:** PascalCase vs camelCase

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Follow target convention | Idiomatic | Diff from source | New code |
| Preserve source names | Easier mapping | Non-idiomatic | Migration phase |
| Configurable mapping | Flexible | More complexity | Large codebases |

#### Heuristics
- Types: PascalCase in most languages
- Methods/functions: camelCase (Scala, Java), snake_case (Rust, Python)
- Constants: SCREAMING_SNAKE_CASE or PascalCase

#### Example Scenario
**Source (F#):**
```fsharp
type Person = { FirstName: string; LastName: string }
let GetFullName person = $"{person.FirstName} {person.LastName}"
```

**Target (Scala):**
```scala
case class Person(firstName: String, lastName: String)
def getFullName(person: Person): String = s"${person.firstName} ${person.lastName}"
```

#### Tool Guidance
- Default: Auto-transform to target convention
- Lint: Flag non-idiomatic names
- Information needed: None (mechanical)

---

### Decision: Object Slicing Prevention

**Category:** api
**Frequency:** occasional
**Automation:** heuristic (can detect by-value class parameters)

**Source Pattern:** Java -> C++
**Anti-pattern:** Object Slicing

#### Context
C++ copies objects by value; passing derived class to base class parameter loses derived data.

#### Options
| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| Pass by reference | No slicing, polymorphic | Lifetime concerns | Most cases |
| Pass by pointer | Explicit, nullable | Manual memory | Optional args |
| Use smart pointers | Safe, clear ownership | Overhead | Ownership transfer |
| Make base class abstract | Prevents misuse | More restrictive | Type hierarchies |

#### Heuristics
- If function uses virtual methods -> pass by reference/pointer
- If ownership transfers -> use unique_ptr
- If shared -> use shared_ptr

#### Example Scenario
**Source (Java):**
```java
void process(Base obj) {  // No slicing in Java (reference semantics)
    obj.virtualMethod();
}
```

**Target (C++) - Correct:**
```cpp
void process(const Base& obj) {  // Reference: no slicing
    obj.virtualMethod();  // Polymorphic
}
```

**Target (C++) - Incorrect:**
```cpp
void process(Base obj) {  // Value: SLICING!
    obj.virtualMethod();  // Always calls Base version
}
```

#### Tool Guidance
- Default: Use const references for class parameters
- Lint: Flag by-value class parameters with virtual methods
- Information needed: Polymorphism requirements

---

## Summary Tables

### 1. Decision Points by Category

| Category | Decision Points | Common Triggers |
|----------|-----------------|-----------------|
| error_handling | 2 | Exception->Result, unchecked errors |
| null_handling | 2 | Force unwrap, null semantics |
| concurrency | 3 | Process->pure, lazy->strict, OTP |
| memory | 2 | Clone vs borrow, lifetimes |
| types | 3 | Dynamic->static, ADT, Either |
| collections | 2 | Precision, mutability |
| api | 2 | Naming, slicing |
| **Total** | **16** | |

### 2. Decision Points by Automation Potential

| Automation Level | Count | Examples |
|------------------|-------|----------|
| Full | 1 | Naming conventions |
| Heuristic | 5 | Error checking, slicing, Either direction |
| Partial | 7 | Result types, optional handling, clone/borrow |
| None | 3 | OTP redesign, advanced types, lazy->strict |

### 3. Most Common Decisions (from pattern frequency)

| Rank | Decision | Occurrences | Source->Target |
|------|----------|-------------|----------------|
| 1 | Dynamic->Static types | 29 | Python, Clojure, Elixir -> static langs |
| 2 | Mutable->Immutable | 18 | Python -> FP languages |
| 3 | Error handling model | 15 | Exceptions -> Results |
| 4 | Memory ownership | 12 | GC langs -> Rust |
| 5 | Null/Optional handling | 10 | Obj-C->Swift, Python->TS |

### 4. Decision Tree for Common Scenarios

```
START: What type of conversion?
|
+-- Error handling change?
|   |
|   +-- Source uses exceptions?
|   |   +-- Target is Rust -> Result<T,E>
|   |   +-- Target is Go -> (value, error)
|   |   +-- Target is Haskell -> Either/ExceptT
|   |
|   +-- Source uses return codes?
|       +-- Convert to target idiom directly
|
+-- Memory model change?
|   |
|   +-- Source is GC'd?
|   |   +-- Target is Rust -> Start with owned, add borrows
|   |   +-- Target is C++ -> Use smart pointers
|   |
|   +-- Source is manual?
|       +-- Target is Rust -> Map ownership explicitly
|
+-- Type system change?
|   |
|   +-- Dynamic to Static?
|   |   +-- Known variants -> Sum type/sealed trait
|   |   +-- Unknown variants -> Flag for review
|   |
|   +-- Static to Static?
|       +-- Map types directly, handle gaps
|
+-- Concurrency model change?
    |
    +-- Source has actors/processes?
    |   +-- Target supports actors -> Map pattern
    |   +-- Target is pure FP -> Extract state, pass explicitly
    |
    +-- Source is threaded?
        +-- Target is async -> Convert to async/await
        +-- Target has channels -> Use message passing
```

---

## Human Decision Gap Classification

### Skill Reference Gaps (92 gaps)
These redirect to language-specific skills:

| Pattern | Count | Mitigation |
|---------|-------|------------|
| `{Lang} language fundamentals` | 46 | `lang-{lang}-dev` skill |
| Advanced memory engineering | 2 | `lang-{lang}-memory-eng` skill |

### Methodology Reference Gaps (46 gaps)
These redirect to conversion methodology:

| Pattern | Count | Mitigation |
|---------|-------|------------|
| `General conversion methodology` | 46 | `meta-convert-dev` skill |

### Reverse Conversion Gaps (18 gaps)
These redirect to reverse skills:

| Pattern | Count | Mitigation |
|---------|-------|------------|
| `Reverse conversion (X -> Y)` | 18 | `convert-{y}-{x}` skill |

### Platform/Runtime Gaps (15 gaps)
These require architecture decisions:

| Gap | Source | Target | Decision Type |
|-----|--------|--------|---------------|
| ClojureScript specifics | clojure | elixir | Platform choice |
| ClojureScript -> Elm | clojure | elm | Runtime model |
| Phoenix LiveView | elixir | elm | Architecture |
| OTP distributed | elixir | fsharp | Architecture |
| Browser-specific Elm | elm | roc | Platform |
| .NET interop | fsharp | haskell | FFI strategy |
| Web frameworks | python | haskell | Framework |

### Advanced Pattern Gaps (12 gaps)
These require case-by-case analysis:

| Gap | Languages | Why Manual |
|-----|-----------|------------|
| C++ metaprogramming (SFINAE, CRTP) | cpp -> rust | No direct equivalent |
| Advanced type features (GADTs, Type Families) | haskell -> roc | Simpler type system |
| Type provider patterns | fsharp -> scala | No direct equivalent |
| Advanced Scala libraries | python -> scala | Domain-specific |
| SwiftUI -> UIKit | objc -> swift | Framework migration |

---

## Appendix: Anti-Pattern Decision Points

The 29 negative patterns also represent decision points - specifically, decisions that should be avoided:

| Anti-Pattern | Category | Decision to Make |
|--------------|----------|------------------|
| Use-After-Free | memory | Use ownership/borrowing correctly |
| Overusing Rc/Arc | memory | Prefer borrowing first |
| Over-cloning | memory | Learn to work with references |
| Force Unwrapping | null_handling | Use safe unwrap patterns |
| Ignoring Error Returns | error_handling | Always check errors |
| Assuming Dynamic Typing | types | Define explicit types |
| Expecting Mutable State | collections | Use immutable patterns |
| Assuming Lazy Evaluation | concurrency | Add explicit strictness |
| Object Slicing | api | Pass by reference |

---

## Data Sources

- **Gap Analysis:** `.claude/plans/merge-convert-skills/data/gap-analysis.json`
- **Pattern Database:** `.claude/plans/merge-convert-skills/data/patterns.sql`
- **Clustering Analysis:** `.claude/plans/merge-convert-skills/analysis/clustering-and-gaps.md`
- **Gap Classification:** `.claude/plans/merge-convert-skills/analysis/gap-classification.md`
