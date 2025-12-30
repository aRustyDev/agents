---
name: convert-haskell-clojure
description: Convert Haskell code to idiomatic Clojure. Use when migrating Haskell projects to Clojure, translating pure functional patterns to practical functional JVM programming, or refactoring Haskell codebases to leverage REPL-driven development and dynamic typing. Extends meta-convert-dev with Haskell-to-Clojure specific patterns.
---

# Convert Haskell to Clojure

Convert Haskell code to idiomatic Clojure. This skill extends `meta-convert-dev` with Haskell-to-Clojure specific type mappings, idiom translations, and transformation strategies for moving from pure lazy functional programming with static types to practical dynamic functional programming on the JVM.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: Haskell static types (HM) → Clojure dynamic types
- **Idiom translations**: Type classes → protocols, monads → explicit threading, lazy → lazy seqs
- **Error handling**: Maybe/Either → nil/exceptions or tagged maps
- **Concurrency patterns**: STM/async → atoms/refs/agents, parallel → pmap/reducers
- **Evaluation strategy**: Lazy (default) → strict with explicit lazy seqs
- **REPL workflow**: GHCi → Clojure REPL-driven development
- **Effects**: IO monad → effects anywhere (with discipline)

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- Haskell language fundamentals - see `lang-haskell-dev`
- Clojure language fundamentals - see `lang-clojure-dev`
- Reverse conversion (Clojure → Haskell) - see `convert-clojure-haskell`
- Advanced type-level programming - Template Haskell, GADTs, Type Families have no direct equivalent

---

## Quick Reference

| Haskell | Clojure | Notes |
|---------|---------|-------|
| `String` or `Text` | `String` | Clojure strings are Java strings |
| `Int` / `Integer` | `Long` / `BigInteger` | Clojure uses Long by default |
| `Double` | `Double` | Java Double |
| `Bool` | `Boolean` | `true` / `false` |
| `Nothing` | `nil` | Represents absence |
| `Just x` | `x` | Value present (check with `some?`) |
| `[a]` | `[]` or `(list)` | Vector or list |
| `Map k v` | `{}` | Hash map |
| `Set a` | `#{}` | Hash set |
| `data T = ...` | `(defrecord T ...)` | Named types |
| `newtype` | No equivalent | Use plain value or `reify` |
| `type` | `(def T ...)` | Type alias |
| `f :: a -> b` | `(defn f [a] ...)` | Function (no type signature) |
| `\x -> ...` | `(fn [x] ...)` or `#(...)` | Lambda |
| `f . g` | `(comp f g)` | Function composition (reversed order) |
| `fmap` | `map` | Transform in context |
| `>>=` | `mapcat` or explicit chaining | Monadic bind |
| `do` notation | `let` or threading macros | Sequential operations |
| `Maybe a` | Value or `nil` | Optional values |
| `Either e a` | `{:ok val}` / `{:error e}` | Result type pattern |
| `IO a` | No equivalent | Effects anywhere |
| Type classes | Protocols | Polymorphism |
| `STM` | Refs with `dosync` | Software transactional memory |
| `async` | `future` / `pmap` | Async computation |

## When Converting Code

1. **Remove type signatures** - Clojure is dynamically typed
2. **Make laziness explicit** - Haskell lazy by default, Clojure strict by default
3. **Replace monads with idioms** - `Maybe` → nil checks, `Either` → tagged maps, `IO` → direct effects
4. **Convert type classes to protocols** - Or use multimethods for dynamic dispatch
5. **Embrace REPL workflow** - Test incrementally, explore data interactively
6. **Handle purity boundaries** - No IO monad; effects can happen anywhere (maintain discipline)
7. **Test equivalence** - Property-based testing with `test.check`

---

## Type System Mapping

### Primitive Types

