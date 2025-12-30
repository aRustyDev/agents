---
name: convert-elixir-clojure
description: Convert Elixir code to idiomatic Clojure. Use when migrating Elixir/Phoenix applications to Clojure, translating GenServer actors to component/mount patterns, or refactoring BEAM concurrency to JVM STM/core.async. Extends meta-convert-dev with Elixir-to-Clojure specific patterns.
---

# Convert Elixir to Clojure

Convert Elixir code to idiomatic Clojure. This skill extends `meta-convert-dev` with Elixir-to-Clojure specific type mappings, idiom translations, and tooling for translating between BEAM VM and JVM runtimes.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Elixir types → Clojure types (dynamic → dynamic)
- **Idiom translations**: Elixir patterns → idiomatic Clojure
- **Runtime transition**: BEAM VM (actors) → JVM (STM/core.async)
- **Concurrency models**: GenServer/Supervisor → component/mount, core.async
- **OTP patterns**: Supervision trees → Stuart Sierra's component
- **Data structures**: Elixir maps/structs → Clojure maps/records
- **Build tools**: Mix → Leiningen/deps.edn

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Elixir language fundamentals - see `lang-elixir-dev`
- Clojure language fundamentals - see `lang-clojure-dev`
- Reverse conversion (Clojure → Elixir) - see `convert-clojure-elixir`
- Phoenix framework specifics - see web framework conversion skills

---

## Quick Reference

| Elixir | Clojure | Notes |
|--------|---------|-------|
| `:atom` | `:keyword` | Both use keyword syntax |
| `{:ok, value}` | `{:ok value}` | Vectors instead of tuples |
| `%{key: value}` | `{:key value}` | Maps similar, different syntax |
| `[1, 2, 3]` | `[1 2 3]` | Vectors (no commas in Clojure) |
| `defmodule Module` | `(ns module)` | Namespace definition |
| `def name, do: value` | `(def name value)` | Variable binding |
| `defp private` | `(defn- private)` | Private functions |
| `fn x -> x end` | `(fn [x] x)` | Anonymous functions |
| `\|>` (pipe) | `(-> x f g)` | Thread-first macro |
| `GenServer` | `component` / `core.async` | State management |
| `Supervisor` | `component` | Lifecycle management |
| `Task.async` | `future` / `core.async` | Async execution |

---

## 8 Pillars Validation

### Elixir Coverage

| Pillar | Coverage | Status |
|--------|----------|--------|
| Module System | ✓ | Full coverage in lang-elixir-dev |
| Error Handling | ✓ | {:ok/:error} tuples, pattern matching |
| Concurrency Model | ✓ | Processes, GenServer, Supervisor |
| Metaprogramming | ✓ | Macros, use directive |
| Zero/Default Values | ✓ | nil, pattern matching |
| Serialization | ✓ | Phoenix params, JSON, Ecto |
| Build/Deps | ✓ | Mix, hex.pm |
| Testing Idioms | ✓ | ExUnit |

**Score: 8/8 (Green)**

### Clojure Coverage

| Pillar | Coverage | Status |
|--------|----------|--------|
| Module System | ✓ | Full coverage in lang-clojure-dev |
| Error Handling | ✓ | try/catch, ex-info |
| Concurrency Model | ✓ | Atoms, refs, agents, core.async |
| Metaprogramming | ✓ | Macros, syntax-quote |
| Zero/Default Values | ✓ | nil, or, defaults |
| Serialization | ✓ | EDN, JSON, spec |
| Build/Deps | ✓ | Leiningen, deps.edn |
| Testing Idioms | ✓ | clojure.test, test.check, Midje |

**Score: 8/8 (Green)**

**Validation Status:** ✅ Both languages have comprehensive coverage. Conversion can proceed with confidence.

---

## Type System Mapping

### Primitive Types

| Elixir | Clojure | Notes |
|--------|---------|-------|
| `:atom` | `:keyword` | Keywords work identically |
| `integer` | `integer` | Arbitrary precision in both |
| `float` | `double` | 64-bit floating point |
| `true` / `false` | `true` / `false` | Boolean values identical |
| `nil` | `nil` | Nil represents absence |
| `"string"` | `"string"` | Strings are immutable sequences |
| `'charlist'` | `[\c \h \a \r]` | Character lists less common in Clojure |

