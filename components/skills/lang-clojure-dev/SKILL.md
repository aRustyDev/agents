---
name: lang-clojure-dev
description: Foundational Clojure patterns covering functional programming, REPL-driven development, immutable data structures, and idiomatic code. Use when writing Clojure code, working with sequences and lazy evaluation, understanding macros, or needing guidance on functional programming patterns. This is the entry point for Clojure development.
---

# Clojure Fundamentals

Foundational Clojure patterns and core language features. This skill serves as a reference for idiomatic Clojure development and functional programming practices.

## Overview

**This skill covers:**
- Core syntax (functions, data structures, special forms)
- Functional programming patterns
- REPL-driven development workflow
- Immutable data structures and persistent collections
- Sequence operations and lazy evaluation
- Destructuring and pattern matching
- Macros and metaprogramming basics
- Concurrency primitives (atoms, refs, agents)
- Java interop fundamentals

**This skill does NOT cover:**
- ClojureScript and web development - see `lang-clojurescript-dev`
- Specific frameworks (Ring, Compojure, etc.) - see framework-specific skills
- Build tooling (Leiningen, deps.edn) - see `lang-clojure-build-dev`
- Testing patterns - see `lang-clojure-testing-dev`

---

## Quick Reference

| Task | Pattern |
|------|---------|
| Define function | `(defn name [args] body)` |
| Anonymous function | `(fn [x] (* x x))` or `#(* % %)` |
| Create vector | `[1 2 3]` or `(vector 1 2 3)` |
| Create map | `{:key "value"}` or `(hash-map :key "value")` |
| Create set | `#{1 2 3}` or `(hash-set 1 2 3)` |
| Thread-first | `(-> x (f) (g))` = `(g (f x))` |
| Thread-last | `(->> coll (map f) (filter pred))` |
| Conditional | `(if test then else)` |
| Pattern match | `(case x 1 :one 2 :two :default)` |
| List comprehension | `(for [x coll] (transform x))` |

---

## Core Data Structures

### Lists

```clojure
;; Lists - linked lists, evaluated as function calls
'(1 2 3)          ; Quoted list (not evaluated)
(list 1 2 3)      ; Create list
(cons 0 '(1 2 3)) ; => (0 1 2 3)
(first '(1 2 3))  ; => 1
(rest '(1 2 3))   ; => (2 3)
(nth '(1 2 3) 1)  ; => 2
```

### Vectors

```clojure
;; Vectors - indexed access, grow at the end
[1 2 3]           ; Vector literal
(vector 1 2 3)    ; Create vector
(conj [1 2] 3)    ; => [1 2 3] (add to end)
(get [1 2 3] 1)   ; => 2
([1 2 3] 1)       ; => 2 (vectors are functions)
(assoc [1 2 3] 1 42) ; => [1 42 3]
(subvec [1 2 3 4 5] 1 4) ; => [2 3 4]
```

### Maps

```clojure
;; Maps - key-value pairs
{:name "Alice" :age 30}  ; Map literal
(hash-map :a 1 :b 2)     ; Create map
(get {:a 1} :a)          ; => 1
({:a 1} :a)              ; => 1 (maps are functions)
(:a {:a 1})              ; => 1 (keywords are functions)
(assoc {:a 1} :b 2)      ; => {:a 1 :b 2}
(dissoc {:a 1 :b 2} :b)  ; => {:a 1}
(update {:a 1} :a inc)   ; => {:a 2}
(merge {:a 1} {:b 2})    ; => {:a 1 :b 2}

;; Nested updates
(assoc-in {:user {:name "Alice"}} [:user :age] 30)
;; => {:user {:name "Alice" :age 30}}

(update-in {:user {:count 0}} [:user :count] inc)
;; => {:user {:count 1}}
```

### Sets

```clojure
;; Sets - unique elements
#{1 2 3}              ; Set literal
(hash-set 1 2 3)      ; Create set
(conj #{1 2} 3)       ; => #{1 2 3}
(disj #{1 2 3} 2)     ; => #{1 3}
(contains? #{1 2 3} 2) ; => true
(#{1 2 3} 2)          ; => 2 (sets are functions)

;; Set operations
(clojure.set/union #{1 2} #{2 3})        ; => #{1 2 3}
(clojure.set/intersection #{1 2} #{2 3}) ; => #{2}
(clojure.set/difference #{1 2} #{2 3})   ; => #{1}
```

---

## Functions

### Defining Functions

```clojure
;; Named function
(defn greet
  "Returns a greeting for the given name."
  [name]
  (str "Hello, " name "!"))

;; Multi-arity function
(defn greet
  ([] (greet "World"))
  ([name] (str "Hello, " name "!"))
  ([greeting name] (str greeting ", " name "!")))

;; Variadic function (variable arguments)
(defn sum [& numbers]
  (reduce + numbers))

(sum 1 2 3 4) ; => 10

;; Pre and post conditions
(defn divide [numerator denominator]
  {:pre [(not= denominator 0)]
   :post [(number? %)]}
  (/ numerator denominator))
```

