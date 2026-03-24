---
name: convert-python-clojure
description: Convert Python code to idiomatic Clojure. Use when migrating Python projects to Clojure, translating Python patterns to idiomatic Clojure, or refactoring Python codebases to leverage functional programming. Extends meta-convert-dev with Python-to-Clojure specific patterns.
---

# Convert Python to Clojure

Convert Python code to idiomatic Clojure. This skill extends `meta-convert-dev` with Python-to-Clojure specific type mappings, idiom translations, and tooling for transforming imperative, object-oriented Python code into functional, immutable Clojure.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Python types → Clojure types (dynamic → dynamic with immutability)
- **Idiom translations**: Python patterns → idiomatic Clojure (OOP → functional)
- **Error handling**: Exceptions → explicit error values
- **Async patterns**: asyncio → core.async
- **Data structures**: Mutable collections → immutable persistent collections
- **REPL workflow**: Script-based → REPL-driven development

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Python language fundamentals - see `lang-python-dev`
- Clojure language fundamentals - see `lang-clojure-dev`
- Reverse conversion (Clojure → Python) - see `convert-clojure-python`
- ClojureScript - see `convert-python-clojurescript`

---

## Quick Reference

| Python | Clojure | Notes |
|--------|---------|-------|
| `int` | `int` / `long` / `BigInt` | Clojure has arbitrary precision |
| `float` | `double` | 64-bit floating point |
| `bool` | `true` / `false` | Direct mapping |
| `str` | `String` | Java strings (immutable) |
| `bytes` | `byte-array` | Mutable byte array |
| `list[T]` | `[...]` | Vector (indexed, immutable) |
| `tuple` | `[...]` or `(list ...)` | Vector or list |
| `dict[K, V]` | `{:key val}` | Hash map (immutable) |
| `set[T]` | `#{...}` | Hash set (immutable) |
| `None` | `nil` | Absence of value |
| `class` | `defrecord` / `deftype` | Data structures |
| `def func():` | `(defn func [] ...)` | Function definition |
| `lambda x: x*2` | `#(* % 2)` or `(fn [x] (* x 2))` | Anonymous function |
| `for x in xs:` | `(doseq [x xs] ...)` | Side-effecting iteration |
| `[x for x in xs]` | `(for [x xs] ...)` | Lazy sequence comprehension |
| `try/except` | `(try ... (catch ...))` | Exception handling |
| `async def` | core.async channels | Different concurrency model |

## When Converting Code

1. **Analyze source thoroughly** before writing target
2. **Map types first** - Python and Clojure are both dynamic but Clojure emphasizes immutability
3. **Embrace immutability** - replace in-place mutations with functional transformations
4. **Use REPL-driven development** - Clojure is designed for interactive development
5. **Adopt functional idioms** - avoid classes, prefer pure functions and data transformations
6. **Handle edge cases** - None→nil, exceptions, mutable state
7. **Test equivalence** - same inputs → same outputs

---

## Type System Mapping

### Primitive Types

| Python | Clojure | Notes |
|--------|---------|-------|
| `int` | `int` / `long` | Automatic promotion to BigInteger |
| `float` | `double` | 64-bit IEEE 754 |
| `bool` | `true` / `false` | Lowercase boolean literals |
| `str` | `String` | Java.lang.String (immutable) |
| `bytes` | `byte-array` | Mutable Java byte array |
| `bytearray` | `byte-array` | Same as bytes in Clojure |
| `None` | `nil` | Represents absence |
| `...` (Ellipsis) | - | No equivalent |

**Note on Integers**: Both Python and Clojure support arbitrary precision integers. Clojure automatically promotes from `long` to `BigInteger` on overflow.

### Collection Types

| Python | Clojure | Notes |
|--------|---------|-------|
| `list[T]` | `[...]` | Vector - indexed, immutable, O(log32 n) |
| `tuple[T, U]` | `[...]` | Vector (immutable by default) |
| `tuple[T, ...]` | `(list ...)` | List for sequential access |
| `dict[K, V]` | `{:key val}` | Hash map - immutable, O(log32 n) |
| `set[T]` | `#{...}` | Hash set - immutable |
| `frozenset[T]` | `#{...}` | Sets are immutable by default |
| `collections.deque` | `clojure.lang.PersistentQueue` | Immutable queue |
| `collections.OrderedDict` | `(array-map ...)` or `linked-hash-map` | Maintains insertion order |
| `collections.defaultdict` | Map + `get-in` with default | Use `(get m k default)` pattern |
| `collections.Counter` | `frequencies` function | Built-in frequency counter |
| `range(n)` | `(range n)` | Lazy sequence |