| Haskell | Clojure | Notes |
|---------|---------|-------|
| `Int` | `Long` | 64-bit signed integer (default) |
| `Integer` | `BigInteger` | Arbitrary precision (use `N` suffix: `42N`) |
| `Float` | `Float` | 32-bit float (rare) |
| `Double` | `Double` | 64-bit float (default: `3.14`) |
| `Bool` | `Boolean` | `true` / `false` |
| `Char` | `Character` | Single character (rare, use strings) |
| `String` | `String` | Java String (immutable) |
| `Text` | `String` | Both map to Java String |
| `()` (unit) | `nil` | Void/no meaningful return |

### Collection Types

| Haskell | Clojure | Notes |
|---------|---------|-------|
| `[a]` (list) | `(list 1 2 3)` or `'(1 2 3)` | Linked list (rarely used) |
| `[a]` | `[1 2 3]` | **Preferred**: Vector (indexed access) |
| `Map k v` | `{:key val}` | Hash map (fast lookup) |
| `Set a` | `#{1 2 3}` | Hash set (unique elements) |
| `(a, b)` | `[a b]` | Tuple as vector |
| `(a, b, c)` | `[a b c]` | Multi-element tuple |
| Infinite list | Lazy seq: `(iterate inc 0)` | Must be explicit |

### Composite Types

| Haskell | Clojure | Notes |
|---------|---------|-------|
| `data User = User { name :: String, age :: Int }` | `(defrecord User [name age])` | Named record type |
| `type UserId = Int` | `(def UserId Long)` | Type alias (documentation only) |
| `newtype Email = Email String` | Plain string or custom validation | No compile-time wrapper |
| `data Color = Red \| Green \| Blue` | `#{:red :green :blue}` or spec | Enum as keyword set |
| `data Result a = Ok a \| Err String` | `{:ok val}` or `{:error msg}` | Tagged map pattern |

### Optional and Error Types

**Haskell:**
```haskell
-- Maybe for optional values
findUser :: UserId -> Maybe User
findUser uid = Map.lookup uid users

-- Either for errors
divide :: Double -> Double -> Either String Double
divide _ 0 = Left "Division by zero"
divide a b = Right (a / b)
```

**Clojure:**
```clojure
;; nil for optional values
(defn find-user [user-id]
  (get users user-id))  ; Returns nil if not found

;; Tagged maps for errors (idiomatic)
(defn divide [a b]
  (if (zero? b)
    {:error "Division by zero"}
    {:ok (/ a b)}))

;; Or throw exceptions
(defn divide! [a b]
  (when (zero? b)
    (throw (ex-info "Division by zero" {:a a :b b})))
  (/ a b))
```

**Why this translation:**
- Haskell's Maybe forces explicit handling; Clojure's nil is pervasive (less safe)
- Either → tagged maps is idiomatic Clojure for recoverable errors
- Exceptions are acceptable in Clojure for exceptional cases
- Use `ex-info` for exceptions with data

---

## Idiom Translation

### Pattern: Type Classes → Protocols

**Haskell:**
```haskell
-- Type class for serialization
class Serializable a where
  serialize :: a -> ByteString
  deserialize :: ByteString -> Maybe a

-- Instance for User
instance Serializable User where
  serialize (User name age) = encode (name, age)
  deserialize bs = case decode bs of
    Just (name, age) -> Just (User name age)
    Nothing -> Nothing

-- Use
let json = serialize user
```

**Clojure:**
```clojure
;; Protocol for serialization
(defprotocol Serializable
  (serialize [this])
  (deserialize [this bytes]))

;; Extend for User record
(defrecord User [name age])

(extend-protocol Serializable
  User
  (serialize [user]
    (json/generate-string user))
  (deserialize [_ bytes]
    (json/parse-string bytes true)))

;; Or inline with defrecord
(defrecord User [name age]
  Serializable
  (serialize [this]
    (json/generate-string this)))

;; Use
(serialize user)
```

**Why this translation:**
- Type classes define polymorphic interfaces; protocols do the same in Clojure
- Protocols are more dynamic: can extend existing types at runtime
- No compile-time type checking in Clojure
- `extend-protocol` extends multiple types at once