### Anonymous Functions

```clojure
;; Full form
(fn [x] (* x x))

;; Short form
#(* % %)

;; Multiple arguments
#(+ %1 %2)

;; Using in higher-order functions
(map #(* % 2) [1 2 3]) ; => (2 4 6)
(filter #(> % 5) [3 7 2 8]) ; => (7 8)
```

### Function Composition

```clojure
;; comp - right to left composition
(def process (comp str inc))
(process 5) ; => "6"

;; partial - partial application
(def add5 (partial + 5))
(add5 10) ; => 15

;; complement - logical negation
(def not-empty? (complement empty?))
(not-empty? [1 2 3]) ; => true
```

---

## Sequence Operations

### Core Sequence Functions

```clojure
;; map - transform each element
(map inc [1 2 3]) ; => (2 3 4)
(map + [1 2 3] [10 20 30]) ; => (11 22 33)

;; filter - keep matching elements
(filter even? [1 2 3 4]) ; => (2 4)

;; remove - inverse of filter
(remove even? [1 2 3 4]) ; => (1 3)

;; reduce - accumulate
(reduce + [1 2 3 4]) ; => 10
(reduce + 100 [1 2 3]) ; => 106 (with initial value)

;; take / drop
(take 3 [1 2 3 4 5]) ; => (1 2 3)
(drop 2 [1 2 3 4 5]) ; => (3 4 5)

;; take-while / drop-while
(take-while #(< % 5) [1 2 6 7 3]) ; => (1 2)
(drop-while #(< % 5) [1 2 6 7 3]) ; => (6 7 3)
```

### Lazy Sequences

```clojure
;; Infinite sequences
(def naturals (iterate inc 0))
(take 5 naturals) ; => (0 1 2 3 4)

;; Lazy evaluation
(def evens (filter even? naturals))
(take 3 evens) ; => (0 2 4)

;; repeat
(take 3 (repeat "hi")) ; => ("hi" "hi" "hi")

;; cycle
(take 5 (cycle [1 2])) ; => (1 2 1 2 1)

;; range
(range 5)      ; => (0 1 2 3 4)
(range 2 7)    ; => (2 3 4 5 6)
(range 0 10 2) ; => (0 2 4 6 8)
```

### List Comprehension

```clojure
;; for - list comprehension
(for [x [1 2 3]]
  (* x x))
;; => (1 4 9)

;; Multiple bindings (cartesian product)
(for [x [1 2]
      y [3 4]]
  [x y])
;; => ([1 3] [1 4] [2 3] [2 4])

;; With :when (filter)
(for [x (range 10)
      :when (even? x)]
  x)
;; => (0 2 4 6 8)

;; With :let (local binding)
(for [x [1 2 3]
      :let [y (* x x)]]
  [x y])
;; => ([1 1] [2 4] [3 9])
```

---

## Destructuring

### Sequential Destructuring

```clojure
;; Vector destructuring
(let [[a b c] [1 2 3]]
  (+ a b c)) ; => 6

;; Rest binding
(let [[first & rest] [1 2 3 4]]
  rest) ; => (2 3 4)

;; Named arguments + rest
(let [[a b & more :as all] [1 2 3 4 5]]
  {:a a :b b :more more :all all})
;; => {:a 1 :b 2 :more (3 4 5) :all [1 2 3 4 5]}
```

### Associative Destructuring

```clojure
;; Map destructuring
(let [{name :name age :age} {:name "Alice" :age 30}]
  (str name " is " age)) ; => "Alice is 30"

;; Shorthand with :keys
(let [{:keys [name age]} {:name "Alice" :age 30}]
  (str name " is " age))

;; With defaults
(let [{:keys [name age] :or {age 0}} {:name "Bob"}]
  age) ; => 0

;; Nested destructuring
(let [{{{city :city} :address} :user}
      {:user {:address {:city "NYC"}}}]
  city) ; => "NYC"

;; Function arguments
(defn greet-person [{:keys [name age]}]
  (str "Hello " name ", you are " age))

(greet-person {:name "Alice" :age 30})
```

---

## Control Flow

### Conditionals

```clojure
;; if
(if (even? 4)
  "even"
  "odd") ; => "even"

;; if-not
(if-not (empty? [1 2 3])
  "has items"
  "empty") ; => "has items"

;; when (no else branch)
(when (pos? 5)
  (println "positive")
  "result") ; => "result"

;; when-not
(when-not (empty? [])
  "not empty") ; => nil

;; cond (multiple conditions)
(cond
  (< x 0) "negative"
  (> x 0) "positive"
  :else "zero")

;; condp (compare with predicate)
(condp = x
  1 "one"
  2 "two"
  3 "three"
  "other")

;; case (compile-time dispatch)
(case x
  1 "one"
  2 "two"
  "default")
```

