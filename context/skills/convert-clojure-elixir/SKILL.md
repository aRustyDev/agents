---
name: convert-clojure-elixir
description: Convert Clojure code to idiomatic Elixir. Use when migrating Clojure/JVM applications to Elixir/BEAM, translating functional Lisp patterns to Elixir, or refactoring immutable data processing to leverage Elixir's actor model and OTP. Extends meta-convert-dev with Clojure-to-Elixir specific patterns.
---

# Convert Clojure to Elixir

Convert Clojure code to idiomatic Elixir. This skill extends `meta-convert-dev` with Clojure-to-Elixir specific type mappings, idiom translations, and tooling for translating between these two functional languages across different runtimes (JVM → BEAM).

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Clojure types → Elixir types across runtimes
- **Idiom translations**: Lisp patterns → idiomatic Elixir
- **Concurrency models**: JVM threads/atoms → BEAM processes/GenServers
- **Data structures**: Persistent collections → Elixir's immutable structures
- **Metaprogramming**: Clojure macros → Elixir macros
- **Build tools**: Leiningen/deps.edn → Mix project structure
- **REPL workflow**: Clojure REPL → IEx patterns

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Clojure language fundamentals - see `lang-clojure-dev`
- Elixir language fundamentals - see `lang-elixir-dev`
- Reverse conversion (Elixir → Clojure) - see `convert-elixir-clojure`
- ClojureScript specifics - see `convert-clojurescript-*` skills

---

## Quick Reference

| Clojure | Elixir | Notes |
|---------|--------|-------|
| `nil` | `nil` | Same concept, different runtime |
| `true` / `false` | `true` / `false` | Booleans as atoms |
| `:keyword` | `:atom` | Keywords → atoms |
| `"string"` | `"string"` | Both UTF-8, Elixir on binaries |
| `[1 2 3]` | `[1, 2, 3]` | Vectors → lists (different impl) |
| `{:a 1 :b 2}` | `%{a: 1, b: 2}` | Maps syntax differs |
| `(defn f [x] x)` | `def f(x), do: x` | Function definition |
| `(fn [x] x)` | `fn x -> x end` | Anonymous functions |
| `->` | `\|>` | Threading/piping |
| `atom` | GenServer/Agent | State management |
| `agent` | Agent/GenServer | Async state |
| `(ns my.ns)` | `defmodule My.Ns` | Namespaces → modules |

---

## When Converting Code

1. **Analyze source thoroughly** - Understand Clojure's JVM dependencies and state model
2. **Map types first** - Create type equivalence table, note platform differences
3. **Preserve semantics** - Functional purity translates well, state management differs
4. **Rethink concurrency** - Atoms/refs/agents → processes/GenServers/Agents
5. **Modernize for BEAM** - Embrace OTP patterns for fault tolerance
6. **Adopt Elixir idioms** - Pattern matching, with statements, pipe operator
7. **Test equivalence** - Same inputs → same outputs, verify supervision if stateful

---

## Type System Mapping

### Primitive Types

| Clojure | Elixir | Notes |
|---------|--------|-------|
| `nil` | `nil` | Null/absence indicator |
| `true` / `false` | `true` / `false` | Booleans (atoms) |
| `Long` / `42` | `integer` | Arbitrary precision in both |
| `Double` / `3.14` | `float` | 64-bit double precision |
| `BigDecimal` | `Decimal` (library) | Use `decimal` package |
| `:keyword` | `:atom` | Keywords map to atoms |
| `Symbol` | Atom or String | Context-dependent |
| `"string"` | `"string"` | UTF-8 strings (binary in Elixir) |
| `Character` | Integer codepoint | Elixir: `?a` = 97 |
| `Ratio` (1/3) | Float or `Ratio` lib | Elixir: `1/3` is float division |

### Collection Types

| Clojure | Elixir | Notes |
|---------|--------|-------|
| `[1 2 3]` (vector) | `[1, 2, 3]` (list) | Clojure: O(1) index; Elixir: O(n) list |
| `'(1 2 3)` (list) | `[1, 2, 3]` | Both linked lists |
| `{:a 1 :b 2}` (map) | `%{a: 1, b: 2}` | Similar hash maps |
| `#{1 2 3}` (set) | `MapSet.new([1, 2, 3])` | Set implementations |
| `(list 1 2 3)` | `[1, 2, 3]` | Linked lists |
| `(vector 1 2 3)` | `Tuple` or `List` | Context: indexed → tuple, seq → list |
| Persistent queue | `:queue` module | Use Erlang's queue |
| LazySeq | `Stream` | Lazy evaluation |