### Collection Types

| Elixir | Clojure | Notes |
|--------|---------|-------|
| `[1, 2, 3]` | `[1 2 3]` | Lists → Vectors |
| `{:ok, value}` | `[:ok value]` | Tuples → Vectors |
| `%{a: 1, b: 2}` | `{:a 1 :b 2}` | Maps similar, syntax differs |
| `%{"a" => 1}` | `{"a" 1}` | String keys work in both |
| `MapSet.new([1, 2])` | `#{1 2}` | Sets |
| Keyword list | Keyword list | `[{:a 1} {:b 2}]` similar |

### Composite Types

| Elixir | Clojure | Notes |
|--------|---------|-------|
| `defstruct [:name, :age]` | `(defrecord User [name age])` | Structs → Records or Maps |
| `%User{name: "Alice"}` | `(->User "Alice" nil)` | Record constructor |
| `@type user :: %{name: String.t()}` | `^:user {:name String}` | Type specs → spec |
| `@spec func(integer) :: String.t()` | `^{:args [Integer] :ret String}` | Function specs |

---

## Idiom Translation

### Pattern: Module Definition

**Elixir:**
```elixir
defmodule MyApp.Users do
  @moduledoc """
  Handles user-related operations.
  """

  alias MyApp.Repo
  import Ecto.Query

  @type user :: %{id: integer, name: String.t()}

  @spec get_user(integer) :: {:ok, user} | {:error, :not_found}
  def get_user(id) do
    case Repo.get(User, id) do
      nil -> {:error, :not_found}
      user -> {:ok, user}
    end
  end

  defp build_query(filters) do
    from u in User, where: ^filters
  end
end
```

**Clojure:**
```clojure
(ns myapp.users
  "Handles user-related operations."
  (:require [myapp.db :as db]
            [clojure.spec.alpha :as s]))

(s/def ::id int?)
(s/def ::name string?)
(s/def ::user (s/keys :req-un [::id ::name]))

(defn get-user
  "Retrieves user by ID. Returns {:ok user} or {:error :not-found}."
  [id]
  (if-let [user (db/find-by-id :users id)]
    {:ok user}
    {:error :not-found}))

(defn- build-query [filters]
  (merge {:table :users} filters))
```

**Why this translation:**
- `defmodule` → `(ns ...)` namespace declaration
- `@moduledoc` → namespace docstring
- `@type` and `@spec` → `clojure.spec` definitions
- CamelCase modules → kebab-case namespaces
- Pattern matching on nil → `if-let` for nil safety

---

### Pattern: Pattern Matching to Destructuring

**Elixir:**
```elixir
def process_response({:ok, %{"data" => data, "meta" => meta}}) do
  {:success, data, meta}
end

def process_response({:error, reason}) do
  {:failure, reason}
end

def handle_user(%User{name: name, age: age}) when age >= 18 do
  "Adult: #{name}"
end
```

**Clojure:**
```clojure
(defn process-response
  [{status :status data :data meta :meta :as response}]
  (case status
    :ok [:success data meta]
    :error [:failure (:reason response)]))

;; Or with multimethods
(defmulti process-response first)

(defmethod process-response :ok
  [[_ {:keys [data meta]}]]
  [:success data meta])

(defmethod process-response :error
  [[_ reason]]
  [:failure reason])

(defn handle-user
  [{:keys [name age] :as user}]
  (when (>= age 18)
    (str "Adult: " name)))
```

**Why this translation:**
- Multiple function clauses → `case`, multimethods, or separate functions
- Guards → conditional logic in function body
- Struct pattern matching → map destructuring with `:keys`
- Tag tuples → vectors with first element as tag

---

### Pattern: Pipelines

**Elixir:**
```elixir
def process_data(input) do
  input
  |> String.trim()
  |> String.downcase()
  |> String.split(",")
  |> Enum.map(&String.trim/1)
  |> Enum.reject(&(&1 == ""))
  |> Enum.join(";")
end
```

**Clojure:**
```clojure
(defn process-data [input]
  (->> input
       str/trim
       str/lower-case
       (#(str/split % #","))
       (map str/trim)
       (remove empty?)
       (str/join ";")))

;; Or with thread-first for better readability
(defn process-data [input]
  (-> input
      str/trim
      str/lower-case
      (str/split #",")
      (->> (map str/trim)
           (remove empty?)
           (str/join ";"))))
```

