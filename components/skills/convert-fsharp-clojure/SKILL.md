---
name: convert-fsharp-clojure
description: Convert F# code to idiomatic Clojure. Use when migrating F# projects to Clojure, translating F# patterns to idiomatic Clojure, or refactoring F# codebases. Extends meta-convert-dev with F#-to-Clojure specific patterns.
---

# Convert F# to Clojure

Convert F# code to idiomatic Clojure. This skill extends `meta-convert-dev` with F#-to-Clojure specific type mappings, idiom translations, and tooling for converting functional code between .NET and JVM platforms.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: F# static types → Clojure dynamic types with optional spec
- **Idiom translations**: F# ML-style patterns → idiomatic Clojure Lisp-style
- **Error handling**: F# Result type → Clojure error conventions
- **Async patterns**: F# async workflows → Clojure core.async or futures
- **Platform translation**: .NET CLR → JVM ecosystem

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- F# language fundamentals - see `lang-fsharp-dev`
- Clojure language fundamentals - see `lang-clojure-dev`
- Reverse conversion (Clojure → F#) - see `convert-clojure-fsharp`

---

## Quick Reference

| F# | Clojure | Notes |
|------------|----------|-------|
| `string` | `String` | Direct mapping (both use JVM/CLR strings) |
| `int` | `Long` | Clojure integers are Java longs by default |
| `float` | `Double` | Clojure floats are Java doubles |
| `bool` | `Boolean` | `true`/`false` in both |
| `list<'T>` | `'(...)` or `[]` | F# list → Clojure vector (usually) |
| `seq<'T>` | lazy seq | F# seq → Clojure lazy sequence |
| `array<'T>` | Java array | Use vectors instead where possible |
| `Map<'K,'V>` | `{...}` | F# Map → Clojure hash-map |
| `Set<'T>` | `#{...}` | F# Set → Clojure hash-set |
| `Option<'T>` | `nil` or value | F# Some/None → Clojure nil or explicit wrapping |
| `Result<'T,'E>` | `{:ok ...}` / `{:error ...}` | Convention-based or library |
| Record type | `defrecord` or map | Depends on polymorphism needs |
| Discriminated union | Tagged map or multimethod | Use `:type` key or dispatch |
| `async { }` | `core.async` or `future` | Async workflow → channel-based or JVM futures |
| `function` | `fn` or `defn` | Lambda/function definition |
| Pipe `\|>` | Thread-last `->>` | Data-last threading |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - plan static → dynamic type strategy
3. **Preserve semantics** over syntax similarity
4. **Adopt Clojure idioms** - don't write "F# code in Clojure syntax"
5. **Handle edge cases** - nullability, error paths, lazy evaluation gotchas
6. **Test equivalence** - same inputs → same outputs
7. **Embrace REPL workflow** - Clojure development is REPL-driven

---

## Type System Mapping

### Primitive Types

| F# | Clojure | Notes |
|------------|----------|-------|
| `bool` | `Boolean` | `true`/`false` (lowercase in Clojure) |
| `byte` | `Byte` | Java byte (8-bit signed) |
| `sbyte` | `Byte` | Maps to Java byte |
| `int16` | `Short` | Java short (16-bit) |
| `uint16` | `Character` / `Integer` | No unsigned in JVM; use wider type |
| `int` / `int32` | `Integer` | Java int (32-bit) |
| `uint32` | `Long` | Use long for unsigned 32-bit range |
| `int64` | `Long` | Default Clojure integer type |
| `uint64` | `BigInteger` | Use arbitrary precision |
| `single` / `float32` | `Float` | Java float (32-bit) |
| `double` / `float` | `Double` | Default Clojure decimal type |
| `decimal` | `BigDecimal` | Arbitrary precision decimal |
| `char` | `Character` | Java char (UTF-16 code unit) |
| `string` | `String` | Immutable strings (both platforms) |
| `bigint` | `BigInteger` | Arbitrary precision integers |
| `unit` | `nil` | F# `()` → Clojure `nil` for side-effect functions |

### Collection Types

| F# | Clojure | Notes |
|------------|----------|-------|
| `list<'T>` | `[...]` vector | Clojure vectors are more common than lists |
| `'T list` | `'(...)` list | Use when prepending is primary operation |
| `array<'T>` | Java array or vector | Prefer vectors; use arrays for interop |
| `seq<'T>` | lazy seq | Both are lazy, composable sequences |
| `ResizeArray<'T>` | `(atom [])` | Mutable ArrayList → atom-wrapped vector |
| `Set<'T>` | `#{...}` | Hash-based set in both |
| `Map<'K,'V>` | `{...}` | Hash-based map in both |
| `'T[]` (array) | Java array | Use `(make-array ...)` or vectors |
| `'T option` | value or `nil` | `Some x` → `x`, `None` → `nil` |
| `'T voption` | value or `nil` | Value option → nil handling |
| `Result<'T,'E>` | `{:ok v}` / `{:error e}` | Convention or library (e.g., cats) |
| `tuple<'A,'B>` | `[a b]` vector | Clojure uses vectors for tuples |

### Composite Types

| F# | Clojure | Notes |
|------------|----------|-------|
| Record type | `defrecord` | When polymorphism/protocols needed |
| Record type | Plain map `{...}` | When just data structure |
| Discriminated union | Tagged map `{:type :variant ...}` | Convention-based tagging |
| Discriminated union | `defmulti`/`defmethod` | For polymorphic dispatch |
| Interface | Protocol | Behavior contracts |
| Abstract class | Protocol | Clojure favors protocols over inheritance |
| Struct | Map | Value type → immutable map |
| Anonymous record | Map | `{| X=1; Y=2 |}` → `{:x 1 :y 2}` |
| Type abbreviation | Type hint or nothing | F# `type UserId = int` → Clojure just uses int with convention |

### Function Types

| F# | Clojure | Notes |
|------------|----------|-------|
| `'a -> 'b` | `(fn [a] b)` | Single-argument function |
| `'a -> 'b -> 'c` | `(fn [a] (fn [b] c))` | Currying → nested functions or multi-arity |
| `unit -> 'a` | `(fn [] a)` | Thunk/nullary function |
| `'a * 'b -> 'c` | `(fn [a b] c)` | Tupled arguments → multiple parameters |
| Generic `'a` | No static types | Use type hints for performance: `^String` |
| Constraint `'a when 'a : IComparable` | Protocol check | Runtime protocol satisfaction |

---

## Idiom Translation

### Pattern 1: Option Type Handling

**F#:**
```fsharp
type User = { Name: string; Email: string option }

let getEmailDomain (user: User) =
    user.Email
    |> Option.map (fun email -> email.Split('@').[1])
    |> Option.defaultValue "no-domain"

// Pattern matching
match user.Email with
| Some email -> printfn "Email: %s" email
| None -> printfn "No email"
```

**Clojure:**
```clojure
;; User as map
(def user {:name "Alice" :email "alice@example.com"})

(defn get-email-domain [user]
  (if-let [email (:email user)]
    (second (clojure.string/split email #"@"))
    "no-domain"))

;; Pattern matching with case or cond
(if-let [email (:email user)]
  (println "Email:" email)
  (println "No email"))

;; Using some-> threading (stops on nil)
(some-> user :email (clojure.string/split #"@") second)
```

**Why this translation:**
- F# `Option.map` → Clojure `some->/some->>` or explicit `if-let`
- F# pattern matching → Clojure `if-let`, `when-let`, or `case`
- F# `None` → Clojure `nil` (idiomatic to use nil for absence)
- Option chaining in F# → threading macros with nil-safety in Clojure

### Pattern 2: Result Type Error Handling

**F#:**
```fsharp
type Result<'T,'E> =
    | Ok of 'T
    | Error of 'E

let divide x y =
    if y = 0 then
        Error "Division by zero"
    else
        Ok (x / y)

let compute a b c =
    divide a b
    |> Result.bind (fun x -> divide x c)
    |> Result.map (fun x -> x * 2)
```

**Clojure:**
```clojure
;; Convention-based error handling
(defn divide [x y]
  (if (zero? y)
    {:error "Division by zero"}
    {:ok (/ x y)}))

(defn ok? [result]
  (contains? result :ok))

(defn bind [result f]
  (if (ok? result)
    (f (:ok result))
    result))

(defn compute [a b c]
  (-> (divide a b)
      (bind #(divide % c))
      (bind #(if (ok? %) {:ok (* (:ok %) 2)} %))))

;; Or using library like cats or manifold
;; Or embrace exceptions for exceptional cases
(defn divide-ex [x y]
  (when (zero? y)
    (throw (ex-info "Division by zero" {:x x :y y})))
  (/ x y))

(defn compute-ex [a b c]
  (try
    (* (/ (/ a b) c) 2)
    (catch Exception e
      {:error (.getMessage e)})))
```

**Why this translation:**
- F# Result type → Clojure conventions (`:ok`/`:error` maps) or libraries
- F# `Result.bind` → Clojure manual bind or monadic libraries (cats)
- F# discriminated union → Clojure maps with type tags
- Alternatively, use exceptions for truly exceptional cases (more idiomatic in Clojure)

### Pattern 3: List Processing with Pipe Operator

**F#:**
```fsharp
let processItems items =
    items
    |> List.filter (fun x -> x.IsActive)
    |> List.map (fun x -> x.Value)
    |> List.sum
```

**Clojure:**
```clojure
(defn process-items [items]
  (->> items
       (filter :is-active)
       (map :value)
       (reduce +)))

;; Or using tranducers for efficiency
(defn process-items-xf [items]
  (transduce
    (comp (filter :is-active)
          (map :value))
    +
    items))
```

**Why this translation:**
- F# pipe `|>` → Clojure thread-last `->>` (data flows as last argument)
- F# `List.filter` → Clojure `filter`
- F# `List.map` → Clojure `map`
- F# `List.sum` → Clojure `(reduce +)` or `(apply +)`
- Tranducers provide composable, efficient transformations (optional optimization)

### Pattern 4: Discriminated Unions to Tagged Maps

**F#:**
```fsharp
type Shape =
    | Circle of radius: float
    | Rectangle of width: float * height: float
    | Triangle of base: float * height: float

let area shape =
    match shape with
    | Circle r -> Math.PI * r * r
    | Rectangle (w, h) -> w * h
    | Triangle (b, h) -> 0.5 * b * h
```

**Clojure:**
```clojure
;; Tagged map approach
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
(area (triangle 6 8))    ;; => 24.0

;; Alternative: protocols for polymorphism
(defprotocol Shape
  (area [this]))

(defrecord Circle [radius]
  Shape
  (area [_] (* Math/PI radius radius)))

(defrecord Rectangle [width height]
  Shape
  (area [_] (* width height)))

(defrecord Triangle [base height]
  Shape
  (area [_] (* 0.5 base height)))
```

**Why this translation:**
- F# discriminated unions → Clojure tagged maps with `:type` key
- F# pattern matching → Clojure `defmulti`/`defmethod` for polymorphic dispatch
- Alternative: protocols + records for OOP-style polymorphism
- Tagged maps are more flexible; protocols are more performant

### Pattern 5: Records and Immutability

**F#:**
```fsharp
type Person = {
    FirstName: string
    LastName: string
    Age: int
}

let person = { FirstName = "Alice"; LastName = "Smith"; Age = 30 }
let olderPerson = { person with Age = 31 }
```

**Clojure:**
```clojure
;; Plain map (most common)
(def person {:first-name "Alice" :last-name "Smith" :age 30})
(def older-person (assoc person :age 31))

;; Or using update
(def older-person (update person :age inc))

;; defrecord when you need type-based dispatch
(defrecord Person [first-name last-name age])

(def person (->Person "Alice" "Smith" 30))
(def older-person (assoc person :age 31))

;; Map constructor
(def person (map->Person {:first-name "Alice" :last-name "Smith" :age 30}))
```

**Why this translation:**
- F# record → Clojure map (most idiomatic) or `defrecord` (when protocols needed)
- F# copy-and-update `{ r with ... }` → Clojure `assoc` or `update`
- Both are immutable by default
- Use plain maps unless you need polymorphism or type-based dispatch

### Pattern 6: Async Workflows

**F#:**
```fsharp
let fetchUser userId = async {
    do! Async.Sleep 100
    return { Id = userId; Name = "User" + string userId }
}

let processUsers userIds = async {
    let! users =
        userIds
        |> List.map fetchUser
        |> Async.Parallel
    return users |> Array.sumBy (fun u -> u.Id)
}
```

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

;; Using Manifold (futures/deferreds)
;; (require '[manifold.deferred :as d])
```

**Why this translation:**
- F# `async { }` → Clojure `future` (simple) or `go` blocks (core.async)
- F# `Async.Parallel` → Clojure `pmap` or multiple futures with `deref`
- F# `do!` → Clojure `<!` in core.async or `@` for futures
- F# `let!` → Clojure `<!` or `deref`
- core.async provides CSP-style channels; futures are simpler for basic parallelism

### Pattern 7: Pattern Matching

**F#:**
```fsharp
let describe value =
    match value with
    | 0 -> "zero"
    | 1 | 2 -> "one or two"
    | n when n < 0 -> "negative"
    | n when n > 100 -> "large"
    | _ -> "other"
```

**Clojure:**
```clojure
(defn describe [value]
  (cond
    (= value 0) "zero"
    (#{1 2} value) "one or two"
    (< value 0) "negative"
    (> value 100) "large"
    :else "other"))

;; Using case for constant matching
(defn describe-simple [value]
  (case value
    0 "zero"
    (1 2) "one or two"
    "other"))

;; Using core.match library for advanced pattern matching
;; (require '[clojure.core.match :refer [match]])
;; (defn describe-match [value]
;;   (match [value]
;;     [0] "zero"
;;     [1] "one or two"
;;     [2] "one or two"
;;     [n] :guard (< n 0) "negative"
;;     [n] :guard (> n 100) "large"
;;     :else "other"))
```

**Why this translation:**
- F# `match` → Clojure `cond` (most flexible), `case` (constants), or core.match library
- F# guards `when` → Clojure conditions in `cond`
- F# `_` (wildcard) → Clojure `:else`
- F# OR patterns `|` → Clojure sets `#{...}` for membership test
- core.match library provides ML-style pattern matching if needed

### Pattern 8: Computation Expressions to Macros

**F#:**
```fsharp
type MaybeBuilder() =
    member _.Bind(x, f) = Option.bind f x
    member _.Return(x) = Some x

let maybe = MaybeBuilder()

let result = maybe {
    let! x = Some 10
    let! y = Some 20
    return x + y
}
```

**Clojure:**
```clojure
;; Using macros to create similar DSL
(defmacro maybe [& body]
  (let [bindings (take-while #(not= % :return) body)
        return-expr (second (drop-while #(not= % :return) body))]
    `(let [~@(mapcat (fn [[sym _ expr]]
                       [sym `(when-let [v# ~expr] v#)])
                     (partition 3 bindings))]
       (when (and ~@(map first (partition 3 bindings)))
         ~return-expr))))

;; Usage (somewhat contrived, not idiomatic Clojure)
;; Idiomatic Clojure would use threading macros instead

;; Better: use existing libraries or threading
(some-> (Some 10)
        (#(when-let [x %]
            (when-let [y (Some 20)]
              (+ x y)))))

;; Most idiomatic: embrace nil handling
(when-let [x 10]
  (when-let [y 20]
    (+ x y)))
```

**Why this translation:**
- F# computation expressions → Clojure macros (for DSL creation)
- F# `let!` → Clojure `when-let` or custom macro bindings
- F# builder pattern → Clojure macro expansion
- Most idiomatic: use threading macros (`some->`, `some->>`) or plain `when-let`
- Clojure favors simpler constructs over heavy DSLs

---

## Paradigm Translation

### Mental Model Shift: Static ML → Dynamic Lisp

| F# Concept | Clojure Approach | Key Insight |
|------------------|-------------------|-------------|
| Static types with inference | Dynamic with optional spec | Types checked at compile time → runtime |
| Type-driven design | Data-driven design | Shape defined by types → shape defined by usage |
| Discriminated unions | Maps with type tags | Compile-time variants → runtime tags |
| Pattern matching | Multimethods or cond | Static exhaustiveness → dynamic dispatch |
| Modules and namespaces | Namespaces | Similar organization, different syntax |
| Type providers | Macros at compile time | Compile-time type generation → compile-time code generation |
| Eager evaluation | Lazy sequences | Evaluate now → evaluate on demand (sequences) |
| ML syntax | S-expressions | Infix notation → prefix notation |

### Concurrency Mental Model

| F# Model | Clojure Model | Conceptual Translation |
|----------------|----------------|------------------------|
| `async { }` | `future` or `go` block | Async workflow → JVM future or CSP channel |
| `Async.Parallel` | `pmap` or multiple futures | Parallel execution → parallel map or future coordination |
| `Async.RunSynchronously` | `@future` or `deref` | Block for result → dereference future |
| MailboxProcessor | Agent or core.async channel | Message-passing actor → agent or channel |
| Task (TPL) | CompletableFuture | .NET Task → JVM CompletableFuture |
| Cancellation tokens | Interrupt or promise | Explicit cancellation → thread interrupt or promise patterns |

---

## Error Handling

### F# Error Model → Clojure Error Model

F# uses Result types and exceptions. Clojure uses exceptions as primary mechanism, with conventions for error data.

**F# Result Pattern:**
```fsharp
type Result<'T,'E> =
    | Ok of 'T
    | Error of 'E

let parseAge input =
    match System.Int32.TryParse(input) with
    | (true, age) when age >= 0 -> Ok age
    | (true, _) -> Error "Age cannot be negative"
    | (false, _) -> Error "Invalid number"
```

**Clojure Exception Pattern (Idiomatic):**
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

**Error Propagation:**

| F# | Clojure | Notes |
|------------|----------|-------|
| `Result.bind` | Manual `if` or library | Chain error-returning functions |
| `Result.map` | Map over `:ok` value | Transform success value |
| Pattern matching | `if` / `case` / `cond` | Handle Ok/Error branches |
| Exception propagation | `try`/`catch` | Clojure embraces exceptions |
| Railway-oriented programming | Function composition with error handling | Less common in Clojure |

**Clojure ex-info Pattern:**
```clojure
;; Create rich exception with data
(throw (ex-info "User not found" {:user-id 123}))

;; Catch and extract data
(try
  (risky-operation)
  (catch clojure.lang.ExceptionInfo e
    (let [data (ex-data e)]
      (log/error "Failed:" (.getMessage e) "Data:" data))))
```

---

## Concurrency Patterns

### F# Async → Clojure Async

**Simple async operation:**

```fsharp
// F#
let fetchData url = async {
    use client = new HttpClient()
    let! response = client.GetStringAsync(url) |> Async.AwaitTask
    return response
}
```

```clojure
;; Clojure with future
(defn fetch-data [url]
  (future
    (slurp url)))

;; Clojure with core.async
(require '[clojure.core.async :as async :refer [go <!]])
(require '[clj-http.client :as http])

(defn fetch-data-async [url]
  (go
    (:body (http/get url))))
```

**Parallel execution:**

```fsharp
// F#
let fetchAll urls = async {
    let! results =
        urls
        |> List.map fetchData
        |> Async.Parallel
    return results
}
```

```clojure
;; Clojure with pmap (parallel map)
(defn fetch-all [urls]
  (pmap fetch-data urls))

;; Clojure with futures
(defn fetch-all-futures [urls]
  (let [futures (map #(future (fetch-data %)) urls)]
    (map deref futures)))

;; Clojure with core.async
(defn fetch-all-async [urls]
  (let [channels (map fetch-data-async urls)]
    (async/go
      (loop [results [] chs channels]
        (if (empty? chs)
          results
          (recur (conj results (async/<! (first chs)))
                 (rest chs)))))))
```

**MailboxProcessor → Agent:**

```fsharp
// F#
type Message =
    | Increment
    | GetValue of AsyncReplyChannel<int>

let counter = MailboxProcessor.Start(fun inbox ->
    let rec loop state = async {
        let! msg = inbox.Receive()
        match msg with
        | Increment ->
            return! loop (state + 1)
        | GetValue reply ->
            reply.Reply state
            return! loop state
    }
    loop 0)
```

```clojure
;; Clojure with agent
(def counter (agent 0))

(defn increment! []
  (send counter inc))

(defn get-value []
  @counter)

;; Or with core.async for more complex state machines
(require '[clojure.core.async :as async :refer [go chan <! >!]])

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

---

## Memory & Platform Translation

### .NET CLR → JVM

Both F# and Clojure run on managed runtimes with garbage collection, but there are platform differences:

| Aspect | F# (.NET) | Clojure (JVM) | Translation |
|--------|-----------|---------------|-------------|
| Memory model | CLR GC | JVM GC | Both are GC'd; no ownership concerns |
| Value types | Structs (stack) | Primitives (stack/box) | Use primitives where possible |
| Reference types | Classes (heap) | Objects (heap) | Direct mapping |
| Nullability | Can be null (except value types) | Can be nil | Similar null handling needed |
| Generics | CLR generics | JVM generics (type erasure) | Type erasure at runtime in JVM |
| Primitive types | .NET types (Int32, etc.) | Java types (Integer, etc.) | Different class names, similar semantics |

**No explicit memory management needed in either language.** Focus on:
- Avoiding excessive allocations
- Using transients for performance-critical mutable updates
- Leveraging persistent data structures (both languages)

**Platform Library Mapping:**

| Category | F# (.NET) | Clojure (JVM) |
|----------|-----------|---------------|
| HTTP | HttpClient | clj-http, http-kit |
| JSON | System.Text.Json | cheshire, jsonista, data.json |
| Date/Time | System.DateTime | java.time, clj-time |
| Regex | System.Text.RegularExpressions | java.util.regex via #"..." |
| Collections | System.Collections | clojure.core collections |
| Async | async/Task | future, core.async, manifold |
| Testing | Expecto, xUnit | clojure.test, Midje |
| Build | dotnet, Paket | Leiningen, tools.deps |

---

## Common Pitfalls

1. **Transliterating Types Instead of Embracing Maps**
   - F# records → Clojure records everywhere
   - Better: Use plain maps unless polymorphism needed
   - Clojure is data-oriented; maps are the primary abstraction

2. **Overusing Result-Style Error Handling**
   - F# Result type everywhere
   - Clojure idiom: Use exceptions for exceptional cases
   - Use `{:ok/:error}` conventions sparingly (validation, boundaries)

3. **Ignoring Lazy Evaluation**
   - F# sequences are lazy, but Clojure sequences are VERY lazy
   - Watch for `map`/`filter` chains that don't realize
   - Force realization with `doall`/`dorun` when side effects needed

4. **Fighting Dynamic Typing**
   - Trying to encode all F# type information
   - Embrace runtime flexibility; use spec for validation
   - Trust the REPL for fast feedback

5. **Missing nil/null Differences**
   - F# `None` is explicit; Clojure `nil` is pervasive
   - Clojure collections can contain nil
   - Use `nil?`, `some?`, `when-let` for nil-safe operations

6. **Currying vs. Multi-Arity**
   - F# auto-curries: `let add x y = x + y` is `'a -> 'b -> 'c`
   - Clojure uses multi-arity: `(defn add ([x] ...) ([x y] ...))`
   - Don't manually curry in Clojure; use `partial` when needed

7. **Computation Expressions vs. Macros**
   - F# computation expressions are common for DSLs
   - Clojure macros are powerful but used more sparingly
   - Prefer higher-order functions and data over macros

8. **Namespaces vs. Modules**
   - F# modules are compile-time only
   - Clojure namespaces are runtime entities
   - Be aware of namespace reloading in REPL (requires careful state management)

9. **Keyword vs. String Keys in Maps**
   - Using strings for map keys (like F# record field names)
   - Clojure idiom: Use keywords (`:key-name`) for map keys
   - Keywords are interned, faster to compare, and are functions

10. **Ignoring REPL Workflow**
    - Writing whole programs before testing
    - Clojure development is REPL-first: write function, test in REPL, iterate
    - Use `comment` blocks for REPL experiments in source files

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| **Leiningen** | Build tool | Popular, convention-based (like npm) |
| **tools.deps** | Dependency management | Official Clojure CLI tools |
| **CIDER** | Emacs REPL | Most powerful REPL integration |
| **Cursive** | IntelliJ plugin | Full IDE experience |
| **Calva** | VS Code plugin | Good REPL support |
| **clj-kondo** | Linter | Static analysis for Clojure |
| **eastwood** | Linter | Additional static checks |
| **clojure.spec** | Runtime specs | Validation and generative testing |
| **test.check** | Property-based testing | Like FsCheck for F# |
| **core.async** | CSP channels | Async programming library |
| **manifold** | Futures/streams | Alternative async library |

---

## Examples

### Example 1: Simple - Option Type to Nil Handling

**Before (F#):**
```fsharp
type User = { Name: string; Age: int option }

let getAge user =
    match user.Age with
    | Some age -> age
    | None -> 0

let users = [
    { Name = "Alice"; Age = Some 30 }
    { Name = "Bob"; Age = None }
]

let averageAge =
    users
    |> List.choose (fun u -> u.Age)
    |> List.average
```

**After (Clojure):**
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

### Example 2: Medium - Discriminated Union to Multimethod

**Before (F#):**
```fsharp
type PaymentMethod =
    | CreditCard of cardNumber: string * cvv: string
    | PayPal of email: string
    | Bitcoin of address: string

type Payment = {
    Amount: decimal
    Method: PaymentMethod
}

let processPayment payment =
    match payment.Method with
    | CreditCard (number, cvv) ->
        sprintf "Processing card %s" number
    | PayPal email ->
        sprintf "Processing PayPal for %s" email
    | Bitcoin address ->
        sprintf "Processing Bitcoin to %s" address

let payment = {
    Amount = 100.0m
    Method = CreditCard ("1234-5678", "123")
}
```

**After (Clojure):**
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

### Example 3: Complex - Async Workflow to core.async

**Before (F#):**
```fsharp
type ApiResponse<'T> = {
    Data: 'T
    StatusCode: int
}

let fetchUser userId = async {
    do! Async.Sleep 100
    return { Data = {| Id = userId; Name = "User" + string userId |}; StatusCode = 200 }
}

let fetchOrders userId = async {
    do! Async.Sleep 150
    return { Data = [1; 2; 3]; StatusCode = 200 }
}

let getUserDashboard userId = async {
    let! userResponse = fetchUser userId
    if userResponse.StatusCode <> 200 then
        return Error "Failed to fetch user"
    else
        let! ordersResponse = fetchOrders userId
        if ordersResponse.StatusCode <> 200 then
            return Error "Failed to fetch orders"
        else
            return Ok {|
                User = userResponse.Data
                Orders = ordersResponse.Data
                OrderCount = List.length ordersResponse.Data
            |}
}

// Run async
let dashboard = getUserDashboard 42 |> Async.RunSynchronously
match dashboard with
| Ok data -> printfn "Dashboard: %A" data
| Error msg -> printfn "Error: %s" msg
```

**After (Clojure):**
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
      dashboard (<!! dashboard-chan)]
  (if (:ok dashboard)
    (println "Dashboard:" (:ok dashboard))
    (println "Error:" (:error dashboard))))

;; Alternative: Using futures (simpler for basic cases)
(defn fetch-user-future [user-id]
  (future
    (Thread/sleep 100)
    {:data {:id user-id :name (str "User" user-id)}
     :status-code 200}))

(defn fetch-orders-future [user-id]
  (future
    (Thread/sleep 150)
    {:data [1 2 3]
     :status-code 200}))

(defn get-user-dashboard-future [user-id]
  (let [user-response @(fetch-user-future user-id)]
    (if (not= (:status-code user-response) 200)
      {:error "Failed to fetch user"}
      (let [orders-response @(fetch-orders-future user-id)]
        (if (not= (:status-code orders-response) 200)
          {:error "Failed to fetch orders"}
          {:ok {:user (:data user-response)
                :orders (:data orders-response)
                :order-count (count (:data orders-response))}})))))
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-typescript-clojure` - TypeScript → Clojure (similar dynamic target)
- `convert-elm-clojure` - Elm → Clojure (similar functional source)
- `lang-fsharp-dev` - F# development patterns
- `lang-clojure-dev` - Clojure development patterns

Cross-cutting pattern skills (for areas not fully covered by lang-*-dev):
- `patterns-concurrency-dev` - Async, channels, threads across languages
- `patterns-serialization-dev` - JSON, validation, struct tags across languages