### Composite Types

| Clojure | Elixir | Notes |
|---------|--------|-------|
| `(defrecord User [name age])` | `defstruct [:name, :age]` | Records → Structs |
| `(deftype X [...])` | `defstruct` or custom protocol | Type definitions |
| `(defprotocol P ...)` | `defprotocol` | Protocol-based polymorphism |
| `(reify P ...)` | Struct with protocol impl | Anonymous implementation |
| Metadata `^{:key val}` | Module attributes `@key val` | Compile-time metadata |
| Tagged literal `#inst` | Custom sigil `~D[...]` | Reader macros → sigils |

---

## Paradigm Translation

### Mental Model Shift: Clojure/JVM → Elixir/BEAM

| Clojure Concept | Elixir Approach | Key Insight |
|-----------------|-----------------|-------------|
| Persistent data structures | Immutable data by default | Both immutable, Elixir uses structural sharing |
| Atoms (thread-safe ref) | GenServer or Agent | Shared state → process with message passing |
| Refs (coordinated) | GenServer with transactions | STM → explicit serialization via GenServer |
| Agents (async) | Agent (similar!) | Very similar async state model |
| Futures | Task.async/await | Async computation patterns |
| core.async channels | GenStage or Broadway | Backpressure-aware streaming |
| Vars (dynamic binding) | Process dictionary (avoid) | Use explicit passing or Application env |
| Multimethods | Protocols | Polymorphism via protocols |
| Macros | Macros | Both have powerful macro systems |

### Concurrency Mental Model

| Clojure Model | Elixir Model | Conceptual Translation |
|---------------|--------------|------------------------|
| Atom (swap!) | Agent.update/GenServer.call | Synchronous state mutation → process message |
| Ref (dosync) | GenServer with transaction fn | Coordinated refs → single process serializes |
| Agent (send) | Agent.cast | Async state update → nearly 1:1 |
| Future (future ...) | Task.async | One-off async computation |
| core.async go blocks | spawn/GenServer | CSP channels → actor model |
| Thread pool | Supervisor + workers | OTP supervision for fault tolerance |

---

## Idiom Translation

### Pattern: Namespace to Module

**Clojure:**
```clojure
(ns myapp.core
  "Application core namespace."
  (:require [clojure.string :as str]
            [clojure.set :as set]
            [myapp.util :refer [helper]]))

(defn greet [name]
  (str "Hello, " name "!"))

(defn- private-fn []
  "Private function")
```

**Elixir:**
```elixir
defmodule Myapp.Core do
  @moduledoc """
  Application core module.
  """

  alias String, as: Str
  alias MapSet, as: Set
  import Myapp.Util, only: [helper: 1]

  @doc "Greets a person"
  @spec greet(String.t()) :: String.t()
  def greet(name) do
    "Hello, #{name}!"
  end

  defp private_fn do
    "Private function"
  end
end
```

**Why this translation:**
- `ns` → `defmodule` with CamelCase
- `:require` → `alias` for module aliases
- `:refer` → `import` for specific functions
- `defn` → `def`, `defn-` → `defp`
- String interpolation: `(str ...)` → `"#{...}"`
- `@moduledoc` and `@doc` for documentation
- `@spec` for type specifications

---

### Pattern: Function Definition and Multi-Arity

**Clojure:**
```clojure
;; Multi-arity function
(defn greet
  ([] (greet "World"))
  ([name] (str "Hello, " name "!"))
  ([greeting name] (str greeting ", " name "!")))

;; Variadic function
(defn sum [& numbers]
  (reduce + 0 numbers))

;; Pre/post conditions
(defn divide [numerator denominator]
  {:pre [(not= denominator 0)]
   :post [(number? %)]}
  (/ numerator denominator))
```

