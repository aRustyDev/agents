# Haskell

> Purely functional programming language with strong static typing and lazy evaluation.

## Overview

Haskell is a standardized, general-purpose purely functional programming language, first specified in 1990 and named after logician Haskell Curry. It emphasizes pure functions, immutability, and a powerful type system with type inference.

The language pioneered many concepts now common in other languages: type classes, monads for effects, algebraic data types, and advanced type system features. GHC (Glasgow Haskell Compiler) is the de facto standard implementation, providing extensive language extensions beyond Haskell 2010.

Haskell is used in academia, finance, blockchain, and formal verification. Its type system serves as a reference for other languages' advanced type features.

## Family Classification

| Dimension | Classification | Notes |
|-----------|----------------|-------|
| Primary Family | ML-FP | Pure FP with lazy evaluation |
| Secondary Family | — | No OOP |
| Subtype | pure | Enforced purity via types |

See: [ML-FP Family](../language-families/ml-fp.md)

## Version History

| Version | Release | Key Changes for Conversion |
|---------|---------|---------------------------|
| Haskell 98 | 1999 | Standard baseline |
| Haskell 2010 | 2010 | FFI, hierarchical modules |
| GHC 9.0 | 2021-02 | Linear types |
| GHC 9.4 | 2022-08 | Improved records, DeepSubsumption |
| GHC 9.8 | 2023-10 | Type-level programming improvements |

## Feature Profile

### Type System

- **Strength:** strong (static, no implicit conversions)
- **Inference:** global (Hindley-Milner with extensions)
- **Generics:** higher-kinded (type constructors, GADTs)
- **Nullability:** explicit (Maybe a)

### Memory Model

- **Management:** gc (GHC runtime GC)
- **Mutability:** immutable (ST monad for local mutation, IORef for IO)
- **Allocation:** heap (lazy thunks, sharing)

### Control Flow

- **Structured:** guards, case, if-then-else, where, let-in
- **Effects:** monadic (IO, ST, effect systems)
- **Async:** async library, STM (Software Transactional Memory)

### Data Types

- **Primitives:** Int, Integer, Float, Double, Char, Bool
- **Composites:** algebraic data types, records, tuples
- **Collections:** [], Map, Set, Vector, Seq
- **Abstraction:** type classes, modules, newtypes

### Metaprogramming

- **Macros:** Template Haskell (compile-time code generation)
- **Reflection:** runtime (Typeable), type-level (TypeRep)
- **Code generation:** deriving, generics (GHC.Generics)

## Ecosystem

| Tool | Name | Notes |
|------|------|-------|
| Package Manager | Cabal, Stack | Stack for reproducibility |
| Build System | Cabal, Stack, Nix | Cabal v2 is modern |
| LSP | HLS (Haskell Language Server) | Good IDE support |
| Formatter | Ormolu, Fourmolu, stylish-haskell | Ormolu is opinionated |
| Linter | HLint | Extensive suggestions |
| REPL | GHCi | Interactive development |
| Test Framework | Hspec, Tasty, QuickCheck | QuickCheck for property testing |

## Syntax Patterns