### Pattern: Monadic Do-Notation → Threading Macros

**Haskell:**
```haskell
-- Maybe monad chaining
processUser :: UserId -> Maybe Result
processUser uid = do
  user <- findUser uid
  profile <- getProfile user
  settings <- getSettings profile
  return (computeResult settings)

-- Or with bind
processUser' uid =
  findUser uid >>= getProfile >>= getSettings >>= return . computeResult
```

**Clojure:**
```clojure
;; Using some-> (thread-first, stop on nil)
(defn process-user [user-id]
  (some-> user-id
          find-user
          get-profile
          get-settings
          compute-result))

;; Or with when-let for explicit nil handling
(defn process-user [user-id]
  (when-let [user (find-user user-id)]
    (when-let [profile (get-profile user)]
      (when-let [settings (get-settings profile)]
        (compute-result settings)))))

;; Or using monads library (cats, algo.monads)
(require '[cats.core :as m])
(require '[cats.monad.maybe :as maybe])

(defn process-user [user-id]
  (m/mlet [user (maybe/maybe (find-user user-id))
           profile (maybe/maybe (get-profile user))
           settings (maybe/maybe (get-settings profile))]
    (m/return (compute-result settings))))
```

**Why this translation:**
- `some->` is idiomatic Clojure for Maybe-like chaining
- Stops threading at first nil
- For complex error handling, tagged maps or exceptions are more common
- Monads library exists but not idiomatic for most Clojure code

### Pattern: Function Composition

**Haskell:**
```haskell
-- Right-to-left composition
processData :: [Int] -> Int
processData = sum . filter even . map (*2)

-- Or with $
processData' xs = sum $ filter even $ map (*2) xs

-- Or with &
import Data.Function ((&))
processData'' xs =
  xs
  & map (*2)
  & filter even
  & sum
```

**Clojure:**
```clojure
;; Thread-last (->>), left-to-right
(defn process-data [xs]
  (->> xs
       (map #(* % 2))
       (filter even?)
       (reduce +)))

;; Or comp (right-to-left like Haskell)
(def process-data
  (comp
    #(reduce + %)
    #(filter even? %)
    #(map (fn [x] (* x 2)) %)))

;; But ->> is more idiomatic
```

**Why this translation:**
- Haskell's `.` composes right-to-left: `(f . g . h) x = f (g (h x))`
- Clojure's `comp` also composes right-to-left
- But `->>` (thread-last) is more idiomatic and reads left-to-right
- Use `->>` for data transformations

### Pattern: Pattern Matching

**Haskell:**
```haskell
-- Pattern matching on ADT
data Shape = Circle Double
           | Rectangle Double Double
           | Triangle Double Double Double

area :: Shape -> Double
area (Circle r) = pi * r * r
area (Rectangle w h) = w * h
area (Triangle a b c) =
  let s = (a + b + c) / 2
  in sqrt (s * (s - a) * (s - b) * (s - c))

-- Pattern matching on lists
sumList :: [Int] -> Int
sumList [] = 0
sumList (x:xs) = x + sumList xs
```

**Clojure:**
```clojure
;; Use maps with :type key for tagged unions
(defn area [shape]
  (case (:type shape)
    :circle (let [{:keys [radius]} shape]
              (* Math/PI radius radius))
    :rectangle (let [{:keys [width height]} shape]
                 (* width height))
    :triangle (let [{:keys [a b c]} shape
                    s (/ (+ a b c) 2)]
                (Math/sqrt (* s (- s a) (- s b) (- s c))))))

;; Or use multimethods for polymorphism
(defmulti area :type)

(defmethod area :circle [{:keys [radius]}]
  (* Math/PI radius radius))

(defmethod area :rectangle [{:keys [width height]}]
  (* width height))

(defmethod area :triangle [{:keys [a b c]}]
  (let [s (/ (+ a b c) 2)]
    (Math/sqrt (* s (- s a) (- s b) (- s c)))))

;; Pattern matching on lists
(defn sum-list [xs]
  (if (empty? xs)
    0
    (+ (first xs) (sum-list (rest xs)))))

;; Or idiomatic reduce
(defn sum-list [xs]
  (reduce + 0 xs))
```

