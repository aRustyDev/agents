---
name: convert-clojure-haskell
description: Bidirectional conversion between Clojure and Haskell. Use when migrating projects between these languages in either direction. Extends meta-convert-dev with Clojure↔Haskell specific patterns. Use when migrating Clojure projects to Haskell, translating Clojure patterns to idiomatic Haskell, or refactoring Clojure codebases. Extends meta-convert-dev with Clojure-to-Haskell specific patterns.
---

# Clojure ↔ Haskell Conversion

Bidirectional conversion between Clojure and Haskell. This skill extends `meta-convert-dev` with Clojure↔Haskell specific type mappings, idiom translations, and tooling for migrating functional JVM code to native compiled Haskell.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Clojure types → Haskell types
- **Idiom translations**: Clojure patterns → idiomatic Haskell
- **Error handling**: Clojure exceptions → Haskell Maybe/Either
- **Concurrency patterns**: Clojure atoms/refs/agents → Haskell STM/async
- **REPL workflow**: REPL-driven development → GHCi interactive development
- **Macro translation**: Clojure macros → Haskell Template Haskell or type-level patterns

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Clojure language fundamentals - see `lang-clojure-dev`
- Haskell language fundamentals - see `lang-haskell-dev`
- ClojureScript → PureScript/Elm - see dedicated frontend conversion skills

---

## Quick Reference

| Clojure | Haskell | Notes |
|---------|---------|-------|
| `String` | `String` or `Text` | Use Text for production |
| `Long` | `Int` or `Integer` | Integer for unbounded |
| `Double` | `Double` | Direct mapping |
| `Boolean` | `Bool` | Direct mapping |
| `nil` | `Nothing` | Part of Maybe type |
| `vector` | `[]` or `Vector` | List or Data.Vector |
| `map` | `Map` | Use Data.Map |
| `set` | `Set` | Use Data.Set |
| `keyword` | Custom type or `String` | No direct equivalent |
| `atom` | `IORef` or `TVar` | Mutable reference |
| `ref` | `TVar` | Software transactional memory |
| `agent` | `Async` | Asynchronous computation |
| `(defn f [x] ...)` | `f x = ...` | Function definition |
| `(fn [x] ...)` | `\x -> ...` | Anonymous function |
| `try/catch` | `Either` or `ExceptT` | Error handling |

## When Converting Code

1. **Analyze source thoroughly** - Understand Clojure's dynamic nature before writing static Haskell
2. **Map types first** - Clojure's dynamic types need explicit Haskell types
3. **Preserve semantics** over syntax similarity
4. **Embrace static typing** - Use Haskell's type system to prevent runtime errors
5. **Handle nil properly** - All potential nils become Maybe/Either
6. **Test equivalence** - Same inputs → same outputs for pure logic

---

## Type System Mapping

### Primitive Types

| Clojure | Haskell | Notes |
|---------|---------|-------|
| `String` | `String` | List of Char (inefficient) |
| `String` | `Text` | **Preferred** for production (from `Data.Text`) |
| `Long` | `Int` | Bounded integer (architecture-dependent) |
| `Long` | `Integer` | Unbounded (arbitrary precision) |
| `Double` | `Float` | Single precision |
| `Double` | `Double` | **Preferred** double precision |
| `Boolean` | `Bool` | Direct mapping |
| `nil` | `Nothing` | Use Maybe type |
| `Keyword` | `Text` or custom ADT | Keywords are symbols; consider tagged types |
| `Symbol` | `String` | Rarely needed; use at compile time |

### Collection Types

| Clojure | Haskell | Notes |
|---------|---------|-------|
| `(list ...)` | `[a]` | Linked list |
| `[...]` (vector) | `[a]` or `Vector a` | Use Data.Vector for indexed access |
| `{:key val}` | `Map Text a` | Use Data.Map from `containers` |
| `#{...}` | `Set a` | Use Data.Set from `containers` |
| `(seq ...)` | `[a]` | Lazy sequences → lazy lists |
| Transient collections | `Vector` or mutable structures | Use ST monad or Data.Vector |

### Composite Types