**Elixir:**
```elixir
# Multi-arity with default arguments
def greet(name \\ "World")
def greet(name), do: "Hello, #{name}!"

# Or separate clauses for different behavior
def greet(), do: greet("World")
def greet(name) when is_binary(name), do: "Hello, #{name}!"
def greet(greeting, name), do: "#{greeting}, #{name}!"

# Variadic (rest parameters)
def sum(numbers) when is_list(numbers) do
  Enum.reduce(numbers, 0, &+/2)
end

# Guards replace pre-conditions
def divide(numerator, denominator) when denominator != 0 do
  numerator / denominator
end
def divide(_numerator, 0), do: {:error, :division_by_zero}
```

**Why this translation:**
- Multi-arity: Elixir uses default arguments `\\` or separate clauses
- Variadic: Elixir requires explicit list, no `& rest` syntax
- Pre-conditions: Use guards (`when`)
- Post-conditions: Use explicit pattern matching on return
- Return tagged tuples `{:ok, val}` or `{:error, reason}` for safety

---

### Pattern: Threading Macros

**Clojure:**
```clojure
;; Thread-first
(-> 5
    (+ 3)
    (* 2)
    (- 1))
;; => 15

;; Thread-last
(->> [1 2 3 4 5]
     (map inc)
     (filter even?)
     (reduce +))
;; => 12

;; as-> for flexible positioning
(as-> 0 $
  (inc $)
  (+ 3 $)
  (* 2 $))
;; => 8
```

**Elixir:**
```elixir
# Pipe operator (thread-first style)
5
|> Kernel.+(3)
|> Kernel.*(2)
|> Kernel.-(1)
# => 15

# More idiomatic with functions
[1, 2, 3, 4, 5]
|> Enum.map(&(&1 + 1))
|> Enum.filter(&rem(&1, 2) == 0)
|> Enum.reduce(0, &+/2)
# => 12

# Elixir pipe always threads as first argument
# For flexibility, use intermediate variables
value = 0
value = value + 1
value = 3 + value
value = value * 2
# => 8
```

**Why this translation:**
- `->` → `|>` (pipe operator)
- Elixir pipe threads as **first argument only**
- `->>` (thread-last) has no direct equivalent; use intermediate bindings
- `as->` flexibility requires explicit variable assignment
- Embrace Elixir's Enum/Stream modules over manual threading

---

### Pattern: Destructuring

**Clojure:**
```clojure
;; Vector destructuring
(let [[a b c] [1 2 3]]
  (+ a b c))

;; Map destructuring
(let [{:keys [name age]} {:name "Alice" :age 30}]
  (str name " is " age))

;; With defaults
(let [{:keys [name age] :or {age 0}} {:name "Bob"}]
  age)

;; Nested destructuring
(let [{{city :city} :address} {:address {:city "NYC"}}]
  city)

;; Function arguments
(defn greet-person [{:keys [name age]}]
  (str "Hello " name ", you are " age))
```

**Elixir:**
```elixir
# List destructuring
[a, b, c] = [1, 2, 3]
a + b + c

# Map destructuring
%{name: name, age: age} = %{name: "Alice", age: 30}
"#{name} is #{age}"

# With defaults (via pattern matching)
def get_age(%{age: age}), do: age
def get_age(_), do: 0

# Nested destructuring
%{address: %{city: city}} = %{address: %{city: "NYC"}}
city

# Function arguments
def greet_person(%{name: name, age: age}) do
  "Hello #{name}, you are #{age}"
end

# With head/tail
[head | tail] = [1, 2, 3]
# head = 1, tail = [2, 3]
```

**Why this translation:**
- Both support pattern matching destructuring
- Clojure `:keys` → Elixir explicit `key: var` or same name `%{name: name}`
- Defaults: Clojure `:or` → Elixir multiple function clauses
- Similar nested destructuring syntax
- Elixir has `[head | tail]` for list cons pattern

---

### Pattern: Sequence Operations

**Clojure:**
```clojure
;; map, filter, reduce
(->> data
     (map parse-record)
     (filter valid?)
     (map transform)
     (reduce (fn [acc item] (merge acc item)) {}))

;; List comprehension
(for [x (range 10)
      :when (even? x)
      :let [y (* x x)]]
  [x y])

;; Lazy sequences
(def naturals (iterate inc 0))
(take 5 naturals)
;; => (0 1 2 3 4)
```