**Why this translation:**
- `|>` (thread-first) → `->` or `->>` depending on position
- Enum functions → `map`, `filter`, `remove`, sequence functions
- Capture operator `&func/arity` → direct function reference
- Mix `->` and `->>` with transition at collection operations

---

### Pattern: GenServer to Component

**Elixir:**
```elixir
defmodule UserCache do
  use GenServer

  # Client API

  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def get(key) do
    GenServer.call(__MODULE__, {:get, key})
  end

  def put(key, value) do
    GenServer.cast(__MODULE__, {:put, key, value})
  end

  # Server Callbacks

  @impl true
  def init(_opts) do
    {:ok, %{}}
  end

  @impl true
  def handle_call({:get, key}, _from, state) do
    {:reply, Map.get(state, key), state}
  end

  @impl true
  def handle_cast({:put, key, value}, state) do
    {:noreply, Map.put(state, key, value)}
  end
end
```

**Clojure (using Stuart Sierra's component):**
```clojure
(ns myapp.user-cache
  (:require [com.stuartsierra.component :as component]))

(defrecord UserCache [cache]
  component/Lifecycle

  (start [this]
    (assoc this :cache (atom {})))

  (stop [this]
    (assoc this :cache nil)))

;; Public API

(defn get-user [cache key]
  (get @(:cache cache) key))

(defn put-user [cache key value]
  (swap! (:cache cache) assoc key value))

;; System construction
(defn user-cache-system []
  (component/system-map
    :cache (map->UserCache {})))
```

**Clojure (using core.async):**
```clojure
(ns myapp.user-cache
  (:require [clojure.core.async :as async :refer [go go-loop <! >!]]))

(defn start-cache []
  (let [state (atom {})
        request-ch (async/chan)
        response-ch (async/chan)]

    (go-loop []
      (when-let [[cmd reply-ch] (<! request-ch)]
        (case (first cmd)
          :get (>! reply-ch (get @state (second cmd)))
          :put (do (swap! state assoc (second cmd) (nth cmd 2))
                   (>! reply-ch :ok)))
        (recur)))

    {:request-ch request-ch}))

(defn get-user [cache key]
  (let [reply-ch (async/chan)]
    (async/>!! (:request-ch cache) [:get key reply-ch])
    (async/<!! reply-ch)))

(defn put-user [cache key value]
  (let [reply-ch (async/chan)]
    (async/>!! (:request-ch cache) [:put key value reply-ch])
    (async/<!! reply-ch)))
```

**Why this translation:**
- GenServer state → atom (synchronous) or core.async (asynchronous)
- `handle_call` → synchronous function or async channel handler
- `handle_cast` → async update via `swap!` or channel message
- Supervision → component lifecycle management
- Process mailbox → core.async channels

---

### Pattern: Supervisor to Component System

**Elixir:**
```elixir
defmodule MyApp.Application do
  use Application

  @impl true
  def start(_type, _args) do
    children = [
      {UserCache, []},
      {SessionStore, []},
      {MyApp.Repo, []},
      MyAppWeb.Endpoint
    ]

    opts = [strategy: :one_for_one, name: MyApp.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
```

**Clojure:**
```clojure
(ns myapp.system
  (:require [com.stuartsierra.component :as component]
            [myapp.user-cache :as cache]
            [myapp.session-store :as session]
            [myapp.db :as db]))

(defn create-system []
  (component/system-map
    :db (db/new-database "jdbc:postgresql://localhost/myapp")
    :cache (component/using
             (cache/new-cache)
             [:db])
    :session (component/using
               (session/new-store)
               [:db :cache])))

(defn start-system []
  (component/start (create-system)))

(defn stop-system [system]
  (component/stop system))

;; In production
(defonce system (atom nil))

(defn init []
  (reset! system (start-system)))

(defn shutdown []
  (swap! system #(when % (component/stop %))))
```

**Why this translation:**
- Supervisor children → component system-map
- Restart strategies → component lifecycle hooks
- Dependency injection → `component/using`
- OTP supervision → explicit start/stop coordination
- Named registration → namespace-level state atom

---

## Error Handling

### Elixir Error Model → Clojure Error Model

**Elixir uses tagged tuples for expected errors:**
```elixir
def divide(a, b) when b != 0, do: {:ok, a / b}
def divide(_, 0), do: {:error, :division_by_zero}

def fetch_user(id) do
  with {:ok, data} <- Http.get("/users/#{id}"),
       {:ok, user} <- parse_user(data) do
    {:ok, user}
  else
    {:error, reason} -> {:error, reason}
  end
end
```

**Clojure equivalent:**
```clojure
(defn divide [a b]
  (if (zero? b)
    [:error :division-by-zero]
    [:ok (/ a b)]))

;; Using ex-info for errors
(defn divide-ex [a b]
  (if (zero? b)
    (throw (ex-info "Division by zero" {:a a :b b}))
    (/ a b)))

;; Monadic error handling
(defn fetch-user [id]
  (try
    (let [data (http/get (str "/users/" id))
          user (parse-user data)]
      [:ok user])
    (catch Exception e
      [:error (.getMessage e)])))

;; Or using cats library for Either monad
(require '[cats.monad.either :as either])

(defn fetch-user [id]
  (either/>>= (http-get id)
              parse-user))
```

### Pattern: with Statement → Monadic Composition

**Elixir:**
```elixir
def create_user(params) do
  with {:ok, validated} <- validate_params(params),
       {:ok, user} <- insert_user(validated),
       {:ok, email} <- send_welcome_email(user) do
    {:ok, user}
  else
    {:error, reason} -> {:error, reason}
  end
end
```

**Clojure:**
```clojure
;; Using if-let chain
(defn create-user [params]
  (if-let [validated (validate-params params)]
    (if-let [user (insert-user validated)]
      (if-let [email (send-welcome-email user)]
        [:ok user]
        [:error :email-failed])
      [:error :insert-failed])
    [:error :validation-failed]))

;; Using some-> threading
(defn create-user [params]
  (some-> params
          validate-params
          insert-user
          (#(send-welcome-email %))
          (vector :ok)))

;; Using cats Either monad (most similar to 'with')
(require '[cats.monad.either :as either])

(defn create-user [params]
  (either/>>= (validate-params params)
              insert-user
              send-welcome-email))
```

---

## Concurrency Patterns

### Elixir Processes → Clojure Concurrency

**Elixir:**
```elixir
# Spawn process
pid = spawn(fn ->
  receive do
    {:hello, caller} -> send(caller, {:ok, "Hello back!"})
  end
end)

send(pid, {:hello, self()})

receive do
  {:ok, message} -> IO.puts(message)
after
  1000 -> IO.puts("Timeout!")
end

# Task async
task = Task.async(fn -> expensive_computation() end)
result = Task.await(task, 5000)

# Parallel processing
results = [1, 2, 3, 4]
|> Enum.map(&Task.async(fn -> process(&1) end))
|> Enum.map(&Task.await/1)
```

**Clojure:**
```clojure
;; Using future (thread pool)
(def result
  (future (expensive-computation)))

@result  ;; Dereference to get value (blocks)
(deref result 5000 :timeout)  ;; With timeout

;; Using core.async (CSP style)
(require '[clojure.core.async :as async :refer [go go-loop <! >! chan]])

(let [c (chan)]
  (go
    (let [msg (<! c)]
      (when (= (first msg) :hello)
        (>! (second msg) [:ok "Hello back!"]))))

  (let [reply-ch (chan)]
    (>!! c [:hello reply-ch])
    (async/alt!!
      reply-ch ([msg] (println msg))
      (async/timeout 1000) (println "Timeout!"))))

;; Parallel processing with pmap
(def results
  (pmap process [1 2 3 4]))

;; Or with futures
(def results
  (->> [1 2 3 4]
       (map #(future (process %)))
       (map deref)))

;; Or with core.async
(defn parallel-process [items]
  (let [out-ch (chan (count items))]
    (doseq [item items]
      (go (>! out-ch (process item))))
    (async/<!! (async/into [] (async/take (count items) out-ch)))))
```

### Task.async → future / core.async

| Elixir | Clojure | Use Case |
|--------|---------|----------|
| `Task.async/await` | `future` / `deref` | Simple async with threads |
| `Task.async_stream` | `pmap` | Parallel mapping |
| `spawn_link` | `core.async/go` | Lightweight concurrency |
| GenServer | `atom` + functions | Synchronous state |
| GenServer | `core.async` channels | Asynchronous state |
| Agent | `agent` | Asynchronous updates |

### Supervision → Lifecycle Management

**Elixir:**
```elixir
defmodule Worker do
  use GenServer

  def start_link(arg) do
    GenServer.start_link(__MODULE__, arg)
  end

  def init(arg) do
    # Initialize resources
    {:ok, arg}
  end

  def terminate(reason, state) do
    # Cleanup
    :ok
  end
end

# Supervised
children = [{Worker, initial_state}]
Supervisor.start_link(children, strategy: :one_for_one)
```

**Clojure:**
```clojure
(ns myapp.worker
  (:require [com.stuartsierra.component :as component]))

(defrecord Worker [state resource]
  component/Lifecycle

  (start [this]
    (let [resource (initialize-resource (:state this))]
      (assoc this :resource resource)))

  (stop [this]
    (when-let [resource (:resource this)]
      (cleanup-resource resource))
    (assoc this :resource nil)))

;; Component system
(defn worker-system [initial-state]
  (component/system-map
    :worker (map->Worker {:state initial-state})))

;; Start/stop
(def system (component/start (worker-system {})))
(component/stop system)
```

---

## Memory & Ownership

Both Elixir and Clojure use garbage collection, so memory management is similar:

### Immutability Translation

**Elixir:**
```elixir
# All data is immutable
user = %{name: "Alice", age: 30}
updated = %{user | age: 31}  # Creates new map

# For performance, use structural sharing
big_map = Map.new(1..1000, &{&1, &1})
updated = Map.put(big_map, :new, :value)  # Shares structure
```

**Clojure:**
```clojure
;; All data is immutable with persistent data structures
(def user {:name "Alice" :age 30})
(def updated (assoc user :age 31))  ;; Creates new map with sharing

;; Structural sharing is automatic
(def big-map (into {} (map #(vector % %) (range 1000))))
(def updated (assoc big-map :new :value))  ;; Shares structure
```

Both languages optimize immutability through structural sharing, so translation is straightforward.

---

## Common Pitfalls

### 1. Process-Based State → Functional State

**Pitfall:** Assuming process isolation exists in JVM

```elixir
# Elixir: Each process has isolated state
GenServer.start_link(Counter, 0, name: :counter1)
GenServer.start_link(Counter, 0, name: :counter2)
# Two independent counters
```

```clojure
;; Clojure: State is shared unless explicitly isolated
(def counter1 (atom 0))  ; Independent
(def counter2 (atom 0))  ; Independent

;; Or use component for isolation
(def system
  (component/system-map
    :counter1 (->Counter (atom 0))
    :counter2 (->Counter (atom 0))))
```

**Fix:** Use atoms, refs, or component records for isolated state.

---

### 2. Pattern Matching Everywhere → Selective Destructuring

**Pitfall:** Over-relying on pattern matching syntax

```elixir
# Elixir: Pattern matching in function heads
def process({:ok, %User{name: name, age: age}}) when age >= 18 do
  "Adult: #{name}"
end
def process({:error, reason}), do: "Error: #{reason}"
```

```clojure
;; Clojure: Use destructuring + conditionals
(defn process [result]
  (let [[status value] result]
    (case status
      :ok (let [{:keys [name age]} value]
            (when (>= age 18)
              (str "Adult: " name)))
      :error (str "Error: " value))))

;; Or multimethod for dispatch
(defmulti process first)
(defmethod process :ok [[_ {:keys [name age]}]]
  (when (>= age 18)
    (str "Adult: " name)))
(defmethod process :error [[_ reason]]
  (str "Error: " reason))
```

---

### 3. Assuming Lightweight Processes

**Pitfall:** Creating thousands of "processes" expecting BEAM-like performance

```elixir
# Elixir: 1 million processes is normal
Enum.map(1..1_000_000, fn i ->
  spawn(fn -> process(i) end)
end)
```

```clojure
;; Clojure: JVM threads are heavy, use alternatives
;; BAD:
(doall (map #(future (process %)) (range 1000000)))  ;; Out of memory!

;; GOOD: Use core.async for lightweight concurrency
(require '[clojure.core.async :as async])

(doseq [i (range 1000000)]
  (async/go (process i)))  ;; Go blocks are lightweight

;; Or batch processing
(->> (range 1000000)
     (partition-all 1000)
     (pmap #(mapv process %))
     (apply concat))
```

---

### 4. Tuple Syntax Differences

**Pitfall:** Mixing up tuple/vector syntax

```elixir
# Elixir: Tuples use curly braces
{:ok, result}
{:error, :not_found}
```

```clojure
;; Clojure: Use vectors for tuples
[:ok result]
[:error :not-found]

;; Maps use curly braces
{:status :ok :result result}
```

---

### 5. Module/Namespace Differences

**Pitfall:** Direct translation of module names

```elixir
# Elixir: MyApp.Users.Create
defmodule MyApp.Users.Create do
  # ...
end
```

```clojure
;; Clojure: Use kebab-case and dots
(ns myapp.users.create)

;; NOT: (ns MyApp.Users.Create)  ;; This won't work
```

---

## Tooling

| Tool | Elixir | Clojure | Notes |
|------|--------|---------|-------|
| **Build Tool** | Mix | Leiningen / CLI | deps.edn for modern approach |
| **Package Manager** | Hex | Clojars / Maven | JVM ecosystem broader |
| **REPL** | IEx | nREPL / CIDER | Both excellent for dev |
| **Testing** | ExUnit | clojure.test | Similar features |
| **Property Testing** | StreamData | test.check | Same approach |
| **Code Formatter** | `mix format` | `cljfmt` | Automatic formatting |
| **Linter** | Credo | Eastwood / clj-kondo | Static analysis |
| **Docs** | ExDoc | Codox | Generated docs |

### Migration Workflow

```bash
# 1. Setup Clojure project
lein new app myapp
# or
clj -Tnew app :name myapp/myapp

# 2. Add dependencies
# Edit project.clj or deps.edn

# 3. Port module by module
# Start with data structures, then logic, then OTP

# 4. Replace GenServers
# Choose: component, core.async, or atoms

# 5. Update tests
# ExUnit → clojure.test

# 6. Integration testing
# Ensure behavior matches original
```

---

## Examples

### Example 1: Simple - Data Transformation

**Before (Elixir):**
```elixir
defmodule DataTransformer do
  def transform(data) do
    data
    |> Enum.map(&process_item/1)
    |> Enum.filter(&valid?/1)
    |> Enum.group_by(&(&1.category))
  end

  defp process_item(%{value: v} = item) do
    %{item | value: v * 2}
  end

  defp valid?(%{value: v}), do: v > 0
end
```

**After (Clojure):**
```clojure
(ns data-transformer)

(defn- process-item [item]
  (update item :value * 2))

(defn- valid? [item]
  (> (:value item) 0))

(defn transform [data]
  (->> data
       (map process-item)
       (filter valid?)
       (group-by :category)))
```

---

### Example 2: Medium - GenServer State Management

**Before (Elixir):**
```elixir
defmodule RateLimiter do
  use GenServer

  def start_link(opts) do
    limit = Keyword.get(opts, :limit, 100)
    GenServer.start_link(__MODULE__, limit, name: __MODULE__)
  end

  def check_rate(key) do
    GenServer.call(__MODULE__, {:check, key})
  end

  @impl true
  def init(limit) do
    {:ok, %{limit: limit, counts: %{}}}
  end

  @impl true
  def handle_call({:check, key}, _from, state) do
    count = Map.get(state.counts, key, 0)
    if count < state.limit do
      new_counts = Map.put(state.counts, key, count + 1)
      {:reply, :ok, %{state | counts: new_counts}}
    else
      {:reply, {:error, :rate_limited}, state}
    end
  end
end
```

**After (Clojure):**
```clojure
(ns rate-limiter
  (:require [com.stuartsierra.component :as component]))

(defrecord RateLimiter [limit counts-atom]
  component/Lifecycle

  (start [this]
    (assoc this :counts-atom (atom {})))

  (stop [this]
    (assoc this :counts-atom nil)))

(defn check-rate [limiter key]
  (let [counts @(:counts-atom limiter)
        count (get counts key 0)
        limit (:limit limiter)]
    (if (< count limit)
      (do
        (swap! (:counts-atom limiter) update key (fnil inc 0))
        :ok)
      [:error :rate-limited])))

(defn new-rate-limiter
  ([] (new-rate-limiter 100))
  ([limit]
   (map->RateLimiter {:limit limit})))

;; Usage
(def limiter (component/start (new-rate-limiter 100)))
(check-rate limiter "user-123")
```

---

### Example 3: Complex - Supervised Worker Pool

**Before (Elixir):**
```elixir
defmodule WorkerPool.Supervisor do
  use Supervisor

  def start_link(opts) do
    Supervisor.start_link(__MODULE__, opts, name: __MODULE__)
  end

  @impl true
  def init(opts) do
    pool_size = Keyword.get(opts, :size, 10)

    children = for i <- 1..pool_size do
      Supervisor.child_spec(
        {Worker, id: i},
        id: {Worker, i}
      )
    end

    Supervisor.init(children, strategy: :one_for_one)
  end
end

defmodule Worker do
  use GenServer

  def start_link(opts) do
    id = Keyword.fetch!(opts, :id)
    GenServer.start_link(__MODULE__, id, name: via_tuple(id))
  end

  def process(id, job) do
    GenServer.call(via_tuple(id), {:process, job})
  end

  @impl true
  def init(id) do
    {:ok, %{id: id, jobs_processed: 0}}
  end

  @impl true
  def handle_call({:process, job}, _from, state) do
    result = perform_work(job)
    {:reply, result, %{state | jobs_processed: state.jobs_processed + 1}}
  end

  defp via_tuple(id), do: {:via, Registry, {WorkerRegistry, id}}
  defp perform_work(job), do: {:ok, job}
end
```

**After (Clojure):**
```clojure
(ns worker-pool
  (:require [com.stuartsierra.component :as component]
            [clojure.core.async :as async :refer [go-loop <! >!]]))

(defrecord Worker [id state job-ch]
  component/Lifecycle

  (start [this]
    (let [state-atom (atom {:id id :jobs-processed 0})
          job-ch (async/chan)]

      ;; Start worker loop
      (go-loop []
        (when-let [[job reply-ch] (<! job-ch)]
          (let [result (perform-work job)]
            (swap! state-atom update :jobs-processed inc)
            (>! reply-ch result))
          (recur)))

      (assoc this :state state-atom :job-ch job-ch)))

  (stop [this]
    (when-let [ch (:job-ch this)]
      (async/close! ch))
    (assoc this :state nil :job-ch nil)))

(defn perform-work [job]
  [:ok job])

(defn process-job [worker job]
  (let [reply-ch (async/chan)
        job-ch (:job-ch worker)]
    (async/>!! job-ch [job reply-ch])
    (async/<!! reply-ch)))

(defrecord WorkerPool [size workers]
  component/Lifecycle

  (start [this]
    (let [workers (into {}
                        (for [i (range size)]
                          [i (component/start (map->Worker {:id i}))]))]
      (assoc this :workers workers)))

  (stop [this]
    (doseq [[_ worker] (:workers this)]
      (component/stop worker))
    (assoc this :workers nil)))

(defn get-worker [pool id]
  (get-in pool [:workers (mod id (:size pool))]))

(defn process-with-pool [pool job-id job]
  (let [worker (get-worker pool job-id)]
    (process-job worker job)))

;; System construction
(defn worker-pool-system
  ([] (worker-pool-system 10))
  ([size]
   (component/system-map
     :pool (map->WorkerPool {:size size}))))

;; Usage
(def system (component/start (worker-pool-system 10)))
(process-with-pool (:pool system) 123 {:data "work"})
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-erlang-elixir` - Related BEAM conversion (reverse direction)
- `convert-python-clojure` - Dynamic to dynamic conversion patterns
- `lang-elixir-dev` - Elixir development patterns
- `lang-clojure-dev` - Clojure development patterns

Cross-cutting pattern skills (for areas not fully covered by lang-*-dev):
- `patterns-concurrency-dev` - Processes, actors, STM, core.async patterns
- `patterns-serialization-dev` - JSON, EDN, validation across languages
- `patterns-metaprogramming-dev` - Macros and compile-time code generation

---

## References

- [Elixir Documentation](https://elixir-lang.org/)
- [Clojure Documentation](https://clojure.org/)
- [Stuart Sierra's Component](https://github.com/stuartsierra/component)
- [core.async Guide](https://clojure.org/guides/core_async)
- [From Erlang to Clojure](https://blog.josephwilk.net/clojure/from-erlang-to-clojure.html)