| Clojure | Haskell | Notes |
|---------|---------|-------|
| `(defrecord User [name age])` | `data User = User { name :: Text, age :: Int }` | Record syntax |
| `(deftype ...)` | `data` or `newtype` | For performance or type safety |
| Maps as records | Record types or `Map` | Prefer explicit records |
| Multi-arity functions | Multiple function definitions or tuples | Pattern matching on arity |
| Protocols | Type classes | Polymorphic behavior |
| Multimethods | Type classes or pattern matching | Dynamic dispatch → static dispatch |

### Nil and Optional Values

**Clojure:**
```clojure
(defn find-user [id users]
  (first (filter #(= (:id %) id) users)))  ; Returns nil if not found

(get {:name "Alice"} :age)  ; Returns nil
```

**Haskell:**
```haskell
import Data.Maybe (listToMaybe)
import qualified Data.Map as Map

findUser :: Int -> [User] -> Maybe User
findUser userId = listToMaybe . filter (\u -> userId == userId u)

-- Map lookup returns Maybe
Map.lookup "age" (Map.fromList [("name", "Alice")])  -- Nothing
```

**Why this translation:**
- Clojure's nil is pervasive; Haskell makes optionality explicit with Maybe
- All nil checks in Clojure become pattern matches on Nothing/Just
- Type safety prevents null pointer exceptions at compile time

---

## Idiom Translation

### Pattern 1: Threading Macros to Function Composition

**Clojure:**
```clojure
;; Thread-first (->)
(-> data
    (parse-json)
    (get :users)
    (filter active?)
    (map :name)
    (sort))

;; Thread-last (->>)
(->> (range 100)
     (map inc)
     (filter even?)
     (reduce +))
```

**Haskell:**
```haskell
import Data.Function ((&))
import qualified Data.List as List

-- Using function composition (right to left)
processData :: Value -> [Text]
processData = List.sort . map name . filter active . getUsers . parseJSON

-- Or using & operator (left to right, like ->)
processData' :: Value -> [Text]
processData' data =
    data
    & parseJSON
    & getUsers
    & filter active
    & map name
    & List.sort

-- Thread-last style
sumEvenInc :: Int
sumEvenInc = sum . filter even . map (+1) $ [0..99]

-- Or with $
sumEvenInc' = sum $ filter even $ map (+1) [0..99]
```

**Why this translation:**
- Clojure's `->` maps to Haskell's `&` operator (from Data.Function)
- Function composition (`.`) is more idiomatic in Haskell but reads right-to-left
- Use `$` for right-associative application
- Pattern: `(->> x f g h)` → `h . g . f $ x`

### Pattern 2: Destructuring

**Clojure:**
```clojure
;; Sequential destructuring
(let [[a b & rest] [1 2 3 4 5]]
  (+ a b))

;; Map destructuring
(defn greet [{:keys [name age] :or {age 0}}]
  (str "Hello " name ", age " age))

(greet {:name "Alice" :age 30})
```

**Haskell:**
```haskell
-- Pattern matching on lists
exampleList :: [Int] -> Int
exampleList (a:b:rest) = a + b
exampleList _ = 0

-- Record pattern matching
data Person = Person { name :: Text, age :: Int }

greet :: Person -> Text
greet Person{name, age} = "Hello " <> name <> ", age " <> show age

-- With default values (Maybe pattern)
greetMaybe :: Maybe Int -> Person -> Text
greetMaybe maybeAge Person{name} =
    let actualAge = fromMaybe 0 maybeAge
    in "Hello " <> name <> ", age " <> show actualAge
```

**Why this translation:**
- Clojure's destructuring is runtime; Haskell's pattern matching is compile-time
- Haskell enforces exhaustive pattern matching
- Record syntax provides named field access
- Default values use Maybe or function parameters

### Pattern 3: Sequence Operations

**Clojure:**
```clojure
;; Map, filter, reduce
(->> users
     (filter :active)
     (map :email)
     (filter valid-email?)
     (reduce conj #{}))

;; List comprehension with for
(for [x (range 10)
      y (range 10)
      :when (= (+ x y) 10)]
  [x y])
```

**Haskell:**
```haskell
import Data.Set (Set)
import qualified Data.Set as Set

-- Map, filter, fold
processUsers :: [User] -> Set Email
processUsers =
    Set.fromList .
    filter validEmail .
    map email .
    filter active

-- List comprehension
pairs :: [(Int, Int)]
pairs = [(x, y) | x <- [0..9], y <- [0..9], x + y == 10]

-- Or with do-notation (list monad)
pairs' :: [(Int, Int)]
pairs' = do
    x <- [0..9]
    y <- [0..9]
    guard (x + y == 10)
    return (x, y)
```

