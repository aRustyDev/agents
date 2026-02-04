# LISP/Homoiconic Family

> Languages featuring homoiconicity (code as data), powerful macro systems, and dynamic typing.

## Overview

The LISP family descends from the original LISP (1958), one of the oldest programming language families:

- **Homoiconicity** - Code is represented as data structures (lists)
- **Macros** - Transform code at compile/read time
- **S-expressions** - Uniform syntax: `(operator operand1 operand2)`
- **Dynamic typing** - Runtime type checking
- **REPL-driven** - Interactive development central to workflow
- **Functional core** - First-class functions, closures

The uniform syntax enables unprecedented metaprogramming capabilities.

## Subtypes

| Subtype | Description | Languages |
|---------|-------------|-----------|
| **modern** | Contemporary dialects with modern tooling | Clojure, Racket |
| **classic** | Traditional implementations | Common Lisp, Scheme |

### Modern vs Classic Differences

| Aspect | Modern | Classic |
|--------|--------|---------|
| Ecosystem | Modern package managers | Varies |
| Data structures | Immutable (Clojure) | Mutable |
| Concurrency | Built-in (STM, core.async) | Library-based |
| Platform | JVM, JS, BEAM | Native, various |

## Key Characteristics

- **Code as data** - Programs are lists that can be manipulated
- **Powerful macros** - Extend language syntax
- **Minimal syntax** - Everything is an S-expression
- **Dynamic typing** - Types checked at runtime
- **REPL-centric** - Live coding, incremental development
- **Multiple paradigms** - Functional, imperative, OOP available
- **Garbage collected** - Automatic memory management

## Languages in Family

| Language | Subtype | Platform | Notes |
|----------|---------|----------|-------|
| Clojure | modern | JVM/JS/CLR | Immutable data, STM, rich ecosystem |
| Racket | modern | Native | Language-oriented programming |
| Common Lisp | classic | Native | ANSI standard, CLOS, conditions |
| Scheme | classic | Various | Minimalist, hygienic macros |
| Emacs Lisp | classic | Emacs | Editor scripting |

## Type System

### Dynamic Typing

- **Runtime checks** - Types verified during execution
- **No declarations required** - Variables untyped
- **Type predicates** - `number?`, `string?`, `list?`

### Optional Type Systems

| Language | Type System | Notes |
|----------|-------------|-------|
| Clojure | core.typed, Spec | Optional, gradual |
| Racket | Typed Racket | Gradual typing |
| Common Lisp | Declarations | Optimization hints |

### Common Type Patterns

```clojure
;; Clojure spec
(s/def ::name string?)
(s/def ::age pos-int?)
(s/def ::person (s/keys :req [::name ::age]))

;; Type predicates
(defn process [x]
  (cond
    (number? x) (inc x)
    (string? x) (str x "!")
    :else x))
```

## Memory Model

- **Garbage collected** - All LISP implementations use GC
- **Immutable (Clojure)** - Persistent data structures
- **Mutable (Classic)** - Traditional mutable cells
- **Cons cells** - Fundamental building block (pairs)

### Clojure Persistent Data Structures

| Structure | Characteristics |
|-----------|-----------------|
| Vector | Indexed, O(log32 n) access |
| Map | Hash array mapped trie |
| Set | Hash set |
| List | Linked list, O(1) prepend |

Structural sharing enables efficient "updates" without mutation.

## Concurrency Model

| Language | Primary Model |
|----------|---------------|
| Clojure | STM + Atoms + Agents + core.async |
| Racket | Places (processes) + Channels |
| Common Lisp | Threads (implementation-dependent) |
| Scheme | Varies by implementation |

### Clojure Concurrency Primitives

```clojure
;; Atom - uncoordinated synchronous
(def counter (atom 0))
(swap! counter inc)

;; Ref - coordinated synchronous (STM)
(def account (ref 100))
(dosync (alter account - 50))

;; Agent - uncoordinated asynchronous
(def logger (agent []))
(send logger conj "message")

;; core.async channels
(def ch (chan))
(go (>! ch "hello"))
(go (println (<! ch)))
```

