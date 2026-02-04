# ML/Functional Family

> Statically-typed functional languages with type inference, algebraic data types, and pattern matching.

## Overview

The ML/Functional family descends from the ML (Meta Language) tradition, emphasizing:

- **Immutability by default** - Data structures are immutable unless explicitly marked mutable
- **Strong static typing** - Types checked at compile time with powerful inference
- **Algebraic data types** - Sum types (variants) and product types (records/tuples)
- **Pattern matching** - Destructuring and control flow via pattern matching
- **First-class functions** - Functions as values, closures, higher-order functions

This family is the most common **target** for conversions (29 skills), reflecting industry interest in adopting functional programming principles.

## Subtypes

| Subtype | Description | Languages |
|---------|-------------|-----------|
| **pure** | Enforced referential transparency, no side effects in pure code | Haskell, Elm, PureScript, Idris |
| **hybrid** | Functional-first with imperative escape hatches | Scala, F#, OCaml, ReasonML, Roc |

### Pure vs Hybrid Differences

| Aspect | Pure | Hybrid |
|--------|------|--------|
| Side effects | Monadic IO only | Available directly |
| Mutability | Not available | Available but discouraged |
| Evaluation | Lazy (Haskell) or strict (Elm) | Always strict |
| Interop | FFI with explicit effects | Native platform interop |
| Learning curve | Steeper | More gradual |

## Key Characteristics

- **Hindley-Milner type inference** - Most types inferred automatically
- **Parametric polymorphism** - Generic functions work on any type
- **Higher-kinded types** - Type constructors as type parameters (Haskell, Scala)
- **Typeclasses/Traits** - Ad-hoc polymorphism without inheritance
- **Immutable by default** - Explicit markers for mutability
- **Expression-oriented** - Everything returns a value
- **Recursion over iteration** - Tail-call optimization common

## Languages in Family

| Language | Subtype | Platform | Notes |
|----------|---------|----------|-------|
| Haskell | pure | Native/GHC | Reference pure FP, lazy evaluation |
| Elm | pure | JavaScript | No runtime exceptions, web-focused |
| PureScript | pure | JavaScript | Strict Haskell-like for web |
| Scala | hybrid | JVM | OOP+FP fusion, rich ecosystem |
| F# | hybrid | .NET | ML syntax on CLR, computation expressions |
| OCaml | hybrid | Native | Original ML descendant, fast compiler |
| ReasonML | hybrid | JavaScript | OCaml syntax variant for web |
| Roc | hybrid | Native | No exceptions, platforms, effects |

## Type System

### Strengths

- **Global type inference** - Rarely need type annotations
- **Algebraic data types** - Model domain precisely
- **Exhaustive pattern matching** - Compiler ensures all cases handled
- **No null** - Option/Maybe types for optional values
- **Phantom types** - Encode invariants in types

### Typing Features

| Feature | Support | Notes |
|---------|---------|-------|
| Generics | ● Native | Parametric polymorphism |
| Higher-kinded types | ◕ Full | Haskell, Scala; limited in others |
| Type inference | ● Native | Hindley-Milner or bidirectional |
| GADTs | ◕ Full | Haskell, OCaml; Scala via match types |
| Dependent types | ◔ Limited | Idris full; Haskell via extensions |

### Common Type Patterns

```text
-- Sum types (variants)
data Maybe a = Nothing | Just a
data Either a b = Left a | Right b
data Result e a = Err e | Ok a

-- Product types (records)
data Person = Person { name :: String, age :: Int }

-- Recursive types
data List a = Nil | Cons a (List a)
data Tree a = Leaf a | Node (Tree a) (Tree a)
```

## Memory Model

- **Garbage collected** - All ML-FP languages use GC
- **Immutable by default** - Persistent data structures
- **No manual memory management** - No pointers, no malloc/free
- **Value semantics** - Data is copied conceptually (optimized by compiler)

### Persistent Data Structures

Immutable collections that share structure:

- Lists share tails
- Trees share unchanged subtrees
- Maps use HAMTs (Hash Array Mapped Tries)

## Concurrency Model