**Why this translation:**
- Both languages support functional pipelines
- Haskell's list comprehensions are more powerful (guards, multiple generators)
- Set.fromList is idiomatic for building sets from lists
- Do-notation provides monadic abstraction over list comprehension

### Pattern 4: Lazy Sequences

**Clojure:**
```clojure
;; Infinite sequences
(def naturals (iterate inc 0))
(take 5 naturals)  ; (0 1 2 3 4)

;; Lazy evaluation
(def evens (filter even? naturals))
(take 3 evens)  ; (0 2 4)

;; Custom lazy sequence
(defn fibonacci []
  (map first (iterate (fn [[a b]] [b (+ a b)]) [0 1])))
```

**Haskell:**
```haskell
-- Infinite lists (lazy by default)
naturals :: [Integer]
naturals = iterate (+1) 0

take 5 naturals  -- [0,1,2,3,4]

-- Lazy filtering
evens :: [Integer]
evens = filter even naturals

take 3 evens  -- [0,2,4]

-- Custom lazy sequence
fibonacci :: [Integer]
fibonacci = 0 : 1 : zipWith (+) fibonacci (tail fibonacci)

-- Or more explicit
fibonacci' :: [Integer]
fibonacci' = map fst $ iterate (\(a, b) -> (b, a + b)) (0, 1)
```

**Why this translation:**
- Both languages are lazy by default for sequences
- Haskell's laziness is pervasive; Clojure's is opt-in for sequences
- Infinite data structures work the same way
- Haskell's `zipWith` provides elegant recursive definitions

---

## Paradigm Translation

### Mental Model: Dynamic → Static Typing

| Clojure Approach | Haskell Approach | Key Insight |
|------------------|------------------|-------------|
| Runtime type checks | Compile-time type checking | Types guarantee correctness |
| Maps as flexible data | Records with defined fields | Explicit structure |
| Protocols for polymorphism | Type classes for polymorphism | Principled abstraction |
| nil anywhere | Maybe/Either for optionality | Explicit error handling |
| Exception throwing | Pure error values (Either) | Errors are values |

### Concurrency Mental Model

| Clojure Model | Haskell Model | Conceptual Translation |
|---------------|---------------|------------------------|
| Atoms (atomic updates) | IORef or TVar | Mutable reference |
| Refs (coordinated) | STM (Software Transactional Memory) | Coordinated updates |
| Agents (async) | Async library | Background computation |
| core.async channels | Concurrency library channels | CSP-style communication |
| Future/promise | Async or Future | Deferred computation |

---

## Error Handling

### Exceptions → Maybe/Either

**Clojure:**
```clojure
(defn parse-age [s]
  (try
    (let [age (Integer/parseInt s)]
      (if (pos? age)
        age
        (throw (ex-info "Age must be positive" {:age age}))))
    (catch NumberFormatException e
      (throw (ex-info "Invalid number" {:input s})))))

(defn validate-user [age-str email-str]
  (try
    {:age (parse-age age-str)
     :email (validate-email email-str)}
    (catch Exception e
      nil)))
```

**Haskell:**
```haskell
import Text.Read (readMaybe)
import Data.Text (Text)

data ValidationError
    = InvalidNumber Text
    | NegativeAge Int
    | InvalidEmail Text
    deriving (Show, Eq)

parseAge :: Text -> Either ValidationError Int
parseAge s =
    case readMaybe (unpack s) of
        Nothing -> Left (InvalidNumber s)
        Just age ->
            if age > 0
                then Right age
                else Left (NegativeAge age)

validateUser :: Text -> Text -> Either ValidationError User
validateUser ageStr emailStr = do
    age <- parseAge ageStr
    email <- validateEmail emailStr
    return $ User age email

-- Or with Applicative for independent validations
validateUser' :: Text -> Text -> Either ValidationError User
validateUser' ageStr emailStr =
    User <$> parseAge ageStr <*> validateEmail emailStr
```

**Why this translation:**
- Clojure exceptions are runtime; Haskell Either is type-checked
- Either forces handling of error cases at compile time
- Do-notation provides clean error chaining (like try/catch flow)
- Applicative style validates independently and collects errors