### Composite Types

| Python | Clojure | Notes |
|--------|---------|-------|
| `@dataclass` | `defrecord` | Named fields, map-like access |
| `class` (data) | `defrecord` or plain map | Prefer maps for simple data |
| `class` (behavior) | Protocols + `defrecord` | Polymorphism via protocols |
| `typing.NamedTuple` | `defrecord` | Named, typed fields |
| `typing.TypedDict` | Plain map `{:key val}` | Maps with keyword keys |
| `enum.Enum` | Keyword enum | `#{:state/pending :state/done}` |
| `typing.Union[T, U]` | Tagged map or multimethod | `{:type :int :value 42}` |
| `typing.Optional[T]` | `nil` or value | `nil` represents absence |
| `typing.Callable` | `fn` or `IFn` | First-class functions |
| `typing.Protocol` | Clojure protocol | Polymorphism |

---

## Idiom Translation

### Pattern 1: List Comprehensions → Sequence Operations

**Python:**
```python
# List comprehension
squared_evens = [x * x for x in numbers if x % 2 == 0]

# Nested comprehension
pairs = [(x, y) for x in range(3) for y in range(2)]

# Generator expression
total = sum(x * x for x in numbers if x % 2 == 0)
```

**Clojure:**
```clojure
;; for - lazy sequence comprehension
(def squared-evens
  (for [x numbers
        :when (even? x)]
    (* x x)))

;; Nested for - cartesian product
(def pairs
  (for [x (range 3)
        y (range 2)]
    [x y]))

;; Direct transformation with threading
(def total
  (->> numbers
       (filter even?)
       (map #(* % %))
       (reduce +)))
```

**Why this translation:**
- Python list comprehensions are eager; Clojure `for` is lazy (more efficient)
- Clojure's threading macros (`->>`) make pipelines clearer
- `reduce` is idiomatic for aggregation

### Pattern 2: Dictionary Operations → Map Operations

**Python:**
```python
# Get with default
value = config.get("timeout", 30)

# Setdefault pattern
cache.setdefault(key, expensive_compute())

# Dictionary comprehension
squared = {k: v * v for k, v in items.items()}

# Merging dictionaries
merged = {**dict1, **dict2}
```

**Clojure:**
```clojure
;; Get with default
(def value (get config :timeout 30))

;; Lazy computation with update
(def cache (update cache key #(or % (expensive-compute))))

;; Or with caching (using memoize)
(defn get-cached [cache key compute-fn]
  (if-let [v (get cache key)]
    v
    (let [v (compute-fn)]
      (assoc cache key v))))

;; Map transformation
(def squared
  (into {} (map (fn [[k v]] [k (* v v)]) items)))

;; Merging maps
(def merged (merge dict1 dict2))
```

**Why this translation:**
- Clojure maps are immutable; use `assoc`, `update`, `merge` for "changes"
- Keywords (`:timeout`) are idiomatic for map keys
- `into` + `map` is the comprehension pattern for maps

### Pattern 3: Classes → Records and Maps

**Python:**
```python
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str

    def full_info(self):
        return f"{self.name} ({self.email})"

# Usage
user = User(id=1, name="Alice", email="alice@example.com")
print(user.name)
print(user.full_info())
```

**Clojure:**
```clojure
;; defrecord for structured data
(defrecord User [id name email])

;; Constructor and access
(def user (->User 1 "Alice" "alice@example.com"))
(println (:name user))  ; Map-like access

;; Functions operate on data
(defn full-info [user]
  (str (:name user) " (" (:email user) ")"))

(println (full-info user))

;; Alternative: plain map (often preferred for simple data)
(def user {:id 1 :name "Alice" :email "alice@example.com"})
(println (:name user))
(println (full-info user))
```

**Why this translation:**
- Clojure separates data from behavior (functions operate on data structures)
- `defrecord` provides type identity and performance benefits
- Plain maps are often simpler and more flexible than records
- Functions are defined separately, not as methods

### Pattern 4: Iteration → Sequence Operations

**Python:**
```python
# Imperative loop with mutation
result = []
for item in items:
    if item > 0:
        result.append(item * 2)

# Enumerate
for i, item in enumerate(items):
    print(f"{i}: {item}")

# Zip
for name, age in zip(names, ages):
    print(f"{name} is {age}")
```