### Nil Handling

```clojure
;; if-let (bind only if truthy)
(if-let [result (get {:a 1} :a)]
  (str "found: " result)
  "not found") ; => "found: 1"

;; when-let
(when-let [x (seq [1 2 3])]
  (first x)) ; => 1

;; some-> (thread-first, stop on nil)
(some-> {:a {:b 1}}
        :a
        :b
        inc) ; => 2

;; some->> (thread-last, stop on nil)
(some->> [1 2 3]
         (map inc)
         (filter even?)
         first) ; => 2

;; or (return first truthy value)
(or nil false 0 "result") ; => 0
```

---

## Threading Macros

```clojure
;; -> (thread-first)
(-> 5
    (+ 3)
    (* 2)
    (- 1)) ; => 15
;; Equivalent to: (- (* (+ 5 3) 2) 1)

;; ->> (thread-last)
(->> [1 2 3 4 5]
     (map inc)
     (filter even?)
     (reduce +)) ; => 12

;; as-> (thread with named argument)
(as-> 0 $
  (inc $)
  (+ 3 $)
  (* 2 $)) ; => 8

;; cond-> (conditional threading)
(cond-> []
  true (conj 1)
  (even? 2) (conj 2)
  false (conj 3)) ; => [1 2]

;; cond->> (conditional thread-last)
(cond->> [1 2 3]
  true (map inc)
  false (filter even?)) ; => (2 3 4)
```

---

## Namespaces and Requires

```clojure
;; Define namespace
(ns myapp.core
  "Application core namespace."
  (:require [clojure.string :as str]
            [clojure.set :as set]
            [myapp.util :refer [helper]]
            [myapp.config :refer :all]))

;; Refer specific functions
(:require [clojure.string :refer [upper-case lower-case]])

;; Import Java classes
(:import [java.util Date Calendar]
         [java.io File])

;; Using functions from required namespaces
(str/upper-case "hello") ; => "HELLO"
(set/union #{1 2} #{2 3}) ; => #{1 2 3}
```

---

## State Management

### Atoms

```clojure
;; Create atom
(def counter (atom 0))

;; Read value
@counter ; => 0

;; Update with swap!
(swap! counter inc) ; => 1
(swap! counter + 5) ; => 6

;; Set value with reset!
(reset! counter 0) ; => 0

;; Conditional update with compare-and-set!
(compare-and-set! counter 0 10) ; => true if current value is 0
```

### Refs (Coordinated, Synchronous)

```clojure
;; Create refs
(def account-a (ref 100))
(def account-b (ref 200))

;; Transaction with dosync
(dosync
  (alter account-a - 50)
  (alter account-b + 50))

;; Read consistent values
(dosync
  [@account-a @account-b]) ; => [50 250]

;; commute (optimistic update)
(dosync
  (commute account-a + 10))
```

### Agents (Asynchronous)

```clojure
;; Create agent
(def logger (agent []))

;; Send asynchronous update
(send logger conj "log entry 1")
(send logger conj "log entry 2")

;; Read value (may not be updated yet)
@logger

;; Wait for all actions to complete
(await logger)

;; send-off for blocking operations
(send-off logger
  (fn [logs]
    (Thread/sleep 1000)
    (conj logs "delayed entry")))
```

---

## Macros

### Using Macros

```clojure
;; Macros expand at compile time
;; Quote to prevent evaluation
'(+ 1 2) ; => (+ 1 2) (unevaluated list)

;; Common built-in macros
(when condition
  (do-thing-1)
  (do-thing-2))

(defn name [args] body) ; defn is a macro

(-> x f g h) ; threading macros are macros
```

### Defining Macros

```clojure
;; Simple macro
(defmacro unless [condition & body]
  `(if (not ~condition)
     (do ~@body)))

(unless false
  (println "This runs")
  "result") ; => "result"