**Why this translation:**
- Haskell has first-class ADTs; Clojure uses maps with `:type` keys
- `case` on type tag for simple dispatch
- Multimethods for extensible polymorphism
- Pattern matching on lists uses `first`/`rest` instead of `:`
- Prefer higher-order functions (reduce, map) over explicit recursion

### Pattern: Lazy Evaluation

**Haskell:**
```haskell
-- Lazy by default
naturals :: [Integer]
naturals = [0..]  -- Infinite list, no problem

fibs :: [Integer]
fibs = 0 : 1 : zipWith (+) fibs (tail fibs)

-- Take only what you need
take 10 fibs  -- [0,1,1,2,3,5,8,13,21,34]
```

**Clojure:**
```clojure
;; Strict by default, lazy sequences explicit
(def naturals (iterate inc 0))  ; Lazy seq

(def fibs
  (map first (iterate (fn [[a b]] [b (+ a b)]) [0 1])))

;; Or using lazy-seq
(defn fib-seq
  ([] (fib-seq 0 1))
  ([a b]
   (lazy-seq (cons a (fib-seq b (+ a b))))))

(take 10 fibs)  ; (0 1 1 2 3 5 8 13 21 34)

;; Force realization with doall
(doall (take 10 fibs))  ; Realizes all elements
```