## Common Patterns

### S-expression Syntax

```clojure
;; Everything is a list
(function arg1 arg2 arg3)

;; Nested expressions
(+ 1 (* 2 3))  ; => 7

;; Data literals
[1 2 3]        ; vector
{:a 1 :b 2}    ; map
#{1 2 3}       ; set
```

### Macros (Code as Data)

```clojure
;; Define a macro
(defmacro unless [condition & body]
  `(if (not ~condition)
     (do ~@body)))

;; Use it
(unless false
  (println "This runs"))
```

### Threading Macros (Clojure)

```clojure
;; Thread-first
(-> data
    (assoc :key value)
    (update :count inc)
    (dissoc :temp))

;; Thread-last
(->> numbers
     (filter even?)
     (map inc)
     (reduce +))
```

### Destructuring

```clojure
(let [{:keys [name age]} person
      [first & rest] items]
  ...)
```

## Conversion Considerations

### Converting FROM LISP

**What's easy to preserve:**

- Functional logic (maps, filters, reduces)
- Data transformations
- Recursive algorithms
- Higher-order functions

**What's hard to translate:**

- Macros → must expand first, lose abstraction
- Homoiconicity → no equivalent in most languages
- Reader macros → not portable
- `eval` → limited or unavailable
- REPL-driven code → needs restructuring
- Conditions/restarts (CL) → exception handling

**Common pitfalls:**

- Trying to translate macros literally
- Ignoring lazy sequence behavior (Clojure)
- Losing code-as-data patterns

**Semantic gaps:**

- LISP → ML-FP: 27 gaps (macro expansion, dynamic typing)
- LISP → any: Loss of homoiconicity

### Converting TO LISP

**What maps naturally:**

- Functional code → functional code
- Trees/nested structures → S-expressions
- Data processing → pipeline operations
- Closures → closures

**What requires restructuring:**

- Class hierarchies → protocols + records (Clojure) or CLOS (CL)
- Static types → removed or spec'd
- Mutable state → refs/atoms (Clojure) or special vars
- Exception handling → conditions (CL) or try/catch

**Idiomatic patterns to target:**

- Use threading macros for pipelines
- Leverage destructuring
- Prefer immutable data (Clojure)
- Use protocols for polymorphism
- Build DSLs with macros where appropriate

**Anti-patterns to avoid:**

- Over-using macros (functions suffice usually)
- Mutating data unnecessarily
- Ignoring lazy evaluation semantics
- Not using REPL for development

## Cross-References

### Phase 0 Pattern Clusters

- **Universal patterns**: bool, String, int, List (shared patterns)
- **Family-specific**: Macro patterns, S-expression syntax
- **Gap patterns**: 27 gaps LISP → ML-FP, 12 gaps LISP → BEAM

### Related convert-* Skills

- convert-clojure-fsharp (204 patterns)
- convert-python-clojure (189 patterns)
- convert-clojure-haskell (177 patterns)
- convert-clojure-scala (176 patterns)
- convert-clojure-roc (172 patterns)

## Sources

- [Clojure Documentation](https://clojure.org/reference)
- [Racket Documentation](https://docs.racket-lang.org/)
- [Common Lisp HyperSpec](http://www.lispworks.com/documentation/HyperSpec/)
- [Structure and Interpretation of Computer Programs](https://mitp-content-server.mit.edu/books/content/sectbyfn/books_pres_0/6515/sicp.zip/index.html)
- [The Joy of Clojure](https://www.manning.com/books/the-joy-of-clojure)

## See Also

- [ML-FP](ml-fp.md) - Common conversion target
- [Dynamic](dynamic.md) - Shares dynamic typing
- [Overview](overview.md) - Cross-family comparison matrices