;; Macro with syntax quote
(defmacro debug [expr]
  `(let [result# ~expr]
     (println '~expr "=>" result#)
     result#))

(debug (+ 1 2))
;; Prints: (+ 1 2) => 3
;; Returns: 3

;; Auto-gensym with #
(defmacro with-logging [& body]
  `(let [start# (System/currentTimeMillis)]
     (let [result# (do ~@body)]
       (println "Took" (- (System/currentTimeMillis) start#) "ms")
       result#)))
```

---

## Java Interop

```clojure
;; Create Java object
(new java.util.Date)
(java.util.Date.) ; Shorthand

;; Call instance method
(.toUpperCase "hello") ; => "HELLO"
(.substring "hello" 1 3) ; => "el"

;; Call static method
(Math/abs -5) ; => 5
(System/getProperty "java.version")

;; Access field
(.length "hello") ; => 5

;; Chain calls with ..
(.. "hello"
    (toUpperCase)
    (substring 0 3)) ; => "HEL"

;; doto (call multiple methods on same object)
(doto (java.util.HashMap.)
  (.put "a" 1)
  (.put "b" 2))
```

---

## REPL-Driven Development

### Workflow

```clojure
;; 1. Start REPL
;; lein repl or clj

;; 2. Load namespace
(require '[myapp.core :as core] :reload)

;; 3. Test function interactively
(core/my-function "test input")

;; 4. Inspect data
(pprint complex-data-structure)

;; 5. Check documentation
(doc map)
(source map)

;; 6. Find functions
(apropos "str")
(find-doc "sequence")

;; 7. Examine namespace
(dir clojure.string)
(ns-publics 'clojure.string)
```

### Common REPL Utilities

```clojure
;; Pretty print
(require '[clojure.pprint :refer [pprint]])
(pprint {:a 1 :b 2 :c {:d 3}})

;; Inspect Java classes
(require '[clojure.reflect :as r])
(r/reflect String)

;; Test assertions
(assert (= 4 (+ 2 2)))

;; Time execution
(time (reduce + (range 1000000)))
```

---

## Common Idioms

### Pipeline Processing

```clojure
;; Transform data through pipeline
(->> data
     (map parse-record)
     (filter valid?)
     (map transform)
     (group-by :category)
     (into (sorted-map)))
```

### Error Handling

```clojure
;; try/catch
(try
  (/ 1 0)
  (catch ArithmeticException e
    (println "Error:" (.getMessage e))
    nil)
  (finally
    (println "Cleanup")))

;; With custom exceptions
(try
  (when (invalid? data)
    (throw (ex-info "Invalid data"
                    {:data data :reason :validation})))
  (process data)
  (catch clojure.lang.ExceptionInfo e
    (let [{:keys [data reason]} (ex-data e)]
      (log/error "Failed:" reason))))
```

### Memoization

```clojure
;; Cache function results
(def fib
  (memoize
    (fn [n]
      (if (<= n 1)
        n
        (+ (fib (- n 1))
           (fib (- n 2)))))))

(fib 40) ; Fast after first call
```

### Transducers

```clojure
;; Composable algorithmic transformations
(def xf
  (comp
    (map inc)
    (filter even?)
    (take 5)))

;; Apply to different contexts
(sequence xf (range)) ; => (2 4 6 8 10)
(into [] xf (range))  ; => [2 4 6 8 10]
(transduce xf + (range)) ; => 30
```

---

## Troubleshooting

### Nil Pointer Exceptions

**Problem:** `NullPointerException` when calling methods

```clojure
(.toUpperCase nil) ; NullPointerException
```

**Fix:** Use nil-safe operations
```clojure
(some-> nil .toUpperCase) ; => nil
(when-let [s "hello"]
  (.toUpperCase s))
```

### Stack Overflow

**Problem:** Recursion without tail call optimization

```clojure
(defn sum [n]
  (if (zero? n)
    0
    (+ n (sum (dec n))))) ; Not tail recursive

(sum 10000) ; StackOverflowError
```

**Fix:** Use `recur` for tail recursion
```clojure
(defn sum [n]
  (loop [n n acc 0]
    (if (zero? n)
      acc
      (recur (dec n) (+ acc n)))))

;; Or use reduce
(defn sum [n]
  (reduce + (range (inc n))))
```

### Lazy Sequence Realization

**Problem:** Unexpected performance due to lazy evaluation

```clojure
;; This realizes the entire sequence multiple times
(let [nums (map expensive-fn (range 1000))]
  (+ (count nums) (first nums) (last nums)))
```

**Fix:** Force realization once with `doall` or `vec`
```clojure
(let [nums (vec (map expensive-fn (range 1000)))]
  (+ (count nums) (first nums) (last nums)))
```

### Keyword vs String Keys

**Problem:** Map lookup returns nil

```clojure
(get {"name" "Alice"} :name) ; => nil
```

**Fix:** Use consistent key types
```clojure
(get {:name "Alice"} :name) ; => "Alice"
;; Or convert
(keyword "name") ; => :name
```

---

## References

- [Clojure Documentation](https://clojure.org/reference/documentation)
- [ClojureDocs](https://clojuredocs.org/)
- [Clojure Style Guide](https://guide.clojure.style/)
- [Clojure Koans](http://clojurekoans.com/)
- [4Clojure Problems](http://www.4clojure.com/)