### Exception Handling Patterns

| Clojure Pattern | Haskell Pattern | Notes |
|-----------------|-----------------|-------|
| `try/catch` | `Either a b` or `ExceptT` | Pure error handling |
| `throw` | `Left err` or `throwError` | Return error value |
| `ex-info` with data | Custom ADT error types | Structured errors |
| `finally` | `bracket` or `finally` | Resource cleanup |
| `nil` for missing | `Maybe a` | Optional values |

---

## Concurrency Patterns

### Atoms → IORef/TVar

**Clojure:**
```clojure
(def counter (atom 0))

;; Atomic update
(swap! counter inc)
(swap! counter + 10)

;; Read value
@counter

;; Reset value
(reset! counter 0)

;; Conditional update
(compare-and-set! counter 0 100)
```

**Haskell:**
```haskell
import Data.IORef
import Control.Concurrent.STM

-- Using IORef (not transactional)
example :: IO ()
example = do
    counter <- newIORef 0

    -- Atomic update
    modifyIORef' counter (+1)
    modifyIORef' counter (+10)

    -- Read value
    value <- readIORef counter

    -- Write value
    writeIORef counter 0

-- Using TVar (transactional)
exampleSTM :: IO ()
exampleSTM = do
    counter <- newTVarIO 0

    atomically $ do
        modifyTVar' counter (+1)
        modifyTVar' counter (+10)

    -- Read
    value <- readTVarIO counter

    -- Write
    atomically $ writeTVar counter 0
```

**Why this translation:**
- Clojure atoms provide atomic updates; Haskell IORef or TVar similar
- For simple cases, IORef sufficient; for composition, use STM
- STM provides composable transactions like Clojure refs
- Both guarantee atomic updates without locks

### Refs → Software Transactional Memory (STM)

**Clojure:**
```clojure
(def account-a (ref 100))
(def account-b (ref 200))

;; Coordinated transaction
(dosync
  (alter account-a - 50)
  (alter account-b + 50))

;; Read consistent snapshot
(dosync
  [@account-a @account-b])
```

**Haskell:**
```haskell
import Control.Concurrent.STM

transfer :: TVar Int -> TVar Int -> Int -> IO ()
transfer fromAccount toAccount amount = atomically $ do
    fromBalance <- readTVar fromAccount
    toBalance <- readTVar toAccount
    writeTVar fromAccount (fromBalance - amount)
    writeTVar toAccount (toBalance + amount)

-- Read consistent snapshot
readAccounts :: TVar Int -> TVar Int -> IO (Int, Int)
readAccounts account1 account2 = atomically $ do
    bal1 <- readTVar account1
    bal2 <- readTVar account2
    return (bal1, bal2)

-- Usage
main :: IO ()
main = do
    accountA <- newTVarIO 100
    accountB <- newTVarIO 200
    transfer accountA accountB 50
    (a, b) <- readAccounts accountA accountB
    print (a, b)  -- (50, 250)
```

**Why this translation:**
- Both use Software Transactional Memory for coordinated updates
- Clojure's dosync = Haskell's atomically
- alter/commute = modifyTVar/writeTVar
- Both provide automatic retry on conflicts
- Both guarantee ACID properties

### Agents → Async

**Clojure:**
```clojure
(def logger (agent []))

;; Send async update
(send logger conj "Entry 1")
(send logger conj "Entry 2")

;; Wait for completion
(await logger)

;; For blocking operations
(send-off logger
  (fn [logs]
    (Thread/sleep 1000)
    (conj logs "Delayed")))
```

**Haskell:**
```haskell
import Control.Concurrent.Async
import Control.Concurrent (threadDelay)

-- Using async library
exampleAsync :: IO ()
exampleAsync = do
    -- Launch async computations
    a1 <- async $ return (1 :: Int)
    a2 <- async $ return (2 :: Int)

    -- Wait for results
    result1 <- wait a1
    result2 <- wait a2

    print (result1 + result2)

-- For sequential async operations (like agents)
processLogs :: [String] -> IO ()
processLogs initialLogs = do
    ref <- newIORef initialLogs

    -- Spawn background worker
    async $ do
        threadDelay 1000000  -- 1 second
        modifyIORef' ref (++ ["Delayed entry"])

    -- Continue main work...
    return ()
```