**Elixir:**
```elixir
# map, filter, reduce with Enum
data
|> Enum.map(&parse_record/1)
|> Enum.filter(&valid?/1)
|> Enum.map(&transform/1)
|> Enum.reduce(%{}, fn item, acc -> Map.merge(acc, item) end)

# List comprehension
for x <- 0..9, rem(x, 2) == 0 do
  y = x * x
  {x, y}
end

# Lazy sequences with Stream
naturals = Stream.iterate(0, &(&1 + 1))
Enum.take(naturals, 5)
# => [0, 1, 2, 3, 4]
```

**Why this translation:**
- `->>` → `|>` with `Enum` module
- Clojure lazy by default; Elixir use `Stream` for laziness
- List comprehension: `for` in Clojure → `for` in Elixir (similar!)
- `:when` → guard in comprehension
- `:let` → inline binding in comprehension body
- `iterate` → `Stream.iterate`

---

### Pattern: Atoms and State Management

**Clojure:**
```clojure
;; Atom (synchronous state)
(def counter (atom 0))

@counter  ; Read
(swap! counter inc)  ; Update
(reset! counter 0)   ; Set
(compare-and-set! counter 0 10)  ; CAS

;; Agent (asynchronous state)
(def logger (agent []))
(send logger conj "log entry")
(await logger)

;; Ref (coordinated state)
(def account-a (ref 100))
(def account-b (ref 200))

(dosync
  (alter account-a - 50)
  (alter account-b + 50))
```

**Elixir:**
```elixir
# Agent (async state - similar to Clojure Agent!)
{:ok, counter} = Agent.start_link(fn -> 0 end)

Agent.get(counter, & &1)           # Read
Agent.update(counter, &(&1 + 1))   # Update
Agent.update(counter, fn _ -> 0 end)  # Reset

# GenServer (for more complex state, like Clojure Atom with transactions)
defmodule Counter do
  use GenServer

  def start_link(initial), do: GenServer.start_link(__MODULE__, initial, name: __MODULE__)
  def get, do: GenServer.call(__MODULE__, :get)
  def increment, do: GenServer.call(__MODULE__, :increment)

  @impl true
  def init(initial), do: {:ok, initial}

  @impl true
  def handle_call(:get, _from, state), do: {:reply, state, state}
  def handle_call(:increment, _from, state), do: {:reply, state + 1, state + 1}
end

# Coordinated state (dosync) → GenServer with batched operations
defmodule Bank do
  use GenServer

  def transfer(from, to, amount) do
    GenServer.call(__MODULE__, {:transfer, from, to, amount})
  end

  @impl true
  def handle_call({:transfer, from, to, amount}, _from, accounts) do
    accounts = accounts
    |> Map.update!(from, &(&1 - amount))
    |> Map.update!(to, &(&1 + amount))
    {:reply, :ok, accounts}
  end
end
```

**Why this translation:**
- Clojure Atom → Elixir Agent (very similar for simple async state)
- Clojure Atom (with swap!) → Elixir GenServer.call (for synchronous)
- Clojure Agent → Elixir Agent (nearly 1:1 mapping!)
- Clojure Ref + dosync → GenServer (serialize transactions in single process)
- BEAM processes provide isolation and fault tolerance beyond JVM atoms

---

### Pattern: Error Handling

**Clojure:**
```clojure
;; try/catch
(try
  (/ 1 0)
  (catch ArithmeticException e
    (println "Error:" (.getMessage e))
    nil)
  (finally
    (println "Cleanup")))

;; With ex-info
(try
  (when (invalid? data)
    (throw (ex-info "Invalid data"
                    {:data data :reason :validation})))
  (process data)
  (catch clojure.lang.ExceptionInfo e
    (let [{:keys [data reason]} (ex-data e)]
      (log/error "Failed:" reason))))
```

**Elixir:**
```elixir
# try/rescue/after
try do
  1 / 0
rescue
  e in ArithmeticError ->
    IO.puts("Error: #{Exception.message(e)}")
    nil
after
  IO.puts("Cleanup")
end

# Preferred: Tagged tuples with case/with
def divide(a, b) when b != 0, do: {:ok, a / b}
def divide(_, 0), do: {:error, :division_by_zero}

case divide(10, 0) do
  {:ok, result} -> result
  {:error, reason} -> handle_error(reason)
end

# with statement for chaining
def process_user(params) do
  with {:ok, validated} <- validate(params),
       {:ok, user} <- create_user(validated),
       {:ok, _email} <- send_welcome(user) do
    {:ok, user}
  else
    {:error, reason} -> {:error, reason}
  end
end

# Custom exceptions
defmodule ValidationError do
  defexception [:message, :data, :reason]
end

raise ValidationError, message: "Invalid", data: data, reason: :validation
```