```haskell
-- Function definition
greet :: String -> Int -> String
greet name times = concat $ replicate times ("Hello, " ++ name ++ "! ")

-- Generic function (parametric polymorphism)
identity :: a -> a
identity x = x

-- Async function (IO with async)
fetchData :: String -> IO Response
fetchData url = do
  response <- httpGet url
  case statusCode response of
    200 -> pure response
    code -> throwIO $ HttpError code

-- Data type (product)
data User = User
  { userId :: String
  , userName :: String
  , userEmail :: Maybe String
  }

-- Sum type (ADT)
data Result a e
  = Ok a
  | Err e

-- GADT example
data Expr a where
  LitInt  :: Int -> Expr Int
  LitBool :: Bool -> Expr Bool
  Add     :: Expr Int -> Expr Int -> Expr Int
  If      :: Expr Bool -> Expr a -> Expr a -> Expr a

-- Pattern matching
area :: Shape -> Double
area shape = case shape of
  Circle r -> pi * r * r
  Rectangle w h -> w * h

-- Type class definition
class Show a where
  show :: a -> String

instance Show Int where
  show = showInt

-- Type class with functional dependencies
class Monad m => MonadState s m | m -> s where
  get :: m s
  put :: s -> m ()

-- Monad do-notation
processUsers :: [User] -> IO [String]
processUsers users = do
  validated <- traverse validateUser users
  let names = map userName validated
  pure names

-- List comprehension
evenSquares :: [Int] -> [Int]
evenSquares xs = [x * x | x <- xs, even x]

-- Higher-order functions
doubled :: [Int] -> [Int]
doubled = map (* 2)

filtered :: [Int] -> [Int]
filtered = filter even

summed :: [Int] -> Int
summed = foldl' (+) 0

-- Applicative style
data Person = Person String Int

parsePerson :: Parser Person
parsePerson = Person <$> parseString <*> parseInt

-- Error handling with Either
divide :: Int -> Int -> Either String Int
divide _ 0 = Left "Division by zero"
divide a b = Right (a `div` b)

-- Newtype for type safety
newtype UserId = UserId { unUserId :: String }
```

## Semantic Gaps

| Gap | Severity | Workaround |
|-----|----------|------------|
| Lazy evaluation can cause space leaks | moderate | Use strict data types, BangPatterns |
| Partial functions (head, tail) | moderate | Use safe alternatives (headMay), -Wincomplete-patterns |
| String as [Char] is inefficient | minor | Use Text or ByteString |
| Record field name collisions | moderate | Use DuplicateRecordFields, OverloadedRecordDot |
| Steep learning curve | moderate | Start with basic Haskell, add extensions gradually |

## Convert-* Coverage

| Direction | Count | Skills |
|-----------|-------|--------|
| As Source | 2 | haskell-roc, haskell-scala |
| As Target | 6 | python-haskell, elixir-haskell, clojure-haskell, elm-haskell, erlang-haskell, fsharp-haskell |

**Note:** Primary pure FP reference - conversions focus on preserving purity and type safety.

## Idiomatic Patterns

### ADTs → Enums/Unions

```haskell
-- Haskell: algebraic data type
data Maybe a = Nothing | Just a

-- IR equivalent: enum with generics
-- enum Maybe<T> { None, Some(T) }
```

### Type Classes → Traits/Interfaces

```haskell
-- Haskell: type class
class Eq a where
  (==) :: a -> a -> Bool

-- IR equivalent: trait with method
-- trait Eq { fn eq(&self, other: &Self) -> bool }
```

### do-Notation → Effect Composition

```haskell
-- Haskell: do notation
do
  x <- getLine
  putStrLn x

-- IR equivalent: monadic bind
-- getLine.flatMap(x => putStrLn(x))
```

### Guards → Pattern Conditions

```haskell
-- Haskell: guards
abs x
  | x < 0     = -x
  | otherwise = x

-- IR equivalent: pattern with guard
-- match x { n if n < 0 => -n, n => n }
```

## Related Languages

- **Influenced by:** Miranda, ML, Lisp, SASL
- **Influenced:** Rust (traits), Scala (type classes), PureScript, Elm, Idris
- **Compiles to:** Native (GHC), JavaScript (GHCJS, PureScript)
- **FFI compatible:** C (native FFI)

## Sources

- [Haskell 2010 Report](https://www.haskell.org/onlinereport/haskell2010/)
- [GHC User's Guide](https://ghc.gitlab.haskell.org/ghc/doc/users_guide/)
- [Learn You a Haskell](http://learnyouahaskell.com/)
- [Haskell Wiki](https://wiki.haskell.org/)

## See Also

- [ML-FP Family](../language-families/ml-fp.md)
- [Elm](elm.md) - Simplified Haskell for web
- [Scala](scala.md) - Hybrid FP comparison
- [Roc](roc.md) - Modern pure FP
