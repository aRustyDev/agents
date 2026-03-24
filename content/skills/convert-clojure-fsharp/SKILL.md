---
name: convert-clojure-fsharp
description: Bidirectional conversion between Clojure and Fsharp. Use when migrating projects between these languages in either direction. Extends meta-convert-dev with Clojure↔Fsharp specific patterns.
---

# Convert Clojure to F#

Convert Clojure code to idiomatic F#. This skill extends `meta-convert-dev` with Clojure-to-F# specific type mappings, idiom translations, and tooling for converting functional code from JVM/Lisp to .NET/ML platforms.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Clojure dynamic types → F# static types with type inference
- **Idiom translations**: Clojure Lisp-style patterns → idiomatic F# ML-style
- **Error handling**: Clojure exception model → F# Result type and railway-oriented programming
- **Async patterns**: Clojure core.async and futures → F# async workflows and tasks
- **Platform translation**: JVM ecosystem → .NET CLR ecosystem
- **REPL workflow**: Clojure REPL-driven development → F# FSI and interactive development

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Clojure language fundamentals - see `lang-clojure-dev`
- F# language fundamentals - see `lang-fsharp-dev`

---

## Quick Reference

| Clojure | F# | Notes |
|---------|-----|-------|
| `String` | `string` | Direct mapping (both use platform strings) |
| `Long` | `int64` / `int` | Clojure integers are longs; F# defaults to int32 |
| `Double` | `float` | Clojure floats are doubles; F# float is double |
| `Boolean` | `bool` | `true`/`false` in both |
| `[...]` vector | `list<'T>` | Clojure vector → F# list (immutable) |
| lazy seq | `seq<'T>` | Both are lazy, composable sequences |
| Java array | `'T[]` array | Use F# arrays for mutable indexed access |
| `{...}` map | `Map<'K,'V>` | Clojure hash-map → F# immutable Map |
| `#{...}` set | `Set<'T>` | Clojure hash-set → F# immutable Set |
| `nil` | `None` | Clojure nil → F# Option type |
| `{:ok ...} / {:error ...}` | `Result<'T,'E>` | Convention-based → type-safe discriminated union |
| `defrecord` / map | Record type | Tagged map → strongly-typed record |
| Tagged map with `:type` | Discriminated union | Runtime dispatch → compile-time variant |
| `future` | `async { }` | JVM futures → F# async workflows |
| `fn` or `defn` | `fun` or `let` | Lambda/function definition |
| Thread-last `->>` | Pipe `\|>` | Data threading |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - plan dynamic → static type strategy
3. **Preserve semantics** over syntax similarity
4. **Adopt F# idioms** - don't write "Clojure code in F# syntax"
5. **Handle edge cases** - nil-safety, error paths, lazy evaluation differences
6. **Test equivalence** - same inputs → same outputs
7. **Embrace static typing** - use F#'s type system to catch errors at compile time
8. **Leverage type inference** - F# can infer most types, annotations optional

---

## Type System Mapping

### Primitive Types

