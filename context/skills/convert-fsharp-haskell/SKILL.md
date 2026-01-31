---
name: convert-fsharp-haskell
description: Convert F# code to idiomatic Haskell. Use when migrating F# projects to Haskell, translating computation expressions to monadic patterns, or refactoring .NET functional code to pure functional Haskell. Extends meta-convert-dev with F#-to-Haskell specific patterns.
---

# Convert F# to Haskell

Convert F# code to idiomatic Haskell. This skill extends `meta-convert-dev` with F#-to-Haskell specific type mappings, idiom translations, and tooling for translating from .NET functional-first to pure functional programming.

## This Skill Extends

- `meta-convert-dev` - Foundational conversion patterns (APTV workflow, testing strategies)

For general concepts like the Analyze → Plan → Transform → Validate workflow, testing strategies, and common pitfalls, see the meta-skill first.

## This Skill Adds

- **Type mappings**: F# discriminated unions → Haskell algebraic data types
- **Idiom translations**: Computation expressions → do-notation and monads
- **Error handling**: Result/Option → Either/Maybe with standard monadic patterns
- **Async patterns**: F# async workflows → IO monad and async library
- **Type providers**: F# compile-time generation → Haskell Template Haskell or runtime parsing
- **Purity**: F# impure-by-default → Haskell pure-by-default with explicit IO

## This Skill Does NOT Cover