**Why this translation:**
- Clojure agents are for async sequential updates
- Haskell async provides concurrent execution
- For sequential updates, combine async with IORef
- Both allow non-blocking computation

### core.async → Channels

**Clojure:**
```clojure
(require '[clojure.core.async :as async])

(let [ch (async/chan 10)]
  ;; Producer
  (async/go
    (async/>! ch "Hello")
    (async/>! ch "World")
    (async/close! ch))

  ;; Consumer
  (async/go-loop []
    (when-let [msg (async/<! ch)]
      (println msg)
      (recur))))
```

**Haskell:**
```haskell
import Control.Concurrent
import Control.Concurrent.Chan

exampleChannels :: IO ()
exampleChannels = do
    ch <- newChan

    -- Producer
    forkIO $ do
        writeChan ch "Hello"
        writeChan ch "World"
        -- Note: Chan doesn't have explicit close

    -- Consumer
    forkIO $ forever $ do
        msg <- readChan ch
        putStrLn msg

    threadDelay 1000000  -- Wait for processing

-- Or with STM channels (bounded)
import Control.Concurrent.STM.TBQueue

exampleBounded :: IO ()
exampleBounded = do
    queue <- newTBQueueIO 10

    forkIO $ do
        atomically $ writeTBQueue queue "Hello"
        atomically $ writeTBQueue queue "World"

    forkIO $ forever $ do
        msg <- atomically $ readTBQueue queue
        putStrLn msg
```

**Why this translation:**
- Both provide CSP-style channels for communication
- Clojure's core.async go blocks = Haskell's forkIO
- STM channels provide bounded queues like core.async
- Both enable producer/consumer patterns

---

## Memory & Ownership

### Immutability by Default

Both Clojure and Haskell embrace immutability, but with different enforcement:

| Aspect | Clojure | Haskell |
|--------|---------|---------|
| Default | Immutable persistent structures | Pure values (immutable) |
| Mutable escape hatch | Atoms, refs, agents | IO monad, ST monad |
| Enforcement | Convention (runtime) | Type system (compile-time) |
| Structure sharing | Yes (persistent data structures) | Yes (via laziness and GC) |

**Clojure:**
```clojure
;; All updates return new values
(def v1 [1 2 3])
(def v2 (conj v1 4))  ; v1 unchanged
;; v1 => [1 2 3]
;; v2 => [1 2 3 4]

;; Structural sharing
(def big-map (into {} (map vector (range 10000) (range 10000))))
(def updated (assoc big-map 5000 "changed"))  ; O(log n), shares most nodes
```

**Haskell:**
```haskell
-- All values are immutable by default
v1 = [1, 2, 3]
v2 = v1 ++ [4]  -- v1 unchanged
-- v1 = [1,2,3]
-- v2 = [1,2,3,4]

-- Structural sharing via laziness
import qualified Data.Map as Map

bigMap = Map.fromList [(i, i) | i <- [0..9999]]
updated = Map.insert 5000 "changed" bigMap  -- O(log n), shares structure
```

**Why this translation:**
- Both languages default to immutability
- Haskell enforces purity via types; Clojure via convention
- Performance characteristics similar due to structural sharing
- Mutable state explicit in both (atoms/refs vs IORef/TVar)

---

## Macro Translation

### Clojure Macros → Haskell Alternatives

Clojure macros operate at the syntactic level; Haskell provides multiple alternatives:

| Clojure Macro Use Case | Haskell Alternative | Notes |
|------------------------|---------------------|-------|
| Code generation | Template Haskell | Compile-time metaprogramming |
| DSL creation | Embedded DSL with operators | Type-safe DSLs |
| Conditional compilation | CPP or Cabal flags | Preprocessing |
| Control flow abstraction | Higher-order functions | Functions as first-class |
| Syntax transformation | Type classes + operators | Principled abstraction |

**Clojure:**
```clojure
;; Custom control flow macro
(defmacro unless [condition & body]
  `(if (not ~condition)
     (do ~@body)))

(unless false
  (println "This runs"))