| Language | Primary Model | Notes |
|----------|---------------|-------|
| Haskell | Green threads + STM | Lightweight threads, composable transactions |
| Scala | Futures + Akka actors | JVM threads + actor library |
| F# | Async workflows | .NET Task-based |
| Elm | None | Single-threaded by design |
| OCaml | Multicore (5.0+) | Effect handlers, domains |

### Effect Handling

| Approach | Languages | Description |
|----------|-----------|-------------|
| Monadic IO | Haskell | Effects wrapped in IO monad |
| Effect systems | Roc, Koka | Algebraic effects with handlers |
| Direct | Scala, F#, OCaml | Effects available, FP encouraged |

## Common Patterns

### Pattern Matching

```haskell
case maybeValue of
  Nothing -> defaultValue
  Just x  -> transform x
```

### Higher-Order Functions

```haskell
map :: (a -> b) -> [a] -> [b]
filter :: (a -> Bool) -> [a] -> [a]
fold :: (b -> a -> b) -> b -> [a] -> b
```

### Monadic Composition

```haskell
do
  x <- getLine
  y <- readFile x
  return (process y)
```

### Typeclass Instances

```haskell
class Functor f where
  fmap :: (a -> b) -> f a -> f b

instance Functor Maybe where
  fmap f Nothing  = Nothing
  fmap f (Just x) = Just (f x)
```

## Conversion Considerations

### Converting FROM ML-FP

**What's easy to preserve:**

- Type information (helps target typing)
- Pure functions (map directly)
- ADTs (to enums, sealed classes, etc.)
- Pattern matching (to switch/match)

**What's hard to translate:**

- Higher-kinded types (most targets lack HKT)
- Lazy evaluation (Haskell) → strict (must force evaluation points)
- Typeclasses → interfaces/traits (lose ad-hoc polymorphism)
- Monadic effects → direct effects (restructure control flow)

**Common pitfalls:**

- Assuming target has type inference
- Forgetting to handle laziness
- Losing exhaustiveness guarantees

**Semantic gaps (63 gaps ML-FP→ML-FP):**

- Pure ↔ hybrid effect systems
- HKT availability varies
- Evaluation strategy differences

### Converting TO ML-FP

**What maps naturally:**

- Pure functions from any language
- Immutable data structures
- Recursive algorithms
- Interface-based polymorphism

**What requires restructuring:**

- Mutable state → State monad or refs
- Exceptions → Result/Either types
- Null checks → Maybe/Option
- Loops → recursion/folds
- Class hierarchies → ADTs + functions

**Idiomatic patterns to target:**

- Replace null with Maybe/Option
- Replace exceptions with Result/Either
- Replace loops with map/filter/fold
- Replace inheritance with composition

**Anti-patterns to avoid:**

- Overusing monads for simple code
- Excessive point-free style
- Ignoring performance of immutable structures

## Cross-References

### Phase 0 Pattern Clusters

- **Universal patterns**: bool, String, int, float, List (appear in 60%+ of ML-FP conversions)
- **Family-specific**: unit (10 patterns), IO a (6 patterns), 'a array (4 patterns)
- **Gap patterns**: 63 gaps in ML-FP → ML-FP conversions

### Related convert-* Skills

- convert-python-haskell (238 patterns)
- convert-python-scala (198 patterns)
- convert-fsharp-scala (210 patterns)
- convert-haskell-scala (179 patterns)
- convert-clojure-haskell (177 patterns)

## Sources

- [Haskell Documentation](https://www.haskell.org/documentation/)
- [Scala Documentation](https://docs.scala-lang.org/)
- [F# Documentation](https://fsharp.org/docs/)
- [Elm Guide](https://guide.elm-lang.org/)
- [OCaml Manual](https://ocaml.org/manual/)
- [Roc Tutorial](https://www.roc-lang.org/tutorial)

## See Also

- [Dependent Types](dependent-types.md) - Extension of ML-FP with value-dependent types
- [Gradual Typing](gradual-typing.md) - Adding optional types to dynamic languages
- [Overview](overview.md) - Cross-family comparison matrices