**Why this translation:**
- Haskell: lazy by default, force with `seq` / `deepseq` / bang patterns
- Clojure: strict by default, lazy with `lazy-seq`, `iterate`, `repeat`, `cycle`
- Use `iterate` for infinite sequences
- Use `take` to consume only what's needed
- `doall` forces realization (opposite of Haskell's forcing strictness)

### Pattern: List Comprehensions

**Haskell:**
```haskell
-- List comprehension with guards
pythagorean :: Int -> [(Int, Int, Int)]
pythagorean n = [(a, b, c) | a <- [1..n],
                             b <- [a..n],
                             c <- [b..n],
                             a^2 + b^2 == c^2]
```

**Clojure:**
```clojure
;; for comprehension
(defn pythagorean [n]
  (for [a (range 1 (inc n))
        b (range a (inc n))
        c (range b (inc n))
        :when (= (+ (* a a) (* b b)) (* c c))]
    [a b c]))
```

**Why this translation:**
- Syntax is very similar
- Haskell uses `|`, Clojure uses `:when` for filters
- Generators bind with `<-` in Haskell, bind directly in Clojure
- Both support multiple generators and filters

---

## Error Handling

### Maybe → Nil

**Haskell:**
```haskell
safeHead :: [a] -> Maybe a
safeHead [] = Nothing
safeHead (x:_) = Just x

-- Use with pattern matching
case safeHead xs of
  Nothing -> defaultValue
  Just x -> processValue x

-- Or with maybe function
maybe defaultValue processValue (safeHead xs)
```

**Clojure:**
```clojure
(defn safe-head [xs]
  (first xs))  ; Returns nil for empty

;; Use with if-let
(if-let [x (safe-head xs)]
  (process-value x)
  default-value)

;; Or with some-> (nil-safe threading)
(some-> xs safe-head process-value)

;; Or with or for default
(or (safe-head xs) default-value)
```

**Why this translation:**
- Haskell forces explicit handling with Maybe
- Clojure uses nil pervasively (less safe but more convenient)
- `if-let`, `when-let`, `some->` provide nil-safe operations
- Use `or` for default values

### Either → Tagged Maps or Exceptions

**Haskell:**
```haskell
parseAge :: String -> Either String Int
parseAge s = case reads s of
  [(n, "")] | n >= 0 -> Right n
  _ -> Left "Invalid age"

-- Chain with do-notation
validateUser :: UserData -> Either String User
validateUser userData = do
  age <- parseAge (ageString userData)
  email <- validateEmail (emailString userData)
  return (User (userName userData) age email)
```

**Clojure:**
```clojure
;; Tagged maps (idiomatic for recoverable errors)
(defn parse-age [s]
  (try
    (let [n (Long/parseLong s)]
      (if (>= n 0)
        {:ok n}
        {:error "Age must be non-negative"}))
    (catch NumberFormatException _
      {:error "Not a valid number"})))

;; Chain with helper
(defn ok? [result]
  (contains? result :ok))

(defn validate-user [user-data]
  (let [age-result (parse-age (:age user-data))]
    (if (ok? age-result)
      (let [email-result (validate-email (:email user-data))]
        (if (ok? email-result)
          {:ok {:name (:name user-data)
                :age (:ok age-result)
                :email (:ok email-result)}}
          email-result))
      age-result)))

;; Or exceptions (idiomatic for unrecoverable errors)
(defn parse-age! [s]
  (let [n (Long/parseLong s)]  ; Throws on invalid
    (when (< n 0)
      (throw (ex-info "Age must be non-negative" {:age n})))
    n))
```

**Why this translation:**
- Either forces error handling; Clojure uses tagged maps or exceptions
- Tagged maps `{:ok val}` / `{:error msg}` are common for recoverable errors
- Exceptions are acceptable for programming errors or exceptional conditions
- No monadic chaining; use explicit conditionals or helper macros

---

## Concurrency Patterns

### STM → Refs with dosync

**Haskell:**
```haskell
import Control.Concurrent.STM

type Account = TVar Int

transfer :: Account -> Account -> Int -> STM ()
transfer from to amount = do
  fromBalance <- readTVar from
  when (fromBalance < amount) retry
  modifyTVar from (subtract amount)
  modifyTVar to (+ amount)

-- Run transaction
main = do
  account1 <- newTVarIO 1000
  account2 <- newTVarIO 0
  atomically $ transfer account1 account2 500
```

**Clojure:**
```clojure
;; Refs for coordinated, synchronous updates
(def account1 (ref 1000))
(def account2 (ref 0))

(defn transfer [from to amount]
  (dosync
    (let [from-balance @from]
      (when (< from-balance amount)
        (throw (ex-info "Insufficient funds" {})))
      (alter from - amount)
      (alter to + amount))))

;; Use
(transfer account1 account2 500)
;; Or with commute for non-order-dependent updates
(dosync
  (commute account1 - 500)
  (commute account2 + 500))
```

**Why this translation:**
- Both use software transactional memory
- Haskell: `TVar` with `atomically`, `readTVar`, `modifyTVar`, `retry`
- Clojure: `ref` with `dosync`, `@` (deref), `alter`, `commute`
- Haskell's `retry` blocks until condition met; Clojure uses explicit checks

### Async → Future / Pmap

**Haskell:**
```haskell
import Control.Concurrent.Async

main = do
  (result1, result2) <- concurrently
    (fetchUrl "http://example.com/1")
    (fetchUrl "http://example.com/2")
  print (result1, result2)

-- Race: first to complete wins
winner <- race
  (fetchFromServer1 key)
  (fetchFromServer2 key)
```

**Clojure:**
```clojure
;; future for async execution
(let [result1 (future (fetch-url "http://example.com/1"))
      result2 (future (fetch-url "http://example.com/2"))]
  (println [@result1 @result2]))  ; @ blocks until ready

;; pmap for parallel map
(def results
  (pmap fetch-url ["http://example.com/1"
                   "http://example.com/2"]))

;; No built-in race; use promises
(defn race [& fns]
  (let [p (promise)]
    (doseq [f fns]
      (future (deliver p (f))))
    @p))

(race #(fetch-from-server1 key)
      #(fetch-from-server2 key))
```

**Why this translation:**
- Haskell `async` library → Clojure `future`
- `concurrently` → spawn futures, deref all
- `race` → promise with multiple futures (first delivery wins)
- `mapConcurrently` → `pmap` (parallel map)

---

## Metaprogramming

### Template Haskell → Macros

**Haskell:**
```haskell
{-# LANGUAGE TemplateHaskell #-}

import Language.Haskell.TH

-- Generate function at compile time
$(do
    let name = mkName "add5"
    let body = [| \x -> x + 5 |]
    [d| $(varP name) = $body |]
 )

-- Use
result = add5 10  -- 15
```

**Clojure:**
```clojure
;; Macros expand at compile time
(defmacro add-n [n]
  `(fn [x#] (+ x# ~n)))

(def add5 (add-n 5))
(add5 10)  ; => 15

;; Or simpler: just generate code
(defmacro defadder [name n]
  `(defn ~name [x#]
     (+ x# ~n)))

(defadder add5 5)
(add5 10)  ; => 15
```

**Why this translation:**
- Both provide compile-time code generation
- Template Haskell is more powerful but complex
- Clojure macros are simpler, more accessible
- Quote/unquote syntax: `` ` `` (quote), `~` (unquote), `~@` (unquote-splice)
- Auto-gensym with `#`: `x#` generates unique symbol

---

## Serialization

### Aeson → Cheshire/Transit

**Haskell:**
```haskell
{-# LANGUAGE DeriveGeneric #-}

import Data.Aeson
import GHC.Generics

data User = User
  { name :: Text
  , email :: Text
  , age :: Int
  } deriving (Generic, Show)

instance FromJSON User
instance ToJSON User

-- Encode/decode
encodeUser :: User -> ByteString
encodeUser = encode

decodeUser :: ByteString -> Maybe User
decodeUser = decode
```

**Clojure:**
```clojure
;; Using Cheshire for JSON
(require '[cheshire.core :as json])

;; Records for structured data
(defrecord User [name email age])

;; Encode
(defn encode-user [user]
  (json/generate-string user))

;; Decode
(defn decode-user [json-str]
  (json/parse-string json-str true))  ; true = keywordize keys

;; Or use Transit for Clojure types
(require '[cognitect.transit :as transit])
(import '[java.io ByteArrayOutputStream ByteArrayInputStream])

(defn to-transit [data]
  (let [out (ByteArrayOutputStream.)]
    (transit/write (transit/writer out :json) data)
    (.toString out)))

(defn from-transit [s]
  (transit/read
    (transit/reader
      (ByteArrayInputStream. (.getBytes s))
      :json)))
```

**Why this translation:**
- Haskell Aeson uses Generic deriving; Clojure uses runtime serialization
- Cheshire for JSON (most common)
- Transit preserves Clojure data types (keywords, sets, etc.)
- No compile-time validation in Clojure

---

## Build and Dependencies

### Cabal/Stack → Leiningen/tools.deps

**Haskell (Cabal):**
```cabal
name:          my-app
version:       0.1.0.0
build-depends: base >= 4.14 && < 5
             , text >= 1.2
             , aeson >= 2.0
             , containers

library
  exposed-modules: MyApp
  hs-source-dirs:  src
```

**Haskell (Stack):**
```yaml
resolver: lts-21.0
packages: [.]
extra-deps:
  - some-package-1.0.0
```

**Clojure (Leiningen):**
```clojure
(defproject my-app "0.1.0-SNAPSHOT"
  :dependencies [[org.clojure/clojure "1.11.1"]
                 [cheshire "5.12.0"]
                 [org.clojure/data.json "2.4.0"]])
```

**Clojure (tools.deps):**
```clojure
{:deps
 {org.clojure/clojure {:mvn/version "1.11.1"}
  cheshire/cheshire {:mvn/version "5.12.0"}}}
```

**Why this translation:**
- Cabal/Stack manage packages and versions; Leiningen/tools.deps do the same
- Dependencies from Maven Central (Clojure) vs Hackage/Stackage (Haskell)
- Both support local dependencies and git dependencies

---

## Testing

### QuickCheck → test.check

**Haskell:**
```haskell
import Test.QuickCheck

-- Property: reversing twice gives original
prop_reverse_involutive :: [Int] -> Bool
prop_reverse_involutive xs = reverse (reverse xs) == xs

-- Property: sorted list is sorted
prop_sort_sorted :: [Int] -> Bool
prop_sort_sorted xs = isSorted (sort xs)

-- Run
main = do
  quickCheck prop_reverse_involutive
  quickCheck prop_sort_sorted
```

**Clojure:**
```clojure
(ns myapp.props-test
  (:require [clojure.test :refer [deftest is]]
            [clojure.test.check :as tc]
            [clojure.test.check.generators :as gen]
            [clojure.test.check.properties :as prop]
            [clojure.test.check.clojure-test :refer [defspec]]))

;; Property: reversing twice gives original
(defspec reverse-involutive 100
  (prop/for-all [v (gen/vector gen/small-integer)]
    (= v (vec (reverse (reverse v))))))

;; Property: sorted output
(defspec sort-produces-sorted 100
  (prop/for-all [v (gen/vector gen/small-integer)]
    (let [sorted (sort v)]
      (every? (fn [[a b]] (<= a b))
              (partition 2 1 sorted)))))
```

**Why this translation:**
- Both are property-based testing libraries
- QuickCheck → test.check (same concepts)
- `quickCheck` → `defspec` or `tc/quick-check`
- `Arbitrary` generators → `gen/` generators
- `forAll` → `prop/for-all`

---

## Common Pitfalls

### 1. Assuming Static Type Safety

```clojure
;; ❌ No compile-time type errors
(defn add [a b]
  (+ a b))

(add "hello" "world")  ; Runtime error!
```

**Fix:** Use spec for runtime validation
```clojure
(require '[clojure.spec.alpha :as s])

(s/def ::number number?)
(defn add [a b]
  {:pre [(s/valid? ::number a) (s/valid? ::number b)]}
  (+ a b))
```

### 2. Not Handling Nil Explicitly

```clojure
;; ❌ Nil is not checked at compile time
(defn process [data]
  (.toUpperCase (:name data)))  ; NullPointerException if :name is nil
```

**Fix:** Use nil-safe operations
```clojure
(defn process [data]
  (some-> data :name .toUpperCase))

;; Or explicit check
(defn process [data]
  (when-let [name (:name data)]
    (.toUpperCase name)))
```

### 3. Forgetting Lazy Evaluation Differences

```clojure
;; ❌ This realizes the entire sequence multiple times
(let [nums (map expensive-fn (range 1000))]
  (+ (count nums) (first nums) (last nums)))
```

**Fix:** Force realization once
```clojure
(let [nums (vec (map expensive-fn (range 1000)))]
  (+ (count nums) (first nums) (last nums)))
```

### 4. Over-using Exceptions vs. Tagged Maps

```clojure
;; ❌ Exceptions for control flow
(try
  (divide a b)
  (catch ArithmeticException e
    :division-by-zero))
```

**Fix:** Use tagged maps for expected errors
```clojure
(let [result (divide a b)]
  (if (:error result)
    (handle-error result)
    (handle-success (:ok result))))
```

### 5. Not Leveraging REPL-Driven Development

```clojure
;; ❌ Writing entire function without testing
(defn complex-algorithm [data]
  ;; 50 lines of code
  )
```

**Fix:** Build incrementally in REPL
```clojure
;; In REPL:
(def sample-data {...})

;; Step 1
(def step1 (parse-data sample-data))
;; Inspect step1

;; Step 2
(def step2 (transform step1))
;; Inspect step2

;; Combine into function after validation
(defn complex-algorithm [data]
  (-> data parse-data transform))
```

---

## Tooling

| Category | Haskell | Clojure | Notes |
|----------|---------|---------|-------|
| Build tool | Cabal, Stack | Leiningen, tools.deps | Package management |
| REPL | GHCi | `lein repl`, `clj` | Interactive development |
| Package registry | Hackage, Stackage | Clojars, Maven Central | Dependency sources |
| Testing | HSpec, QuickCheck | clojure.test, test.check | Unit + property-based |
| Linting | HLint | clj-kondo, eastwood | Static analysis |
| Formatter | Ormolu, Brittany | cljfmt, zprint | Code formatting |
| Doc generation | Haddock | Codox | API documentation |

---

## Examples

### Example 1: Simple - Function with Pattern Matching

**Before (Haskell):**
```haskell
-- Factorial with pattern matching
factorial :: Integer -> Integer
factorial 0 = 1
factorial n = n * factorial (n - 1)
```

**After (Clojure):**
```clojure
;; Factorial with cond
(defn factorial [n]
  (if (zero? n)
    1
    (* n (factorial (dec n)))))

;; Or with recur for tail recursion
(defn factorial [n]
  (loop [n n acc 1]
    (if (zero? n)
      acc
      (recur (dec n) (* acc n)))))
```

### Example 2: Medium - Map Transformation with Maybe

**Before (Haskell):**
```haskell
import Data.Maybe (mapMaybe)
import qualified Data.Map as Map

-- Extract emails from user map, filtering out Nothing
getEmails :: Map.Map UserId User -> [Email]
getEmails users =
  mapMaybe (userEmail . snd) (Map.toList users)

userEmail :: User -> Maybe Email
userEmail (User _ email _) = email
```

**After (Clojure):**
```clojure
;; Extract emails, filtering out nil
(defn get-emails [users]
  (->> users
       vals
       (map :email)
       (filter some?)))

;; Or with keep (map + filter non-nil in one step)
(defn get-emails [users]
  (keep :email (vals users)))
```

### Example 3: Complex - Concurrent Processing with STM

**Before (Haskell):**
```haskell
import Control.Concurrent.STM
import Control.Concurrent.Async
import qualified Data.Map as Map

type Cache = TVar (Map.Map Key Value)

-- Concurrent cache operations
updateCache :: Cache -> Key -> Value -> STM ()
updateCache cache key value = do
  m <- readTVar cache
  writeTVar cache (Map.insert key value m)

lookupCache :: Cache -> Key -> STM (Maybe Value)
lookupCache cache key = do
  m <- readTVar cache
  return (Map.lookup key m)

-- Process items concurrently and update cache
processItems :: Cache -> [Item] -> IO ()
processItems cache items = do
  results <- mapConcurrently processItem items
  atomically $ mapM_ (uncurry (updateCache cache)) results

processItem :: Item -> IO (Key, Value)
processItem item = do
  value <- expensiveComputation item
  return (itemKey item, value)
```

**After (Clojure):**
```clojure
;; Using refs for coordinated updates
(def cache (ref {}))

;; Concurrent cache operations
(defn update-cache! [cache key value]
  (dosync
    (alter cache assoc key value)))

(defn lookup-cache [cache key]
  (dosync
    (get @cache key)))

;; Process items concurrently and update cache
(defn process-items! [cache items]
  (let [results (pmap process-item items)]
    (dosync
      (doseq [[k v] results]
        (alter cache assoc k v)))))

(defn process-item [item]
  (let [value (expensive-computation item)]
    [(:key item) value]))

;; Or using atoms for independent updates (simpler)
(def cache-atom (atom {}))

(defn update-cache-atom! [cache key value]
  (swap! cache assoc key value))

(defn process-items-atom! [cache items]
  (doseq [item (pmap process-item items)]
    (let [[k v] item]
      (swap! cache assoc k v))))
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)
- `convert-clojure-haskell` - Reverse conversion (Clojure → Haskell)
- `lang-haskell-dev` - Haskell language fundamentals
- `lang-clojure-dev` - Clojure language fundamentals

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Concurrency patterns across languages (STM, async, actors)
- `patterns-serialization-dev` - Serialization patterns across languages (JSON, validation)
- `patterns-metaprogramming-dev` - Metaprogramming across languages (macros, Template Haskell)