;; DSL macro
(defmacro with-logging [expr]
  `(let [start# (System/currentTimeMillis)
         result# ~expr]
     (println "Took" (- (System/currentTimeMillis) start#) "ms")
     result#))
```

**Haskell:**
```haskell
{-# LANGUAGE TemplateHaskell #-}

import Language.Haskell.TH

-- Template Haskell for code generation
-- (Advanced use case, often unnecessary)

-- More idiomatic: Higher-order functions
unless :: Bool -> IO () -> IO ()
unless condition action =
    if not condition
        then action
        else return ()

-- Usage
unless False $ putStrLn "This runs"

-- Logging via function composition
import System.CPUTime
import Text.Printf

withLogging :: IO a -> IO a
withLogging action = do
    start <- getCPUTime
    result <- action
    end <- getCPUTime
    let diff = fromIntegral (end - start) / (10^12)
    printf "Computation time: %0.3f sec\n" (diff :: Double)
    return result

-- Usage
withLogging $ do
    putStrLn "Working..."
    return ()
```

**Why this translation:**
- Most Clojure macros can be replaced with Haskell functions
- Higher-order functions provide abstraction without compile-time magic
- Template Haskell available for true compile-time metaprogramming
- Type system + operators enable many DSLs without macros

---

## Common Pitfalls

### 1. Dynamic Type Assumptions → Static Type Requirements

**Problem:** Clojure allows heterogeneous collections; Haskell requires homogeneous types.

```clojure
;; Clojure: Mixed types OK
(def mixed [1 "two" :three 4.0])
```

```haskell
-- Haskell: Need sum type for mixed
data Value
    = IntVal Int
    | StringVal String
    | KeywordVal String
    | DoubleVal Double

mixed :: [Value]
mixed = [IntVal 1, StringVal "two", KeywordVal "three", DoubleVal 4.0]
```

**Fix:** Use algebraic data types (ADTs) to represent variants.

### 2. Nil Propagation → Maybe Chaining

**Problem:** Clojure's nil freely propagates; Haskell requires explicit handling.

```clojure
;; Clojure: nil just flows through
(-> data :user :email str/upper-case)  ; NPE if any step is nil
```

```haskell
-- Haskell: Must handle Maybe at each step
import qualified Data.Text as T
import Data.Maybe (fromMaybe)

processEmail :: Data -> Maybe T.Text
processEmail d = do
    user <- getUser d
    email <- getEmail user
    return $ T.toUpper email

-- Or with combinators
processEmail' :: Data -> T.Text
processEmail' d =
    fromMaybe "" $ fmap T.toUpper (getUser d >>= getEmail)
```

**Fix:** Use Maybe monad or applicative functors to chain computations.

### 3. Lazy Sequences vs Lazy Evaluation

**Problem:** Clojure sequences are explicitly lazy; Haskell is lazy everywhere.

```clojure
;; Clojure: Force evaluation when needed
(let [xs (map expensive-fn (range 1000))]
  (doall xs)  ; Force evaluation
  xs)
```

```haskell
-- Haskell: Lazy by default, force with strictness annotations
import Control.DeepSeq

let xs = map expensiveFn [0..999]
in xs `deepseq` xs  -- Force full evaluation

-- Or use strict data structures
import qualified Data.Vector as V

let xs = V.map expensiveFn (V.enumFromN 0 1000)
in xs  -- Vector is strict
```

**Fix:** Understand laziness difference; use strict evaluation when needed.

### 4. Keyword Keys → Text or Custom Types

**Problem:** Clojure keywords don't have direct Haskell equivalent.

```clojure
;; Clojure: Keywords as map keys
{:name "Alice" :age 30 :email "alice@example.com"}
```

```haskell
-- Option 1: Use records (preferred)
data User = User
    { name :: Text
    , age :: Int
    , email :: Text
    }

-- Option 2: Use Text keys in Map
import qualified Data.Map as Map

userMap :: Map Text String
userMap = Map.fromList
    [ ("name", "Alice")
    , ("age", "30")
    , ("email", "alice@example.com")
    ]

-- Option 3: Custom keyword type
newtype Keyword = Keyword Text deriving (Eq, Ord, Show)

keywordMap :: Map Keyword String
keywordMap = Map.fromList
    [ (Keyword "name", "Alice")
    , (Keyword "age", "30")
    ]
```

**Fix:** Use records for structured data; Map for truly dynamic cases.

### 5. REPL Workflow Differences

**Problem:** Clojure's REPL allows redefining anything; GHCi more restricted.

**Clojure:**
```clojure
;; Can reload everything at runtime
(require 'myapp.core :reload)
(in-ns 'myapp.core)
```

**Haskell (GHCi):**
```haskell
-- Type changes require restart
:reload  -- Reload current modules
:type expr  -- Check types
:info Name  -- Get information

-- For rapid development, use ghcid
-- ghcid watches files and reloads automatically
```

**Fix:** Use ghcid for auto-reload; accept that type changes need restart.

---

## Tooling

### Development Tools

| Tool | Purpose | Clojure Equivalent |
|------|---------|-------------------|
| GHC | Haskell compiler | Clojure compiler (JVM) |
| GHCi | Interactive REPL | Clojure REPL |
| Cabal | Build tool & package manager | Leiningen |
| Stack | Alternative build tool | Leiningen + profiles |
| Hoogle | Type-based search | clojure.repl/apropos |
| HLint | Linter | Eastwood |
| ghcid | Auto-reload dev tool | REPL-driven dev |
| Haddock | Documentation generator | Codox |

### Build Configuration Mapping

**Clojure (project.clj):**
```clojure
(defproject myapp "0.1.0"
  :dependencies [[org.clojure/clojure "1.11.1"]
                 [cheshire "5.12.0"]
                 [compojure "1.7.0"]]
  :main myapp.core)
```

**Haskell (package.yaml or .cabal):**
```yaml
# package.yaml (for stack/hpack)
name: myapp
version: 0.1.0

dependencies:
  - base >= 4.7 && < 5
  - aeson  # JSON (like cheshire)
  - text   # Text handling
  - warp   # Web server (like ring)

executables:
  myapp:
    main: Main.hs
    source-dirs: src
```

### Library Equivalents

| Purpose | Clojure | Haskell |
|---------|---------|---------|
| JSON | cheshire | aeson |
| HTTP client | clj-http | http-client, req |
| Web framework | Ring/Compojure | Warp/Servant |
| Database | clojure.java.jdbc | persistent, postgresql-simple |
| Testing | clojure.test | HUnit, QuickCheck, Hspec |
| Async | core.async | async, stm |
| CLI parsing | tools.cli | optparse-applicative |
| Logging | timbre | fast-logger, katip |

---

## Examples

### Example 1: Simple - Data Transformation

**Before (Clojure):**
```clojure
(defn process-users [users]
  (->> users
       (filter :active)
       (map :email)
       (map str/lower-case)
       (into #{})))

;; Usage
(process-users
  [{:name "Alice" :email "ALICE@EXAMPLE.COM" :active true}
   {:name "Bob" :email "BOB@EXAMPLE.COM" :active false}
   {:name "Carol" :email "CAROL@EXAMPLE.COM" :active true}])
;; => #{"alice@example.com" "carol@example.com"}
```

**After (Haskell):**
```haskell
import qualified Data.Text as T
import qualified Data.Set as Set

data User = User
    { name :: T.Text
    , email :: T.Text
    , active :: Bool
    } deriving (Show, Eq)

processUsers :: [User] -> Set.Set T.Text
processUsers =
    Set.fromList .
    map (T.toLower . email) .
    filter active

-- Usage
let users =
        [ User "Alice" "ALICE@EXAMPLE.COM" True
        , User "Bob" "BOB@EXAMPLE.COM" False
        , User "Carol" "CAROL@EXAMPLE.COM" True
        ]
in processUsers users
-- fromList ["alice@example.com","carol@example.com"]
```

### Example 2: Medium - Error Handling

**Before (Clojure):**
```clojure
(defn parse-user [data]
  (try
    (let [age (Integer/parseInt (:age data))]
      (when (neg? age)
        (throw (ex-info "Negative age" {:age age})))
      {:name (:name data)
       :age age
       :email (:email data)})
    (catch NumberFormatException e
      (throw (ex-info "Invalid age format" {:input (:age data)})))
    (catch Exception e
      nil)))

(defn process-user-data [raw-data]
  (try
    (let [user (parse-user raw-data)]
      (when (some nil? (vals user))
        (throw (ex-info "Missing fields" {:user user})))
      user)
    (catch Exception e
      {:error (.getMessage e)})))
```

**After (Haskell):**
```haskell
import qualified Data.Text as T
import Text.Read (readMaybe)

data User = User
    { userName :: T.Text
    , userAge :: Int
    , userEmail :: T.Text
    } deriving (Show, Eq)

data ParseError
    = InvalidAgeFormat T.Text
    | NegativeAge Int
    | MissingField T.Text
    deriving (Show, Eq)

parseUser :: Map T.Text T.Text -> Either ParseError User
parseUser dataMap = do
    name <- maybe (Left $ MissingField "name") Right $ Map.lookup "name" dataMap
    ageStr <- maybe (Left $ MissingField "age") Right $ Map.lookup "age" dataMap
    email <- maybe (Left $ MissingField "email") Right $ Map.lookup "email" dataMap

    age <- case readMaybe (T.unpack ageStr) of
        Nothing -> Left $ InvalidAgeFormat ageStr
        Just a | a < 0 -> Left $ NegativeAge a
               | otherwise -> Right a

    return $ User name age email

-- Or with Applicative for cleaner code
import Control.Applicative ((<|>))

parseUser' :: Map T.Text T.Text -> Either ParseError User
parseUser' m =
    User <$> getField "name" m
         <*> (getField "age" m >>= parseAge)
         <*> getField "email" m
  where
    getField k = maybe (Left $ MissingField k) Right $ Map.lookup k m
    parseAge s = case readMaybe (T.unpack s) of
        Nothing -> Left $ InvalidAgeFormat s
        Just a | a < 0 -> Left $ NegativeAge a
               | otherwise -> Right a
```

### Example 3: Complex - Concurrent Processing

**Before (Clojure):**
```clojure
(require '[clojure.core.async :as async])

(defn fetch-user [id]
  (Thread/sleep 100)  ; Simulate network call
  {:id id :name (str "User-" id) :score (rand-int 100)})

(defn process-users [ids]
  (let [ch (async/chan)
        results (atom [])]
    ;; Spawn workers
    (doseq [id ids]
      (async/go
        (let [user (fetch-user id)]
          (async/>! ch user))))

    ;; Collect results
    (async/go-loop [remaining (count ids)]
      (when (pos? remaining)
        (let [user (async/<! ch)]
          (swap! results conj user)
          (recur (dec remaining)))))

    ;; Wait and return
    (Thread/sleep 500)
    (->> @results
         (sort-by :score)
         (reverse)
         (take 5))))

;; Usage
(process-users (range 20))
```

**After (Haskell):**
```haskell
import Control.Concurrent.Async
import Control.Concurrent (threadDelay)
import Data.List (sortBy)
import Data.Ord (Down(..), comparing)

data User = User
    { userId :: Int
    , userName :: String
    , userScore :: Int
    } deriving (Show, Eq)

fetchUser :: Int -> IO User
fetchUser uid = do
    threadDelay 100000  -- 0.1 seconds (microseconds)
    score <- randomRIO (0, 99)
    return $ User uid ("User-" ++ show uid) score

processUsers :: [Int] -> IO [User]
processUsers ids = do
    -- Spawn async tasks
    asyncUsers <- mapM (async . fetchUser) ids

    -- Wait for all results
    users <- mapM wait asyncUsers

    -- Sort by score (descending) and take top 5
    let topUsers = take 5 $ sortBy (comparing (Down . userScore)) users

    return topUsers

-- Usage
main :: IO ()
main = do
    topUsers <- processUsers [0..19]
    mapM_ print topUsers

-- Alternative with parallel processing
import Control.Parallel.Strategies

processUsersParallel :: [Int] -> IO [User]
processUsersParallel ids = do
    users <- mapM fetchUser ids
    let sorted = take 5 $ sortBy (comparing (Down . userScore)) users
    return sorted
```

**Why this translation:**
- Clojure's core.async go blocks → Haskell's async tasks
- Both provide concurrent execution
- Haskell's async library handles errors automatically
- Sorting and taking top N is identical pattern
- Type safety prevents many concurrency bugs at compile time

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `convert-elm-haskell` - Similar functional → Haskell conversion
- `lang-clojure-dev` - Clojure development patterns
- `lang-haskell-dev` - Haskell development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Async, channels, threads across languages
- `patterns-serialization-dev` - JSON, validation across languages
- `patterns-metaprogramming-dev` - Macros, Template Haskell across languages
