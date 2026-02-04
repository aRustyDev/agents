# Clojure

> Modern Lisp dialect emphasizing functional programming, immutability, and interactive development on the JVM.

## Overview

Clojure is a dynamic, functional programming language created by Rich Hickey and first released in 2007. It's a modern dialect of Lisp that runs on the Java Virtual Machine (JVM), JavaScript engines (ClojureScript), and .NET (ClojureCLR).

Clojure emphasizes immutability, persistent data structures, and a functional programming style while providing seamless Java interoperability. Its homoiconic nature (code as data) enables powerful metaprogramming through macros.

The language excels in data processing, concurrent programming, and domains requiring exploratory development. Its REPL-driven development style and focus on simplicity have influenced many modern languages and frameworks.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | LISP | Code as data, macros |
| Secondary Family | FP | Functional, immutable |
| Subtype | modern-lisp | JVM-based, STM concurrency |

See: [LISP Family](../language-families/lisp.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| 1.0 | 2009-05 | Initial stable release |
| 1.5 | 2013-03 | Reducers |
| 1.7 | 2015-06 | Transducers, reader conditionals |
| 1.9 | 2017-12 | spec library |
| 1.10 | 2018-12 | Error messages, prepl |
| 1.11 | 2022-03 | Iteration, clojure.math |
| 1.12 | 2024-02 | Method values, array class literals |

## Feature Profile

### Type System

- **Strength:** dynamic (runtime typing)
- **Inference:** none (optional type hints for performance)
- **Generics:** runtime (duck typing)
- **Nullability:** nullable (nil is a value)

### Memory Model

- **Management:** gc (JVM garbage collection)
- **Mutability:** default-immutable (refs, atoms, agents for state)
- **Allocation:** persistent data structures (structural sharing)
- **Concurrency:** STM (Software Transactional Memory)

### Control Flow

- **Structured:** if, cond, case, when, loop/recur
- **Effects:** exceptions (can use monadic style)
- **Async:** core.async (CSP channels), futures, agents

### Data Types

- **Primitives:** numbers, strings, characters, keywords, symbols, booleans, nil
- **Composites:** lists, vectors, maps, sets
- **Collections:** persistent (structural sharing), lazy sequences
- **Abstraction:** protocols, multimethods, namespaces

### Metaprogramming

- **Macros:** first-class (code as data, quasiquoting)
- **Reflection:** runtime (JVM reflection)
- **Code generation:** macros, eval

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | Leiningen, deps.edn | deps.edn is modern |
| Build System | Leiningen, tools.deps | Clojure CLI |
| LSP | clojure-lsp | Good support |
| Formatter | cljfmt, zprint | zprint is configurable |
| Linter | clj-kondo | Excellent |
| REPL | built-in | Core development tool |
| Test Framework | clojure.test | Built-in |

## Syntax Patterns

```clojure
;; Function definition
(defn greet
  "Greets a person the specified number of times."
  [name times]
  (apply str (repeat times (str "Hello, " name "! "))))

;; Multiple arities
(defn greet
  ([name] (greet name 1))
  ([name times] (apply str (repeat times (str "Hello, " name "! ")))))

;; Anonymous function
(fn [x] (* x 2))
#(* % 2)  ; reader macro shorthand

;; Data structures
(def user {:id "1" :name "Alice" :email nil})

;; Accessing data
(:name user)  ; => "Alice"
(get user :email "default@example.com")  ; => "default@example.com"

;; Updating immutable data
(assoc user :email "alice@example.com")
(update user :name clojure.string/upper-case)

;; Record definition
(defrecord User [id name email])

(def alice (->User "1" "Alice" nil))
(def alice (map->User {:id "1" :name "Alice"}))

;; Protocol definition (type class equivalent)
(defprotocol Stringify
  (to-string [this]))

(extend-protocol Stringify
  User
  (to-string [user] (str "User(" (:name user) ")"))

  String
  (to-string [s] s))

;; Multimethod (ad-hoc polymorphism)
(defmulti area :shape)

(defmethod area :circle [{:keys [radius]}]
  (* Math/PI radius radius))

(defmethod area :rectangle [{:keys [width height]}]
  (* width height))

(area {:shape :circle :radius 5})

;; Threading macros (pipeline)
(-> data
    (filter pos?)
    (map #(* % 2))
    (reduce +))

(->> numbers
     (filter even?)
     (map #(* % 2))
     (reduce +))

;; Let binding with destructuring
(let [{:keys [name email] :or {email "unknown"}} user]
  (println name email))

;; Pattern matching (with core.match)
(require '[clojure.core.match :refer [match]])

(match [x]
  [{:shape :circle :radius r}] (* Math/PI r r)
  [{:shape :rectangle :width w :height h}] (* w h)
  :else nil)

;; Error handling
(try
  (/ 1 0)
  (catch ArithmeticException e
    {:error :division-by-zero})
  (finally
    (println "cleanup")))

;; Atom for managed state
(def counter (atom 0))
(swap! counter inc)
@counter  ; deref to read

;; Lazy sequence
(def fibs
  (lazy-seq
    (cons 0 (cons 1 (map + fibs (rest fibs))))))

(take 10 fibs)

;; Transducer
(def xf (comp (filter odd?) (map inc)))
(transduce xf + [1 2 3 4 5])

;; core.async (CSP)
(require '[clojure.core.async :as async])

(let [ch (async/chan)]
  (async/go
    (async/>! ch "hello"))
  (async/go
    (println (async/<! ch))))

;; Spec for validation
(require '[clojure.spec.alpha :as s])

(s/def ::name string?)
(s/def ::age pos-int?)
(s/def ::user (s/keys :req-un [::name ::age]))

(s/valid? ::user {:name "Alice" :age 30})

;; Macro definition
(defmacro unless [pred then else]
  `(if (not ~pred) ~then ~else))
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| No static types | moderate | Use spec, Schema, or Typed Clojure |
| JVM startup time | moderate | Use GraalVM native-image, keep REPL running |
| Stack not tail-call optimized | minor | Use loop/recur, trampoline |
| Parentheses can be intimidating | minor | Use structural editing (paredit) |
| No pattern matching built-in | minor | Use core.match library |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 7 | clojure-elixir, clojure-elm, clojure-erlang, clojure-fsharp, clojure-haskell, clojure-roc, clojure-scala |
| As Target | 1 | python-clojure |