**Why this translation:**
- `try/catch` → `try/rescue` (similar syntax)
- Elixir prefers **tagged tuples** `{:ok, val}` / `{:error, reason}` over exceptions
- `ex-info` → custom exception with `defexception`
- `with` statement chains operations that return tagged tuples
- Pattern match on error tuples rather than catch

---

## Concurrency Patterns

### Clojure Concurrency → Elixir Concurrency

| Pattern | Clojure | Elixir |
|---------|---------|--------|
| Async task | `(future ...)` | `Task.async` |
| Thread pool | `pmap` | `Task.async_stream` |
| Channels | `core.async` channels | GenStage/Broadway |
| Shared state | Atom | Agent or GenServer |
| Transaction | Refs + dosync | GenServer with state fn |
| Fire and forget | Agent send | Agent.cast or GenServer.cast |

### Example: Parallel Processing

**Clojure:**
```clojure
;; Using futures
(let [results (doall (map #(future (process-item %)) items))]
  (map deref results))

;; Using pmap (parallel map)
(pmap process-item items)

;; core.async
(require '[clojure.core.async :as a])

(let [c (a/chan)]
  (a/go
    (while true
      (let [item (a/<! c)]
        (process item))))
  (a/>!! c item))
```

**Elixir:**
```elixir
# Using Task.async
results = items
|> Enum.map(&Task.async(fn -> process_item(&1) end))
|> Enum.map(&Task.await/1)

# Using Task.async_stream (parallel map)
items
|> Task.async_stream(&process_item/1, max_concurrency: 10)
|> Enum.map(fn {:ok, result} -> result end)

# Using GenServer for stateful processing
defmodule Processor do
  use GenServer

  def start_link(_), do: GenServer.start_link(__MODULE__, [], name: __MODULE__)

  def process_item(item) do
    GenServer.cast(__MODULE__, {:process, item})
  end

  @impl true
  def init([]), do: {:ok, []}

  @impl true
  def handle_cast({:process, item}, state) do
    result = process(item)
    {:noreply, [result | state]}
  end
end
```

**Why this translation:**
- `future` → `Task.async` for one-off async work
- `pmap` → `Task.async_stream` for parallel mapping
- core.async → GenStage for backpressure-aware pipelines
- BEAM's lightweight processes enable massive concurrency

---

## Metaprogramming

### Macros: Clojure → Elixir

**Clojure:**
```clojure
;; Simple macro
(defmacro unless [condition & body]
  `(if (not ~condition)
     (do ~@body)))

(unless false
  (println "This runs")
  "result")