**Clojure:**
```clojure
;; Functional transformation (immutable)
(def result
  (->> items
       (filter pos?)
       (map #(* % 2))))

;; map-indexed (like enumerate)
(doseq [[i item] (map-indexed vector items)]
  (println (str i ": " item)))

;; map for pairing (like zip)
(doseq [[name age] (map vector names ages)]
  (println (str name " is " age)))
```

**Why this translation:**
- Clojure favors pure transformations over imperative loops
- `filter`, `map`, `reduce` are core sequence operations
- `doseq` is for side effects (like printing), `for` is for lazy sequences
- `map-indexed` and `map vector` replace Python's enumerate and zip

### Pattern 5: None Handling → nil Handling

**Python:**
```python
# None checks
if user is not None:
    name = user.name
else:
    name = "Anonymous"

# Or with walrus
if (user := get_user(id)) is not None:
    process(user)

# Default value
name = user.name if user else "Anonymous"
```

**Clojure:**
```clojure
;; nil checks with when-let
(when-let [user (get-user id)]
  (process user))

;; Or with if-let
(def name
  (if-let [user user]
    (:name user)
    "Anonymous"))

;; Or with threading (some-> stops on nil)
(def name
  (some-> user :name (str " is here")))

;; Default value with or
(def name (or (:name user) "Anonymous"))
```