**Note:** Common source language for FP conversions. Homoiconicity and macros may not translate directly.

## Idiomatic Patterns

### Persistent Data → Immutable Collections

```clojure
;; Clojure: persistent data structure
(def v [1 2 3])
(def v2 (conj v 4))  ; v unchanged, v2 is [1 2 3 4]

;; IR equivalent: immutable with structural sharing
;; let v2 = v.push(4);  // v unchanged
```

### Protocols → Type Classes

```clojure
;; Clojure: protocol
(defprotocol Show
  (show [this]))

;; IR equivalent: type class
;; trait Show { fn show(&self) -> String }
```

### Threading Macros → Pipeline

```clojure
;; Clojure: thread-first
(-> x f g h)

;; IR equivalent: pipeline or composition
;; h(g(f(x))) OR x |> f |> g |> h
```

### Atoms → Managed State

```clojure
;; Clojure: atom
(def state (atom {}))
(swap! state assoc :key value)

;; IR equivalent: ref/cell with atomic update
;; state.update(|s| s.insert(:key, value))
```

## Related Languages

- **Influenced by:** Lisp, ML, Haskell, Erlang
- **Influenced:** Elixir (some), many data-oriented languages
- **Compiles to:** JVM bytecode, JavaScript (ClojureScript)
- **FFI compatible:** Java (native), JavaScript (ClojureScript)

## Sources

- [Clojure Reference](https://clojure.org/reference/)
- [Clojure Guides](https://clojure.org/guides/)
- [ClojureDocs](https://clojuredocs.org/)
- [Clojure Spec Guide](https://clojure.org/guides/spec)

## See Also

- [LISP Family](../language-families/lisp.md)
- [Scala](scala.md) - JVM alternative
- [Elixir](elixir.md) - Macro-enabled FP comparison
- [Haskell](haskell.md) - Pure FP comparison