;; Macro with gensym
(defmacro with-logging [& body]
  `(let [start# (System/currentTimeMillis)]
     (let [result# (do ~@body)]
       (println "Took" (- (System/currentTimeMillis) start#) "ms")
       result#)))
```

**Elixir:**
```elixir
# Macros
defmacro unless(condition, do: block) do
  quote do
    if !unquote(condition) do
      unquote(block)
    end
  end
end

unless false do
  IO.puts("This runs")
  "result"
end

# Macro with unique variable (hygiene)
defmacro with_logging(do: block) do
  quote do
    start = System.monotonic_time(:millisecond)
    result = unquote(block)
    IO.puts("Took #{System.monotonic_time(:millisecond) - start} ms")
    result
  end
end
```

**Why this translation:**
- Syntax quote: `` ` `` → `quote do`
- Unquote: `~` → `unquote()`
- Splice: `~@` → `unquote()` in list context
- Auto-gensym: `name#` → automatic hygiene in Elixir
- Elixir macros use AST (abstract syntax tree) manipulation

---

## Build and Dependencies

### Leiningen → Mix

**Clojure (project.clj):**
```clojure
(defproject myapp "0.1.0"
  :description "My Clojure app"
  :dependencies [[org.clojure/clojure "1.11.1"]
                 [cheshire "5.12.0"]
                 [ring/ring-core "1.10.0"]]
  :main myapp.core
  :profiles {:dev {:dependencies [[midje "1.10.9"]]}})
```

**Elixir (mix.exs):**
```elixir
defmodule Myapp.MixProject do
  use Mix.Project

  def project do
    [
      app: :myapp,
      version: "0.1.0",
      elixir: "~> 1.14",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {Myapp.Application, []}
    ]
  end

  defp deps do
    [
      {:jason, "~> 1.4"},         # Cheshire equivalent
      {:plug_cowboy, "~> 2.6"},   # Ring equivalent
      {:midje, "~> 1.10", only: :test}
    ]
  end
end
```

### Common Commands

| Task | Clojure | Elixir |
|------|---------|--------|
| Create project | `lein new app myapp` | `mix new myapp` |
| Dependencies | `lein deps` | `mix deps.get` |
| REPL | `lein repl` | `iex -S mix` |
| Run | `lein run` | `mix run` |
| Test | `lein test` | `mix test` |
| Build JAR | `lein uberjar` | `mix release` |

---

## Testing

### clojure.test → ExUnit

**Clojure:**
```clojure
(ns myapp.core-test
  (:require [clojure.test :refer [deftest testing is are]]
            [myapp.core :as core]))

(deftest add-test
  (is (= 4 (core/add 2 2)))
  (is (= 0 (core/add -1 1))))

(deftest arithmetic-test
  (are [x y expected] (= expected (core/add x y))
    1 1 2
    2 3 5
    -1 1 0))
```

**Elixir:**
```elixir
defmodule Myapp.CoreTest do
  use ExUnit.Case

  test "add/2 adds two numbers" do
    assert Myapp.Core.add(2, 2) == 4
    assert Myapp.Core.add(-1, 1) == 0
  end

  # Table-driven test (similar to are)
  test "arithmetic operations" do
    assert Myapp.Core.add(1, 1) == 2
    assert Myapp.Core.add(2, 3) == 5
    assert Myapp.Core.add(-1, 1) == 0
  end
end
```

**Why this translation:**
- `deftest` → `test`
- `is` → `assert`
- `are` → multiple assertions in test (no direct macro)
- ExUnit has powerful async testing: `use ExUnit.Case, async: true`
- Doctests: `@doc` examples become tests

---

## Common Pitfalls

1. **Vector vs List Performance**
   - Clojure vectors: O(1) indexed access
   - Elixir lists: O(n) indexed access
   - **Fix:** Use tuples for small indexed collections, maps for key access

2. **Keyword vs Atom Semantics**
   - Clojure keywords are functions: `(:name user)`
   - Elixir atoms are not callable: `user[:name]` or `user.name`
   - **Fix:** Use map access syntax, not function application

3. **Lazy by Default vs Eager**
   - Clojure sequences lazy by default
   - Elixir Enum eager, Stream lazy
   - **Fix:** Explicitly use `Stream` for lazy operations

4. **Shared State Model**
   - Clojure: atoms/refs for shared state (thread-safe)
   - Elixir: processes for state (isolated)
   - **Fix:** Rethink state as processes, not shared memory

5. **Nil Punning**
   - Clojure: `nil` and `false` are falsy
   - Elixir: only `false` and `nil` are falsy (same!)
   - **Fix:** Actually works similarly, but be explicit in guards

6. **Java Interop Loss**
   - Clojure can call any Java library
   - Elixir runs on BEAM, not JVM
   - **Fix:** Find Elixir/Erlang equivalents or use ports/NIFs

7. **Dynamic Vars**
   - Clojure: dynamic binding with `^:dynamic` and `binding`
   - Elixir: no dynamic binding; use process dictionary (discouraged) or explicit passing
   - **Fix:** Pass context explicitly or use Application environment

8. **Metadata**
   - Clojure: extensive metadata on symbols `^{:key val}`
   - Elixir: module attributes `@key val` (compile-time only)
   - **Fix:** Use module attributes or store in data structures

---

## Limitations

This skill focuses on core language translation. For complete migration, also consider:

- **Java library dependencies**: Must find Elixir/Erlang equivalents
- **JVM-specific features**: Reflection, classloaders, Java interop
- **ClojureScript**: Separate consideration for JavaScript target
- **Runtime differences**: JVM GC vs BEAM preemptive scheduling

---

## Tooling

| Tool | Purpose | Notes |
|------|---------|-------|
| Mix | Build tool, deps, tasks | Replaces Leiningen |
| IEx | Interactive shell (REPL) | Replaces Clojure REPL |
| ExUnit | Testing framework | Replaces clojure.test |
| Dialyzer | Static type checker | Optional, uses typespecs |
| Credo | Code linting | Quality checks |
| ExDoc | Documentation generator | Generates HTML docs from `@doc` |

---

## Examples

### Example 1: Simple - Data Transformation

**Before (Clojure):**
```clojure
(defn process-users [users]
  (->> users
       (filter :active)
       (map #(select-keys % [:id :name :email]))
       (map #(update % :name clojure.string/upper-case))))
```

**After (Elixir):**
```elixir
def process_users(users) do
  users
  |> Enum.filter(& &1.active)
  |> Enum.map(&Map.take(&1, [:id, :name, :email]))
  |> Enum.map(&update_in(&1, [:name], fn n -> String.upcase(n) end))
end
```

### Example 2: Medium - Stateful Counter

**Before (Clojure):**
```clojure
(def counter (atom 0))

(defn increment []
  (swap! counter inc))

(defn get-count []
  @counter)

(defn reset-count []
  (reset! counter 0))
```

**After (Elixir):**
```elixir
defmodule Counter do
  use Agent

  def start_link(initial_value) do
    Agent.start_link(fn -> initial_value end, name: __MODULE__)
  end

  def increment do
    Agent.update(__MODULE__, &(&1 + 1))
  end

  def get_count do
    Agent.get(__MODULE__, & &1)
  end

  def reset_count do
    Agent.update(__MODULE__, fn _ -> 0 end)
  end
end
```

### Example 3: Complex - Concurrent Pipeline

**Before (Clojure):**
```clojure
(require '[clojure.core.async :as a])

(defn process-pipeline [items]
  (let [input (a/chan 100)
        output (a/chan 100)]
    ;; Stage 1: Parse
    (a/go-loop []
      (when-let [item (a/<! input)]
        (let [parsed (parse-item item)]
          (a/>! output parsed))
        (recur)))

    ;; Stage 2: Validate
    (a/go-loop []
      (when-let [item (a/<! output)]
        (when (valid? item)
          (process item))
        (recur)))

    ;; Feed items
    (doseq [item items]
      (a/>!! input item))

    (a/close! input)))
```

**After (Elixir):**
```elixir
defmodule Pipeline do
  def process_pipeline(items) do
    items
    |> Task.async_stream(&parse_item/1, max_concurrency: 10)
    |> Stream.filter(fn {:ok, item} -> valid?(item) end)
    |> Stream.map(fn {:ok, item} -> item end)
    |> Task.async_stream(&process/1, max_concurrency: 10)
    |> Stream.run()
  end

  defp parse_item(item), do: # ... parsing logic
  defp valid?(item), do: # ... validation logic
  defp process(item), do: # ... processing logic
end

# Or using GenStage for more control
defmodule Pipeline.Producer do
  use GenStage

  def start_link(items) do
    GenStage.start_link(__MODULE__, items)
  end

  def init(items) do
    {:producer, items}
  end

  def handle_demand(demand, items) when demand > 0 do
    {to_send, remaining} = Enum.split(items, demand)
    {:noreply, to_send, remaining}
  end
end

defmodule Pipeline.Consumer do
  use GenStage

  def start_link() do
    GenStage.start_link(__MODULE__, :ok)
  end

  def init(:ok) do
    {:consumer, :ok}
  end

  def handle_events(items, _from, state) do
    items
    |> Enum.map(&parse_item/1)
    |> Enum.filter(&valid?/1)
    |> Enum.each(&process/1)
    {:noreply, [], state}
  end
end
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `lang-clojure-dev` - Clojure development patterns
- `lang-elixir-dev` - Elixir development patterns
- `convert-erlang-elixir` - Similar BEAM target conversion
- `patterns-concurrency-dev` - Async, processes, actors across languages
- `patterns-serialization-dev` - JSON, validation across languages
- `patterns-metaprogramming-dev` - Macros across languages