**Why this translation:**
- Clojure uses `nil` instead of `None`
- `when-let` and `if-let` bind and test in one step
- `some->` and `some->>` short-circuit on `nil` (like optional chaining)
- `or` returns first truthy value (like Python's `or`)

### Pattern 6: Exceptions → Explicit Error Handling

**Python:**
```python
# Raising exceptions
def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

# Catching exceptions
try:
    result = divide(10, 0)
except ValueError as e:
    print(f"Error: {e}")
    result = None

# Finally block
try:
    file = open("data.txt")
    data = file.read()
finally:
    file.close()
```

**Clojure:**
```clojure
;; Throwing exceptions (when appropriate)
(defn divide [a b]
  (if (zero? b)
    (throw (ex-info "Division by zero" {:a a :b b}))
    (/ a b)))

;; Catching exceptions
(def result
  (try
    (divide 10 0)
    (catch Exception e
      (println "Error:" (.getMessage e))
      nil)))

;; with-open for resource cleanup (like Python's with)
(with-open [rdr (clojure.java.io/reader "data.txt")]
  (def data (slurp rdr)))

;; Functional error handling (preferred for non-exceptional cases)
(defn safe-divide [a b]
  (if (zero? b)
    {:error "Division by zero"}
    {:ok (/ a b)}))

(let [result (safe-divide 10 0)]
  (if (:error result)
    (println "Error:" (:error result))
    (println "Result:" (:ok result))))
```

**Why this translation:**
- Clojure uses exceptions for truly exceptional cases
- For expected errors, return maps with `:ok` / `:error` keys (or use a library like `cats` for Either)
- `with-open` ensures resource cleanup (like Python's context managers)
- `ex-info` creates exceptions with data maps

### Pattern 7: Decorators → Macros or Higher-Order Functions

**Python:**
```python
# Function decorator
def logged(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper

@logged
def process(data):
    return len(data)

# Property decorator
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self):
        return 3.14159 * self._radius ** 2
```

**Clojure:**
```clojure
;; Higher-order function (decorator-like)
(defn logged [f]
  (fn [& args]
    (println "Calling" (str f))
    (let [result (apply f args)]
      (println "Finished" (str f))
      result)))

(def process (logged (fn [data] (count data))))

;; Or as a macro (compile-time transformation)
(defmacro defn-logged [name args & body]
  `(defn ~name ~args
     (println "Calling" ~(str name))
     (let [result# (do ~@body)]
       (println "Finished" ~(str name))
       result#)))

(defn-logged process [data]
  (count data))

;; "Property" via function (Clojure has no properties)
(defrecord Circle [radius])

(defn area [circle]
  (* 3.14159 (:radius circle) (:radius circle)))

(def c (->Circle 5))
(println (area c))
```

**Why this translation:**
- Python decorators → Clojure higher-order functions or macros
- Macros run at compile time, can transform syntax
- Clojure has no property syntax; use plain functions
- `defmacro` for code transformation, `defn` for runtime wrapping

### Pattern 8: Object-Oriented → Functional

**Python:**
```python
# Class with state and methods
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

    def get(self):
        return self.count

counter = Counter()
counter.increment()
counter.increment()
print(counter.get())  # 2
```

**Clojure:**
```clojure
;; Immutable data + pure functions
(defn increment [counter]
  (update counter :count inc))

(defn get-count [counter]
  (:count counter))

;; Usage with threading
(-> {:count 0}
    (increment)
    (increment)
    (get-count)
    (println))  ; 2

;; For mutable state, use atoms
(def counter (atom {:count 0}))

(defn increment! [counter]
  (swap! counter update :count inc))

(defn get-count! [counter]
  (:count @counter))

(increment! counter)
(increment! counter)
(println (get-count! counter))  ; 2
```

**Why this translation:**
- Clojure prefers immutable data + pure functions over mutable objects
- `->` threading macro passes result through function chain
- For necessary state, use atoms (`swap!` for updates, `@` for reads)
- Separate data (maps) from behavior (functions)

### Pattern 9: String Formatting → str and format

**Python:**
```python
# f-strings
name = "Alice"
age = 30
message = f"Hello {name}, you are {age} years old"

# format method
message = "Hello {}, you are {} years old".format(name, age)

# % formatting
message = "Hello %s, you are %d years old" % (name, age)
```

**Clojure:**
```clojure
;; str concatenation
(def name "Alice")
(def age 30)
(def message (str "Hello " name ", you are " age " years old"))

;; format (uses Java String.format)
(def message (format "Hello %s, you are %d years old" name age))

;; Or using clojure.pprint for complex formatting
(require '[clojure.pprint :refer [cl-format]])
(def message (cl-format nil "Hello ~A, you are ~D years old" name age))
```

**Why this translation:**
- `str` concatenates arguments (simple, idiomatic)
- `format` uses Java's `String.format` (printf-style)
- `cl-format` (Common Lisp format) for advanced formatting

### Pattern 10: Async/Await → core.async

**Python:**
```python
import asyncio

async def fetch_user(user_id):
    await asyncio.sleep(0.1)  # Simulate I/O
    return {"id": user_id, "name": f"User {user_id}"}

async def main():
    user = await fetch_user(123)
    print(user)

asyncio.run(main())
```

**Clojure:**
```clojure
(require '[clojure.core.async :as async :refer [go <! >! chan]])

;; core.async uses channels for communication
(defn fetch-user [user-id]
  (go
    (<! (async/timeout 100))  ; Simulate I/O
    {:id user-id :name (str "User " user-id)}))

(defn main []
  (let [result-chan (fetch-user 123)
        user (<!! result-chan)]  ; <!! blocks, <! for within go block
    (println user)))

(main)

;; Or with go blocks and channels
(go
  (let [user (<! (fetch-user 123))]
    (println user)))
```

**Why this translation:**
- Python's async/await → Clojure's `go` blocks and channels
- `<!` takes from channel (inside `go`), `<!!` blocks (outside `go`)
- `>!` puts onto channel, `>!!` blocks
- Different paradigm: CSP (channels) vs promises/futures

---

## Error Handling

### Python Exceptions → Clojure Approaches

| Python | Clojure | Notes |
|--------|---------|-------|
| `raise Exception("msg")` | `(throw (Exception. "msg"))` | Direct exception |
| `raise ValueError(...)` | `(throw (ex-info "msg" {:data ...}))` | Exception with data |
| `try: ... except E: ...` | `(try ... (catch E e ...))` | Catching exceptions |
| `try: ... finally: ...` | `(try ... (finally ...))` | Cleanup block |
| Return `None` for errors | Return `nil` or `{:error ...}` | Explicit error values |

### Exception Handling Translation

**Python:**
```python
def load_config(path):
    try:
        with open(path) as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Config file not found: {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return None
    finally:
        print("Cleanup")
```

**Clojure:**
```clojure
(require '[clojure.data.json :as json])

(defn load-config [path]
  (try
    (-> path
        slurp
        json/read-str)
    (catch java.io.FileNotFoundException e
      (println "Config file not found:" path)
      nil)
    (catch Exception e
      (println "Invalid JSON:" (.getMessage e))
      nil)
    (finally
      (println "Cleanup"))))
```

**Why this translation:**
- Similar try/catch/finally structure
- Clojure uses Java exception classes
- `slurp` reads entire file (like Python's `read()`)
- `json/read-str` parses JSON string

### Functional Error Handling (Preferred)

**Python (using optional types):**
```python
from typing import Optional

def safe_divide(a: int, b: int) -> Optional[float]:
    if b == 0:
        return None
    return a / b

result = safe_divide(10, 0)
if result is not None:
    print(f"Result: {result}")
else:
    print("Division by zero")
```

**Clojure (using maps or nil):**
```clojure
;; Returning nil for errors
(defn safe-divide [a b]
  (when-not (zero? b)
    (/ a b)))

(if-let [result (safe-divide 10 0)]
  (println "Result:" result)
  (println "Division by zero"))

;; Or using explicit error maps
(defn safe-divide [a b]
  (if (zero? b)
    {:error "Division by zero"}
    {:ok (/ a b)}))

(let [result (safe-divide 10 0)]
  (if (:error result)
    (println "Error:" (:error result))
    (println "Result:" (:ok result))))
```

**Why this translation:**
- Nil represents absence/failure (like Python's None)
- Maps with `:ok`/`:error` keys make errors explicit
- Functional error handling avoids exception overhead for common cases

---

## Concurrency Patterns

### Python Threading/Asyncio → Clojure Concurrency

| Python | Clojure | Notes |
|--------|---------|-------|
| `threading.Thread` | `(Thread. ...)` or futures | Java threads |
| `asyncio.run(coro)` | `(go ...)` or `(future ...)` | Async execution |
| `asyncio.gather(*tasks)` | `(async/alts! ...)` or `pmap` | Concurrent ops |
| `asyncio.Queue` | `(chan)` | Async channel |
| `threading.Lock` | `(atom)`, `(ref)`, or Java locks | Coordinated state |
| `concurrent.futures` | `future`, `promise` | Async results |

### Asyncio → core.async

**Python:**
```python
import asyncio

async def fetch_data(url):
    await asyncio.sleep(0.1)  # Simulate I/O
    return f"Data from {url}"

async def main():
    # Concurrent execution
    results = await asyncio.gather(
        fetch_data("url1"),
        fetch_data("url2"),
        fetch_data("url3")
    )
    for result in results:
        print(result)

asyncio.run(main())
```

**Clojure:**
```clojure
(require '[clojure.core.async :as async :refer [go <! >! chan]])

(defn fetch-data [url]
  (go
    (<! (async/timeout 100))  ; Simulate I/O
    (str "Data from " url)))

;; Concurrent execution with channels
(defn main []
  (let [urls ["url1" "url2" "url3"]
        channels (map fetch-data urls)]
    ;; Collect results
    (doseq [ch channels]
      (println (<!! ch)))))

(main)

;; Or using alts! for first-to-complete
(go
  (let [urls ["url1" "url2" "url3"]
        channels (map fetch-data urls)
        [result ch] (async/alts! channels)]
    (println "First result:" result)))
```

**Why this translation:**
- Python's async/await uses event loop; Clojure uses CSP channels
- `go` blocks are lightweight (like goroutines)
- Channels (`chan`) pass values between go blocks
- `alts!` is like `select` in Go (first-to-complete)

### Threading → Atoms and Futures

**Python:**
```python
from concurrent.futures import ThreadPoolExecutor

def process_item(item):
    return item * 2

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(process_item, range(10)))
    print(results)
```

**Clojure:**
```clojure
;; pmap - parallel map (uses futures)
(def results
  (pmap #(* % 2) (range 10)))

(println (doall results))  ; Force realization

;; Or explicit futures
(def results
  (doall (map #(future (* % 2)) (range 10))))

;; Dereference futures to get values
(def values (map deref results))
(println values)

;; Or use thread pool explicitly
(import '[java.util.concurrent Executors])
(def executor (Executors/newFixedThreadPool 4))

(def tasks
  (map #(.submit executor ^Callable (fn [] (* % 2))) (range 10)))

(def results (map #(.get %) tasks))
(.shutdown executor)
```

**Why this translation:**
- `pmap` is parallel map (automatic thread pool)
- `future` creates async task, `deref` or `@` waits for result
- Can use Java executors for fine-grained control

### State Management

**Python:**
```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    with lock:
        counter += 1

threads = [threading.Thread(target=increment) for _ in range(100)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)  # 100
```

**Clojure:**
```clojure
;; Atoms for uncoordinated state
(def counter (atom 0))

(defn increment! []
  (swap! counter inc))

;; Parallel updates (thread-safe)
(doall (pmap (fn [_] (increment!)) (range 100)))

(println @counter)  ; 100

;; Or refs for coordinated transactions
(def account-a (ref 100))
(def account-b (ref 200))

(defn transfer [from to amount]
  (dosync
    (alter from - amount)
    (alter to + amount)))

(transfer account-a account-b 50)
(println @account-a @account-b)  ; 50 250
```

**Why this translation:**
- Atoms for independent state (`swap!` for atomic updates)
- Refs for coordinated state (`dosync` for transactions)
- No locks needed - Clojure's concurrency primitives are thread-safe

---

## Common Pitfalls

### 1. Mutable State → Immutable Data

**Problem:**
```clojure
;; Python: in-place mutation
# items.append(value)
# items[0] = new_value

;; Clojure: trying to mutate
(def items [1 2 3])
(conj items 4)  ; Returns new vector, doesn't modify items!
(println items)  ; Still [1 2 3]
```

**Solution:**
```clojure
;; Rebind with new value
(def items (conj items 4))  ; Now items is [1 2 3 4]

;; Or use atoms for mutable state
(def items (atom [1 2 3]))
(swap! items conj 4)
(println @items)  ; [1 2 3 4]

;; Or work with local bindings
(let [items [1 2 3]
      items (conj items 4)
      items (conj items 5)]
  (println items))  ; [1 2 3 4 5]
```

**Why this matters:** Clojure's persistent data structures are immutable by default.

### 2. Truthiness Differences

**Problem:**
```clojure
;; Python: empty collections are falsy
# if items:  # True for [1, 2], False for []

;; Clojure: empty collections are truthy!
(if [] "truthy" "falsy")  ; => "truthy"
```

**Solution:**
```clojure
;; Explicitly check for emptiness
(if (seq items)
  "has items"
  "empty")

;; Or use empty?
(if-not (empty? items)
  "has items"
  "empty")
```

**Why this matters:** Only `nil` and `false` are falsy in Clojure. Empty collections are truthy.

### 3. Sequence Realization

**Problem:**
```clojure
;; Lazy sequences aren't realized until needed
(def nums (map #(do (println "Computing" %) (* % 2)) [1 2 3]))
;; Nothing printed yet!

(count nums)  ; Now it prints "Computing 1" "Computing 2" "Computing 3"
```

**Solution:**
```clojure
;; Force realization with doall
(def nums (doall (map #(do (println "Computing" %) (* % 2)) [1 2 3])))
;; Immediately prints

;; Or use doseq for side effects
(doseq [x [1 2 3]]
  (println "Computing" x))
```

**Why this matters:** Clojure sequences are lazy by default. Side effects in lazy sequences may not execute when expected.

### 4. Keyword vs String Keys

**Problem:**
```clojure
;; Python: strings as keys
# user = {"name": "Alice", "age": 30}

;; Clojure: mixing keywords and strings
(def user {"name" "Alice" :age 30})  ; Inconsistent!
(:name user)  ; nil (looking for keyword, but key is string)
```

**Solution:**
```clojure
;; Use keywords consistently
(def user {:name "Alice" :age 30})
(:name user)  ; "Alice"

;; Or strings consistently (less idiomatic)
(def user {"name" "Alice" "age" 30})
(get user "name")  ; "Alice"
```

**Why this matters:** Keywords (`:name`) are idiomatic for map keys in Clojure. They're faster and work as functions.

### 5. Namespace Collisions

**Problem:**
```clojure
;; Python: methods are namespaced by class
# user.get("name")
# config.get("timeout")

;; Clojure: same function name across namespaces
(require '[clojure.set :as set])
(set/union #{1 2} #{2 3})  ; Must qualify or alias
```

**Solution:**
```clojure
;; Always use namespace aliases
(require '[clojure.string :as str]
         '[clojure.set :as set])

(str/upper-case "hello")
(set/union #{1 2} #{2 3})

;; Or refer specific functions
(require '[clojure.string :refer [upper-case lower-case]])
(upper-case "hello")
```

**Why this matters:** Clojure namespaces prevent collisions but require explicit imports.

### 6. Integer Division

**Problem:**
```clojure
;; Python 3: / always returns float
# 5 / 2  # 2.5

;; Clojure: / returns ratio for integers
(/ 5 2)  ; 5/2 (ratio), not 2.5
```

**Solution:**
```clojure
;; Convert to double for floating-point division
(/ 5.0 2)  ; 2.5

;; Or use quot for integer division
(quot 5 2)  ; 2

;; Force ratio to double
(double (/ 5 2))  ; 2.5
```

**Why this matters:** Clojure preserves exact ratios. Use `double` or floating-point literals for decimals.

### 7. Variadic Functions

**Problem:**
```clojure
;; Python: *args, **kwargs
# def func(*args, **kwargs):
#     print(args, kwargs)

;; Clojure: rest args only (no keyword args)
(defn func [& args]
  (println args))

(func 1 2 3)  ; (1 2 3)
```

**Solution:**
```clojure
;; Use destructuring for keyword-style args
(defn func [& {:keys [name age] :or {age 0}}]
  (println name age))

(func :name "Alice" :age 30)  ; "Alice 30"
(func :name "Bob")  ; "Bob 0" (default age)

;; Or use maps explicitly
(defn func [opts]
  (println (:name opts) (:age opts 0)))

(func {:name "Alice" :age 30})
```

**Why this matters:** Clojure doesn't have keyword arguments. Use map destructuring or explicit maps.

### 8. Global Mutable State

**Problem:**
```clojure
;; Python: global keyword
# counter = 0
# def increment():
#     global counter
#     counter += 1

;; Clojure: def creates immutable binding
(def counter 0)
(defn increment []
  (def counter (inc counter)))  ; Bad! Creates new binding

(increment)
(println counter)  ; Still 0!
```

**Solution:**
```clojure
;; Use atoms for mutable state
(def counter (atom 0))

(defn increment! []
  (swap! counter inc))

(increment!)
(println @counter)  ; 1

;; Or pass state explicitly (functional style)
(defn increment [counter]
  (inc counter))

(-> 0
    increment
    increment
    increment
    println)  ; 3
```

**Why this matters:** `def` creates new vars; use atoms for mutable state or pass state explicitly.

---

## Tooling

### Translation Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Manual translation | Full control | Recommended for production |
| REPL experimentation | Interactive development | Core Clojure workflow |
| `clj-python` | Python-Clojure interop | Call Python from Clojure (libpython-clj) |

### Development Environment

| Python | Clojure | Purpose |
|--------|---------|---------|
| `python` | `clj` or `lein repl` | REPL |
| `pip` / `uv` | Leiningen or tools.deps | Package management |
| `pytest` | `clojure.test` | Testing framework |
| `mypy` | `clojure.spec` | Runtime validation |
| `black` | `cljfmt` | Code formatting |
| `pylint` | `eastwood`, `kibit` | Linting |

### Common Library Equivalents

| Python Package | Clojure Library | Purpose |
|----------------|-----------------|---------|
| `requests` | `clj-http` | HTTP client |
| `aiohttp` | `http-kit` | Async HTTP |
| `flask` / `fastapi` | `ring` + `compojure` | Web framework |
| `pydantic` | `clojure.spec` | Data validation |
| `click` / `argparse` | `tools.cli` | CLI parsing |
| `logging` | `tools.logging` | Logging |
| `datetime` | `clj-time` | Date/time |
| `pathlib` | `clojure.java.io` | File I/O |
| `json` | `clojure.data.json` | JSON parsing |
| `re` | `clojure.string` | Regex |
| `sqlite3` | `clojure.java.jdbc` | Database |
| `pandas` | `tech.ml.dataset` | Data frames |
| `numpy` | `core.matrix` | Numerical computing |

---

## Examples

### Example 1: Simple - HTTP GET Request

**Before (Python):**
```python
import requests

def fetch_user(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()

try:
    user = fetch_user(123)
    print(f"User: {user['name']}")
except requests.HTTPError as e:
    print(f"HTTP error: {e}")
```

**After (Clojure):**
```clojure
(require '[clj-http.client :as http]
         '[clojure.data.json :as json])

(defn fetch-user [user-id]
  (-> (str "https://api.example.com/users/" user-id)
      http/get
      :body
      (json/read-str :key-fn keyword)))

;; Usage
(try
  (let [user (fetch-user 123)]
    (println "User:" (:name user)))
  (catch Exception e
    (println "HTTP error:" (.getMessage e))))
```

**Key changes:**
- `requests.get` → `clj-http.client/get`
- Dictionary access `user['name']` → keyword access `(:name user)`
- `json/read-str` with `:key-fn keyword` converts JSON keys to keywords
- Similar try/catch structure

### Example 2: Medium - Configuration Parser

**Before (Python):**
```python
from pathlib import Path
import json
from dataclasses import dataclass

@dataclass
class Config:
    host: str
    port: int
    timeout: int = 30

    def validate(self):
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Invalid port: {self.port}")

def load_config(path):
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with path.open() as f:
        data = json.load(f)

    config = Config(**data)
    config.validate()
    return config

config = load_config(Path("config.json"))
print(f"Server: {config.host}:{config.port}")
```

**After (Clojure):**
```clojure
(require '[clojure.data.json :as json]
         '[clojure.spec.alpha :as s])

;; Define spec for validation
(s/def ::host string?)
(s/def ::port (s/and int? #(<= 1 % 65535)))
(s/def ::timeout (s/and int? pos?))
(s/def ::config (s/keys :req-un [::host ::port]
                        :opt-un [::timeout]))

(defn load-config [path]
  (when-not (.exists (clojure.java.io/file path))
    (throw (ex-info "Config not found" {:path path})))

  (let [config (-> path
                   slurp
                   (json/read-str :key-fn keyword)
                   (merge {:timeout 30}))]  ; Default value
    (when-not (s/valid? ::config config)
      (throw (ex-info "Invalid config" (s/explain-data ::config config))))
    config))

;; Usage
(let [config (load-config "config.json")]
  (println (format "Server: %s:%d" (:host config) (:port config))))
```

**Key changes:**
- `@dataclass` → plain map with `clojure.spec` validation
- Default values via `merge`
- `clojure.spec` for validation (runtime checks)
- `ex-info` for exceptions with data

### Example 3: Complex - Data Processing Pipeline

**Before (Python):**
```python
from collections import defaultdict
from dataclasses import dataclass
from typing import List

@dataclass
class Transaction:
    user_id: int
    amount: float
    category: str

def process_transactions(transactions: List[Transaction]):
    # Group by user
    by_user = defaultdict(list)
    for txn in transactions:
        by_user[txn.user_id].append(txn)

    # Calculate totals per category for each user
    results = {}
    for user_id, txns in by_user.items():
        category_totals = defaultdict(float)
        for txn in txns:
            category_totals[txn.category] += txn.amount

        # Only users with total > 100
        total = sum(category_totals.values())
        if total > 100:
            results[user_id] = {
                "total": total,
                "by_category": dict(category_totals),
                "count": len(txns)
            }

    return results

transactions = [
    Transaction(1, 50.0, "food"),
    Transaction(1, 75.0, "transport"),
    Transaction(2, 200.0, "food"),
    Transaction(1, 25.0, "food"),
]

results = process_transactions(transactions)
for user_id, stats in results.items():
    print(f"User {user_id}: {stats}")
```

**After (Clojure):**
```clojure
(defn process-transactions [transactions]
  (->> transactions
       ;; Group by user
       (group-by :user-id)

       ;; Transform each user's transactions
       (map (fn [[user-id txns]]
              (let [;; Calculate category totals
                    by-category (->> txns
                                     (group-by :category)
                                     (map (fn [[cat items]]
                                            [cat (reduce + (map :amount items))]))
                                     (into {}))

                    total (reduce + (vals by-category))
                    count (count txns)]

                [user-id {:total total
                         :by-category by-category
                         :count count}])))

       ;; Filter users with total > 100
       (filter (fn [[_ stats]] (> (:total stats) 100)))

       ;; Convert to map
       (into {})))

;; Usage
(def transactions
  [{:user-id 1 :amount 50.0 :category "food"}
   {:user-id 1 :amount 75.0 :category "transport"}
   {:user-id 2 :amount 200.0 :category "food"}
   {:user-id 1 :amount 25.0 :category "food"}])

(def results (process-transactions transactions))

(doseq [[user-id stats] results]
  (println (format "User %d: %s" user-id stats)))
```

**Key changes:**
- `@dataclass` → plain maps
- Imperative loops → functional pipeline with `->>` threading
- `defaultdict` → `group-by` function
- `for` loops → `map`, `filter`, `reduce`
- Immutable transformations throughout
- More declarative, less mutable state

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `lang-python-dev` - Python development patterns
- `lang-clojure-dev` - Clojure development patterns
- `patterns-concurrency-dev` - Async/channels patterns across languages
- `patterns-serialization-dev` - JSON/EDN serialization patterns