| Clojure | F# | Notes |
|---------|-----|-------|
| `Boolean` | `bool` | `true`/`false` (same in both) |
| `Byte` | `byte` | 8-bit unsigned (F# has sbyte for signed) |
| `Short` | `int16` | 16-bit signed |
| `Integer` | `int` / `int32` | 32-bit signed (F# default int) |
| `Long` | `int64` | 64-bit signed (Clojure default integer type) |
| `Float` | `single` / `float32` | 32-bit floating point |
| `Double` | `double` / `float` | 64-bit floating point (F# default float) |
| `BigInteger` | `bigint` | Arbitrary precision integers |
| `BigDecimal` | `decimal` | Arbitrary precision decimals |
| `Character` | `char` | UTF-16 code unit |
| `String` | `string` | Immutable strings (both platforms) |
| `nil` | - | Use `Option<'T>` (None for nil, Some for value) |

### Collection Types

| Clojure | F# | Notes |
|---------|-----|-------|
| `[...]` vector | `list<'T>` | Persistent vector → immutable list |
| `'(...)` list | `list<'T>` | Clojure list → F# list (both linked lists) |
| lazy seq | `seq<'T>` | Lazy sequences in both |
| Java array / vector | `'T[]` | Use F# arrays for mutable indexed access |
| `{...}` hash-map | `Map<'K,'V>` | Persistent map → immutable Map |
| `#{...}` hash-set | `Set<'T>` | Persistent set → immutable Set |
| `(atom [...])` | `'T ref` / mutable | Atom-wrapped vector → mutable reference |
| `nil` or value | `Option<'T>` | None/Some wrapping |
| `{:ok v}` / `{:error e}` | `Result<'T,'E>` | Convention → discriminated union |
| `[a b]` tuple | `'A * 'B` | Clojure vector → F# tuple |

### Composite Types

| Clojure | F# | Notes |
|---------|-----|-------|
| `defrecord` | Record type | When protocols/polymorphism needed |
| Plain map `{...}` | Record type | Data structure → strongly-typed record |
| Tagged map `{:type :variant ...}` | Discriminated union | Runtime tag → compile-time variant |
| Protocol | Interface / Abstract class | Behavior contracts |
| `defmulti`/`defmethod` | Discriminated union + pattern match | Dynamic dispatch → static dispatch |
| Map with `:type` key | Single-case union | Type safety wrapper |
| Nested maps | Nested record types | Structure becomes explicit |

### Function Types

| Clojure | F# | Notes |
|---------|-----|-------|
| `(fn [a] b)` | `'a -> 'b` | Single-argument function |
| `(fn [a b] c)` | `'a -> 'b -> 'c` | Multi-argument → curried |
| `(fn [] a)` | `unit -> 'a` | Nullary function/thunk |
| Multi-arity `defn` | Multiple `let` bindings / overloads | Arity dispatch → separate functions |
| Variadic `& args` | `params 'a[]` or list | Rest args → array or list parameter |
| Generic (no types) | Generic `'a` | Dynamic → parameterized types |
| Runtime type check | Type constraint | `'a when 'a : IComparable` |

---

## Idiom Translation

### Pattern 1: Nil Handling to Option Type

**Clojure:**
```clojure
;; User as map
(def user {:name "Alice" :email "alice@example.com"})

(defn get-email-domain [user]
  (if-let [email (:email user)]
    (second (clojure.string/split email #"@"))
    "no-domain"))

;; Using some-> threading (stops on nil)
(some-> user :email (clojure.string/split #"@") second)
```

**F#:**
```fsharp
// User as record
type User = { Name: string; Email: string option }

let getEmailDomain user =
    user.Email
    |> Option.map (fun email -> email.Split('@').[1])
    |> Option.defaultValue "no-domain"

// Pattern matching
let getEmailDomain' user =
    match user.Email with
    | Some email -> email.Split('@').[1]
    | None -> "no-domain"
```

**Why this translation:**
- Clojure `nil` → F# `None` (explicit absence)
- Clojure `if-let` / `when-let` → F# `Option.map` / `Option.bind`
- Clojure `some->` threading → F# Option combinators
- F# makes nullability explicit in the type system
- Pattern matching provides exhaustive checking

### Pattern 2: Exception-Based to Result Type Error Handling

**Clojure:**
```clojure
;; Exception-based (idiomatic Clojure)
(defn divide [x y]
  (when (zero? y)
    (throw (ex-info "Division by zero" {:x x :y y})))
  (/ x y))

(defn compute [a b c]
  (try
    (* (/ (/ a b) c) 2)
    (catch Exception e
      {:error (.getMessage e)})))

;; Or convention-based error handling
(defn divide-safe [x y]
  (if (zero? y)
    {:error "Division by zero"}
    {:ok (/ x y)}))
```

**F#:**
```fsharp
// Result type (idiomatic F#)
let divide x y =
    if y = 0 then
        Error "Division by zero"
    else
        Ok (x / y)

// Railway-oriented programming
let compute a b c =
    result {
        let! step1 = divide a b
        let! step2 = divide step1 c
        return step2 * 2
    }

// Or using Result.bind
let compute' a b c =
    divide a b
    |> Result.bind (fun x -> divide x c)
    |> Result.map (fun x -> x * 2)
```

**Why this translation:**
- Clojure exceptions → F# Result type (errors as values)
- Clojure `{:ok/:error}` conventions → F# discriminated unions
- Explicit error handling at compile time
- Railway-oriented programming for chaining fallible operations
- Type safety prevents forgetting error cases

### Pattern 3: Vector Processing with Threading Macros to Pipe Operator

**Clojure:**
```clojure
(defn process-items [items]
  (->> items
       (filter :is-active)
       (map :value)
       (reduce +)))

;; Or using tranducers
(defn process-items-xf [items]
  (transduce
    (comp (filter :is-active)
          (map :value))
    +
    items))
```

**F#:**
```fsharp
// Using pipe operator
let processItems items =
    items
    |> List.filter (fun x -> x.IsActive)
    |> List.map (fun x -> x.Value)
    |> List.sum

// More concise with accessor functions
let processItems' items =
    items
    |> List.filter _.IsActive
    |> List.map _.Value
    |> List.sum

// Lazy evaluation with sequences
let processItemsLazy items =
    items
    |> Seq.filter (fun x -> x.IsActive)
    |> Seq.map (fun x -> x.Value)
    |> Seq.sum
```

**Why this translation:**
- Clojure `->>` (thread-last) → F# `|>` (pipe forward)
- Clojure `filter`/`map`/`reduce` → F# `List.filter`/`List.map`/`List.sum`
- Both support lazy evaluation (seqs in Clojure, `Seq` in F#)
- F# pipe operator is data-first (same as thread-last)
- Tranducers → F# doesn't have direct equivalent, use sequences

### Pattern 4: Tagged Maps to Discriminated Unions

**Clojure:**
```clojure
;; Constructor functions
(defn circle [radius]
  {:type :circle :radius radius})

(defn rectangle [width height]
  {:type :rectangle :width width :height height})

(defn triangle [base height]
  {:type :triangle :base base :height height})

;; Using multimethods for dispatch
(defmulti area :type)

(defmethod area :circle [{:keys [radius]}]
  (* Math/PI radius radius))

(defmethod area :rectangle [{:keys [width height]}]
  (* width height))

(defmethod area :triangle [{:keys [base height]}]
  (* 0.5 base height))

;; Usage
(area (circle 5.0))      ;; => 78.53981633974483
(area (rectangle 4 5))   ;; => 20
```

**F#:**
```fsharp
// Discriminated union
type Shape =
    | Circle of radius: float
    | Rectangle of width: float * height: float
    | Triangle of baseLen: float * height: float

// Pattern matching for dispatch
let area shape =
    match shape with
    | Circle r -> System.Math.PI * r * r
    | Rectangle (w, h) -> w * h
    | Triangle (b, h) -> 0.5 * b * h

// Usage
let shapes = [
    Circle 5.0
    Rectangle (4.0, 5.0)
    Triangle (6.0, 8.0)
]

shapes |> List.map area
// [78.54; 20.0; 24.0]
```

**Why this translation:**
- Clojure tagged maps → F# discriminated unions
- Runtime `:type` tag → compile-time variant type
- `defmulti`/`defmethod` → pattern matching
- Exhaustive pattern matching ensures all cases handled
- Type safety prevents typos in variant names

### Pattern 5: Immutable Data Updates

**Clojure:**
```clojure
;; Plain map (most common)
(def person {:first-name "Alice" :last-name "Smith" :age 30})
(def older-person (assoc person :age 31))

;; Or using update
(def older-person (update person :age inc))

;; Nested updates
(def user {:profile {:name "Alice" :email "alice@example.com"}})
(def updated-user (assoc-in user [:profile :email] "newemail@example.com"))

(def incremented-user (update-in user [:profile :age] inc))
```

**F#:**
```fsharp
// Record type
type Person = {
    FirstName: string
    LastName: string
    Age: int
}

let person = { FirstName = "Alice"; LastName = "Smith"; Age = 30 }
let olderPerson = { person with Age = 31 }

// Nested records
type Profile = { Name: string; Email: string }
type User = { Profile: Profile }

let user = { Profile = { Name = "Alice"; Email = "alice@example.com" } }
let updatedUser = { user with Profile = { user.Profile with Email = "newemail@example.com" } }

// Helper functions for complex updates
let updateEmail newEmail user =
    { user with Profile = { user.Profile with Email = newEmail } }

let updatedUser' = user |> updateEmail "newemail@example.com"
```

**Why this translation:**
- Clojure `assoc` → F# copy-and-update `{ r with ... }`
- Clojure `update` → F# update with function
- Clojure `assoc-in`/`update-in` → F# nested copy-and-update or helper functions
- Both are immutable by default
- F# records have named fields vs. Clojure keyword keys

### Pattern 6: Lazy Sequences

**Clojure:**
```clojure
;; Infinite sequence
(def naturals (iterate inc 0))
(take 5 naturals) ;; => (0 1 2 3 4)

;; Lazy evaluation
(def evens (filter even? naturals))
(take 3 evens) ;; => (0 2 4)

;; List comprehension
(def squares (for [x (range 10)] (* x x)))

;; Realized only when consumed
(take 5 squares) ;; => (0 1 4 9 16)
```

**F#:**
```fsharp
// Infinite sequence
let naturals = Seq.initInfinite id
Seq.take 5 naturals |> Seq.toList
// [0; 1; 2; 3; 4]

// Lazy evaluation
let evens = Seq.filter (fun x -> x % 2 = 0) naturals
Seq.take 3 evens |> Seq.toList
// [0; 2; 4]

// Sequence expression (lazy)
let squares = seq { for x in 0..9 -> x * x }

// Realized only when enumerated
Seq.take 5 squares |> Seq.toList
// [0; 1; 4; 9; 16]

// Infinite Fibonacci
let fibonacci =
    Seq.unfold (fun (a, b) -> Some(a, (b, a + b))) (0, 1)

Seq.take 10 fibonacci |> Seq.toList
// [0; 1; 1; 2; 3; 5; 8; 13; 21; 34]
```

**Why this translation:**
- Clojure lazy seqs → F# `seq<'T>` (IEnumerable)
- `iterate` → `Seq.initInfinite` / `Seq.unfold`
- `for` comprehension → F# `seq { }` expression
- Both evaluate lazily on demand
- Both support infinite sequences safely

### Pattern 7: Async and Concurrency

**Clojure:**
```clojure
;; Using futures (simple parallelism)
(defn fetch-user [user-id]
  (Thread/sleep 100)
  {:id user-id :name (str "User" user-id)})

(defn process-users [user-ids]
  (let [futures (map #(future (fetch-user %)) user-ids)
        users (map deref futures)]
    (reduce + (map :id users))))

;; Using core.async (CSP-style)
(require '[clojure.core.async :as async :refer [go <! >!]])

(defn fetch-user-async [user-id]
  (go
    (<! (async/timeout 100))
    {:id user-id :name (str "User" user-id)}))

(defn process-users-async [user-ids]
  (go
    (let [channels (map fetch-user-async user-ids)
          users (<! (async/merge channels))]
      (reduce + (map :id users)))))
```

**F#:**
```fsharp
// Async workflows
let fetchUser userId = async {
    do! Async.Sleep 100
    return { Id = userId; Name = $"User{userId}" }
}

let processUsers userIds = async {
    let! users =
        userIds
        |> List.map fetchUser
        |> Async.Parallel

    return users |> Array.sumBy (fun u -> u.Id)
}

// Run async
processUsers [1; 2; 3; 4; 5]
|> Async.RunSynchronously
// Returns: 15

// Task-based (more .NET-idiomatic)
let fetchUserTask userId = task {
    do! Task.Delay 100
    return { Id = userId; Name = $"User{userId}" }
}

let processUsersTask userIds = task {
    let! users =
        userIds
        |> List.map fetchUserTask
        |> Task.WhenAll

    return users |> Array.sumBy (fun u -> u.Id)
}
```

**Why this translation:**
- Clojure `future` → F# `async { }` workflows or `task { }`
- Clojure `deref` (`@`) → F# `Async.RunSynchronously` or `await`
- Clojure core.async channels → F# MailboxProcessor or async workflows
- F# `Async.Parallel` for parallel execution
- F# has both async (F# workflows) and Task (.NET tasks)

### Pattern 8: Macros to Computation Expressions

**Clojure:**
```clojure
;; Macros for DSL creation
(defmacro when-let [bindings & body]
  `(let ~bindings
     (when ~(first bindings)
       ~@body)))

;; Threading macros (built-in)
(-> x f g h)
(->> coll (map f) (filter pred))

;; Custom control flow
(defmacro unless [condition & body]
  `(if (not ~condition)
     (do ~@body)))
```

**F#:**
```fsharp
// Computation expressions (similar to macros for DSL)
type MaybeBuilder() =
    member _.Bind(x, f) = Option.bind f x
    member _.Return(x) = Some x
    member _.ReturnFrom(x) = x

let maybe = MaybeBuilder()

let validateAge age = maybe {
    let! validAge =
        if age >= 0 && age <= 120 then Some age
        else None
    return validAge
}

// Result computation expression
type ResultBuilder() =
    member _.Bind(x, f) = Result.bind f x
    member _.Return(x) = Ok x
    member _.ReturnFrom(x) = x

let result = ResultBuilder()

let divideBy x y = maybe {
    let! result =
        if y <> 0 then Some (x / y)
        else None
    return result
}

// Pipe operators (built-in, not macros)
let result =
    x
    |> f
    |> g
    |> h
```

**Why this translation:**
- Clojure macros → F# computation expressions (for DSLs)
- Thread macros → F# pipe operators (built-in, not meta-programming)
- Clojure compile-time code generation → F# computation builders
- F# computation expressions are more constrained but type-safe
- F# favors built-in language features over custom syntax

---

## Paradigm Translation

### Mental Model Shift: Dynamic Lisp → Static ML

| Clojure Concept | F# Approach | Key Insight |
|-----------------|-------------|-------------|
| Dynamic typing | Static with inference | Types inferred at compile time |
| Data-driven design | Type-driven design | Types guide design and prevent errors |
| Maps with keyword keys | Records with named fields | Structure defined by types vs. convention |
| `defmulti`/`defmethod` | Discriminated unions + pattern matching | Dynamic dispatch → static exhaustive matching |
| S-expressions | ML syntax | Prefix notation → infix/pipeline notation |
| REPL-first | Type-first with FSI | Interactive but type-guided development |
| Macros for DSL | Computation expressions | Compile-time code gen → type-safe builders |
| Lazy by default (seqs) | Explicit lazy (seq) | Lazy sequences explicit in F# |

### Concurrency Mental Model

| Clojure Model | F# Model | Conceptual Translation |
|---------------|----------|------------------------|
| `future` | `async { }` | JVM future → F# async workflow |
| `pmap` | `Async.Parallel` / `Array.Parallel.map` | Parallel map → parallel execution |
| `@future` | `Async.RunSynchronously` | Dereference → blocking wait |
| Agent | MailboxProcessor | Agent-based → message-passing actor |
| core.async channels | MailboxProcessor / async channels | CSP channels → F# mailbox or async |
| Atoms/Refs | `ref<'T>` / mutable | Managed state → mutable references |

---

## Error Handling

### Clojure Error Model → F# Error Model

Clojure primarily uses exceptions with some convention-based error handling. F# strongly favors Result types and railway-oriented programming.

**Clojure Exception Pattern:**
```clojure
(defn parse-age [input]
  (try
    (let [age (Integer/parseInt input)]
      (if (>= age 0)
        age
        (throw (ex-info "Age cannot be negative" {:input input}))))
    (catch NumberFormatException e
      (throw (ex-info "Invalid number" {:input input} e)))))

;; Or return error map
(defn parse-age-safe [input]
  (try
    (let [age (Integer/parseInt input)]
      (if (>= age 0)
        {:ok age}
        {:error "Age cannot be negative"}))
    (catch NumberFormatException e
      {:error "Invalid number"})))
```

**F# Result Pattern (Idiomatic):**
```fsharp
// Result type (built-in discriminated union)
type ParseError =
    | InvalidNumber of string
    | NegativeAge of string

let parseAge input =
    match System.Int32.TryParse(input) with
    | false, _ -> Error (InvalidNumber input)
    | true, age when age < 0 -> Error (NegativeAge input)
    | true, age -> Ok age

// Railway-oriented programming
let validateAndProcess input =
    result {
        let! age = parseAge input
        let! category =
            if age < 18 then Ok "minor"
            elif age < 65 then Ok "adult"
            else Ok "senior"
        return (age, category)
    }
```

**Error Propagation:**

| Clojure | F# | Notes |
|---------|-----|-------|
| `try`/`catch` | `Result.bind` | Exception propagation → explicit Result chaining |
| Manual `if` checks on `{:ok/:error}` | Pattern matching on Result | Convention → type-safe |
| Nested try/catch | Computation expression | Imperative → declarative |
| `ex-info` with data | Custom error types | Exception with map → discriminated union |
| Throw/catch | Result/Option | Exceptional control flow → values |

**F# Option vs Result:**
```fsharp
// Use Option for absence vs. presence
let findUser id =
    if id = 1 then Some { Id = 1; Name = "Alice" }
    else None

// Use Result for success vs. failure with error info
let validateEmail email =
    if email.Contains("@") then Ok email
    else Error "Invalid email format"

// Combining both
let getUser id =
    match findUser id with
    | None -> Error "User not found"
    | Some user -> Ok user
```

---

## Concurrency Patterns

### Clojure Async → F# Async

**Simple async operation:**

```clojure
;; Clojure with future
(defn fetch-data [url]
  (future
    (slurp url)))

;; Clojure with core.async
(require '[clojure.core.async :as async :refer [go <!]])

(defn fetch-data-async [url]
  (go
    (:body (http/get url))))
```

```fsharp
// F# async workflow
let fetchData url = async {
    use client = new System.Net.Http.HttpClient()
    let! response = client.GetStringAsync(url) |> Async.AwaitTask
    return response
}

// F# task (more .NET-idiomatic)
let fetchDataTask url = task {
    use client = new System.Net.Http.HttpClient()
    let! response = client.GetStringAsync(url)
    return response
}
```

**Parallel execution:**

```clojure
;; Clojure with pmap (parallel map)
(defn fetch-all [urls]
  (pmap fetch-data urls))

;; Clojure with futures
(defn fetch-all-futures [urls]
  (let [futures (map #(future (fetch-data %)) urls)]
    (map deref futures)))
```

```fsharp
// F# Async.Parallel
let fetchAll urls = async {
    let! results =
        urls
        |> List.map fetchData
        |> Async.Parallel
    return results |> Array.toList
}

// F# Array.Parallel for CPU-bound work
let processAll items =
    items
    |> Array.Parallel.map expensiveComputation
```

**Agent/Actor Pattern:**

```clojure
;; Clojure with agent
(def counter (agent 0))

(defn increment! []
  (send counter inc))

(defn get-value []
  @counter)

;; Or with core.async
(defn counter-loop [initial-state]
  (let [ch (chan)]
    (go
      (loop [state initial-state]
        (let [msg (<! ch)]
          (case (:type msg)
            :increment (recur (inc state))
            :get-value (do
                        (>! (:reply msg) state)
                        (recur state))))))
    ch))
```

```fsharp
// F# MailboxProcessor (actor)
type CounterMessage =
    | Increment
    | GetValue of AsyncReplyChannel<int>

let createCounter initialValue =
    MailboxProcessor.Start(fun inbox ->
        let rec loop count = async {
            let! msg = inbox.Receive()
            match msg with
            | Increment ->
                return! loop (count + 1)
            | GetValue reply ->
                reply.Reply count
                return! loop count
        }
        loop initialValue)

// Usage
let counter = createCounter 0
counter.Post Increment
counter.Post Increment
let count = counter.PostAndReply GetValue  // Returns 2
```

---

## Memory & Platform Translation

### JVM → .NET CLR

Both Clojure and F# run on managed runtimes with garbage collection, but there are platform differences:

| Aspect | Clojure (JVM) | F# (.NET) | Translation |
|--------|---------------|-----------|-------------|
| Memory model | JVM GC | CLR GC | Both are GC'd; no ownership concerns |
| Value types | Primitives (boxed in collections) | Structs (stack-allocated) | Use value types where beneficial |
| Reference types | Objects (heap) | Classes (heap) | Direct mapping |
| Nullability | `nil` everywhere | Can be null | Use Option to prevent null |
| Generics | Type erasure | Reified generics | Full type info at runtime |
| Primitive types | Java types (Long, Double) | .NET types (int64, float) | Different defaults, similar semantics |

**No explicit memory management needed in either language.** Focus on:
- Avoiding excessive allocations
- Using appropriate data structures (mutable when needed)
- Leveraging persistent data structures (both languages)

**Platform Library Mapping:**

| Category | Clojure (JVM) | F# (.NET) |
|----------|---------------|-----------|
| HTTP | clj-http, http-kit | System.Net.Http, HttpClient |
| JSON | cheshire, jsonista | System.Text.Json, Newtonsoft.Json |
| Date/Time | java.time, clj-time | System.DateTime, NodaTime |
| Regex | java.util.regex (`#"..."`) | System.Text.RegularExpressions |
| Collections | clojure.core | System.Collections, FSharp.Collections |
| Async | future, core.async | async/await, Task, MailboxProcessor |
| Testing | clojure.test, Midje | Expecto, xUnit, FsUnit |
| Build | Leiningen, tools.deps | dotnet CLI, Paket, FAKE |

---

## Common Pitfalls

1. **Preserving Dynamic Typing Mentality**
   - Clojure: Maps with keyword keys everywhere
   - Pitfall: Using F# Map everywhere instead of records
   - Better: Define record types for domain models; Map for truly dynamic data

2. **Missing Type Annotations**
   - Clojure: No type annotations
   - Pitfall: Relying entirely on type inference in public APIs
   - Better: Annotate function signatures in modules; helps documentation and compile errors

3. **Ignoring Lazy Evaluation Differences**
   - Clojure: Sequences are lazy by default
   - F#: Lists are eager, seqs are lazy
   - Watch for: Side effects in lazy sequences
   - Solution: Use `Seq.cache` or convert to list when side effects matter

4. **Exception-Heavy Code**
   - Clojure: Exceptions for control flow are common
   - Pitfall: Translating all exception handling directly
   - Better: Use Result type for expected errors, exceptions only for truly exceptional cases

5. **Missing Nil vs None Differences**
   - Clojure: `nil` is pervasive and used as false
   - F#: `None` is explicit; `null` exists but discouraged
   - Use `Option.defaultValue`, `Option.defaultWith` to handle None safely

6. **Multimethods vs Pattern Matching**
   - Clojure: `defmulti`/`defmethod` for dynamic dispatch
   - Pitfall: Looking for equivalent runtime dispatch in F#
   - Better: Use discriminated unions with pattern matching; compile-time exhaustiveness checking

7. **Namespace vs Module Confusion**
   - Clojure: Namespaces are runtime entities
   - F#: Modules are compile-time organizational units
   - Be aware: F# requires explicit module/namespace declarations; files don't auto-create them

8. **REPL Workflow Assumptions**
   - Clojure: REPL-first development, hot-reload everything
   - F#: FSI (F# Interactive) exists but compile-first workflow more common
   - Adapt: Use FSI for exploration, but expect to recompile more often

9. **Keyword Keys vs Named Fields**
   - Clojure: Keywords `:key-name` for map keys
   - F#: Named fields in records
   - Watch for: Typos in keywords → Typos in field names caught at compile time

10. **Threading Macro Overuse**
    - Clojure: `->>` and `->` everywhere
    - Pitfall: Trying to pipe everything in F#
    - Better: Use pipe when it improves readability; F# also has composition (`>>`)

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| **dotnet CLI** | Build, run, test, publish | Standard .NET tooling |
| **Paket** | Alternative package manager | Like Leiningen for F# |
| **FAKE** | Build automation | F# DSL for build scripts |
| **FSI** | F# Interactive (REPL) | Similar to Clojure REPL |
| **Fantomas** | Code formatter | Like cljfmt for F# |
| **FSharpLint** | Linter | Static analysis for F# |
| **Ionide** | VS Code extension | F# support with IntelliSense |
| **JetBrains Rider** | IDE | Full F# and .NET support |
| **Expecto** | Testing framework | BDD-style testing |
| **FsCheck** | Property-based testing | Like test.check for F# |

---

## Examples

### Example 1: Simple - Nil Handling to Option Type

**Before (Clojure):**
```clojure
;; User as map
(def users
  [{:name "Alice" :age 30}
   {:name "Bob" :age nil}])

(defn get-age [user]
  (or (:age user) 0))

;; Average age of users with age
(defn average-age [users]
  (let [ages (keep :age users)]
    (if (seq ages)
      (/ (reduce + ages) (count ages))
      0)))

(average-age users) ;; => 30
```

**After (F#):**
```fsharp
// User as record
type User = {
    Name: string
    Age: int option
}

let users = [
    { Name = "Alice"; Age = Some 30 }
    { Name = "Bob"; Age = None }
]

let getAge user =
    user.Age |> Option.defaultValue 0

// Average age of users with age
let averageAge users =
    let ages = users |> List.choose (fun u -> u.Age)
    if List.isEmpty ages then
        0.0
    else
        ages |> List.map float |> List.average

averageAge users  // 30.0
```

### Example 2: Medium - Tagged Maps to Discriminated Union

**Before (Clojure):**
```clojure
;; Constructor functions
(defn credit-card [card-number cvv]
  {:type :credit-card :card-number card-number :cvv cvv})

(defn paypal [email]
  {:type :paypal :email email})

(defn bitcoin [address]
  {:type :bitcoin :address address})

;; Multimethod for polymorphic dispatch
(defmulti process-payment (fn [payment] (:type (:method payment))))

(defmethod process-payment :credit-card [payment]
  (let [{:keys [card-number]} (:method payment)]
    (str "Processing card " card-number)))

(defmethod process-payment :paypal [payment]
  (let [{:keys [email]} (:method payment)]
    (str "Processing PayPal for " email)))

(defmethod process-payment :bitcoin [payment]
  (let [{:keys [address]} (:method payment)]
    (str "Processing Bitcoin to " address)))

;; Usage
(def payment
  {:amount 100.0
   :method (credit-card "1234-5678" "123")})

(process-payment payment)
;; => "Processing card 1234-5678"
```

**After (F#):**
```fsharp
// Discriminated union
type PaymentMethod =
    | CreditCard of cardNumber: string * cvv: string
    | PayPal of email: string
    | Bitcoin of address: string

type Payment = {
    Amount: decimal
    Method: PaymentMethod
}

// Pattern matching for dispatch
let processPayment payment =
    match payment.Method with
    | CreditCard (number, cvv) ->
        $"Processing card {number}"
    | PayPal email ->
        $"Processing PayPal for {email}"
    | Bitcoin address ->
        $"Processing Bitcoin to {address}"

// Usage
let payment = {
    Amount = 100.0m
    Method = CreditCard ("1234-5678", "123")
}

processPayment payment
// "Processing card 1234-5678"
```

### Example 3: Complex - Async Workflow Conversion

**Before (Clojure):**
```clojure
;; Using core.async
(require '[clojure.core.async :as async :refer [go <! >! chan timeout]])

(defn fetch-user [user-id]
  (go
    (<! (timeout 100))
    {:data {:id user-id :name (str "User" user-id)}
     :status-code 200}))

(defn fetch-orders [user-id]
  (go
    (<! (timeout 150))
    {:data [1 2 3]
     :status-code 200}))

(defn get-user-dashboard [user-id]
  (go
    (let [user-response (<! (fetch-user user-id))]
      (if (not= (:status-code user-response) 200)
        {:error "Failed to fetch user"}
        (let [orders-response (<! (fetch-orders user-id))]
          (if (not= (:status-code orders-response) 200)
            {:error "Failed to fetch orders"}
            {:ok {:user (:data user-response)
                  :orders (:data orders-response)
                  :order-count (count (:data orders-response))}}))))))

;; Usage
(let [dashboard-chan (get-user-dashboard 42)
      dashboard (async/<!! dashboard-chan)]
  (if (:ok dashboard)
    (println "Dashboard:" (:ok dashboard))
    (println "Error:" (:error dashboard))))
```

**After (F#):**
```fsharp
// Types
type ApiResponse<'T> = {
    Data: 'T
    StatusCode: int
}

type User = { Id: int; Name: string }
type Dashboard = {
    User: User
    Orders: int list
    OrderCount: int
}

// Async functions
let fetchUser userId = async {
    do! Async.Sleep 100
    return { Data = { Id = userId; Name = $"User{userId}" }; StatusCode = 200 }
}

let fetchOrders userId = async {
    do! Async.Sleep 150
    return { Data = [1; 2; 3]; StatusCode = 200 }
}

// Result-based error handling with async
let getUserDashboard userId = async {
    let! userResponse = fetchUser userId
    if userResponse.StatusCode <> 200 then
        return Error "Failed to fetch user"
    else
        let! ordersResponse = fetchOrders userId
        if ordersResponse.StatusCode <> 200 then
            return Error "Failed to fetch orders"
        else
            return Ok {
                User = userResponse.Data
                Orders = ordersResponse.Data
                OrderCount = List.length ordersResponse.Data
            }
}

// Usage
let dashboard = getUserDashboard 42 |> Async.RunSynchronously
match dashboard with
| Ok data -> printfn $"Dashboard: {data}"
| Error msg -> printfn $"Error: {msg}"
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-typescript-fsharp` - TypeScript → F# (similar static target)
- `lang-clojure-dev` - Clojure development patterns
- `lang-fsharp-dev` - F# development patterns

Cross-cutting pattern skills (for areas not fully covered by lang-*-dev):
- `patterns-concurrency-dev` - Async, channels, actors across languages
- `patterns-serialization-dev` - JSON, validation, type providers across languages
- `patterns-metaprogramming-dev` - Macros, computation expressions, quotations across languages