- General conversion methodology - see `meta-convert-dev`
- F# language fundamentals - see `lang-fsharp-dev`
- Haskell language fundamentals - see `lang-haskell-dev`
- Reverse conversion (Haskell → F#) - see `convert-haskell-fsharp`
- .NET interop specifics - focus on pure functional patterns

---

## Quick Reference

| F# | Haskell | Notes |
|-----|---------|-------|
| `type Person = { Name: string }` | `data Person = Person { name :: String }` | Record types |
| `type Shape = Circle of float \| Square of float` | `data Shape = Circle Float \| Square Float` | Discriminated unions → ADTs |
| `Option<'T>` | `Maybe a` | Direct correspondence |
| `Result<'T,'E>` | `Either e a` | Note: error on left, value on right |
| `List<'T>` / `'T list` | `[a]` | Lists |
| `async { ... }` | `do { ... }` in IO monad | Async workflow → IO actions |
| `let!` / `do!` | `<-` in do-notation | Monadic bind |
| `\|>` (pipe forward) | `$` or `&` (application) | Function application |
| `>>` (compose forward) | `.` (compose backward) | Function composition (reversed!) |
| `[<Measure>] type kg` | Phantom types or units library | Units of measure |

---

## When Converting Code

1. **Analyze source thoroughly** before writing target - understand computation expressions and their translations
2. **Map types first** - create type equivalence table for domain models
3. **Identify purity boundaries** - F# allows side effects anywhere, Haskell requires IO monad
4. **Adopt target idioms** - embrace Haskell's type classes (Functor, Applicative, Monad)
5. **Handle edge cases** - null safety, lazy evaluation, bottom values
6. **Test equivalence** - same inputs → same outputs
7. **Leverage type system** - use Haskell's type classes to reduce boilerplate

---

## Type System Mapping

### Primitive Types

| F# | Haskell | Notes |
|-----|---------|-------|
| `string` | `String` or `Text` | Use Text for performance, String for compatibility |
| `int` | `Int` (machine int) or `Integer` (arbitrary precision) | F# int is Int32, Haskell Int is machine-word |
| `int64` | `Int64` or `Integer` | Explicit 64-bit |
| `float` / `double` | `Double` | IEEE 754 double precision |
| `decimal` | `Rational` or `Scientific` | Exact decimal arithmetic |
| `bool` | `Bool` | Direct mapping |
| `char` | `Char` | Direct mapping |
| `unit` | `()` | Unit type |
| `byte` | `Word8` | Unsigned 8-bit |

### Collection Types

| F# | Haskell | Notes |
|-----|---------|-------|
| `'T list` | `[a]` | Linked lists (similar performance) |
| `'T array` | `Array a` (Data.Array) or `Vector a` | Immutable arrays; Vector for performance |
| `List<'T>` (.NET) | `[a]` or `Seq a` | .NET List → Haskell list or sequence |
| `Set<'T>` | `Set a` (Data.Set) | Ordered sets |
| `Map<'K,'V>` | `Map k v` (Data.Map) | Ordered maps |
| `'T seq` | `[a]` (lazy evaluation by default) | Sequences → lazy lists |
| `('A * 'B)` | `(a, b)` | Tuples (direct mapping) |
| `('A * 'B * 'C)` | `(a, b, c)` | Multi-element tuples |

### Composite Types

| F# | Haskell | Notes |
|-----|---------|-------|
| `type alias Person = { ... }` | `data Person = Person { ... }` | Records |
| `type Shape = Circle \| Square` | `data Shape = Circle Float \| Square Float` | Discriminated unions → ADTs |
| `Option<'T>` | `Maybe a` | `Some x` → `Just x`, `None` → `Nothing` |
| `Result<'T,'E>` | `Either e a` | `Ok x` → `Right x`, `Error e` → `Left e` |
| `Async<'T>` | `IO a` | F# async → IO monad or async library |
| Single-case union | `newtype` | Type safety wrappers |

---

## Idiom Translation

### Pattern: Discriminated Unions to Algebraic Data Types

F# and Haskell both have excellent sum type support, but syntax differs.

**F#:**
```fsharp
type PaymentMethod =
    | Cash
    | CreditCard of cardNumber: string
    | DebitCard of cardNumber: string * pin: int

let processPayment method =
    match method with
    | Cash -> "Processing cash"
    | CreditCard cardNum -> $"Credit card {cardNum}"
    | DebitCard (cardNum, _) -> $"Debit card {cardNum}"

// Using the type
let payment = CreditCard "1234-5678"
processPayment payment
```

**Haskell:**
```haskell
data PaymentMethod
    = Cash
    | CreditCard { cardNumber :: String }
    | DebitCard { cardNumber :: String, pin :: Int }
    deriving (Show, Eq)

processPayment :: PaymentMethod -> String
processPayment Cash = "Processing cash"
processPayment (CreditCard cardNum) = "Credit card " ++ cardNum
processPayment (DebitCard cardNum _) = "Debit card " ++ cardNum

-- Using the type
payment :: PaymentMethod
payment = CreditCard "1234-5678"

result = processPayment payment
```

**Why this translation:**
- Both languages have native sum types with similar semantics
- F#'s `of` keyword → Haskell's constructor arguments
- Named fields in F# → record syntax in Haskell (optional but idiomatic)
- Pattern matching is nearly identical in both languages

---

### Pattern: Records

Both languages have records, but F# updates are syntactically different.

**F#:**
```fsharp
type Person = {
    FirstName: string
    LastName: string
    Age: int
}

let person = {
    FirstName = "Alice"
    LastName = "Smith"
    Age = 30
}

// Copy-and-update
let olderPerson = { person with Age = 31 }

// Pattern matching
let getFullName { FirstName = f; LastName = l } = $"{f} {l}"
```

**Haskell:**
```haskell
data Person = Person
    { firstName :: String
    , lastName :: String
    , age :: Int
    } deriving (Show, Eq)

person :: Person
person = Person
    { firstName = "Alice"
    , lastName = "Smith"
    , age = 30
    }

-- Record update syntax
olderPerson :: Person
olderPerson = person { age = 31 }

-- Pattern matching with record syntax
getFullName :: Person -> String
getFullName Person{ firstName = f, lastName = l } = f ++ " " ++ l

-- Or with field accessors
getFullName' :: Person -> String
getFullName' p = firstName p ++ " " ++ lastName p
```

**Why this translation:**
- Both use similar record update syntax
- Haskell's record syntax includes type constructor in pattern match
- Haskell field accessors are automatic functions (firstName :: Person -> String)
- Both are immutable by default

---

### Pattern: Option/Result to Maybe/Either

F#'s Option and Result types map directly to Haskell's Maybe and Either.

**F#:**
```fsharp
// Option
let findUser id =
    if id = 1 then Some { Name = "Alice"; Age = 30 }
    else None

// Using Option
match findUser 1 with
| Some user -> user.Name
| None -> "Unknown"

// Option module functions
let result =
    findUser 1
    |> Option.map (fun u -> u.Name)
    |> Option.defaultValue "Unknown"

// Result
let divide x y =
    if y = 0 then Error "Division by zero"
    else Ok (x / y)

// Chaining Results
let calculate =
    result {
        let! a = divide 10 2
        let! b = divide 20 4
        return a + b
    }
```

**Haskell:**
```haskell
-- Maybe
findUser :: Int -> Maybe Person
findUser 1 = Just Person { name = "Alice", age = 30 }
findUser _ = Nothing

-- Using Maybe
case findUser 1 of
    Just user -> name user
    Nothing -> "Unknown"

-- Maybe functions
result :: String
result = maybe "Unknown" name (findUser 1)

-- Or with fmap and fromMaybe
result' :: String
result' = fromMaybe "Unknown" (name <$> findUser 1)

-- Either
divide :: Double -> Double -> Either String Double
divide _ 0 = Left "Division by zero"
divide x y = Right (x / y)

-- Chaining Either (with do-notation)
calculate :: Either String Double
calculate = do
    a <- divide 10 2
    b <- divide 20 4
    return (a + b)
```

**Why this translation:**
- Option → Maybe: `Some` becomes `Just`, `None` becomes `Nothing`
- Result → Either: `Ok` becomes `Right`, `Error` becomes `Left`
- F# computation expressions → Haskell do-notation
- Both support similar functional combinators (map, bind, etc.)

---

### Pattern: Computation Expressions to Do-Notation

F#'s computation expressions translate to Haskell's do-notation.

**F#:**
```fsharp
// Option workflow
type OptionBuilder() =
    member _.Bind(x, f) = Option.bind f x
    member _.Return(x) = Some x

let option = OptionBuilder()

let validateAge age =
    option {
        let! valid =
            if age >= 0 && age <= 120 then Some age
            else None
        return valid * 2
    }

// Async workflow
let fetchData url = async {
    printfn $"Fetching {url}..."
    do! Async.Sleep 1000
    return $"Data from {url}"
}

let processUrls urls = async {
    let! results =
        urls
        |> List.map fetchData
        |> Async.Parallel

    return results |> Array.toList
}
```

**Haskell:**
```haskell
-- Maybe monad (built-in, no need for custom builder)
validateAge :: Int -> Maybe Int
validateAge age = do
    valid <- if age >= 0 && age <= 120
             then Just age
             else Nothing
    return (valid * 2)

-- IO monad for async operations
fetchData :: String -> IO String
fetchData url = do
    putStrLn $ "Fetching " ++ url ++ "..."
    threadDelay 1000000  -- 1 second in microseconds
    return $ "Data from " ++ url

-- Using Control.Concurrent.Async for parallel
import Control.Concurrent.Async (mapConcurrently)

processUrls :: [String] -> IO [String]
processUrls urls = mapConcurrently fetchData urls
```

**Why this translation:**
- F# computation expressions ≈ Haskell monads
- `let!` in F# ≈ `<-` in Haskell do-notation
- `return` works the same in both
- F# custom builders not needed in Haskell (monads are first-class)
- F# `Async.Parallel` → Haskell `mapConcurrently` from async library

---

### Pattern: Pipeline Operators

F# pipelines translate to Haskell application and composition.

**F#:**
```fsharp
// Forward pipe |>
let result =
    [1..10]
    |> List.filter (fun x -> x % 2 = 0)
    |> List.map (fun x -> x * x)
    |> List.sum

// Forward composition >>
let processData = List.filter even >> List.map ((*) 2) >> List.sum

result = processData [1..10]

// Backward pipe <|
let result = List.sum <| List.map ((*) 2) <| List.filter even [1..10]
```

**Haskell:**
```haskell
-- Use $ for application (like <|)
result :: Int
result =
    sum $ map (^2) $ filter even [1..10]

-- Or use . for composition (backward, like <<)
processData :: [Int] -> Int
processData = sum . map (^2) . filter even

result' = processData [1..10]

-- For left-to-right, use & from Data.Function
import Data.Function ((&))

result'' :: Int
result'' =
    [1..10]
    & filter even
    & map (^2)
    & sum
```

**Why this translation:**
- F# `|>` (forward) ↔ Haskell `$` (application) or `&` (reverse application)
- F# `>>` (forward composition) ↔ Haskell `.` (backward composition)
- Haskell composition is right-to-left by default (like F#'s `<<`)
- For F#-style left-to-right, use `&` operator

---

### Pattern: Active Patterns to View Patterns / Pattern Synonyms

F# active patterns have no direct equivalent, but Haskell offers alternatives.

**F#:**
```fsharp
// Single-case active pattern
let (|Even|Odd|) n =
    if n % 2 = 0 then Even else Odd

match 42 with
| Even -> "even"
| Odd -> "odd"

// Partial active pattern
let (|Integer|_|) (str: string) =
    match System.Int32.TryParse(str) with
    | true, value -> Some value
    | false, _ -> None

match "123" with
| Integer n -> $"Number: {n}"
| _ -> "Not a number"
```

**Haskell:**
```haskell
{-# LANGUAGE PatternSynonyms #-}
{-# LANGUAGE ViewPatterns #-}

-- View patterns approach
isEven :: Int -> Maybe ()
isEven n | even n = Just ()
         | otherwise = Nothing

isOdd :: Int -> Maybe ()
isOdd n | odd n = Just ()
        | otherwise = Nothing

-- Usage with view patterns
describe :: Int -> String
describe (isEven -> Just ()) = "even"
describe (isOdd -> Just ()) = "odd"

-- Pattern synonyms (simpler for this case)
pattern Even :: Int
pattern Even <- (even -> True)

pattern Odd :: Int
pattern Odd <- (odd -> True)

describe' :: Int -> String
describe' Even = "even"
describe' Odd = "odd"

-- Parsing integers
parseInteger :: String -> Maybe Int
parseInteger = readMaybe

describe'' :: String -> String
describe'' (parseInteger -> Just n) = "Number: " ++ show n
describe'' _ = "Not a number"
```

**Why this translation:**
- F# active patterns → Haskell view patterns or pattern synonyms
- View patterns more verbose but more powerful
- Pattern synonyms simpler for basic cases
- `readMaybe` from Text.Read provides safe parsing

---

### Pattern: Type Providers to Runtime Parsing

F# type providers provide compile-time types from data. Haskell typically uses runtime parsing or Template Haskell.

**F#:**
```fsharp
open FSharp.Data

// CSV Type Provider (compile-time)
type StockData = CsvProvider<"stocks.csv">

let data = StockData.Load("stocks.csv")
for row in data.Rows do
    printfn $"{row.Date}: {row.Close}"

// JSON Type Provider
type Weather = JsonProvider<"""
{
    "temperature": 72,
    "condition": "sunny"
}
""">

let weather = Weather.Load("weather.json")
printfn $"Temperature: {weather.Temperature}°F"
```

**Haskell:**
```haskell
{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE OverloadedStrings #-}

import Data.Aeson
import GHC.Generics
import qualified Data.ByteString.Lazy as B

-- Define types explicitly
data StockRow = StockRow
    { date :: String
    , close :: Double
    } deriving (Generic, Show)

instance FromJSON StockRow

-- Load and parse at runtime
loadStocks :: FilePath -> IO [StockRow]
loadStocks path = do
    contents <- B.readFile path
    case decode contents of
        Just rows -> return rows
        Nothing -> error "Failed to parse CSV"

-- JSON
data Weather = Weather
    { temperature :: Int
    , condition :: String
    } deriving (Generic, Show)

instance FromJSON Weather

loadWeather :: FilePath -> IO Weather
loadWeather path = do
    contents <- B.readFile path
    case decode contents of
        Just w -> return w
        Nothing -> error "Failed to parse JSON"

-- Alternative: Use Template Haskell for compile-time generation
{-# LANGUAGE TemplateHaskell #-}
import Data.Aeson.TH

$(deriveJSON defaultOptions ''Weather)  -- Generate instances
```

**Why this translation:**
- F# type providers are compile-time, Haskell alternatives are runtime or TH
- Haskell's `aeson` library provides safe JSON parsing with types
- Template Haskell can generate instances but not infer from samples
- Trade-off: Less magic, more explicit types, same type safety at use site

---

## Error Handling

### F# Result/Option → Haskell Either/Maybe

F# and Haskell have similar approaches to explicit error handling.

**Comparison:**

| Aspect | F# | Haskell |
|--------|-----|---------|
| Optional values | `Option<'T>` | `Maybe a` |
| Result type | `Result<'T,'E>` | `Either e a` |
| Success constructor | `Ok`, `Some` | `Right`, `Just` |
| Failure constructor | `Error`, `None` | `Left`, `Nothing` |
| Chaining | computation expressions | do-notation |
| Standard library | `Option`, `Result` modules | `Data.Maybe`, `Data.Either` |

**F#:**
```fsharp
type ValidationError = string

let validateAge age =
    if age >= 0 && age <= 120 then
        Ok age
    else
        Error "Invalid age"

let validateEmail email =
    if email.Contains("@") then
        Ok email
    else
        Error "Invalid email"

// Chain validations
let validatePerson age email =
    result {
        let! validAge = validateAge age
        let! validEmail = validateEmail email
        return (validAge, validEmail)
    }

// Error: "Invalid age"
validatePerson (-1) "test@example.com"

// Ok: (30, "test@example.com")
validatePerson 30 "test@example.com"
```

**Haskell:**
```haskell
type ValidationError = String

validateAge :: Int -> Either ValidationError Int
validateAge age
    | age >= 0 && age <= 120 = Right age
    | otherwise = Left "Invalid age"

validateEmail :: String -> Either ValidationError String
validateEmail email
    | '@' `elem` email = Right email
    | otherwise = Left "Invalid email"

-- Chain validations
validatePerson :: Int -> String -> Either ValidationError (Int, String)
validatePerson age email = do
    validAge <- validateAge age
    validEmail <- validateEmail email
    return (validAge, validEmail)

-- Left "Invalid age"
result1 = validatePerson (-1) "test@example.com"

-- Right (30, "test@example.com")
result2 = validatePerson 30 "test@example.com"
```

**Why this translation:**
- F# `Result<'T,'E>` maps directly to `Either e a`
- Note: Either puts error on left, value on right (opposite intuition)
- Both support monadic composition (computation expressions / do-notation)
- Both fail-fast: first error stops the chain

---

## Concurrency Patterns

### F# Async Workflows → Haskell IO and Async Library

F# async workflows are similar to Haskell's IO monad combined with the async library.

**Comparison:**

| Aspect | F# | Haskell |
|--------|-----|---------|
| Async type | `Async<'T>` | `IO a` (or `Async a` with library) |
| Running | `Async.RunSynchronously` | No separate step (IO runs at main) |
| Concurrency | `Async.Parallel`, `Async.Start` | `forkIO`, `mapConcurrently`, `race` |
| Delay | `Async.Sleep` | `threadDelay` |
| Bind syntax | `let!` / `do!` | `<-` in do-notation |

**F#:**
```fsharp
// Simple async
let fetchUser userId = async {
    printfn $"Fetching user {userId}"
    do! Async.Sleep 1000
    return { Id = userId; Name = "Alice" }
}

// Run async
let user = fetchUser 1 |> Async.RunSynchronously

// Parallel execution
let fetchMultiple userIds = async {
    let! users =
        userIds
        |> List.map fetchUser
        |> Async.Parallel

    return users |> Array.toList
}

// Fire-and-forget
Async.Start(fetchUser 1 |> Async.Ignore)
```

**Haskell:**
```haskell
import Control.Concurrent (threadDelay, forkIO)
import Control.Concurrent.Async

-- IO action (like F# async)
fetchUser :: Int -> IO User
fetchUser userId = do
    putStrLn $ "Fetching user " ++ show userId
    threadDelay 1000000  -- 1 second (microseconds)
    return $ User userId "Alice"

-- Run IO (happens automatically in main)
main :: IO ()
main = do
    user <- fetchUser 1
    print user

-- Parallel execution with async library
fetchMultiple :: [Int] -> IO [User]
fetchMultiple userIds = mapConcurrently fetchUser userIds

-- Alternative: manual forking
fetchMultiple' :: [Int] -> IO [User]
fetchMultiple' userIds = do
    asyncs <- mapM (async . fetchUser) userIds
    mapM wait asyncs

-- Fire-and-forget
main' :: IO ()
main' = do
    forkIO $ fetchUser 1 >> return ()
    -- Continue with other work
    return ()
```

**Why this translation:**
- F# `Async<'T>` conceptually similar to `IO a`
- F# async needs explicit `RunSynchronously`; Haskell IO runs in main
- `Async.Parallel` → `mapConcurrently` from async library
- `threadDelay` takes microseconds (1000000 = 1 second)
- Haskell's async library provides structured concurrency

---

## Memory & Ownership

### F# (GC + Mutable) → Haskell (GC + Immutable)

Both languages are garbage-collected, but Haskell enforces immutability more strictly.

**Comparison:**

| Aspect | F# | Haskell |
|--------|-----|---------|
| Memory model | GC (via .NET CLR) | GC (via GHC runtime) |
| Mutability | `mutable` keyword for fields | Immutable by default, `IORef`/`STM` for state |
| References | `ref` cells | `IORef`, `TVar`, `MVar` |
| Arrays | Mutable arrays available | `Array` (immutable), `IOArray`/`STArray` (mutable in IO/ST) |
| Laziness | Eager by default | Lazy by default |

**F#:**
```fsharp
// Mutable field
type Counter() =
    let mutable count = 0
    member _.Increment() = count <- count + 1
    member _.Count = count

// Reference cell
let counter = ref 0
counter := !counter + 1
printfn $"Count: {!counter}"

// Mutable array (in-place updates)
let arr = [| 1; 2; 3 |]
arr.[0] <- 10
```

**Haskell:**
```haskell
import Data.IORef
import Control.Monad (replicateM_)

-- Counter with IORef (mutable in IO)
data Counter = Counter { counterRef :: IORef Int }

newCounter :: IO Counter
newCounter = Counter <$> newIORef 0

increment :: Counter -> IO ()
increment (Counter ref) = modifyIORef' ref (+1)

getCount :: Counter -> IO Int
getCount (Counter ref) = readIORef ref

-- Usage
main :: IO ()
main = do
    counter <- newCounter
    replicateM_ 5 (increment counter)
    count <- getCount counter
    putStrLn $ "Count: " ++ show count

-- STRef for local mutation (pure interface)
import Control.Monad.ST
import Data.STRef

localMutation :: Int -> Int
localMutation n = runST $ do
    ref <- newSTRef 0
    replicateM_ n $ modifySTRef' ref (+1)
    readSTRef ref
```

**Why this translation:**
- F# `mutable` / `ref` → Haskell `IORef` (requires IO monad)
- For pure local mutation, use `STRef` with `runST`
- Haskell's default immutability encourages functional patterns
- Most code doesn't need mutable references

---

## Common Pitfalls

### 1. Confusing Either Direction

**Problem:** F#'s Result has Ok/Error, Haskell's Either has Left/Right

```haskell
-- WRONG: Thinking Right is error
validate x = if x > 0 then Left x else Right "Error"

-- CORRECT: Right is success, Left is error
validate x = if x > 0 then Right x else Left "Error"
```

**Fix:** Remember: "Right is right (correct)"

### 2. Missing IO for Side Effects

**Problem:** F# allows side effects anywhere, Haskell requires IO

```haskell
-- WRONG: Can't use putStrLn in pure function
greet :: String -> String
greet name = putStrLn $ "Hello, " ++ name  -- Type error!

-- CORRECT: Return IO action
greet :: String -> IO ()
greet name = putStrLn $ "Hello, " ++ name
```

**Fix:** Mark functions with side effects as returning `IO`

### 3. Composition Direction

**Problem:** F# `>>` is forward, Haskell `.` is backward

```haskell
-- F# style (forward)
-- let process = add1 >> double >> toString

-- WRONG direct translation
process = add1 . double . toString  -- Composes backward!

-- CORRECT: Reverse order
process = toString . double . add1

-- OR: Use <<< for forward composition (less idiomatic)
-- OR: Use & for application
```

**Fix:** Reverse composition order or use `&` for left-to-right

### 4. Lazy Evaluation Surprises

**Problem:** Haskell is lazy by default, F# is eager

```haskell
-- F# would evaluate immediately
-- Haskell delays until needed
result = expensiveComputation 1000000

-- May cause space leaks
badSum = foldl (+) 0 [1..1000000]  -- Builds up thunks

-- CORRECT: Use strict operations when needed
goodSum = foldl' (+) 0 [1..1000000]  -- Strict fold
```

**Fix:** Use strict versions (`foldl'`, `seq`, `!` bang patterns) when needed

### 5. String Types Confusion

**Problem:** Haskell has multiple string types

```haskell
-- String (lazy, inefficient)
name :: String
name = "Alice"

-- Text (strict, efficient)
name' :: Text
name' = "Alice"  -- Needs OverloadedStrings

-- ByteString (for binary data)
data' :: ByteString
data' = "binary"
```

**Fix:** Use `Text` for Unicode strings, `ByteString` for binary, `String` for simple cases

### 6. Type Class Constraints Not Explicit

**Problem:** F# inference works differently than Haskell's

```haskell
-- F# infers numeric type
-- F# let add x y = x + y  (generic numeric)

-- Haskell needs constraint
add :: Num a => a -> a -> a
add x y = x + y
```

**Fix:** Add type signatures with constraints

---

## Tooling

| Tool | F# | Haskell | Notes |
|------|-----|---------|-------|
| **Build** | `dotnet build` | `cabal build` / `stack build` | Stack is more batteries-included |
| **REPL** | `dotnet fsi` | `ghci` / `stack ghci` | Interactive development |
| **Package Manager** | NuGet (via dotnet) | Cabal / Hackage | Stack uses Stackage curated sets |
| **Formatter** | Fantomas | `ormolu` / `fourmolu` / `stylish-haskell` | Multiple choices in Haskell |
| **Linter** | FSharpLint | `hlint` | Suggests improvements |
| **Type Checker** | F# compiler | GHC | GHC has more advanced type features |
| **Testing** | Expecto, xUnit, FsUnit | HSpec, QuickCheck, Hedgehog, Tasty | Property testing popular in Haskell |
| **Language Server** | Ionide | HLS (Haskell Language Server) | IDE integration |

---

## Examples

### Example 1: Simple - Record Type Conversion

Convert a simple F# record to Haskell.

**Before (F#):**
```fsharp
type User = {
    Id: int
    Name: string
    Email: string
    Age: int
}

let createUser id name email age = {
    Id = id
    Name = name
    Email = email
    Age = age
}

let getEmail user = user.Email

let updateAge age user = { user with Age = age }

// Usage
let user = createUser 1 "Alice" "alice@example.com" 30
let email = getEmail user
let older = updateAge 31 user
```

**After (Haskell):**
```haskell
data User = User
    { userId :: Int
    , userName :: String
    , userEmail :: String
    , userAge :: Int
    } deriving (Show, Eq)

createUser :: Int -> String -> String -> Int -> User
createUser id' name email age = User
    { userId = id'
    , userName = name
    , userEmail = email
    , userAge = age
    }

getEmail :: User -> String
getEmail = userEmail  -- Record accessor is a function

updateAge :: Int -> User -> User
updateAge age user = user { userAge = age }

-- Usage
user :: User
user = createUser 1 "Alice" "alice@example.com" 30

email :: String
email = getEmail user

older :: User
older = updateAge 31 user
```

---

### Example 2: Medium - Discriminated Unions and Pattern Matching

Convert F# discriminated unions and pattern matching.

**Before (F#):**
```fsharp
type Expression =
    | Literal of int
    | Add of Expression * Expression
    | Multiply of Expression * Expression
    | Variable of string

let rec evaluate env expr =
    match expr with
    | Literal n -> n
    | Add (left, right) ->
        evaluate env left + evaluate env right
    | Multiply (left, right) ->
        evaluate env left * evaluate env right
    | Variable name ->
        Map.find name env

let simplify expr =
    match expr with
    | Add (Literal 0, e) -> e
    | Add (e, Literal 0) -> e
    | Multiply (Literal 1, e) -> e
    | Multiply (e, Literal 1) -> e
    | Multiply (Literal 0, _) -> Literal 0
    | Multiply (_, Literal 0) -> Literal 0
    | e -> e

// Usage
let env = Map [("x", 5); ("y", 10)]
let expr = Add (Variable "x", Multiply (Literal 2, Variable "y"))
let result = evaluate env expr  // 5 + (2 * 10) = 25
```

**After (Haskell):**
```haskell
import qualified Data.Map as Map

data Expression
    = Literal Int
    | Add Expression Expression
    | Multiply Expression Expression
    | Variable String
    deriving (Show, Eq)

type Environment = Map.Map String Int

evaluate :: Environment -> Expression -> Int
evaluate env (Literal n) = n
evaluate env (Add left right) =
    evaluate env left + evaluate env right
evaluate env (Multiply left right) =
    evaluate env left * evaluate env right
evaluate env (Variable name) =
    env Map.! name  -- Partial function, use Map.lookup for safety

simplify :: Expression -> Expression
simplify (Add (Literal 0) e) = e
simplify (Add e (Literal 0)) = e
simplify (Multiply (Literal 1) e) = e
simplify (Multiply e (Literal 1)) = e
simplify (Multiply (Literal 0) _) = Literal 0
simplify (Multiply _ (Literal 0)) = Literal 0
simplify e = e

-- Usage
env :: Environment
env = Map.fromList [("x", 5), ("y", 10)]

expr :: Expression
expr = Add (Variable "x") (Multiply (Literal 2) (Variable "y"))

result :: Int
result = evaluate env expr  -- 5 + (2 * 10) = 25
```

---

### Example 3: Complex - Async Workflows to IO with Concurrency

Convert F# async workflows to Haskell IO with the async library.

**Before (F#):**
```fsharp
open System

type User = { Id: int; Name: string; Email: string }
type ApiError = NetworkError of string | ParseError of string

let fetchFromApi url = async {
    printfn $"Fetching from {url}"
    do! Async.Sleep 500
    if url.Contains("fail") then
        return Error (NetworkError "Network failed")
    else
        return Ok $"Data from {url}"
}

let parseUser data =
    if data.Contains("error") then
        Error (ParseError "Parse failed")
    else
        Ok { Id = 1; Name = "Alice"; Email = "alice@example.com" }

let getUserData url = async {
    let! fetchResult = fetchFromApi url
    return
        fetchResult
        |> Result.bind parseUser
}

let getAllUsers urls = async {
    let! results =
        urls
        |> List.map getUserData
        |> Async.Parallel

    return results |> Array.toList
}

// Usage
let urls = ["https://api.example.com/user/1"; "https://api.example.com/user/2"]
let results = getAllUsers urls |> Async.RunSynchronously
```

**After (Haskell):**
```haskell
import Control.Concurrent (threadDelay)
import Control.Concurrent.Async (mapConcurrently)
import Data.List (isInfixOf)

data User = User
    { userId :: Int
    , userName :: String
    , userEmail :: String
    } deriving (Show, Eq)

data ApiError
    = NetworkError String
    | ParseError String
    deriving (Show, Eq)

fetchFromApi :: String -> IO (Either ApiError String)
fetchFromApi url = do
    putStrLn $ "Fetching from " ++ url
    threadDelay 500000  -- 500ms in microseconds
    return $ if "fail" `isInfixOf` url
             then Left (NetworkError "Network failed")
             else Right ("Data from " ++ url)

parseUser :: String -> Either ApiError User
parseUser dat
    | "error" `isInfixOf` dat = Left (ParseError "Parse failed")
    | otherwise = Right $ User 1 "Alice" "alice@example.com"

getUserData :: String -> IO (Either ApiError User)
getUserData url = do
    fetchResult <- fetchFromApi url
    return $ fetchResult >>= parseUser  -- Chaining Either with >>=

getAllUsers :: [String] -> IO [Either ApiError User]
getAllUsers urls = mapConcurrently getUserData urls

-- Usage
main :: IO ()
main = do
    let urls = ["https://api.example.com/user/1", "https://api.example.com/user/2"]
    results <- getAllUsers urls
    print results
```

---

## See Also

For more examples and patterns, see:
- `meta-convert-dev` - Foundational patterns with cross-language examples
- `lang-fsharp-dev` - F# development patterns
- `lang-haskell-dev` - Haskell development patterns

Cross-cutting pattern skills:
- `patterns-concurrency-dev` - Async, STM, threading across languages
- `patterns-serialization-dev` - JSON, validation across languages
- `patterns-metaprogramming-dev` - Type providers vs Template Haskell
